"""Validate generated inventory, rank inputs and geometries; record payload sizes."""
import argparse
import json
from pathlib import Path
from shapely.geometry import shape


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=Path('web/data/foursquare-japan'))
    parser.add_argument('--output', type=Path, default=Path('data/validation/national-summary.json'))
    args = parser.parse_args()
    root = args.input
    manifest = json.loads((root / 'manifest.json').read_text(encoding='utf-8'))
    if 'administrative_names' in manifest:
        regions = json.loads((root / 'regions.json').read_text(encoding='utf-8'))
        assert len(regions) == 57
        assert {k for k in regions if k.startswith('pref-')} == {f'pref-{i:02}' for i in range(1,48)}
        assert sorted(c for k,r in regions.items() if k != 'japan' and not k.startswith('pref-') for c in r['pref_codes']) == [f'{i:02}' for i in range(1,48)]
    categories = ['all', 'food', 'shopping'] + (['service'] if 'service_input_signature' in manifest else [])
    expected = {(s, c, 'exclude') for s in [200, 400, 800] for c in categories}
    assert len(manifest['datasets']) == len(expected)
    assert {(d['sigma'], d['category'], d['status']) for d in manifest['datasets']} == expected
    summary, sizes, features = [], [], 0
    for d in manifest['datasets']:
        peaks = json.loads((root / d['peaks_file']).read_text(encoding='utf-8'))['features']
        assert len(peaks) == d['peaks']
        assert all(peaks[i]['properties']['density'] >= peaks[i+1]['properties']['density'] for i in range(len(peaks)-1))
        assert len({tuple(f['geometry']['coordinates']) for f in peaks}) == len(peaks)
        assert all('name_basis' in f['properties'] for f in peaks)
        if 'administrative_names' in manifest:
            assert all('pref_code' in f['properties'] and 'municipality' in f['properties'] for f in peaks)
        detail_peak_count = 0
        for c in d['chunks']:
            path = root / c['file']
            assert path.stat().st_size == c['bytes']
            geo = json.loads(path.read_text(encoding='utf-8'))
            detail_peak_count += sum(f['properties']['kind'] == 'peak' for f in geo['features'])
            assert all(shape(f['geometry']).is_valid for f in geo['features']), c['file']
            features += len(geo['features'])
            sizes.append(c['bytes'])
        assert detail_peak_count == len(peaks)
        overview = json.loads((root / d['overview_file']).read_text(encoding='utf-8'))
        assert all(shape(f['geometry']).is_valid for f in overview['features']), d['overview_file']
        summary.append({'sigma':d['sigma'], 'category':d['category'], 'count':d['count'], 'peaks':d['peaks'],
                        'chunks':len(d['chunks']), 'detail_bytes':sum(c['bytes'] for c in d['chunks']),
                        'overview_bytes':(root / d['overview_file']).stat().st_size})
    result = {'choices':len(summary), 'geometry_features':features, 'invalid_geometries':0,
              'detail_total_bytes':sum(sizes), 'largest_chunk_bytes':max(sizes), 'rows':summary}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(f'Validated {len(summary)} choices, {features} detail features, all geometries valid; {sum(sizes)} detail bytes')


if __name__ == '__main__':
    main()
