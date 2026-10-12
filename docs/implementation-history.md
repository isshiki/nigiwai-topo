# 実装・調査の履歴

以下は過去時点の記録です。現在の仕様は [README](../README.md) を参照してください。古い件数・未実装・配信待ちの記述は当時の状態を表します。


## 最新：保留4地名の周辺地域を確認（2026-10-10）

4参照地名に対応する6峰の周辺POI 2,065件について、同じFSQ snapshotの住所を取得し全ID・原座標一致を検証。施設名・住所・公的所在地から、蛇口（海上世界／太子湾）、福田（印力中心／竹子林）、沙井、前海桂湾と確認した。曖昧な元地名の翻訳確定とは区別し、6峰の画面名称を確認済み商圏・施設名へ変更。POI・地形は維持。[地域同定の根拠と峰別候補](docs/held-locale-poi-review.md)。

## 最新：世界v2の外部配信と24地名の再調査（2026-10-10）

世界v2のS3アップロードが完了。7,052ファイル・394,293,518 bytesを照合し、CloudFrontのRange（206）・CORSを確認。画面の世界データ接続先を `https://re.masahiko.info/nigiwai-topo/world/2026-09-15-v2/` に切り替えた。旧版は保存、GitHub Pagesは未公開。

保留24参照名を再調査し20件を採用、4件は参照位置と候補名の対応が確定せず原表記を維持。476件の最終判定は472採用・4保留、表示補正辞書は累計498参照名。韓国はカタカナ、中国は原語を確認した日本語向け漢字表記。自然地形を参照した名前はポップアップで区別する。

[24件の判定・出典・未解決理由](docs/held-locale-final-review.md)。以下は作業経過の記録。

## 最新：疑わしい13峰の地形修正（2026-10-10）

13峰周辺の5,436件を、ID・snapshot・原座標を固定した位置品質による計算保留にし、段彩・等高線・3D用形状を再生成した。全件の誤位置が確定した意味ではなく、原本を保存し、住所不足の正常な登録が含まれる可能性も画面に記載。元13地点と半径2km内の表示下限800以上の山はなくなった。13区画・12パッケージを修正し、残り2,935パッケージのSHA256一致を確認。配信用MVT・概観・峰索引・表示範囲トップ20を検証済み。

