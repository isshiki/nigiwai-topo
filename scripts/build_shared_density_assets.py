"""Generate both displays from one verified world-radius result file."""
import argparse
import csv
import hashlib
import json
import re
from collections import Counter
from pathlib import Path
import numpy as np
from build_peak_index import write_index

ROOT = Path('data/shared-density')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args()
    refs = json.loads((ROOT / 'references.json').read_text(encoding='utf-8'))
    cache = json.loads((ROOT / 'maxima.json').read_text(encoding='utf-8'))
    records = refs['records']
    assert refs['report']['unresolved_peaks'] == 0
    assert cache['complete'] and len(cache['results']) == len(records)
    assert cache['radius_m'] == 800 and cache['sigma_m'] == 200
    assert cache['reference_sha256'] == hashlib.sha256(json.dumps(records, ensure_ascii=False).encode()).hexdigest()
    assert cache['source_bytes'] == Path('data/world-build/active.parquet').stat().st_size
    assert cache['source_mtime_ns'] == Path('data/world-build/active.parquet').stat().st_mtime_ns
    assert cache['policy_sha256'] == hashlib.sha256(Path('docs/held-density-exclusions-v6.json').read_bytes()).hexdigest()
    output = ROOT / 'release'
    output.mkdir(exist_ok=True)
    station_data = json.loads(Path('web/station-tier-data.json').read_text(encoding='utf-8'))
    station_lookup = {s['id']: s for s in station_data['stations']}
    repeated = Counter(r['name'] for r in records)
    repeated_local = Counter((s['name'], s['prefecture'], s['municipality']) for s in station_data['stations'])
    clarified = {'OpenStreetMap:node/5351281122': 'イチョン駅（ソウル）', 'GeoNames:1843702': 'イチョン市', 'OpenStreetMap:node/9271807339': '市庁駅（テジョン）', 'OpenStreetMap:node/355173718': '市庁駅（プサン）', 'OpenStreetMap:node/355172716': 'オサン駅', 'GeoNames:1839652': 'オサン市', 'OpenStreetMap:node/1768537544': 'プサン駅', 'GeoNames:1838524': 'プサン市'}
    features = []
    for r in records:
        result = cache['results'][r['id']]
        label = clarified.get(r['id'], r['name'])
        if r.get('station_id') and repeated[r['name']] > 1:
            station = station_lookup[r['station_id']]
            qualifier = station['prefecture'] + '・' + station['municipality']
            if repeated_local[station['name'], station['prefecture'], station['municipality']] > 1:
                qualifier += '／' + re.sub(r'^\d+号線', '', station['lines'][0]['name']).strip('()')
            label += '（' + qualifier + '）'
        assert result['distance_m'] <= 800
        assert result['density'] == round(result['raw_density'])
        features.append({'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [result['lon'], result['lat']]}, 'properties': {'kind': 'peak', 'shared_reference': True, 'reference_id': r['id'], 'display_name': label, 'name': label, 'name_source': r['source'], 'name_source_ids': r.get('source_ids', [r['id'].split(':', 1)[-1]]), 'density': result['density'], 'radius_m': 800, 'anchor_lon': r['lon'], 'anchor_lat': r['lat'], 'station_id': r.get('station_id')}})
    visible = [f for f in features if f['properties']['density'] >= 800]
    write_index(visible, output / 'reference-index')
    (output / 'references.geojson').write_text(json.dumps({'type': 'FeatureCollection', 'features': features}, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    data = json.loads(Path('web/station-tier-data.json').read_text(encoding='utf-8'))
    by_id = {f['properties']['station_id']: f for f in features if f['properties']['station_id']}
    for s in data['stations']:
        f = by_id[s['id']]
        p = f['properties']
        assert s['lon'] == p['anchor_lon'] and s['lat'] == p['anchor_lat'], 'Station anchor changed; recalculate the shared density cache'
        s['score'] = p['density']
        s['peak'] = {'name': p['display_name'], 'lon': f['geometry']['coordinates'][0], 'lat': f['geometry']['coordinates'][1], 'reference_station_id': s['id'], 'density': s['score']}
    values = np.array([s['score'] for s in data['stations']])
    data['thresholds'] = dict(zip(['SS', 'S', 'A', 'B', 'C'], map(float, np.quantile(values, [.99, .95, .8, .5, .2]))))
    for s in data['stations']:
        s['tier'] = next((t for t, cutoff in data['thresholds'].items() if s['score'] >= cutoff), 'D')
    data.update(metric='station_radius_max_density', radius_m=800, sigma_m=200, matched_count=len(data['stations']), unmatched_count=0, shared_reference_sha256=cache['reference_sha256'])
    (output / 'station-tier-data.json').write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    with (output / 'world-reference-density.csv').open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.writer(stream)
        writer.writerow(['参照ID', '地名', '登録密度_件_per_km2', '最大点_緯度', '最大点_経度', '参照点_緯度', '参照点_経度', '半径_m'])
        for f in sorted(visible, key=lambda f: -f['properties']['density']):
            p = f['properties'];lon, lat = f['geometry']['coordinates']
            writer.writerow([p['reference_id'], p['display_name'], p['density'], lat, lon, p['anchor_lat'], p['anchor_lon'], 800])
    report = {'reference_count': len(features), 'visible_reference_count': len(visible), 'station_count': len(data['stations']), 'radius_m': 800, 'sigma_m': 200, 'tiers': {t: sum(s['tier'] == t for s in data['stations']) for t in ['SS', 'S', 'A', 'B', 'C', 'D']}}
    (output / 'manifest.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    if args.apply:
        Path('web/station-tier-data.json').write_bytes((output / 'station-tier-data.json').read_bytes())
    print(json.dumps(report))


if __name__ == '__main__':
    main()
