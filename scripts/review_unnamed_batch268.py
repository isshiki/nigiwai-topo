"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'6074404': ('ミルバートン', 'https://autoreserve.com/ja/ca/ontario/milverton', 'CA ON原Gerbers Workwear15MainStNを会社自身のLinkedIn公開検索全文の店舗住所15MainStreetN MilvertonON N0K1M0と照合。直接LinkedIn取得Cachemiss、現公式Contact掲載はDonegal/Wingham/Strathroyのみで現営業は断定しない。公開会社プロフィールによる旧住所対応として記録、第三者AllbizはSilvertonBC誤分類あり根拠に使わない。支持105/121、住所111、独立座標101、参照429m。AutoReserve対象国州町ページのミルバートン（オンタリオ州）、6MainSt MilvertonON N0K1M0の用例を参考に編集表記採用。直接取得Cachemiss。モデルミルバーンのverton脱落不採用、公的日本語指定・現地録音の証明ではない。密度・位置不変。')}

RESEARCHED_HOLDS = {'6127700': ('AutoReserve ON対象町とAirbnbにローズニース用例を確認。EPA公的2010一覧は元KaHeatRR4に対してRR4 670PackerRoad Roseneathを直接確認。Langs観光案内はRR3と一致するがMarinas公開座標44.240833,-78.071667は元44.192852,-78.057812から約5.4km。元住所parquetで異なるRR施設7件が完全同一座標44.192852483915296,-78.05781199969996、さらに別6件が44.19290555655383,-78.05786619001336に一致。郵便地名対応だけで中心施設の位置品質を確定しない。町中心学校9047CR45やFairGround9109CR45を次に公的照合して地形由来の確認を継続。', ['https://autoreserve.com/ja/ca/ontario/roseneath', 'https://nepis.epa.gov/Exe/ZyPURL.cgi?Dockey=P1010DN1.TXT', 'https://www.ricelakecanada.com/langs_resort.htm', 'https://marinas.com/view/marina/ywcrv6_Langs_Family_Resort_Fishing_and_Marina_Roseneath_ON_Canada'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch267-review.json')
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
        item['address_rechecked_batch']=268
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=268)
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
                ja_editorial=ja, batch=268, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=38, previous_holds_before=18,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==268} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch268-review.json', dict(snapshot=report['snapshot'], summary=summary,
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
