"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'5226988': ('コローム', 'https://books.google.com/books?id=KIhCHhlw8QoC&pg=PP11', "SouthDakota町名発音資料What'sThatName?1949編DonaldD.Burchard/OrrinMeltonのGoogleBooks公開SearchWithinVolume2応答を直接取得しpage_idPP11の対象Colome(kuh-LOHM)を確認。これに基づきコロームを編集音写。書誌本文を直接確認、ページ画像全体や録音は未確認、現在の話者実聴・公式日本語指定ではない。従来RoadsideThoughtsKAH-lohmは自己近似注意付きでアクセントが異なるため今回の根拠にしない。原28ec18d6501d4d77993c3799ColomeHighSchool01 105WCarrStと州教育局の同名校PhysicalAddress105CarrStColomeSD57528を再照合。番地道路町州は対応するが原W方向は公式未記載、完全文字一致とはしない。原学校DistrictとSchoolを独立3施設に数えない。住所支持29/30、25住所、25座標、参照50mの条件を再確認、原峰位置と密度は不変。")}

RESEARCHED_HOLDS = {'6085350': ('従来EagleViewLodge480249Ave運営者一致を保持。町公式2025-09-16候補者資料PDFを直接取得し第3頁にмирнам(mirnam)由来を確認。CommunityStoriesのPeterKrawchuk1980記事も同町由来を直接確認。由来句のローマ字表記を現在の町名IPAと混同しない。読み確定は保留。', ['https://www.myrnam.ca/wp-content/uploads/PROSPECTIVE-CANDIDATES-PACKAGE-Updated-2025-09-16.pdf', 'https://www.communitystories.ca/v1/pm_v2.php?ex=00000464&fl=&id=story_line_child&lg=English&pos=1&scpos=1&sl=5522']), '4276077': ('従来Southwind住所照合根拠を保持。大学出版局1001KansasPlaceNames公式書誌は地名発音を含むと記すがNatoma個別項目は未確認。新たに1955UniversityKansasWilliamAllenWhiteSchoolJournalism刊PronunciationGuidetoKansasPlaceNamesのHathi識別子mdp.39015047651115と学会の書評を発見。Hathi直接取得403を回避せず、発音未確認。次は正規公開プレビュー又は大学公開書誌の個別項目を確認。', ['https://kansaspress.ku.edu/9780700603930/', 'https://hdl.handle.net/2027/mdp.39015047651115', 'https://ans-names.pitt.edu/ans/article/download/141/140/284'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch324-review.json')
    rows = [x for x in prior['items'] if x['decision']=='hold']
    report = read(WORK/'address-name-review.json')
    evidence = {x['peak']:x for x in report['items']}
    approvals = read('docs/unnamed-world-name-approvals.json')
    existing = {x['peak'] for x in approvals['items']}
    assert not ({p for x in rows for p in x['peak_keys']} & existing), 'Prior report resurrected adopted peaks'
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
        item['address_rechecked_batch']=325
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=325)
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
                ja_editorial=ja, batch=325, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=22, previous_holds_before=6,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==325} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch325-review.json', dict(snapshot=report['snapshot'], summary=summary,
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
