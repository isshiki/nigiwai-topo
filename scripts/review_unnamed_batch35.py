"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {}
RESEARCHED_HOLDS = {'5888569': ('村公式https://www.villageofavonlea.com/aboutとカナダ地名局https://geonames.nrcan.gc.ca/search-place-names/unique?id=HACMRでSaskatchewanの村を確認。300 McRorie Aveの州許可一覧は検索結果にあるが本文404で一次照合未完了。Avonlea.caは別州の観光施設、既存日本語は小説・日本の店等で対象町の読み根拠として採用しない。', ['https://www.villageofavonlea.com/about', 'https://geonames.nrcan.gc.ca/search-place-names/unique?id=HACMR', 'https://www.slga.com/-/media/slga/files/liquor/for-suppliers/retailer-details/saskatchewan-rsps/list-of-saskatchewan-retail-store-permittees-rsps-jan-1-2026.pdf']), '5968869': ('16 POIが4座標に集中するため住所支持の独立性に注意。Tweedsmuir Park Lodgeの7001 Corbould Drは観光協会https://bellacoola.ca/businesses/tweedsmuir-park-lodge/でBella Coolaの郵便所在地として掲載され、Stuieの施設という別資料もある。郵便地名と実所在地を混同せず個別座標検証が必要。Hagensborgの現地発音根拠も未確定で保留。', ['https://bellacoola.ca/businesses/tweedsmuir-park-lodge/', 'https://bellacoolaforest.com/wp-content/uploads/2020/11/Wood-Post-Aug-2020.pdf'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch34-review.json')
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
        item['address_rechecked_batch']=35
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=35)
            continue
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='pronunciation', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=35, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=161, previous_holds_before=59,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==35} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch35-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='未反映220件の住所条件を再検証。Avonleaの同名施設混同とHagensborgの座標集中・郵便地名の注意点を個別調査。追加採用なし。',items=rows))
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
