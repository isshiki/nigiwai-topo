"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'6051177': ('リースク', 'https://leask.ca/leask-office/', 'Leask CA SK GeoNames6051177峰53.022,-106.743支持27/27住所23独立座標21参照787m。原35c099de80014f5a38caf468 Village Office15MainSt座標53.022351,-106.743314を自治体LeaskOffice Location15MainStreetに直接照合。郵送Box40と区別し同番地LeaskHotelを自治体施設として混同しない。CMU leask L IY1 S Kによる編集表記リースク、当地実聴・公的日本語指定ではない。元位置密度不変。'), '5968839': ('ハファード', 'https://www.srsd119.ca/wp-content/uploads/SP_RL_SRPSD_to_Parents_re_Jan_return_2021_12_30.pdf', 'Hafford CA SK GeoNames5968839峰52.728,-107.354支持34/38=.895住所33独立座標28参照229m。原dd6519d77cfd4dc3cedb8984 HaffordRegionalLibrary17MainStを学区2021/12/30公開資料PDFindex2印刷3頁HaffordBranchLibrary17MainStに直接照合。原73e6c4e9cf854410b2ea44c1 HaffordTownOffice106MainStも同頁TownOfHafford106MainStに照合、図書館17と自治体106を区別。CMU hafford HH AE1 F ER0 Dによる編集表記ハファード、モデルハフォードを修正。辞書は当地実聴・公式日本語指定を証明しない。元位置密度不変。'), '5941474': ('ドナルダ', 'https://village.donalda.ab.ca/wp-content/uploads/2021/07/Business-Tourism-Guide-2021-22.pdf', 'Donalda CA AB GeoNames5941474峰52.585,-112.575支持20/23=.870住所19独立座標20参照457m。第127回で保存・描画確認済み自治体BusinessTourismGuide2021-22 PDFindex32印刷31頁広告TERESAS Catering5019MainStreetDonaldaABと原e29aff40436a40d647310ec9 TheresasCatering5019MainStの業務番地村名を照合。Teresa/Theresa綴り差は維持し同住所ATBや広告別店Stettlerと混同しない。CMU donalda D OW0 N AA1 L D AH0による編集表記ドナルダ、モデルドンダラを修正。辞書は当地実聴・公式日本語指定を証明しない。元位置密度不変。')}
RESEARCHED_HOLDS = {'5898322': ('Benito原図書館141MainStに対し図書館公式historyは140MainStreetで2007移転も記録。同一番地とは扱わない。原AgShield170Path83に対して会社公式170Highway83Northは会社名番地道路番号が対応するがPath/HighwayとNorthの差を記録し、追加地理照合を続ける。モデルだけで読みを確定しない。', ['https://benitolibrary.ca/history/', 'https://www.agshield.com/contactus.html'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch191-review.json')
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
        item['address_rechecked_batch']=192
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=192)
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
                ja_editorial=ja, batch=192, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=85, previous_holds_before=31,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==192} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch192-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='Leask自治体とHafford学区資料、Donalda確認済み広告の住所を照合。CMU編集表記と当地実聴を区別。Benito住所差は保留。',items=rows))
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
