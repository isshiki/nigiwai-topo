"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'5922169': ('チャーチポイント', 'https://www.jstage.jst.go.jp/article/jags/13/3/13_161/_pdf', 'Church Point CA GeoNames5922169峰44.332,-66.118支持64/75=.853住所18独立座標56参照744m。元POI4dd025de7d8b975f18f8ecb5 St.Anne University Pool1695 Route1座標44.331715,-66.118545と大学公式Centre sportif1695 route1 Pointe-de-l’Église NSを対応確認 https://www.usainteanne.ca/contact/centre-sportif 。大学英語LobsterQualityCentre公式 https://www.usainteanne.ca/en/research/units/lqc 本文1695Highway1 ChurchPoint NovaScotiaはフランス語所在地との対応確認用であり別独立施設を装う根拠ではない。元大学POI1649Highway1は現住所1695と不一致で採用根拠にしない。私室・教室・研究室などの大学内細分POI多数を独立した地域施設の証拠として数え直さず、登録密度の限界として記録。日本語は大石太郎2020地理空間13(3)161-177カナダ沿海諸州におけるアカディアンの文化遺産を活用した地域活性化 https://www.jstage.jst.go.jp/article/jags/13/3/13_161/_pdf PDF15頁印刷175頁注9を画像とPDFium本文で直接確認。ノヴァスコシア州南西部チャーチポイント（ポワントゥ・ドゥ・レグリーズ）にサンタンヌ大学と記し同地特定できる。JSTAGE本文のpypdf文字化けはPDFiumとページ画像で確認し解消。研究者日本語用例を編集表記として採用、正式指定や発音録音ではない。原座標密度不変。')}
RESEARCHED_HOLDS = {}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch97-review.json')
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
        item['address_rechecked_batch']=98
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=98)
            continue
        item.pop('next_research_lead', None)
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='japanese_academic_publication', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=98, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                editorial_usage_url=url, editorial_usage_kind='academic_publication', review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=124, previous_holds_before=42,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==98} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch98-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='Church Pointの大学施設住所と地理学論文の日本語用例を照合して反映。',items=rows))
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
