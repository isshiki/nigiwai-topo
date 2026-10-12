"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'6170584': ('タートルフォード', 'https://rcmp.ca/en/saskatchewan/detachments', 'Turtleford CA SK GeoNames6170584峰53.389,-108.962支持67/77=.87住所56独立座標43参照931m。元e758938e93874e96630fe678 RoyalCanadianMountedPolice505MainStを警察運営公式 https://rcmp.ca/en/saskatchewan/detachments TurtlefordDetachment所在地505MainStreet Turtleford Saskatchewanに直接照合。郵送POBox190を所在地にしない。Regina大学 https://esask.uregina.ca/entry/turtleford.html はTurtlelakeRiverの渡渉地と郵便局長JohnBloomによる命名を説明。 https://www.merriam-webster.com/dictionary/turtle https://www.merriam-webster.com/dictionary/ford の一般語発音からタートルフォードと編集音写。現地録音や公式日本語名の直接確認ではない。WDM博物館2023PDFは検索索引だけで直接取得に失敗したため採用根拠には含めない。位置密度不変。')}
RESEARCHED_HOLDS = {'6060139': ('元LakelandAgencies418MainStを村公式 https://villageofloonlake.ca/local-businesses/ の同名同住所に直接照合。一般語loon/lake辞書発音は確認したが当地の読みや命名由来は未確認。他州や米国LoonLakeの由来を転用しない。', ['https://villageofloonlake.ca/local-businesses/', 'https://www.merriam-webster.com/dictionary/loon', 'https://www.merriam-webster.com/dictionary/lake'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch166-review.json')
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
        item['address_rechecked_batch']=167
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=167)
            continue
        item.pop('next_research_lead', None)
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='etymology_informed_editorial', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=167, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=102, previous_holds_before=36,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==167} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch167-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='Turtlefordの警察所在地を運営者公式に照合。大学地名説明と辞書発音に基づく編集表記。',items=rows))
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
