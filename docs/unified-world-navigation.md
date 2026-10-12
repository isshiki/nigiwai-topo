> 2026-10-11更新：世界の表示名は接尾辞なし・日本語辞書接続・同名の代表1件へ変更。最新の仕様と714条件の検証は[世界の名称修正](world-display-names.md)を参照。以下の旧仕様・検査結果は変更前の記録を含みます。

# 世界共通画面の地域と駅参照（2026-10-11）

世界v2の密度を唯一の表示データとして、地域選択は移動範囲を指定する。日本専用の旧計算に切り替えない。タイトルは「にぎわいの地形図【世界版】」、業種すべて・σ200mで共通。

世界・6大陸・175の国と地域を用意。日本を選ぶと9地方・47県の追加選択が現れる。全域は選択した地方・県の範囲へ移動。国の境界ボックスはNatural Earth 1:110mを使用し、小国の欠落と日付変更線付近の広い範囲がある。国別行政領域への包含判定や世界すべての国・自治体の網羅を意味しない。ランキングは常に現在の地図表示範囲の上位20峰。

日本N02の9,046駅グループを検索・参照点に再接続。韓国はGeofabrik South Korea OSM PBFから現役のrailway=station/haltのnode/wayを取得、近接・同名駅をまとめ1,249グループ。1,153グループにOSM name:jaがあり、未登録は現地名を維持。wayは平均座標。最寄り駅を測地距離で照合し、1.5km以内の世界峰1,007点に「駅付近」を付与する。密度・峰座標・元の名前と参照IDは不変。座標と元参照IDが一致する峰だけ画面上で補完する。

ソウル首都圏 bbox [126.5,37.1,127.3,37.9]、800件/km²以上の上位20点は、広域名6種類から駅名20種類に分かれる。これは固定範囲の実データ検査であり、画面の任意範囲で重複ゼロを保証しない。同じ駅周辺に複数峰があれば同名になる。駅名は商圏名の確定ではない。他国の駅参照と韓国名のカタカナ統一も未完了。

一部駅のカタカナは韓国観光公社・ソウル市の日本語資料で確認。OSMのカタカナ＋漢字括弧はカタカナを採用。漢字名・現地名が残る駅もある。

- https://japanese1.visitkorea.or.kr/jpn/SHP/SH_JPN_1_6.jsp
- https://english1.visitkorea.or.kr/e_book/access/ecatalogt.jsp?Dir=914&callmode=normal&catimage=&eclang=ko&start=132&um=s
- https://japanese.seoul.go.kr/wp-content/uploads/2026/03/2026_guidebook_JP.pdf

## 再現

Natural Earth原本を data/raw/world-names/countries.geojson、Geofabrik PBFを data/raw/world-names/kr-stations/south-korea.osm.pbf に保存。出典・ライセンスは web/licenses/World-Names-NOTICE.txt、PBF SHA256は抽出manifestに記録。日本の既存regions/stationsと世界v2配信データが必要。

```powershell
.venv/Scripts/python.exe scripts/build_world_regions.py
.venv/Scripts/python.exe scripts/extract_korea_station_names.py
.venv/Scripts/python.exe scripts/build_world_station_labels.py
$env:NIGIWAI_TEST_WORLD_FOLDER='foursquare-world-v2'
$env:NIGIWAI_PUBLIC_WORLD='1'
node tests/world_area_check.cjs
node tests/peak_locality_names_check.cjs
.venv/Scripts/python.exe scripts/package_pages.py --data-url https://re.masahiko.info/nigiwai-topo/japan/2026-09-15/ --config web/config.js
```

新規辞書は画面パッケージに同梱。密度PMTilesのS3再アップロードは不要。Pagesは未公開。

## 検証結果

ブラウザで日本→東京都→渋谷の検索、世界入力101,729,099件の維持、韓国→ホンデイック検索と個別駅名ランキング、国変更時の日本用追加選択の非表示を確認。コンソールerror 0。実データ319,885峰の検査で既存6峰＋韓国1,007峰だけを補完し、密度・座標・原本が不変、元参照IDの不一致では補完しないことを確認。画面パッケージ5,207,142 bytes。検証画像はdata/validation/unified-japan-regions.png、unified-korea-names.png。
