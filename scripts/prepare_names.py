"""Import public N02/N03 data, verify hashes, build station naming references."""
import argparse
from collections import defaultdict
import hashlib
import io
import json
from pathlib import Path
from zipfile import ZipFile

import shapefile
from shapely.geometry import shape, Point
from shapely.ops import unary_union

from region import BBOX, in_bbox
from national_grid import JAPAN_BBOX


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--raw-dir', type=Path, required=True)
    parser.add_argument('--national', action='store_true')
    args = parser.parse_args()
    provenance = json.loads((args.raw_dir / 'manifest.json').read_text(encoding='utf-8'))
    for key in ['n02', 'n03-13']:
        item = provenance[key]
        assert hashlib.sha256((args.raw_dir / item['file']).read_bytes()).hexdigest() == item['sha256'], key
    with ZipFile(args.raw_dir / provenance['n03-13']['file']) as z:
        boundary = json.loads(z.read(next(n for n in z.namelist() if n.endswith('.geojson'))))
    tokyo = unary_union([shape(f['geometry']) for f in boundary['features']])
    groups = defaultdict(list)
    with ZipFile(args.raw_dir / provenance['n02']['file']) as z:
        names = z.namelist()
        base = next(n[:-4] for n in names if n.endswith('_Station.shp') and 'Shift-JIS' in n)
        reader = shapefile.Reader(shp=io.BytesIO(z.read(base + '.shp')), dbf=io.BytesIO(z.read(base + '.dbf')), encoding='cp932')
        for row in reader.iterShapeRecords():
            attrs = row.record.as_dict()
            geometry = shape(row.shape.__geo_interface__)
            midpoint = geometry.interpolate(.5, normalized=True)
            if not args.national and tokyo.covers(midpoint) and not in_bbox(midpoint.x, midpoint.y):
                raise ValueError('A Tokyo station lies outside the acquisition bounds; expand the study area.')
            if args.national or in_bbox(midpoint.x, midpoint.y):
                groups[attrs.get('N02_005g') or attrs['N02_005c']].append((attrs, midpoint))
    stations = []
    for key, members in groups.items():
        lon = sum(p.x for _, p in members) / len(members)
        lat = sum(p.y for _, p in members) / len(members)
        inside = any(tokyo.covers(p) for _, p in members)
        stations.append({'id': str(key), 'name': members[0][0]['N02_005'], 'lon': lon, 'lat': lat, 'tokyo': inside})
    tokyo_stations = [s for s in stations if s['tokyo']]
    assert args.national or all(in_bbox(s['lon'], s['lat'], BBOX) for s in tokyo_stations)
    towns = []
    for f in boundary['features']:
        p = shape(f['geometry']).representative_point()
        if in_bbox(p.x, p.y, BBOX):
            props = f['properties']
            towns.append({'name': props.get('N03_004') or props.get('N03_003'), 'lon': p.x, 'lat': p.y})
    out = Path('data/raw/names-japan' if args.national else 'data/raw/names')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'stations.json').write_text(json.dumps(stations, ensure_ascii=False), encoding='utf-8')
    (out / 'towns.json').write_text(json.dumps(towns, ensure_ascii=False), encoding='utf-8')
    (out / 'manifest.json').write_text(json.dumps({'sources': {k: provenance[k] for k in ['n02', 'n03-13']}, 'station_groups': len(stations), 'tokyo_station_groups': len(tokyo_stations), 'bbox': JAPAN_BBOX if args.national else BBOX, 'naming': 'Nearest station within 1500m; else coordinate label.' if args.national else 'Nearest station within 1500m; else nearest municipality representative (approximate).'}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Station groups: {len(stations)}, Tokyo station groups: {len(tokyo_stations)}; national references' if args.national else f'Station groups: {len(stations)}, Tokyo station groups: {len(tokyo_stations)}; all inside build bounds')


if __name__ == '__main__':
    main()
