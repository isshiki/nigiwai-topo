"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'6167524': ('トンプキンズ', 'https://www.saskatchewan.ca/government/municipal-administration/municipal-directory?s=%7B84d91843-bed4-41ff-9424-6bda0f797561%7D', 'Tompkins CA SK GeoNames6167524峰50.062,-108.794支持19/19住所18独立座標15参照804m。原3a030cb4ff3944bee0ede9e0 Village of Tompkins5 2nd Stを州自治体名簿Physical Address5 2nd Street Tompkins SK S0N2S0に直接照合。Mailing Box247と区別。CMU tompkins T AA1 M P K IH0 N Zに基づく編集表記トンプキンズ、当地実聴・公的日本語指定ではない。元位置密度不変。'), '5919514': ('チェンバレン', 'https://www.longlakeinsurance.ca/chamberlain/', 'Chamberlain CA SK GeoNames5919514峰50.852,-105.568支持18/21=.857住所13独立座標19参照194m。原f09cfd4dbf8244392295118f Long Lake Insurance703 Hwy11を同社公式Chamberlain Office703 Highway11 Box43 Chamberlain SK S0G0R0に直接照合。郵送Box43を道路住所と区別。CMU chamberlain CH EY1 M B ER0 L AH0 Nに基づく編集表記チェンバレン、当地実聴・公的日本語指定ではない。元位置密度不変。'), '4728323': ('シェリダン', 'https://splashway.com/contact/', 'Sheridan US TX GeoNames4728323峰29.496,-96.671支持28/32=.875住所22独立座標29参照238m。原4c58816a12f0d13a149709ad Splashway Family Waterpark5211MainSt座標29.497436,-96.670844を同施設公式PhysicalAddress5211MainStreet Sheridan Texas77475に直接照合。POBox85と別Hideaway5235の住所と区別。TSHA https://www.tshaonline.org/handbook/entries/sheridan-tx-colorado-county 町座標29.493574,-96.671085でColorado郡の地点を補確認。Houston郡同名旧集落やWyomingの町と混同しない。CMU sheridan SH EH1 R IH0 D AH0 Nに基づく編集表記シェリダン、当地実聴・公的日本語指定ではない。元位置密度不変。')}
RESEARCHED_HOLDS = {'5230920': ('Roscoe SD原自治体110 N Mitchell Stに対し現自治体公式https://roscoesd.org/contactは205 N Mitchell St POBox95。住所差を確認したため同一住所として採用しない。原Avera206MerrillAveWも公式本文未取得。候補維持し別の原施設一次住所を調査。', ['https://roscoesd.org/contact'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch189-review.json')
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
        item['address_rechecked_batch']=190
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=190)
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
                ja_editorial=ja, batch=190, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=90, previous_holds_before=31,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==190} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch190-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='Tompkins州自治体名簿、Chamberlain保険会社、Sheridan施設の原住所を照合。辞書編集表記と当地実聴を区別。',items=rows))
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
