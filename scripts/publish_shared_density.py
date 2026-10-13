"""Publish a verified common reference index to an unused S3 release prefix."""
import argparse
import json
import subprocess
import urllib.request
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument('--prefix', required=True)
args = parser.parse_args()
import re
assert re.fullmatch(r'nigiwai-topo/world/[a-zA-Z0-9-]+/', args.prefix)
root = Path('data/shared-density/publish')
manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
assert manifest['radius_m'] == 800 and manifest['sigma_m'] == 200
assert manifest['station_count'] == 9032
expected = {p.relative_to(root).as_posix(): p.stat().st_size for p in root.rglob('*') if p.is_file()}
assert all(Path(p).suffix in {'.json', '.csv', '.txt'} for p in expected)


def aws(*arguments):
    result = subprocess.run(['aws', *arguments, '--profile', 'nigiwai-topo', '--output', 'json'], check=True, capture_output=True, text=True, encoding='utf-8')
    return json.loads(result.stdout or '{}')


assert aws('sts', 'get-caller-identity')['Account'] == '207364224120'
assert aws('s3api', 'list-objects-v2', '--bucket', 'remasahiko', '--prefix', args.prefix, '--max-keys', '1').get('KeyCount', 0) == 0, 'Use a new immutable release prefix'
subprocess.run(['aws', 's3', 'sync', str(root), 's3://remasahiko/' + args.prefix, '--profile', 'nigiwai-topo', '--region', 'ap-northeast-1', '--no-progress', '--only-show-errors'], check=True)
actual = {r['Key'][len(args.prefix):]: r['Size'] for r in aws('s3api', 'list-objects-v2', '--bucket', 'remasahiko', '--prefix', args.prefix).get('Contents', [])}
assert actual == expected
base = 'https://re.masahiko.info/' + args.prefix
for file in ['manifest.json', 'reference-index/index.json', 'reference-index/0.json']:
    with urllib.request.urlopen(urllib.request.Request(base + file, headers={'Origin': 'https://isshiki.github.io'}), timeout=30) as response:
        assert response.headers.get('Access-Control-Allow-Origin') == '*'
        assert json.load(response) == json.loads((root / file).read_text(encoding='utf-8'))
report = {'complete': True, 'base': base, 'files': len(actual), 'bytes': sum(actual.values()), 'cors_verified': True, 'manifest': manifest}
Path('data/validation/shared-density-published.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(report))
