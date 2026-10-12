"""Publish individually researched local readings, retaining unresolved records."""
import json
from collections import Counter
from pathlib import Path

WORK = Path('data/name-research/unnamed-world')
CONFIRMED = {
 '6065271': ('マンコータ', 'https://books.google.com/books?id=VPwRAQAAIAAJ&pg=PA151', 'BillBarry著PeoplePlacesContemporarySaskatchewanPlaceNames2003の公開検索PA151でMANKOTA[manKOtuh]Village south of Kincaid on18を確認。PA4の著者説明は対象地を知る人の発音を実聴した場合に掲載すると明示。原頁画像や現代音声実聴を行ったとはしない。manKOtuhに基づくマンコータを編集音写として採用、公式日本語指定とは区別。州公式地名データHAKXEはManitobaとNorthDakotaから命名と確認。元4c745f7344d395214659f4be学校2401stAveと州2020選挙資料の一致、現学校公式2401stStreetEastの番地町一致と道路名差、公式リンクと原点約9m近接の既存照合を保持。今回学校公式現住所を再確認し、道路名差だけで誤位置とはしない。25/25地名支持、24住所、22座標、原密度位置不変。'),
 '5926991': ('カンサル', 'https://books.google.com/books?id=VPwRAQAAIAAJ&pg=PA55', 'BillBarry著PeoplePlacesContemporarySaskatchewanPlaceNames2003の公開検索PA55で対象町CONSUL[CONsul]Village southwest of Eastend on13/21を確認。PA4は対象地を知る人の発音を著者が実聴した場合に掲載すると明示。州公式地名データHAUWHも官職名由来を確認。対象発音表記と北米英語の母音対応に基づくカンサルを編集音写として採用、公式日本語表記・精密IPA・今回音声実聴と区別。一般名詞だけの発音で採用したのではなく対象町の読みを新たに確認。州観光局ManleyBreadandHoney105CentreStConsulを再確認し原0e8de7b179564708e73181a6と施設番地道路町を照合。14/15地名支持、15住所、7座標、参照487m、原密度位置不変。')
}
RESEARCHED_HOLDS = {
 '5896578': ('BillBarry2003公開検索PA21でBEAUVAL[boVAL]Northern village southeast of IlealaCrosse on165を確認。ボーヴァルという編集候補の対象地域の読み根拠を取得できたが、既存キャンプ郵送先と実所在地差および14施設の座標集中は未解決で名称反映保留。フランス動物園の発音を転用しない。', ['https://books.google.com/books?id=VPwRAQAAIAAJ&pg=PA21']),
 '5937747': ('BillBarry2003公開検索PA64でDENAREBEACH[dNAIR]Northern village southwest of Creighton on167を確認。編集候補デネアビーチの対象地域読み根拠を取得。州公式地名データHAFYCはDepartmentofNaturalResources各頭2文字由来を確認。14施設の座標集中と住所対応の未確定部分を残し名称反映保留。', ['https://books.google.com/books?id=VPwRAQAAIAAJ&pg=PA64'])
}



def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def save(path, obj):
    Path(path).write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')


def main():
    prior = read('docs/unnamed-world-batch351-review.json')
    rows = [x for x in prior['items'] if x['decision']=='hold']
    report = read(WORK/'address-name-review.json')
    evidence = {x['peak']:x for x in report['items']}
    approvals = read('docs/unnamed-world-name-approvals.json')
    existing = {x['peak'] for x in approvals['items']}
    assert not ({p for x in rows for p in x['peak_keys']} & existing), 'Prior report resurrected adopted peaks'
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
        if ident in CONFIRMED or ident in RESEARCHED_HOLDS:
            item['address_rechecked_batch']=352
        if ident not in CONFIRMED:
            if ident in RESEARCHED_HOLDS:
                note, urls = RESEARCHED_HOLDS[ident]
                item.update(reason=note, research_urls=urls, external_research_batch=352)
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
                ja_editorial=ja, batch=352, policy='address_review_85', reviewed_by='Codex',
                model='qwen3.5:9b', model_ja=item.get('model_ja'),
                pronunciation_source_url=url, pronunciation_review_note=note, review_note=note))
            existing.add(peak)
    assert found==set(CONFIRMED)
    summary = dict(candidate_peaks_before=20, previous_holds_before=3,
        adopted_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='adopt'),
        remaining_candidate_peaks=sum(len(x['peak_keys']) for x in rows if x['group']=='new_candidates' and x['decision']=='hold'),
        resolved_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='adopt' for x in rows),
        remaining_previous_holds=sum(x['group']=='previous_holds' and x['decision']=='hold' for x in rows),
        added_total=sum(len(x['peak_keys']) for x in rows if x['decision']=='adopt'),
        published_total=len(existing), unnamed_remaining=5356-len(existing))
    assert {x['id'].split(':')[1] for x in rows if x.get('external_research_batch')==352} == set(RESEARCHED_HOLDS)
    summary['individually_researched_held_references'] = len(RESEARCHED_HOLDS)
    save('docs/unnamed-world-batch352-review.json', dict(snapshot=report['snapshot'], summary=summary,
        policy='自治体・施設運営者住所と元POIを照合。対象町の日本語学術・旅行用例を参考に編集表記を採用、公開検索本文と直接取得を区別。',items=rows))
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
