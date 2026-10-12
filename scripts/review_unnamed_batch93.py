"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'6074485': ('ミンデモヤ', 'https://www.destinationontario.com/ja-jp/travel-resources/family-road-trip-northeastern-ontario', 'Mindemoya CA GeoNames6074485峰45.733,-82.167支持76/86=.884住所80独立座標68参照105m。元POI a97e8d36e7fb4c92a7eabd13 BMO Bank of Montreal 6103 542 Hwy 座標45.732081,-82.166238を銀行公式 https://branches.bmo.com/on/mindemoya/b2373/ 本文6103 HWY#542 KING ST Mindemoya ONに照合。元POI5bb335a76539427d9415f505 Welcome Centre2207 551 Hwy座標45.734086,-82.167527を自治体公式 https://www.centralmanitoulin.ca/recreation-culture/visiting-central-manitoulin/welcome-centre/ 本文2207 Hwy551 Mindemoya ONに照合。Destination Ontario日本語 https://www.destinationontario.com/ja-jp/travel-resources/family-road-trip-northeastern-ontario 本文の施設所在地524ケチャンクーケムトレイル、ミンデモヤを直接確認。湖名だけから転用せず住所の地域欄の日本語用例を採用。公的観光ページの日本語表記であり村の正式日本語指定や発音実聴の認定ではない。原位置密度不変。')}
RESEARCHED_HOLDS = {}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch92-review.json')
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
        item['address_rechecked_batch']=87
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=93)
            continue
        item.pop('next_research_lead', None)
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='japanese_public_report', reason=note,
            japanese_label_type='published_japanese')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=93, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                japanese_source_url=url, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=126, previous_holds_before=45,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==93} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch93-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='Mindemoyaの公的日本語所在地表記と銀行・自治体の元POI住所を照合して反映。',items=rows))
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
