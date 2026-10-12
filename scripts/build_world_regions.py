"""Single world data source, with country navigation and Japanese subdivisions."""
import json
from pathlib import Path
def points(value):
    if len(value)>=2 and isinstance(value[0],(int,float)):yield value[:2]
    else:
        for child in value:yield from points(child)
def main():
    regions=json.loads(Path('data/distribution/foursquare-world-v2/regions.json').read_text(encoding='utf-8'))
    for r in regions.values():r['group']='world'
    countries=json.loads(Path('data/raw/world-names/countries.geojson').read_text(encoding='utf-8'))
    for f in countries['features']:
        p=f['properties'];code=p.get('ISO_A2_EH') or p.get('ISO_A2')
        if not code or code=='-99':continue
        coords=list(points(f['geometry']['coordinates']));xs,ys=zip(*coords)
        bbox=[min(xs),max(-85.05,min(ys)),max(xs),min(85.05,max(ys))]
        regions['country-'+code.lower()]={'name':'台湾' if code=='TW' else p.get('NAME_JA') or p['NAME'],'bbox':bbox,'group':'country','country_code':code}
    japan=json.loads(Path('data/distribution/foursquare-japan/regions.json').read_text(encoding='utf-8'))
    regions.pop('country-jp',None)
    regions['japan']={**japan['japan'],'name':'日本','group':'country','country_code':'JP'}
    for key,r in japan.items():
        if key!='japan':regions[key]={**r,'parent':'japan','group':'prefecture' if key.startswith('pref-') else 'japan-region'}
    Path('web/world-regions.js').write_text('window.NIGIWAI_WORLD_REGIONS = '+json.dumps(regions,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    print(json.dumps({'countries':sum(r['group']=='country' for r in regions.values()),'japan_subdivisions':sum(r.get('parent')=='japan' for r in regions.values())}))
if __name__=='__main__':main()
