# 世界の地名を日本語表記にするための事前調査

## 最新結果（2026-10-10）

今回対象の476参照名のうち452件を反映し24件を保留。中国の90件はその内数で全件確認済み。保留18峰の追加調査により5峰を追加補完。高密度60峰は累計47峰を補完し13峰を位置品質確認待ちとした。詳細は [保留18峰の調査](held-peak-investigation.md)。登録名・公的資料とCodex編集音写を区別して記録する。古い件数は各段階のスナップショット。詳細・再現手順は [名称品質の確認結果](world-name-quality-plan.md)。

調査日: 2026-10-08。LLMによる翻訳は保留。表示辞書・峰・密度・S3配信データを変更せず、公式仕様の確認と実データの照合を実施した。対象は計算済み峰の参照地名113,083件のうち、日本語未対応107,290件。

## 結論

まず日本語表記が登録済みの地理データから参照IDで補完し、食い違いを確認したうえで、未登録の地名にモデルを使う構成が適している。今回の調査で全世界の小さな町まで網羅し、表記が一意で、無料一括取得と公開アプリへの再配布に対応する単一の日本語辞書は確認できなかった。これは存在しないことの証明ではない。

GeoNamesとNatural Earthの照合により、16,377地名、85,107峰に登録済み日本語の候補を得た。まだ採用済みではなく、未対応入力107,290件も変更していない。Wikidataは追加補完が見込めるが全件の日本語ラベル取得は未実施。登録資料間でも表記差があるため、複数モデルの一致だけで正解とはしない。

## データと辞書の比較

|候補|日本語名・対応づけ|取得・利用|このプロジェクトでの評価|
|---|---|---|---|
|GeoNames alternateNamesV2|言語コードja、GeoNames ID、優先名・略称・通称・旧称・利用期間|公開ZIP、CC BY 4.0|最優先で調べる候補。現在の名称IDと直接結合できる|
|Natural Earth Populated Places|NAME_JA、GEONAMESID、WIKIDATAID|公開GeoJSON/Shapefile、Public Domain|主要都市を補う。全世界の小さな町の網羅用ではない|
|Wikidata|日本語label、GeoNames ID P1566、座標等|API・ダンプ、構造化データCC0|名称文字列で検索するよりIDで結合。日本語labelがない対象もある|
|ParaNames|Wikidata ID付きの多言語固有名、LOC分類|公開データと研究コード。採用する版のデータライセンスを個別確認|Wikidataをローカルで扱う候補。別の独立した典拠ではない|
|OpenStreetMap|name:ja、wikidata、geonames等のタグと座標|公開PBF等、ODbL|駅・地区の補完。世界抽出とGeoNamesとの照合が必要|
|日外『外国地名よみかた辞典』|原綴り↔カタカナ、国名、地名約4万件|出版物。公開再配布可能な一括データは今回確認できず|重要地名・表記差の確認用。書籍購入だけで一括再配布の許諾になるわけではない|
|朝倉『世界地名大事典』|都市・自然・歴史地名等、約4.8万の本項目（見よ項目込み5万強）|出版物。公開再配布可能な一括データは今回確認できず|個別確認用。今回の10万超の町村名をすべて覆うとは判断できない|
|GeoNLP/GeoLOD|識別子付き地名辞書、公開一覧は日本の歴史地名・行政区域・施設中心|辞書ごとの条件を確認|日本側の補完に有用。公開一覧から世界都市の日本語辞書は確認できず|
|CLDR|国・タイムゾーン代表都市の各言語表記|公開ロケールデータ|都市名全体の辞書ではなく、少数の慣用表記の補助候補|
|NGA GNS / USGS GNIS|地物の標準名・別名・座標|公開ダウンロード|対象同定・原綴り確認に有用。世界都市名の日本語辞書としての網羅性は確認できず|
|JMnedict / NEologd|固有名・読み、形態素解析用の辞書|公開辞書、それぞれのライセンス|GeoNames IDや座標付きの世界日本語地名辞書ではない。同名の別場所を判別する主資料にしない|

GeoNamesの通常のcities500のalternatenames列は言語コードを持たないため、日本語かどうかを文字種だけで決めず、言語コード付きの別名表を参照する。中国語の漢字名を日本語だと判断しない。

Natural Earthは名称にWikidataを使用していることを明記する。ParaNamesもWikidata由来である。これらの一致を、独立した3つの辞典が同じ読みを支持した証拠として数えない。

## 実データ照合

GeoNames公式alternateNamesV2.zip: 204,816,034 bytes。SHA-256は `data/name-research/geonames-ja-summary.json` に保存。日本語jaの別名行は世界全体で218,561行（都市だけではなく地物を含む、同じ地名の別表記も含む）。

- 今回使うGeoNames参照106,901件のうち、ja別名あり14,775件。
- 旧称・通称・略称・終了期間ありを除外して14,773件。
- 日本語文字を含まない4件も除外すると14,769件。
- 使用参照全体では856件に複数の非旧称等の候補がある。preferredフラグがあっても正しさの人手保証ではない。
- 使用峰数の多い未対応300地名では203件に上の日本語候補がある。

Natural Earth公式リポジトリのne_10m_populated_places.geojson: 7,342地点、日本語名あり7,342地点。現在の未対応GeoNames IDに4,773件が一致し、GeoNames候補にない1,608件を追加できる。和集合16,377地名、使用峰85,107件。全候補を採用できると仮定した場合の残りは90,913件で、実際の採用済み件数ではない。

GeoNamesとNatural Earthで、同じ参照IDの日本語名が完全一致しないもの344件。空白・中黒・カタカナ表記の差も含むので、344件の誤訳という意味ではない。例えばタイChumphonはGeoNames「チュムポン」、Natural Earth「チュンポン」。Stung TrengはGeoNames「スタンプトレング」、Natural Earth「ストゥントレン」。表記差だけの場合と実際の読みの誤りは確認を分ける。

GeoNames別名表のwkdtで、未対応106,901参照のうち33,176件に明示的Wikidataリンク、5参照に複数QIDを確認。リンクがあっても日本語labelがあるとは限らない。これを使えば大量の文字列検索やSPARQL逆引きを減らせる。

