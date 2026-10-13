"""Prototype nationwide station scores; no POI retrieval or credentials required."""
import hashlib
import io
import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from zipfile import ZipFile

import numpy as np
import shapefile
from pyproj import Geod

ROOT = Path('data/raw/station-tier')
GEOD = Geod(ellps='WGS84')


def sphere(lon, lat):
    lon, lat = np.radians(lon), np.radians(lat)
    return np.column_stack([np.cos(lat) * np.cos(lon), np.cos(lat) * np.sin(lon), np.sin(lat)])


def merge_same_name_stations(stations, limit_m=500):
    """Merge exact names within one municipality; cap all pairwise distances."""
    named = defaultdict(list)
    for s in stations:
        named[(s['name'], s['pref_code'], s['municipality'])].append(s)
    merged = []
    for members in named.values():
        clusters = []
        for s in sorted(members, key=lambda s: s['id']):
            cluster = next((group for group in clusters if all(
                GEOD.inv(s['lon'], s['lat'], other['lon'], other['lat'])[2] <= limit_m
                for other in group)), None)
            if cluster is None:
                clusters.append([s])
            else:
                cluster.append(s)
        for group in clusters:
            s = dict(group[0])
            s['source_station_ids'] = [r['id'] for r in group]
            s['lon'] = sum(r['lon'] for r in group) / len(group)
            s['lat'] = sum(r['lat'] for r in group) / len(group)
            routes = {l['id']: l for r in group for l in r['lines']}
            s['lines'] = [routes[key] for key in sorted(routes)]
            merged.append(s)
    merged.sort(key=lambda s: s['id'])
    owners = {source_id: i for i, s in enumerate(merged) for source_id in s['source_station_ids']}
    return merged, np.array([owners[s['id']] for s in stations])


def main():
    source = json.loads(Path('data/raw/names-japan/manifest.json').read_text(encoding='utf-8'))['sources']['n02']
    archive = ROOT / source['file']
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == source['sha256']
    stations = json.loads(Path('data/distribution/foursquare-japan/stations.json').read_text(encoding='utf-8'))
    regions = json.loads(Path('data/distribution/foursquare-japan/regions.json').read_text(encoding='utf-8'))
    lines = defaultdict(set)
    with ZipFile(archive) as z:
        base = next(n[:-4] for n in z.namelist() if n.endswith('_Station.shp') and 'Shift-JIS' in n)
        reader = shapefile.Reader(shp=io.BytesIO(z.read(base + '.shp')), dbf=io.BytesIO(z.read(base + '.dbf')), encoding='cp932')
        for record in reader.iterRecords():
            a = record.as_dict()
            key = str(a.get('N02_005g') or a['N02_005c'])
            lines[key].add((a['N02_004'], a['N02_003']))
    assert len({s['id'] for s in stations}) == len(stations)
    for s in stations:
        assert lines[s['id']], s['id']
        s['lines'] = [{'company': c, 'name': n, 'id': c + ' / ' + n} for c, n in sorted(lines[s['id']])]
        s['prefecture'] = regions['pref-' + s['pref_code']]['name']
    source_station_count = len(stations)
    stations, _ = merge_same_name_stations(stations)
    for s in stations:
        s.pop('tokyo', None)
    payload = {'prototype': True, 'snapshot': '2026-09-15', 'station_source_sha256': source['sha256'], 'merge_distance_m': 500, 'source_station_count': source_station_count, 'station_count': len(stations), 'stations': stations}
    Path('web/station-tier-data.json').write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    report = {'source_station_count': source_station_count, 'station_count': len(stations), 'merged_groups': [{'id': s['id'], 'name': s['name'], 'members': s['source_station_ids']} for s in stations if len(s['source_station_ids']) > 1]}
    Path('data/validation/station-tier-build.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    subprocess.run([sys.executable, 'scripts/build_shared_density_assets.py', '--apply'], check=True)
    subprocess.run([sys.executable, 'scripts/pack_station_tier_data.py'], check=True)


if __name__ == '__main__':
    main()
