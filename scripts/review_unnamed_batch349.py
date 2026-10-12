"""Record new primary-source checks without altering unresolved names."""
import json
from pathlib import Path


def main():
    prior = json.loads(Path('docs/unnamed-world-batch348-review.json').read_text(encoding='utf-8'))
    rows = [x for x in prior['items'] if x['decision'] == 'hold']
    approvals = json.loads(Path('docs/unnamed-world-name-approvals.json').read_text(encoding='utf-8'))
    assert len(approvals['items']) == 877
    assert len(rows) == 24
    item = next(x for x in rows if x['id'] == 'GeoNames:2702619')
    sample = item['evidence'][0]['samples'][0]
    assert sample['fsq_place_id'] == 'c5da9cdd3655486ee7a14bf3'
    assert sample['address'] == 'Stationsv. 6'
    item['external_research_batch'] = 349
    item['reason'] = ('Bräcke自治体の2024-01-26選挙会場資料VN2024/9を公開PDF本文で確認。'
                      'Hotell Östjemten・Stationsvägen 6・Kälarneが元POIのホテル名とStationsv.6に一致。'
                      '所在地名の対応は補強できたが発音資料ではない。Nordisk familjebok第4版13巻'
                      '印刷163–164頁のKälarne個別項目を直接取得し、町と旧自治体を確認、音声表記なし。'
                      'Svensk uppslagsbokのJämtland地域方言説明も個別町名の発音ではない。'
                      'Riksarkivet書誌にCarl Lindberg「Kälarne」Jämten1934 pp177–193を確認したが'
                      '当該論文本文は未取得。人物Henry Kälarne、Gjurdの発音、近隣町の音声は転用しない。'
                      'モデルのカールネは根拠未確定のため保留継続。')
    item['research_urls'] = [
        'https://brackekommun.ondemand.formpipe.com/welcome-sv/namnder-styrelser/valnamnden/valnamnden/agenda/lokalerpdf?downloadMode=open',
        'https://runeberg.org/nffm/0098.html',
        'https://runeberg.org/svupps/2-15/0247.html',
        'https://riksarkivet.x-ref.se/theme/custom/pdfs/GCSuppl2B.pdf',
    ]
    item['next_research_lead'] = 'Carl Lindberg, Kälarne, Jämten 1934 pp177–193: 本文未取得、発音掲載も未確認。'
    summary = dict(candidate_peaks_before=20, previous_holds_before=4,
                   adopted_candidate_peaks=0, remaining_candidate_peaks=20,
                   resolved_previous_holds=0, remaining_previous_holds=4,
                   added_total=0, published_total=877, unnamed_remaining=4479,
                   individually_researched_held_references=1)
    out = dict(snapshot=prior['snapshot'], summary=summary,
               policy='今回新たに確認した資料の到達範囲を記録。未確定の読みは採用せず辞書・キューを変更しない。', items=rows)
    Path('docs/unnamed-world-batch349-review.json').write_text(
        json.dumps(out, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
