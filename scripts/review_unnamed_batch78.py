"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'5910127': ('ブルース・マインス', 'https://ameblo.jp/kfumi/entry-12476085011.html', 'Bruce Mines ON CA GeoNames5910127、峰46.300,-83.792、支持41/47=.872、住所39、独立座標38、距離627m。元POI5d23b97bbe636e0023b1bc3f Red House Ice Cream9172 17Hwyを地域観光媒体Northern Ontario Travel記事 https://northernontario.travel/algoma-country/red-house-ice-cream-bruce-mines 本文9172 Hwy17 Bruce Mines ONと照合。歩き人ふみの実訪記 https://ameblo.jp/kfumi/entry-12476085011.html はカナダオンタリオ州、スーセントマリーから東行の旅でブルース マインスという町と英語Bruce Minesを併記。実訪日本語用例のマインスを保持し空白を中点に整える編集表記ブルース・マインスを採用。モデルのマインズに自動修正しない。法定日本語名や現地音声認定ではない。観光記事の住所は資料時点の対応で現在営業保証ではない。元参照ID・座標・密度不変。')}
RESEARCHED_HOLDS = {'5888569': ('Avonlea SKのCo-op Ag原住所300 McRorie AvenueをCanadian Cattle Identification Agency 2025-12-29販売店一覧PDF13頁300 MCRORIE AVE AVONLEA SKと直接照合。同住所のHome重複を独立根拠に数えない。JMnedictアボンリー/アヴォンリーは国・座標なくPEIの架空村と混同できるため読みは未確定。次はSK村を明示した地域音声または日本語用例。', ['https://www.canadaid.ca/wp-content/uploads/2026/01/DEALER-Monthly-Lists-as-of-Dec-29-2025.pdf']), '5962520': ('Gogama ON原POI Desjardins Credit Union41 Poupore Stを銀行公式2022年8月版PDF2頁Gogama(J.R.Corner Store)41 Poupore Street Gogama ON P0M1W0に直接照合。地域サイトの同店住所も一致。併設銀行と店を独立住所根拠として二重計上しない。歴史的住所対応で現在営業保証ではない。日本語モデルゴガマの読みは未確定、現地資料または実訪日本語用例を継続調査。', ['https://www.desjardins.com/ressources/pdf/f05-o00107-carte-centre-services-adresses-e.pdf?resVer=1619188464000', 'https://gogama.ca/jrcorner2.html'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch77-review.json')
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
        item['address_rechecked_batch']=78
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=78)
            continue
        item.pop('next_research_lead', None)
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='editorial_japanese_usage', reason=note,
            japanese_label_type='editorial_japanese_usage')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=78, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                editorial_usage_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=134, previous_holds_before=45,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==78} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch78-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='カナダ3候補の住所・読みを照合し実訪日本語用例のある1峰を反映。',items=rows))
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
