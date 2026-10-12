"""Join pinned POI evidence to manually checked official locality evidence."""
import json
from collections import Counter
from pathlib import Path
ROOT=Path('data/name-research/held-locale-pois')
CHECKED={
 'Hudi': {'region':'深圳市南山区・蛇口／海上世界と太子湾','peak_regions':['海上世界周辺','太子湾・蛇口クルーズ母港周辺'], 'sources':[
 {'url':'https://qh.sz.gov.cn/en/life-in-qianhai/malls-and-places-for-leisure/content/post_10660073.html','basis':'海上世界商圏の匯港は蛇口工業三路1号。太子湾も別項目で紹介。'},
 {'url':'https://www.hilton.com/zh-hant/hotels/szxsshi-hilton-shenzhen-shekou-nanhai/hotel-location/','basis':'ヒルトン蛇口南海は南山区望海路1177号、海上世界広場近隣。'},
 {'url':'https://www.cmskchp.com/','basis':'母港運営者の所在地は南山区海運路1号。'}], 'terms':['海上世界','Hilton','蛇口','明华','Minghua','太子','Prince'], 'assessment':'虎地という自然地形の参照同定は未解決だが、峰の店舗群は蛇口の実在商圏と対応する。2峰に同じ施設名を一括適用しない。'},
 'Dalingxia': {'region':'深圳市福田区・農林路と竹子林周辺','peak_regions':['印力中心（深国投広場）周辺','竹子林・東方銀座ホテル周辺'], 'sources':[
 {'url':'https://www.szzx.gov.cn/szzx/zwhdt/tawyh/content/post_1220865.html','basis':'印力中心は福田区農林路69号・僑香路交差点。'},
 {'url':'https://www.sz.gov.cn/cn/xxgk/zfxxgj/zcfg/content/post_9584291.html','basis':'深国投広場の公的郵送先は同じ農林路69号。'},
 {'url':'https://wtl.sz.gov.cn/ggfw/lyl/xjbgjdylb/','basis':'東方銀座ホテルの所在地は福田区深南大道竹子林。'}], 'terms':['深国投','印力','东方银座','Oriental Ginza','竹子林','儿童'], 'assessment':'大嶺下という山の同定は未解決だが、名前が割り当てられた2峰の商業・宿泊施設群はそれぞれ別の街区として確認できる。'},
 'Haoye': {'region':'深圳市宝安区・沙井中心地区西側','peak_regions':['沙井・京基百納広場周辺'], 'sources':[
 {'url':'https://jtys.sz.gov.cn/zwgk/xxgkml/ghjh/zxgh/content/post_4278186.html','basis':'京基百納周辺は宝安区沙井街道中心区西区と記載。周辺のスーパー・病院・バス施設も記載。'},
 {'url':'https://www.sz.gov.cn/cn/xxgk/zfxxgj/gqdt/content/mpost_12131470.html','basis':'沙井街道と沙井京基百納広場の活動を確認。'}], 'terms':['沙井','京基','百纳','Vanguard','华润','沙头'], 'assessment':'西郷の蚝業社区という候補は採用しない。周辺の沙井店舗・施設群と公的商圏資料が対応するため、地域を沙井として確認できる。'},
 'Hongshulin': {'region':'深圳市南山区・前海桂湾','peak_regions':['万象前海・前海卓悦INTOWN周辺'], 'sources':[
 {'url':'https://qh.sz.gov.cn/en/life-in-qianhai/malls-and-places-for-leisure/content/post_10660073.html','basis':'万象前海は前海桂湾・桂湾四路169号、前海卓悦INTOWNは夢海大道5033号。'}], 'terms':['万象前海','前海','SCIA','桂湾'], 'assessment':'福田の紅樹林保護区を参照する根拠はない。POI群は万象前海と隣接施設で、前海桂湾の商圏と確認できる。'}
}
def main():
    local=json.loads(ROOT.joinpath('local.json').read_text(encoding='utf-8'))
    address_path=ROOT/'addresses.json'
    acquisition=json.loads(address_path.read_text(encoding='utf-8')) if address_path.exists() else None
    addresses={r['fsq_place_id']:r for r in acquisition['items']} if acquisition else {}
    items=[]
    for r in local['items']:
        checked=CHECKED[r['original']];unique={p['id']:p for p in r['samples']}
        anchors=[]
        for i,p in enumerate(r['peaks']):
            near=[s for s in r['samples'] if s['center']==f'peak{i}'];chosen=[s for s in near if any(t.lower() in s['name'].lower() for t in checked['terms'])][:12]
            anchors.append({**p,'region':checked['peak_regions'][i],'poi_count_1km':len(near),'poi_count_300m':sum(s['distance_m']<=300 for s in near),'evidence_pois':[{**s,'address_record':addresses.get(s['id'])} for s in chosen]})
        joined=[addresses[k] for k in unique if k in addresses]
        items.append({'reference_id':r['id'],'original':r['original'],'reference_coordinates':[r['lon'],r['lat']],**checked,'unique_local_pois':len(unique),'address_nonempty':sum(bool(p.get('address')) for p in joined),'localities':dict(Counter(p.get('locality') or '(missing)' for p in joined)),'peaks':anchors})
    report={'reviewed_at':'2026-10-10','radius_m':1000,'unique_pois':local['unique_pois'],'address_acquisition_verified':bool(acquisition and acquisition['ids_and_coordinates_verified']),'snapshot_id':acquisition['snapshot_id'] if acquisition else None,'decision':'4地域を施設群と公的所在地で確認。元GeoNames地名の翻訳確定とは区別。6峰を座標・参照IDで限定し、確認済みの商圏・施設名を表示へ反映。密度・POIは変更しない。','items':items}
    Path('docs/held-locale-poi-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    lines=['# 保留4参照名の周辺POI確認','','4参照名に割り当てられた6峰と参照地点の各1kmを調査。重複を除く2,065件の施設名を確認し、公的資料の所在地と照合した。各峰の商圏・周辺地域を確認できた。元の曖昧な地名がこの街区の正式名だという判定ではない。','','|元参照名|確認した地域|峰別の参照候補|','|---|---|---|']
    for r in items:lines.append('|'+r['original']+'|'+r['region']+'|'+ '／'.join(r['peak_regions'])+'|')
    lines+=['','## 根拠','']
    for r in items:
        lines+=['### '+r['original'],'',r['assessment'],'']
        for p in r['peaks']:
            lines+=['- '+p['region']+'：1km内'+str(p['poi_count_1km'])+'件、300m内'+str(p['poi_count_300m'])+'件。代表施設：'+ '、'.join(s['name'] for s in p['evidence_pois'][:4])+'。']
        for s in r['sources']:lines+=['- [所在地の資料]('+s['url']+')：'+s['basis']]
        lines+=['- 元住所欄あり：'+str(r['address_nonempty'])+'件／周辺固有ID '+str(r['unique_local_pois'])+'件。']
        lines+=['']
    lines+=['## 住所欄と限界','',('同じFSQ snapshotの住所欄を取得し、2,065件全てのIDと原座標をローカル原本と一致検証。住所のある数とlocality内訳、代表ID・住所・峰からの距離はJSONに保存。' if report['address_acquisition_verified'] else 'FSQの住所欄取得は実行中。施設名と公的所在地の照合結果は記録済みだが、原住所欄の確認完了とは扱わない。'),'','峰から施設までの距離は元FSQ座標に対するWGS84測地距離で、位置精度の保証ではない。公的住所・商圏資料と複数の店舗名が対応するため地域同定の根拠とした。個々の全店舗の誤位置・重複を検査したわけではない。曖昧な近隣地名だけを理由にPOIや密度面を削除する根拠は得られなかった。画面の名称は、6峰それぞれの原座標と参照IDを照合して確認済み商圏・施設名へ変更。元地名はポップアップに残す。','','[ID・原座標・住所欄・判定記録](held-locale-poi-review.json)。再現：`scripts/research_held_locale_pois.py` → `scripts/report_held_locale_pois.py`。取得記録はGit除外の `data/name-research/held-locale-pois/`。']
    Path('docs/held-locale-poi-review.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ['unique_pois','address_acquisition_verified','snapshot_id']}))
if __name__=='__main__':main()
