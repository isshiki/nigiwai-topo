"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'3386002': ('トルスー', 'https://ciberduvidas.iscte-iul.pt/consultorio/perguntas/sobre-a-grafia-de-trucu-ceara-brasil/29574', 'BR CE峰-6.097,-39.740、支持16/18=.889、住所17、独立座標18、参照153m。原69b720574c6c8f1db13a89b0 Solon Guedes Cavalcante Eef、Francisco Teixeira de Padua S/N Vila Trussuを確認。自治体公式2026年6月11日記事は同名学校がTrussu地区にあると明記し、改修・拡張を説明（移転や番地一致は断定しない）。学校住所ディレクトリにも原住所とINEP23114304が一致。CiberdúvidasのCarlos Rocha2011年解説は対象Acopiara地区のTrussuをTruçuと対応させる。語源は専門家自身も未確定としており断定しない。IBGE自治体史の検索公開本文には対象旧地区Trussúの表記があり、末尾の強勢とss/çを参考に編集表記トルスーを採用。全語の当地録音・公的日本語名未確認。モデルのトラッスは不採用。Iguatu側の同名貯水池やRio Grande do SulのTuruçuと区別。密度・座標不変。')}

RESEARCHED_HOLDS = {}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch258-review.json')
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
        item['address_rechecked_batch']=259
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=259)
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
                ja_editorial=ja, batch=259, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=41, previous_holds_before=24,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==259} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch259-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='自治体の同名学校・地区と原POI住所を照合。対象地区の専門家の綴り解説と公的歴史表記を参考に編集音写。全語録音未確認を明記。',items=rows))
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
