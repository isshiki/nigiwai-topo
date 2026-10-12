"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'5729916': ('ハーフウェイ', 'https://en.wiktionary.org/wiki/halfway', '英語辞書のUS発音/ˌhæfˈweɪ/に基づく編集音写。大文字地名項目https://en.wiktionary.org/wiki/HalfwayにBaker County Oregonの町語義を確認。施設公式https://www.halfwaymotelrvpark.com/motelのHalfway Motel、170 South Main Street、Halfway ORが原POIと一致。45/45件支持、参照635m。一般語の発音を使用した編集表記であり町の現地録音の検証済みとは主張しない。')}
RESEARCHED_HOLDS = {'4277796': ('銀行公式https://www.bankofprotection.com/locationsの本店302 N. Broadway、Protection KSが原POIと完全一致。27/27件支持。一般語protectionの資料とは別に町名の現地読みの確認を継続。今回は住所の一次資料確認まで完了し保留。', ['https://www.bankofprotection.com/locations', 'https://en.wiktionary.org/wiki/protection']), '5021600': ('大文字地名辞書にPolk County Minnesotaの町語義、小文字辞書に/ˈklaɪ.mæks/を確認。105 W Broadwayの検索資料は非公式案内のため個別住所の一次資料と現地読みの照合を継続。', ['https://en.wiktionary.org/wiki/Climax', 'https://en.wiktionary.org/wiki/climax'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch29-review.json')
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
        item['address_rechecked_batch']=30
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=30)
            continue
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='pronunciation', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=30, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=163, previous_holds_before=60,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==30} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch30-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='未反映223件の住所条件を再検証。Halfwayの施設公式住所を照合し一般英語辞書発音の編集音写を追加。Protectionは銀行公式住所の一致を確認、Climaxは町語義を確認し追加調査を継続。',items=rows))
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
