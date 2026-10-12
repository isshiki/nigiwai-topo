"""Generate resumable Japanese candidates for geographically supported names.

Never publishes model output. Identity/address evidence remains independently
stored and output requires review before joining into the public dictionary.
"""
import json
from pathlib import Path
from types import SimpleNamespace
import translate_names as t

ROOT=Path('data/name-research/unnamed-world')

def main():
    report=json.loads((ROOT/'address-name-review.json').read_text(encoding='utf-8'))['items']
    published=json.loads(Path('docs/unnamed-world-name-decisions.json').read_text(encoding='utf-8'))['items']
    known={p['reference']['id'] for p in published}
    items={}
    for p in report:
        if not p['candidates']:continue
        c=p['candidates'][0]
        if c['id'] in known:continue
        if c['support_share']>=.9 and c['supporting_pois']>=12 and c['distance_m']<=500 and p['distinct_coordinates']>=8 and p['with_address']>=8:
            key='GeoNames:'+c['id']
            items.setdefault(key,{'id':key,'region':'world','original':c['name'],'country':c['country'],'lon':c['lon'],'lat':c['lat'],'source_ids':[c['id']],'reference_kind':'populated_place','peak_keys':[]})['peak_keys'].append(p['peak'])
    rows=list(items.values())
    t.save(ROOT/'translation-input.json',{'items':rows,'not_adopted':True,'source_snapshot':'2026-09-15'})
    t.COUNTRIES={'world':('World','various')}
    t.INSTRUCTION+='今回も意味訳や州名の追加をしない。音写に自信がなければunknown。入力の地理的同定を改変しない。'
    print('Unpublished reference names:',len(rows),flush=True)
    t.run(SimpleNamespace(output=ROOT/'translation-qwen35-9b.json',model='qwen3.5:9b',limit=0,batch_size=8,japanese_only=True),rows)

if __name__=='__main__':main()
