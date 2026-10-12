"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'5028985': ('グリグラ', 'https://web.archive.org/web/20110722194213/http://www.ap.org/minnesota/prono.html', 'AP通信のミネソタ州発音ガイドで地名の読みを確認。MNのEast State St・Main Aveと町名を含む原POI施設名を照合。保存版の発音に基づく編集音写であり公式日本語名ではない。'), '5019235': ('ブライスリン', 'https://web.archive.org/web/20110722194213/http://www.ap.org/minnesota/prono.html', 'AP通信のミネソタ州発音ガイドで地名の読みを確認。MNのN 3rd St・N Main StとBricelyn State Bankの原住所を照合。保存版の発音に基づく編集音写。'), '5043838': ('ロスセイ', 'https://web.archive.org/web/20110722194213/http://www.ap.org/minnesota/prono.html', 'AP通信のミネソタ州発音ガイドで地名の読みを確認。MNの1st St SW・2nd St NWとRothsay Secondaryの原住所を照合。モデルのロースエイは採用しない。保存版の発音に基づく編集音写。'), '5050174': ('トフティ', 'https://web.archive.org/web/20110722194213/http://www.ap.org/minnesota/prono.html', 'AP通信のミネソタ州発音ガイドで地名の読みを確認。MNの原POI地名Tofteが33件、住所あり25件、異なる座標29件。Tofte Fire Dept.など施設名も対応。モデルのトフトは採用しない。保存版の発音に基づく編集音写。'), '2057730': ('ワイルキャッチェム', 'https://m.scoop.co.nz/stories/BU0612/S00298/cockatoo-to-humpty-doo.htm', 'Tourism Australiaが発行しScoopに掲載した2006年の広報資料で西オーストラリアの町の読みを確認。WAのRailway Tce・Honour Ave、郵便局の原住所と照合。検索取得できた本文の発行者と州・地名・発音説明を確認。公式日本語名ではなく編集音写。')}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch8-review.json')
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
        item['address_rechecked_batch']=9
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
                ja_editorial=ja, batch=9, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=209, previous_holds_before=77,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    save('docs/unnamed-world-batch9-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='未反映286峰の住所条件を再検証。AP通信の州別発音ガイドとTourism Australiaの発行資料で確認できた5峰を採用。公式日本語名としては扱わない。残りの読みの個別調査は未完了。',items=rows))
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
