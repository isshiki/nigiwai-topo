"""Attach N03 municipality names and prefecture ownership to national peaks.

Run after build_national.py. Uses official 2026 N03 ZIP; no POI re-fetch needed.
"""
import hashlib
import argparse
import io
import json
from pathlib import Path
from zipfile import ZipFile

import shapefile
from shapely.geometry import shape, Point
from shapely import STRtree
from shapely.ops import nearest_points
from national_grid import PROJECT

ROOT = Path('web/data/foursquare-japan')
ARCHIVE = Path('data/raw/admin/N03-20260101_GML.zip')


def main():
    global ROOT
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=ROOT)
    args = parser.parse_args()
    ROOT = args.input
    geometries, attributes, prefectures = [], [], {}
    with ZipFile(ARCHIVE) as archive:
        base = next(n[:-4] for n in archive.namelist() if n.endswith('.shp') and 'prefecture' not in n)
        encoding = archive.read(base + '.cpg').decode().strip() if base + '.cpg' in archive.namelist() else 'cp932'
        reader = shapefile.Reader(shp=io.BytesIO(archive.read(base + '.shp')),
                                  dbf=io.BytesIO(archive.read(base + '.dbf')), encoding=encoding)
        for row in reader.iterShapeRecords():
            p = row.record.as_dict()
            code = str(p.get('N03_007') or '')
            if len(code) != 5 or not p.get('N03_004'):
                continue
            geom = shape(row.shape.__geo_interface__)
            geometries.append(geom)
            attributes.append((code[:2], p['N03_004'] + (p.get('N03_005') or '')))
            b = geom.bounds
            entry = prefectures.setdefault(code[:2], {'name': p['N03_001'], 'bbox': list(b)})
            old = entry['bbox']
            entry['bbox'] = [min(old[0], b[0]), min(old[1], b[1]), max(old[2], b[2]), max(old[3], b[3])]
    tree = STRtree(geometries)
    cache = {}

    def locate(coords):
        key = tuple(coords)
        if key in cache:
            return cache[key]
        point = Point(coords)
        hits = tree.query(point, predicate='intersects')
        nearby = False
        index = int(hits[0]) if len(hits) else int(tree.nearest(point))
        if not len(hits):
            edge = nearest_points(point, geometries[index])[1]
            x, y = PROJECT.transform(*coords)
            ex, ey = PROJECT.transform(edge.x, edge.y)
            nearby = True
            if ((x-ex)**2 + (y-ey)**2)**.5 > 1500:
                cache[key] = ('', '', False)
                return cache[key]
        code, town = attributes[index]
        cache[key] = (code, town, nearby)
        return cache[key]

    def enrich(collection):
        for f in collection['features']:
            p = f['properties']
            if p.get('kind') != 'peak':
                continue
            code, town, nearby = locate(f['geometry']['coordinates'])
            p.update(pref_code=code, municipality=town, admin_nearby=nearby)
            if p.get('station_distance_m', 999999) > 1500 and town:
                p['name'] = town + ('付近' if nearby else '')
                p['name_basis'] = 'N03行政区域の市区町村名' + ('（区域外1.5km以内の参考名）' if nearby else '（峰が属する区域）')

    station_path = ROOT / 'stations.json'
    stations = json.loads(station_path.read_text(encoding='utf-8'))
    for station in stations:
        code, town, nearby = locate([station['lon'], station['lat']])
        station.update(pref_code=code, municipality=town)
    station_path.write_text(json.dumps(stations, ensure_ascii=False), encoding='utf-8')
    manifest_path = ROOT / 'manifest.json'
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    for item in manifest['datasets']:
        for chunk in item['chunks']:
            path = ROOT / chunk['file']
            collection = json.loads(path.read_text(encoding='utf-8'))
            enrich(collection)
            path.write_text(json.dumps(collection, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
            chunk['bytes'] = path.stat().st_size
        path = ROOT / item['peaks_file']
        collection = json.loads(path.read_text(encoding='utf-8'))
        enrich(collection)
        path.write_text(json.dumps(collection, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
        print(item['sigma'], item['category'], 'named', sum(bool(f['properties'].get('municipality')) for f in collection['features']), flush=True)
    regions = {'japan': {'name': '全国', 'bbox': manifest['bbox'], 'pref_codes': []}}
    blocks = [('hokkaido','北海道',1,1),('tohoku','東北',2,7),('kanto','関東',8,14),
              ('chubu','中部',15,23),('kinki','近畿',24,30),('chugoku','中国',31,35),
              ('shikoku','四国',36,39),('kyushu','九州',40,46),('okinawa','沖縄',47,47)]
    for key, name, start, end in blocks:
        codes = [f'{i:02}' for i in range(start,end+1)]
        boxes = [prefectures[c]['bbox'] for c in codes]
        regions[key] = {'name':name, 'pref_codes':codes, 'bbox':[min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes)]}
    for code, p in sorted(prefectures.items()):
        regions['pref-'+code] = {**p, 'pref_codes':[code]}
    (ROOT / 'regions.json').write_text(json.dumps(regions,ensure_ascii=False),encoding='utf-8')
    manifest['administrative_names'] = {'source':'国土数値情報 N03 2026 (国土交通省), CC BY 4.0',
        'file':str(ARCHIVE), 'sha256':hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
        'naming':'Station within 1500m; otherwise containing municipality, or nearest boundary within 1500m marked 付近.'}
    manifest_path.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    assert len(prefectures) == 47


if __name__ == '__main__':
    main()
