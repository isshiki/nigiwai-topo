"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'6945981': ('ラック・エトゥシュマン', 'https://jp.trip.com/hotels/lac-etchemin-hotel-detail-10534950/auberge-les-etchemins/', '原Banque Nationale2222eAvenueを銀行公式支店一覧本文と自治体公開検索本文の同支店同住所に照合。支持107/110、住所106、独立座標80、参照211m。三サンプル銀行とATMは同一施設として扱う。Trip.com対象町ホテル1831Route277 G0R1S0のラック＝エトゥシュマン、Tripadvisor同町レストランの同表記、Airbnb同町宿泊のラック・エトゥシュマンを公開検索本文で確認。区切り中黒の編集表記ラック・エトゥシュマン採用。別用例ラック・エチェミンとの表記差あり、公的指定・現地録音の確認とは区別。Trip.com直接取得InternalError。モデルラ・シェミン不採用。密度・位置不変。'), '8593673': ('サン・ポール・ド・モンミニ', 'https://www.traveloka.com/ja-jp/hotel/canada/area/lac-etchemin-4008673929/best-hotels-in-lac-etchemin', '原Caisses Desjardins3054eAveを運営者公式Saint-Paul-de-Montminy支店3054eAvenue G0R3Y0公開検索全文と運営者事業継続PDF同住所に照合。支持20/22、住所20、独立座標18、参照184m。Traveloka近隣都市一覧のサンポール・ド・モンミニを公開検索本文で確認。中黒を整えた編集表記サン・ポール・ド・モンミニ採用。公式日本語指定や現地録音の証明ではない。日本語旅行ページ直接取得InternalError。原ABCの住所309Aは自治体309と同番地でも同施設の証明に使わない。密度・位置不変。')}

RESEARCHED_HOLDS = {'10292222': ('Airbnb日本語対象町ページでサン・ジュスト・ド・ブレトニエールの用例を確認。原LHeureux Daniel367route204はPagesJaunesで同名同住所を照合できるが運営者・自治体・登録資料による一次住所確認は未完了。原教会住所の複雑な番地表記も未確定で保留。人名日本語ブルトニエールを町に無条件転用しない。', ['https://www.airbnb.jp/saint-just-de-bretenieres-canada/stays/monthly', 'https://www.pagesjaunes.ca/bus/Quebec/Saint-Just-de-Bretenieres/L-Heureux-Daniel-Inc/7332053.html'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch265-review.json')
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
        item['address_rechecked_batch']=266
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=266)
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
                ja_editorial=ja, batch=266, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=38, previous_holds_before=21,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==266} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch266-review.json', dict(snapshot=report['snapshot'], summary=summary,
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
