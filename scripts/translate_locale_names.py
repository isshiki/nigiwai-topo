"""Generate locale policy revisions, preserving original source identities."""
import argparse,json,re
from pathlib import Path
from types import SimpleNamespace
import translate_names as t

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--run',action='store_true');parser.add_argument('--batch-size',type=int,default=5);args=parser.parse_args()
    w=Path('data/name-translation/world')
    refs=json.loads((w/'dictionary.json').read_text(encoding='utf-8'))['items']
    registered=json.loads((w/'registered-names.json').read_text(encoding='utf-8'))
    candidates={r['id']:r for r in json.loads((w/'all-candidates.json').read_text(encoding='utf-8'))['items']}
    rows=[]
    for r in refs:
        if r['country'] not in ('KR','CN'):continue
        entry=registered.get(r['id']);candidate=candidates.get(r['id'],{}).get('ja')
        value=entry['name'] if entry else candidate or r['original']
        if r['country']=='KR':invalid=not bool(re.search('[ァ-ヺ]',value)) or bool(re.search('[一-鿿가-힣]',value))
        else:invalid=not bool(re.search('[一-鿿]',value)) or bool(re.search('[广门龙东车马风岛阳阴云汉乡县湾边进华庆兴宁黄齐济吴苏郑叶刘赵张陈钟归]',value))
        if invalid:rows.append({k:r.get(k) for k in ('id','source','source_ids','original','country','lon','lat','reference_kind','peak_count')})
    t.save(w/'locale-policy-input.json',{'items':rows,'note':'Policy revision candidates, not adopted names. Chinese character flags are a limited heuristic.'})
    for r in rows:r['region']='world'
    t.COUNTRIES={'world':('World','various')}
    print('Locale policy review targets:',len(rows),flush=True)
    if args.run:t.run(SimpleNamespace(output=w/'locale-policy-qwen3.5-9b.json',model='qwen3.5:9b',limit=0,batch_size=args.batch_size),rows)

if __name__=='__main__':main()
