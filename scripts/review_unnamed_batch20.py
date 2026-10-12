"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'5908499': ('ブレトン', 'https://en.wiktionary.org/wiki/Breton', '英語発音/ˈbɹɛtən/とAlbertaの村語義を確認。村公式https://www.breton.ca/の4916 50 Ave Breton Albertaと原POIのAB、5004/5012 50 Ave等、46/48件支持、参照798mを照合。フランス語の同綴りからの転写ではなく英語辞書発音に基づく編集音写。現地音声確認済みではない。'), '5905878': ('ボーデン', 'https://en.wiktionary.org/wiki/Borden', '辞書発音/ˈbɔɹ.dən/とGreat Bend No.405 Saskatchewanの村語義を確認。州保健局公式https://www.saskhealthauthority.ca/facilities-locations/borden-primary-health-centreの308 Shepard Street Borden SKが原POIのBorden Primary Health Centreと一致。27/29件支持、参照730m。辞書発音に基づく編集音写であり現地音声確認済みではない。'), '6092581': ('オデッサ', 'https://en.wiktionary.org/wiki/Odessa', '英語発音/oʊˈdɛsə/とFrancis No.127 Saskatchewanの村語義を確認。村公式https://odessa.ca/community-center/の406 1st Avenueの施設にVillage Officeがあることが原POIのVillage of Odessa住所と一致。17/19件支持、参照40m。ウクライナの同名都市ではない。辞書発音に基づく編集音写。'), '5065502': ('チェンバーズ', 'https://en.wiktionary.org/wiki/Chambers', '米国発音/ˈt͡ʃeɪmbɚz/とHolt County Nebraskaの村語義を確認。銀行公式https://chambersbank.com/services/の104 E. Main Street Chambers NE 68725が原POIのChambers State Bankと一致。26/26件支持、参照93m。辞書発音に基づく編集音写であり現地音声確認済みではない。')}
RESEARCHED_HOLDS = {}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch19-review.json')
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
        item['address_rechecked_batch']=20
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=20)
            continue
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='pronunciation', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=20, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=186, previous_holds_before=63,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==20} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch20-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='未反映249件の住所条件を再検証。発音辞書に対象の町を明示した4峰について、公的・施設公式住所と照合して編集音写を採用。未確定の読みは保留して調査継続。',items=rows))
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
