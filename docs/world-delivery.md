> 履歴・調査記録：旧仕様、当時の件数、未完了事項を含みます。現在の公開仕様・完了状態は[現在の状態](current-state.md)を参照してください。

# 世界既定条件の配信準備（2026-10-08、進行中）

最新（2026-10-10）：13峰の位置品質による計算保留を適用したv2をローカル生成・検証済み。13区画・12パッケージを変更し、2,935パッケージは旧版SHA256と一致。暫定峰319,885、概観3,604タイル・5,118,453 bytes。S3/CloudFrontのv2へ接続済み。7,052ファイル・394,293,518 bytesの一致とRange・CORSを確認。検証記録は `data/validation/world-v2-published.json`。[v2修正と配信手順](held-density-rebuild.md)。下記はv1の生成・配信履歴。

対象はσ200m・全業種だけ。94,976区画、3,431,162,970 bytesのGeoJSONを検査。非空17,922区画、段彩335,021、等高線343,621、初期峰326,352。座標丸めで長さ0になった等高線4本は描画不能な退化線として除外扱い。タイル変換時make_validでPointへ退化し、線レイヤには入らない。新規生成コードも丸め後に退化線を作らないよう修正。

各4×4区画（最大1.8度四方）を束ね、非空2,947パッケージを作成。区画一覧・サイズ・全形状・範囲・密度値・峰座標重複を検査した。峰の最終境界補正前のため、初期峰数は最終数ではない。段彩・等高線は境界補正によって再生成しない。

## 峰の補正と名称

初期生成は区画内部だけで局所最大を判定し、区画外により高い密度があると端の点を峰として拾う場合がある。repair_world_peaks.pyは端付近に峰のある区画を抽出し、共通格子を64セル広げて再評価する。補正結果はdata/world-build/peak-repairに保存し、原本の密度形状を変更しない。paddingが核心密度を変えないテストと、区画外の高い密度で仮の峰を除去できるテストを追加した。突出度による独立峰判定とは異なる。

