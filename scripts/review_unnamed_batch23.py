"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'4534577': ('クラウダー', 'https://en.wiktionary.org/wiki/Crowder', '米国発音/ˈkɹaʊdɚ/とPittsburg County Oklahomaの町語義を確認。Choctaw Nation公式決議https://www.choctawnation.com/wp-content/uploads/2022/03/cb-27-22.pdfが707 Bond Street Crowderのcommunity centerを明示し原POIと一致。19/22件支持、参照416m。モデルのクローダーを修正。辞書発音の編集音写。'), '5040349': ('オーア', 'https://en.wiktionary.org/wiki/Orr', '米国発音/ɔɹ/とSt Louis County Minnesotaの町語義を確認。市公式https://orrmn.gov/contact/の4429 Highway53 Orr MN55771と元POIのMN、周辺41/46件の町名支持、参照99mを照合。サンプル施設は住所欠損を含み市役所番地の完全一致は主張しない。辞書発音の編集音写。'), '5268050': ('プレスクアイル', 'https://en.wiktionary.org/wiki/Presque_Isle', '英語発音/pɹɛsk aɪl/とVilas County Wisconsinの町・集落語義を確認。町公式https://presqueislewi.gov/、州名簿https://mds.wi.gov/View/Clerk?ID=1751のVilas WI所在地が元POIのWIと対応。23/26件支持、参照31m。個々の番地完全一致やフランス語の音写とは扱わない。辞書発音の編集音写。')}
RESEARCHED_HOLDS = {}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch22-review.json')
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
        item['address_rechecked_batch']=23
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=23)
            continue
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='pronunciation', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=23, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=179, previous_holds_before=61,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==23} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch23-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='未反映240件の住所条件を再検証。対象の町を明示した辞書発音と行政・施設公式資料を照合した米国3峰を編集音写として採用。残りは調査継続。',items=rows))
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
