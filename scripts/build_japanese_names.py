"""Prepare Japanese peak names from linked Wikidata labels; no density rebuild."""
import json
import re
import time
import urllib.parse
import urllib.request
import urllib.error
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def build():
    output = {}
    overrides = json.loads((ROOT / 'scripts/japanese-name-overrides.json').read_text(encoding='utf-8'))
    for area in json.loads((ROOT / 'scripts/world-pilots.json').read_text(encoding='utf-8'))['regions']:
        region = area['id']
        raw = ROOT / 'data/raw/world-names' / region
        records = sum((json.loads((raw / name).read_text(encoding='utf-8')) for name in ('stations.json', 'places.json')), [])
        used = set()
        for path in (ROOT / 'data/distribution' / f'foursquare-{region}').glob('*-peaks.json'):
            for feature in json.loads(path.read_text(encoding='utf-8'))['features']:
                used.update(feature['properties'].get('name_source_ids', []))
        selected = [r for r in records if used.intersection(r['osm_ids'])]
        qids = sorted({r['wikidata'] for r in selected if re.fullmatch(r'Q\d+', r.get('wikidata') or '')})
        cache = ROOT / 'data/cache/japanese-names' / region
        cache.mkdir(parents=True, exist_ok=True)
        entities = {}
        for start in range(0, len(qids), 50):
            batch = qids[start:start+50]
            path = cache / (str(start) + '.json')
            if path.exists():
                data = json.loads(path.read_text(encoding='utf-8'))
                if data.get('ids') != batch:
                    data = None
            else:
                data = None
            if data is None:
                query = urllib.parse.urlencode({'action':'wbgetentities', 'ids':'|'.join(batch), 'props':'labels', 'languages':'ja', 'format':'json'})
                request = urllib.request.Request('https://www.wikidata.org/w/api.php?' + query,
                    headers={'User-Agent':'NigiwaiTopo/0.1 (Japanese map name preparation)'})
                for attempt in range(5):
                    try:
                        with urllib.request.urlopen(request, timeout=60) as response:
                            body = json.load(response)
                        break
                    except urllib.error.HTTPError as error:
                        if error.code not in (429, 502, 503, 504) or attempt == 4:
                            raise
                        time.sleep(min(60, 15 * (attempt + 1)))
                if 'entities' not in body:
                    raise RuntimeError('Wikidata did not return entities')
                data = {'ids':batch, 'entities':body['entities']}
                path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')
                time.sleep(3)
            entities.update(data['entities'])
        mapping = {}
        missing = []
        for record in selected:
            label = entities.get(record.get('wikidata'), {}).get('labels', {}).get('ja', {}).get('value')
            if record['name_key'] == 'name:ja':
                label, source = record['name'], 'OSM name:ja'
            else:
                source = 'https://www.wikidata.org/wiki/' + (record.get('wikidata') or '')
            override = next((overrides.get(region, {}).get(id) for id in record['osm_ids']
                             if overrides.get(region, {}).get(id)), None)
            if override:
                if not override.get('name') or not override.get('source'):
                    raise ValueError('Manual names require a name and verification source')
                label, source = override['name'], override['source']
            if label:
                for osm_id in record['osm_ids']:
                    mapping[osm_id] = {'name':label, 'source':source}
            else:
                missing.append({'osm_ids':record['osm_ids'], 'name':record['name'], 'wikidata':record.get('wikidata')})
        output[region] = mapping
        (cache / 'missing.json').write_text(json.dumps(missing, ensure_ascii=False, indent=2), encoding='utf-8')
        print(region, 'peak references', len(selected), 'Japanese', len(selected)-len(missing), 'unresolved', len(missing))
    (ROOT / 'web/japanese-names.json').write_text(json.dumps(output, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (ROOT / 'web/japanese-names.js').write_text('window.NIGIWAI_JAPANESE_NAMES = ' + json.dumps(output, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')


if __name__ == '__main__':
    build()
