"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'5975472': ('ハインズクリーク', 'https://github.com/scriptin/jmdict-simplified/releases/tag/3.6.2%2B20261005200550', 'Hines Creek CA GeoNames5975472、支持26/29、住所26、独立座標24、参照距離411m。元POI69b58e9f80dbfd541ce2403d Hines Creek Municipal Library 212 10 Stを図書館公式 https://www.hinescreeklibrary.ab.ca/About-Us と自治体 https://hinescreek.com/business-directory/ の212 10 Street Hines Creek AB T0H2A0に照合。JMnedict2026-10-05 entry5060967 kanaハインズクリーク、translationHines Creek、typeplaceを確認。辞書は国座標を含まずAlaska同名河川との区別を証明しない。所在地は独立した元住所と自治体で確定し、辞書の同綴り地名表記を対象町へ適用する編集判断を明記。FamilySearch日本語ページは本文取得不可、検索断片は採用根拠に数えない。自動翻訳百科事典も採用根拠にしない。法的指定や現地録音での発音確定ではない。位置密度不変。辞書抽出はCCBYSA4.0で別途配布。')}
RESEARCHED_HOLDS = {'6164443': ('村公式 https://www.villageoftheodore.net/page8 にSt.Theodore School105 Main St,Theodore SK S0A4C0を確認。原POI69b5956a80dbfd541cec1bdfは同名同住所だがlocalityがInvermayなので自治体表記と不一致を記録。JMnedictシオドア/Theodore/placeは国座標なし、同名の豪州・米国や人名の読みと対象SK町の対応は未確認。原施設住所一致だけで読みを確定せず保留。', ['https://www.villageoftheodore.net/page8']), '5948012': ('JMnedictエルムクリーク/Elm Creek/placeは国座標なし。検索で確認した英辞郎Elm Creekは米国と明記されCA町の証明にしない。原Ma’s Drive-In128Pth2に対し運営予約TouchBistro現住所58Manitoba13なので完全一致と主張しない。移転・道路番号・店舗同一性確認または別施設の公式住所が必要。', ['https://order.tbdine.com/pickup/39856/menu']), '2069974': ('運行会社GenesisTransport2022年時刻表にHawkerGeneralStore16WilpenaRd、Hawkerを確認、原POI4bb9229498c7ef3b20d63102同住所。現営業状態は2022年資料では認定しない。JMnedictホーカー/Hawker/placeは国座標を含まず、SA町とACT同名地区の表記対応はまだ確認していない。日本語ホーカー検索はSingapore屋台が多く転用しない。', ['https://genesistransport.com.au/wp-content/uploads/Fleurieu-to-Flinders-Timetable-2022.pdf'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch70-review.json')
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
        item['address_rechecked_batch']=71
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=71)
            continue
        item.pop('next_research_lead', None)
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='public_japanese', reason=note,
            japanese_label_type='public_japanese')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=71, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                japanese_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=139, previous_holds_before=45,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==71} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch71-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='Hines Creekの図書館・自治体住所を照合し辞書表記の適用判断を明記して候補1峰を反映。',items=rows))
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
