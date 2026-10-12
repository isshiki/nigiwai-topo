"""Publish the reviewed first batch of source-backed coordinate reference names."""
import json,io,zipfile,os
from pathlib import Path
from collections import defaultdict
from build_world_display_names import japanese,js_object

ROOT=Path('data/name-research/unnamed-world')
WORLD_ROOT=Path(os.environ.get('NIGIWAI_WORLD_ROOT','data/distribution/foursquare-world-v2'))
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))

def cohort_counts(original_keys, present_keys, adopted_keys):
    """Count the original audit cohort in the selected density release."""
    original, present, adopted = map(set, (original_keys, present_keys, adopted_keys))
    if not adopted <= original & present:
        raise ValueError('Adopted names absent from selected release or original cohort')
    absent = sorted(original - present)
    return {'original_cohort':len(original), 'adopted':len(adopted),
            'remaining':len((original & present) - adopted),
            'absent_from_selected_release':len(absent), 'absent_peak_keys':absent}

def main():
    report=read(ROOT/'address-name-review.json')
    shortlist=read('docs/unnamed-world-name-approvals.json')['items'] if Path('docs/unnamed-world-name-approvals.json').exists() else read(ROOT/'adoption-shortlist.json')
    aliases=read(ROOT/'candidate-japanese-aliases.json')['aliases']
    by_peak={p['peak']:p for p in report['items']}
    facility={p['peak']:p for p in read(ROOT/'facility-name-review.json')['items']} if (ROOT/'facility-name-review.json').exists() else {}
    wanted=defaultdict(set)
    for p in shortlist:wanted[p['ref']['country']].add(p['ref']['id'])
    admins={}
    for country,ids in wanted.items():
        with zipfile.ZipFile(Path('data/name-research/coordinate-countries')/(country+'.zip')) as z,z.open(country+'.txt') as stream:
            for line in io.TextIOWrapper(stream,encoding='utf-8'):
                f=line.rstrip('\n').split('\t')
                if f[0] in ids:admins[f[0]]=country+'.'+f[10]
    context=read('data/name-research/world-name-context.json')['admin1']
    regions=js_object('web/world-regions.js')
    country_names={r['country_code']:r['name'] for r in regions.values() if 'country_code' in r}
    entries={};decisions=[]
    for choice in shortlist:
        p=by_peak[choice['peak']]
        if choice.get('policy') in ('reviewed_address_text_anchors','reviewed_public_cartographic_point','reviewed_public_cartographic_area','reviewed_census_place_boundary'):
            from reviewed_address_text import reviewed_text_reference
            c = reviewed_text_reference(choice, p)
        elif choice.get('policy')=='facility_text_review':
            evidence=next(c for c in facility[p['peak']]['candidates'] if c['id']==choice['ref']['id'])
            c={k:evidence[k] for k in ['id','name','lon','lat','feature_code']}
            country=evidence['admin1'].split('.')[0]
            c.update(country=country,source_url=f'https://download.geonames.org/export/dump/{country}.zip',distance_m=evidence['reference_distance_m'],supporting_pois=evidence['text_matches'],support_share=round(evidence['text_matches']/p['near_pois'],3))
            if evidence['distinct_coordinates']<8 or evidence['facility_name_matches']<3 or evidence['address_matches']<8:raise ValueError('Facility evidence below adopted criteria')
        else:
            c=p['candidates'][0]
            if p['status']!='candidate_supported':raise ValueError('Address candidate not supported')
        if c!=choice['ref']:raise ValueError('Research identity changed')
        minimum=(.85,6,1000,4,4) if choice.get('policy') in ('address_review_85','reviewed_address_text_anchors','reviewed_public_cartographic_point','reviewed_public_cartographic_area','reviewed_census_place_boundary') else (.85,12,300,8,8) if choice.get('policy')=='facility_text_review' else (.9,12,500,8,8)
        if choice.get('policy') == 'reviewed_official_address_anchors':
            from official_address_anchor_review import validate_anchor_review
            minimum = validate_anchor_review(choice, p, c)
        share,count,distance,coordinates,address=minimum
        if not (c['support_share']>=share and c['supporting_pois']>=count and c['distance_m']<=distance and p['distinct_coordinates']>=coordinates and p['with_address']>=address):raise ValueError('Evidence below adopted criteria')
        names=aliases.get(c['id'],[]);preferred=[n['name'] for n in names if n['preferred']]
        unique=[choice['ja_editorial']] if choice.get('ja_editorial') else sorted(set(preferred or [n['name'] for n in names]))
        if len(unique)!=1 or not japanese(unique[0]):raise ValueError('Ambiguous Japanese alias')
        admin=context.get(admins[c['id']],{}).get('ja')
        qualifier='・'.join(filter(None,[country_names[c['country']],admin]))
        name=unique[0]+'（'+qualifier+'）'
        name_basis='日本語人物紹介の出生地名を大学の本人取材記事で対応確認した編集表記（記事の居留地分類・正式日本語指定・音声検証の認定ではありません）' if choice.get('editorial_usage_kind')=='biographical_place_usage' else '自治体国際交流資料で対象国・州・村を確認した日本語使用例に基づく編集表記（正式日本語指定や音声検証の認定ではありません）' if choice.get('editorial_usage_kind')=='municipal_exchange' else '国の公開報告書で対象州を確認した日本語地名使用例に基づく編集表記（行政区分・実証地点と峰の同一性・公的指定・音声検証の認定ではありません）' if choice.get('editorial_usage_kind')=='government_report' else '近傍の同名気象地点の日本語用例を所在地名に対応させた編集表記（地点座標と峰位置の同一性・公的指定・発音録音の認定ではありません）' if choice.get('editorial_usage_kind')=='weather_station_name' else '大学公開研究題名の日本語歴史地名を公的史跡資料で現在集落に対応させた編集表記（論文本文や発音録音の認定ではありません）' if choice.get('editorial_usage_kind')=='historical_research_title' else '業界記事の日本語地域用例を地域資料で同名集落に対応させた編集表記（範囲の同一性や公的指定の認定ではありません）' if choice.get('editorial_usage_kind')=='industry_region_report' else '翻訳者と地理注を確認した大学公開訳詩資料の日本語使用例に基づく編集表記（公的指定や発音録音の認定ではありません）' if choice.get('editorial_usage_kind')=='literary_translation' else '著者と対象州を確認した学会誌資料の日本語用例に基づく編集表記（現地実訪・公的指定・発音録音の認定ではありません）' if choice.get('editorial_usage_kind')=='academic_report' else '対象州を確認した日本語報道訳の使用例に基づく編集表記（現地実訪・公的指定・発音録音の認定ではありません）' if choice.get('editorial_usage_kind')=='japanese_news_translation' else '取材者と対象州を確認した現地取材記事の日本語訳用例に基づく編集表記（公的指定や発音録音の認定ではありません）' if choice.get('editorial_usage_kind')=='translated_reportage' else '地区自治体の日本語使用例を同形集落名に対応させた編集表記（範囲の同一性や公的指定の認定ではありません）' if choice.get('editorial_usage_kind')=='district_policy_report' else '著者と対象州を確認した現地調査論文の日本語使用例に基づく編集表記（公的指定や発音録音の認定ではありません）' if choice.get('editorial_usage_kind')=='academic_publication' else '町名を由来とする社名の日本語業界使用例を対応させた編集表記（町の公的指定や発音録音の認定ではありません）' if choice.get('editorial_usage_kind')=='company_place_origin' else '発行主体を確認した農業産地報告の日本語使用例に基づく編集表記（公的指定や発音録音の認定ではありません）' if choice.get('editorial_usage_kind')=='agricultural_publication' else '発表者を確認した公開講演資料の日本語使用例に基づく編集表記（公的指定や発音録音の認定ではありません）' if choice.get('editorial_usage_kind')=='business_presentation' else '著者と対象州を確認した居住記の日本語使用例に基づく編集表記（公的指定や発音録音の認定ではありません）' if choice.get('editorial_usage_kind')=='resident_article' else '出演団体の公式公演記録にある日本語地名用例に基づく編集表記（公的指定や発音録音の認定ではありません）' if choice.get('editorial_usage_kind')=='performance_record' else '対象州と施設の対応を確認した論文の施設名用例を所在地名に対応させた編集表記（町の公的指定や発音録音認定ではありません）' if choice.get('editorial_usage_kind')=='academic_related_place' else '著者を確認した日本語実訪記の使用例に基づく編集表記（公的指定や発音録音の認定ではありません）' if choice.get('editorial_usage_url') else '公的資料の日本語表記' if choice.get('japanese_source_url') else '公的・地域資料の現地発音からCodexで作成した編集音写（公式日本語名の登録ではありません）' if choice.get('pronunciation_source_url') else 'Qwen候補をCodexで確認・修正した編集音写（公式日本語名の登録ではありません）' if choice.get('model') else 'Codexによる編集音写（公式日本語名の登録ではありません）' if choice.get('ja_editorial') else '登録日本語別名'
        if choice.get('pronunciation_source_url') or choice.get('japanese_source_url') or choice.get('registered_source_url'):
            name_basis+='。表記確認：'+choice.get('pronunciation_review_note',choice.get('review_note',''))
        if choice.get('reading_status') == 'inferred':
            if '推定' not in name:
                raise ValueError('Inferred reading must be visibly labeled')
            name_basis='ユーザー了承の方針による推定の編集音写。現地の読みや公式日本語名の確認済み表記ではありません。'+choice.get('review_note','')
        evidence_label='地名欄・住所本文（国勢調査局の統計地区境界への包含を確認）' if choice.get('policy')=='reviewed_census_place_boundary' else '地名欄・住所本文（大学調査範囲図と州の地名座標を個別確認）' if choice.get('policy')=='reviewed_public_cartographic_area' else '地名欄・住所本文（公的資料の街路座標と地図を個別確認）' if choice.get('policy')=='reviewed_public_cartographic_point' else '地名欄・住所本文（独立2施設の公式住所または公式位置を個別確認）' if choice.get('policy')=='reviewed_address_text_anchors' else '施設名・住所本文' if choice.get('policy')=='facility_text_review' else '住所地名'
        basis=f"周辺750mのPOI {p['near_pois']}件中{c['supporting_pois']}件の{evidence_label}が参照ID GeoNames:{c['id']}に対応（原参照名：{c['name']}）。一致率{c['support_share']*100:.1f}%、峰から参照点まで{c['distance_m']}m。{name_basis}を使用。行政境界への包含や全POIの位置精度を確定した意味ではありません。"
        entry={'name':name,'source':'Foursquare OS Places / Apache 2.0 + GeoNames / CC BY 4.0','source_id':'GeoNames:'+c['id'],'source_name':c['name'],'source_url':c['source_url'],'reference_distance_m':c['distance_m'],'coordinates':p['coordinates'],'registered_source_url':choice.get('registered_source_url'),'japanese_source_url':choice.get('japanese_source_url'),'editorial_usage_url':choice.get('editorial_usage_url'),'editorial_usage_kind':choice.get('editorial_usage_kind'),'pronunciation_source_url':choice.get('pronunciation_source_url'),'candidate_model':choice.get('model'),'reviewed_by':choice.get('reviewed_by'),'basis':basis,'status':'reviewed_address_official_japanese' if choice.get('japanese_source_url') else 'reviewed_address_editorial_transliteration' if choice.get('ja_editorial') else 'reviewed_address_reference'}
        if choice.get('reading_status') == 'inferred':
            entry.update(reading_status='inferred', status='reviewed_address_inferred_reading')
        entries[p['peak']]=entry
        decisions.append({'peak':p['peak'],'coordinates':p['coordinates'],'density':p['density'],'name':name,'candidate_model':choice.get('model'),'model_ja':choice.get('model_ja'),'reviewed_by':choice.get('reviewed_by'),'batch':choice.get('batch',1),'name_type':'official_japanese' if choice.get('japanese_source_url') else 'editorial_transliteration' if choice.get('ja_editorial') else 'registered_japanese','pronunciation_source_url':choice.get('pronunciation_source_url'),'japanese_source_url':choice.get('japanese_source_url'),'editorial_usage_url':choice.get('editorial_usage_url'),'editorial_usage_kind':choice.get('editorial_usage_kind'),'review_note':choice.get('review_note'),'reference':c,'near_pois':p['near_pois'],'distinct_coordinates':p['distinct_coordinates'],'with_address':p['with_address'],'locality_counts':p['locality_counts'],'sample_ids':[r['fsq_place_id'] for r in p['samples']],'basis':basis})
    # Guard the rounded text keys against collisions or changes in actual data.
    seen={};present=set();manifest=read(WORLD_ROOT/'manifest.json')
    for package in manifest['packages']:
        for f in read(WORLD_ROOT/package['id']/'200-all-peaks.json')['features']:
            key=f['properties']['name']
            if key in by_peak:
                if f['geometry']['coordinates'] != by_peak[key]['coordinates']:
                    raise ValueError('Original cohort coordinate key changed or collided')
                if key in present:raise ValueError('Original cohort peak occurs in multiple packages')
                present.add(key)
            if key not in entries:continue
            if f['properties']['name_source']!='coordinates' or f['geometry']['coordinates']!=entries[key]['coordinates']:raise ValueError('Coordinate key changed or collided')
            seen[key]=seen.get(key,0)+1
    if len(seen)!=len(entries) or any(n!=1 for n in seen.values()):raise ValueError('Peak coverage differs')
    counts=cohort_counts(by_peak,present,entries)
    Path('web/unnamed-world-peak-names.js').write_text('Object.assign(window.NIGIWAI_COORDINATE_NAMES,'+json.dumps(entries,ensure_ascii=False,separators=(',',':'))+');\n',encoding='utf-8')
    Path('docs/unnamed-world-name-decisions.json').write_text(json.dumps({'snapshot':report['snapshot'],'batch':max(p.get('batch',1) for p in shortlist),**counts,'selected_world_root':WORLD_ROOT.as_posix(),'policy':'Reviewed source Japanese aliases plus address consensus, geographic point comparison, multiple distinct POI coordinates; reference labels only','items':decisions},ensure_ascii=False,indent=2),encoding='utf-8')
    meta=read(ROOT/'audit-progress.json');meta['names_published']=len(entries);meta['unnamed_remaining']=counts['remaining'];meta['selected_release_cohort']=counts;meta['selected_world_root']=WORLD_ROOT.as_posix()
    (ROOT/'audit-progress.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    print('Published reference names:',len(entries),'Remaining:',counts['remaining'],'Absent from selected release:',counts['absent_from_selected_release'])

if __name__=='__main__':main()