Wikidata P1566の標本調査: 使用峰数上位50件のうち46件がWikidataに結び付き、35件に日本語label。GeoNames/Natural Earth候補にない4件もこの小標本に含まれた。この標本は大都市寄りであり、全世界の網羅率には外挿しない。無作為50件はHTTP429で未取得。再試行も429だったため、以後の問い合わせを止めた。日本語ラベルの全件取得は未実施。

## モデル候補

|モデル|公式資料で確認した特徴|評価上の注意|
|---|---|---|
|Google TranslateGemma 4B/12B/27B|翻訳専用、55言語で評価。専用テンプレートと原言語・翻訳先言語の指定が必要|一般翻訳の評価であり、世界地名の慣用日本語名の正解率ではない|
|Tencent Hy-MT2 1.8B/7B/30B-A3B|日本語を含む多言語、用語指定・表記保存・構造化入力の例、GGUFあり|固有名の意味直訳を防ぐ指定と、言語別の検証が必要|
|bilibili Index-Translate 2B/9B/35B-A3B|2026-09-30公開、150言語、用語・フォーマット指定、公式GGUF|公開直後の候補。今回の地名での品質とローカル動作は未検証|
|既存Qwen 3.5 9B / Granite 4.2 8B|既存3試作の比較結果あり|30件の結果だけで世界全域の品質を決めない。新規候補との比較基準に利用|

新規モデルはダウンロードも実行もしていない。無料外部APIへの全件送信や有料APIの利用もしていない。地名特化モデルを調べるうえではParaNamesの固有名翻訳研究も候補になるが、既知の慣用名の欠落、参照元時点、別場所への誤対応を解決する万能モデルとは判断できない。

## 提案する次工程

1. 既存日本語名、GeoNames ja、Natural Earth、WikidataのID付き候補を併記した候補辞書を作る。複数候補・食い違い・旧称・QID多重対応はレビュー対象として残す。
2. Wikidataの全件照合はwkdt/P1566を使い、キャッシュ・取得間隔・再試行上限を設ける。429を受けたらRetry-Afterに従い、大量の公共API要求を避ける。ParaNames等のローカル資料も比較する。
3. 小さな町・複数言語の国・同名別地点・中国/韓国/アラビア文字・慣用名のある都市などを含む200〜300件の評価集合を作る。既知の別表記も許容正解として保持する。
4. 新規翻訳専用モデル1〜2種と既存Qwenを比較する。一致率だけでなく、違う街、意味の直訳、読みの破綻、慣用名の取りこぼし、回答なし、時間を記録する。
5. 辞書優先で補完し、残りだけモデル生成。候補は出典・生成器・確認状態を保存し、元表記を残す。背景の文字は対象外。

## 再現と保存先

```powershell
.venv\Scripts\python.exe scripts/research_geonames_ja.py
.venv\Scripts\python.exe scripts/research_external_names.py
.venv\Scripts\python.exe scripts/research_name_comparison.py
.venv\Scripts\python.exe scripts/research_geonames_links.py
```

取得・分析結果はGit除外の `data/name-research/`。公開物は変更していない。Wikidata標本の未取得は成功扱いにしない。HTTP429発生中に上記を繰り返し実行しない。

## 主な一次資料

