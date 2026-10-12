"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'5230920': ('ロスコー', 'https://files-backend.assets.thrillshare.com/documents/asset/uploaded_file/1834/Ecsd/a7182947-2a66-4807-a99f-f1185c0cb638/Safe_Return_to_In-Person_Learning_Plan.pdf?disposition=inline', 'Roscoe US SD GeoNames5230920峰45.449,-99.338支持23/26=.885住所21独立座標26参照62m。原9d3a4b9cc0084d76b6bdf89c EdmundsCentralHighSchool105 1ST Ave NE座標45.452443,-99.338408を学区公開計画PDFindex0表紙105 1st Avenue NE RoscoeSD57471に直接照合。学区ホームhttps://www.echs.k12.sd.us/と州教育名簿https://doe.sd.gov/ofm/school.aspx?districtnumber=22005&schoolsort=2200502も1051stAveを補確認。原自治体110NMitchellと現205NMitchell差は解消したと偽らず別施設証拠で町を確認。CMU roscoe R AA1 S K OW0による編集表記ロスコー、モデルロスコウを整理。当地実聴・公的日本語指定ではない。元位置密度不変。'), '5049441': ('スワンビル', 'https://icecastlefishhousesmfg.com/dealers.php', 'Swanville US MN GeoNames5049441峰45.915,-94.640支持38/41=.927住所36独立座標37参照615m。原51eba36977074f3bff4d6518 NilsonsHardware&RentItCenter207DegraffAve座標45.914994,-94.640381をメーカーIceCastle公式販売店一覧NilsonHardware207DegraffAve SwanvilleMN56382に直接照合。同一覧がリンクするhttps://nilsondirect.com/contact-us/の207DeGraffを補確認。現ブランドRippinBackroadsと旧Nilson名称を記録。同建物UPSとIceCastle原レコードは独立座標証拠に重複計上しない。CMU構成語swan S W AA1 Nとville V IH1 Lから編集音写スワンビル。辞書にSwanville全体の地名発音があるとは主張せず当地実聴・公的日本語指定ではない。元位置密度不変。')}
RESEARCHED_HOLDS = {'4772340': ('McKenney原21101BoydtonPlankRdに対応する州DEQ公開資料の検索候補を得たが本文通常HTTPS取得は403。制限を回避せず同番地だけで原店名との同一性を確定しない。USDA公開裁定一覧のWallaceSuperMarket同番地を次の一次資料候補として調査する。', ['https://www.deq.virginia.gov/home/showpublisheddocument/21581/638386625192370000'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch192-review.json')
    rows = [x for x in prior['items'] if x['decision']=='hold']
    report = read(WORK/'address-name-review.json')
    evidence = {x['peak']:x for x in report['items']}
    approvals = read('docs/unnamed-world-name-approvals.json')
    existing = {x['peak'] for x in approvals['items']}
    found = set()
    for item in rows:
        ident = item['id'].split(':')[1]
        for peak in item['peak_keys']:
            p = evidence[peak]
            c = p['candidates'][0]
            assert c == next(x['reference'] for x in item['evidence'] if x['peak']==peak)
            assert p['status']=='candidate_supported' and c['id']==ident
            assert c['support_share']>=.85 and c['supporting_pois']>=6 and c['distance_m']<=1000
            assert p['distinct_coordinates']>=4 and p['with_address']>=4
        item['address_rechecked_batch']=193
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=193)
            continue
        item.pop('next_research_lead', None)
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='dictionary_informed_editorial', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=193, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=82, previous_holds_before=31,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==193} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch193-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='Roscoe学区資料の別原施設とSwanvilleメーカー販売店一覧の原住所を照合。辞書編集表記と当地実聴を区別。',items=rows))
    save('docs/unnamed-world-name-approvals.json',approvals)
    queue=read(WORK/'remaining-review-queue.json')
    queue['items']=[x for x in queue['items'] if x['peak'] not in existing]
    queue['remaining']=len(queue['items'])
    queue['priority_counts']=dict(Counter(str(x['priority']) for x in queue['items']))
    assert queue['remaining']==5356-len(existing)
    save(WORK/'remaining-review-queue.json',queue)
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':
    main()
