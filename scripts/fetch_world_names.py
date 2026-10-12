"""Small pilot extracts only; world rollout should use regional OSM PBFs."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import urllib.parse
import urllib.request
from world_names import reference_records, GEOD

ENDPOINT = 'https://overpass-api.de/api/interpreter'


def fetch(region):
    root = Path('data/raw/world-names')/region['id']
    root.mkdir(parents=True, exist_ok=True)
    raw_path = root/'overpass.json'
    previous = {}
    west, south, east, north = region['bbox']
    # Fetch outside the pilot to avoid losing nearby station/reference names.
    corners = [(x,y) for x in (west,east) for y in (south,north)]
    halo = [GEOD.fwd(x,y,bearing,20000)[:2] for x,y in corners for bearing in range(0,360,15)]
    bounds = [min(p[0] for p in halo),min(p[1] for p in halo),max(p[0] for p in halo),max(p[1] for p in halo)]
    w,s,e,n = bounds
    bbox = f'{s},{w},{n},{e}'
    query = f'''[out:json][timeout:55];(
      nwr[railway~"^(station|halt)$"]({bbox});
      nwr[public_transport=station][train=yes]({bbox});
      nwr[public_transport=station][subway=yes]({bbox});
      nwr[public_transport=station][light_rail=yes]({bbox});
      node[place~"^(city|town|village|suburb|quarter|neighbourhood)$"]({bbox});
    );out center tags;'''
    if raw_path.exists():
        previous = json.loads((root/'manifest.json').read_text(encoding='utf-8'))
        if hashlib.sha256(raw_path.read_bytes()).hexdigest() != previous['raw_sha256']:
            raise ValueError('Cached OSM raw hash mismatch')
        query = previous['query']
        bounds = previous['fetch_bbox']
    else:
        request = urllib.request.Request(ENDPOINT, data=urllib.parse.urlencode({'data':query}).encode(),
            headers={'User-Agent':'nigiwai-topo-pilot/0.1'})
        with urllib.request.urlopen(request, timeout=65) as response:
            payload = response.read()
        data = json.loads(payload)
        if data.get('remark') or 'elements' not in data:
            raise ValueError('Incomplete Overpass result; not cached')
        raw_path.with_suffix('.pending').write_bytes(payload)
        raw_path.with_suffix('.pending').replace(raw_path)
    data = json.loads(raw_path.read_text(encoding='utf-8'))
    if data.get('remark'):
        raise ValueError('Incomplete cached Overpass result')
    stations, places = reference_records(data['elements'])
    changed = not previous
    for name, rows in [('stations.json',stations),('places.json',places)]:
        content = json.dumps(rows, ensure_ascii=False, separators=(',',':'))
        target = root/name
        if not target.exists() or target.read_text(encoding='utf-8') != content:
            changed = True
            target.write_text(content,encoding='utf-8')
    manifest = {'region':region,'fetch_bbox':bounds,'query':query,'endpoint':ENDPOINT,
        'source':'© OpenStreetMap contributors','license':'ODbL-1.0','license_url':'https://www.openstreetmap.org/copyright',
        'osm_timestamp':data.get('osm3s',{}).get('timestamp_osm_base'),
        'prepared_utc':datetime.now(timezone.utc).isoformat() if changed else previous['prepared_utc'],
        'raw_sha256':hashlib.sha256(raw_path.read_bytes()).hexdigest(),
        'station_groups':len(stations),'place_names':len(places),
        'station_merge_m':300,'station_name_radius_m':1500,
        'naming':'name:ja then name then name:en; nearest settlement reference, not containment'}
    (root/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(region['id'], 'station groups',len(stations),'place names',len(places),flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--region', choices=['sg-singapore','gb-london','is-reykjavik'])
    args = parser.parse_args()
    config = json.loads(Path('scripts/world-pilots.json').read_text(encoding='utf-8'))
    for region in config['regions']:
        if not args.region or args.region == region['id']:
            fetch(region)
