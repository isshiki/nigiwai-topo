"""Build source-backed world Japanese names; unresolved conflicts stay separate."""
import json,re,unicodedata
from pathlib import Path
from translate_names import save
WORK=Path('data/name-translation/world')
def norm(text):return re.sub(r'[\s・･\-－]', '',unicodedata.normalize('NFKC',text))
def select_registered(aliases,natural=None):
    rows=[r for r in aliases if not any(r.get(k) for k in ('historic','colloquial','short','to')) and re.search('[ぁ-ゖァ-ヺ一-鿿]',r['name'])]
    labels={norm(r['name']) for r in rows}
    if len(labels)>1:return None,'multiple_geonames_labels'
    if rows:
        if natural and norm(natural)!=norm(rows[0]['name']):return None,'source_disagreement'
        preferred=next((r for r in rows if r.get('preferred')),rows[0])
        return {'name':preferred['name'],'source':'GeoNames alternateNames ja','status':'registered'},None
    if natural and re.search('[ぁ-ゖァ-ヺ一-鿿]',natural):return {'name':natural,'source':'Natural Earth NAME_JA (Wikidata derived)','status':'registered'},None
    return None,None

def build():
    items=json.loads((WORK/'dictionary.json').read_text(encoding='utf-8'))['items']
    aliases=json.loads(Path('data/name-research/geonames-ja-aliases.json').read_text(encoding='utf-8'))['aliases']
    natural={r['geonames_id']:r['ja'] for r in json.loads(Path('data/name-research/natural-earth-matches.json').read_text(encoding='utf-8'))}
    wiki_path=WORK/'wikidata-names.json';wiki=json.loads(wiki_path.read_text(encoding='utf-8')) if wiki_path.exists() else {}
    mapping={};review=[];pending=[];counts={}
    for item in items:
        ids=item['source_ids'];key=item['id'];entry=None;reason=None
        if item['status']=='existing':entry={'name':item['ja'],'source':item['source'],'status':'existing'}
        elif item['source']=='GeoNames':
            entry,reason=select_registered(aliases.get(ids[0],[]),natural.get(ids[0]))
            w=wiki.get(ids[0])
            if w:
                if entry and norm(entry['name'])!=norm(w['name']):entry=None;reason='wikidata_disagreement'
                elif not entry and reason:
                    candidates={norm(r['name']) for r in aliases.get(ids[0],[]) if not any(r.get(k) for k in ('historic','colloquial','short','to'))}
                    if natural.get(ids[0]):candidates.add(norm(natural[ids[0]]))
                    if candidates=={norm(w['name'])}:entry=w;reason=None
                else:entry=w
        if entry:
            mapping[key]=entry;counts[entry['source']]=counts.get(entry['source'],0)+1
        elif reason:review.append({**item,'reason':reason,'aliases':aliases.get(ids[0],[]),'natural_earth':natural.get(ids[0]),'wikidata':wiki.get(ids[0])})
        else:pending.append(item)
    save(WORK/'registered-names.json',mapping);save(WORK/'review.json',{'items':review})
    save(WORK/'model-input.json',{'version':1,'items':pending})
    summary={'references':len(items),'adopted':len(mapping),'review':len(review),'model_pending':len(pending),'sources':counts,'applied_peak_references':sum(r['peak_count'] for r in items if r['id'] in mapping)}
    save(WORK/'registered-summary.json',summary)
    Path('web/world-japanese-names.js').write_text('window.NIGIWAI_JAPANESE_NAMES.world = '+json.dumps(mapping,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    print(summary,flush=True)
    return pending
if __name__=='__main__':build()
