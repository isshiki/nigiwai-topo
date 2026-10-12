"""Export only names used by calculated world peaks, keyed by source identity."""
import json,re
from pathlib import Path
from collections import Counter
from translate_names import save,INSTRUCTION
ROOT=Path('data/distribution/foursquare-world');OUT=Path('data/name-translation/world')
def main():
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    refs={r['id']:r for r in json.loads(Path('data/raw/geonames/places.json').read_text(encoding='utf-8'))}
    existing=json.loads(Path('web/japanese-names.json').read_text(encoding='utf-8'))
    osm={k:v for region,m in existing.items() for k,v in m.items()}
    names={};no_ref=0;total=0
    for part in manifest['packages']:
        for f in json.loads((ROOT/part['id']/'200-all-peaks.json').read_text(encoding='utf-8'))['features']:
            total+=1;p=f['properties'];ids=p.get('name_source_ids',[])
            if not ids:no_ref+=1;continue
            key=(p['name_source'],ids[0])
            if key in names:names[key]['peak_count']+=1;continue
            ref=refs.get(ids[0],{}) if p['name_source']=='GeoNames' else {}
            original=ref.get('name',p.get('nearest_station',p['name'].removesuffix('付近')))
            known=osm.get(ids[0]) if p['name_source']=='OpenStreetMap' else None
            if p['name_source']=='国土数値情報 N02' or (ref.get('country')=='JP' and re.search('[ぁ-ゖァ-ヺ一-鿿]',original)):known={'name':original,'source':p['name_source']}
            names[key]={'id':p['name_source']+':'+ids[0],'source':p['name_source'],'source_ids':ids,'original':original,'country':ref.get('country'),
                'lon':ref.get('lon',f['geometry']['coordinates'][0]),'lat':ref.get('lat',f['geometry']['coordinates'][1]),
                'reference_kind':ref.get('feature_code','station'),'peak_count':1,'ja':known['name'] if known else None,'status':'existing' if known else 'pending'}
    items=sorted(names.values(),key=lambda r:(-r['peak_count'],r['id']))
    assert sum(r['peak_count'] for r in items)==total-no_ref
    assert len({r['id'] for r in items})==len(items)
    pending=[r for r in items if r['status']=='pending']
    save(OUT/'dictionary.json',{'version':1,'items':items})
    save(OUT/'input.json',{'version':1,'instruction':INSTRUCTION,'items':pending})
    for i in range(0,len(pending),50):save(OUT/'chatgpt'/f'batch-{i//50:04}.json',{'instruction':INSTRUCTION,'items':pending[i:i+50]})
    report={'peaks':total,'coordinate_only_peaks':no_ref,'unique_references':len(items),'existing_japanese':len(items)-len(pending),'pending':len(pending),'batches_50':(len(pending)+49)//50,'countries':dict(Counter(r['country'] or 'unknown' for r in pending))}
    save(OUT/'summary.json',report)
    print({k:v for k,v in report.items() if k!='countries'},flush=True)
if __name__=='__main__':main()
