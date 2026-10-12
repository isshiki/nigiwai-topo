# 日本版のPMTiles配信

画面・コード・ライセンスをGitHub Pages、生成したPMTilesと峰・駅・地域データをS3等のHTTPSストレージに配置する。ブラウザはPMTilesの必要部分だけHTTP Rangeで取得する。GitHub側でPythonや地図サーバーは動かさない。

## 再生成とローカル確認

全国GeoJSONの計算・行政区域名補完が完了した状態で実行する。

```powershell
uv sync --locked
uv run --offline scripts/build_pmtiles.py
uv run --offline scripts/validate_pmtiles.py
uv run --offline scripts/serve.py
```

WindowsのPythonでMVTを生成し、PMTiles v3へ集約。Tippecanoe/WSLの導入は不要。入力の密度値と分類は変えない。zoom 3–8は従来の800件/km²以上の簡略段彩、zoom 9–12は全詳細段彩と等高線。zoom 13以上は12のタイルを拡大する。形状はWeb Mercatorへ変換し4096単位で量子化、最大0.5単位の形状簡略化と8単位の端余白を使う。点の正確な座標・地名・ランキングは別JSONを使用する。

生成先はGit対象外の `data/distribution/foursquare-japan/`。条件ごとの9 PMTiles、9峰JSON、全国manifest、駅・地域JSON、NOTICEとApacheを配布する。タイル生成はzoom単位で `data/cache/pmtiles/` のSQLiteに保存し、途中から再開できる。

localhostの表示URLは http://127.0.0.1:8820/ 。`serve.py` は `/tiles/` を配布データへ割り当て、GET/HEAD、206部分取得、ETag、If-Match、範囲外416、CORSを扱う。標準の `python -m http.server` では部分取得できないため代用しない。

## AWSで配信する

既存AWSアカウントを利用でき、Cloudflareへの追加契約は不要。公開用S3 REST HTTPS URL（静的サイト用HTTPエンドポイントではない）か、S3をオリジンにしたCloudFrontを利用する。CloudFrontを使う場合はOAC等でS3を非公開にできる。S3から直接読む場合は配布用プレフィックスの匿名GET許可が必要。既存バケット全体の公開設定を変更せず、配布先とアクセス方式を決めてから設定する。

1. バケット・リージョン・公開URLを決める。AWSの既存CLIプロファイルを使い、キーはリポジトリにも画面にも入れない。
2. `docs/s3-cors.json` のYOUR-ACCOUNTを実際のPagesのオリジンへ変更する（リポジトリのパスは付けない）。S3のCORSにGET/HEAD、Range/If-Match、ETag等を設定する。CloudFrontの場合もOriginと必要ヘッダーが正しく渡る設定を確認する。
3. 配布ディレクトリ全体を `s3://BUCKET/foursquare-japan/` にアップロード。PMTilesはContent-Type=application/octet-stream、Content-Encodingは未設定。内部のタイルはgzip圧縮されているが、アーカイブ全体をgzipとして配信しない。
4. 公開URLへのRangeリクエストが206、Content-RangeとETagが返ること、PagesのOriginでCORSが通ることを確認する。

以下は実際の値を決めてから実行するコマンド例。現時点ではAWSの設定変更やアップロードは行っていない。

```powershell
aws s3api put-bucket-cors --bucket BUCKET --cors-configuration file://docs/s3-cors.json --profile PROFILE
aws s3 sync data/distribution/foursquare-japan s3://BUCKET/foursquare-japan/ --profile PROFILE
uv run --offline scripts/package_pages.py --data-url https://YOUR-DOMAIN/foursquare-japan/
```

`data/site/` がPagesへ配置する静的サイト。大容量データは含まない。GitHub ActionsでこのフォルダをPagesへデプロイするか、専用公開ブランチに内容を配置する。既存のweb/dataは計算入力なのでPagesへ丸ごとアップロードしない。

`web/config.js` はローカル用、公開パッケージのconfig.jsには指定HTTPS URLを入れる。ストレージ内のファイル名と階層は維持する。更新時はバージョン別プレフィックスへの一式アップロード後にconfigのURLを切り替えると、異なる世代のヘッダーとタイルを読む事故を避けやすい。

