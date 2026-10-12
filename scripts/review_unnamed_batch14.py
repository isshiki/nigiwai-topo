"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'3038537': ('エニェ・ル・デュック', 'https://christaldesaintmarc.com/un-village-chatillonnais-et-ses-ecarts-aignay-le-duc-a214930503', 'Gérard Heinzéの郷土調査（Alphonse Roserotの1924年の研究に基づく、2023年公開）の個別項目の現地読みAin-gnéを確認。Wiktionnaireのɛ.ɲɛ.lə.dykとも整合。元POI25/26件のAignay le Duc表記、Côte-d’Or、place du Colonel Monod・rue Nicolas Frochot・place de la Mairieと参照位置81mを照合。エニェ・ル・デュックは編集音写で公式日本語名ではない。'), '2154355': ('オメオ', 'https://flighttraveller.com/2016/04/30/post-1040/', '2016年の日本語による現地旅行記がGreat Alpine RoadのCobungraからOmeoへ実際に訪問した町をオメオと表記。Expedia日本語のOmeo旅行案内の159 Day Ave Omeo VICとも照合。元POIのOmeo Information CentreのDay Ave、VIC、住所地名支持44/49件、参照位置572mと対応する。人名・商品名から推測せず、町を対象にした訪問者の日本語表記を採用。公式日本語名・現地音声確認済みとは扱わない。')}
RESEARCHED_HOLDS = {'6051792': ('町公式史・州政府資料でAlbertaのLegalの同定は補強できたが、町固有の発音は個人SNS・匿名投稿が中心。公式史の語源だけでは読みを確定せず保留。', ['https://www.legal.ca/experience/local-tourism/history', 'https://www.alberta.ca/francophone-heritage']), '5901898': ('Manitoba政府の地名辞典でBirtleの位置と由来を確認。英国の同名地・姓・乳児名の発音資料を町に転用しない。対象町の読みの個別確認は未完了。', ['https://www.manitoba.ca/nrnd/forest/pubs/forest_lands/cdgnm.pdf']), '2984257': ('検索で音韻表記が複数見つかったが末尾のjの有無などが異なり、現地の個別資料による裏付け不足。住所条件は充足するが保留。', ['https://www.dico-rimes.com/dico-rime/152413/recey_sur_ource.php'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch13-review.json')
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
        item['address_rechecked_batch']=14
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=14)
            continue
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='pronunciation', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=14, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=198, previous_holds_before=66,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==14} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch14-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='未反映264件の住所条件を再検証。郷土地名調査と日本語の現地訪問記録により2峰の編集表記を採用。3地名は個別資料不足で保留。残りの読みの調査は未完了。',items=rows))
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
