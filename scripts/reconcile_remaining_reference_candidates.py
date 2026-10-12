"""Compare full POI address text with existing references, without publishing."""
import io
import json
import re
import unicodedata
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import duckdb
from pyproj import Geod

ROOT = Path('data/name-research/unnamed-world')


def words(text):
    text = unicodedata.normalize('NFKD', text or '').casefold()
    text = ''.join(c for c in text if not unicodedata.combining(c))
    return ' '.join(re.findall(r'[^\W_]+', text, re.UNICODE))


def contains(text, alias):
    # Full word sequence, never a substring such as York within Yorkshire.
    return bool(alias) and (' ' + alias + ' ') in (' ' + words(text) + ' ')


def main():
    classification = json.loads((ROOT / 'remaining-classification383.json').read_text(encoding='utf-8'))
    targets = [x for x in classification['items'] if x['reference_candidates']]
    assert len(targets) == 1615
    old = {x['peak']: x for x in json.loads((ROOT / 'address-name-review.json').read_text(encoding='utf-8'))['items']}
    ids = defaultdict(set)
    for x in targets:
        for ref in x['reference_candidates']:
            ids[ref['country']].add(ref['id'])
    aliases = {}
    for country, wanted in ids.items():
        with zipfile.ZipFile(Path('data/name-research/coordinate-countries') / (country + '.zip')) as z:
            with z.open(country + '.txt') as stream:
                for line in io.TextIOWrapper(stream, encoding='utf-8'):
                    f = line.rstrip('\n').split('\t')
                    if f[0] in wanted:
                        # Latin/local official names only; alternateNames may contain unrelated short forms.
                        aliases[f[0]] = sorted({words(f[1]), words(f[2])} - {''})
    con = duckdb.connect(config={'threads': 2, 'memory_limit': '2GB'})
    con.execute('create temp table targets(peak varchar)')
    con.executemany('insert into targets values (?)', [(x['peak'],) for x in targets])
    cursor = con.execute('''SELECT p.peak,a.* FROM
      (SELECT DISTINCT peak,fsq_place_id FROM read_parquet(?)
       WHERE peak IN (SELECT peak FROM targets)) p
      JOIN read_parquet(?) a USING(fsq_place_id)''',
                         [str(ROOT / 'local-parts/*.parquet'), str(ROOT / 'addresses.parquet')])
    fields = [c[0] for c in cursor.description]
    groups = defaultdict(list)
    for row in cursor.fetchall():
        p = dict(zip(fields, row))
        groups[p['peak']].append(p)
    geod = Geod(ellps='WGS84')
    items, categories = [], Counter()
    for x in targets:
        t = old[x['peak']]
        near = [p for p in groups[x['peak']] if geod.inv(*t['coordinates'], p['longitude'], p['latitude'])[2] <= 750]
        assert len(near) == t['near_pois']
        ref = x['reference_candidates'][0]
        names = aliases[ref['id']]
        field_ids, address_ids, facility_ids, ambiguous_ids = [], [], [], []
        competitors = x['reference_candidates'][1:]
        for p in near:
            if p['country'] != ref['country']:
                continue
            field = any(contains(p.get(k), a) for k in ('locality', 'post_town') for a in names)
            address = any(contains(p['address'], a) for a in names)
            facility = any(contains(p['name'], a) for a in names)
            if field: field_ids.append(p['fsq_place_id'])
            if address: address_ids.append(p['fsq_place_id'])
            if facility: facility_ids.append(p['fsq_place_id'])
            if (field or address) and any(any(contains(p.get(k), a) for k in ('locality', 'post_town', 'address')
                                             for a in aliases[c['id']]) for c in competitors):
                ambiguous_ids.append(p['fsq_place_id'])
        supporting = (set(field_ids) | set(address_ids)) - set(ambiguous_ids)
        share = len(supporting) / len(near) if near else 0
        ready = (share >= .85 and len(supporting) >= 6 and ref['distance_m'] <= 1000
                 and x['distinct_coordinates'] >= 4 and x['with_address'] >= 4
                 and x['largest_coordinate_share'] < .5)
        if ready: category = 'manual_geographic_review_shortlist'
        elif ref['distance_m'] > 1000: category = 'reference_distance_review'
        elif x['largest_coordinate_share'] >= .5: category = 'coordinate_quality_review'
        else: category = 'additional_address_or_public_source_required'
        categories[category] += 1
        items.append({'peak': x['peak'], 'density': x['density'], 'country': ref['country'],
                      'reference': ref, 'category': category, 'near_pois': len(near),
                      'reference_aliases_used': names, 'prior_support': ref['supporting_pois'],
                      'text_support': len(supporting), 'text_support_share': round(share, 4),
                      'locality_text_ids': field_ids, 'address_text_ids': address_ids,
                      'facility_name_ids': facility_ids, 'ambiguous_text_ids': ambiguous_ids,
                      'new_text_support_ids': sorted(supporting - set(field_ids)),
                      'not_adopted': True})
    report = {'scope': 1615, 'checked': len(items), 'names_adopted': 0,
              'category_counts': dict(categories), 'items': items,
              'limits': 'Text is an additional research signal, not independent external evidence. A locality in an address can denote a district, stale address, or distant namesake. Facility names are never counted as address votes. Readings and geographic identity require review. Existing adoption data unchanged.'}
    (ROOT / 'reference-reconciliation384.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('scope', 'checked', 'names_adopted', 'category_counts')}))


if __name__ == '__main__':
    main()
