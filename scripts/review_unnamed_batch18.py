"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'6051792': ('リガル', 'https://en.wiktionary.org/wiki/Legal', 'WiktionaryのLegal個別項目の発音/lɪˈɡæl/と当該カナダの町の語義を確認。所在地資料https://www.legal.ca/experience/local-tourism/historyと原POIのAB、57/65件支持、57425 Range Rd 253、参照540mを照合。辞書発音の日本語編集音写であり、現地音声確認済みや公的日本語名ではない。モデル候補の機械採用ではない。'), '6084170': ('マンデア', 'https://en.wiktionary.org/wiki/Mundare', 'WiktionaryのMundare個別項目の発音/mʌnˈdɛɹ/と当該カナダの町の語義を確認。所在地資料https://www.mundare.ca/と原POIのAB、48/51件支持、町役場5128 50 Stと公式住所一致、参照717mを照合。辞書発音の日本語編集音写であり、現地音声確認済みや公的日本語名ではない。モデル候補の機械採用ではない。'), '6157721': ('ストートン', 'https://en.wiktionary.org/wiki/Stoughton', 'WiktionaryのStoughton個別項目の発音/stoʊtən/と当該カナダの町の語義を確認。所在地資料https://www.stoughtonsk.ca/と原POIのSK、63/64件支持、304/315/316 Main St、町役場232 Main Street、参照669mを照合。辞書発音の日本語編集音写であり、現地音声確認済みや公的日本語名ではない。モデル候補の機械採用ではない。'), '6078487': ('モレル', 'https://en.wiktionary.org/wiki/Morell', 'WiktionaryのMorell個別項目の発音/mɒˈɹɛl/と当該カナダの町の語義を確認。所在地資料https://morell.ca/と原POIのPE、36/39件支持、29 Park St・7710 St Peters Rd、公式所在地12 Sunset Crescent、参照556mを照合。辞書発音の日本語編集音写であり、現地音声確認済みや公的日本語名ではない。モデル候補の機械採用ではない。'), '5921077': ('シェティキャンプ', 'https://en.wiktionary.org/wiki/Ch%C3%A9ticamp', 'WiktionaryのChéticamp個別項目の発音/ʃɛ.tɪ.kæmp/と当該カナダの町の語義を確認。所在地資料https://novascotia.com/explore-by-region/cape-breton-island/cheticamp/と原POIのNS、47/55件支持、15122 Cabot Trail Rd・15250 Main St、Cape Breton西岸の町、参照894mを照合。辞書発音の日本語編集音写であり、現地音声確認済みや公的日本語名ではない。モデル候補の機械採用ではない。')}
RESEARCHED_HOLDS = {'5934031': ('辞書Cupar項目はSaskatchewanを含むがクーパー型の読み。一方、現地の匿名投稿はcup型と説明しており、食い違いは未解決。辞書の町語義だけで現地差を無視せず保留。', ['https://en.wiktionary.org/wiki/Cupar', 'https://www.rootschat.com/forum/index.php?topic=846420.9'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch17-review.json')
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
        item['address_rechecked_batch']=18
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=18)
            continue
        ja,url,note = CONFIRMED[ident]
        found.add(ident)
        item.update(decision='adopt', ja=ja, source_url=url,
            source_kind='pronunciation', reason=note,
            japanese_label_type='editorial_transliteration')
        for peak in item['peak_keys']:
            assert peak not in existing, 'Already published; refusing duplicate approval'
            approvals['items'].append(dict(peak=peak, ref=evidence[peak]['candidates'][0],
                ja_editorial=ja, batch=18, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=193, previous_holds_before=64,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==18} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch18-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='未反映257件の住所条件を再検証。カナダの町を明示した発音辞書項目と所在地資料を照合した5峰を編集表記として採用。Cuparの発音の食い違いは未解決で保留。残りの調査は未完了。',items=rows))
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
