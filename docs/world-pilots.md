> 履歴・調査記録：旧仕様、当時の件数、未完了事項を含みます。現在の公開仕様・完了状態は[現在の状態](current-state.md)を参照してください。

# 海外3地域の試作

2026-10-06時点では日本全国に加え、シンガポール・ロンドン・レイキャビク周辺の有限範囲を表示できる。全世界・各国全域を収録した版ではない。画面のエリアで切り替え、選択エリアの地域行の「全域」で試作範囲へ戻る。

## データと方法

所有者が海外・世界版の取得にも既存トークンの読取利用を許可した。Foursquare Portalの読み取り専用カタログで日本版と同じ2026-09-15のPlaces/Categories snapshotを固定する。取得は無料のOS Placesで、有料Places APIを呼ばない。秘密値・接続SQL・署名付きURLを保存・表示しない。

地域中心のLAEA、共通100m格子、50km区画、σ200/400/800m。入力には最大σの4倍＋550m=3,750mの余白を付け、国のコードで切らない。日本用LAEAは海外に流用しない。出力の段彩・等高線・峰は試作範囲で切り出す。表示範囲外が透明でも施設がないという意味ではない。

海外の業種はFoursquareの上位分類を使う。Dining and Drinking=飲食、Retail=買い物、Business and Professional Services/Health and Medicine=サービス。複数区分は飲食→買い物→サービスの順で1区分にする。その他は「すべて」にだけ含める。日本の既存飲食・買い物は従来の名称分類を維持しているため、業種別の国際比較にはこの分類差もある。

名前は[OSMの駅・都市・地区](world-names.md)。駅が1.5km以内なら駅名、遠ければ都市・地区の参考名に「付近」、名前がなければ座標。OSMの参照時点とFSQのsnapshotは別に記録する。駅のないレイキャビクも都市・地区名で検索できる。

## 実測

|地域|取得数（余白・閉店分含む）|閉店除外後の入力|試作範囲内の入力|200m・全業種の峰|配布一式|
|---|---:|---:|---:|---:|---:|
|シンガポール周辺|515,137|469,915|417,151|316|3,198,878 bytes|
|ロンドン周辺|822,276|702,336|647,991|999|8,712,855 bytes|
|レイキャビク周辺|13,902|13,244|13,033|35|257,318 bytes|

各地域4業種×3σ=12条件、海外計36条件。3地域合計12,169,051 bytes（約12.2MB）、PMTiles36個合計5,335,127 bytes、1,988タイル。原本と中間GeoJSONはこの配布量に含めない。残りは峰JSON、分割索引、駅・地名と出典。全世界の容量予測としてこの都市密度を一律に外挿しない。

実際のHTTPSで初期JSON（manifest・駅・地名・200m全業種の峰索引と最初の区画）を取得した転送量はシンガポール519,607 bytes、ロンドン738,229 bytes、レイキャビク51,232 bytes。PMTiles、背景、ライブラリは含めない。これはヘッダーやブラウザキャッシュ・圧縮を含む完全なページ転送量ではない。

入力の一意ID、件数、閉店数、ハッシュを照合。22,529形状を検査し、全地域で有効かつ出力範囲内。各12条件×20範囲×3表示下限の計2,160検索で、分割索引トップ20が全件検索と一致。地域中心・辺・角での東西/南北1kmのサンプル距離誤差は最大0.000732%未満。正積投影であることに加え、これら小範囲での距離歪みを確認したもので、世界全体の保証ではない。

元データの取得と形状生成時の修正も再現処理に反映した。Unicode改行文字が施設名に含まれるJSONLを物理行単位で読む。座標丸めによる接触穴は形状を修復してから範囲と交差させる。800件/km²の概観がない条件でも、拡大時の100件/km²以上の詳細を配信する。

## 配信と画面

