"""Compare source locality strings with independent gazetteer point references.

Distance to a locality reference is a screening signal, not address geocoding,
polygon containment, a confirmed error count, or an automatic exclusion rule.
"""
import io,json,zipfile,unicodedata,math
from pathlib import Path
from collections import Counter,defaultdict
import duckdb
from pyproj import Geod
from datetime import datetime,timezone

ROOT=Path('data/name-research/held-poi-addresses')
GEOD=Geod(ellps='WGS84')
THRESHOLD=50000
COUNTRY_ONLY={
    'US':{'usa','us','unitedstates','unitedstatesofamerica','america'},
    'BR':{'brasil','brazil','br'},'IN':{'india','in'},
    'ID':{'indonesia','id'},'IR':{'iran','ir'},
    'TR':{'turkey','turkiye','türkiye','tr'},'AU':{'australia','au'},
}
def normalized(value):
    value=unicodedata.normalize('NFKD',value or '').casefold().translate(str.maketrans({'ي':'ی','ك':'ک'}))
    return ''.join(c for c in value if c.isalnum())
def match_locality(lon,lat,candidates):
    if not candidates:return {'status':'unmatched_locality','candidate_count':0}
    ranked=sorted(({**r,'distance_m':round(GEOD.inv(lon,lat,r['lon'],r['lat'])[2])} for r in candidates),key=lambda r:r['distance_m'])
    return {'status':'locality_reference_far' if ranked[0]['distance_m']>THRESHOLD else 'locality_reference_not_far','candidate_count':len(ranked),'nearest_references':ranked[:3]}
def reference_index(keys,countries):
    index=defaultdict(dict)
    for country in countries:
        archive=Path('data/name-research/coordinate-countries')/(country+'.zip')
        with zipfile.ZipFile(archive) as z,z.open(country+'.txt') as stream:
            for line in io.TextIOWrapper(stream,encoding='utf-8'):
                f=line.rstrip('\n').split('\t')
                if f[6]!='P' or f[7] in ('PPLH','PPLQ','PPLW') or f[8]!=country:continue
                aliases={normalized(s) for s in [f[1],f[2],*f[3].split(',')]}
                for alias in aliases & keys[country]:
                    index[(country,alias)][f[0]]={'id':f[0],'name':f[1],'country':country,'lon':float(f[5]),'lat':float(f[4]),'feature_code':f[7],'modified':f[18]}
    return {k:list(v.values()) for k,v in index.items()}
