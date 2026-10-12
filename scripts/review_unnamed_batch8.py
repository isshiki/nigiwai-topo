"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {
    '5711124': ('アルシー', 'https://lifeofwry.com/2023/11/30/corvallis-to-alsea-to-waldport-to-florence-to-mapleton-to-corvallis/', '現地訪問者の一次記録で町の読みを確認。公的発音資料ではない。ORのE Main St住所と参照位置を照合。'),
    '5798370': ('アイオウン', 'https://media.scenicwa.com/sbrtguide15/files/inc/d3d93c8940.pdf', 'ワシントン州の観光道路ガイドでIoneの読みを確認。WAのTown Hall・Blackwell St住所と照合。他州の同名地と区別。'),
    '5832055': ('メティーツィー', 'https://www.latimes.com/nation/la-na-big-jim-blake-20150802-story.html', '現地バーを取材した記事の地元発音説明を確認。昔の先住民語の読みとは区別。WYのState St住所と照合。新聞取材に基づく編集音写。'),
    '5489619': ('サン・ホーン', 'https://takemytrip.com/2016/08/san-jon-new-mexico/', '現地旅行著者の訪問記録にある地名発音説明を確認。公的資料ではない。NMのHighway 469住所と照合。'),
    '5039068': ('ニーヴィス', 'https://www.roadsideamerica.com/story/8738', 'ミネソタの町の実地観光記事で発音を確認。カリブ海の同名島の資料は使わない。MNのBunyan Trails Dr住所と照合。'),
    '4095185': ('ユーライ', 'https://www.simonandschuster.ca/books/The-Ballad-of-Little-River/Paul-Hemphill/9781439138267', '現地に住んで取材したPaul Hemphillの著書を出版社の抜粋で確認。人名の通常読みとは区別。ALのDavis Ave・Highway 21住所と照合。'),
    '5991882': ('キラルー', 'https://inrdream.com/2018/07/bonnechere-provincial-park/', 'オンタリオ州立公園を訪問した著者の地域旅行記で読みを確認。アイルランドの同名地の読みだけを転用しない。ONのQueen St・Mill St住所と照合。公的資料ではない。'),
    '5898304': ('ベンゴフ', 'https://wheelygoodeacrosscanada.blogspot.com/2011/08/today-we-need-to-go-into-downtown.html', '町を訪問した著者の記録で発音を確認。姓の発音資料だけから推測しない。SKのCredit Union・Regional Library・Main St住所と照合。公的資料ではない。'),
    '6128122': ('ローロー', 'https://epe.lac-bac.gc.ca/100/201/300/briarpatch/2011/2011-08/articles/view/the-shipbuilder-dog-river-other-roadside-delights?nodisclaimer=1', 'カナダ国立図書館保存のBriarpatch現地旅行記事で町の読みを確認。フランス語の一般名詞・姓の読みを転用しない。SKのMain St住所と照合。保存機関が発音を認定した意味ではない。'),
    '4461962': ('カララ', 'https://visitcurrituck.com/blog/your-questions-about-corolla-answered/', '地域観光局の地元発音説明を確認。車名の読みとは区別。NCのCorolla住所の支持102件を確認。少数のRaleigh住所を採用根拠に含めない。'),
    '2657749': ('アハラカル', 'https://www.otter-adventures.co.uk/regions/loch-moidart.html', '当地で活動し近隣に住むガイドの発音説明を確認。Main St・Post Office・Highlandの原住所と照合。公式日本語名ではない。'),
    '6110051': ('ポンテックス', 'https://www.flickr.com/photos/pageworld/53530787226', '近隣Val Marie在住の写真家James R. Pageの現地記録で町の読みを確認。写真は再配布しない。SKのCentre St住所と照合。公的資料ではない。'),
    '6092735': ('オギマー', 'https://www.policymagazine.ca/a-small-saskatchewan-towns-heritage-minute-close-up/', 'Historica Canadaの代表による現地撮影訪問記録で町の読みを確認。モデルのオジェマを採用しない。SKのMain St住所と照合。近隣参照点976mは個別確認用の1km条件内であり峰と参照点は同じ位置ではない。'),
}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch7-review.json')
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
        item['address_rechecked_batch']=8
        if ident not in CONFIRMED:
            continue
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='pronunciation', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=8, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=215, previous_holds_before=84,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    save('docs/unnamed-world-batch8-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='未反映299峰の住所条件を再検証。採用13峰の現地読みを外部資料で確認。一次旅行記・地域観光・現地取材の出典強度を明示し、公式日本語名としては扱わない。残りの外部読み調査は未完了。',items=rows))
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
