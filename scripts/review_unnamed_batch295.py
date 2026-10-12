"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {}

RESEARCHED_HOLDS = {'5896578': ('集中8件に含む原461d215419df4e254c9ea65aPineRidgeBibleCamp住所S0MBeauval、座標-107.61071609545635,55.14440923320611を公式運営者と個別照合。公式directions34行はCunningsLakeSK沿いHwy965、About44行はtownofBeauval近隣、公式NewsはPOBox160Beauval郵送先と区別。政府GeoNames検索結果HAFDA lake代表点55.1167542,-107.8340283は元座標の約14.5km西南西。湖代表点はキャンプ正確位置ではないため誤差距離の断定や座標置換はしないが、市街座標の根拠に郵送地域を使えないと確認。残る集中施設は未認定。学区公式Beauval頁でValleyViewSchoolの町対応を確認するが道路住所は掲載せず地点保証にはしない。NCTR本文260-264行学校BeauvalSK1897-1995確認、学校名は町現地読み・日本語指定の証明とはしない。現在日本語名と密度変更なし。次は集中13施設の運営者実所在地、キャンプ正確位置と学術PDF本文を照合。', ['https://www.pineridgebiblecamp.ca/directions', 'https://www.pineridgebiblecamp.ca/', 'https://www.pineridgebiblecamp.ca/news', 'https://geogratis.gc.ca/services/geoname/en/geonames.html?skip=63600&sort-field=name', 'https://www.nlsd113.ca/apps/pages/index.jsp?pREC_ID=1358306&type=d&uREC_ID=1067796', 'https://nctr.ca/residential-schools/saskatchewan/beauval-ile-a-la-crosse/'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch294-review.json')
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
        item['address_rechecked_batch']=295
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=295)
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
                ja_editorial=ja, batch=295, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=25, previous_holds_before=10,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==295} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch295-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='自治体・施設運営者住所と元POIを照合。対象町の日本語学術・旅行用例を参考に編集表記を採用、公開検索本文と直接取得を区別。',items=rows))
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