日本は既存の `nigiwai-topo/japan/2026-09-15-v2/`。海外は `nigiwai-topo/pilots/<region>/2026-09-15-v1/` に配置済み。バケットremasahikoと既存CloudFront `re.masahiko.info` を利用し、AWS設定と日本の配布一式を変更していない。全36条件のHTTPS Range/CORS/ETag/ヘッダーバイトとOPTIONS、峰索引JSONのCORS・順位を確認した。

地域別manifestの `peaks_index` が指定される場合、画面は峰全件ファイルを読み込まない。完全に表示内に入る索引区画は上位100の要約を使用し、画面端に交差する区画は葉まで検索する。トップ20は全件検索と同じ密度順位。名称の同順位は並びが変わる場合がある。表示ラベルも上位候補から衝突回避で間引く。日付変更線をまたぐ表示範囲は2つに分割する。JSON要求は同時4件、索引キャッシュは128区画、切り替え・移動中の古い結果は画面に適用しない。日本版は現在の峰全件JSONを継続している。

日本は地理院の淡色地図、海外試作はOSM標準ラスターを透過表示する。出典は常時表示し、OSM参照表と加工表示はODbL、密度はFSQのApache 2.0/NOTICEを保持する。ブラウザは通常の表示範囲だけの背景取得を行い、事前取得はしない。[OSMタイル利用方針](https://operations.osmfoundation.org/policies/tiles/) に従い、一般公開を拡大する前に背景配信の容量・利用条件を満たす方式を決める。`worldRaster` で取得先を設定できるが、提供元を変える場合は出典も合わせて変更する。

エリア切り替え、背景と出典、表示範囲トップ20、駅なし都市検索は、実データを使ったDOM/MapLibreのテスト代替で確認。実ブラウザの操作・見た目は現在の操作制限により未検証。localhostの画面・設定・スクリプトはHTTP200を確認した。Pagesパッケージは約46.8KB、作成のみでGitHub Pagesには公開していない。

## 再現

```powershell
# .envのトークンを利用。他プロジェクトを読む場合は所有者の明示許可が前提。
uv --cache-dir data/cache/uv run scripts/fetch_world_names.py
foreach ($pilotId in @('sg-singapore','gb-london','is-reykjavik')) {
  uv --cache-dir data/cache/uv run scripts/fetch_foursquare.py --pilot $pilotId
  uv --cache-dir data/cache/uv run --offline scripts/world_pipeline.py --region $pilotId
  uv --cache-dir data/cache/uv run --offline scripts/build_pmtiles.py --input "web/data/foursquare-$pilotId" --output "data/distribution/foursquare-$pilotId"
  uv --cache-dir data/cache/uv run --offline scripts/validate_pmtiles.py --input "data/distribution/foursquare-$pilotId" --original "web/data/foursquare-$pilotId"
}
uv --cache-dir data/cache/uv run --offline scripts/validate_world.py
uv --cache-dir data/cache/uv run --offline python -m unittest discover -s tests
node tests/area_switch_check.cjs
node scripts/validate_peak_delivery.cjs
```

publish_data.pyに `--input`、`--original`、`--prefix`、`--data-url`、`--skip-package` を指定する。通常は計画のみで、実行時に `--upload` を追加する。既存プレフィックスへの上書きは拒否する。複数エリアの画面をまとめるときは次を使う。

```powershell
uv --cache-dir data/cache/uv run --offline scripts/package_pages.py --data-url https://re.masahiko.info/nigiwai-topo/japan/2026-09-15-v2/ --config web/config.js
```

## 次の段階

大きな国は都市試作の範囲をそのまま巨大化せず、区画ごとに取得・計算・配信する。今回の原本と参照表は小規模試作用の地域単位で、世界全件をメモリに持つ設計にはしない。隣り合う地域の投影・格子の整合と継ぎ目、日付変更線の密度形状の分割、極域、国/行政区域の選択、背景配信を実装・検証する。現在は日付変更線の検索範囲・区画bboxを扱うが、実データの密度形状が日付変更線をまたぐケースはまだ未検証。

突出度、σとしきい値の感度、日本の経済センサス比較、記事の方法と限界も残っている。GitHub Pagesの公開は世界版を仕上げてから行う。
