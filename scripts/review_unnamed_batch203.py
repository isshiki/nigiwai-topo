"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'6067347': ('メアリーフィールド', 'https://www.centralplainsco-op.crs/wcm/connect/sites/880c162e-0487-4a29-b1db-0625ab03e267/May%2B2018%2BCardlock%2BLocation%2BGuide.pdf?CACHEID=ROOTWORKSPACE.Z18_2IKA1G82M08S50ANCIK0482G01-880c162e-0487-4a29-b1db-0625ab03e267-oBQQ0DY&MOD=AJPERES', 'Maryfield CA SK GeoNames6067347峰49.836,-101.525支持30/31=.968住所28独立座標20参照691m。原2b34db78ba38452090b8f268 BorderlandCooperativeLtd101MainSt49.8358709,-101.5251598を協同組合公式配信2018CardlockGuide PDFindex251同社101MainStreet Maryfieldと直接照合。掲載49°49′59.67N101°31′36.50Wは原POIから約306mで同町。別原RBC115MainStは銀行2014年公式閉鎖報告の検索結果があり現在営業の裏付けに使わない。CMU mary M EH1 R IY0 field F IY1 L Dからメアリーフィールドの構成語編集音写。当地実聴・公式日本語指定・別名競走馬の地名転用ではない。モデルマリーフィールドは不採用。原位置密度不変。'), '5691025': ('ピック・シティ', 'https://attorneygeneral.nd.gov/wp-content/uploads/2025/03/Licensees-AlcoholicBeverage.pdf', 'PickCity US ND GeoNames5691025峰47.511,-101.455支持17/19=.895住所15独立座標18参照116m。原4cb8c26643ec6dcbb9609831 DamBarSteakhouse35MainRdEをNorthDakotaAttorneyGeneral2025-03-05名簿PDFindex44 THE DAM BAR LLC35 MAIN RD E PICK CITY ND58545に直接照合。郵送POBOX2646とは区別。CMU pick P IH1 K city S IH1 T IY0の構成語編集音写ピック・シティ。由来人物Pickの実聴や当地発音確定ではなく、Bavarian別言語IPAも転用しない。原位置密度不変。')}
RESEARCHED_HOLDS = {}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch202-review.json')
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
        item['address_rechecked_batch']=203
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=203)
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
                ja_editorial=ja, batch=203, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=71, previous_holds_before=30,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==203} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch203-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='Maryfield協同組合・PickCity州免許名簿住所を照合し構成語編集表記を追加。',items=rows))
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
