"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'6181652': ('ウィクウェミコン', 'https://fnp-ppn.aadnc-aandc.gc.ca/FNP/Main/Search/FNMain.aspx?BAND_NUMBER=175&lang=eng', 'カナダ政府First Nation ProfilesのWik-we-mi-kongを確認。ONのWikwemikong Wayと28/31件の住所地名を照合。政府は日本語表記を指定しておらず、ここでのカタカナは編集音写。現在のWiikwemkoong綴りとは区別して元参照名の読みを採用。'), '2682575': ('リックスグレンセン', 'https://snowsafety.info/wordpress/wp-content/uploads/2024/08/fefee16b5a00a311824742af8a0c86c3-1.pdf', '全日本スキー連盟安全対策委員会2024年事業報告の会場・宿舎名リックスグレンセンと所在地98194 Riksgränsenを確認。原POIのRiksgränsvägen・Norrbotten/Kiruna、28/29件を照合。別の報告にグランセン表記もあるため表記を選定。自治体の公式日本語名ではなく資料に基づく編集表記。'), '2684034': ('ポルユス', 'https://www.hoshizora.de/shishido/sweden201110/porjus/porjus.html', '現地訪問者の2011年オーロラ観望記でスウェーデンPorjusの村名ポルユスを確認。田中千尋の現地観測記録でもPorjus（ポルユス）とNorbotten/Jokkmokkの対応を確認。原住所52/52件、Vintervägen・Fjällgatanと照合。駅・製品のみを指す結果は根拠にしない。個人の訪問資料による編集表記で自治体公式日本語名ではない。')}
RESEARCHED_HOLDS = {'6177197': ('自治体史の発音説明Sip-O-Whiskeyは旧名Sipiweskeであり現行Wawanesaではない。', ['https://www.oakland-wawanesa.ca/p/Village-of-Wawanesa-History']), '6155718': ('議会記録はSt. Brieuxに地域英語とフランス語の読みの違いがあると記載するが、読みを文字で指定していない。', ['https://publications.gc.ca/collections/collection_2013/parl/xc59-1/XC59-1-2-411-69-eng.pdf']), '5965019': ('Granumの発音資料はノルウェー姓または生物学用語でありAlbertaの町ではない。', ['https://www.svkrfam.no/documents/Slektsbok.pdf']), '6136934': ('Ryleyの読みは人名辞書でありAlbertaの村の読みとして確定できない。', ['https://www.behindthename.com/name/ryley']), '2669360': ('Tärnabyの日本語結果は商品名と機械翻訳を含む宿泊施設サイトで表記が混在。地域の読みの根拠として不足。', ['https://www.ishii-sports.com/wp-content/uploads/2018/06/kavat_aw18_01.pdf']), '2155315': ('Nimmitabelの観光記事の発音説明はMonaroを指し、Nimmitabelの読みではない。', ['https://highcountryonline.com.au/bombala-delegate-nimmitabel/']), '2059048': ('Warookaの由来に複数案があり、検索記事は他の町の発音を記載。対象の現地読みは未確定。', ['https://exploringsouthaustralia.com.au/weird-place-names-in-south-australia/']), '6072486': ('Meteghanの検索で得たpronouncedは死亡記事の表現であり地名の発音根拠ではない。', ['https://haligonia.ca/police-investigate-fatal-highway-accident-298801/']), '5906055': ('日本語論文のBoston Barは小説の酒場でありBritish Columbiaの町ではない。', ['https://kwansei.repo.nii.ac.jp/record/16276/files/20130924-4.PDF'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch11-review.json')
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
        item['address_rechecked_batch']=12
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=12)
            continue
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='pronunciation', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=12, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=204, previous_holds_before=71,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==12} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch12-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='未反映275峰の住所条件を再検証。カナダ政府の読みと日本の団体報告・現地訪問記で確認した3峰を編集表記として採用。公式日本語名としては扱わない。残りの読みの個別調査は未完了。',items=rows))
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
