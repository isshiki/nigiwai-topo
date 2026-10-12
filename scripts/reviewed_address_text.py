"""Validate individual text-supported names with two reviewed official anchors."""
import json
import hashlib
from pathlib import Path

import duckdb
from pyproj import Geod
from reconcile_remaining_reference_candidates import contains
from official_address_anchor_review import validate_anchor_review


def validate_reviewed_hierarchy(peak, original, near, support):
    """Allow only explicitly reviewed parent/child identities; never add votes."""
    path = Path('docs/unnamed-world-reference-hierarchy400.json')
    records = json.loads(path.read_text(encoding='utf-8'))['items'] if path.exists() else []
    children = [x for x in peak['candidates'] if x['id'] != original['id']]
    if not children or len(children) + 1 != len(peak['candidates']):
        raise ValueError('Invalid parent candidate identity')
    for child in children:
        matches = [r for r in records if r['peak'] == peak['peak']
                   and r['parent_reference_id'] == original['id']
                   and r['child_reference_id'] == child['id']]
        if len(matches) != 1:
            raise ValueError('Unreviewed competing reference')
        r = matches[0]
        if (r['relationship'] != 'part_of_inhabited_place'
                or r['decision'] != 'hierarchy_relationship_confirmed_name_application_pending'
                or r['verification'] != 'primary_search_body'
                or r['parent_name'] != original['name'] or r['child_name'] != child['name']
                or r['country'] != original['country'] or r['country'] != child['country']):
            raise ValueError('Reviewed hierarchy identity changed')
        pois = [p for p in near if p[0] == r['competing_poi_id']]
        if (len(pois) != 1 or list(pois[0][-2:]) != r['competing_poi_coordinates']
                or pois[0][1] != r['country'] or pois[0][2] != child['name']
                or r['competing_poi_id'] in support):
            raise ValueError('Child evidence changed or counted as parent support')


def reviewed_text_reference(choice, peak):
    rows = json.loads(Path('data/name-research/unnamed-world/reference-reconciliation384.json').read_text(encoding='utf-8'))['items']
    evidence = next(x for x in rows if x['peak'] == peak['peak'])
    if evidence['category'] != 'manual_geographic_review_shortlist':
        raise ValueError('Not in geographic review shortlist')
    con = duckdb.connect()
    pois = con.execute('''SELECT DISTINCT a.fsq_place_id,a.country,a.locality,a.post_town,
        a.address,a.longitude,a.latitude FROM read_parquet(?) p
        JOIN read_parquet(?) a USING(fsq_place_id) WHERE p.peak=?''',
        ['data/name-research/unnamed-world/local-parts/*.parquet',
         'data/name-research/unnamed-world/addresses.parquet', peak['peak']]).fetchall()
    con.close()
    near = [p for p in pois if Geod(ellps='WGS84').inv(*peak['coordinates'],p[-2],p[-1])[2] <= 750]
    if len(near) != peak['near_pois']:
        raise ValueError('Text evidence neighborhood changed')
    original = evidence['reference']
    field, address = set(), set()
    for p in near:
        pid,country,locality,post_town,text,lon,lat = p
        if country != original['country']: continue
        if any(contains(t,a) for t in (locality,post_town) for a in evidence['reference_aliases_used']): field.add(pid)
        if any(contains(text,a) for a in evidence['reference_aliases_used']): address.add(pid)
    if field != set(evidence['locality_text_ids']) or address != set(evidence['address_text_ids']):
        raise ValueError('Recorded text IDs changed')
    if evidence['ambiguous_text_ids']:
        raise ValueError('Competing references need separate geographic review')
    support = field | address
    if len(peak['candidates']) != 1:
        validate_reviewed_hierarchy(peak, original, near, support)
    hold_path=Path('docs/reference-text-evidence-exclusions.json')
    if hold_path.exists():
        held=json.loads(hold_path.read_text(encoding='utf-8'))['records']
        blocked={x['id'] for x in held if x['peak']==peak['peak'] and x['reference_id']==original['id']}
        if support & blocked:
            raise ValueError('Contradictory address text included in place-support votes; re-review required')
    ref = {**original, 'supporting_pois':len(support),
           'support_share':round(len(support)/len(near),3)}
    if ref != choice['ref']:
        raise ValueError('Reviewed text reference changed')
    # Retain the existing independent-facility, independent-publisher and distance guards.
    if choice.get('policy') == 'reviewed_census_place_boundary':
        from shapely.geometry import shape, Point
        record = json.loads(Path(choice['cartographic_review']).read_text(encoding='utf-8'))
        data = Path(record['local_geojson']).read_bytes()
        features = json.loads(data)['features']
        if (record['peak'] != peak['peak'] or record['reference_id'] != ref['id']
                or record['peak_coordinates'] != peak['coordinates']
                or record['decision'] != 'census_geographic_containment_reviewed_application_pending'
                or hashlib.sha256(data).hexdigest() != record['sha256']
                or ref['country'] != 'US' or len(features) != 1
                or features[0]['properties']['GEOID'] != record['census_geoid']
                or features[0]['properties']['BASENAME'] != ref['name']):
            raise ValueError('Reviewed Census identity changed')
        boundary = shape(features[0]['geometry'])
        if not boundary.is_valid or not boundary.contains(Point(*peak['coordinates'])):
            raise ValueError('Peak not inside reviewed Census place boundary')
    elif choice.get('policy') == 'reviewed_public_cartographic_area':
        from verify_reviewed_cartographic_area import verify
        record = json.loads(Path(choice['cartographic_review']).read_text(encoding='utf-8'))
        government = json.loads(Path(record['independent_government_coordinate_review']).read_text(encoding='utf-8'))
        if (record['peak'] != peak['peak'] or record['reference_id'] != ref['id']
                or record['decision'] != 'geographic_map_correspondence_confirmed_application_pending'
                or record['peak_coordinates'] != peak['coordinates']
                or government['peak'] != peak['peak'] or government['reference_id'] != ref['id']
                or government['country'] != ref['country'] or government['verification'] != 'primary_pdf_body'
                or Geod(ellps='WGS84').inv(*peak['coordinates'],*government['government_coordinates'])[2] > 500):
            raise ValueError('Reviewed area or independent locality evidence changed')
        verify(choice['cartographic_review'])
    elif choice.get('policy') == 'reviewed_public_cartographic_point':
        record = json.loads(Path(choice['cartographic_review']).read_text(encoding='utf-8'))
        pdf = Path(record['local_pdf'])
        if (record['peak'] != peak['peak'] or record['reference_id'] != ref['id']
                or record['decision'] != 'adopt_geographic_reference'
                or record['peak_coordinates'] != peak['coordinates']
                or record['country'] != ref['country']
                or hashlib.sha256(pdf.read_bytes()).hexdigest() != record['sha256']
                or Geod(ellps='WGS84').inv(*peak['coordinates'],*record['street_start_coordinates'])[2] > 50):
            raise ValueError('Reviewed public cartographic evidence changed')
    else:
        validate_anchor_review(choice,peak,ref)
    return ref
