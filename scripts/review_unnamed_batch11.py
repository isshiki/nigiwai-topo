"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'5913030': ('ケイブリー', 'https://cabri.ca/history-of-cabri/', '町公式サイトのKay bree（第一音節強勢）を確認。SKのCentre Stの原住所とCabri 41/45件を照合。参照点832mであり峰と同一位置ではない。公式日本語名ではなく編集音写。'), '5411432': ('アグウィラー', 'https://www.denver7.com/news/local-news/how-do-you-say-that-in-colorado-check-out-the-correct-pronunciations', 'Denver7のColorado地名ガイドのAguilar in Las Animas、AG-wih-larを確認。原住所27件はCO 26件・AK 1件で、Aguilar表記はCO 22件・AK 1件。AKのAce Hardwareは州の不整合があるため地域特定の根拠から除外し、COのMain St等で照合。POI自体の密度は変更しない。公式日本語名ではなく編集音写。'), '4709236': ('マーケイ', 'https://petticoatsandpistols.com/2016/11/how-to-talk-like-a-texan-place-names-edition/', 'Kathleen Rice AdamsのTexas地域発音記事でMarquezはmar-KAYと確認。TX 77865とGoodwin Blvdの原住所、Marquez 36/37件を照合。姓の一般的なスペイン語発音やモデルのマラケスを転用しない。参照点638m。個人の地域発音記事による編集音写であり公式日本語名ではない。')}
RESEARCHED_HOLDS = {'5336303': ('USGSのChilcoot/Chilkoot説明はAlaskaでありCaliforniaの町ではない。現地読み未確定。', ['https://pubs.usgs.gov/bul/0187/report.pdf']), '5320914': ('Wikieup公式サイトは地名由来のみ。検索の発音説明はHualapaiで対象語が違う。', ['https://wikieup.org/']), '5226988': ('Colomeの発音サイトは自身の近似読みとの注意書きがあり、独立した現地資料による確認が不足。', ['https://roadsidethoughts.com/sd/colome-xx-tripp-profile.htm']), '5718823': ('Chemultの発音結果は自動推定、または未聴取の投稿音声。確定読みとして採用しない。', ['https://hyphenateit.com/en-us/words/chemult', 'https://forvo.com/word/chemult%C2%A0/']), '6084170': ('ForvoのMundareはLatinの動詞でありAlbertaの町ではない。', ['https://forvo.com/word/mundare/']), '5951004': ('日本語旅行記事のフェアモント温泉は施設を指し、町名との対象一致が未確定。', ['https://www.thefraser.com/pdfs/gekkan-fraser-2018-04.pdf']), '6074485': ('先住民団体ガイドの読みはManitowaningでありMindemoyaではない。語源だけで読みを確定しない。', ['https://www.anishinabek.ca/wp-content/uploads/2017/04/2017pwguideweb.pdf']), '5993109': ('Alberta保健機関の住所でKitscotyの場所は確認できるが、発音記載がない。', ['https://www.albertahealthservices.ca/findhealth/facility.aspx?id=1000156']), '6085350': ('Myrnam公式サイトのウクライナ語語源だけでは現在の現地読みを確定できない。', ['https://www.myrnam.ca/']), '5928098': ('CoronachのIPAは百科事典転載で、地域発音の一次根拠が未確認。', ['https://en-academic.com/dic.nsf/enwiki/2498397/']), '5932187': ('Cremona AlbertaのIPAは百科事典転載で、現地の個別発音資料が未確認。', ['https://en-academic.com/dic.nsf/enwiki/1821661/1067594'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch10-review.json')
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
        item['address_rechecked_batch']=11
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=11)
            continue
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='pronunciation', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=11, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=207, previous_holds_before=71,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch11-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='未反映278峰の住所条件を再検証。町公式サイト・地域放送局・Texas地域発音記事で確認できた3峰を採用。公式日本語名としては扱わない。残りの読みの個別調査は未完了。',items=rows))
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
