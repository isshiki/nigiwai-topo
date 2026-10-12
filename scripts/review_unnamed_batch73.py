"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'1720427': ('カラヤン', 'https://kotobank.jp/word/ばぶやん諸島-3164285', 'Calayan PH GeoNames1720427、支持20/22=.909、住所6、独立座標22、参照距離210m。元POI517a3911e4b0176567459850 Calayanの住所Babuyan Islands、localityCalayan、regionCagayanProvinceを日本大百科全書のバブヤン諸島・カガヤン州の位置説明に照合。ブリタニカ国際大百科事典小項目事典のコトバンク公開本文 https://kotobank.jp/word/ばぶやん諸島-3164285 は港をカラヤンと表記し、島名だけから町名を創作していない。フィリピン港湾庁 https://ppa.com.ph/sites/default/files/proc_request_files/M103_02162021__000003_RFQ.pdf 1頁を画像化して直接確認、Calayan Port,Calayan Island,Cagayanと明記。南シナ海のKalayaanを別地域として除外。元レストランCastillejosStの番地や個々の営業状態は外部で未確認、地域同定と全店舗住所の保証は区別。原FortIlocandiaRoom320住所CalayabはLaoag地名の可能性があり22件中例外として記録、地域支持の追加根拠には使わない。日本語使用例として採用、法的日本語指定や録音認定ではない。記事本文は転載せず名前・出典・照合判断のみ。位置密度不変。')}
RESEARCHED_HOLDS = {'7289197': ('HotelSagar原POI55541079498ec133ecdd839e SN Pant Marg View Pointを https://www.kausanihotel.com/contact-us.html の同住所KausaniUttarakhand263639に照合。インド政府観光サイトIncredibleIndia検索本文にはカウサニとウッタラーカンドがあるが直接本文取得はSSLエラー、wwwなしや旧.orgも取得不可。SSL無効化しない。検索断片のみでは採用せず公式日本語本文の別取得経路を次に確認。', ['https://www.kausanihotel.com/contact-us.html', 'https://www.prod.incredibleindia.gov.in/content/incredible-india-v2/ja/destinations/kausani.html']), '4972355': ('Monhegan日本語用例の再検索でモンヘガン・モンヘイガン・モンヒガン・モンヒーガン・大学資料モンガンなど差異を確認。旅行サイト機械翻訳の混在やブログだけで標準表記とは判断しない。次は地元MuseumまたはMaine公的発音資料と、元POI222MonheganAveの住所対応を調査。', ['https://satoyama.kenkyu.ryukoku.ac.jp/cms/wp-content/uploads/2022/10/ebd778a3fd00aa30ae06252defb6bd54.pdf'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch72-review.json')
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
        item['address_rechecked_batch']=73
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=73)
            continue
        item.pop('next_research_lead', None)
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='public_japanese', reason=note,
            japanese_label_type='public_japanese')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=73, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                japanese_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=137, previous_holds_before=45,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==73} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch73-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='Calayanの元地域住所と港湾庁所在地を照合し百科事典の港名日本語を反映。',items=rows))
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
