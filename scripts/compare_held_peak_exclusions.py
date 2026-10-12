"""Local sensitivity experiment using the unchanged production density kernel.

Never edits source, distribution, frontend configuration, or remote storage.
"""
import json,math
from pathlib import Path
from collections import Counter
import numpy as np
from global_density import density,DLON,DLAT,GEOD,row_metrics
from build_global_sample import peak_mask,surface
from prepare_world import connection
from fetch_world import write_json

OUT=Path('data/validation/held-poi-impact')
SIZE=100
PADDING=30
def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def validate_reviewed_ids(review,records):
    result=set()
    for decision in review['items']:
        r=records[decision['id']]
        if r['status']!='locality_reference_far' or r['name']!=decision['name']:raise ValueError('Reviewed identity or screening status changed')
        if [r['longitude'],r['latitude']]!=decision['coordinates'] or r['locality']!=decision['locality']:raise ValueError('Reviewed source moved')
        if not all(t.casefold() in (r['address'] or '').casefold() for t in decision['address_components']):raise ValueError('Reviewed address changed')
        result.add(decision['id'])
    return result
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    audit=load('data/name-research/held-poi-addresses/audit-detail.json')
    records={r['fsq_place_id']:r for item in audit['items'] for r in item['records']}
    review=load('docs/reviewed-poi-location-conflicts.json')
    manifest=load('data/world-build/manifest.json')
    if manifest['snapshots']['places']['snapshot_id']!=review['snapshot_id']:raise ValueError('Snapshot mismatch')
    strict=validate_reviewed_ids(review,records)
    broad={sid for sid,r in records.items() if r['status']=='locality_reference_far'}
    if not strict<=broad:raise ValueError('Scenarios not nested')
    exclusions={'original':set(),'reviewed_only':strict,'all_distant_candidates':broad}
    write_json(OUT/'exclusion-scenarios.json',{'snapshot_id':review['snapshot_id'],'experimental_only':True,'scenarios':{k:sorted(v) for k,v in exclusions.items()}})
    targets=[r for r in load('docs/held-peak-investigation.json')['items'] if r['decision']=='hold']
    # Retain a shared global lattice; a smaller output window does not change
    # production cell spacing, Gaussian support, metric areas, or sigma.
    for r in targets:
        lon,lat=r['coordinates'];px=round((lon+180)/DLON);py=round((lat+90)/DLAT)
        r['i']=px//SIZE;r['j']=py//SIZE
        w=-180+(r['i']*SIZE-PADDING)*DLON;e=w+(SIZE+2*PADDING)*DLON
        s=-90+(r['j']*SIZE-PADDING)*DLAT;n=s+(SIZE+2*PADDING)*DLAT
        r['bbox']=[w-.1,s-.015,e+.1,n+.015]
    cache=OUT/'local-input.parquet';cache_meta=OUT/'local-input.json'
    with connection() as con:
        if not(cache.exists() and cache_meta.exists()):
            clauses=[];params=['data/world-build/active.parquet']
            for r in targets:
                w,s,e,n=r['bbox'];clauses.append('(longitude BETWEEN ? AND ? AND latitude BETWEEN ? AND ?)');params +=[w,e,s,n]
            # All source country codes are retained, including nearby countries.
            sql='SELECT fsq_place_id,longitude,latitude FROM read_parquet(?) WHERE '+' OR '.join(clauses)
            con.execute("COPY ("+sql+") TO '"+cache.as_posix()+"' (FORMAT PARQUET)",params)
            write_json(cache_meta,{'snapshot_id':review['snapshot_id'],'source_sha256':manifest['sha256'],'boxes':[r['bbox'] for r in targets]})
        else:
            saved=load(cache_meta)
            if saved['snapshot_id']!=review['snapshot_id'] or saved['source_sha256']!=manifest['sha256'] or saved['boxes']!=[r['bbox'] for r in targets]:raise ValueError('Comparison cache differs')
        rows=con.execute('SELECT * FROM read_parquet(?)',[str(cache)]).fetchall()
    ids=np.array([r[0] for r in rows]);points=np.array([[r[1],r[2]] for r in rows])
    if not broad<=set(ids):raise ValueError('Exclusion IDs missing from production source')
    results=[]
    for number,target in enumerate(targets):
        lon,lat=target['coordinates'];w,s,e,n=target['bbox']
        spatial=(points[:,0]>=w)&(points[:,0]<=e)&(points[:,1]>=s)&(points[:,1]<=n)
        local_ids=ids[spatial];local_points=points[spatial]
        scenarios={}
        previous_density=None
        for label,excluded in exclusions.items():
            keep=np.array([sid not in excluded for sid in local_ids],dtype=bool)
            xs,ys,z=density(local_points[keep],target['i'],target['j'],200,size=SIZE,padding=PADDING)
            if previous_density is not None and np.any(z>previous_density+1e-8):
                raise ValueError('Nested exclusions increased density on the comparison grid')
            previous_density=z.copy()
            c=int(np.argmin(abs(xs-lon)));r=int(np.argmin(abs(ys-lat)))
            if abs(xs[c]-lon)>1e-9 or abs(ys[r]-lat)>1e-9:raise ValueError('Original summit not on shared lattice')
            xx,yy=np.meshgrid(xs,ys);_,_,distance=GEOD.inv(np.full(xx.shape,lon),np.full(yy.shape,lat),xx,yy)
            vicinity=distance<=2000
            area_x,area_y=row_metrics(ys);area=(area_x*area_y)[:,None]/1e6
            counts=int(np.count_nonzero(peak_mask(z,ys)&vicinity&(z>=800)))
            scenarios[label]={'removed_local_input_ids':int(np.count_nonzero(~keep)),'density_at_original_summit':float(z[r,c]),'max_density_within_2km':float(z[vicinity].max()),'peaks_800_within_2km':counts,'area_800_within_2km_km2':float(np.sum((z>=800)*vicinity*area))}
            if label=='original' and round(float(z[r,c]))!=target['density']:raise ValueError('Production baseline not reproduced')
            def namer(x,y):return {'name':f'{y:.3f}, {x:.3f}','name_source':'coordinates','name_basis':'検証用の座標表示'}
            geo=surface(xs,ys,z,namer);geo['experiment']={'scenario':label,'original_peak':target['peak'],'production_data_unchanged':True}
            write_json(OUT/f'{number:02d}-{label}.geojson',geo)
        results.append({'peak':target['peak'],'coordinates':target['coordinates'],'published_density':target['density'],'scenarios':scenarios})
        print(json.dumps({'peak':target['peak'],'densities':{k:round(v['density_at_original_summit']) for k,v in scenarios.items()}}),flush=True)
    for scenario in exclusions:
        ranked=sorted(results,key=lambda r:-r['scenarios'][scenario]['density_at_original_summit'])
        for rank,r in enumerate(ranked,1):r['scenarios'][scenario]['rank_among_original_13_positions']=rank
    report={'snapshot_id':review['snapshot_id'],'sigma_m':200,'floor':800,'production_baseline_verified':True,'experimental_only':True,'excluded_ids':{k:len(v) for k,v in exclusions.items()},'limits':'Rank compares the original 13 summit positions, not global rankings or surviving summit locations. 2km windows overlap; peak counts/areas must not be summed. Broad scenario is hypothetical, not confirmed incorrect IDs. No corrected coordinates inferred or source/distribution changed. Same production lattice, kernel, metric areas, halo and snapshot; active input includes all country codes.','items':results}
    write_json(OUT/'report.json',report)
    write_json(Path('docs/held-peak-exclusion-impact.json'),report)
    below=sum(r['scenarios']['all_distant_candidates']['density_at_original_summit']<800 for r in results)
    no_peak=sum(r['scenarios']['all_distant_candidates']['peaks_800_within_2km']==0 for r in results)
    md=['# 保留13峰：POI除外の影響比較（2026-10-10）','',
        '## 結果','',
        f'公式資料の住所・施設名との対応が強い4個のFSQ IDを個別確認した。これだけを除外した試算では峰は残り、元13地点の密度順位も変わらなかった。一方、都市名との遠距離不整合候補{len(broad):,}件をすべて除いた仮の感度分析では、元13地点中{below}地点が表示下限800未満になり、同じ{no_peak}地点では半径2km内の800以上の峰もなくなった。','',
        '**後者は3,470件を誤位置と確定した結果ではない。配信データには採用していない。** 都市名未登録・未照合などの1,926件と、近い候補のある40件は残す条件で比較した。未照合を正しい位置と保証したものではない。半径2kmの窓は重なるため、峰数や面積を地域合計として足さない。','',
        '## 元の峰の位置での密度（件/km²）','',
        '|峰の緯度・経度|現状|個別確認4件を除外|候補3,470件を除外する仮定|13地点内の順位：現状→仮定|','|---|---:|---:|---:|---|']
    for r in results:
        values=r['scenarios'];md.append('|'+r['peak']+'|'+ '|'.join(f'{round(values[k]["density_at_original_summit"]):,}' for k in exclusions)+'|'+str(values['original']['rank_among_original_13_positions'])+'→'+str(values['all_distant_candidates']['rank_among_original_13_positions'])+'|')
    md+=['','順位は元13地点だけの順位。世界ランキングや、移動後の頂の順位ではない。表の0は四捨五入値で、近傍全体に登録が一切ないという意味ではない。','',
        '## 個別に確認した4件','',
        '番地・建物・地区などの元住所の構成要素、元locality、公式施設資料が対応するものを選んだ。モデルの推測や同一座標だけによる判定ではない。元の施設住所に対応する正確な座標への移動は行っていない。','']
    for r in review['items']:md+=['- **'+r['name']+'**（FSQ `'+r['id']+'`）：'+r['basis']+' [一次資料]('+r['source_url']+')。']
    md+=['','個別判定は `docs/reviewed-poi-location-conflicts.json`。公式資料は現在の内容なので、snapshot時点との移転・社名変更の時間差は残る。HCPは内装設計会社側の公式資料まで絞り、302 Paritosh Buildingの住所対応を確認した。','',
        '## 再計算の検証','',
        '- 全13地点で再計算した現状密度を四捨五入すると、配信済み峰の密度と完全一致した。',
        '- 現行の `global_density.density()` を使い、共有格子の間隔・σ200m・件/km²への換算・カーネル支持範囲を維持。周辺余白を付けた局所格子で計算。',
        '- 密度入力は全世界のactive原本から取り、国別ファイルや13峰の約1.1km四方だけには限定しない。除外候補IDが全て計算用入力にも存在することを確認した。',
        '- 各条件で除外後密度が現状を上回らないこと、4件除外の密度が3,470件除外の密度を下回らないことを検証する。',
        '- 39個の検証用GeoJSON（段彩・等高線・峰）、入力キャッシュ、除外ID一覧、詳細結果は `data/validation/held-poi-impact/` に保存。配信PMTiles、S3、通常画面の地形は更新していない。','',
        '```powershell',
        '.venv\\Scripts\\python.exe scripts/compare_held_peak_exclusions.py',
        '.venv\\Scripts\\python.exe -m unittest discover -s tests -p test_held_exclusion_impact.py',
        '```','',
        '## 次の修正判断','',
        '4件だけの除外では問題の山を解消できない。一括の50km距離条件も確定判定にはしない。次に、住所と郵便番号がそろったNew Delhi・Ahmedabad・Pune等の都市群を重点的に照合し、地名別名の取り違え・同名地区・広域localityを除外したID単位の判定を増やす。住所不足が多いブラジルやインドネシア、トルコの残る峰は、代表点への集中だけで全レコードを削除せず、位置確認待ちの表示を維持する。','']
    Path('docs/held-peak-exclusion-impact.md').write_text('\n'.join(md),encoding='utf-8')
if __name__=='__main__':main()