- [GeoNamesダンプの仕様・ライセンス](https://download.geonames.org/export/dump/readme.txt)
- [GeoNames User Manual（wkdtを含む）](https://www.geonames.org/manual.html)
- [Natural Earth都市データ](https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-populated-places/) / [公式データ](https://github.com/nvkelso/natural-earth-vector/blob/master/geojson/ne_10m_populated_places.geojson) / [利用条件とWikidata由来名称](https://www.naturalearthdata.com/about/terms-of-use/)
- [Wikidata GeoNames ID P1566](https://www.wikidata.org/wiki/Property:P1566) / [データアクセスとライセンス](https://www.wikidata.org/wiki/Wikidata:Data_access) / [API制限](https://www.wikidata.org/wiki/Wikidata:SPARQL_query_service/query_limits)
- [ParaNamesの著者リポジトリ](https://github.com/bltlab/paranames) / [固有名翻訳の研究論文](https://aclanthology.org/2024.lrec-main.1103/)
- [OSMの日本語名称タグ](https://wiki.openstreetmap.org/wiki/Key:name:ja) / [利用条件](https://www.openstreetmap.org/copyright)
- [日外アソシエーツ『外国地名よみかた辞典』](https://www.nichigai.co.jp/PDF/2128-5.pdf)
- [朝倉書店『世界地名大事典』](https://www.asakura.co.jp/lp/timeijiten/index.html)
- [GeoNLP公開辞書一覧](https://geonlp.ex.nii.ac.jp/dictionary/)
- [CLDR代表都市表記の仕様](https://unicode.org/reports/tr35/tr35-dates.html)
- [NGA GNSダウンロード](https://geonames.nga.mil/geonames/GNSData/)
- [JMnedictの仕様](https://www.jmdict.org/enamdict/enamdict_doc.html) / [NEologd](https://github.com/neologd/mecab-ipadic-neologd/blob/master/README.ja.md)
- [TranslateGemma公式モデルカード](https://huggingface.co/google/translategemma-12b-it)
- [Tencent Hy-MT2公式モデルカード](https://huggingface.co/tencent/Hy-MT2-7B)
- [Index-Translate公式リポジトリ](https://github.com/bilibili/Index-Translate)



### 第140回：ポルトガルの薬局所在地を公的資料で再確認

Infarmedの2004年10月薬局一覧の本文1頁で、Farmácia Vargues LadeiraとSão Martinho das Amoreiras／Odemira／Bejaの対応を確認した。元POIの施設名・所在地に一致するが、街路番地は未記載であり、現在の営業や住所の証明にも使用しない。大学発音教材の通常取得は403で失敗し、本文・解答を読んだものとして扱わない。日本語名は追加せず、候補111峰・従来保留39件、累計751峰の反映を維持する。詳細は `unnamed-world-batch140-review.json`。

出典： https://www.infarmed.pt/documents/15786/17838/lista2_2004_10.pdf/14ff872f-b93b-489d-8169-33d70533a5ca?version=1.0


### 第141回：Allianceの一次住所照合

村公式の事業所一覧で元POI Battle River Credit Unionの117 Main St Wが117 Main St Westと一致し、役場POIの209 Main Stも村公式所在地と一致した。Main Street Medleyは元にEastの記載がなく、宿泊施設は203 Main St Wと公式206 Main St Eastが異なるため完全一致の根拠にしない。一般語allianceの発音は町の発音として確定せず保留。候補111峰・従来保留39件、反映751峰を維持。詳細は `unnamed-world-batch141-review.json`。

出典： https://www.villageofalliance.ca/business-directory/ および https://www.villageofalliance.ca/


### 第142回：Notre-Dame-du-Lausを追加

州地名委員会が現地読みを明記したNotre-Dame-du-Lausを「ノートルダム・デュ・ロー」と編集音写。元BMR店舗の106 Rue Principaleを運営者公式住所に番地一致照合。候補110峰・従来保留39件、反映752峰（編集651）、未反映4,604峰。録音聴取や公式日本語名とは扱わない。根拠は `unnamed-world-batch142-review.json`。


### 第143回：ケベック2地名の確認

Sainte-Justineの出版社日本語項目「サントジュスチーヌ」を直接確認したが国・位置がなく同定を保留。州政府279887の町位置は対象と整合。自治体旧事業所URLはJS必須となっており検索抽出を直接本文確認扱いしない。Saint-Hilarionでは自治体公式Services本文のLoisirs346Route138が元POI番地と一致した。両件の読み確定は保留し、候補110峰・従来保留39件、反映752峰を維持する。詳細は `unnamed-world-batch143-review.json`。


### 第144回：Sainte-Justineの薬局運営者住所

Familiprix運営者公開ページを通常HTTP取得し、元POIの135-7 Rue PrincipaleとSte-Justine QC G0R1Y0を本文・Pharmacy構造化データで確認。元の末尾#135まで一致したとは称さない。運営者データはlatitude46.406406を含み対象町に対応する。日本語辞書項目は所在地情報を欠くため読み同定を継続する。候補110峰・従来保留39件、反映752峰で表示追加なし。詳細は `unnamed-world-batch144-review.json`。


### 第145回：Nuevo Rosaritoの座標集中

元住所Parquetを再監査し、近傍bbox25件7座標のうち16件が完全同一座標だった。個別異住所の位置対応を支持件数だけで保証しない。Score33は北部PuertoNuevoの同名飲食店に対応する疑いがあり、自治体原文確認が必要。公的許可PDFのweb取得は容量制限、通常HTTP取得はタイムアウトで原文未読。誤った地名付与と未確認の除外を避け、110峰・39件を維持。詳細は `unnamed-world-batch145-review.json`、元行は `data/name-research/unnamed-world/nuevo-rosarito-coordinate-audit.json`。


### 第146回：Score33の別位置

醸造会社の公式取扱店ページ https://borderpsychobrewery.com/directory/score-33/ は店名・電話・店舗URLと案内先座標32.24229537021305,-116.93214462386194を掲載。元POIの座標との差は488.7km。地図本文未取得と掲載リンク座標の確認を区別する。現峰の位置支持根拠にこのPOIを転用しない。他施設全体の誤位置・峰除外はまだ確定していない。残110峰・39件、反映752峰。詳細は `unnamed-world-batch146-review.json`。


### 第147回：残候補149地点の座標集中再監査

元住所Parquetを約500mの緯度経度bboxで抽出して、完全同一座標の最大集中率を集計した。149地点中6地点で過半数が同一座標（Aduliena、Hagensborg、Sapezal、Denare Beach、Ejido Nuevo Rosarito、Sandy Bay）。円形近傍の件数と同一視せず、同一座標だけで誤位置とも断定しない。個別住所・施設位置の再確認を名前採用前のキューに記録した。件数は110峰・39件、採用752峰を維持。詳細は `unnamed-world-batch147-review.json` と `data/name-research/unnamed-world/remaining-coordinate-concentration-audit.json`。


### 第148回：Denare Beach役場番地

公式HTML参照の公開JS本文を取得し、512 7th Ave／PO Box70／Denare Beach SK S0P0B0を確認、元役場POI番地と一致。完全同一座標14施設は異なる街路住所を持ち、役場住所の一致を全施設位置の証明にしない。SandyBayは前回の診療所確認が既に存在し、再確認を新規成果に数えない。残110峰・39件、反映752峰で新規表示なし。詳細は `unnamed-world-batch148-review.json`。

2026-10-11 batch149: Leuglayをルグレとして反映。P. Lebel (1936), Origine et étymologie du nom de Leuglay, p35 のフランス語発音lœgléを原画像で確認。歴史的研究に基づく編集音写。原POI住所1 Ruelle de la Fermeを国立公園公式施設案内と照合。出典 https://bm.dijon.fr/documents/MEMOIRES%20CACO/1832-2001/1936-021-06-031-035-1376903.pdf および https://parcsnationaux.fr/fr/des-decouvertes/visiter-et-semerveiller/les-parcs-nationaux-accessibles-tous/parc-national-de-2 。累計753峰、今回の候補残109峰・従来保留39件、全体未登録4603峰。

2026-10-11 batch150: BygdsiljumのICA公式Robertsforsvägen4を元POIと照合。TranskriberのVästanträsk143は郵便都市と集落を区別。Sveriges RadioのISOF研究員地名解説録音を発見、未聴取のため読み確定は保留。根拠はunnamed-world-batch150-review.json。残109峰・39件、累計753峰。

2026-10-11 batch151: Bruzaholmをブルーサホルムとして反映。ISOF町の調査カード1964年原画像 https://www4.isof.se/NAU/bilder/_s2fx001/219212a1/p3/0000104a.pdf の発音記録と、企業公式 https://www.bruzaholmsstaldukar.se/ のBruksvägen5を元POIと照合。歴史的現地調査に基づく編集音写であり公式日本語名や現在の録音確認とは称さない。累計754峰、残候補109峰・従来保留38件、全体未登録4602峰。

2026-10-11 batch152: Lysvikをリュースヴィークとして反映。ISOFのFryksdals härad・Värmlandの現地発音調査カード（Sven Lagerlöf1905 Ulma517:34）原画像 https://www4.isof.se/NAU/bilder/_s2sx001/409122d1/p3/0000010a.pdf とCoop公式 https://catering.coop.se/varmland/?store=coop-lysvik のGamlaVägen40を原POIに照合。歴史資料による編集音写。現在録音・公式日本語名とは称さない。累計755峰、残108峰・38件、全体未登録4601峰。

2026-10-11 batch153: Långviksmonをロングヴィクスモーンとして反映。ISOF Björna調査カード1923年原画像 https://www4.isof.se/NAU/bilder/_s2yx001/622307c1/p3/0000138a.pdf とHandlarn公式 https://www.handlarn.se/butiker/storsjobygdens-lanthandel/ Lomvägen2を原POIに照合。歴史資料からの編集音写。Kälarneは1974年集落合併カードと1920年旧教区総称カード、Bispgårdenは1931年方言形カードを確認し、現名称と同一視せず保留。累計756峰、残108峰・37件、全体未登録4600峰。

2026-10-11 batch154: Furudalをフールダールとして1峰反映。ISOF Ore地名調査カード1922年・1932年の発音記録とVisit DalarnaのSnitths Hantverksbageri訪問住所Järnvägsgatan9を原POIに照合。歴史資料に基づく編集表記であり公式日本語名ではない。累計757峰、残108峰・36件、全体未登録4599峰。S3未更新。

2026-10-11 batch155追加調査：BygdsiljumのISOFカード4枚を照合。1927-28と1933の複数の方言採録を確認。1958カードはダム施設名で発音根拠から除外。一般形と方言形の転写を混同しないよう記号凡例の照合を次段階とし保留。残108峰・36件。

2026-10-11 batch156追加調査：HedekasのKrokstad地区の郵便局カードを原画像確認。発音なし、1944年Sv.ortf.参照あり。別地区の同名小屋を対象に混ぜない。日本語名は保留、次の資料照合先を記録。残108峰・36件。

2026-10-11 batch157：Daysland/Ryley/Vantage/Coronachを再調査。一般語・人名の読みと地域固有の読みを区別して保留。1991州地名資料と連邦地名登録を追加調査先として記録。新規採用0。残108峰・36件。詳細unnamed-world-batch157-research.json。

2026-10-11 batch158：公開州資料Place names of Alberta VolumeIII CentralAlbertaのOCRと原本PDFを取得。実際は1994年刊で前回書誌の1991年とは巻が異なる。Ryley/Daysland/Donalda/Allianceの位置と命名由来の項目を抽出。読みの確定は別途必要で採用0。残108峰・36件。原本ページ抽出を継続。

2026-10-11 batch159：Dayslandをデイズランドとして1峰反映。1994年州地名資料VolumeIII印刷68頁のDay命名由来とMerriamWebster day/land発音に基づく編集音写。Flagstaff観光案内のKaplersHomeHardware5038-50Streetと元POIを照合。現地録音の直接確認とは区別。累計758峰、残107峰・36件、全体未登録4598峰。S3未更新。

2026-10-12 batch160：Alliance CA ABをアライアンスとして1峰反映。州地名資料VolumeIII印刷3頁のOhio都市由来とMerriamWebster地名項目の命名元の発音に基づく編集表記。村公式信用組合117MainStWestと原POIを照合。カナダ村の現地発音直接確認とは区別。累計759峰、残106峰・36件、全体未登録4597峰。S3未更新。

2026-10-12 batch161追加調査：Irmaの命名由来と原MedianAutomotive4924 50Aveを提携店掲載住所に照合。人名の言語別読みを町名に無条件転用せず保留。残106峰・36件。

2026-10-12 batch162：CrystalCity命名記録と博物館住所を確認。原住所のSが掲載資料で省略される点を未解決として記録。PaymentsCanada名簿PDF取得失敗、直接確認の根拠にしない。編集候補クリスタルシティは未反映。残106峰・36件。

2026-10-12 batch163：CrystalCityをクリスタルシティとして1峰反映。州地名辞典PDFindex144の命名記録とMerriamWebster crystal/city発音に基づく編集表記。HistoricPlacesDays博物館218BroadwayStreetの案内リンク座標が原POIから45.7mで方向S省略の照合を補強。現地録音直接確認とは区別。累計760峰、残105峰・36件、全体未登録4596峰。S3未更新。

2026-10-12 batch164：FisherBranchをフィッシャーブランチとして1峰反映。HorizonHearing公式78TacheStと元施設住所を照合。現在の一時サービス休止と過去所在地を区別。州地名辞典PDFindex200とMerriamWebster fisher/branch発音に基づく編集表記、現地録音や由来確定とは称さない。累計761峰、残104峰・36件、全体未登録4595峰。S3未更新。

2026-10-12 batch165：Elm Creekをエルムクリークとして1峰反映。元Prairie Roots Co-op43 Church AvenueをRMofGrey公式の同名同住所と照合、公式施設座標とも約12m。州地名資料PDFindex184–185の河川由来とMerriamWebster elm/creek発音に基づく編集音写。現地実聴や公式日本語名とは区別。Ma’sの住所不一致は根拠から除外。累計762峰、残103峰・36件、全体未登録4594峰。S3未更新。

2026-10-12 batch166：CentralButteをセントラルビュートとして1峰反映。町公式IverMainPlace52 3rdAveWestと州選挙公示2016 PDF1頁52 3rdAvenueを元施設住所に照合。大学地名百科の中央丘を集合目印とした命名伝承と辞書central/butte発音に基づく編集音写で、モデルのブッテを訂正。当地実聴や公式日本語名とは区別。累計763峰、残102峰・36件、全体未登録4593峰。S3未更新。Milestoneの公式Affinity118MainSt住所とC.W.Milestone人名由来も確認したが人名の読みは引き続き保留。

2026-10-12 batch167：Turtlefordをタートルフォードとして1峰反映。元RCMP505MainStを警察公式TurtlefordDetachment所在地に直接照合。大学地名百科の河川渡渉地由来と辞書turtle/ford発音に基づく編集音写。当地実聴や公式日本語名ではない。LoonLakeは村公式LakelandAgencies418MainStreet住所を照合して読みを継続調査。累計764峰、残101峰・36件、全体未登録4592峰。S3未更新。

2026-10-12 batch168：ParadiseHillをパラダイスヒルとして1峰反映。元CreditUnionSynergy223MainStを運営2024年報印刷23頁PDFindex24支店一覧に一致確認。村公式history/contact/businessページを通常HTTPS取得して保存。HillofParadise命名説明は伝承と区別し、1887Klondike年代の疑義を明記。辞書paradise/hillに基づく編集音写で、現地実聴・公式日本語名ではない。累計765峰、残100峰・36件、全体未登録4591峰。S3未更新。

2026-10-12 batch169：CutKnifeをカットナイフとして1峰反映。町公式LucerneHotel211BroadStreetと元POIを再照合。大学地名百科に英訳CutKnifeからの丘名・町名由来を確認し、辞書cut/knife発音による編集音写を採用。先住民語原名の読みや当地録音実聴とは区別。図書館115/113番地不一致は根拠から除外して未解決と明記。累計766峰、残99峰・36件、全体未登録4590峰。S3未更新。

2026-10-12 batch170：Mossbankをモスバンクとして1峰反映。元TopShelfGrocery317MainStを町公式同名同住所に照合し、Nagel318/306番地不一致は根拠から除外。大学地名百科で1909郵便局から町への名称転用を確認。moss/bank辞書発音に基づく編集音写で、命名意図の語義や当地実聴は断定しない。町NameOrigin本文はOldWivesLake由来なので町名の証明には使わない。累計767峰、残98峰・36件、全体未登録4589峰。S3未更新。

2026-10-12 batch171：Hildrethの原図書館248CommercialAveを運営公開カタログに直接照合。JustinDesk/orgolab/BermudaTriangleを地域同定の主根拠から外し、モデルヒルドレズの読みは未確認として保留。CourtlandのLennox公式住所取得はタイムアウト、電話事業者PDFは404で追加根拠にしない。追加反映0、累計767峰、残98峰・36件。

2026-10-12 batch172：QuillLakeをクイルレイクとして1峰反映。元図書館54MainStを村公式施設一覧54MainStreetに直接照合。村公式の南方QuillLakes由来と辞書quill発音kwilに基づく編集表記を採用し、モデルキールレイクを訂正。湖名自体の語源と当地録音実聴は未確定。累計768峰、残97峰・36件、全体未登録4588峰。S3未更新。

2026-10-12 batch173：Imperialをインペリアルとして1峰反映。元CoopFoodStore206RoyalStを州政府2021施設一覧PDFindex30同名同番地に直接照合。大学地名百科のBritishEmpire由来と辞書imperial発音による編集音写、当地実聴や公式日本語名とは区別。LoonLake公式施設一覧の今回取得本文では以前の住所を再確認できず保留を維持。累計769峰、残96峰・36件、全体未登録4587峰。S3未更新。

2026-10-12 batch174：Granum原図書館310RailwayAveを運営公式に直接照合。植物学用語とラテン語の読みはAlberta地名発音の証明ではないため保留を維持。ChampionはATB旧所在地135MainStと現村庁舎同番地の施設同一性が未確認。追加0、累計769峰、残96峰・36件。

2026-10-12 batch175：Hanley町役場の原107LincolnStを町広報2014年9月12頁107LincolnStreetに照合。現行公式は107LincolnAveであり差異を記録。英国同名町由来の一次確認と読みが不足し保留維持。追加0、累計769峰、残96峰・36件。

2026-10-12 batch176：ShellLakeのLarkRestaurantとGobblesを村公式事業者一覧で確認。ただし番地記載なし。販売仲介物件記録112CarlEricksonAveを追加根拠として記録し、辞書shell発音と当地地名発音は区別して保留。追加0、累計769峰、残96峰・36件。

2026-10-12 batch177：ChristopherLake周辺29件を住所parquetから再抽出。公式村役場10CentralAvenueと原N方向付き住所は差を記録、RendezVousは施設名一致のみ。CA所在USPS280AMainStは施設種別矛盾として名前根拠から除外。道路263対235MainStreetWestも完全一致にしない。追加0、累計769峰、残96峰・36件。

2026-10-12 batch178：州地名辞典PDFindex426のMiami先住民集団由来とindex632のSomerset英国出身者由来・別伝承を確認。FloridaMiamiや別SomersetHouseの由来を転用しない。原施設公式住所と当地読みは保留。追加0、累計769峰、残96峰・36件。

2026-10-12 batch179：Somerset原32件を全抽出しRBC3093rdStreet、BSI3053rdStreet公式候補を発見。命名元英国SomersetのOxfordIPAを直接確認し編集候補サマセット。公式銀行本文直接取得未了、2011報告404を成功扱いにせず保留。追加0、累計769峰、残96峰・36件。

2026-10-12 batch180：Somersetをサマセットとして1峰反映。原RBC3093rdStを銀行2023年公式報告のATM設置表（PDFindex28、印刷29頁）に直接照合。撤去表もあるため現営業の証明とはしない。州地名辞典の英国出身地由来とOxford英国県名発音に基づく編集表記で、現地実聴・公式日本語名とは区別。累計770峰、残95峰・36件、全体未登録4586峰。S3未更新。

2026-10-12 batch181：ShellLakeをシェルレイクとして1峰反映。原LarkRestaurant112CarlEricksonAveを物件担当者HeatherSarrazin自身の掲載履歴に直接照合。村公式は施設名一致、番地なし。REMAX現行ページは一覧転送で番地確認成功としない。shell/lake辞書発音による編集表記、当地実聴・公式日本語名・命名語源ではなく米国同名都市由来も転用しない。累計771峰、残94峰・36件、全体未登録4585峰。S3未更新。

2026-10-12 batch181補足：Hanley大学地名百科本文は英国同名町由来・発音を記載しないことを確認。町広報の住所対応と区別し保留を維持。

2026-10-12 batch182：保留Courtlandをコートランドとして1峰反映。原TebowPlumbing410MainStをメーカーLennox公式販売店同施設同番地に直接照合、公式座標も当地。CMU辞書courtland K AO1 R T L AE0 N Dによる編集表記で当地実聴・公式日本語名と区別。大学史料のCortlandtNYと別資料CortlandNYの由来差は確定しない。累計772峰、残94峰・35件、全体未登録4584峰。S3未更新。

2026-10-12 batch182補足：HildrethのCMU辞書HH IH1 L D R IH0 THを確認。モデル末尾ズと無声THの不一致を検出し編集候補ヒルドレスを記録、町名への対応確認を継続。

2026-10-12 batch183：保留Hildrethをヒルドレスとして1峰反映。原図書館248CommercialAveを運営カタログに再照合。州歴史資料が旧所有者CarsonHildrethに敬意を表した命名と明記。CMU辞書HH IH1 L D R IH0 THに基づく編集音写でモデルヒルドレズの末尾を修正、当地発音・本人発音の直接確認とは区別。累計773峰、残94峰・34件、全体未登録4583峰。S3未更新。

2026-10-12 batch183追加調査：CMU公式辞書を研究用取得し残る候補を完全語一致で照合。39参照名に発音記載あり、data/name-research/unnamed-world/cmudict-remaining-leads.jsonに保存。米英辞書の語発音であり、カナダ・フランス等の当地発音、同名別地・人名の同一性を証明しないため自動採用しない。Granum/Edam/Miami等の地域差を含め住所と当地資料を個別確認する。

2026-10-12 batch184：Hanleyをハンリーとして1峰反映。原役場107LincolnStを町広報2014年9月12頁107LincolnStreetに再照合。CMU辞書HH AE1 N L IY0による編集表記でカナダ当地実聴・公式日本語名とは区別、英国由来は未確認なので根拠に含めない。FairfieldMcDonalds公式取得403で住所未確認、別施設を次の調査先とし保留。累計774峰、残93峰・34件、全体未登録4582峰。S3未更新。

2026-10-12 batch185：Milestoneをマイルストーンとして1峰反映。原AffinityCreditUnion118MainStを町公式FinancialServices同施設同番地に直接照合。DropIn施設名のみを109番地確認としない。CMU辞書M AY1 L S T OW2 Nによる編集表記で当地固有発音・公式日本語名・命名由来と区別。累計775峰、残92峰・34件、全体未登録4581峰。S3未更新。

2026-10-12 batch186：Ryleyをライリーとして1峰反映。原McPhersonLibrary5113 50thStを運営公式同名5113 50st RyleyABに再照合。CMU辞書R AY1 L IY0による編集音写で当地実聴・公式日本語名と区別。EJCAのRileyと現在町の同一性は未確定なので公開日本語用例に数えず別の未解決事項として保持。FairfieldDG公式店舗25783直接取得403、住所確認成功にしない。累計776峰、残91峰・34件、全体未登録4580峰。S3未更新。

2026-10-12 batch186補足：Gurley原消防署738 3rdStを州消防署名簿に直接照合。CMU辞書による編集候補ガーリーを記録、モデルグルリーとの相違を確認して次の個別調査へ。

2026-10-12 batch187：保留Gurleyをガーリーとして1峰反映。原消防署7383rdStを州2017消防署名簿に直接照合、地元GAVE団体で消防署と郵便局7433rdStを別施設として補確認。CMU辞書G ER1 L IY0による編集音写でモデルグルリーを修正。当地実聴・公式日本語名ではなくFredGurleyからの命名も断定しない。累計777峰、残91峰・33件、全体未登録4579峰。S3未更新。

2026-10-12 batch187追加調査：Follett原InterBank241SMainStを全原住所から抽出し銀行公式通常HTTPS本文に直接照合。原サンプル104SMainStとは別施設として記録。follett-address-evidence.jsonに保存し読みの確認を次に進める。

2026-10-12 batch188：Follettを編集表記フォレットとして1峰反映。原InterBank241 S Main Stを銀行公式本文と直接照合し、104SMainStの別施設と区別。TSHA町座標で補確認。CMU F AA1 L IH0 Tに基づく編集表記で当地実聴・公式日本語名ではない。累計778峰、候補91峰・保留32件、全体未登録4578峰。S3未更新。根拠：docs/unnamed-world-batch188-review.json。

2026-10-12 batch189：ChampionチャンピオンとMcCrearyマクリーリーの2峰を反映。前者は原自治体135MainStと自治体公式本文を照合。後者は原保育施設416 2ndAveと州名簿PDFindex137印刷138頁ID7921を照合、郵送先と別棟を区別。CMU辞書編集音写、当地実聴・公的日本語指定ではない。累計780峰、候補90峰・保留31件、全体未登録4576峰。根拠docs/unnamed-world-batch189-review.json。S3未更新。

2026-10-12 batch190：Tompkinsトンプキンズ、Chamberlainチェンバレン、Sheridanシェリダン計3峰を反映。州自治体名簿と会社・施設公式本文の原住所を照合。SheridanはColorado郡の座標をTSHAで確認し他州・Houston郡同名地を除外。CMU辞書による編集表記で当地実聴・公的日本語指定ではない。Roscoe原110NMitchellと現在自治体205NMitchellは異なり保留継続。累計783峰、候補87峰・保留31件、全体未登録4573峰。根拠docs/unnamed-world-batch190-review.json。S3未更新。

2026-10-12 batch191：LeeperリーパーとGrandyグランディの2峰を反映。消防会社と原CaratokeTobaccoの公式道路住所に直接照合。郵送先・建物共有の別店舗・峰から遠い補助施設を区別。CMUによる編集表記で当地実聴や公式日本語指定ではない。Dinsmore自治体住所100MainStを議事録で確認、モデルとCMU第一母音差は保留。Ewen州発音ガイド通常HTTPS403を記録し回避せず保留。累計785峰、候補85峰・保留31件、全体未登録4571峰。根拠docs/unnamed-world-batch191-review.json。S3未更新。

2026-10-12 batch192：Leaskリースク、Haffordハファード、Donaldaドナルダ計3峰を反映。元自治体事務所を公式15MainStreetに、原図書館17MainStと自治体106MainStを学区PDF印刷3頁に照合。Donalda保存済み自治体広告画像を再目視し元Catering5019MainStreetと確認、別店Stettlerを区別。CMU辞書編集表記で当地実聴・公的日本語指定ではない。Benitoは図書館原141と公式140、会社原Path83と公式Highway83Northの差を記録して保留。累計788峰、候補82峰・保留31件、全体未登録4568峰。根拠docs/unnamed-world-batch192-review.json。S3未更新。

2026-10-12 batch193：Roscoeロスコー、Swanvilleスワンビル計2峰を反映。前者は元学校1051stAveNEと学区公開計画表紙、州教育名簿を照合。原自治体番地差は別施設証拠で町確認し差自体を解消したとは主張しない。後者は原NilsonHardware207DegraffAveをメーカー販売店一覧に直接照合し現店舗公式で補確認。CMU辞書による編集表記、Swanvilleは構成語からの音写で地名全体の辞書登録・当地実聴・公的日本語指定ではない。累計790峰、候補80峰・保留31件、全体未登録4566峰。根拠docs/unnamed-world-batch193-review.json。S3未更新。

2026-10-12 batch193補足：McKenney原21101BoydtonPlankRdに対応する州DEQ公開資料の検索候補を得たが本文通常HTTPS取得は403。制限を回避せず同番地だけで原店名との同一性を確定しない。USDA公開裁定一覧のWallaceSuperMarket同番地を次の一次資料候補として調査する。

2026-10-12 batch194：Colborneをコールボーンとして1峰反映。原ColbornePublicLibrary6KingStWと施設公式6KingSt.West ColborneONを直接照合。自治体名簿のEast表記の相違は保持し、施設自身の資料を採用。CMU colborne K OW1 L B AO0 R Nによる編集音写で当地実聴・公的日本語指定ではない。累計791峰、候補79峰・保留31件、全体未登録4565峰。根拠docs/unnamed-world-batch194-review.json。S3未更新。

2026-10-12 batch195：Arborfieldアーバーフィールド1峰を反映。原BeelandCoOperativeAssociationLtd1stAveをCampbellCanada販促規約AppendixB同名1stAvenue ArborfieldSKに直接照合。同座標カードロック別名は独立証拠に重複計上しない。CMU構成語arbor/fieldによる編集音写で地名全体の辞書・当地実聴・公式日本語指定ではない。英国地名の由来同一性は主張しない。Irma5005 50thStも同一次一覧に照合したが人名言語差と町の読みは未解消で保留維持。累計792峰、候補78峰・保留31件、全体未登録4564峰。根拠docs/unnamed-world-batch195-review.json。S3未更新。

2026-10-12 batch196：Saltcoatsソルトコーツ1峰を反映。原公民館203GlasgowAveと自治体公式同施設203GlasgowAvenueを直接照合。自治体HistoryのScotland母港由来を補確認。CMU salt/coats構成語による編集音写で地名全体の辞書発音・当地実聴・公的日本語指定ではない。役場117AllanAveと郵送Box120は別施設。累計793峰、候補77峰・保留31件、全体未登録4563峰。根拠docs/unnamed-world-batch196-review.json。S3未更新。

2026-10-12 batch197：NewGermanyニュー・ジャーマニー1峰を反映。原小学校150SchoolStと運営SSRCE公式名簿150SchoolStreet NewGermanyNSを直接照合。連邦CGNDB CBBJP集落座標を補確認、Ontarioと南アフリカ同名地を区別。CMU new/germanyからの編集音写で当地実聴・公的日本語指定ではない。モデルゲルマニー不採用。原QuikMart5234Mainは一次照合未了で根拠に使わない。累計794峰、候補76峰・保留31件、全体未登録4562峰。根拠docs/unnamed-world-batch197-review.json。S3未更新。

2026-10-12 batch198：LoonLakeルーン・レイク、WillowBunchウィロー・バンチ計2峰反映。前者は原LakelandAgencies418MainStとWesternSurety公式代理店一覧を直接照合。村公式の検索結果と取得本文の差を解消したとはしない。後者は原SportsmansClub10CAveと州官報2020-09-25 PDFindex33印刷2468の10AveCを照合、短縮名と道路語順差を明記。2020法人資料は現在営業保証ではない。CMU構成語による編集表記で当地実聴・公的日本語指定とは区別。累計796峰、候補74峰・保留31件、全体未登録4560峰。根拠docs/unnamed-world-batch198-review.json。S3未更新。

2026-10-12 batch199：Kirkfieldカークフィールド1峰反映。原図書館7MunroeStと運営公式KirkfieldBranch同住所を直接照合。本部Lindsay住所は別施設。CMU kirk/field構成語からの編集音写で当地実聴・地名全体の辞書発音・公的日本語指定ではない。モデルキークフィールド不採用。原MackenzieInn現一次住所は未確認で採用根拠にせず、2023閉館の自治体公開資料もあるため営業保証をしない。累計797峰、候補73峰・保留31件、全体未登録4559峰。根拠docs/unnamed-world-batch199-review.json。S3未更新。

2026-10-12 batch200：旧保留Owensburgオーウェンズバーグ1峰反映。原CBHatfieldMercantile11461EMainStとIndianaFSSA公開名簿PDFindex79の同商店・住所を直接照合。博物館11431は別施設。消防署の図書館検索結果と取得本文の差を確認成功とはしない。CMU owens/burg構成語の編集音写で当地実聴・公的日本語指定ではない。累計798峰、候補73峰・保留30件、全体未登録4558峰。根拠docs/unnamed-world-batch200-review.json。S3未更新。

2026-10-12 batch201：DuckCreekVillageダック・クリーク・ビレッジ1峰反映。原HotMamasPizza61MovieRanchRdとKaneCounty郡観光局同施設61MovieRanckRdの番地・施設対応を確認。一文字の道路綴り差を保持し完全一致とはしない。CMU duck/creek/village構成語による編集音写で当地実聴・公的日本語指定ではない。累計799峰、候補72峰・保留30件、全体未登録4557峰。根拠docs/unnamed-world-batch201-review.json。S3未更新。

2026-10-12 batch202：Craigmontクレイグモント1峰反映。原図書館112WMainStとIdahoCommissionforLibraries2016統計PDFindex69同図書館・住所を照合。CMU craig/mont構成語の編集音写で、現地発音は実聴未確認、公的日本語名ではない。モデルクレイモンツは不採用。累計800峰、候補71峰・保留30件、全体未登録4556峰。根拠docs/unnamed-world-batch202-review.json、https://libraries.idaho.gov/files/Final%20Stats%2016.pdf 。S3未更新。

2026-10-12 batch203：Maryfieldメアリーフィールド、PickCityピック・シティ計2峰反映。原協同組合101MainStを公式2018CardlockGuide PDFindex251に、原DamBar35MainRdEをND州司法長官2025免許名簿PDFindex44に照合。CMU mary/field/pick/cityによる構成語編集音写で当地実聴・公式日本語指定ではない。Maryfield別銀行の閉鎖報告は営業裏付けに使わない。累計802峰、候補69峰・保留30件、全体未登録4554峰。根拠docs/unnamed-world-batch203-review.json。Colome一般発音動画の由来記述は市公式ChrisColombe由来と食い違い採用せず。Warooka日本語検索用例は自動翻訳の可能性を排除できず不採用、ColerainのOH同名町検索結果も不採用。S3未更新。

2026-10-12 batch204：Theodoreシオドア、PilotMoundパイロット・マウンド2峰反映。原Westland102MainStreetを村公式Businesses本文に、原FCL11BroadwayAveEをFCL公式PilotMoundHomeCentre住所に照合。原FCL略称と店舗表示名の差を記録。CMU theodore/pilot/moundによる編集音写で当地実聴・公式日本語指定とは区別。Canwood原RM621に対する公式641MainStreetの不一致、学校サイト取得タイムアウト、旧教育委員会PDF404を記録し保留。累計804峰、候補67峰・保留30件、全体未登録4552峰。根拠docs/unnamed-world-batch204-review.json。S3未更新。

2026-10-12 batch205：旧保留SaintGermainをセント・ジャーメインとして1峰反映。OneidaCounty2012VisitorGuide PDFindex5当該町saint jer-meynを直接確認、原Mobil102StateHighway70Eと地元商工会議所2026DestinationGuide PDFindex38 Mobil102Hwy70を照合。公式名簿で方向E省略を記録。別国のフランス語読みに置換しない。掲載当地英語読みからの編集音写で、当地音声実聴・公的日本語指定ではない。累計805峰、候補67峰・保留29件、全体未登録4551峰。根拠docs/unnamed-world-batch205-review.json、https://oneidacountywi.com/documents/oneida-county-visitor-guide-2012.pdf 、https://st-germain.com/wp-content/uploads/2026/01/26StGermainVG.pdf 。S3未更新。

2026-10-12 batch206：Eaglevilleイーグルビル、Grovespringグローブスプリング2峰を反映。原Subway21022 E State Hwy NとSubway公式21022 State Highway N、原MFA2135HighwayMと運営者公式2135StateHwyMを照合。道路方向省略・略記差を記録。CMU構成語の辞書発音による編集音写で、当地全語発音・音声実聴・公式日本語指定とは区別。累計807峰、候補65峰・保留29件、全体未登録4549峰。判断docs/unnamed-world-batch206-review.json。S3未更新。

2026-10-12 batch207：Consulの原ManleyBreadHoney105CentreStを州観光局の同名同住所に直接照合。ChristopherLake役場は2021自治体公聴会通知で10CentralAvenueSouth、原POIはN方向で矛盾するため単純一致を却下。読み・別施設照合を継続。追加0、累計807、候補65峰・保留29件。判断unnamed-world-batch207-review.json。

2026-10-12 batch208：Glenavonグレンアボン1峰反映。原RMChester104MainStとEnbridge2017公開縦覧場所PDFindex1の104MainStreetGlenavonSKを照合。Cambridge全語IPAから編集音写。当該カナダ町の当地発音明示・現在営業・公式日本語指定は断定しない。累計808、候補64峰・保留29件、全体未登録4548。判断unnamed-world-batch208-review.json。S3未更新。

2026-10-12 batch209：McKenney辞書読みを確認、当該町タグのForvo音声とUSDA店舗裁定C0248558の次の参照候補を特定。音声未実聴・正規USDA本文取得失敗で住所対応は未確定。Milverton企業自己掲載住所を候補化、AllbizのSilvertonBC見出し矛盾は根拠から除外。追加0、累計808、残64峰・29件。判断unnamed-world-batch209-review.json。

2026-10-12 batch210：McKenney裁定PDF本文は案件名のみで住所・町の記載なし、USDA住所一覧通常HTTPS403で認証未完了。Plantersville原Allphin15046Hwy105EとGermania現行Montgomery14888Hwy105WSte103の差を確認し同名認証を却下。旧所在地資料・別施設の確認を次の調査とする。追加0、累計808、残64峰・29件。判断unnamed-world-batch210-review.json。

2026-10-12 batch211：Plantersvilleプランターズビル1峰反映。原USPS8625PostOfficeRdをUSPS2021公式PDFindex8の同施設同住所TX77363に照合。CMU planters/villeから編集音写。疑わしい同住所スーパー群とAllphin現行住所差は採用根拠から除外、原POI品質全体は保証しない。累計809、候補63峰・保留29件、全体未登録4547。判断unnamed-world-batch211-review.json。S3未更新。

2026-10-12 batch212：Fairfieldフェアフィールド1峰反映。原AugustaCooperative5788NLeeHwyと運営公式の同施設同番地FairfieldVA24435を照合。CMU fairfieldから編集音写。郵便局原5586対公式告知5585の差は未解決で根拠から外す。累計810、候補62峰・保留29件、全体未登録4546。判断unnamed-world-batch212-review.json。S3未更新。

2026-10-12 batch213：Luseland大学地名百科の命名元LuseLandDevelopmentCo、Pangman村公式の命名元PeterPangmanを確認。読み資料を探す対象を具体化。Irma辞書英語語義にはAlberta村があるが英語IPAなし、別言語読みは転用しない。追加0、累計810、残62峰・29件。判断unnamed-world-batch213-review.json。

2026-10-12 batch214：Luselandルーズランド1峰反映。原町役場503GrandAveを町公式同施設同番地に照合。大学地名百科で命名元LuseLandDevelopmentCoを確認、CMU luse/landから編集音写。当地全語実聴とは区別。Pangman原CoopGasBar101MergensStを村公式同給油所同住所に照合、読みは保留。累計811、候補61峰・保留29件、全体未登録4545。判断unnamed-world-batch214-review.json。S3未更新。

2026-10-12 batch215：Smeaton原NorthHaven2ndAveNと運営者207-2ndAvenueNorthを部分照合。元番地は欠落。RainbowLodgeは州観光局でPiprellLake施設と確認し町中心の原座標証明には使わない。辞書直接ページ403、読みは保留。追加0、累計811、残61峰・29件。判断unnamed-world-batch215-review.json。
