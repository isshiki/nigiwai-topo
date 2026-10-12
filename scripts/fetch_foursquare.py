"""Acquire full-AOI FSQ OS Places; never print remote credential-bearing errors."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from contextlib import ExitStack

import duckdb
from region import FETCH_BBOX


def load_token(path):
    token = os.environ.get('FSQ_OS_PLACES_TOKEN')
    if token:
        return token
    if path.is_file():
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            key, sep, value = line.partition('=')
            if sep and key.strip() == 'FSQ_OS_PLACES_TOKEN':
                return value.strip().strip('\"\'')
    raise ValueError('Missing FSQ_OS_PLACES_TOKEN. Save a personal Portal token in .env; never paste it in chat.')


def records(cursor):
    names = [c[0] for c in cursor.description]
    return [dict(zip(names, row)) for row in cursor.fetchall()]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--env-file', type=Path, default=Path('.env'))
    parser.add_argument('--national', action='store_true', help='Stream all JP records into Japan-wide grid shards')
    parser.add_argument('--world', action='store_true', help='Acquire the fixed world snapshot as resumable country Parquet files')
    parser.add_argument('--world-plan', action='store_true', help='Inventory the world snapshot without downloading place files')
    parser.add_argument('--service-only', action='store_true', help='Acquire the additional JP service category into separate shards')
    parser.add_argument('--pilot', choices=['sg-singapore','gb-london','is-reykjavik'], help='Acquire a bounded overseas pilot with a metric halo')
    args = parser.parse_args()
    if (args.world or args.world_plan) and (args.national or args.pilot or args.service_only):
        parser.error('World acquisition cannot be combined with national/pilot flags')
    if args.service_only and not args.national:
        parser.error('--service-only requires --national')
    if args.pilot and args.national:
        parser.error('--pilot and --national are mutually exclusive')
    token = load_token(args.env_file)
    Path('data/cache/duckdb').mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(config={'extension_directory': 'data/cache/duckdb', 'threads': 2, 'memory_limit': '2GB'})
    try:
        con.execute('INSTALL httpfs; LOAD httpfs; INSTALL iceberg; LOAD iceberg')
        con.execute("CREATE SECRET fsq_portal (TYPE iceberg, TOKEN '" + token.replace("'", "''") + "')")
        con.execute("ATTACH 'places' AS places (TYPE iceberg, SECRET fsq_portal, ENDPOINT 'https://catalog.h3-hub.foursquare.com/iceberg', READ_ONLY)")
        pins_path = Path('data/cache/foursquare/snapshots.json')
        pins = json.loads(pins_path.read_text()) if pins_path.is_file() else {}
        tables = {}
        for kind, table in [('places', 'places.datasets.places_os'), ('categories', 'places.datasets.categories_os')]:
            snapshots = records(con.execute(f'SELECT snapshot_id, timestamp_ms FROM iceberg_snapshots({table}) ORDER BY timestamp_ms DESC'))
            selected = next((s for s in snapshots if kind not in pins or str(s['snapshot_id']) == pins[kind]['snapshot_id']), None)
            if selected is None:
                raise ValueError('Pinned snapshot unavailable')
            sid = str(selected['snapshot_id'])
            if not sid.isascii() or not sid.isdigit():
                raise ValueError('Invalid snapshot ID')
            pins[kind] = {'snapshot_id': sid, 'timestamp': str(selected['timestamp_ms'])}
            tables[kind] = f'{table} AT (VERSION => {sid})'
        cats = records(con.execute('SELECT * FROM ' + tables['categories']))
        category_map = {}
        for c in cats:
            category_map[c['category_id']] = classify_category(c)
        if args.world or args.world_plan:
            from fetch_world import fetch_world
            fetch_world(con, tables['places'], cats, pins, plan_only=not args.world)
            return
        if args.pilot:
            from world_pipeline import fetch_pilot
            fetch_pilot(con, tables['places'], cats, pins, args.pilot)
            return
        if args.national:
            pins_path.parent.mkdir(parents=True, exist_ok=True)
            pins_path.write_text(json.dumps(pins, indent=2), encoding='utf-8')
            fetch_national(con, tables['places'], category_map, pins, cats, args.service_only)
            return
        west, south, east, north = FETCH_BBOX
        params = ['JP', west, east, south, north]
        predicate = 'country=? AND longitude BETWEEN ? AND ? AND latitude BETWEEN ? AND ?'
        expected = con.execute(f'SELECT count(*) FROM {tables["places"]} WHERE {predicate}', params).fetchone()[0]
        rows = records(con.execute(f'SELECT fsq_place_id, name, longitude, latitude, fsq_category_ids, date_closed FROM {tables["places"]} WHERE {predicate}', params))
        if len(rows) != expected or len({r['fsq_place_id'] for r in rows}) != expected:
            raise ValueError('Count or unique-ID mismatch')
        points = []
        for r in rows:
            categories = {category_map.get(cid, 'other') for cid in r['fsq_category_ids'] or []}
            points.append({'id': r['fsq_place_id'], 'name': r['name'], 'lon': float(r['longitude']), 'lat': float(r['latitude']), 'category': 'food' if 'food' in categories else 'shopping' if 'shopping' in categories else 'other', 'date_closed': r['date_closed'], 'category_ids': r['fsq_category_ids']})
        raw = {'source': 'Foursquare OS Places（snapshot固定）', 'synthetic': False, 'bbox': FETCH_BBOX, 'points': points, 'count': expected, 'snapshots': pins, 'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'source_url': 'https://docs.foursquare.com/data-products/docs/access-fsq-os-places', 'quality': 'Closed places retained for baseline. Category mapping provisional; not a count of currently open businesses.'}
        out = Path('data/raw/foursquare')
        out.mkdir(parents=True, exist_ok=True)
        target = out / 'points.json'
        target.write_text(json.dumps(raw, ensure_ascii=False, default=str), encoding='utf-8')
        (out / 'categories.json').write_text(json.dumps(cats, ensure_ascii=False, default=str), encoding='utf-8')
        manifest = {k: v for k, v in raw.items() if k != 'points'}
        manifest['sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
        (out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
        pins_path.parent.mkdir(parents=True, exist_ok=True)
        pins_path.write_text(json.dumps(pins, indent=2), encoding='utf-8')
        print(f'FSQ full AOI: {expected} records; count and unique IDs verified')
    finally:
        con.close()


def classify_category(c):
    if c.get('level1_category_name') in ['Business and Professional Services', 'Health and Medicine']:
        return 'service'
    # Hierarchy identifies services; legacy food/shopping matching remains below.
    text = ' '.join(str(v).lower() for k, v in c.items() if 'name' in k)
    if any(x in text for x in ['dining', 'restaurant', 'café', 'coffee', 'bar', 'pub']):
        return 'food'
    if any(x in text for x in ['retail', 'store', 'shopping', 'shop']):
        return 'shopping'
    return 'service' if c.get('level1_category_name') in ['Business and Professional Services', 'Health and Medicine'] else 'other'


def fetch_national(con, table, category_map, pins, cats, service_only=False):
    from national_grid import PROJECT, tile_key, tile_bbox, JAPAN_BBOX
    out = Path('data/raw/foursquare-japan-service' if service_only else 'data/raw/foursquare-japan')
    out.mkdir(parents=True, exist_ok=True)
    (out / 'categories.json').write_text(json.dumps(cats, ensure_ascii=False, default=str), encoding='utf-8')
    target = out / 'manifest.json'
    if target.exists():
        previous = json.loads(target.read_text(encoding='utf-8'))
        if previous.get('complete') and previous['snapshots'] == pins and (not service_only or previous.get('classification_version') == 2):
            print('Japan snapshot already acquired; reusing complete local shards', flush=True)
            return
    west, south, east, north = JAPAN_BBOX
    predicate = 'country=? AND longitude BETWEEN ? AND ? AND latitude BETWEEN ? AND ?'
    params = ['JP', west, east, south, north]
    if service_only:
        service_ids = [cid for cid, kind in category_map.items() if kind == 'service']
        priority_ids = [cid for cid, kind in category_map.items() if kind in ['food', 'shopping']]
        predicate += ' AND list_has_any(fsq_category_ids, ?) AND NOT list_has_any(fsq_category_ids, ?)'
        params.extend([service_ids, priority_ids])
    total_jp = con.execute(f'SELECT count(*) FROM {table} WHERE country=?', ['JP']).fetchone()[0]
    expected, unique = con.execute(f'SELECT count(*), count(DISTINCT fsq_place_id) FROM {table} WHERE {predicate}', params).fetchone()
    if expected != unique:
        raise ValueError('Duplicate national IDs')
    print(f'Japan: {expected} records in geographic guard bounds' + (' (service subset)' if service_only else f'; {total_jp - expected} outside/invalid'), flush=True)
    con.execute(f'SELECT fsq_place_id, name, longitude, latitude, fsq_category_ids, date_closed FROM {table} WHERE {predicate}', params)
    counts, active_counts, files, closed, actual = {}, {}, {}, 0, 0
    with ExitStack() as stack:
        while rows := con.fetchmany(20000):
            xs, ys = PROJECT.transform([r[2] for r in rows], [r[3] for r in rows])
            for r, x, y in zip(rows, xs, ys):
                key = tile_key(x, y)
                if key not in files:
                    files[key] = stack.enter_context((out / f'{key[0]}_{key[1]}.jsonl').open('w', encoding='utf-8'))
                categories = {category_map.get(cid, 'other') for cid in r[4] or []}
                category = 'food' if 'food' in categories else 'shopping' if 'shopping' in categories else 'service' if 'service' in categories else 'other'
                point = {'id': r[0], 'name': r[1], 'lon': r[2], 'lat': r[3], 'x': x, 'y': y, 'category': category, 'date_closed': str(r[5]) if r[5] else None}
                files[key].write(json.dumps(point, ensure_ascii=False, separators=(',', ':')) + '\n')
                counts[key] = counts.get(key, 0) + 1
                if not r[5]:
                    active_counts[category] = active_counts.get(category, 0) + 1
                closed += bool(r[5])
                actual += 1
            if actual % 200000 == 0:
                print(f'Acquired {actual}/{expected}', flush=True)
    if actual != expected:
        raise ValueError('National count mismatch')
    parts = []
    for (i, j), count in sorted(counts.items()):
        path = out / f'{i}_{j}.jsonl'
        parts.append({'i': i, 'j': j, 'count': count, 'file': path.name, 'bbox': tile_bbox(i, j), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    manifest = {'source': 'Foursquare OS Places（snapshot固定・日本全国）', 'complete': True, 'classification_version': 2, 'bbox': JAPAN_BBOX, 'count': actual, 'country_records': total_jp, 'outside_or_invalid': total_jp - actual, 'known_closed': closed, 'active_categories': active_counts, 'snapshots': pins, 'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'parts': parts}
    if service_only:
        manifest['outside_or_invalid'] = None
        manifest['subset'] = 'service: Business and Professional Services / Health and Medicine, excluding records with food or shopping categories'
    temporary = out / 'manifest.pending.json'
    temporary.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(target)
    print(f'Japan acquisition verified: {actual} records, {len(parts)} shards, {closed} known closed', flush=True)


if __name__ == '__main__':
    try:
        main()
    except Exception:
        print('FSQ acquisition failed: check local token, Portal access, network, schema or snapshot. Remote details suppressed to protect credentials.', file=sys.stderr)
        sys.exit(1)
