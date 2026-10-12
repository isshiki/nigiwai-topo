"""Build six coordinate-bound labels; never translate an ambiguous GeoNames ID globally."""
import json
from pathlib import Path
LABELS={'Hudi':['海上世界','太子湾・蛇口クルーズ母港'],'Dalingxia':['印力中心','竹子林'],'Haoye':['沙井・京基百納広場'],'Hongshulin':['前海桂湾・万象前海']}
def main():
    report=json.loads(Path('docs/held-locale-poi-review.json').read_text(encoding='utf-8'))
    if not report['address_acquisition_verified']:raise ValueError('POI addresses are unverified')
    entries=[]
    for r in report['items']:
        for i,p in enumerate(r['peaks']):
            if not any(a.get('address_record',{}).get('address') for a in p['evidence_pois']):raise ValueError('No address evidence')
            entries.append({'coordinates':p['coordinates'],'source_id':r['reference_id'],'original':r['original'],'name':LABELS[r['original']][i]+'付近','basis':'周辺POIの施設名・住所と公的所在地を照合した参照名。行政区域への包含判定ではなく、施設の実標高でもありません。元の近隣地名の翻訳ではありません。','source_urls':[s['url'] for s in r['sources']]})
    if len(entries)!=6 or len({tuple(r['coordinates']) for r in entries})!=6:raise ValueError('Expected six distinct peaks')
    Path('web/world-peak-locality-names.js').write_text('window.NIGIWAI_PEAK_LOCALITY_NAMES = '+json.dumps(entries,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    print('Built six coordinate-bound locality labels')
if __name__=='__main__':main()
