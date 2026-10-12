"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {
 '6086743': ('ニールバーグ', 'https://www.saskhealthauthority.ca/facilities-locations/manitou-health-centre', 'CA SK峰52.838,-109.629支持49/52=.942住所49独立座標31参照649m。原a205d93c697b4071d76fde60 ManitouHealthCentre1052ndAveWを州保健当局同名1052ndAvenueW NeilburgSKS0M2C0に直接照合。村公式https://www.neilburg.ca/neilburg_info.htmlも同施設1052ndAvenueWestを記載。Box190/280は郵送先で番地ではない。CMU neil N IY1 L、burg B ER1 Gからニールバーグを編集音写。構成語読みであり当地全語録音実聴や公的日本語指定ではない。位置密度不変。'),
 '5975777': ('ホッジビル', 'https://www.saskhealthauthority.ca/facilities-locations/hodgeville-health-centre', 'CA SK峰50.110,-106.960支持18/20=.9住所18独立座標13参照904m。原2d633917e7d1407269751ec3 HodgevilleHealthCentre105MainSt50.11247446833247,-106.96261895082291を州保健当局同施設105MainStreet HodgevilleSKS0H2B0に直接照合。原GreenDoor等7件同一座標を独立店舗位置証拠には数えず、別座標の同医療施設を照合対象とした。CMU hodge HH AA1 JH、ville V IH1 Lからホッジビルを編集音写。当地全語録音実聴や公的日本語指定、命名由来の確定とは区別。位置密度不変。')}

RESEARCHED_HOLDS = {}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch218-review.json')
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
        item['address_rechecked_batch']=219
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=219)
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
                ja_editorial=ja, batch=219, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=60, previous_holds_before=28,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==219} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch219-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='州保健当局の同施設同番地と元POIを照合。CMU構成語読みから編集音写。当地全語録音や公的指定とは区別。',items=rows))
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
