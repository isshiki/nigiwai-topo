"""Resume worldwide reference-radius maxima; never overwrite the live map."""
import hashlib
import argparse
import json
import math
import time
from collections import defaultdict
from pathlib import Path
import duckdb
import numpy as np
from scipy.spatial import cKDTree
from build_station_radius_density import maximum_at_station
from build_station_tiers import sphere
from global_density import GEOD, DLON

ROOT = Path('data/shared-density')
SOURCE = Path('data/world-build/active.parquet')


def replace_checkpoint(pending, target):
    for attempt in range(30):
        try:
            pending.replace(target)
            return
        except PermissionError:
            if attempt == 29:
                raise
            time.sleep(.2)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--initial-references', type=Path, default=ROOT / 'references.json')
    args = parser.parse_args()
    inventory = json.loads(args.initial_references.read_text(encoding='utf-8'))
    records = inventory['records']
    policy = Path('docs/held-density-exclusions-v6.json')
    signature = hashlib.sha256(json.dumps({'source': [SOURCE.stat().st_size, SOURCE.stat().st_mtime_ns], 'policy': hashlib.sha256(policy.read_bytes()).hexdigest(), 'records': records, 'radius_m': 800, 'sigma_m': 200, 'version': 1}, ensure_ascii=False).encode()).hexdigest()
    prepared = ROOT / 'input-signature.txt'
    folder = ROOT / ('input-' + signature[:12])
    groups = defaultdict(list)
    needed = set()
    for r in records:
        x = min(179, int(math.floor((r['lon'] + 180) / 2)))
        y = min(89, int(math.floor((r['lat'] + 90) / 2)))
        groups[x, y].append(r)
        for a in range(x - 1, x + 2):
            for b in range(max(0, y - 1), min(89, y + 1) + 1):
                needed.add((a % 180, b))
    if not prepared.exists() or prepared.read_text() != signature:
        print('Preparing spatially partitioned original POI coordinates', flush=True)
        con = duckdb.connect(config={'threads': 2, 'memory_limit': '2GB'})
        con.execute('CREATE TABLE needed(x INTEGER,y INTEGER)')
        con.executemany('INSERT INTO needed VALUES (?,?)', sorted(needed))
        con.execute('CREATE TABLE held(id VARCHAR)')
        con.executemany('INSERT INTO held VALUES (?)', [(r['id'],) for r in json.loads(policy.read_text(encoding='utf-8'))['records']])
        folder.mkdir(parents=True, exist_ok=True)
        source_sql = SOURCE.as_posix().replace("'", "''")
        folder_sql = folder.as_posix().replace("'", "''")
        con.execute(f"COPY (SELECT longitude,latitude,cell_x,cell_y FROM read_parquet('{source_sql}') p WHERE EXISTS(SELECT 1 FROM needed n WHERE n.x=p.cell_x AND n.y=p.cell_y) AND NOT EXISTS(SELECT 1 FROM held h WHERE h.id=p.fsq_place_id)) TO '{folder_sql}' (FORMAT PARQUET, PARTITION_BY(cell_x,cell_y), COMPRESSION ZSTD, OVERWRITE_OR_IGNORE TRUE)")
        con.close()
        prepared.write_text(signature)
    cache = ROOT / 'maxima.json'
    old = json.loads(cache.read_text(encoding='utf-8')) if cache.exists() else {}
    results = old.get('results', {}) if old.get('signature') == signature else {}
    con = duckdb.connect(config={'threads': 2, 'memory_limit': '2GB'})
    for group_number, ((x, y), group) in enumerate(sorted(groups.items()), 1):
        if all(r['id'] in results for r in group):
            continue
        files = [str(f) for a in range(x - 1, x + 2) for b in range(max(0, y - 1), min(89, y + 1) + 1) for f in (folder / f'cell_x={a % 180}' / f'cell_y={b}').glob('*.parquet')]
        points = con.execute('SELECT longitude,latitude FROM read_parquet(?)', [files]).fetchnumpy() if files else {'longitude': [], 'latitude': []}
        xy = np.column_stack([points['longitude'], points['latitude']])
        tree = cKDTree(sphere(xy[:, 0], xy[:, 1])) if len(xy) else None
        for r in group:
            if r['id'] in results:
                continue
            if abs(r['lat']) > 84.95:
                raise ValueError('Reference too close to unsupported polar display limit: ' + r['id'])
            indices = tree.query_ball_point(sphere(np.array([r['lon']]), np.array([r['lat']]))[0], 2 * math.sin(2300 / (2 * 6371000))) if tree else []
            results[r['id']] = maximum_at_station(xy[indices], r)
        pending = cache.with_suffix('.pending')
        pending.write_text(json.dumps({'signature': signature, 'complete': len(results) == len(records), 'reference_count': len(records), 'results': results}, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
        replace_checkpoint(pending, cache)
        print(json.dumps({'completed': len(results), 'total': len(records), 'group': group_number, 'groups': len(groups)}, separators=(',', ':')), flush=True)
    # The coordinate audit may recover additional references during the long
    # initial spatial extraction. Accept only additions, never changed anchors.
    latest = json.loads((ROOT / 'references.json').read_text(encoding='utf-8'))['records']
    by_id = {r['id']: r for r in latest}
    if any(by_id.get(r['id']) != r for r in records):
        raise ValueError('Existing reference changed during computation')
    for r in latest:
        if r['id'] in results:
            continue
        _, _, dx = GEOD.inv(r['lon'] - DLON / 2, r['lat'], r['lon'] + DLON / 2, r['lat'])
        margin = 2500 * DLON / dx
        points = con.execute('SELECT longitude,latitude FROM read_parquet(?) WHERE longitude BETWEEN ? AND ? AND latitude BETWEEN ? AND ? AND fsq_place_id NOT IN (SELECT unnest(?))', [str(SOURCE), r['lon'] - margin, r['lon'] + margin, r['lat'] - .025, r['lat'] + .025, [v['id'] for v in json.loads(policy.read_text(encoding='utf-8'))['records']]]).fetchnumpy()
        xy = np.column_stack([points['longitude'], points['latitude']])
        results[r['id']] = maximum_at_station(xy, r)
    payload = {'source_bytes': SOURCE.stat().st_size, 'source_mtime_ns': SOURCE.stat().st_mtime_ns, 'policy_sha256': hashlib.sha256(policy.read_bytes()).hexdigest(), 'radius_m': 800, 'sigma_m': 200, 'reference_sha256': hashlib.sha256(json.dumps(latest, ensure_ascii=False).encode()).hexdigest(), 'signature': signature, 'complete': len(results) == len(latest), 'reference_count': len(latest), 'results': results}
    pending = cache.with_suffix('.pending')
    pending.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    replace_checkpoint(pending, cache)
    print('Complete: shared worldwide radius results cached; live assets unchanged', flush=True)


if __name__ == '__main__':
    main()
