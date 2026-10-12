"""Sample external name sources without applying translations."""
import json,urllib.request,urllib.parse,time,random
from pathlib import Path
ROOT=Path('data/name-research');ROOT.mkdir(parents=True,exist_ok=True)
def fetch(url,path,accept='application/json'):
    if path.exists():return json.loads(path.read_text(encoding='utf-8'))
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'NigiwaiTopo/0.1 (name coverage research)','Accept':accept}),timeout=90) as r:body=json.load(r)
    path.write_text(json.dumps(body,ensure_ascii=False),encoding='utf-8');return body

def main():
    items=json.loads(Path('data/name-translation/world/input.json').read_text(encoding='utf-8'))['items']
    by_id={r['source_ids'][0]:r for r in items if r['source']=='GeoNames'}
    natural=fetch('https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_10m_populated_places.geojson',ROOT/'natural-earth.json')
    records=[]
    for feature in natural['features']:
        p={k.lower():v for k,v in feature['properties'].items()}
        if p.get('name_ja'):records.append({'geonames_id':str(int(p['geonamesid'])) if p.get('geonamesid') and p['geonamesid']>0 else None,'ja':p['name_ja'],'name':p.get('name'),'wikidata':p.get('wikidataid'),'coordinates':feature['geometry']['coordinates']})
    matched=[r for r in records if r['geonames_id'] in by_id]
    report={'natural_earth_total':len(natural['features']),'natural_earth_japanese':len(records),'natural_earth_pending_matches':len({r['geonames_id'] for r in matched})}
    (ROOT/'natural-earth-matches.json').write_text(json.dumps(matched,ensure_ascii=False,indent=2),encoding='utf-8')
    geo=[r for r in items if r['source']=='GeoNames']
    common=geo[:50];random_rows=random.Random(20261008).sample(geo[50:],50)
    for label,rows in [('frequent',common),('random',random_rows)]:
        values=' '.join(json.dumps(r['source_ids'][0]) for r in rows)
        query='SELECT ?gid ?item ?ja WHERE { VALUES ?gid { '+values+' } ?item <http://www.wikidata.org/prop/direct/P1566> ?gid . OPTIONAL { ?item <http://www.w3.org/2000/01/rdf-schema#label> ?ja . FILTER(LANG(?ja)="ja") } }'
        url='https://query.wikidata.org/sparql?'+urllib.parse.urlencode({'query':query,'format':'json'})
        try:
            data=fetch(url,ROOT/f'wikidata-{label}.json','application/sparql-results+json')
            bindings=data['results']['bindings'];linked={r['gid']['value'] for r in bindings};ja={r['gid']['value'] for r in bindings if 'ja' in r}
            report['wikidata_'+label]={'sample':len(rows),'linked':len(linked),'japanese_labels':len(ja),'method':'GeoNames ID exact match; not full-world coverage estimate'}
        except Exception as e:report['wikidata_'+label]={'error':type(e).__name__,'http_status':getattr(e,'code',None),'sample':len(rows)}
        time.sleep(3)
    (ROOT/'external-sources-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');print(report,flush=True)
if __name__=='__main__':main()
