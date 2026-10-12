"""Merge valid model candidates by ID; keep failures and unknowns explicit."""
import json,re
from pathlib import Path
from collections import Counter
from translate_names import save,validate
WORK=Path('data/name-translation/world')

def main():
    expected=json.loads((WORK/'model-input.json').read_text(encoding='utf-8'))['items']
    allowed={r['id']:r for r in expected};merged={}
    for filename in ('candidates-qwen3.5-9b.json','retry-granite4.2-8b.json'):
        path=WORK/filename
        if not path.exists():continue
        rows=json.loads(path.read_text(encoding='utf-8'))['items']
        validate(rows,{'items':rows})
        for row in rows:
            if row['id'] not in allowed:raise ValueError('Unexpected source ID')
            if row['id'] in merged:continue
            if any(row.get(k)!=allowed[row['id']].get(k) for k in ('original','country','lon','lat')):raise ValueError('Reference metadata mismatch')
            if row['kind']=='unknown' and row['ja'] is not None:
                row={**row,'model_returned_ja':row['ja'],'ja':None}
            merged[row['id']]=row
    failures=[{**r,'status':'generation_failed','reason':'No valid response after model retries'} for r in expected if r['id'] not in merged]
    rows=list(merged.values());unknown=[r for r in rows if r['ja'] is None]
    # Flags identify a review priority, not a proof that a name is wrong.
    flagged=[]
    for row in rows:
        reasons=[]
        if row.get('kind')=='conventional':reasons.append('model_claims_conventional_without_source')
        if row['country']=='KR' and re.search(r'-(si|gun|gu)$',row['original']):reasons.append('korean_administrative_suffix')
        if row['ja'] and re.search('[A-Za-z]',row['ja']):reasons.append('latin_characters_in_candidate')
        if reasons:flagged.append({**row,'review_reasons':reasons})
    save(WORK/'all-candidates.json',{'version':1,'verified':False,'items':rows})
    save(WORK/'candidate-review.json',{'priority':flagged,'unknown':unknown,'generation_failed':failures})
    summary={'expected':len(expected),'valid_responses':len(rows),'named_candidates':len(rows)-len(unknown),'unknown':len(unknown),'generation_failed':len(failures),'accounted_for':len(rows)+len(failures),'priority_review':len(flagged),'kinds':dict(Counter(r['kind'] for r in rows)),'models':dict(Counter(r['model'] for r in rows)),'display_applied':False}
    save(WORK/'completion-check.json',summary)
    save(WORK/'retry-pending.json',{'items':failures})
    print(json.dumps(summary))

if __name__=='__main__':main()
