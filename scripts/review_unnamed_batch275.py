"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'5073930': ('ナイオブララ', 'https://autoreserve.com/ja/us/nebraska/niobrara', '原POIc23a76b160e34d53c9668e20住所parquet再確認。州図書館委員会ホストの図書館公式25414ParkAveSte3に直接照合、POBox15郵送先と区別。対象US NE Niobrara都市ページ公開検索本文のナイオブララと町内25412ParkAve等を確認。川の辞書や匿名発音推測を村へ転用しない。支持36/36、住所32、独立座標28、参照576m。日本語資料直接取得Cachemissと公開検索本文を区別。対象町の日本語使用例を参考にした編集表記、公的指定・当地録音確認とは区別。密度・座標不変。'), '6078998': ('モートラック', 'https://autoreserve.com/ja/restaurants/Ba8LQ1wMDkYYq8jwFhqq', '原POI67470f04f56a48a098ae8a90住所parquet再確認。教会運営団体2020-01-10物件委員会議事録PDF1頁のMortlachUnitedChurch203RoseStreetに直接照合。売却承認記録で現営業は証明しない。対象CanadaSKMortlachの施設頁公開検索本文にモートラックと17 2ndAveE MortlachSKS0H3E0を確認。ウイスキーやスコットランド地名の読みだけは根拠にしない。支持22/22、住所22、独立座標18、参照543m。日本語資料直接取得Cachemissと公開検索本文を区別。対象町の日本語使用例を参考にした編集表記、公的指定・当地録音確認とは区別。密度・座標不変。')}

RESEARCHED_HOLDS = {}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch274-review.json')
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
        item['address_rechecked_batch']=275
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=275)
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
                ja_editorial=ja, batch=275, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=34, previous_holds_before=17,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==275} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch275-review.json', dict(snapshot=report['snapshot'], summary=summary,
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
