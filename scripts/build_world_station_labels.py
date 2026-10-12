"""Korean station labels for existing world peaks; keep density and source data unchanged."""
import json,re
from pathlib import Path
from collections import Counter
from global_names import ReferenceTree
def main():
    root=Path('data/distribution/foursquare-world-v2')
    stations=json.loads(Path('data/raw/world-names/kr-stations/stations.json').read_text(encoding='utf-8'))
    kana={'弘大入口':'ホンデイック','新沙':'シンサ','恵化':'ヘファ','建大入口':'コンデイック','蚕室セネ':'チャムシルセネ','永登浦':'ヨンドゥンポ'}
    edited=json.loads(Path('docs/korea-station-name-overrides.json').read_text(encoding='utf-8'))['names']
    for s in stations:
        original=s['name'].removesuffix('駅')
        s['name']=edited.get(original,kana.get(original,re.sub(r'[（(][^()（）]*[)）]','',original) if re.search(r'[ァ-ヶ]',original) else original))
    tree=ReferenceTree(stations);labels={};seoul=[];original_count=Counter();after_count=Counter()
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    for package in manifest['packages']:
        w,s,e,n=package['bbox']
        if e<124 or w>132 or n<33 or s>39:continue
        for f in json.loads((root/package['id']/'200-all-peaks.json').read_text(encoding='utf-8'))['features']:
            lon,lat=f['geometry']['coordinates'];props=f['properties']
            if not 124<=lon<=132 or not 33<=lat<=39:continue
            station,distance=tree.nearest(lon,lat)
            if distance<=1500:
                labels[f'{lon:.7f},{lat:.7f}']={'name':station['name'],'basis':f'OSMの参照駅まで{round(distance)}m。行政区域への包含判定ではありません。元の広域地名の翻訳ではありません。'+('日本語未登録の駅名は編集音写。' if station['name_key']!='name:ja' else ''),'source_id':'OpenStreetMap:'+station['osm_ids'][0],'original_source':props.get('name_source'),'original_source_ids':props.get('name_source_ids',[]),'station_distance_m':round(distance),'source_urls':['https://www.openstreetmap.org/'+station['osm_ids'][0]],'name_key':station['name_key']}
            if 126.5<=lon<=127.3 and 37.1<=lat<=37.9 and props['density']>=800:
                label=labels.get(f'{lon:.7f},{lat:.7f}');seoul.append({'coordinates':[lon,lat],'density':props['density'],'before':props['name'],'after':label['name'] if label else props['name'],'station_distance_m':label['station_distance_m'] if label else None})
    seoul.sort(key=lambda p:p['density'],reverse=True)
    for p in seoul[:20]:original_count[p['before']]+=1;after_count[p['after']]+=1
    japan=json.loads(Path('data/distribution/foursquare-japan/stations.json').read_text(encoding='utf-8'))
    refs=[{'name':s['name'],'lon':s['lon'],'lat':s['lat'],'source':'N02','id':s['id']} for s in japan]+[{'name':s['name'],'lon':s['lon'],'lat':s['lat'],'source':'OSM','osm_ids':s['osm_ids']} for s in stations]
    Path('web/world-station-peak-names.js').write_text('window.NIGIWAI_STATION_PEAK_NAMES = '+json.dumps(labels,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    Path('web/world-reference-stations.js').write_text('window.NIGIWAI_REFERENCE_STATIONS = '+json.dumps(refs,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    report={'korea_stations':len(stations),'japanese_station_labels':sum(s['name_key']=='name:ja' for s in stations),'renamed_world_peaks':len(labels),'seoul_top20_unique_before':len(original_count),'seoul_top20_unique_after':len(after_count),'seoul_top20':seoul[:20]}
    Path('data/validation/world-station-labels.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k!='seoul_top20'}))
if __name__=='__main__':main()