[ローカル世界版](http://127.0.0.1:8820/?area=world&region=world) は検証済みv2を読む。S3/CloudFrontはv2配信へ切替済み。GitHub Pagesは未公開。[修正結果・限界・再現手順・配信手順](docs/held-density-rebuild.md)。以下の名称補完やラベルのみの保留は、この地形修正前の経過。

## 名称確認の最新結果（2026-10-10）

追加調査の結果、位置品質の確認待ち13峰は▲・名称・数値ラベル、ランキング、峰検索候補から外した。8峰は位置問題の強い疑い、5峰は暫定保留。対象の頂だけを座標で限定し、元POI・段彩・等高線・3Dは維持する。画面にもこの限界を明記。[13峰ごとの表示判断](docs/held-peak-display-decisions.md)。

今回の確認待ち476参照名をCodexで内容確認し、452件を表示へ追加、24件を保留した。中国の一意な漢字候補90件はこの476件の内数で、すべて確認・反映済み。公式日本語名と原語からの編集音写・漢字表記を区別し、出典ID・原表記・根拠を保持する。保留だった18峰を追加調査し、大学・集落・鉱山キャンプの5峰を補完。座標だけだった高密度60峰は累計47峰を補完、13峰を位置品質の確認待ちとした。詳細は [保留18峰の調査](docs/held-peak-investigation.md)。世界全峰と国内レコードの名前処理、表示範囲トップ20を再検証。密度・地形は変更せず、GitHub Pagesは未公開。

詳しい判定・検査方法・再現手順は [名称品質の確認結果](docs/world-name-quality-plan.md) を参照。

<!-- held-address-audit:start -->
保留13峰近傍の5,436個の元FSQ IDの住所情報を取得し、ID・座標一致を全件検証した。地名の全照合候補から50km超は3,470件（不整合の検査候補であり、誤位置確定数ではない）。住所の欠損・名称未照合も記録。密度・地形・配信データは変更していない。詳しくは [元住所の照合結果](docs/held-peak-address-audit.md)。
<!-- held-address-audit:end -->

除外前後の感度分析も完了。公式資料と元住所の対応が強い4件だけを除くと、13峰は残り、13地点内の密度順位も変わらなかった。不整合候補3,470件をすべて除く仮定では8地点が800件/km²未満となり、半径2km内の表示対象の峰もなくなる。候補全件の誤位置が確定したという意味ではなく、配信地形は変更していない。現状の13峰の密度を再現し、全比較格子で除外後の密度が増加しないことを検証した。[除外の影響と次の確認](docs/held-peak-exclusion-impact.md)。

**お店と施設の登録密度を、山に見立てた地図。** 公開POIの密度を件/km²で計算し、段彩・等高線・段々3Dで表示する個人ブログ向け試作。人出・売上・物理的な標高ではありません。デフォルトはσ=200m・表示下限800件/km²。

## Foursquare全国版

[全国版を開く](http://127.0.0.1:8820/?dataset=foursquare&region=japan)。公開画面はFoursquare専用。全国・9地方・47都道府県を選択できます（旧datasetパラメータは無視）。全国版はFoursquareの2026-09-15 snapshotを固定し、JP登録・122–154°E / 20–46°Nの5,022,570件を取得。閉店判明489,866件を除く4,532,704件を使用（飲食1,239,454件・買い物835,850件）。範囲外・座標欠損等102件を除外しました。離島の登録も対象ですが、実際の網羅率を保証するものではありません。

全国N02の9,046駅グループを検索・峰の参考名に使用。ランキングは選択条件と表示下限に応じた地図の表示範囲内の上位20峰で、クリックで移動します。独立峰の突出度を判定した順位ではありません。

全国版は日本中心のランベルト正積方位図法、共通100m格子、50km区画、4σ以上の余白で計算。表示範囲に応じて外部配信可能なPMTilesの必要部分を読み込みます。zoom 9未満は800件/km²以上の段彩を簡略化した概観（等高線は省略）、拡大時は詳細形状。全国版の閉店情報は判明分除外に固定。業種4種（すべて・飲食・買い物・サービス）×σ3種、計12条件を生成します。[全国化の方法と限界](docs/national.md)

```powershell
uv --cache-dir data/cache/uv run --offline scripts/prepare_names.py --national --raw-dir C:/Projects-GitHub/rail-gap-map/data/raw
uv --cache-dir data/cache/uv run scripts/fetch_foursquare.py --national --env-file C:/Projects-GitHub/geoai-open-lab/.env
uv --cache-dir data/cache/uv run --offline scripts/build_national.py
# 公式N03全国2026年版を取得（約766MB、Git対象外）
New-Item -ItemType Directory -Force data/raw/admin | Out-Null
Invoke-WebRequest https://nlftp.mlit.go.jp/ksj/gml/data/N03/N03-2026/N03-20260101_GML.zip -OutFile data/raw/admin/N03-20260101_GML.zip
uv --cache-dir data/cache/uv run --offline scripts/enrich_admin.py
uv --cache-dir data/cache/uv run --offline scripts/validate_national.py
uv --cache-dir data/cache/uv run --offline scripts/build_pmtiles.py
uv --cache-dir data/cache/uv run --offline scripts/validate_pmtiles.py
```

他プロジェクトの個人用トークンを読む場合は所有者の明示許可が前提。通常は本プロジェクトの.envを使用します。全国取得は原本を区画JSONLへ逐次保存し、COUNT・一意ID件数・取得件数を照合、原本SHA-256を検査。ビルドは区画単位で再開でき、生成済みの同一snapshotは再取得しません。

サービス業種を追加しました。計算入力は1,110,734件。理美容・修理・金融・不動産などの業務サービスと医療を対象にし、Foursquare分類上の事務所・製造業も含みます。追加取得・生成・配信の完了状況は[サービス分類と再現手順](docs/service-category.md)を参照。既存の飲食・買い物と一部重複するため、業種別件数は合算できません。

## 操作と地名

左側メニューで地域を選ぶと、その範囲へ移動し、表示範囲の峰からランキングを表示します。地形は全国共通で県境を切らず、周辺も描画します。中部は新潟・北陸・甲信・東海、近畿は三重を含む区分。東京都の旧URL `region=tokyo` は都全域へ移動します。

近隣駅（1.5km以内）を峰名にし、駅から遠い峰はN03の所属市区町村・政令市区名を表示。海岸線外などは行政区域まで1.5km以内の参考名に「付近」を付け、それ以上は座標表示。町丁目名の命名ではありません。行政区域に属する峰を県別に分類し、区域外の近隣分類には参考分類フラグを持たせます。

「現在地」は押したときにブラウザの許可を得て取得します。このアプリでは位置を保存・送信しません。背景タイルは移動先に応じて取得します。HTTPSまたはlocalhostで使用してください。出典は地図下部に常時表示し、FSQ NOTICE全文・Apacheライセンス・加工内容も配布します。

旧東京3データ比較と架空データの原本・生成物は削除済みです。比較用コードと方法の記録だけ保持しています。

## ローカル表示

Python 3.14、uv。依存はuv.lockで固定。

```powershell
uv --cache-dir data/cache/uv sync --locked
uv --cache-dir data/cache/uv run --offline scripts/serve.py
```

生成済みのdata/distribution/foursquare-japanがあれば再取得・再計算は不要。MapLibreと地理院背景タイルはブラウザが外部から読みます。駅検索文字は検索サービスへ送りません。

## 検証と公開容量

再現は上記の全国取得・計算・地名補完の順で行います。原本・キャッシュ・生成データ・認証情報はGit対象外です。

```powershell
uv --cache-dir data/cache/uv run --offline python -m unittest discover -s tests -v
uv --cache-dir data/cache/uv run --offline scripts/validate_national.py
node --check web/app.js
```

2026-10-06に旧東京のOverture・OSM・Foursquare比較原本と生成物、東京名付け資料、架空生成物を削除。全国FSQ原本・N03・全国駅資料・snapshot固定情報・全国計算キャッシュは再現に使用するため保持しました。旧比較の取得・計算コードとdocsの実験記録は残しています。

サービス追加版のPMTiles12個は合計21,500,802 bytes（約21.5MB）。峰・駅・地域JSONとライセンスを含む外部配布29ファイルは38,432,830 bytes（約38.4MB）。Pages用の画面パッケージは約36.4KB（MapLibre・PMTilesライブラリは固定バージョンCDNから取得）。元の約121MBのGeoJSONは再生成入力として保持し、配信では読みません。[AWSへの配置手順](docs/pmtiles-deployment.md)。GitHub Pagesの公開サイト上限は1GB、通常Gitで100MiBを超える単一ファイルは追加できません（[Pages制限](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits)、[ファイル制限](https://docs.github.com/en/repositories/working-with-files/managing-large-files/about-large-files-on-github)）。海外3地域の試作は配布一式約12.2MB。全世界の容量は未測定。現在のGeoJSONと12条件を世界に展開する場合は上限超過を想定し、PMTiles等の最適化と地図データの外部配信を検討します。PMTiles化だけで上限内に収まる保証はありません。

海外試作では峰索引の分割読み込みを実装済み。突出度による独立峰、経済センサス比較、全世界への拡大と配信性能の追加最適化は未完了。[全国の方法](docs/national.md) / [出典](docs/data-sources.md) / [検証](docs/validation.md)。現在はローカル検証用で、外部公開・commit・pushは行っていません。


## Pagesと外部ストレージ

現在の表示はPMTiles方式。ローカルではserve.pyが画面と配布先を兼ねます。公開時はdata/distribution/foursquare-japanの一式をS3等へ置き、次のコマンドで画面だけをdata/siteへ生成します。

```powershell
uv run --offline scripts/package_pages.py --data-url https://YOUR-DOMAIN/foursquare-japan/
```

配信先はHTTPS・Range・CORS対応が必要。AWSのバケットはremasahiko（東京リージョン）。サービス追加版はnigiwai-topo/japan/2026-09-15-v2/配下へ29ファイルをアップロード済み。既存CloudFront re.masahiko.infoの地図用パス限定CORS/OPTIONSを利用し、全12条件の外部部分取得を検証済み。data/siteは同じHTTPS URLを設定した未公開パッケージ。現在のweb/config.jsもこの版を読みます。旧v1は上書きしていません。


通常のローカル画面もCloudFrontから地図データを取得します。ネット接続が必要です。ローカルデータで検証する場合だけweb/config.jsのdataBaseを `tiles/foursquare-japan/` に変更します。GitHub Pagesへの実デプロイはまだ行っていません。


## 表示調整と世界版の予定

地域選択の横の「全域」は選択中の全国・地方・県全体へ戻る操作。駅検索の「移動」と「現在地」を並べた。左メニューはデスクトップで約1.25倍（内容幅260→325px）、峰の地名11→13px・密度10→12px。地図の移動余白は実際のメニュー位置から計算する。狭い画面では下部パネルを使う。

GitHub Pagesの実公開は世界版が完成してから行う。[世界版に向けた残作業と順序](docs/world-plan.md)。

日本全国に加え、シンガポール・ロンドン・レイキャビク周辺の試作を表示できる。メニューの「エリア」で切り替え、「地域」の横の「全域」で選択範囲に戻る。海外は各12条件を生成・外部配信し、表示範囲トップ20を保つ峰索引を分割取得する。[海外試作のデータ・再現・検証](docs/world-pilots.md)。全世界・各国全域の収録はまだ行っていない。

海外の名前参照はOSMの駅を優先し、駅が遠い場合は都市・地区名で補完する。試作3地域の参照データを取得・検証し、密度生成処理への命名関数の接続を実装した。[世界版の名前づけ](docs/world-names.md)。海外3地域のPOI密度・地名・画面・配信まで接続済み。

[ロンドン試作を開く](http://127.0.0.1:8820/?area=gb-london&region=gb-london) / [シンガポール試作](http://127.0.0.1:8820/?area=sg-singapore&region=sg-singapore) / [レイキャビク試作](http://127.0.0.1:8820/?area=is-reykjavik&region=is-reykjavik)。

## 山の日本語表記

海外の山ラベル・ランキングは、OSMの日本語名とWikidataの日本語名を事前取得した辞書を使用します。日本語名がない場合は現地名を維持します。背景地図の文字は変更しません。取得・再生成手順と未対応件数は [名称データ](docs/world-names.md#山の日本語表記2026-10-07) を参照してください。

未対応地名はJSONにまとめ、既存のローカルOllamaで日本語候補を生成できます。現在3地域の対象は重複をまとめて582件。10件ごとに保存・再開でき、バックグラウンド実行にも対応します。候補は正式辞書と分けて保存します。[名称候補の生成手順](docs/world-names.md#ローカルllmの名称候補2026-10-07)。

3モデルで3地域30件を独立比較しました。全モデルの完全一致0件、表記の区切り等を除く一致2件。9Bは30件すべてに候補を返しましたが、モデル間一致を正解とは扱わず、正式辞書への自動採用はしていません。[比較手順と結果](docs/world-names.md#複数モデルの試行)。

## 世界全体の収集

固定2026-09-15版を国コード別の圧縮Parquetに保存する、再開可能な収集処理を追加しました。収集と世界版の地形生成は別工程です。日本語化は後回し、GitHub Pages公開も世界版完成後です。[収集手順・進捗の確認](docs/world-acquisition.md)。

世界版の生成入力は閉店判明分を除き101,734,535件。既定200m・全業種の共通格子による実験生成を開始しました。配信・名称参照・他条件は未完了です。[進捗と検証](docs/world-generation.md)。

200m・全業種の世界形状検査が完了し、2,947個のPMTilesへの変換、峰の境界補正、近隣都市・町村名の付与を進めています。[配信準備・進捗・残作業](docs/world-delivery.md)。

## 世界版の先行表示（2026-10-08）

[世界版をローカルで開く](http://127.0.0.1:8820/?area=world&region=world)。200m・すべての2,947地域を生成・検証済み。世界概観と表示範囲の詳細を切り替え、共通峰索引で表示範囲の上位20件を検索します。6大陸の移動先を用意。未生成の業種・幅、世界全都市の検索、国別選択、日本語化は未対応です。[配信構成と検証](docs/world-delivery.md#世界版画面への接続2026-10-08)。世界版データはS3・CloudFrontへ配信済み（7,051ファイル、394,326,522 bytes）。ローカル画面も外部配信を使用します。全ファイル数・サイズとCloudFrontのRange/CORS/OPTIONSを検証済み。GitHub Pages公開は保留しています。

世界版の翻訳対象を参照IDごとにJSONへ辞書化済み。113,083参照地名のうち日本語未対応107,290件。表示へ反映する翻訳はまだ実行していません。[世界版の翻訳用辞書](docs/world-names.md#世界版の翻訳用辞書2026-10-08) を参照。

翻訳開始前に資料を調査し、GeoNamesとNatural Earthで16,377地名の登録済み日本語候補を確認。現在の表示にはまだ反映していません。[世界地名の日本語化・事前調査](docs/world-name-research.md)。
# 世界の山名の日本語化（2026-10-08）

追加修正を実施: 韓国・中国の500件は応答取得完了。出典付き補正21件を反映し、481件は確認待ちです。実際の表示関数による全件検証で、日本の英字参照名と日本版の座標表示は残り0件。海外の座標表示60峰（密度800以上）は追加調査用リストに整理しました。[実行結果と次の調査](docs/world-name-quality-plan.md)。

追加点検: 世界の座標のみ5,609峰を記録し、日本内194峰を行政区域名で補完。日本の英字参照名877件（沖縄を含む）を日本語地域名・登録別名で画面補完しました。韓国カタカナ・中国日本語漢字の方針に合わせた500件の候補を再生成中。詳細は[確認結果と方針](docs/world-name-quality-plan.md)。

次の工程は[品質確認と採用の作業計画](docs/world-name-quality-plan.md)。全候補の自動点検と457件の確認サンプル作成を実施し、誤読・別地名への置換を出典付きで記録しています。全457件の内容検証は未完了です。

2026-10-10更新: 未対応85,749件の候補生成を完了しました。日本語候補85,152件、不明597件、未保存0件。統合結果は `data/name-translation/world/all-candidates.json`、優先確認リストは `candidate-review.json`。翻訳内容の検証と表示への採用は未完了です。

2026-10-09更新: Wikidata照合完了。採用済み日本語名は25,821件、確認待ち1,513件、未対応85,749件です。Qwen 9Bの300件試行後、残りの未検証候補をバックグラウンド生成中。目視で接尾辞の誤読例があり、モデル候補は画面へ自動採用しません。再開は `./scripts/start_world_translation.ps1`。進捗は `data/name-translation/world/translation.log` を参照。

登録済み日本語名21,051件（既存5,793件を含む）を画面に反映。表記が競合する1,119件は元の表記を維持し、確認用JSONに分離しています。背景地図の文字は変更しません。

`scripts/fetch_world_wikidata_names.py --trial` はGeoNamesの明示的なWikidata IDを使い、P1566の一致を確認して日本語名を補完します。取得完了後に辞書を再構築し、残りからQwen 9Bで300件の候補を生成します。モデル候補は画面へ自動採用しません。取得キャッシュ・進捗・候補はGit管理外の `data/name-translation/world/` に保存します。中断後は同じコマンドで再開できます。

取得はバックグラウンドで進行中です。詳細は [日本語名の手順](docs/world-names.md) を参照してください。


## 2026-10-10 追加の名称修正

韓国のスウォン・インチョン・テグ・テジョン・コンジュを公的日本語資料とGeoNamesの出典IDで照合し、カタカナ表示を追加した。出典付き表示修正は計26件、国別表記の確認待ちは476件。中国語・韓国語の原語別名を500対象中364件（中国249、韓国115）について抽出した。原語の漢字は日本語の慣用名の証明ではないため、未確認候補は表示へ自動採用しない。日本でも使う「湾」を誤って除外していた判定を修正した。

再現: `scripts/build_reviewed_world_names.py` → `scripts/research_native_aliases.py` → `node scripts/validate_name_overlays.cjs`。原語別名と候補・保留理由はGit管理外の `data/name-research/native-locale-review.json` に保存。元資料はGeoNames alternateNamesV2（CC BY 4.0）、SHA256と出典IDを保持。

世界319,897峰と国内44,459レコードの表示名を再検証。日本の対象英語地名と座標だけの表示は0件。海外の表示下限800以上の座標表示60峰は未解決で、近隣都市を遠距離から割り当てず、追加の地理資料による確認対象として残す。GitHub Pagesは未公開。
