"""Merge independently built Japan service layers without changing old layers."""
import json
from pathlib import Path
import shutil


def main():
    source = Path('web/data/foursquare-japan-service')
    target = Path('web/data/foursquare-japan')
    extra = json.loads((source/'manifest.json').read_text(encoding='utf-8'))
    manifest = json.loads((target/'manifest.json').read_text(encoding='utf-8'))
    if extra['snapshots'] != manifest['snapshots']:
        raise ValueError('Service and existing datasets must share pinned snapshots')
    assert {(d['sigma'], d['category']) for d in extra['datasets']} == {(s,'service') for s in (200,400,800)}
    for item in extra['datasets']:
        for name in [item['peaks_file'], item['overview_file']]:
            shutil.copy2(source/name, target/name)
        folder = f"{item['sigma']}-service-exclude"
        shutil.copytree(source/folder, target/folder, dirs_exist_ok=True)
    manifest['datasets'] = [d for d in manifest['datasets'] if d['category'] != 'service'] + extra['datasets']
    manifest['service_input_signature'] = extra['input_signature']
    manifest['service_definition'] = 'Foursquare Business and Professional Services / Health and Medicine. Multiple categories: food then shopping then service. Existing food/shopping layers retain legacy name-based classification; overlapping with service is possible.'
    pending = target/'manifest.pending.json'
    pending.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    pending.replace(target/'manifest.json')
    print('Merged three service layers; preserved existing nine layers')


if __name__ == '__main__':
    main()
