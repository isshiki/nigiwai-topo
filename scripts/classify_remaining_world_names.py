"""Profile every remaining peak from full nearby POI rows; never adopt names."""
import json
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import duckdb
from pyproj import Geod

ROOT = Path('data/name-research/unnamed-world')


def normalized(value):
    return ''.join(c for c in unicodedata.normalize('NFKD', value or '').casefold()
                   if c.isalnum())


def main():
    queue = json.loads((ROOT / 'remaining-review-queue.json').read_text(encoding='utf-8'))
    prior = json.loads((ROOT / 'address-name-review.json').read_text(encoding='utf-8'))
    old = {x['peak']: x for x in prior['items']}
    wanted = {x['peak'] for x in queue['items']}
    assert len(wanted) == queue['remaining']
    con = duckdb.connect(config={'threads': 2, 'memory_limit': '2GB'})
    con.execute('create temp table targets(peak varchar)')
    con.executemany('insert into targets values (?)', [(x,) for x in wanted])
    assert con.execute("select count(*)-count(distinct fsq_place_id) from read_parquet(?)",
                       [str(ROOT / 'addresses.parquet')]).fetchone()[0] == 0
    sql = '''SELECT p.peak,a.* FROM
      (SELECT DISTINCT peak,fsq_place_id FROM read_parquet(?)
       WHERE peak IN (SELECT peak FROM targets)) p
      LEFT JOIN read_parquet(?) a USING(fsq_place_id)'''
    cursor = con.execute(sql, [str(ROOT / 'local-parts/*.parquet'),
                               str(ROOT / 'addresses.parquet')])
    fields = [c[0] for c in cursor.description]
    groups = defaultdict(list)
    for row in cursor.fetchall():
        p = dict(zip(fields, row))
        assert p['fsq_place_id'] is not None, 'Missing joined address row'
        groups[p['peak']].append(p)
    geod = Geod(ellps='WGS84')
    items, reasons, countries, variants = [], Counter(), Counter(), []
    for key in sorted(wanted):
        previous = old[key]
        lon, lat = previous['coordinates']
        near = [p for p in groups[key] if
                geod.inv(lon, lat, p['longitude'], p['latitude'])[2] <= 750]
        assert len(near) == previous['near_pois'], f'Coverage changed: {key}'
        n = len(near)
        address = sum(bool((p['address'] or '').strip()) for p in near)
        locality = sum(bool((p['locality'] or p['post_town'] or '').strip()) for p in near)
        coordinates = Counter((p['longitude'], p['latitude']) for p in near)
        concentration = coordinates.most_common(1)[0][1] / n if n else 0
        names = defaultdict(Counter)
        for p in near:
            for field in ('locality', 'post_town'):
                raw = (p[field] or '').strip()
                if raw:
                    names[(p['country'], normalized(raw))][raw] += 1
        variants_here = [{'country': c, 'normalized': norm, 'raw_counts': dict(raw)}
                         for (c, norm), raw in names.items() if len(raw) > 1]
        variants.extend({'peak': key, **v} for v in variants_here)
        candidates = previous['candidates']
        winner = candidates[0] if candidates else None
        flags = []
        if address < 4: flags.append('insufficient_address')
        if locality < 4: flags.append('insufficient_locality')
        if concentration >= .5 and n >= 6: flags.append('coordinate_concentration')
        if variants_here: flags.append('equivalent_spelling_variants')
        if len(candidates) > 1: flags.append('multiple_reference_candidates')
        if previous['distant_alias_matches']: flags.append('distant_homonym_matches')
        if not n: reason = 'no_nearby_pois'
        elif 'coordinate_concentration' in flags: reason = 'coordinate_concentration_review'
        elif locality < 4: reason = 'insufficient_locality'
        elif address < 4: reason = 'insufficient_address'
        elif not winner: reason = 'no_nearby_place_reference'
        elif winner['distance_m'] > 1000: reason = 'reference_over_1km'
        elif len(candidates) > 1 and candidates[1]['support_share'] >= .2:
            reason = 'competing_references'
        elif variants_here: reason = 'spelling_variants_review'
        else: reason = 'consensus_or_external_evidence_review'
        countries_here = Counter(p['country'] or '(missing)' for p in near)
        country = countries_here.most_common(1)[0][0] if near else '(missing)'
        countries[country] += 1
        reasons[reason] += 1
        items.append({'peak': key, 'density': previous['density'], 'country': country,
                      'primary_reason': reason, 'flags': flags, 'near_pois': n,
                      'with_address': address, 'with_locality_or_post_town': locality,
                      'distinct_coordinates': len(coordinates),
                      'largest_coordinate_share': round(concentration, 4),
                      'locality_counts': Counter(p['locality'] or '(missing)' for p in near).most_common(),
                      'reference_candidates': candidates})
    report = {'remaining': len(items), 'names_adopted': 0, 'not_adopted': True,
              'reason_counts': dict(reasons), 'country_counts': dict(countries.most_common()),
              'normalization_variant_groups': len(variants),
              'coverage_check': 'All remaining peaks match previous full nearby POI counts; unique address IDs; no missing joins.',
              'rules': {'radius_m': 750, 'minimum_address_or_locality_rows': 4,
                        'concentration_share': .5, 'concentration_min_rows': 6,
                        'reference_distance_m': 1000, 'competing_share': .2},
              'limits': 'Primary reasons are ordered research triage heuristics, not proven defects. GeoNames points are not boundaries. Distant homonyms do not prove bad POI coordinates. Spelling normalization does not establish pronunciation or geographic identity.',
              'sql': sql, 'items': items}
    assert sum(reasons.values()) == queue['remaining']
    (ROOT / 'remaining-classification383.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    (ROOT / 'remaining-normalization383.json').write_text(json.dumps({'not_adopted': True, 'items': variants}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps({k: report[k] for k in ('remaining', 'names_adopted', 'reason_counts', 'normalization_variant_groups', 'country_counts')}, ensure_ascii=True))


if __name__ == '__main__':
    main()
