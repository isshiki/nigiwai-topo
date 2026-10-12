"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'5968619': ('ガイスバラ', 'https://www.works-i.com/research/labour/item/four-day_workweek2022.pdf', 'Guysborough CA GeoNames5968619峰45.384,-61.504支持25/29=.862住所25独立座標26参照453m。原NSLC69b59bda80dbfd541cf73f55住所10018Hwy16をNSLC州調達公開RFP SR-26-FY23 https://procurement.novascotia.ca/pt_files/tenders/SR-26-FY23.pdf PDF21頁店2317Guysborough10018Highway16に直接一致確認。元Robin3aefa888efa3277221ff231eおよびCooks857454364f594c5132f4f06f住所10016Highway16を地域観光協会 https://visitguysborough.ca/cooks-gas-bar-robins/ 本文village of Guysboroughと一致確認。同住所店舗は独立2証拠とは数えない。元Courthouse106ChurchStが同座標にあることは位置根拠にしない。リクルートワークス研究所2022週休3日で働く https://www.works-i.com/research/labour/item/four-day_workweek2022.pdf PDF19頁印刷18頁をPDFiumと画像で直接確認、索引ガイズバラと異なり本文はガイスバラ。同資料の自治体2020年6月9か月試行をMODG公式2020秋ニュースレター https://modg.ca/sites/default/files/pdfs/Autumn%202020_0.pdf の同試行記載と対応。自治体名の日本語用例を同形の地区内集落名の編集表記ガイスバラに採用、自治体全体と集落の範囲は同一としない。英国Guisboroughは別地。モデルギーズボロを修正、正式日本語指定や発音実聴ではない。原座標密度不変。')}
RESEARCHED_HOLDS = {}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch98-review.json')
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
        item['address_rechecked_batch']=99
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=99)
            continue
        item.pop('next_research_lead', None)
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='japanese_academic_publication', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=99, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                editorial_usage_url=url, editorial_usage_kind='district_policy_report', review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=123, previous_holds_before=42,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==99} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch99-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='Guysboroughの公式店舗住所と地区自治体の日本語使用例を照合して反映。',items=rows))
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
