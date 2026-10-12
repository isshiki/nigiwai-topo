"""Review-specific display quarantine; never removes source POIs or terrain."""
import json
from pathlib import Path
from collections import Counter
from pyproj import Geod

GEOD=Geod(ellps='WGS84')
def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))

def main():
    audit=load('data/name-research/held-poi-addresses/audit-detail.json')
    impact=load('docs/held-peak-exclusion-impact.json')
    targets={r['peak']:r for r in load('docs/held-peak-investigation.json')['items']}
    if any(r['peak'] not in targets for r in impact['items']):raise ValueError('Unexpected review target')
    centers={'BR':[-51.92528,-14.235004],'ID':[113.921327,-0.789275]}
    extra={
        '-20.000, 145.000':{'fsq_id':'688dd8474eb9e53c2abe7428','name':'RSEA Safety Gladstone','address_components':['55','Hanson'],'locality':'Gladstone Central','postcode':'4680','source_url':'https://www.rsea.com.au/article/896/gladstone-store-relocates','basis':'2022年の公式移転記事の店舗名・番地・道路・都市・郵便番号が元住所と対応。'},
        '-33.000, 146.000':{'fsq_id':'5217489b7e48110568e421aa','name':'Cherrybrook Physiotherapy','address_components':['Appletree','Shopping','Centre'],'locality':'Cherrybrook','postcode':'2126','source_url':'https://www.lifecare.com.au/clinic/cherrybrook-physiotherapy/','basis':'運営者の施設名・ショッピングセンター・都市・郵便番号が元住所と対応。'},
        '-13.001, -54.000':{'fsq_id':'4f9090c4e4b04fd33dd62bd7','name':'IFAL Campus PIn','address_components':['Palmeira','Fora'],'locality':'Palmeira Dos Índios','postcode':None,'source_url':'https://www2.ifal.edu.br/campus/palmeira/o-campus/estrutura','basis':'キャンパス略称だけでなく元住所のPalmeira de Foraと都市名も公式キャンパス資料に対応。'},
    }
    items=[]
    for result in impact['items']:
        key=result['peak'];rows=next(r['records'] for r in audit['items'] if r['peak']==key)
        count=Counter((r['longitude'],r['latitude']) for r in rows)
        coordinate,n=count.most_common(1)[0]
        concentrated=sum(GEOD.inv(*coordinate,r['longitude'],r['latitude'])[2]<=100 for r in rows)
        states=Counter(r['status'] for r in rows)
        vanished=result['scenarios']['all_distant_candidates']['peaks_800_within_2km']==0
        reason=(f"近傍{len(rows)}件中、遠距離の都市名不整合候補{states['locality_reference_far']}件。最多の同一座標には{n}件、そこから100m以内には{concentrated}件。"
                f"異なる住所{len({r['address'] for r in rows if r['address']})}種・locality{len({r['locality'] for r in rows if r['locality']})}種を含む。")
        if vanished:reason+='不整合候補全件除外の仮定で半径2km内の800以上の峰が消えるため、山としての位置・高さの解釈に強い問題がある。'
        else:reason+='住所欠損等が多く、不整合候補のみの除外で残る密度も正しい位置と保証できない。通常の山として採用する根拠が不足するため暫定保留。'
        entry={'peak':key,'coordinates':result['coordinates'],'density':result['published_density'],'decision':'suppress_peak_annotation','confidence':'strong_location_artifact' if vanished else 'provisional_quality_hold','reason':reason,'statistics':{'records':len(rows),'status_counts':dict(states),'max_identical_coordinates':n,'within_100m_of_dominant_coordinate':concentrated},'prior_evidence_record':'docs/held-peak-investigation.json#'+key}
        if key in extra:
            e=extra[key];row=next(p for p in rows if p['fsq_place_id']==e['fsq_id'])
            assert row['name']==e['name'] and row['locality']==e['locality'] and row['postcode']==e['postcode']
            assert row['status']=='locality_reference_far'
            assert all(t.casefold() in row['address'].casefold() for t in e['address_components'])
            entry['additional_primary_check']=e
        country=rows[0]['country']
        if country in centers:
            distance=GEOD.inv(*result['coordinates'],*centers[country])[2]
            if distance<2000:
                entry['country_reference_proximity']={'source_url':'https://developers.google.com/public-data/docs/canonical/countries_csv','reference_coordinates':centers[country],'distance_m':round(distance),'limits':'国の参照座標との近接はデフォルト座標の疑いを補強するだけで、取得経路や全POIの誤位置を確定しない。'}
        items.append(entry)
    assert len(items)==13 and len({tuple(r['coordinates']) for r in items})==13
    report={'snapshot_id':impact['snapshot_id'],'reviewed_at':'2026-10-10','scope':'world / all / sigma 200m; exact original summit coordinates','policy':'Suppress the 13 reviewed summit labels, triangles, ranking entries and search suggestions. Keep raw POIs and terrain unchanged. Eight strong cases and five provisional holds; not a finding that every record is incorrect. Reversible individual decisions; no radius blacklist or global automatic rule.','items':items}
    Path('docs/held-peak-display-decisions.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    published=[{k:r[k] for k in ('peak','coordinates','density','confidence','reason')} for r in items]
    Path('web/peak-quality.js').write_text('window.NIGIWAI_PEAK_QUARANTINE='+json.dumps(published,ensure_ascii=False,separators=(',',':'))+';\n'+
        "window.nigiwaiPeakAllowed=(feature,area)=>area!=='world'||!window.NIGIWAI_PEAK_QUARANTINE.some(r=>feature.properties.kind==='peak'&&feature.properties.name_source==='coordinates'&&feature.properties.name===r.peak&&feature.geometry.coordinates.every((v,i)=>Math.abs(v-r.coordinates[i])<1e-7));\n",encoding='utf-8')
    md=['# 13峰の表示判断（2026-10-10）','','13峰とも通常の▲・名称・数値ラベル、ランキング、峰検索候補から外す。8峰は位置の問題を強く疑う結果、5峰は位置・密度を保証できないため暫定保留。全POIが誤りと確定した判断ではない。','','段彩・等高線・3Dは原本の密度を引き続き表示する。POIの削除・位置修正やS3の再生成は行わず、画面にこの限界を明記する。住所欠損を正しい位置と扱わず、13峰の元の頂だけを座標で限定して除外する。周辺の別の峰・日本版・他の地名には適用しない。','','|峰|判断の強さ|理由|','|---|---|---|']
    md.extend('|'+r['peak']+'|'+('位置問題の強い疑い' if r['confidence']=='strong_location_artifact' else '暫定保留')+'|'+r['reason']+'|' for r in items)
    md+=['','## 今回追加した一次照合','']
    md.extend(f"- {e['name']}（FSQ `{e['fsq_id']}`）：{e['basis']} [一次資料]({e['source_url']})。元座標は遠方の都市参照点から50km超。" for e in extra.values())
    md+=['','ブラジルとインドネシアの2峰は [Googleの国別参照座標](https://developers.google.com/public-data/docs/canonical/countries_csv) の近傍にも位置する。参照座標との一致・近接だけで個別POIを削除せず、住所の混在・欠損と合わせた保留判断に用いた。','','現在の公式資料にはsnapshotとの時差があり、会社・施設の移転の可能性は残る。Puneの候補企業は一次資料を取得できず、新しい個別確定例に加えなかった。トルコの文字化けlocalityや広域名を推測で正規化して誤位置確定数に加えていない。','','## 再現と解除','','`python scripts/decide_held_peak_display.py` で住所・ID・都市・郵便番号の対応を検証し、判定JSONと表示ポリシーを生成。解除は峰ごとに位置根拠を確保して判定を変更する。元の住所監査と除外感度分析は別途保存し、決定の根拠を追跡できる。','']
    Path('docs/held-peak-display-decisions.md').write_text('\n'.join(md),encoding='utf-8')
    print('13 annotations quarantined; 8 strong, 5 provisional; source and terrain unchanged')
if __name__=='__main__':main()
