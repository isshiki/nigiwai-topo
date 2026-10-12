> 2026-10-11更新：世界の表示名は接尾辞なし・日本語辞書接続・同名の代表1件へ変更。最新の仕様と714条件の検証は[世界の名称修正](world-display-names.md)を参照。以下の旧仕様・検査結果は変更前の記録を含みます。

# 世界版の駅名・都市名

## 最新結果（2026-10-10）

今回対象の476参照名のうち452件を反映し24件を保留。中国の90件はその内数で全件確認済み。保留18峰の追加調査により5峰を追加補完。高密度60峰は累計47峰を補完し13峰を位置品質確認待ちとした。詳細は [保留18峰の調査](held-peak-investigation.md)。登録名・公的資料とCodex編集音写を区別して記録する。古い件数は各段階のスナップショット。詳細・再現手順は [名称品質の確認結果](world-name-quality-plan.md)。

日本は国土数値情報N02/N03による現在の命名を維持する。海外の密度入力はFoursquareを使い、名前の参照だけOpenStreetMapから取得する。

## 抽出と命名

`scripts/fetch_world_names.py` が試作3地域の範囲に20kmの参照余白を加え、公開Overpass APIから駅と都市・地区の代表点を取得する。駅は `railway=station/halt` または鉄道・地下鉄・ライトレールの `public_transport=station`。ホーム・停車位置・入口、廃止・建設中・貨物専用の明示がある登録は除外する。単独のバス停は駅にしない。廃止等のタグが欠ける登録や誤った位置は残り得る。駅の面・relationにはAPIのcenterを用いるため、正確な入口・ホームの位置ではない。

`scripts/world_names.py` が300m以内の同名駅、または同一Wikidata IDの駅をまとめる。連鎖的に遠い駅まで結合せず、元の代表点からの距離を使う。全く同じ名前の別駅や、大きなターミナルの別名登録は統合しきれない可能性がある。元のOSM IDを保持し、曖昧な統合は実データ比較で調整する。

名称は `name:ja` → `name` → `name:en`。日本語がない駅を自動翻訳して推測しない。峰から測地線距離で1.5km以内の最寄り駅があれば駅名を使う。なければ都市・地区の代表点を検索し、最寄りの参考名に「付近」を付ける。地区は3km、都市・町・村は15km以内を候補とし、それもなければ座標を表示する。これは行政区域の包含判定ではない。都市・地区の面は初期シンガポール抽出にも含まれるが、その後の取得はAPI負荷を抑えるためnodeの代表点に限定している。抽出クエリを地域manifestに保存する。

峰には `name_basis`、`name_source`、`name_source_ids`、`name_key`、駅までの距離を保存する。日本用 `surface()` の既定動作を維持し、海外では `inverse=RegionalGrid(...).inverse, namer=WorldNamer(...)` を渡す。計算座標と名前参照の座標を混同しない。

```powershell
uv --cache-dir data/cache/uv run scripts/fetch_world_names.py
uv --cache-dir data/cache/uv run --offline python -m unittest discover -s tests
```

取得済み原本は `data/raw/world-names/<region>/overpass.json`。SHA-256一致を確認して再利用する。`stations.json` と `places.json`、manifestを作る。原本にAPIのエラーremarkがある場合は不完全な結果として保存しない。公開APIの呼び出しはこの小規模試作のみで、世界拡大時は地域別PBFのローカル抽出へ置き換える。ブラウザからOverpassを呼ばない。

## 実データ検証（2026-10-06）

|試作地域（参照余白を含む）|駅グループ|都市・地区等の名前|
|---|---:|---:|
|シンガポール周辺|234|1,851|
|ロンドン周辺|895|2,314|
|レイキャビク周辺|0|150|

