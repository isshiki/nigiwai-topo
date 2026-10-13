"""Maximum of the same world density grid within a uniform WGS84 station radius."""
import argparse
import hashlib
import json
import math
import subprocess
import sys
import time
from pathlib import Path

import duckdb
import numpy as np
from scipy.spatial import cKDTree

try:
    from .global_density import density, GEOD, DLON, DLAT
    from .build_station_tiers import sphere
except ImportError:
    from global_density import density, GEOD, DLON, DLAT
    from build_station_tiers import sphere

ROOT = Path('data/station-radius')
SOURCE = Path('data/world-build/active.parquet')
DATA = Path('web/station-tier-data.json')


def maximum_at_station(points, station, radius=800):
    # Longitude cells shrink toward the poles; size must adapt worldwide.
    ix = int(np.rint((station['lon'] + 180) / DLON))
    iy = int(np.rint((station['lat'] + 90) / DLAT))
    _, _, dx = GEOD.inv(station['lon'] - DLON / 2, station['lat'], station['lon'] + DLON / 2, station['lat'])
    padding = max(16, int(math.ceil(radius / dx)) + 2)
    xs, ys, z = density(points, ix, iy, 200, size=1, padding=padding)
    xx, yy = np.meshgrid(xs, ys)
    _, _, distances = GEOD.inv(np.full(xx.size, station['lon']), np.full(xx.size, station['lat']), xx.ravel(), yy.ravel())
    eligible = distances.reshape(z.shape) <= radius
    assert eligible.any()
    values = np.where(eligible, z, -np.inf)
    row, col = np.unravel_index(np.argmax(values), values.shape)
    return {'density': round(float(z[row, col])), 'raw_density': float(z[row, col]), 'lon': float(xs[col]), 'lat': float(ys[row]), 'distance_m': float(distances.reshape(z.shape)[row, col]), 'tested_cells': int(eligible.sum())}


def prepare_points(stations, signature, excluded):
    target = ROOT / 'points.npy'
    meta = ROOT / 'points-signature.txt'
    if target.exists() and meta.exists() and meta.read_text() == signature:
        return np.load(target)
    station_tree = cKDTree(sphere(np.array([s['lon'] for s in stations]), np.array([s['lat'] for s in stations])))
    con = duckdb.connect(config={'threads': 2, 'memory_limit': '2GB'})
    con.execute("SELECT fsq_place_id,longitude,latitude FROM read_parquet(?) WHERE longitude BETWEEN 122 AND 154 AND latitude BETWEEN 20 AND 46", [str(SOURCE)])
    chunks = []
    while rows := con.fetchmany(100000):
        accepted = [r for r in rows if r[0] not in excluded]
        xy = np.array([[r[1], r[2]] for r in accepted])
        if not len(xy):
            continue
        d, _ = station_tree.query(sphere(xy[:, 0], xy[:, 1]))
        # More than 800m station radius + diagonal 4-sigma support + rounding.
        chunks.append(xy[d <= 2 * math.sin(2500 / (2 * 6371000))])
    points = np.concatenate(chunks)
    np.save(target, points)
    meta.write_text(signature)
    return points


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--sample', action='store_true')
    parser.add_argument('--compute-only', action='store_true', help='Cache all circle maxima without changing published station data')
    args = parser.parse_args()
    ROOT.mkdir(parents=True, exist_ok=True)
    data = json.loads(DATA.read_text(encoding='utf-8'))
    stations = data['stations']
    policy = Path('docs/held-density-exclusions-v6.json')
    excluded = {r['id'] for r in json.loads(policy.read_text(encoding='utf-8'))['records']}
    signature = hashlib.sha256(json.dumps({'source_size': SOURCE.stat().st_size, 'source_mtime_ns': SOURCE.stat().st_mtime_ns, 'policy': hashlib.sha256(policy.read_bytes()).hexdigest(), 'stations': [(s['id'], s['lon'], s['lat']) for s in stations], 'radius': 800, 'sigma': 200, 'algorithm': 1}).encode()).hexdigest()
    print('Preparing the original map input near stations', flush=True)
    points = prepare_points(stations, signature, excluded)
    tree = cKDTree(sphere(points[:, 0], points[:, 1]))
    print('Nearby source records:', len(points), flush=True)
    cache = ROOT / 'scores.json'
    previous = json.loads(cache.read_text()) if cache.exists() else {}
    results = previous.get('results', {}) if previous.get('signature') == signature else {}
    selected = stations if not args.sample else [s for s in stations if s['name'] in ['御茶ノ水', '両国', '池袋', '渋谷', '銀座', '新宿', '原宿', '明治神宮前'] and s['pref_code'] == '13']
    started = time.perf_counter()
    for number, s in enumerate(selected, 1):
        if s['id'] not in results:
            nearby = tree.query_ball_point(sphere(np.array([s['lon']]), np.array([s['lat']]))[0], 2 * math.sin(2300 / (2 * 6371000)))
            results[s['id']] = maximum_at_station(points[nearby], s)
        if args.sample or number % 250 == 0 or number == len(selected):
            pending = cache.with_suffix('.pending')
            pending.write_text(json.dumps({'signature': signature, 'results': results}, separators=(',', ':')))
            pending.replace(cache)
            print(json.dumps({'completed': number, 'total': len(selected), 'elapsed_s': round(time.perf_counter() - started, 1), 'station': s['name'], 'density': results[s['id']]['density']}, ensure_ascii=True), flush=True)
    if args.sample or args.compute_only:
        return
    for s in stations:
        result = results[s['id']]
        s['score'] = result['density']
        s['peak'] = {'name': s['name'] + '周辺の最高密度地点', 'density': s['score'], 'lon': result['lon'], 'lat': result['lat'], 'reference_station_id': s['id'], 'distance_m': result['distance_m'], 'raw_density': result['raw_density']}
    values = np.array([s['score'] for s in stations])
    data['thresholds'] = dict(zip(['SS', 'S', 'A', 'B', 'C'], map(float, np.quantile(values, [.99, .95, .8, .5, .2]))))
    for s in stations:
        s['tier'] = next((t for t, cutoff in data['thresholds'].items() if s['score'] > 0 and s['score'] >= cutoff), 'D')
    data.update({'metric': 'station_radius_max_density', 'radius_m': 800, 'sigma_m': 200, 'matched_count': len(stations), 'unmatched_count': 0, 'input_signature': signature, 'grid_step_degrees': DLON, 'zero_density_count': int((values == 0).sum())})
    pending = DATA.with_suffix('.pending')
    pending.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    pending.replace(DATA)
    report = {'complete': True, 'station_count': len(stations), 'radius_m': 800, 'tiers': {t: sum(s['tier'] == t for s in stations) for t in ['SS', 'S', 'A', 'B', 'C', 'D']}, 'examples': {s['name']: {'density': s['score'], 'tier': s['tier'], 'distance_m': s['peak']['distance_m']} for s in stations if s['name'] in ['御茶ノ水', '両国', '池袋', '渋谷', '銀座', '新宿'] and s['pref_code'] == '13'}}
    Path('data/validation/station-radius-density.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    subprocess.run([sys.executable, 'scripts/pack_station_tier_data.py'], check=True)
    print(json.dumps(report, ensure_ascii=True), flush=True)


if __name__ == '__main__':
    main()
