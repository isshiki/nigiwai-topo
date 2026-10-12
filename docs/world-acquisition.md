> 履歴・調査記録：旧仕様、当時の件数、未完了事項を含みます。現在の公開仕様・完了状態は[現在の状態](current-state.md)を参照してください。

# 全世界のFoursquare収集

2026-10-07に収集を開始する構成を追加。日本・海外試作と同じ2026-09-15 snapshotを使用し、公式Places Portalの読み取り専用Iceberg接続から取得する。個人トークンは既存のgeoai-open-labの.envを読むだけで、コピー・表示・出力しない。[公式取得方法](https://docs.foursquare.com/data-products/docs/access-fsq-os-places)。

## 実行

```powershell
# 国コード別の件数・座標不正・閉店数を先に取得
.venv\Scripts\python.exe scripts/fetch_foursquare.py --world-plan --env-file C:/Projects-GitHub/geoai-open-lab/.env
# 非表示のバックグラウンド収集、完了済みの国ファイルを再利用
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start_world_acquisition.ps1
Get-Content data/raw/foursquare-global/run.log -Tail 10
Get-Content data/raw/foursquare-global/error.log -Tail 10
```

保存先はGit管理外 `data/raw/foursquare-global/`。plan.jsonに固定snapshot・国コード別の元件数/有効件数/閉店数、manifest.jsonに完了ファイル・SHA256・サイズ・実測時間・全体完了を記録。国コードはデータ源の属性で、行政区域判定ではない。国コードnullや通常形式以外も衝突しない安全なファイル名で保持する。

国ごとにZSTD圧縮Parquetへストリーム出力する。全世界をPythonメモリへ読み込まない。国単位で原子的に確定し、中断した国は再取得する。件数・IDの一意性・座標・閉店数をファイル確定前に検証。再開時に完了ファイルのハッシュも確認する。最後に国をまたぐ重複IDと全件数を検査し、成功した場合だけcomplete:trueにする。DuckDBは2スレッド/2GBの既存設定で、作業用スピルもプロジェクトのdata/cache/duckdb内に置く。空き20GiB未満では次の国の取得を停止する。tokenを含む可能性があるリモートエラーは既存取得ラッパーで非表示にする。

保持する列: fsq_place_id/name/longitude/latitude/country/fsq_category_ids/date_closed。カテゴリ表も同じ固定snapshotを保存する。閉店判明分を原本から削除せず、密度生成時に除外する。座標は経度-180〜180、緯度-90〜90の有限値を保持。無効座標は計算用ファイルから除外し、国別件数に記録する。極域・日付変更線付近のデータも取得するが、その地形生成対応は別工程。国ごとの保存は、密度を国境で切るという意味ではない。将来の計算では周辺国を含む計算余白を必ず参照する。

## 収集後

世界版の密度生成は既存の250km以内の試作処理をそのまま全国へ流用しない。地域分割・隣接区画の接続、日付変更線、極域、参照名称の地域抽出、国・地域選択、配信容量の測定を順に進める。現時点で現在の画面は日本と3試作のまま。日本語名補完は後回し。S3/CloudFrontに原本を自動公開しない。配信するのは検証後のPMTiles等であり、GitHub Pages公開は世界版が整ってから。

検証: 小さな実Parquetで再開時の非再取得、snapshot変更拒否、無効座標の除外、極・日付変更線の端点保持、国コード欠損、国をまたぐ重複IDの拒否を3テストで確認。


## 取得方式の修正

遠隔の国フィルタでもファイル走査が繰り返されるため、極小グループの取得も遅かった。2026-10-07に全世界を一回のCOPYで `world-source.pending.parquet` へ取得する方式へ変更。件数・閉店数一致を確認して `world-source.parquet` と固定snapshot/ハッシュのメタデータを確定し、その後はローカル原本から国別Parquetへ分割する。確定済みの国別ファイルは維持する。全世界原本は国別分割後も再計算用に保持するため、原本と国別ファイルの両方の保存容量が必要。

原本取得の途中で中断した場合は、原本の取得は初めからやり直す。原本が確定した後は遠隔の再取得は不要で、国別分割は完了済みの国から再開できる。開始前に40GiB、国別分割前に20GiBの空きを確認する。初回データ取得中の正確な完了率はまだ表示せず、run.logとpendingファイルの増加で進行を確認する。

実集計: 元109,440,828件、有効109,367,840件、無効72,988件、254国コードグループ。有効座標のうち閉店判明7,633,305件。集計は完了したが、全世界原本と地形生成の完了を意味しない。