駅グループ数は鉄道駅総数の公的統計ではない。3原本のハッシュと、すべての参照駅の位置でOSMの駅名を選択することを確認した。ロンドンの試作中心ではWestminster駅、レイキャビクの試作中心ではOSMの地区名 `Hlíðar` に「付近」を付ける。検証結果は `data/validation/world-names-summary.json`。自動テスト21件成功（駅重複、連鎖結合の防止、日本語優先、駅から遠い場合、駅なし、南・西半球座標、地域別密度生成への接続を含む）。

Foursquareは固定2026-09-15版、今回のOSM参照は2026-10-06更新分で、時点が異なる。海外3地域の密度データを取得し、実際の峰位置へこの命名を適用、画面と外部配信まで接続した。[海外試作の検証](world-pilots.md)。日本の命名と配信データは維持する。

## 出典と配布

[OSMの駅仕様](https://wiki.openstreetmap.org/wiki/Railway_stations)、[名称仕様](https://wiki.openstreetmap.org/wiki/Key:name)、[Overpass API](https://wiki.openstreetmap.org/wiki/Overpass_API)。駅・都市名の参照データは **© OpenStreetMap contributors / ODbL 1.0**。[OSMの利用条件](https://www.openstreetmap.org/copyright) / [ODbL](https://opendatacommons.org/licenses/odbl/1-0/)。OSM由来の参照表・加工情報を配布可能な形で保持し、海外試作の画面の常時表示、出典欄、配布manifest・OSM-NOTICEに出典とライセンスを入れた。Foursquareの密度データとは出典・ライセンスを区別する。現在の日本版の駅名はOSM由来ではない。


## 山の日本語表記（2026-10-07）

計算済み12条件の峰から `name_source_ids` を抽出し、OSM識別子をキーに `web/japanese-names.js` の静的辞書を作る。名称文字列だけで結合しない。OSM `name:ja` を優先し、リンクされたWikidataの日本語ラベルで補完する。辞書には参照元も保持する。Wikidataの構造化データは [CC0](https://www.wikidata.org/wiki/Wikidata:Licensing)。日本語の登録表記を採用する処理で、すべての名前を人手で確認したものではない。

|地域|山に使う参照レコード|日本語名あり|未登録|
|---|---:|---:|---:|
|シンガポール|336|155|181|
|ロンドン|797|423|374|
|レイキャビク|48|4|44|

これは峰の数ではなく参照名の件数。同じ名前を複数の峰が使う。都市中心だけでなく小さな地区・駅も含むため、全件日本語化には追加調査が必要。未登録の名称一覧は `data/cache/japanese-names/<region>/missing.json`。機械翻訳や未確認のカタカナ表記は追加しない。手動補完は `scripts/japanese-name-overrides.json` に地域・OSM識別子ごとに `name` と確認元 `source` を記載し、再生成する。

```powershell
.venv\Scripts\python.exe scripts/build_japanese_names.py
node tests/area_switch_check.cjs
.venv\Scripts\python.exe scripts/package_pages.py --data-url https://re.masahiko.info/nigiwai-topo/japan/2026-09-15-v2/ --config web/config.js
```

API取得は準備時だけ。キャッシュ済みバッチを再利用し、429等は待機して再試行する。画面では山ラベル・ランキング・ポップアップに共通適用し、ポップアップには変更前の名称も表示する。補完名は検索候補にも追加し、現地名検索も維持する。駅の青い点と背景は元の表記を維持。辞書がない地域や参照名は元の名称へ戻る。密度・峰位置・順位・外部PMTilesの再生成やアップロードは不要。辞書はPages用パッケージにも含める。Pages公開は未実施。

検証: 日本と海外3地域、48条件×3表示下限で順位が変わらないこと、日本語名の適用、地区の「付近」の維持、辞書未登録時の元名表示をDOM/地図のテストダブルで確認。実ブラウザの描画確認は未実施。


## ローカルLLMの名称候補（2026-10-07）

辞書本体は `web/japanese-names.json`。`build_japanese_names.py` が同じ内容のJSも生成し、画面は追加通信なしで読む。現地名未対応599参照レコードを地域内の同じ原表記でまとめ、582生成対象（シンガポール172、ロンドン368、レイキャビク42）へ削減した。異なる地域の同名は統合しない。原表記・地域・言語ヒント・参照種別・座標・OSM識別子を保持する。

```powershell
# 未対応JSONとChatGPT貼付け用20件ずつの30ファイルを生成
.venv\Scripts\python.exe scripts/translate_names.py
# 同じPCのOllamaへ順次送信。保存済みIDは飛ばして再開
.venv\Scripts\python.exe scripts/translate_names.py --run --model qwen3.5:4b
# 非表示のバックグラウンド実行（ログとPIDをプロジェクト内に保存）
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/start_name_translation.ps1
Get-Content data/name-translation/run.log -Tail 10
Get-Content data/name-translation/error.log -Tail 10
```

既存 `C:/Projects-Novel/isekai-langs` の設定を参考に、localhost:11434、温度0、seed1、4096 context、think:false、構造化JSONを使用する。モデルを新規ダウンロードせず既存qwen3.5:4bで実機測定。30件の3バッチは14.1秒（モデル読込含む）、7.1秒、7.5秒、合計約29秒。10件約7.3秒から全582件は約7分という概算で、負荷や回答長で変わる。処理対象は現在の3試作のみで、全世界の見積もりではない。

保存先 `data/name-translation/input.json`、`chatgpt/batch-*.json`、`candidates-qwen3.5-4b.json`。10件ごとに原子的に保存し、中断後も再実行で続行する。重複/欠落ID、JSON構造、日本語文字、長さ、改行を検証する。接続先はコードでローカルに固定しクラウドは呼ばない。失敗時は処理を終了し、再実行できる。バックグラウンド実行はログオン時タスクではなく、一回限りのプロセスで、再起動後には手動再開が必要。

モデルの `conventional` は自己申告で、慣用表記確認済みを意味しない。結果はすべてcandidateとして保存し、正式辞書には自動投入しない。最初の30件にはアイスランド語の未回答や表記の揺れがある。4Bは候補作成に使用できるが、固有名詞の読みの正確さを保証しない。必要な項目だけ9Bや別モデルで再比較し、原表記と照合する。機械的検証は読みの品質確認とは別。確認後に `scripts/japanese-name-overrides.json` へ確認元付きで採用し、辞書を再生成する。


### 複数モデルの試行

`scripts/compare_name_models.py` は保存済み4Bの先頭30件（3地域各10件）を同じ入力JSONから再抽出し、Qwen 9BとGranite 8Bへ順次送る。他モデルの回答は入力から除外する。各モデルを同時実行しない。入力と個別回答・実測時間・一致判定は `data/name-translation/comparison-independent/` に保存する。正規化一致はNFKC・空白・中点・末尾の「駅」の差のみを除去し、null同士を一致とは数えない。全モデル一致は出典確認済みを意味しない。途中の回答を含む入力で実行した初期フォルダ `comparison/` は比較評価に使わない。

```powershell
.venv\Scripts\python.exe scripts/compare_name_models.py
```

4Bの全件バックグラウンド処理は日本語文字の検証に失敗し110件で停止。正式辞書は変更していない。失敗したバッチの生応答を診断できるよう、今後は検証前にも保存する。


試行結果（3地域各10件、計30件）:

|モデル|候補あり|3バッチ実測合計|
|---|---:|---:|
|Qwen 3.5 4B|21/30|28.6秒|
|Qwen 3.5 9B|30/30|40.8秒|
|Granite 4.2 8B|30/30|35.7秒|

3モデル完全一致0件、正規化一致2件（Jurong Town Hall、North Harrow）。ペア正規化一致は4B/9Bが8件、4B/Graniteが3件、9B/Graniteが4件。未回答同士を一致扱いしない。4B時間は先行測定の最初3バッチ、他は今回の独立生成であり、読み込み状態の違いがある。入力順・プロンプト・3地域の標本は共通。30件は網羅的な品質評価ではない。

例: Kársnesは4B未回答、9B「カーズネス」、Granite「カールスネス」。Paddingtonは4B/Granite「パディングトン」、9B「パディントン」。この結果だけでは正解判定できない。GraniteはSwanley New Barn Miniature Railwayに崩れた表記を生成し、第三票の採用に適しているとは確認できなかった。9Bは未回答が少ない候補生成器として使えるが、外部資料による読みの確認は必要。自動多数決採用は行わず、全候補を元の辞書から分離して保存した。正式表示と背景は変更していない。

## 世界版の翻訳用辞書（2026-10-08）

計算済み319,897峰から参照IDごとに名称を抽出。参照地名113,083件、既存日本語5,793件、未対応107,290件。5,609峰は近隣参照名がなく座標表示で、翻訳対象に含めない。既存日本語はN02、試作のOSM/Wikidata辞書、日本のGeoNames日本語表記に限定し、国外の漢字名を日本語扱いしない。同じ文字列でも参照IDが異なる場所は別の項目にする。

辞書は `data/name-translation/world/dictionary.json`。翻訳入力は同ディレクトリの `input.json`、ChatGPT貼付け用50件ずつは `chatgpt/batch-0000.json` 以降2,146ファイル。参照元、原表記、国、座標、参照種別、使用峰数を保持。使用峰数の多い順に並べる。これは翻訳用辞書であり、世界用の日本語名を表示辞書へ反映した状態ではない。

`scripts/translate_world_names.py` は既存Ollamaを呼び出し、10件ずつ候補JSONへ保存・再開する。既定はQwen 3.5 9B・300件の試行。モデルの自動ダウンロードは行わず、候補は画面へ自動採用しない。3試作の候補データを上書きしない。全件処理は `--limit 0` を明示する。現在は辞書作成と実行準備だけを完了し、生成モデルの選択待ち。

```powershell
.venv\Scripts\python.exe scripts/export_world_names.py
.venv\Scripts\python.exe scripts/translate_world_names.py
# Ollamaでの試行を選択した場合
.venv\Scripts\python.exe scripts/translate_world_names.py --run --limit 300
```

先行3都市の9B実測は30件40.8秒。107,290件に単純比例させると約40.5時間だが、モデル読込・機器負荷・言語・出力長の違いがあるため、今回の処理時間の確約には使えない。候補生成後には表記の確認と表示辞書への反映が必要。

## 翻訳前の資料調査（2026-10-08）

翻訳開始を保留し、GeoNames日本語別名・Natural Earth・Wikidata・OSM・地名辞典・翻訳専用モデルを調査。登録済み日本語の候補が16,377地名（85,107峰）で見つかりました。未採用で、現在の辞書・表示は変更していません。Wikidataの全件日本語ラベル照合は未実施。[調査結果と推奨手順](world-name-research.md)。
## 登録名の採用と補完処理（2026-10-08）

### 2026-10-09: 登録名の照合完了・全件候補生成開始

#### 2026-10-10: 候補生成完了

Qwenの有効応答85,726件と、未保存分に対する既存Granite 8Bの23件を統合し、対象85,749件すべてのID・参照メタデータ・形式を照合しました。日本語候補85,152件、不明597件、未保存0件。モデルがunknownと回答した文字列は候補名として採用せずnullに統一し、返された表記はmodel_returned_jaまたは各モデルの元ファイルに保持します。

`scripts/finalize_world_candidates.py` で `data/name-translation/world/all-candidates.json` と `candidate-review.json`、`completion-check.json` を生成します。優先確認9,373件は、出典のない慣用表記の自己申告、韓国の行政区分接尾辞、英字混在などのフラグであり、誤訳件数ではありません。LLM候補の意味・発音の検証は完了しておらず、表示辞書には適用していません。unknownを理由に原表記を消さないでください。

Wikidata 33,168件の照合とQwen 9Bの300件試行は完了しました。登録名の採用25,821件（100,365峰の参照）、出典競合などのレビュー1,513件、未対応85,749件。300件の内訳は音写261件・慣用表記という自己申告31件・不明8件、生成294.5秒です。kindはモデルの自己申告であり、実在の慣用表記を保証しません。

候補の一部を目視確認すると、`Guri-si → グリスイ` のように接尾辞の読みが不適切と考えられる例がありました。形式検証だけで正しい地名と判定せず、全件を未検証候補として保存します。既存300件を引き継ぎ、残り85,449件の生成を開始しました。概算23時間に、機器負荷・再試行・保存時間が加わります。

```powershell
./scripts/start_world_translation.ps1
```

隠れたプロセスで実行し、`data/name-translation/world/translation.log` と `translation.err.log` に出力します。`translation-process.json` にPID・開始日時を記録し、二重起動を避けます。中断後は同じコマンドで再開できます。各バッチを最大3回試行し、形式不備などが続くバッチは候補JSONのfailuresに記録して後続を続けます。記録済みIDは再生成しません。不明回答や失敗分の確認と、表示辞書への採用は生成後の別工程です。

`scripts/build_world_japanese_names.py` でGeoNames日本語別名とNatural Earth NAME_JAを照合し、21,051参照名を採用しました。うち既存日本語名は5,793件。対応する峰の参照数は86,165件です。残りはレビュー1,119件とモデル処理待ち90,913件です（Wikidata補完前の値）。旧称・俗称・短縮名・終了年月を持つ別名を除外し、複数表記や出典間の不一致は自動採用しません。

画面は `web/world-japanese-names.js` を読み、出典と参照IDの組で名前を解決します。同名の別都市を文字列だけで統合しません。地図形状、密度、順位は変更しません。

実行順序:

```powershell
.venv\Scripts\python.exe scripts/build_world_japanese_names.py
.venv\Scripts\python.exe -u scripts/fetch_world_wikidata_names.py --trial
```

後者は約3.3万Wikidata IDを50件ずつ取得し、GeoNames ID（P1566）の一致を検証します。3秒以上の間隔、一般エラーは最大6回の再試行、応答キャッシュを使います。maxlag（サーバー同期遅延）は60秒ずつ待機し、同じバッチから継続します。不一致は `wikidata-review.json` に隔離。取得終了時に辞書を再構築し、その後 `model-input.json` の未対応名から既存Qwen 9Bで300件を試行します。LLM候補は未検証であり、公開用辞書に混ぜません。

現状・ログ: `wikidata-progress.json`、`pipeline.log`、`pipeline.err.log`。2026-10-09時点で900/33,168件、P1566一致の日本語名552件、ID不一致などの確認待ち15件。同期遅延で停止したため待機処理を修正して再開しました。以前の40〜90分という見積もりは撤回し、サーバーの同期遅延が解消するまで完了時間は未確定です。全件モデル翻訳の開始前に試行結果の品質と所要時間を確認します。


## 2026-10-10 追加の名称修正

韓国のスウォン・インチョン・テグ・テジョン・コンジュを公的日本語資料とGeoNamesの出典IDで照合し、カタカナ表示を追加した。出典付き表示修正は計26件、国別表記の確認待ちは476件。中国語・韓国語の原語別名を500対象中364件（中国249、韓国115）について抽出した。原語の漢字は日本語の慣用名の証明ではないため、未確認候補は表示へ自動採用しない。日本でも使う「湾」を誤って除外していた判定を修正した。

再現: `scripts/build_reviewed_world_names.py` → `scripts/research_native_aliases.py` → `node scripts/validate_name_overlays.cjs`。原語別名と候補・保留理由はGit管理外の `data/name-research/native-locale-review.json` に保存。元資料はGeoNames alternateNamesV2（CC BY 4.0）、SHA256と出典IDを保持。

世界319,897峰と国内44,459レコードの表示名を再検証。日本の対象英語地名と座標だけの表示は0件。海外の表示下限800以上の座標表示60峰は未解決で、近隣都市を遠距離から割り当てず、追加の地理資料による確認対象として残す。GitHub Pagesは未公開。
