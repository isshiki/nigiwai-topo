"""Record source-specific follow-ups without publishing unsupported names."""
import json
from pathlib import Path


def main():
    prior = json.loads(Path('docs/unnamed-world-batch250-review.json').read_text(encoding='utf-8'))
    rows = [x for x in prior['items'] if x['decision'] == 'hold']
    updates = {
        '2984257': {
            'note': '第251回：内務省BANATICのImpasse du Marché・21290 Recey-sur-Ourceを再確認。Nénufarの利用案内は固有名詞記事を検索できると説明するが、対象町の記事・1925年版の発音凡例は取得できていない。Aux lecteursは歴史資料への注意書きであり発音凡例ではない。Larousse画像の部分表記[sé]を全名のIPAに拡張せず、保留を維持。',
            'urls': ['https://www.banatic.interieur.gouv.fr/intercommunalite/242100279-sivom-de-recey-sur-ource', 'https://nenufar.huma-num.fr/mode-demploi/', 'https://nenufar.huma-num.fr/aux-lecteurs/'],
            'next': 'Nénufarの対象固有名詞記事を取得し、同版の凡例または独立した全名の読みと照合する。章冒頭の再取得は不要。',
        },
        '5073930': {
            'note': '第251回：Collins辞書のNiobrara本文を直接確認。米国英語の表記はnaɪəˈbrɛrəで、定義は川。従来の川旅行記事のnigh-oh-BRAH-rahとは強勢母音の表記が異なる。村の読みの直接根拠とはしない。ネブラスカ州歴史協会は町がNiobrara川とMissouri川の合流点近くで創設され、その後移転したと説明するが発音を明示しない。既存図書館住所照合は維持し、ニオブララというモデル候補は未採用。',
            'urls': ['https://www.collinsdictionary.com/us/dictionary/english/niobrara', 'https://history.nebraska.gov/niobrara-a-town-too-tough-to-stay-put/', 'https://niobrarane.com/history/'],
            'next': '村に対応する発音資料を探す。川の辞書と旅行記事の母音差を解決せず、村へ自動転用しない。',
        },
        '5844167': {
            'note': '第251回：峰46.943,-119.990の周辺住所Parquet全39件を再取得。401 South MainはChevron、Texacoに加えAlbertsons、ACME Markets、Carrsでも共有される。店舗の実在・位置の個別確認前には独立した裏付けとしない。原Blustery\'s 301 Main St、Vantage Coffee Co. 321 Vantage Hwyを新しい照合対象として抽出。州立公園公式は4511 Huntzinger Road Vantage WAと明記するが、その施設は今回の周辺原POIにないため同施設住所一致とはしない。Cambridge発音ページ本文は403で未取得、回避取得は行わない。地名採用と店舗削除は保留。',
            'urls': ['https://parks.wa.gov/find-parks/state-parks/ginkgo-petrified-forest-state-park', 'https://www.visitvantage.com/', 'https://dictionary.cambridge.org/us/pronunciation/english/vantage'],
            'next': 'Blustery\'sとVantage Coffee Co.の運営者住所を照合し、401 South Mainの複数ブランドの実在と重複を別に監査する。',
        },
    }
    for item in rows:
        ident = item['id'].split(':', 1)[1]
        if ident not in updates:
            continue
        update = updates[ident]
        item['research_history'] = item.get('research_history', []) + [dict(batch=251, date='2026-10-12', **update)]
        item['reason'] = update['note']
        item['research_urls'] = update['urls']
        item['external_research_batch'] = 251
        item['next_research_lead'] = update['next']
    summary = dict(prior['summary'])
    summary['individually_researched_held_references'] = len(updates)
    assert sum(len(x['peak_keys']) for x in rows if x['group'] == 'new_candidates') == 45
    assert sum(x['group'] == 'previous_holds' for x in rows) == 25
    approvals = json.loads(Path('docs/unnamed-world-name-approvals.json').read_text(encoding='utf-8'))
    assert len(approvals['items']) == len({x['peak'] for x in approvals['items']}) == 831
    result = dict(snapshot=prior['snapshot'], summary=summary,
                  policy='対象地の住所・読みを別に照合。一般語や同名の川の読みを確定地名とせず、位置品質の疑義は削除と区別する。', items=rows)
    Path('docs/unnamed-world-batch251-review.json').write_text(json.dumps(result, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False))


if __name__ == '__main__':
    main()
