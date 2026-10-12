"""Resume ID-verified Wikidata Japanese labels, then rebuild and trial Ollama.

No name-only matching. API responses are cached; reruns skip completed batches.
"""
import hashlib,json,re,time,urllib.request,urllib.error,subprocess,sys
from pathlib import Path
from translate_names import save

WORK=Path('data/name-translation/world')

def fetch():
    links=json.loads(Path('data/name-research/geonames-wikidata-links.json').read_text(encoding='utf-8'))['links']
    reverse={}
    for gid,qids in links.items():
        if len(qids)==1:reverse.setdefault(qids[0],[]).append(gid)
    cache=WORK/'wikidata-cache';cache.mkdir(parents=True,exist_ok=True)
    names={};review=[];qids=sorted(reverse)
    for start in range(0,len(qids),50):
        batch=qids[start:start+50]
        path=cache/(hashlib.sha256('|'.join(batch).encode()).hexdigest()+'.json')
        if path.exists():body=json.loads(path.read_text(encoding='utf-8'))
        else:
            from urllib.parse import urlencode
            url='https://www.wikidata.org/w/api.php?'+urlencode({'action':'wbgetentities','ids':'|'.join(batch),'props':'labels|claims','languages':'ja','format':'json','maxlag':5})
            attempt=0
            while True:
                try:
                    req=urllib.request.Request(url,headers={'User-Agent':'NigiwaiTopo/1.0 (place-name dictionary research; Python urllib)'})
                    with urllib.request.urlopen(req,timeout=90) as response:body=json.load(response)
                    if body.get('error',{}).get('code')=='maxlag':
                        print(f'Wikidata maxlag; batch {start}; waiting 60s',flush=True)
                        time.sleep(60)
                        continue
                    if 'error' in body:raise RuntimeError(str(body['error']))
                    save(path,body);break
                except (urllib.error.URLError,RuntimeError) as error:
                    if attempt==5:raise
                    print(f'Wikidata retry {attempt+1}; batch {start}; {type(error).__name__}',flush=True)
                    retry=getattr(error,'headers',{}).get('Retry-After','')
                    time.sleep(max(float(retry) if retry.isdigit() else 0,min(60,5*2**attempt)))
                    attempt+=1
            time.sleep(3)
        for qid in batch:
            entity=body.get('entities',{}).get(qid,{})
            label=entity.get('labels',{}).get('ja',{}).get('value')
            if not label or not re.search('[ぁ-ゖァ-ヺ一-鿿]',label):continue
            ids={str(c.get('mainsnak',{}).get('datavalue',{}).get('value')) for c in entity.get('claims',{}).get('P1566',[]) if c.get('rank')!='deprecated'}
            for gid in reverse[qid]:
                if gid not in ids:
                    review.append({'geonames_id':gid,'qid':qid,'ja':label,'reason':'P1566_missing_or_mismatched'});continue
                names[gid]={'name':label,'source':'Wikidata Japanese label / CC0','status':'registered','qid':qid}
        save(WORK/'wikidata-names.json',names)
        save(WORK/'wikidata-review.json',{'items':review})
        save(WORK/'wikidata-progress.json',{'processed':min(start+50,len(qids)),'total':len(qids),'adoptable':len(names),'review':len(review),'complete':start+50>=len(qids)})
        print(f'Wikidata {min(start+50,len(qids))}/{len(qids)}; verified Japanese {len(names)}',flush=True)

if __name__=='__main__':
    fetch()
    subprocess.run([sys.executable,'scripts/build_world_japanese_names.py'],check=True)
    if '--trial' in sys.argv:
        subprocess.run([sys.executable,'scripts/translate_world_names.py','--run','--limit','300','--model','qwen3.5:9b'],check=True)
