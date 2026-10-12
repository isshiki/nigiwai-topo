"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'6164443': ('シオドア', 'https://www.villageoftheodore.com/page2.html', 'Theodore CA SK GeoNames6164443峰51.425,-102.919支持26/29=.897住所26独立座標22参照920m。原5dd36809fada0200071dc418 WestlandInsuranceGroupLtd O/A FarrellAgencies102MainStreetを村公式Businesses WestlandInsurance102MainStreetと照合。原学校POIのInvermay市町村欄不一致は別施設で残し、今回の住所根拠と混同しない。CMU theodore TH IY1 AH0 D AO2 Rの英語辞書音写からシオドアを編集表記採用。当地実聴・公的日本語指定ではなくJMnedict同名地名を当地確認とみなさない。モデルテオドールは不採用。原位置密度不変。'), '6104764': ('パイロット・マウンド', 'https://build.crs/PilotMound/landing', 'PilotMound CA MB GeoNames6104764峰49.202,-98.895支持62/72=.861住所66独立座標55参照77m。原2b98d62089fe4af4a5d58203 FCL11BroadwayAveE49.2011895,-98.8929957をFederatedCooperativesLimited公式PilotMoundHomeCentre11BroadwayAvenueE PilotMoundMBと照合。原施設名はFCLという運営側略称で店舗表示名と完全同一文字列ではない。別HomeHardware133Broadway検索結果は403本文未読として今回の直接照合根拠にしない。CMU pilot P AY1 L AH0 T mound M AW1 N Dの構成語編集音写パイロット・マウンド。当地実聴・公的日本語指定ではない。原位置密度不変。')}
RESEARCHED_HOLDS = {'5915182': ('Canwood原RM621MainStに対しRM公式取得本文641MainStreetで番地不一致。村役場571MainStreetは別組織なので照合に使わない。原学校df88624b4a994d68227d3492 CanwoodPublicSchool8501stStEと学校公式検索結果8501stStreetEastが対応候補だがwebと通常HTTPS取得はいずれもタイムアウトで本文未確認。2007教育委員会PDFリンクは404。検索結果のみを直接確認とせず保留。', ['https://rmofcanwood.ca/home/welcome/', 'https://cw.srsd119.ca/', 'https://www.srsd119.ca/parentinformationfiles/schoolcommunitycouncilsfiles/SCCNewsletterOct07.pdf'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch203-review.json')
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
        item['address_rechecked_batch']=204
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=204)
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
                ja_editorial=ja, batch=204, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=69, previous_holds_before=30,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==204} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch204-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='Theodore村・PilotMound協同組合公式住所照合。Canwood番地差と取得失敗を記録。',items=rows))
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
