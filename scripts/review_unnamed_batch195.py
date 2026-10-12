"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {'5886559': ('アーバーフィールド', 'https://www.campbellsoup.ca/fed-coop-promotion-rules/', 'Arborfield CA SK GeoNames5886559峰53.105,-103.662支持24/25=.96住所25独立座標19参照892m。原14b111eb556f4806469a3c17 BeelandCoOperativeAssociationLtd 1stAve Arborfield座標53.102870,-103.660886をCampbellCanada2024販促規約AppendixB BeelandCoopAssnLtd 1stAvenue ArborfieldSK S0E0A0に直接照合。同座標のArborfieldCardlock別名は独立証拠として重複計上しない。CMU arbor AA1 R B ER0とfield F IY1 L Dを使った構成語の編集音写アーバーフィールド。地名全体の辞書発音・当地実聴・公式日本語指定とは主張しない。英国同名地との命名由来の同一性も採用根拠にしない。元位置密度不変。')}
RESEARCHED_HOLDS = {'5983858': ('Irma原780dd8636f964102c44edb27 IrmaCooperativeAssociationLtd5005 50thStをCampbellCanada AppendixB同名5005 50thStreet IrmaABに直接照合。CMU人名irma ER1 M AH0を確認したが前回の人名言語差を解消する町名自体の読み資料ではないため保留。モデルイルマを自動採用しない。', ['https://www.campbellsoup.ca/fed-coop-promotion-rules/'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch194-review.json')
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
        item['address_rechecked_batch']=195
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=195)
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
                ja_editorial=ja, batch=195, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=79, previous_holds_before=31,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==195} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch195-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='Arborfield生協原住所とメーカー公開資料を照合。構成語編集音写を明記、Irma町名の読みは保留維持。',items=rows))
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
