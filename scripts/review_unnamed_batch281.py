"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'2997050': ('リュス・ラ・クロワ・オート', 'https://www.vrbo.com/915153a', '原CampinglaCondamine5dd762c30b404a3822ff8d8b lAllevaをparquet再取得。地域自然公園公式現本文44–46行840route de lAlleva,LeGrandLogis26620Lus-la-Croix-Hauteと施設・道路・町対応を再確認。元番地欠落の部分照合で840一致とはしない。Vrbo915153a公開検索タイトルはリュス ラ クロワ オート、本文はLus la Croix Haute、Grenoble70km/Gap50kmと対象ドローム町を明示。直接取得Cachemissを記録。第221回の発音ブログの話者不明・HiSoUR等の自動翻訳の弱さは未解消であり現地読みを実聴したとはしない。今回は対象町の日本語旅行用例に基づく編集表記として採用、公的日本語指定や音声確定とは区別。'), '3010343': ('ラ・シャペル・アン・ヴァルゴデマール', 'https://www.vrbo.com/ja-jp/p1631538a', '原ef3541e3164f49b0a74605df GallandSports Pont de la place、LaChapelleをparquet再取得。地域観光局公式本文10、140行GallandSports Pont la place05800LaChapelle-en-Valgaudémarと施設・地区・町対応を再確認、番地なし、de la/la差は維持。Vrbo1631538a公開検索本文はLaChapelle-en-Valgaudémar Provence-Alpes-Côte dAzurとエクラン国立公園内の村に対応しラ シャペル アン ヴァルゴデマールを掲載。Tripadvisor同村住所05800の宿泊頁でもラ・シャペル・アン・ヴァルゴデマールを確認。両サイト翻訳用例であり現地音声ではない、Vrbo直接取得Cachemiss。旧オック語谷名と村名の違いは引き続き歴史事項として保持、村を明示する日本語用例に基づく編集表記として採用。公的指定ではなくValgaudémar/Valgodemard別村を混同しない。')}

RESEARCHED_HOLDS = {}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch280-review.json')
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
        item['address_rechecked_batch']=281
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=281)
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
                ja_editorial=ja, batch=281, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=32, previous_holds_before=16,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==281} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch281-review.json', dict(snapshot=report['snapshot'], summary=summary,
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
