"""Publish Burstall's identity-checked registered Japanese label."""
import json
from pathlib import Path
from collections import Counter

def read(p):
    return json.loads(Path(p).read_text(encoding='utf-8'))

def save(p, x):
    Path(p).write_text(json.dumps(x, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def main():
    work = Path('data/name-research/unnamed-world')
    prior = read('docs/unnamed-world-batch251-review.json')
    rows = [x for x in prior['items'] if x['decision']=='hold']
    entity = read('data/name-research/reading-sources/burstall-Q855486.json')['entities']['Q855486']
    assert entity['labels']['ja']['value']=='バーストール'
    assert any(c['mainsnak']['datavalue']['value']=='5912226' for c in entity['claims']['P1566'])
    item = next(x for x in rows if x['id']=='GeoNames:5912226')
    evidence = {x['peak']:x for x in read(work/'address-name-review.json')['items']}
    approvals = read('docs/unnamed-world-name-approvals.json')
    existing = {x['peak'] for x in approvals['items']}
    assert len(existing)==len(approvals['items'])==831
    url = 'https://www.wikidata.org/wiki/Q855486'
    note = '第252回：Wikidata Q855486原JSONの日本語ラベル「バーストール」、GeoNames ID5912226、SK町の座標を直接確認（revision2543753042）。原図書館176bb8cff17e4efae4561da4の425MartinStをCER公開通知PDF1頁のChinookRegionalLibrary BurstallBranch39 425MartinStreet Burstall Saskatchewanと再照合。町公式史はGeneralHenryEdwardBurstallからの命名を明記。別人Saraや英国の村からの転用ではなく対象町自体の登録日本語名として採用。Wikidata登録名は公的日本語指定・現地発音録音の保証ではない。位置と密度は変更しない。'
    aliases = read(work/'candidate-japanese-aliases.json')
    assert not aliases['aliases'].get('5912226')
    aliases['aliases']['5912226'] = [dict(name='バーストール', preferred=False, source_url=url, source='Wikidata', revision=entity['lastrevid'])]
    for peak in item['peak_keys']:
        p=evidence[peak]; c=p['candidates'][0]
        assert c==next(e['reference'] for e in item['evidence'] if e['peak']==peak)
        assert p['status']=='candidate_supported' and c['support_share']>=.85 and c['supporting_pois']>=6 and c['distance_m']<=1000
        assert p['distinct_coordinates']>=4 and p['with_address']>=4 and peak not in existing
        approvals['items'].append(dict(peak=peak, ref=c, batch=252, policy='address_review_85', reviewed_by='Codex', registered_source_url=url, review_note=note))
        existing.add(peak)
    item.update(decision='adopt', ja='バーストール', source_kind='registered_japanese', source_url=url, reason=note, external_research_batch=252,
                research_urls=[url,'https://docs2.cer-rec.gc.ca/ll-eng/llisapi.dll/Open/615305','https://www.abetterwayoflife.ca/town-history/'])
    item.pop('next_research_lead',None)
    summary=dict(candidate_peaks_before=45, previous_holds_before=25, adopted_candidate_peaks=1, remaining_candidate_peaks=44,
                 resolved_previous_holds=0, remaining_previous_holds=25, added_total=1, published_total=832, unnamed_remaining=4524, individually_researched_held_references=0)
    assert sum(len(x['peak_keys']) for x in rows if x['decision']=='hold' and x['group']=='new_candidates')==44
    save('docs/unnamed-world-batch252-review.json',dict(snapshot=prior['snapshot'],summary=summary,policy='対象町の登録日本語名・参照ID・公的施設住所を直接照合。',items=rows))
    save(work/'candidate-japanese-aliases.json',aliases)
    save('docs/unnamed-world-name-approvals.json',approvals)
    queue=read(work/'remaining-review-queue.json')
    queue['items']=[x for x in queue['items'] if x['peak'] not in existing]
    queue['remaining']=len(queue['items']);queue['priority_counts']=dict(Counter(str(x['priority']) for x in queue['items']))
    assert queue['remaining']==4524
    save(work/'remaining-review-queue.json',queue)
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__':
    main()
