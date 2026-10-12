"""Validate individually reviewed address anchors; never infer city membership."""
from pathlib import Path
import json
from urllib.parse import urlparse
import duckdb
from pyproj import Geod


def validate_anchor_review(choice, peak, reference):
    review = json.loads(Path('docs/unnamed-world-official-anchor-reviews.json').read_text(encoding='utf-8'))
    record = next(x for x in review['items'] if x['peak'] == peak['peak'])
    if record['decision'] != 'adopt' or record['reference_id'] != reference['id']:
        raise ValueError('Anchor review identity is not approved')
    anchors = record['anchors']
    if len({x['facility_key'] for x in anchors}) < 2 or len({x['raw_address'] for x in anchors}) < 2:
        raise ValueError('Duplicate facilities are not independent anchors')
    if len({x['poi_id'] for x in anchors}) < 2:
        raise ValueError('Repeated source POI is not an independent anchor')
    if len({urlparse(x['source_url']).hostname for x in anchors}) < 2:
        raise ValueError('Two independent source publishers required')
    con = duckdb.connect()
    distances = []
    for anchor in anchors:
        rows = con.execute('SELECT name,address,locality,country,longitude,latitude FROM read_parquet(?) WHERE fsq_place_id=?',
                           ['data/name-research/unnamed-world/addresses.parquet', anchor['poi_id']]).fetchall()
        if len(rows) != 1:
            raise ValueError('Missing or nonunique source POI')
        name, address, locality, country, lon, lat = rows[0]
        if [name, address, locality, country] != anchor['raw_identity']:
            raise ValueError('Source address identity changed')
        if address != anchor['raw_address']:
            raise ValueError('Declared independent address differs from source POI')
        if country != reference['country'] or anchor['official_locality'] != reference['name']:
            raise ValueError('Anchor country or locality mismatch')
        if anchor['verification'] not in ('public_page_body', 'official_search_excerpt'):
            raise ValueError('Unverified address source')
        if address is None:
            if (anchor.get('evidence_kind') != 'official_facility_coordinates'
                    or anchor.get('coordinate_crs') != 'WGS84'
                    or anchor['verification'] != 'public_page_body'):
                raise ValueError('Missing address requires explicit official coordinate evidence')
            official = anchor.get('official_coordinates', [])
            if (len(official) != 2
                    or Geod(ellps='WGS84').inv(lon, lat, *official)[2] > 100):
                raise ValueError('Official facility coordinates do not match source position')
        distance = Geod(ellps='WGS84').inv(*peak['coordinates'], lon, lat)[2]
        if distance > 750:
            raise ValueError('Facility outside reviewed neighborhood')
        distances.append(distance)
    if min(distances) > 100:
        raise ValueError('No independently located facility near peak')
    return (.8, 100, 1000, 20, 20)
