"""Apply explicitly source-reviewed readings; never accept model output alone."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
MI = 'https://www.michigan.gov/leo/bureaus-agencies/bureau-of-services-for-blind-persons/btbl/pronunciation-guide-you-say-it-how-in-michigan'
# id: Japanese editorial reading, evidence URL, evidence type, review explanation.
CONFIRMED = {
    '5006404': ('パワーズ', MI, 'pronunciation', 'ミシガン州の発音資料 POU-urz。MI住所と同州参照点を照合。'),
    '4985309': ('ベア・レイク', MI, 'pronunciation', 'ミシガン州の発音資料 Bear Lake。MI住所と同州参照点を照合。'),
    '5014368': ('ウェルズトン', MI, 'pronunciation', 'ミシガン州の発音資料では Wellston の s は濁音。モデルのウェルストンを修正。'),
    '4990192': ('カーティス', MI, 'pronunciation', 'ミシガン州の発音資料 Curtis。MI住所と同州参照点を照合。'),
    '4995875': ('ヘッセル', MI, 'pronunciation', 'ミシガン州の発音資料 Hessel。MI住所と同州参照点を照合。'),
    '5007828': ('ラディアード', MI, 'pronunciation', 'ミシガン州の発音資料 RUD-ee-urd。モデルのルードヤードを修正。'),
    '4878664': ('タイタンカ', 'https://publications.iowa.gov/30011/1/UIPronunciationGuide.pdf', 'pronunciation', 'アイオワ大学の地名発音資料 teye-TAHN-kuh。IA住所を照合。少数のKuala Lumpur表記を採用根拠にしない。'),
    '4380894': ('シャモイ', 'https://reader.ku.edu/sites/reader/files/2024-12/Missouri%20Place%20Names.pdf', 'pronunciation', 'KU Audio Readerのミズーリ州資料 shuh MOI。動物名の辞書発音とは区別。MO住所を照合。'),
    '5036056': ('ルートセン', 'https://webstpaul.com/the-vault/minnesota-pronunciation-guide/', 'pronunciation', 'セントポールの地域発音資料 LOOT-sen、Northeastern MN。政府資料ではなく地域著者資料に基づく編集音写。MN住所を照合。'),
    '2187816': ('マナポウリ', 'https://www.newzealand.com/jp/manapouri/', 'japanese', '政府観光局の湖畔の町マナポウリの日本語ページ。湖だけでなく町の参照であることを確認。'),
    '2185172': ('オワカ', 'https://www.newzealand.com/jp/owaka/', 'japanese', '政府観光局の町オワカの日本語ページ。Main Road等の原住所と参照点を照合。'),
    '6208495': ('タパヌイ', 'https://www.newzealand.com/jp/tapanui/', 'japanese', '政府観光局の町タパヌイの日本語ページ。Northumberland Street等の原住所と参照点を照合。'),
    '2063591': ('ペネショー', 'https://www.australia.com/ja-jp/places/adelaide-and-surrounds/guide-to-kangaroo-island.html', 'japanese', '政府観光局がPenneshawと日本語名を対記。カンガルー島のSA住所を照合。'),
    '4989605': ('コーペミッシュ', MI, 'pronunciation', '州の地名発音資料 Copemish。Village Hall、1st St、MI 49625等の原POI住所を照合。'),
    '6085582': ('ネイカム', 'https://www.straight.com/arts/741906/time-i-bombed-ivan-decker-gets-no-love-middle-nowhere-saskatchewan', 'pronunciation', '当地で公演したIvan Decker本人の記事の発音説明。政府・公式日本語資料ではない。SKのCentre St等の住所を照合。'),
}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, value):
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    report = read(WORK/'address-name-review.json')
    evidence = {p['peak']: p for p in report['items']}
    inputs = read(WORK/'next-translation-input.json')['items']
    models = {x['id']: x for x in read(WORK/'next-translation-qwen35-9b.json')['items']}
    old = [x for x in read('docs/unnamed-world-batch6-review.json')['items'] if x['decision']=='hold']
    approvals = read('docs/unnamed-world-name-approvals.json')
    existing = {x['peak'] for x in approvals['items']}
    decisions = []
    added = 0
    for group, rows in [('new_candidates', inputs), ('previous_holds', old)]:
        for row in rows:
            ident = row['id'].split(':')[1]
            model = models.get(row['id']) if group=='new_candidates' else row
            if group=='new_candidates':
                assert model is not None
                for k in ['original', 'country', 'lon', 'lat', 'peak_keys']:
                    assert row[k]==model[k], (row['id'], k)
            item = dict(id=row['id'], original=row['original'], country=row['country'],
                        peak_keys=row['peak_keys'], group=group,
                        model_ja=model.get('ja', model.get('model_ja')), evidence=[])
            for peak in row['peak_keys']:
                p = evidence[peak]
                c = p['candidates'][0]
                assert (c['id'], c['name'], c['country'], c['lon'], c['lat']) == (
                    ident, row['original'], row['country'], row['lon'], row['lat'])
                assert p['status']=='candidate_supported'
                assert c['support_share']>=.85 and c['supporting_pois']>=6 and c['distance_m']<=1000
                assert p['distinct_coordinates']>=4 and p['with_address']>=4
                item['evidence'].append(dict(peak=peak, reference=c,
                    near_pois=p['near_pois'], with_address=p['with_address'],
                    distinct_coordinates=p['distinct_coordinates'], locality_counts=p['locality_counts'],
                    samples=[{k:s.get(k) for k in ['fsq_place_id','name','address','locality','region','country']}
                             for s in p['samples'][:3]]))
            item['address_identity_rechecked']=True
            if ident not in CONFIRMED:
                item.update(decision='hold', reason='住所・参照ID・国・座標の対応条件は再検証済み。現地の読みまたは公的日本語名の個別確認は未完了。モデル候補は採用しない。')
                if group=='previous_holds' and ident in ['5832055','5489619']:
                    item['research_urls']=['https://travelwyoming.com/places-to-go/cities/meeteetse/'] if ident=='5832055' else ['https://www.newmexico.org/places-to-visit/scenic-byways/mesalands/']
                    item['reason']='観光局で対象の地域は確認。公的ページから文字での発音は確定できず保留。第三者の綴り読みだけでは採用しない。'
            else:
                ja, url, kind, note = CONFIRMED[ident]
                item.update(decision='adopt', ja=ja, source_url=url, source_kind=kind, reason=note)
                for peak in row['peak_keys']:
                    assert peak not in existing
                    c = evidence[peak]['candidates'][0]
                    choice = dict(peak=peak, ref=c, ja_editorial=ja, batch=7,
                        policy='address_review_85', reviewed_by='Codex',
                        review_note=note, model='qwen3.5:9b', model_ja=item['model_ja'])
                    choice['japanese_source_url' if kind=='japanese' else 'pronunciation_source_url']=url
                    choice['pronunciation_review_note']=note
                    approvals['items'].append(choice)
                    existing.add(peak)
                    added += 1
            decisions.append(item)
    assert len(decisions)==len(inputs)+len(old)
    summary = dict(candidate_references=len(inputs), candidate_peaks=sum(len(x['peak_keys']) for x in inputs),
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in decisions if x['group']=='new_candidates' and x['decision']=='adopt'),
        previous_holds=len(old), resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in decisions),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in decisions),
        added_total=added, published_total=len(existing), unnamed_remaining=5356-len(existing))
    save('docs/unnamed-world-batch7-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='全228峰の住所条件・候補同一性を再検証。採用15名だけ外部の表記・読み資料を確認。保留は読みの確定を意味しない。行政境界やPOI位置品質全件の保証ではない。', items=decisions))
    save('docs/unnamed-world-name-approvals.json', approvals)
    queue = read(WORK/'remaining-review-queue.json')
    queue['items']=[p for p in queue['items'] if p['peak'] not in existing]
    queue['remaining']=len(queue['items'])
    queue['priority_counts']=dict(Counter(str(p['priority']) for p in queue['items']))
    assert queue['remaining']==5356-len(existing)
    save(WORK/'remaining-review-queue.json',queue)
    print(json.dumps(summary,ensure_ascii=False))


if __name__=='__main__':
    main()
