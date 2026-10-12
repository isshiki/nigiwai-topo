"""Resume candidate generation for individually reviewable address matches.

This never changes the public dictionary. A Japanese candidate is not evidence
of the local pronunciation or a confirmed geographic name.
"""
import argparse
import json
from pathlib import Path
from types import SimpleNamespace
import translate_names as t

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / 'data/name-research/unnamed-world'


def prepare():
    report = json.loads((WORK / 'address-name-review.json').read_text(encoding='utf-8'))
    approvals = json.loads((ROOT / 'docs/unnamed-world-name-approvals.json').read_text(encoding='utf-8'))
    published = {p['peak'] for p in approvals['items']}
    old = json.loads((ROOT / 'docs/unnamed-world-batch6-review.json').read_text(encoding='utf-8'))
    held = {p for x in old['items'] if x['decision'] == 'hold' for p in x['peak_keys']}
    groups = {}
    for p in report['items']:
        if p['peak'] in published or p['peak'] in held or not p['candidates']:
            continue
        c = p['candidates'][0]
        if not (p['status'] == 'candidate_supported' and c['support_share'] >= .85
                and c['supporting_pois'] >= 6 and c['distance_m'] <= 1000
                and p['distinct_coordinates'] >= 4 and p['with_address'] >= 4):
            continue
        key = 'GeoNames:' + c['id']
        group = groups.setdefault(key, dict(id=key, region='world', original=c['name'],
            country=c['country'], lon=c['lon'], lat=c['lat'], source_ids=[c['id']],
            reference_kind='populated_place', peak_keys=[]))
        group['peak_keys'].append(p['peak'])
    rows = list(groups.values())
    t.save(WORK / 'next-translation-input.json', dict(items=rows, not_adopted=True,
        snapshot=report['snapshot'], policy='Individual address and pronunciation review required'))
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--run', action='store_true')
    parser.add_argument('--batch-size', type=int, default=8)
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error('--batch-size must be positive')
    rows = prepare()
    print('Reference candidates:', len(rows), 'Peaks:', sum(len(r['peak_keys']) for r in rows), flush=True)
    if not args.run:
        return
    state = WORK / 'next-translation-progress.json'
    t.save(state, dict(status='running', references=len(rows), automatically_published=False))
    t.COUNTRIES = {'world': ('World', 'various')}
    try:
        t.run(SimpleNamespace(output=WORK / 'next-translation-qwen35-9b.json',
            model='qwen3.5:9b', limit=0, batch_size=args.batch_size, japanese_only=True), rows)
    except Exception as error:
        t.save(state, dict(status='failed', references=len(rows), error_type=type(error).__name__,
            automatically_published=False))
        raise
    output = json.loads((WORK / 'next-translation-qwen35-9b.json').read_text(encoding='utf-8'))
    completed = {r['id'] for r in output['items']}
    missing = [r['id'] for r in rows if r['id'] not in completed]
    t.save(state, dict(status='retry_pending' if missing else 'complete', references=len(rows),
        saved=len(rows)-len(missing), missing_ids=missing, automatically_published=False,
        output='next-translation-qwen35-9b.json'))


if __name__ == '__main__':
    main()