## 料金と残る制限

S3の容量・リクエスト・転送料、CloudFrontを使う場合はその料金を確認する。R2は任意の代替先であり必須ではない。無料枠や料金は変更されるため公開時点で公式料金を確認する。小容量でもアクセス数次第で通信費が変わる。

現段階では全国の峰JSONを条件ごとに全件読む。日本版では数MB程度だが、世界版には峰リストの区画分割等が必要。PMTiles化だけで世界版の計算・配信・名前の問題が解決するわけではない。

公式資料: [MapLibreへのPMTiles組み込み](https://docs.protomaps.com/pmtiles/maplibre)、[ストレージ・CORS](https://docs.protomaps.com/pmtiles/cloud-storage)、[S3料金](https://aws.amazon.com/s3/pricing/)。


## 指定バケット remasahiko

専用プレフィックス案: `s3://remasahiko/nigiwai-topo/japan/2026-09-15-v1/`。
公開用REST URL: `https://remasahiko.s3.ap-northeast-1.amazonaws.com/nigiwai-topo/japan/2026-09-15-v1/`。
HEAD応答から実リージョンap-northeast-1を確認済み。ローカルの既存プロファイルisekai-langsは指定アカウント207364224120と一致するが、このバケットへのListBucket・設定参照等の権限がなくAccessDenied。AWSへの書き込みは未実施。

手動アップロードの場合は、S3コンソールで上記フォルダを作り、data/distribution/foursquare-japan内の23ファイルをそのフォルダへアップロードする。フォルダ名foursquare-japanをさらに重ねないように注意（指定URL直下にmanifest.jsonがある形）。23ファイル・33,460,178 bytes。PMTiles9個だけでは駅名・ランキング・地域選択が動かないため、JSONとNOTICE/ライセンスも含めて一式アップロードする。

現在のdata/site/config.jsはこのURLを設定済み。データ側の公開とCORSの設定を終えてからPagesへ画面を配置する。ローカル画面は引き続きローカルデータを読む。

既存バケットが公開済みかは参照権限不足で未確認。S3直接配信なら当該プレフィックスの匿名GETが必要。docs/s3-public-read-statement.jsonは既存バケットポリシーのStatement配列へ追加するための案であり、既存ポリシーを置き換えるファイルではない。Public Access Blockが禁止する場合は設定を勝手に変えず、S3非公開＋CloudFrontの方式を選べる。

docs/s3-upload-iam.jsonは、アップロード担当用のnigiwai-topo配下への最小権限案。CORSや公開設定を変更する権限は含まないので、管理者がコンソールで別途設定する。CORSも既存ルールを残して必要ルールを追加する。CLIを使う場合はこのバケットを扱えるプロファイル名を指定する。

```powershell
aws s3 sync data/distribution/foursquare-japan s3://remasahiko/nigiwai-topo/japan/2026-09-15-v1/ --region ap-northeast-1 --profile PROFILE
uv run --offline scripts/package_pages.py --data-url https://remasahiko.s3.ap-northeast-1.amazonaws.com/nigiwai-topo/japan/2026-09-15-v1/
```


## 実アップロードとCloudFront（2026-10-06）

nigiwai-topoプロファイルで23ファイルのアップロード完了。バケットは公開ブロック有効の非公開構成で、既存CloudFront E37JQKYFGV0SUJ（re.masahiko.info）からOAC経由で配信される。使用URLは https://re.masahiko.info/nigiwai-topo/japan/2026-09-15-v1/ 。manifest9条件とPMTilesヘッダーのHTTP206/Content-Range/実バイト一致を確認。S3への匿名公開Statementは適用しない。

現状はCORS応答がなく、Pagesやlocalhostからのブラウザ読み込みは未接続。バケット全体のワイルドカードCORS案は自動承認レビューで却下され、S3・CloudFrontの設定変更は行っていない。

限定案: S3のCORS・公開ブロック・バケットポリシーは変更しない。CloudFrontにnigiwai-topo/*の専用behaviorを追加し、GET/HEAD/OPTIONSだけ許可、圧縮を無効にしてバイト範囲を保持する。AWS標準Managed-CORS-With-Preflightの読み取り用CORSポリシーをこのbehaviorだけに適用し、docs/cloudfront-preflight.jsのviewer-request関数でOPTIONSを204応答する。既存のデフォルトbehaviorは維持する。新しいポリシーとCloudFront Functionの作成が必要で、関数の実行にはAWSの従量課金がある。適用は承認後に行う。

data/site/config.jsは上記CloudFront URLで再生成済み。web/config.jsはCORS検証完了までローカル用のままにする。


## 承認後の限定設定

ユーザー承認を得てCloudFrontのnigiwai-topo/*だけに設定を追加した。S3のCORS・公開ブロック・バケットポリシーは未変更。CloudFront無料プランではカスタム応答ヘッダーポリシーが使用不可だったため、有料プランへ変更せずManaged-CORS-With-Preflight（5cc3b908-e619-4b99-88e5-2cf7f45965bd）を使用。作成した未使用カスタムポリシーは削除した。専用CloudFront Function NigiwaiTopoPreflightはviewer-requestでOPTIONSだけ204応答し、GET/HEADはそのまま通す。公開前テストが成功。

通常GET/HEADのCORSは標準ポリシー、OPTIONSのRange/If-Match許可は関数で扱う。既存の標準behaviorは保存した原設定と一致。元設定と適用設定はdata/deployment/に保存した。

今後の版はPythonからAWS CLIを呼ぶscripts/publish_data.pyでアップロード・検査・Pages用パッケージ生成をまとめて行える。既存版の上書きと他のS3ファイルの削除をしない。--uploadを付けない場合は計画表示だけで、AWS操作を行わない。

```powershell
uv run --offline scripts/publish_data.py --prefix nigiwai-topo/japan/2026-09-15-v2/ --data-url https://re.masahiko.info/nigiwai-topo/japan/2026-09-15-v2/
# 内容を確認して実行する場合
uv run --offline scripts/publish_data.py --prefix nigiwai-topo/japan/2026-09-15-v2/ --data-url https://re.masahiko.info/nigiwai-topo/japan/2026-09-15-v2/ --upload
```

設定変更はこのコマンドに含めない。データ生成後、全アーカイブ検査→指定アカウント確認→新規プレフィックス確認→アップロード→S3サイズ照合→CDNとCORS/OPTIONS/部分取得検査→Pagesの設定生成の順で行う。途中で失敗すると画面の参照先は切り替えず、アップロード先の新規版は残して調査できる。


## 外部配信の検証完了

CloudFront実URLで9アーカイブのHTTP206、Content-Range、ETag、Access-Control-Allow-Originを確認し、17,614タイルの検査も成功。OPTIONSは204、Allow-Origin=*、Allow-Headers=Range, If-Match。PMTiles JS 4.5.0で実HTTPSタイルの取得・解凍・MapLibre用TileJSONを検査済み。web/config.jsも実CloudFront URLに切り替え、data/siteを再生成した。ブラウザ画面操作は従前の制限により未検証。GitHub Pagesの実公開は別途行う。

S3のCORSは作成しておらず、公開ブロック4項目とバケットポリシーは維持。CloudFront標準behaviorは保存した原設定と一致する。地図専用パスにのみ標準CORSポリシーとOPTIONS関数が設定されている。CloudFrontの料金プランは変更していない。


## サービス追加版（現在の配信先）

2026-10-06に全12条件・29ファイル38,432,830 bytesを `nigiwai-topo/japan/2026-09-15-v2/` へ配置し、web/config.jsを切り替えた。配信URLは `https://re.masahiko.info/nigiwai-topo/japan/2026-09-15-v2/`。全12条件のRange/CORS/ETagとOPTIONSを検証済み。publish_data.pyは9条件/12条件の両方を扱う。AWS設定と旧v1は変更していない。[分類と再現](service-category.md)。
