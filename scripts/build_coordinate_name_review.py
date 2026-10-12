"""Publish explicit editorial proximity labels after inspecting all 60 records."""
import json
from pathlib import Path
from collections import Counter
from pyproj import Geod

# Row numbers are only review navigation: each decision also pins its source ID.
CHOICES={
 1:('8715384','アン・ナハダ'),2:('6300433','インチョン国際空港'),
 4:('7537781','ヴィラ・サン・ジョアン'),5:('8715385','アン・ナイーム'),
 6:('1624232','テンバガプラ'),7:('3467587','カナスヴィエイラス'),
 9:('12713335','ウンゴラレンマウル'),11:('1952007','テンガギラン'),
 12:('1736696','トゥアラン'),13:('1646305','チパナス'),
 14:('9871083','チョイン'),15:('8332176','バン・フアイ・ルアン'),
 17:('7281773','プライア・ド・フォルテ'),18:('448574','アン・ナシーム・アッシャルキー'),
 19:('6597481','サンパイ・ティガ'),20:('3473240','アブラアン'),
 21:('6597480','トゥグ・ウタラ'),22:('6589658','ハンジャワル'),
 23:('12689633','インチョン国際空港'),24:('3461233','イングレーゼス・ド・リオ・ヴェルメーリョ'),
 26:('6589679','パラガジェン'),27:('6925951','ウウラン・サトゥ'),
 29:('7668664','ティミカ空港'),31:('7537798','ペドラ・アングラール'),
 32:('8063716','モーホ・ジ・サン・パウロ'),35:('12148914','クアドラード'),
 36:('8715320','アル・バサーティーン'),37:('1628586','ソロワコ'),
 38:('1624843','タンジュン・レデブ'),39:('8065733','バン・コ・リペ'),
 43:('3461233','イングレーゼス・ド・リオ・ヴェルメーリョ'),
 44:('400675','キング・ハーリド国際空港'),45:('6194442','ソンサルリ'),
 47:('6408419','カリソロ'),48:('8332181','バン・モー・ケーン・トーン'),
 49:('750888','バイラムデレ'),51:('7874506','ジュレレ・ヴェーリョ'),
 53:('6300012','キング・ファハド国際空港'),54:('3444827','シェレン'),
 55:('1846278','チェチョン'),58:('313509','ギュンデュズレル'),59:('8715385','アン・ナイーム')
}
QUALITY={0,3,8,16,28,30,33,34,41,42,50,52}
GEOD=Geod(ellps='WGS84')