def main():
    original=json.loads(Path('docs/held-peak-investigation.json').read_text(encoding='utf-8'))
    targets=[r for r in original['items'] if r['decision']=='hold']
    meta=json.loads((ROOT/'all.json').read_text(encoding='utf-8'))
    con=duckdb.connect(config={'threads':2,'memory_limit':'2GB'})
    cursor=con.execute('SELECT * FROM read_parquet(?)',[str(ROOT/'all.parquet')]);fields=[c[0] for c in cursor.description]
    raw=[dict(zip(fields,row)) for row in cursor.fetchall()];con.close()
    by_id={r['fsq_place_id']:r for r in raw}
    if len(by_id)!=len(raw):raise ValueError('Duplicate source IDs')
    source=json.loads(Path('data/name-research/held-peak-features.json').read_text(encoding='utf-8'))
    source_by={r['peak']:r for r in source['items']}
    expected={p['id']:p for t in targets for p in source_by[t['peak']]['poi_samples']}
    if set(by_id)!=set(expected):raise ValueError('Original evidence IDs not fully recovered')
    for sid,p in expected.items():
        row=by_id[sid]
        if row['longitude']!=p['lon'] or row['latitude']!=p['lat']:raise ValueError('Original snapshot coordinate differs')
    keys=defaultdict(set)
    for row in raw:
        if row.get('locality'):keys[row['country']].add(normalized(row['locality']))
    index=reference_index(keys,keys)
    summary=[];details=[]
    for target in targets:
        peak=target['peak'];pois=[by_id[p['id']] for p in source_by[peak]['poi_samples']]
        if len(pois)!=target['active_poi_count']:raise ValueError('Peak coverage mismatch')
        counts=Counter();city_counts=Counter();far_cities=Counter();evidence=[]
        for p in pois:
            city=p.get('locality');city_counts[city or '(未登録)']+=1
            if normalized(city) in COUNTRY_ONLY.get(p['country'],set()):
                result={'status':'country_only_locality','candidate_count':0}
            else:
                result=match_locality(p['longitude'],p['latitude'],index.get((p['country'],normalized(city)),[])) if city else {'status':'missing_locality','candidate_count':0}
            counts[result['status']]+=1
            if result['status']=='locality_reference_far':far_cities[city]+=1
            evidence.append({'fsq_place_id':p['fsq_place_id'],'name':p['name'],'address':p.get('address'),'locality':city,'region':p.get('region'),'admin_region':p.get('admin_region'),'postcode':p.get('postcode'),'country':p['country'],'longitude':p['longitude'],'latitude':p['latitude'],**result})
        primary=target.get('primary_comparison');primary_poi=primary.get('poi') if primary else None
        primary_row=next((r for r in evidence if primary_poi and r['fsq_place_id']==primary_poi['id']),None)
        info={'peak':peak,'records':len(pois),'address_present':sum(bool(p.get('address') and p['address'].strip()) for p in pois),'locality_present':sum(bool(p.get('locality') and p['locality'].strip()) for p in pois),'statuses':dict(counts),'top_localities':city_counts.most_common(10),'distant_localities':far_cities.most_common(10),'primary_business_evidence':{'source_url':primary['source_url'],'record':primary_row} if primary_row else None}
        summary.append(info);details.append({'peak':peak,'records':evidence})
    limits='Exactly recovered the IDs and coordinates of the original 13 local boxes. Locality aliases are exact after Unicode/case/punctuation normalization; no fuzzy matching or automatic exclusion. More than 50km from every same-country matched populated-place reference is only an address-locality inconsistency screening signal. Unmatched/missing locality is unknown, not valid. Historical source aliases, broad locality scope, old address, branch identity and wrong country remain possible. Not a worldwide quality rate. No geometry/density edited.'
    totals=Counter()
    for r in summary:totals.update(r['statuses'])
    report={'checked_at':datetime.now(timezone.utc).isoformat(),'snapshot_id':meta['snapshot_id'],'scope_peaks':13,'unique_records':len(raw),'threshold_m':THRESHOLD,'ids_and_coordinates_verified':True,'totals':dict(totals),'gazetteer_sources':{k:v for k,v in original['sources'].items() if k in keys},'limits':limits,'items':summary}
    (ROOT/'audit-detail.json').write_text(json.dumps({'limits':limits,'items':details},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    Path('docs/held-peak-address-audit.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    md=['# 保留13峰：元POI住所と座標の照合','',
        f'固定snapshot `{meta["snapshot_id"]}`（2026-09-15）の13峰近傍、計{len(raw):,}個のFSQ IDを取得。前回局所監査とID集合・座標の一致を全件検証した。住所・都市名・地域・郵便番号を追加取得した。閉店判明分は対象外。','',
        '## 照合結果','',
        f'元localityをGeoNames同国の集落・都市・地区の名称および別名と照合。全候補の代表点から50kmを超えて離れるものは{totals["locality_reference_far"]:,}件。50km以内の候補があるものは{totals["locality_reference_not_far"]:,}件。都市名未登録{totals["missing_locality"]:,}件、名称未照合{totals["unmatched_locality"]:,}件、国名だけの値{totals["country_only_locality"]:,}件。国名だけの値は都市への別名一致に使わない。','',
        '**これは誤位置の確定件数ではない。** 距離は住所の正確な緯度経度ではなく地名代表点との距離。近い候補があることも正しい住所の保証ではない。未照合・未登録を正常として扱わない。同名地の候補が一つでも近ければ遠距離の旗を立てない。住所変更、広いlocality範囲、古い別名、別支店、国コードの誤りは追加確認が必要。','',
        '|峰の緯度・経度|POI|住所あり|都市名あり|全照合候補から50km超|50km以内の候補あり|未照合・未登録|','|---|---:|---:|---:|---:|---:|---:|']
    for row in summary:
        counts=row['statuses'];md.append(f'|{row["peak"]}|{row["records"]:,}|{row["address_present"]:,}|{row["locality_present"]:,}|{counts.get("locality_reference_far",0):,}|{counts.get("locality_reference_not_far",0):,}|{counts.get("unmatched_locality",0)+counts.get("missing_locality",0)+counts.get("country_only_locality",0):,}|')
    md+=['','## 一次資料を照合済みの施設レコード','',
        '以下は前回の施設名検索と同じFSQ IDの元住所。元データ内の住所文字列と座標の整合性、公式資料の施設所在地との対応をそれぞれ確認するための証拠であり、名前の一致だけで全レコードを除外しない。','']
    for row in summary:
        primary=row['primary_business_evidence']
        if not primary:continue
        p=primary['record'];md+=['### '+row['peak']+' — '+p['name'],'',
            'FSQ ID: `'+p['fsq_place_id']+'`。元住所: '+str(p.get('address') or '未登録')+' / locality: '+str(p.get('locality') or '未登録')+' / region: '+str(p.get('region') or '未登録')+' / country: '+str(p['country'])+'。','',
            '[施設の一次資料]('+primary['source_url']+')。地名照合状態: `'+p['status']+'`。','']
        if p.get('nearest_references'):
            ref=p['nearest_references'][0];md+=['最短の照合候補: '+ref['name']+'（GeoNames '+ref['id']+'）、元座標から約'+f'{ref["distance_m"]/1000:,.1f}'+'km。','']
    md+=['## 根拠・再現・今後','',
        '- 元FSQ情報: `data/name-research/held-poi-addresses/*.parquet`（Git管理外）。同じsnapshotから住所を取得したSQLと非機密パラメータを `all.json` に保存。認証情報は保存しない。',
        '- 全IDごとの照合: `data/name-research/held-poi-addresses/audit-detail.json`。集計と公式資料照合ID: `docs/held-peak-address-audit.json`。',
        '- 地名参照: [GeoNames国別資料](https://download.geonames.org/export/dump/)、CC BY 4.0。歴史集落PPLH/PPLQ/PPLWは候補から除外。Unicode・大小文字・記号を正規化した完全一致だけを使い、曖昧な類似検索は使わない。',
        '- 誤位置の候補リストは検査用に保存したが、元POI・密度・峰・順位・配信タイルは変更していない。まず具体的な事業所の住所対応を確認し、確認済みIDの除外前後を区画単位で比較する。','',
        '```powershell',
        '.venv\\Scripts\\python.exe scripts/fetch_held_peak_addresses.py',
        '.venv\\Scripts\\python.exe scripts/audit_held_peak_addresses.py',
        '.venv\\Scripts\\python.exe -m unittest discover -s tests -p test_held_address_audit.py',
        '```','']
    Path('docs/held-peak-address-audit.md').write_text('\n'.join(md),encoding='utf-8')
    # Replace only the dedicated progress block; preserve prior work/docs.
    start='<!-- held-address-audit:start -->';end='<!-- held-address-audit:end -->'
    message=f'保留13峰近傍の{len(raw):,}個の元FSQ IDの住所情報を取得し、ID・座標一致を全件検証した。地名の全照合候補から50km超は{totals["locality_reference_far"]:,}件（不整合の検査候補であり、誤位置確定数ではない）。住所の欠損・名称未照合も記録。密度・地形・配信データは変更していない。詳しくは '
    for path,link in [(Path('README.md'),'docs/held-peak-address-audit.md'),(Path('docs/world-name-quality-plan.md'),'held-peak-address-audit.md')]:
        text=path.read_text(encoding='utf-8')
        if start in text and end in text:
            before,rest=text.split(start,1);_,after=rest.split(end,1)
            path.write_text(before+start+'\n'+message+'[元住所の照合結果]('+link+')。\n'+end+after,encoding='utf-8')
    print(json.dumps({'records':len(raw),'peaks':13,'totals':dict(totals)}))
if __name__=='__main__':main()
