> 履歴・調査記録：旧仕様、当時の件数、未完了事項を含みます。現在の公開仕様・完了状態は[現在の状態](current-state.md)を参照してください。

# 世界版の地形生成（進行中）

全世界原本は取得済み。閉店判明分を除き101,734,535件をactive.parquetへ分類した。飲食16,581,151、買い物15,933,486、サービス28,372,248、その他40,847,650。529,772種類の業種組合せを先に分類して結合する。検索用2度セルは5,733個、Web Mercator表示範囲外は8件。既存3試作の原本とID・座標・名称・業種ID・閉店情報まで一致した。

都市別LAEA格子を独立してつなぐ方法では、ロンドンの境界試験でσ200mの平均差2.10%、最大差10.87%を生じた。この方法は世界のモザイクに流用しない。実験実装global_density.pyは経度400,000区間、緯度200,000区間の共通格子を使う。赤道で約100m、経度方向は高緯度ほど細かい。WGS84測地線から行別の実距離と面積を求め、横カーネル・縦重み・件/km²変換を補正する。厳密な球面KDEではなく経線/緯線方向に分離した近似であり、局所LAEAと同一の計算とは主張しない。

共有辺の密度一致、日付変更線の周期入力、緯度0/51.5/80度の単一登録の中心密度が理論値の1%以内を3テストで確認。業種優先とセル端点の2テストも成功。既存3都市の各1区画でσ200/400/800の実データ等高線を生成し、全形状が妥当であることを確認した。峰の区画外近傍を使う境界判定と、登録数の保存性、追加緯度の品質検証は残る。突出度は未実装。

build_world_default.pyで既定200m・全業種をバックグラウンド生成中。occupiedセルと周辺を含む94,976区画。成果物はdata/world-build/default、ログはdata/world-build/build.logとbuild-error.log、進捗はdefault/progress.json。名前は座標の仮表示で名称参照は未接続。日本と3都市の既存配信を変更しない。保存済み区画は再利用するが、実装変更時には別出力先へ変更して混在を避ける。空き20GiB未満では停止する。

```powershell
.venv\Scripts\python.exe scripts/prepare_world.py --check-pilots
.venv\Scripts\python.exe scripts/prepare_world.py
.venv\Scripts\python.exe scripts/check_world_seams.py
.venv\Scripts\python.exe -m unittest tests.test_global_density tests.test_prepare_world
.venv\Scripts\python.exe scripts/build_world_default.py
Get-Content data/world-build/build.log -Tail 10
Get-Content data/world-build/build-error.log -Tail 10
Get-Content data/world-build/default/progress.json
```

完全区画は緯度±85.05まで。表示限界の細い端部と極域の扱い、業種別/σ400/800、峰の境界、名称参照、PMTiles化・配信、国・地域選択、背景の本番運用と最終検証を続ける。これは世界版の完成や配信完了ではない。日本語化とGitHub Pages公開は後回し。