def main():
    report=json.loads(Path('data/name-research/coordinate-local-review.json').read_text(encoding='utf-8'))
    navigation=json.loads(Path('docs/coordinate-review-order.json').read_text(encoding='utf-8'))
    by_key={r['properties']['name']:r for r in report['items']}
    if len(navigation)!=60 or set(navigation)!=set(by_key):raise ValueError('Review targets changed')
    rows=[by_key[key] for key in navigation]
    if len(rows)!=60 or report['errors']:raise ValueError('Incomplete research')
    # Ensure regeneration cannot silently change row identity/order.
    expected=json.loads(Path('data/name-translation/world/coordinate-priority-review.json').read_text(encoding='utf-8'))['items']
    if set(by_key)!={r['properties']['name'] for r in expected}:raise ValueError('Review targets changed')
    evidence={r['peak']:r for r in json.loads(Path('data/name-research/coordinate-poi-cluster-audit.json').read_text(encoding='utf-8'))['items']}
    investigation=json.loads(Path('docs/held-peak-investigation.json').read_text(encoding='utf-8'))
    supplements={r['peak']:r for r in investigation['items']}
    overlays={};decisions=[]
    for i,r in enumerate(rows):
        label=r['properties']['name'];entry={'peak':label,'coordinates':r['coordinates'],'density':r['properties']['density'],'poi_cluster_evidence':evidence[label],'reviewed_at':'2026-10-10'}
        if label in supplements:
            extra=supplements[label]
            if extra['coordinates']!=r['coordinates']:raise ValueError('Investigation peak moved')
            entry['investigation_record']='docs/held-peak-investigation.json'
            if extra['decision']=='hold':
                entry.update(decision='hold',classification=extra['classification'],reason=extra['reason'])
            else:
                ref=extra['reference'];distance=GEOD.inv(*r['coordinates'],ref['lon'],ref['lat'])[2]
                if distance>2500:raise ValueError('Supplement reference too far')
                entry.update(decision='adopt',name=extra['name'],reference=ref,source_url=extra['source_url'],basis=extra['basis'])
                namespace=extra['source_id'].split(':')[0]
                provenance={'GeoNames':'GeoNames / CC BY 4.0','OpenStreetMap':'OpenStreetMap contributors / ODbL','Official':'Official university location reference'}[namespace]
                overlays[label]={'name':extra['name'],'source':provenance+' + reviewed editorial Japanese','source_id':extra['source_id'],'source_name':ref['name'],'source_url':extra['source_url'],'reference_distance_m':round(distance),'basis':extra['basis'],'status':'reviewed_coordinate_reference'}
                if extra.get('corroboration_url'):overlays[label]['corroboration_url']=extra['corroboration_url']
        elif i in QUALITY:
            entry.update(decision='hold',reason='代表地点への位置の丸め・初期値などの疑い。POIの位置精度を追加確認するまで近隣地名を割り当てない。誤位置と断定したものではありません。')
        elif i not in CHOICES:
            entry.update(decision='hold',reason='選択可能な参照地点まで2.5km以上。近隣集落・施設の追加資料を確認。')
        else:
            sid,name=CHOICES[i];source=next((p for p in r['local_candidates'] if p['id']==sid),None)
            if not source:raise ValueError('Reviewed source missing')
            distance=GEOD.inv(*r['coordinates'],source['lon'],source['lat'])[2]
            if distance>2500:raise ValueError('Selected reference too far')
            source_url=f"https://download.geonames.org/export/dump/{source['country']}.zip"
            basis=f"GeoNames国別地名資料の{source['name']}（ID {sid}）から{round(distance):,}mの参照名。近傍表記であり行政境界への包含判定ではありません。日本語はCodexで確認した音写です。"
            entry.update(decision='adopt',name=name+'付近',reference=source,source_url=source_url,basis=basis)
            overlays[label]={'name':name+'付近','source':'GeoNames / CC BY 4.0 + Codex reviewed transliteration','source_id':'GeoNames:'+sid,'source_name':source['name'],'source_url':source_url,'reference_distance_m':round(distance),'basis':basis,'status':'reviewed_coordinate_reference'}
        decisions.append(entry)
    # Rounded coordinate names can occur in more than one tile/peak. Apply only
    # when every record bearing that key lies near the chosen source.
    all_coordinates=json.loads(Path('data/name-translation/world/coverage-coordinate-peaks.json').read_text(encoding='utf-8'))['items']
    for label,entry in list(overlays.items()):
        chosen=next(r['reference'] for r in decisions if r['peak']==label and r['decision']=='adopt')
        matches=[r for r in all_coordinates if r['properties']['name']==label]
        if not matches or any(GEOD.inv(*r['coordinates'],chosen['lon'],chosen['lat'])[2]>2500 for r in matches):raise ValueError('Ambiguous coordinate key')
    summary={'target':60,'adopted':len(overlays),'held':60-len(overlays),'hold_reasons':dict(Counter(r.get('classification','location_quality' if i in QUALITY else 'distance_or_missing_reference') for i,r in enumerate(decisions) if r['decision']=='hold'))}
    Path('docs/world-coordinate-name-review.json').write_text(json.dumps({'summary':summary,'sources':report['sources'],'items':decisions},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    Path('data/name-research/reviewed-coordinate-overrides.json').write_text(json.dumps(overlays,ensure_ascii=False,indent=2),encoding='utf-8')
    js='Object.assign(window.NIGIWAI_COORDINATE_NAMES,'+json.dumps(overlays,ensure_ascii=False,separators=(',',':'))+');\n'
    warnings={r['peak']:{'basis':r['reason'],'status':'location_quality_review_pending'} for r in decisions if r['decision']=='hold' and (r.get('classification')=='location_quality' or r['peak'] in {rows[i]['properties']['name'] for i in QUALITY})}
    js+='window.NIGIWAI_COORDINATE_WARNINGS='+json.dumps(warnings,ensure_ascii=False,separators=(',',':'))+';\n'
    Path('web/world-coordinate-names.js').write_text(js,encoding='utf-8')
    print(json.dumps(summary))

if __name__=='__main__':main()
