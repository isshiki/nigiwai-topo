"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'2058132': ('ウィラブラ', 'https://www.parktrek.com.au/wp-content/uploads/2019/08/Full-Flinders-Ranges-Interp.pdf', 'Park TrekのFlinders Ranges地域ガイド22ページでWirr-ab-raの読みを確認。SAのMain North Rd・High StとWirrabara Farm Serviceの原住所を照合。モデルのウィラバラを採用せず、地域旅行会社の発音説明から編集音写。公式日本語名ではない。'), '2145046': ('ウォルハラ', 'https://geekwanderlost.blogspot.com/2012/05/erica-to-mornington-peninsula-via.html', '現地を訪問した著者の記録でVictoriaのWalhallaはValhallaのVをWに替えた発音と確認。別の鉄道旅行記でもWoll-hallaを確認。VICのChurch Hill Rd・Main Rdの原POI住所を照合。米国South Carolinaの同名町のVALHALLA発音は転用しない。参照点877mは住所再確認用1km条件内であり峰と同一位置ではない。公的資料ではなく編集音写。'), '2068155': ('クーリン', 'https://freedomandfurballs.wordpress.com/2017/02/', '西オーストラリアを訪問した著者の旅行記でKulinの町の読みKoolinを確認。検索で取得できた本文の州・町・発音説明を確認。WAのJohnston Stの郵便局・ホテル原住所と照合。ビクトリアのKulin先住民集団の発音資料は使わない。モデルのクリンを採用せず、一次訪問記に基づく編集音写。公式日本語名ではない。')}
RESEARCHED_HOLDS = {'4362059': ('検索で得た発音は姓・人名のモデル推測であり、対象のMarylandの町の現地読みを確認できない。保留。', ['https://nameplay.org/name/Mchenry']), '5073930': ('読みの説明はWyomingの郡またはNebraskaの河川を対象とし、対象の村の読みの個別確認には不足。保留。', ['https://www.niobraracountylibrary.org/historicals/historical-details/?id=7', 'https://helen-olsson.com/floating-the-niobrara/']), '4972355': ('Monheganの辞書項目には発音記載がなく、地域発音サイトの著者・一次根拠が確認できない。保留。', ['https://en.wiktionary.org/wiki/Monhegan', 'https://talklikealocal.org/']), '6051792': ('Legalのフランス語姓由来は見つかったが、対象の町の読みの信頼できる個別資料が不足。保留。', ['https://coolcanadianplaces.ca/places/legal-alberta/']), '5946523': ('Edamの検索結果はチーズ・人名の発音であり、Saskatchewanの町の現地読みではない。保留。', ['https://www.babynamespedia.com/pronounce/Edam']), '6168694': ('Treherneの発音は人名・姓の資料であり、Manitobaの町の現地読みを確認できない。保留。', ['https://www.ask-oracle.com/baby-name/treherne/']), '5921077': ('Chéticampは地域のフランス語と域外英語の読みが異なる。港湾機関の説明は元の先住民語の読みで現在の地名とは異なる。混同せず保留。', ['https://www.hacheticamp.ca/en/local-amenities/about-cheticamp/', 'https://en.wiktionary.org/wiki/Ch%C3%A9ticamp']), '5934031': ('Cuparの辞書発音はScotlandの同名地と一括で、Saskatchewanの町の地域発音の個別根拠が不足。保留。', ['https://dictionary.cambridge.org/pronunciation/english/cupar', 'https://en.wiktionary.org/wiki/Cupar']), '2154355': ('Omeoの発音資料は人名投稿・動物園のコアラの名を対象とし、Victoriaの町の現地読みとは確定できない。保留。', ['https://www.behindthename.com/name/omeo/submitted']), '8358872': ('Jerramungupの観光資料の発音説明は語源となった先住民語。現在の町名の現地読みと同一とは断定できず保留。', ['https://visitwa.com.au/australias-south-west-region/63-jerramungup-wa.html']), '2144846': ('Walwaの百科事典にIPAがあるが個別の発音出典を確認できず、現地一次資料での裏付けは未完了。保留。', ['https://en.wikipedia.org/wiki/Walwa%2C_Victoria']), '5901898': ('Birtleの検索結果は人名・英国の地名の読みであり、Manitobaの町の現地読みは未確認。保留。', ['https://nameberry.com/name/birtle']), '5887546': ('Ashernの検索結果は同名の地層の文献で、町名の発音記載が確認できない。保留。', ['https://weblex.canada.ca/html/000000/GSCC00053000496.html']), '5924236': ('Cloyneの辞書項目はOntarioの町を含むが発音を記載しない。Irelandの読みだけは転用せず保留。', ['https://en.wiktionary.org/wiki/Cloyne'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch9-review.json')
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
        item['address_rechecked_batch']=10
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=10)
            continue
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='pronunciation', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=10, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=209, previous_holds_before=72,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch10-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='未反映281峰の住所条件を再検証。オーストラリアの地域旅行会社ガイドと現地訪問記で確認できた3峰を採用。公式日本語名としては扱わない。残りの読みの個別調査は未完了。',items=rows))
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
