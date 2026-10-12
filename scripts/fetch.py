"""Fetch public Overture or OSM data for the Tokyo prototype (including halo)."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import urlencode

from region import FETCH_BBOX as BBOX


def category(value):
    text = json.dumps(value).lower()
    if any(s in text for s in ['restaurant', 'cafe', 'coffee', 'food', 'bar', 'pub']):
        return 'food'
    if any(s in text for s in ['shop', 'retail', 'store', 'supermarket', 'mall']):
        return 'shopping'
    return 'other'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('source', choices=['overture', 'osm'])
    parser.add_argument('--release', default='2026-09-23.1')
    args = parser.parse_args()
    target = Path('data/raw') / args.source
    target.mkdir(parents=True, exist_ok=True)
    west, south, east, north = BBOX
    if args.source == 'overture':
        import duckdb
        con = duckdb.connect()
        con.execute("SET extension_directory='data/cache/duckdb'")
        con.execute('INSTALL httpfs; LOAD httpfs')
        # Release must remain a literal path component, never arbitrary SQL.
        import re
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}\.\d+', args.release):
            raise ValueError('Invalid release')
        url = f's3://overturemaps-us-west-2/release/{args.release}/theme=places/type=place/*'
        rows = con.execute(f"SELECT id, names.primary, bbox.xmin, bbox.ymin, taxonomy, confidence, operating_status FROM read_parquet('{url}', hive_partitioning=true) WHERE bbox.xmin BETWEEN ? AND ? AND bbox.ymin BETWEEN ? AND ?", [west, east, south, north]).fetchall()
        points = [{'id': r[0], 'name': r[1], 'lon': r[2], 'lat': r[3], 'category': category(r[4]), 'taxonomy': r[4], 'confidence': r[5], 'operating_status': r[6]} for r in rows]
        source = f'Overture Places {args.release}（未品質フィルタ）'
    else:
        url = 'https://overpass-api.de/api/interpreter'
        query = f'[out:json][timeout:180];(nwr["shop"]({south},{west},{north},{east});nwr["amenity"]({south},{west},{north},{east});nwr["tourism"]({south},{west},{north},{east});nwr["leisure"]({south},{west},{north},{east}););out center tags;'
        request = Request(url, data=urlencode({'data': query}).encode(), headers={'User-Agent': 'nigiwai-topo-prototype/0.1'})
        with urlopen(request, timeout=240) as response:
            payload = response.read()
        (target / 'overpass.json').write_bytes(payload)
        result = json.loads(payload)
        if result.get('remark'):
            raise RuntimeError('Overpass incomplete result: ' + result['remark'])
        points = []
        for element in result['elements']:
            position = element if 'lon' in element else element.get('center')
            if position:
                tags = element.get('tags', {})
                points.append({'id': f"{element['type']}/{element['id']}", 'name': tags.get('name'), 'lon': position['lon'], 'lat': position['lat'], 'category': 'shopping' if 'shop' in tags else category(tags.get('amenity', '')), 'tags': tags})
        source = 'OpenStreetMap（未重複排除・対象タグ暫定）'
    raw = {'source': source, 'synthetic': False, 'bbox': BBOX, 'points': points, 'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'source_url': url, 'count': len(points), 'quality': 'Unfiltered exploratory data. Not comparable coverage until category alignment and deduplication.'}
    output = target / 'points.json'
    output.write_text(json.dumps(raw, ensure_ascii=False, default=str), encoding='utf-8')
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    (target / 'manifest.json').write_text(json.dumps({k: v for k, v in raw.items() if k != 'points'} | {'sha256': digest}, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{output}: {len(points)} records, SHA256 {digest}')


if __name__ == '__main__':
    main()
