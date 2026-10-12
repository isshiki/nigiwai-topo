# サービス業種の追加

Foursquareの固定Categories snapshotの上位分類 `Business and Professional Services` と `Health and Medicine` をサービス区分にする。理美容、クリーニング、修理、金融、不動産、専門業務、医療などを含む。分類には事務所・製造業・工場も含まれるため、生活サービスだけの密度ではない。

複数カテゴリを持つ施設は飲食、買い物、サービスの順に採用し、追加取得内では一意IDを重複させない。飲食と買い物の既存地図は従来の名称の部分一致による分類を維持する。例えば `Barber Shop` は旧分類で飲食になり得たが、今回のサービス分類では上位階層を優先してサービスになる。このため従来の業種地図とサービス地図に一部重複があり、業種別件数の合算はできない。「すべて」は元々これらの施設を含む。

既存の全国トークン利用許可の範囲で、同じ2026-09-15 snapshotから日本国内のサービス該当施設だけを取得する。既存原本はカテゴリIDを保持していないため、`other` をそのままサービスと読み替えない。取得件数と一意ID、原本ハッシュを検証し、閉店判明分を除外する。

```powershell
uv --cache-dir data/cache/uv run scripts/fetch_foursquare.py --national --service-only --env-file C:/Projects-GitHub/geoai-open-lab/.env
uv --cache-dir data/cache/uv run --offline scripts/build_service.py
```

トークンの読取は所有者の許可が前提。通常はプロジェクトの.envを使用する。取得は `data/raw/foursquare-japan-service`、中間生成は `web/data/foursquare-japan-service`。σ200/400/800mの密度・等高線・峰を作り、N02/N03で命名して既存9条件に追加し、全12条件を検証する。配布先へのアップロードは別操作で、既存版を上書きせず新しい版のプレフィックスを使う。GitHub Pagesの公開は世界版完成後。

## 生成結果（2026-10-06）

取得1,148,842件、閉店判明38,108件、計算入力1,110,734件。一意ID数と取得数を照合済み。σ200mは5,573峰、400mは1,643峰、800mは409峰（いずれも検出下限50件/km²の局所最大点。画面の表示下限とは別）。地域選択・現在地・表示範囲トップ20は他業種と同じ処理を使用する。

全12条件の形状・峰リスト・PMTilesを検証済み。新規配信先は `https://re.masahiko.info/nigiwai-topo/japan/2026-09-15-v2/`。29ファイル38,432,830 bytes、PMTiles12個21,500,802 bytes。実HTTPSで全12条件のRange/CORS/ETagとヘッダー一致、OPTIONSを検証し、web/config.jsを切り替えた。旧v1の配信データは上書きしていない。画面のサービス選択が有効になる版であり、GitHub Pagesへの公開は行っていない。
