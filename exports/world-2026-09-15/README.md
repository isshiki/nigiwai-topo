# 世界の登録密度CSV

[全峰CSV（23,187行、約1.71MB）](https://github.com/isshiki/nigiwai-topo/raw/refs/heads/main/exports/world-2026-09-15/world-peaks.csv)／[地名ごとの代表峰CSV（14,563行、約1.08MB）](https://github.com/isshiki/nigiwai-topo/raw/refs/heads/main/exports/world-2026-09-15/world-place-representatives.csv)

世界全体の計算結果から、公開条件の全業種・σ200m・800件/km²以上に合う峰を収録。トップ20に限定しない。極域まで完全に網羅するものではない。

| 列 | 内容 |
| --- | --- |
| 地名 | アプリと同じ日本語表示名。近くの駅・街などを参考にした峰名 |
| 登録密度_件_per_km2 | ガウス平滑化した山頂の登録密度。店舗数ではない |
| 緯度 | 峰の緯度、WGS84、十進度 |
| 経度 | 峰の経度、WGS84、十進度 |

全峰版は同じ地名の複数の峰を残す。代表峰版は世界全体で同じ表示地名の最高密度1件を残す。画面のランキングは表示範囲内で集約するので、代表峰CSVとは範囲と結果が異なり得る。

- 入力データ日付：2026-09-15。公開密度データv6を元に生成。
- UTF-8 BOM、カンマ区切り、改行CRLF。密度と座標は数値として読める。密度は元の値を保持し、区切りのカンマは挿入しない。
- 同じ出典の登録の集まりを比較する参考資料。施設の規模、人出、売上、購買力、商圏境界を示さない。
- 閉店判明分と位置品質の計算保留は除外。ただし営業状況・位置・重複・地名の読みを全件検証したものではない。
- 800未満の峰は含めない。CSVに地点がないことは、その地域に店舗がないという意味ではない。
- 地図上の▲の座標で、駅入口や参照地名の中心ではない。
- 代表峰版は都市別の総POI数ではない。国ごとの登録偏りがあるため実際のにぎわいの国際順位には使わない。

## 出典と利用条件

- 密度の元データ：© 2026 Foursquare Labs, Inc.、Foursquare OS Places、Apache 2.0。[NOTICE・加工内容](../../web/licenses/Foursquare-NOTICE.txt)／[ライセンス全文](../../web/licenses/Apache-2.0.txt)。
- 表示名はGeoNames（CC BY 4.0）、国土数値情報（CC BY 4.0）、OSM（ODbL）、Wikidata（CC0）、Natural Earth（public domain）、JMnedict（CC BY-SA 4.0）などの参照・編集表記を使用。[名称NOTICE](../../web/licenses/World-Names-NOTICE.txt)／[OSM NOTICE](../../web/licenses/OSM-NOTICE.txt)／[JMnedict採用エントリ](../../web/licenses/JMnedict-extract.json)／[JMnedict利用条件](https://www.edrdg.org/edrdg/licence.html)。名称はすべてが公式な日本語表記ではない。
- CSVを再利用する際も出典・加工の説明と該当の利用条件を保持する。背景タイルや個別POIの名称・住所はこのCSVに含まない。

## 再現・検証

プロジェクトルートから`node scripts/export_world_csv.cjs`。Git管理外の`data/distribution/foursquare-world-v6`と画面の表示辞書が必要。

全319,883峰を走査。条件に合う全峰23,187件、代表14,563件。全行の有限数値・座標範囲・800以上・地名欠損なし・禁止接尾辞なし・峰座標重複なしを検証。ファイルの行数・バイト数・SHA256は[metadata.json](metadata.json)。
