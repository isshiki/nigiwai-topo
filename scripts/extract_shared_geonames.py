"""Recover missing reference coordinates from previously downloaded country dumps."""
import json
import zipfile
from pathlib import Path

root = Path('data/shared-density')
audit = json.loads((root / 'references.json').read_text(encoding='utf-8'))
wanted = {key.split(':', 1)[1] for r in audit['unresolved'] for key in r['keys'] if key.startswith('GeoNames:')}
output = root / 'extra-geonames.json'
found = {r['id']: r for r in json.loads(output.read_text(encoding='utf-8'))} if output.exists() else {}
for file in Path('data/name-research/coordinate-countries').glob('*.zip'):
    if not wanted - found.keys():
        break
    with zipfile.ZipFile(file) as archive:
        member = file.stem + '.txt'
        if member not in archive.namelist():
            continue
        with archive.open(member) as stream:
            for row in stream:
                fields = row.decode('utf-8').rstrip('\n').split('\t')
                if fields[0] in wanted:
                    found[fields[0]] = {'id': fields[0], 'name': fields[1], 'lat': float(fields[4]), 'lon': float(fields[5]), 'source': 'GeoNames', 'country': fields[8]}
output.write_text(json.dumps(list(found.values()), ensure_ascii=False), encoding='utf-8')
print(json.dumps({'missing_requested': len(wanted), 'recovered': len(wanted & found.keys()), 'remaining': sorted(wanted - found.keys())}))
