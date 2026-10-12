"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {}

RESEARCHED_HOLDS = {'2263276': ('第260回：政府観光局VisitPortugal日本語本文のSão Martinho do Portoにサン・マルティーニョを直接確認。ただし別町の共通語部分であり当地全名の公的日本語指定ではない。ホテル団体UnitedHotelsの公開検索PDF本文にはAmoreirasのアモレイラス表記。編集案サン・マルティーニョ・ダス・アモレイラスを得たが住所品質を再検査。2006年官報のFarmácia Vargues LadeiraはRua do Cruzeiro1で原POIのRua Dr.António Calapez Gomes Garcia1と街路不一致。自治体2023店一覧PDF2頁のMinimercado de Dulcina DuarteはLargo Adelino Ribeiro da Costa3で原Loja DulcinaのLargo Adelino Amaro da Costaと相違。誤記・改称・移転を断定しない。Monte Maravilhas運営者公式contact本文のGPS37度38分36秒N/8度23分46秒Wを確認し原POI37.651361521885,-8.40422399374588との球面距離1143mを再計算。原位置は同一施設の公式位置から約1.1km離れる。外部資料で地域名は支持されるが峰の付近の独立施設位置の確認には足りず保留。単に全語録音を待つ状態から、住所・位置の不一致の解決へ調査方針変更。表示追加0、密度・座標不変。', ['https://www.visitportugal.com/ja/content/praia-de-sao-martinho-do-porto', 'https://www.unitedhotels.pt/uhpjp.pdf', 'https://files.diariodarepublica.pt/2s/2006/07/138000000/1177111772.pdf', 'https://www.cm-odemira.pt/cmodemira/uploads/document/file/21719/lojas_aderentes_2023.pdf', 'https://www.montemaravilhas.com/contact/'])}


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch259-review.json')
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
        item['address_rechecked_batch']=260
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=260)
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
                ja_editorial=ja, batch=260, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=40, previous_holds_before=24,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==260} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch260-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='共通語の日本語表記と原POIの施設・住所・公式座標を再検証。不一致を同一扱いせず保留。',items=rows))
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
