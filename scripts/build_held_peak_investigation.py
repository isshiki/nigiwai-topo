"""Reproduce explicitly reviewed decisions; source evidence is not an automatic filter."""
import json
from pathlib import Path
from pyproj import Geod
GEOD=Geod(ellps='WGS84')
NOTES={
 '22.106, 77.185':('Decon Lighting Pvt. Ltd.','https://deconlighting.in/','企業公式サイトはDelhiで設立と説明。対象点はDelhiから大きく南に離れる。個別店舗の住所・同一性は未確定。'),
 '39.035, 35.244':(None,None,'761件中723件が同一座標。POI名には離れた道路・個人名等が混在。一次資料での施設同一性は未確定。'),
 '31.878, 53.438':(None,None,'431件中412件が同一座標。名称にはTabriz・Azerbaijanへの言及があるが、個別住所の一次照合は未完了。'),
 '-13.001, -54.000':('IFAL Campus PIn','https://www2.ifal.edu.br/campus/palmeira','IFALの公式キャンパス資料はPalmeira dos Índios（Alagoas）。対象点は同州から離れる。PInの略称対応は推定。'),
 '22.106, 72.577':('Hcp Interior Architecture Pvt. Ltd.','https://hcp.co.in/contact','HCPの公式事務所はAhmedabad、Pune、Chennai。対象点はこれらから離れる。会社名称の対応は有力だがFSQ住所照合待ち。'),
 '22.106, 72.565':('Gujarat Cancer and Research Institute (gcri)','https://gcriindia.org/contact.html','公式住所はCivil Hospital Campus, Asarwa, Ahmedabad。対象点はAhmedabadから大きく南に離れる。'),
 '-20.000, 145.000':('Chatime Toowong Village','https://www.toowongvillage.com.au/stores/chatime','施設公式サイトは9 Sherwood Road, Toowong, QLD 4066。RSEA Safety Gladstoneも公式住所55 Hanson Rd, Gladstoneと別途照合。両都市とも対象点から離れる。'),
 '-33.000, 146.000':('Teddington Legal','https://teddingtonlegal.com.au/contact-us/','公式所在地はHaymarket NSW 2000等。対象点はHaymarketから離れる。分散型法律事務所のため全サービスの位置を代表するかは別途確認。'),
 '39.062, 35.124':('NEU Hospital (International Patients Department)','https://medicine.neu.edu.tr/incoming/?lang=en','公式サイトはNear East University Campus in Nicosia。対象点はNicosiaから離れる。275件中85件の同一座標集中もあり、単なる参照名不足から位置品質確認へ分類変更。'),
 '-14.235, -51.925':('Banco Itau Paraguay S.A.','https://www.itau.com.py/paginas/atencionparavos','公式本店はOliva esquina Chile, Asunción。ブラジル中央の対象点に対し国・都市が一致しない。個別支店は特定していない。'),
 '39.761, -98.501':('Harbour Grand Kowloon','https://www.harbourgrand.com/kowloon/en/contact-us/','ホテル公式住所は20 Tak Fung Street, Hunghom, Kowloon（香港）。Kansasの対象点と国が一致しない。'),
 '22.106, 73.866':(None,None,'222件中82件が同一座標。別のインド3峰と緯度22.1058が共通。Puneを示唆する名称があるが一次資料で個別住所を確定できていない。'),
 '-0.788, 113.921':('RS. Soedarso','https://polise.kalbarprov.go.id/layanan/73/standar-pelayanan-rawat-jalan-rsud-dr-soedarso','州政府の病院サービス資料はPontianak。対象点はPontianakから東へ離れる。病院の同一性は名称照合による。'),
}
def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def main():
    research=load('data/name-research/held-peak-features.json');by={r['peak']:r for r in research['items']}
    if len(by)!=18:raise ValueError('Expected original 18 review targets')
    decisions={}
    for peak,(poi,url,note) in NOTES.items():
        row=by[peak];sample=next((p for p in row['poi_samples'] if p['name']==poi),None) if poi else None
        if poi and not sample:raise ValueError('Evidence POI missing: '+str(poi))
        decisions[peak]={'decision':'hold','classification':'location_quality','conclusion':note,'primary_comparison':{'poi':sample,'source_url':url,'matching':'name-based comparison; upstream address and historical identity not independently confirmed'} if url else None,'reason':note+' POIの位置精度を追加確認中。全レコードを誤位置と断定したものではありません。'}
    for peak,sid,name,url in [
        ('24.854, 46.719','12456147','ヌーラ王女大学','https://pnu.edu.sa/en/Pages/Contact-US.aspx'),
        ('28.649, 48.369','285750','アン・ナーミ',None)]:
        ref=next(r for r in by[peak]['candidates'] if r['id']==sid)
        source=f'https://download.geonames.org/export/dump/{ref["country"]}.zip'
        decisions[peak]={'decision':'adopt','classification':'reference_found','name':name+'付近','reference':ref,'source_id':'GeoNames:'+sid,'source_url':source,'corroboration_url':url,'basis':f'GeoNames国別資料の{ref["name"]}（ID {sid}）の参照地点。日本語は編集表記。近傍名であり行政境界への包含判定ではありません。'+('大学公式資料と近隣POI名称も照合。' if url else 'KWファイルの587件を確認。前回のSA単独検査0件は国選択の漏れでした。')}
    # This is the named place anchor embedded by the university, not an arbitrary
    # map viewport centre. The embed pairs the point with the institution name.
    official=load('data/name-research/held-official-map-links.json')['pmu']
    embed=next(u for u in official['iframes'] if 'Prince+Mohammad' in u)
    decisions['26.146, 50.092']={'decision':'adopt','classification':'reference_found','name':'ムハンマド・ビン・ファハド王子大学付近','reference':{'id':'pmu-contact-map','name':'Prince Mohammad Bin Fahd University','country':'SA','lon':50.0926,'lat':26.146104},'source_id':'Official:pmu-contact-map','source_url':official['source_url'],'map_link':embed,'basis':'大学公式問い合わせページの大学名付き埋込地図の参照地点。近隣の大学・学内施設POIとも照合。日本語は編集表記、行政境界への包含判定ではありません。'}
    for peak,key,way,name,official_url in [
        ('19.031, 99.890','phayao',579088013,'パヤオ大学','https://www.up.ac.th/contact.aspx'),
        ('-4.109, 137.101','ridge-camp',505668631,'リッジ・キャンプ','https://ptfi.co.id/id/news/detail/resmi-dibuka-mess-hall-kenanga-megah-di-super-block-ridge-camp')]:
        osm=load('data/name-research/held-osm-'+key+'.json')
        e=next(e for e in osm['result']['elements'] if e['type']=='way' and e['id']==way)
        ref={'id':str(way),'name':e['tags']['name'],'country':'TH' if key=='phayao' else 'ID',**e['center']}
        decisions[peak]={'decision':'adopt','classification':'reference_found','name':name+'付近','reference':ref,'source_id':f'OpenStreetMap:way/{way}','source_url':f'https://www.openstreetmap.org/way/{way}','corroboration_url':official_url,'basis':f'OpenStreetMap way/{way}の範囲の代表点（境界箱の中心）を参照し、公式施設資料と近隣POI名称を照合。日本語は編集表記。敷地内という包含判定ではありません。'}
    items=[]
    for peak,row in by.items():
        d=decisions[peak]
        if d['decision']=='adopt':
            ref=d['reference'];distance=GEOD.inv(*row['coordinates'],ref['lon'],ref['lat'])[2]
            if distance>2500:raise ValueError('Reference exceeds distance limit')
            d['reference_distance_m']=round(distance);d['basis']+=f' 峰から参照点まで{round(distance):,}m。'
        items.append({'peak':peak,'coordinates':row['coordinates'],'density':row['density'],'active_poi_count':row['active_poi_count'],'nearest_features':row['candidates'][:8],**d})
    report={'checked_at':'2026-10-10','summary':{'investigated':18,'newly_named':5,'location_quality_held':13,'holds_with_primary_name_comparison':sum(bool(r.get('primary_comparison')) for r in items)},'limits':'Official name/address comparisons support suspicion; they do not establish all nearby IDs are erroneous. Original snapshot lacks address/locality in local projection. No density or geometry removed/recomputed. OSM centres are bounding-box representative points, not polygon containment.','additional_evidence':{'rsea':'https://www.rsea.com.au/articleview.aspx?id=35','osm_timestamp':{k:load('data/name-research/held-osm-'+k+'.json')['result'].get('osm3s',{}) for k in ['phayao','ridge-camp']}},'sources':research['sources'],'items':items}
    Path('docs/held-peak-investigation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    md=['# 保留18峰の追加調査（2026-10-10）','',
        '18峰すべてを再調査し、5峰に参照名を追加、13峰を位置品質の確認待ちとした。元の60峰では47峰を命名・13峰を保留。密度・地形・順位は変更していない。','',
        'GeoNames国別資料の全地物種別を15km以内で照会。命名に採用する参照点は従来どおり2.5km以内。大学・鉱山キャンプは公式資料と近隣POI名称も照合し、必要に応じて公開OSMの限定照会を使った。範囲の中心は参照点であり、敷地・行政界への包含判定ではない。','',
        '## 名前を補えた5峰','', '|峰の緯度・経度|表示名|参照点との距離|根拠|','|---|---|---:|---|']
    for r in items:
        if r['decision']=='adopt':md.append(f'|{r["peak"]}|{r["name"]}|{r["reference_distance_m"]:,}m|[参照資料]({r["source_url"]})'+(f'・[公式照合]({r["corroboration_url"]})' if r.get('corroboration_url') else '')+'|')
    md+=['','クウェートの峰は前回、最寄りの遠い地名に基づいてSAファイルだけを検査し0件だった。今回はKWも調べ587件を確認。国境で「最寄り地名の国＝POIの国」と仮定すると取りこぼす例だった。','',
        'パヤオ大学の公式ページにある地図の表示中心は峰から約3.8km離れるため、その中心だけを根拠に採用していない。大学公式名称・住所とOSM wayの大学名・website・電話番号を照合し、近傍の参照点を採用した。リッジ・キャンプも近い実在山・登山キャンプの名称へ置き換えず、OSMのRidge Campと運営主体PT Freeportの施設説明を照合した。','',
        '## 位置品質の確認待ち13峰','',
        '10峰で一次資料の名称・所在地との比較が得られ、3峰は局所データからの疑いにとどまる。一次資料で施設名が見つかっても、FSQの元住所・履歴・個別支店の対応を確認できていないため、全POIの誤位置確定数や世界全体の誤り率として扱わない。','']
    for r in items:
        if r['decision']=='hold':
            md+=['### '+r['peak'],'',r['conclusion'],'']
            if r.get('primary_comparison'):md+=['[照合した一次資料]('+r['primary_comparison']['source_url']+')。対象FSQ ID: `'+r['primary_comparison']['poi']['id']+'`。','']
    md+=['## 残る確認と修正方針','',
        '1. 13峰の元FSQ住所・locality・履歴を固定snapshotから追加取得し、名前だけの照合をIDごとの住所照合へ進める。現在のローカルParquetには住所が含まれない。',
        '2. 誤位置と確認できた個別IDと、疑いのある代表座標・微小な散らばりを区別した除外候補リストを作る。同一座標だけで除外しない。',
        '3. 除外前後のPOI件数・峰数・順位を対象区画で比較し、変更の影響と根拠を記録してからタイルを再生成する。現段階では位置を推測で修正しない。','',
        '詳細: `held-peak-investigation.json`。再現: `research_held_peak_features.py` → `research_held_osm.py`（ネットワーク）→ `build_held_peak_investigation.py` → `build_coordinate_name_review.py`。公式大学地図リンクは `data/name-research/held-official-map-links.json` に保存。公開資料の照合日は2026-10-10、FSQは2026-09-15 snapshot。住所変更・閉鎖・移転の時間差にも注意する。','']
    Path('docs/held-peak-investigation.md').write_text('\n'.join(md),encoding='utf-8')
    print(json.dumps(report['summary']))
if __name__=='__main__':main()
