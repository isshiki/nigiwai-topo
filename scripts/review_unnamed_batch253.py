"""Publish Lismore's identity-checked registered Japanese label."""
import json
from pathlib import Path
from collections import Counter

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))

def save(p, x):
    Path(p).write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def main():
    work = Path('data/name-research/unnamed-world')
    prior = read('docs/unnamed-world-batch252-review.json')
    rows = [x for x in prior['items'] if x['decision']=='hold']
    entity = read('data/name-research/reading-sources/lismore-Q6559021.json')['entities']['Q6559021']
    assert entity['labels']['ja']['value']=='リズモア'
    assert any(c['mainsnak']['datavalue']['value']=='2160062' for c in entity['claims']['P1566'])
    item = next(x for x in rows if x['id']=='GeoNames:2160062')
    evidence = {x['peak']:x for x in read(work/'address-name-review.json')['items']}
    approvals = read('docs/unnamed-world-name-approvals.json')
    existing = {x['peak'] for x in approvals['items']}
    assert len(existing)==len(approvals['items'])==832
    url = 'https://www.wikidata.org/wiki/Q6559021'
    note = '第253回：69参照名をGeoNamesIDでWikidata一括検索、56対応を取得。日本語ラベルが見つかった対象は2160062のみ。Q6559021原JSONはtown in Victoria Australia、日本語リズモア、GeoNames2160062、座標-37.955,143.345を明記（revision2498984936）。原69d917331380b739bbd426b5 LismoreCommunityPharmacy32HighStを地域共同体サイト本文32HighSt Lismore VICと再照合。NSW同名都市の用例は転用せず対象VIC町の登録名として採用。公的日本語指定・現地録音認定ではない。位置と密度は不変。'
    aliases = read(work/'candidate-japanese-aliases.json')
    assert not aliases['aliases'].get('2160062')
    aliases['aliases']['2160062'] = [dict(name='リズモア', preferred=False, source_url=url, source='Wikidata', revision=entity['lastrevid'])]
    for peak in item['peak_keys']:
        p=evidence[peak]; c=p['candidates'][0]
        assert c==next(e['reference'] for e in item['evidence'] if e['peak']==peak)
        assert p['status']=='candidate_supported' and c['support_share']>=.85 and c['supporting_pois']>=6 and c['distance_m']<=1000
        assert p['distinct_coordinates']>=4 and p['with_address']>=4 and peak not in existing
        approvals['items'].append(dict(peak=peak, ref=c, batch=253, policy='address_review_85', reviewed_by='Codex', registered_source_url=url, review_note=note))
        existing.add(peak)
    item.update(decision='adopt', ja='リズモア', source_kind='registered_japanese', source_url=url, reason=note, external_research_batch=253,
                research_urls=[url,'https://lismore.vic.au/lismore-community-pharmacy.html'])
    item.pop('next_research_lead',None)
    summary=dict(candidate_peaks_before=44, previous_holds_before=25, adopted_candidate_peaks=1, remaining_candidate_peaks=43,
                 resolved_previous_holds=0, remaining_previous_holds=25, added_total=1, published_total=833, unnamed_remaining=4523, individually_researched_held_references=0)
    assert sum(len(x['peak_keys']) for x in rows if x['decision']=='hold' and x['group']=='new_candidates')==43
    summary['registered_alias_lookup'] = dict(queried_references=69, linked_entities=56, matching_japanese_labels=1, evidence='data/name-research/reading-sources/batch253-wikidata-labels.json')
    save('docs/unnamed-world-batch253-review.json',dict(snapshot=prior['snapshot'],summary=summary,policy='対象町の登録日本語名・参照ID・公的施設住所を直接照合。',items=rows))
    save(work/'candidate-japanese-aliases.json',aliases)
    save('docs/unnamed-world-name-approvals.json',approvals)
    queue=read(work/'remaining-review-queue.json')
    queue['items']=[x for x in queue['items'] if x['peak'] not in existing]
    queue['remaining']=len(queue['items']);queue['priority_counts']=dict(Counter(str(x['priority']) for x in queue['items']))
    assert queue['remaining']==4523
    save(work/'remaining-review-queue.json',queue)
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__':
    main()
