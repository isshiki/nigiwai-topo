"""Resume the additional service build after fetch_foursquare --service-only."""
import subprocess
import sys
import json
from pathlib import Path


def main():
    # The first acquisition log used a whole-JP total for a subset; do not
    # misreport other categories as invalid coordinates in saved provenance.
    path = Path('data/raw/foursquare-japan-service/manifest.json')
    raw = json.loads(path.read_text(encoding='utf-8'))
    raw['outside_or_invalid'] = None
    raw['subset'] = 'service: Business and Professional Services / Health and Medicine, excluding records with food or shopping categories'
    serialized = json.dumps(raw, ensure_ascii=False, indent=2)
    if path.read_text(encoding='utf-8') != serialized:
        path.write_text(serialized, encoding='utf-8')
    commands = [
        ['scripts/build_national.py', '--input', 'data/raw/foursquare-japan-service',
         '--output', 'web/data/foursquare-japan-service', '--categories', 'service'],
        ['scripts/enrich_admin.py', '--input', 'web/data/foursquare-japan-service'],
        ['scripts/merge_service.py'],
    ]
    commands += [['scripts/build_pmtiles.py', '--choice', f'{sigma}-service'] for sigma in (200,400,800)]
    commands += [['scripts/validate_national.py'], ['scripts/validate_pmtiles.py']]
    for command in commands:
        subprocess.run([sys.executable, *command], check=True)


if __name__ == '__main__':
    main()
