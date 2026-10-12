"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'5906055': ('ボストンバー', 'https://ameblo.jp/shiki-87/entry-10884925376.html', 'バンクーバー在住者の実際のBC州ドライブ記録がBoston Barをボストンバーと対記。米国Bostonの酒場や弁護士協会の訳とは区別。原POI22/24件のBoston Bar住所、BC・47585 Trans Canada Hwy・Fraser Canyon Mobile Home & RV Parkを照合、参照距離946m。日本語の現地訪問者表記を採用する編集名で、公的日本語名や音声確認済みとは扱わない。')}
RESEARCHED_HOLDS = {'6155718': ('カナダ議会の委員会記録でSt. Brieuxはフランス語本来の読みと現地の読みが異なると明言。文字記録は具体的な音韻を示さず、フランスのSaint-Brieucの読みをそのまま適用しない。SKの住所対応は充足するが保留。', ['https://www.ourcommons.ca/documentviewer/en/41-1/PROC/meeting-69/evidence']), '5934031': ('SaskatchewanのCuparについて匿名地域投稿はスコットランドCuparのcoopとは異なるcupと説明する。出典の信頼性と町の具体的な読みがまだ十分でなく、英国の読みを流用せず保留。', ['https://www.rootschat.com/forum/index.php?topic=846420.9']), '5951004': ('BC観光局と題されたパンフレットの転載でフェアモントホットスプリングス表記と95号線・コロンビア川の位置対応が見つかった。ただし原発行サイト・版の一次確認が未完了。宿泊予約サイトだけで確定せず保留。', ['https://paperzz.com/doc/6094769/bc%E5%B7%9E%E8%A6%B3%E5%85%89%E3%83%A2%E3%83%87%E3%83%AB%E3%82%B3%E3%83%BC%E3%82%B9-%E3%83%91%E3%83%B3%E3%83%95%E3%83%AC%E3%82%B7%E3%83%88---%E3%83%96%E3%83%AA%E3%83%86%E3%82%A3%E3%83%83%E3%82%B7%E3%83%A5%E3%83%BB%E3%82%B3%E3%83%AD%E3%83%B3%E3%83%93%E3%82%A2%E5%B7%9E%E8%A6%B3%E5%85%89%E5%B1%80'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch15-review.json')
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
        item['address_rechecked_batch']=16
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=16)
            continue
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='pronunciation', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=16, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=195, previous_holds_before=65,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==16} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch16-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='未反映260件の住所条件を再検証。BC州の日本語現地訪問記録から1峰を採用。3地名の追加資料を確認して保留の理由を更新。残りの読みの調査は未完了。',items=rows))
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