GeoNames公式cities500.zipを取得し236,014都市・町村参照を準備。CC BY 4.0。[公式仕様とライセンス](https://download.geonames.org/export/dump/readme.txt)。取得済み日本N02/3試作OSM駅が1.5km以内なら駅名を採用し、その他はGeoNamesの15km以内の近隣都市・町村名に「付近」を付ける。世界の全駅は未取得。都市の所属区域判定ではない。参照データの時点はFSQ固定2026-09-15と異なる。日本語翻訳は行わない。識別子・出典・距離・根拠を峰属性に保持する。日付変更線を考慮した球面KDTree候補からWGS84測地線で近隣名を選ぶ。

## バックグラウンド処理

1. repair_world_peaks.pyが境界の峰を補正。
2. build_world_pmtiles.pyが2,947個の密度PMTilesを順番に作成。途中再開可能。
3. finalize_world_delivery.pyが上の2工程の完了を待ち、補正済み峰と地名をパッケージへ取り込み、峰JSON/索引/NOTICEを更新し、全配信データを検証する。既存の密度archiveは再利用する。

一回限りのプロセスで定期タスクではない。再起動後は手動再開が必要。待機工程は72時間で失敗として終了する。S3へのアップロードと画面変更はまだ行わない。

```powershell
Get-Content data/world-build/peak-repair/progress.json
Get-Content data/distribution/foursquare-world/progress.json
Get-Content data/world-build/peak-repair-error.log -Tail 10
Get-Content data/world-build/pmtiles-error.log -Tail 10
Get-Content data/world-build/finalize.log -Tail 10
Get-Content data/world-build/finalize-error.log -Tail 10
# 下は実行中でない場合の再開用
.venv\Scripts\python.exe scripts/repair_world_peaks.py
.venv\Scripts\python.exe scripts/build_world_pmtiles.py
.venv\Scripts\python.exe scripts/finalize_world_delivery.py
```

初回バレアレス付近の1パッケージを変換し、63タイル・78,105 bytes、ピークJSON一致、全タイル展開、MVT密度属性、低縮尺の段彩条件、FSQ NOTICEを検証した。validate_pmtiles.pyの日本9/12条件検査を維持し、worldのみ200/allの単一条件を許可した。world峰索引と名称NOTICEも配布物へ含める。

完了後にdata/distribution/foursquare-world/validation.jsonとregistry.jsonを保存する。世界の概観用タイル、表示範囲に応じたパッケージ切替、国・地域選択、他業種・σ400/800、全世界の駅参照の拡充、公開環境のHTTP検証は引き続き必要。配信準備完了はアプリ完成や公開済みを意味しない。GitHub Pages公開は世界版が整ってから。

Windowsの進捗JSON更新時に一時ロックでPermissionErrorが発生したため、原子的置換を最大8回再試行する修正とテストを追加。補正済み峰・変換済みarchive・SQLiteキャッシュを保持して再開した。稼働PIDはdata/world-build/delivery-processes.jsonへ記録する。
## 世界版画面への接続（2026-10-08）

境界補正・名称付与・2,947地域の配信用検証は20:00に完了。詳細PMTilesは211,202,591 bytes、178,380タイル、補正後の峰319,897件。

`scripts/assemble_world.py` が各地域のz3〜8を合成し、z0〜2を同じ形状から縮小した世界概観を作る。概観は5,121,102 bytes、3,616タイル（量子化で空になる透明タイル2枚を含む）。z0〜8は800件/km²以上の段彩を簡略表示、z9以降は現在の表示範囲に交わる地域PMTilesを読み込む。移動で不要な地域レイヤを破棄する。詳細のレイヤはz9〜24、元タイルはz12までで以後拡大表示。

全319,897峰を共通の4,095ノードへ索引化。全域、東京周辺、日付変更線越しのランキング上位20件が原本の全件検索と一致することをDOM/MapLibreの代替オブジェクトで検証。既存の日本・3試作の選択、背景、業種、ランキングも回帰検証した。ブラウザでの視覚確認は利用者が実施し、世界版の表示内容は問題なしとの確認を受けた。

世界エリアと6大陸の移動先を追加。世界版は200m・すべてだけを先行表示し、未生成の業種・幅は選択不可。山の名前検索は表示中の峰を候補とする。世界全都市の検索、国別の選択は未対応。世界の背景はOSM、名称はGeoNames・N02・取得済みOSM駅で、画面と配布物へ各出典を記載。日本語翻訳は引き続き保留。

ローカル: http://127.0.0.1:8820/?area=world&region=world
現在の世界dataBaseは `/tiles/foursquare-world/`。ローカルHTTPのmanifestと概観・詳細PMTilesの206 Range応答を検証した。日本・試作は従来のCDNを継続使用。

配信対象だけを `data/world-release/` へ集める `scripts/publish_world.py` を追加。原本GeoJSONや各地域の重複した峰JSON/索引をアップロードしない。アップロード対象は詳細・概観PMTiles、共通峰索引、manifest、regions、空のstations、NOTICE類。既存AWS方針を変更せず、新規prefix `nigiwai-topo/world/2026-09-15-v1/` を使用する。S3一覧と全ファイルサイズ、CloudFrontのRange・CORS・OPTIONSを検証する。

アップロード前のSTS確認でAWSセッション期限切れが判明し、S3への書き込みはまだ行っていない。`aws login --profile nigiwai-topo` で利用者が再認証後、次を実行し、成功時にweb/config.jsの世界dataBaseを `https://re.masahiko.info/nigiwai-topo/world/2026-09-15-v1/` に変更する。GitHub Pagesの公開は行わない。

```powershell
.venv\Scripts\python.exe scripts/assemble_world.py
.venv\Scripts\python.exe scripts/validate_world_frontend.py
node tests/world_area_check.cjs
.venv\Scripts\python.exe scripts/publish_world.py
```


## S3・CloudFront配信完了（2026-10-08）

利用者がAWSを再認証後、`publish_world.py` が全7,051ファイル・394,326,522 bytesのアップロードと検証を完了。S3一覧のファイル集合と全サイズがローカル配布物と一致。CloudFrontからmanifest・共通峰索引が一致し、概観と詳細PMTilesのRange GETが206と正しいPMTilesヘッダーを返すこと、Originに対するCORS、Rangeを指定したOPTIONS応答を検証した。

世界dataBaseは `https://re.masahiko.info/nigiwai-topo/world/2026-09-15-v1/` へ切替済み。config.jsのキャッシュ識別子も更新。上の再認証待ち・ローカル配信の記述はこの切替前の経過。検証記録は `data/validation/world-published.json`。画面・コードだけを含むPagesパッケージも更新するが、GitHub Pagesの公開は引き続き保留。
