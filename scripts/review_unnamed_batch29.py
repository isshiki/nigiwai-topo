"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'11748824': ('キラーニー', 'https://dictionary.cambridge.org/pronunciation/english/killarney', 'Cambridgeの英語発音/kɪˈlɑːr.ni/を編集音写。https://en.wiktionary.org/wiki/KillarneyにSudbury District Ontarioの自治体語義があり、自治体公式https://www.municipalityofkillarney.ca/business-directory/food-dining/herbert-fisheriesのHerbert Fisheries、21 Channel Streetが原POIの施設名・住所主要部分・ONと一致。原POI住所に混在する1942 Regent Stはこの自治体掲載の所在地ではない。45/52件支持、参照193m。カナダ現地録音や公式日本語名と主張せず、辞書発音に基づく編集表記。')}
RESEARCHED_HOLDS = {'4263238': ('辞書でClay County Indianaの町語義と米英発音を確認。First Financial銀行2011年報の検索結果に8490 East State Road 42があるが、本文取得は410エラー。個別住所の一次資料確認を継続し今回は保留。', ['https://en.wiktionary.org/wiki/Poland', 'https://www.annualreports.com/HostedData/AnnualReportArchive/f/NASDAQ_THFF_2011.pdf']), '6173889': ('Verona辞書にOntarioの当該町語義を確認できず、イタリア等の同名地の発音を対象町の現地読みとして確定しない。住所条件は再検証。', ['https://en.wiktionary.org/wiki/Verona'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch28-review.json')
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
        item['address_rechecked_batch']=29
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=29)
            continue
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='pronunciation', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=29, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=164, previous_holds_before=60,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==29} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch29-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='未反映224件の住所条件を再検証。Killarneyの施設名と住所を自治体掲載に照合し辞書発音の編集音写を追加。PolandとVeronaは一次住所資料または当該町発音の追加確認を継続。',items=rows))
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
