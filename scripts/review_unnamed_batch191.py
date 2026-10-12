"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'5197579': ('リーパー', 'https://www.ftvfc.com/', 'Leeper US PA GeoNames5197579峰41.370,-79.304支持28/32=.875住所25独立座標24参照17m。原3fe02839f7464aa6862cbfb3 Farmington TWP Vol Fir6785Route36を同消防会社公式OurStation6785Rt36 LeeperPA16233に照合。州GameCommission2021/11/08 https://www.pa.gov/agencies/pgc/newsroom/northwest-region-bear-check-station-changes-location も同消防会社6785StateRoute36を記載。郵送Box122と区別。CMU leeper L IY1 P ER0に基づく編集表記リーパー、当地実聴・公式日本語指定ではない。元位置密度不変。'), '4468585': ('グランディ', 'https://www.caratoketobacco.com/about', 'Grandy US NC GeoNames4468585峰36.248,-75.888支持41/46=.891住所42独立座標37参照1000m。原691ba86fdcebcd6c1cc1885c Caratoke Tobacco6328CaratokeHwy座標36.246851,-75.887661を同店舗公式6328CaratokeHwy SuiteE GrandyNC27939に直接照合。公式のSuiteE(5という不完全な記号は転記せず基本道路住所の対応のみ確定。Compueasy同番地を独立位置証拠として重複計上しない。別原FoodLion123ForbesLoop公式https://stores.foodlion.com/nc/grandy/123-forbes-loop は同じ地名を補確認するが峰から約1.3kmで近傍代表施設として扱わない。CMU grandy G R AE1 N D IY0による編集表記グランディ、当地実聴・公式日本語指定ではない。元位置密度不変。')}
RESEARCHED_HOLDS = {'5939508': ('Dinsmore原84f114c6463d4d4daa26cda5自治体100MainStと自治体2024/12/02議事録PDFindex0印刷1頁100MainStreetを直接照合。CMU dinsmore D IY1 N S M AO0 Rとモデルディンスモアで第一母音が異なるため、カナダ地名の読みを追加確認し保留。', ['https://dinsmore.ca/Village/Minutes/2024/APPROVED-December-2-2024-Minutes.pdf']), '4992358': ('Ewen州発音ガイドを通常HTTPS再取得したが403。制限は回避しない。CMU ewen Y UW1 AH0 Nと既存州検索抜粋EYOO-inを当地音声証明として同一視せず読み保留。住所確認は維持。', ['https://www.michigan.gov/leo/bureaus-agencies/bureau-of-services-for-blind-persons/btbl/pronunciation-guide-you-say-it-how-in-michigan'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch190-review.json')
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
        item['address_rechecked_batch']=191
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=191)
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
                ja_editorial=ja, batch=191, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=87, previous_holds_before=31,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==191} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch191-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='Leeper消防署とGrandy原店舗の公式道路住所を照合。CMU編集音写と当地実聴を区別。Dinsmore母音差とEwen403を記録して保留。',items=rows))
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
