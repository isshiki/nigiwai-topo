"""Lossless browser payload; share recurring route and municipality strings."""
import json
from pathlib import Path


def main():
    source = Path('web/station-tier-data.json')
    data = json.loads(source.read_text(encoding='utf-8'))
    routes = {route['id']: route for s in data['stations'] for route in s['lines']}
    route_ids = sorted(routes)
    route_index = {key: i for i, key in enumerate(route_ids)}
    cities = sorted({s['municipality'] for s in data['stations']})
    city_index = {key: i for i, key in enumerate(cities)}
    rows = []
    for s in data['stations']:
        p = s['peak']
        rows.append([s['id'], s['name'], s['lon'], s['lat'], s['pref_code'], city_index[s['municipality']], s['score'], s['tier'], s['source_station_ids'], [route_index[l['id']] for l in s['lines']], None if p is None else [p['name'], p['lon'], p['lat'], p['reference_station_id']]])
    payload = {k: v for k, v in data.items() if k != 'stations'}
    payload.update({'format': 'compact-v1', 'prefectures': {s['pref_code']: s['prefecture'] for s in data['stations']}, 'cities': cities, 'routes': [routes[k] for k in route_ids], 'rows': rows})
    target = Path('web/station-tier-public.json')
    target.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    print(json.dumps({'source_bytes': source.stat().st_size, 'public_bytes': target.stat().st_size, 'stations': len(rows)}))


if __name__ == '__main__':
    main()
