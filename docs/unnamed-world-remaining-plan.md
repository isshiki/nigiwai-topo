# 残る4,454峰の名称調査

2026-10-12、第383回。全残件について、重複を除いた峰・POI対応表と住所Parquetを結合し、WGS84で峰から750m以内を再抽出した。住所IDは一意、結合漏れなし、全峰で従来の近隣POI件数と一致。名称の追加採用は0件、未登録は4,454峰。

## 全件の調査分類

分類は順序付きの調査目安であり、地名や位置の誤りを断定しない。複数の問題候補は別途flagsに保持する。

|優先理由|峰数|
|---|---:|
|近隣の参照地名に結び付かない|2,321|
|合意率・外部証拠の再確認|634|
|同じ正規化キーになる表記揺れ|566|
|参照点が1km超|367|
|同一座標への集中確認|282|
|地名欄の情報不足|194|
|住所欄の情報不足|85|
|複数参照地名の競合|5|
|合計|4,454|

大小文字・Unicode分解・記号除去で同じキーになる原文群を2,482組抽出した。原文は保持し、正規化だけでは地域同定・読み確定・採用を行わない。異なる行政階層や遠距離の同名地は統合しない。

## 次の順序

1. 参照候補がある1,615峰を、国と参照IDによる1,450グループで再調査する。密度順の調査リストを保存した。日本語の同じ表記だけで統合しない。
2. 表記揺れを確認し、公的な地域・施設住所と照合する。既存の一般採用条件は維持し、例外は個別の公式住所証拠を記録する。
3. 参照地名に結び付かない群を国別に調べる。最多のインドネシア754峰、米国437峰、韓国372峰、サウジアラビア363峰を優先する（これらは全分類を含む国別総数）。行政区域・地区名資料を候補とし、点の近さだけで市名を割り当てない。
4. 座標集中282峰の施設・住所・点位置を確認する。集中だけでは除外せず、誤りを裏付けられたPOIのみ別途密度再計算を検討する。
5. 確定分を辞書と画面用パッケージへ反映し、名前・推定表示・重複・世界全件の表示検証を実施する。

再現: `.venv\Scripts\python.exe scripts/classify_remaining_world_names.py`。
成果物はGit管理外の `data/name-research/unnamed-world/remaining-classification383.json`、`remaining-normalization383.json`、`remaining-reference-batches383.json`。実行用Notebookは同フォルダの `remaining-classification383.ipynb`。元住所や既存の採用辞書は変更していない。

全世界の調査は未完了。分類・候補生成を採用完了として数えない。

## 第384回：参照候補1,615峰の住所本文照合

全1,615峰について近隣POIを再抽出し、参照地名の原語名・ASCII名を単語境界付きで地名欄と住所本文に照合した。部分文字列や施設名を住所支持として数えず、競合参照地名も含む行は支持から除外した。地名欄の単語一致は行政階層をまたぐ可能性があるため、採用条件への自動昇格には使用しない。

結果は個別地理確認候補28峰、参照距離の確認377峰、座標集中の確認10峰、追加住所・外部資料が必要1,200峰。合計1,615峰。28峰は確定名称ではない。全件結果と単位ごとのPOI IDを `data/name-research/unnamed-world/reference-reconciliation384.json`、28峰のリストを `reference-shortlist384.json` に保存。

個別調査ではKemptvilleのCIBC（116 Prescott St、峰から68m）とDouvris（200 Sanders St、257m）を独立2施設・2発行元の公式住所で確認。247/303件の既存地名支持と合わせ、従来の個別公式住所方式で「ケンプトビル（推定）」を反映した。CIBCは公式検索本文を使用し、直接取得の失敗を記録。Douvrisは公式公開本文を確認した。読みは未確認の編集音写。累計901名称、未登録4,453峰。Kemptvilleの図書館の古い資料、東西が食い違う不動産店住所は採用根拠から除外した。

DharwadはAxis BankのATM住所を公式PDFで確認したが、MedPlus資料の都市欄・郵便番号と住所本文に食い違いがあり保留。Kotakの公式住所も元POIの街路と異なるため独立アンカーに数えない。[個別採用・保留記録](unnamed-world-batch384-review.json)。

再現: `.venv\Scripts\python.exe scripts/reconcile_remaining_reference_candidates.py`。同フォルダの `reference-reconciliation384.ipynb` からも実行可能。第383回の1,615峰を固定した調査スナップショットであり、Kemptville採用後の未処理参照候補は1,614峰。次は28峰の地域対応を外部資料で個別確認する。

## 第385回：28峰の外部資料による初回個別確認

28峰に対し自治体・施設運営者・州観光局等を検索し、近隣の元POIと照合した。3峰を採用し25峰は保留。一般的な街の存在だけを確認できたものは、峰と住所の対応が確定したものに数えない。全28峰の資料・保留理由は [個別確認記録](unnamed-world-batch385-review.json) に保存。

|採用した参考地名（読みは推定）|全POI本文支持|個別の公式住所確認|
|---|---:|---|
|スタンダード|27/31|Gates Agencies 811 The Broadway、図書館822 The Broadway|
|ロングビュー|34/40|図書館128 Morrison Place、学校101 Morrison Road|
|タインバレー|23/27|Dillon's 1329 Port Hill Station Road、Backwoods Burger 1327 Port Hill Station Road|

図書館等の直接取得が403・cache missの場合は公式検索本文を使用し、検証方法と限界を記録した。Longviewの学校は元POI名が学校区の親組織名であるため、正式な学校名の一致認定ではなく学校区が公開する同一住所を地名の照合に使用した。StandardのBroadway St/The Broadway、Tyne ValleyのPorthill/Port Hillの表記差も保持。

住所本文による支持の利用には、個別に確認した独立2施設・2発行元の住所を必須とする専用の採用方式を追加した。`scripts/reviewed_address_text.py` で元POIから支持ID・件数を再検証し、競合候補のある峰はこの方式では採用しない。支持率は従来の地名欄のみの割合とは異なるため、表示の根拠にも「地名欄・住所本文」と記載する。一般の既存採用条件を一括で緩めてはいない。

PavillionのPavilion KL等、Karaköyのトラム・店舗情報、Aladdinの異地域らしい施設名など、同名による誤対応の疑いを保留記録へ追加。名称も密度も自動で除外せず、位置品質調査を別途必要とする。

累計904名称、世界の未登録4,450峰。推定の日本語読みを確定発音として扱わない。25峰は追加の施設・住所・位置対応の確認が必要で、調査完了ではない。

## 第386–388回：保留25峰の追加調査

新たに5峰を採用し、対象保留は20峰。累計909名称、世界の未登録4,445峰。6手順全体は未完了で、残る住所照合・地域資料照合・位置品質調査を継続する。[全手順の状態](unnamed-world-investigation-status.json)。

- Innhavet「インハヴェット（推定）」: St1 Hamarøyveien3068とAVIS Nordsalten Sentralverksted/Straumenesの公式本文が元POIの住所に対応。旧Shell名はShell公式のノルウェー全店St1改称説明で補足。改称を独立施設として数えない。
- Minden「ミンデン（推定）」の2峰: 市街地峰はRising Thymes124BobcaygeonRoadとDominion Hotel113Bobcaygeon/MainStreet、高速道路沿い峰はSubway12621Highway35とCanadian Tire Gas12627Highway35でそれぞれ個別確認。元DominionのlocalityHaliburtonと公式Mindenの不一致は保存。同じ参照IDの地名として扱い、別都市名を創作しない。
- Ljungdalen「ユングダーレン（推定）」: ICA Ljungdalen700のApoteket公式代理店住所と、Berg自治体2025-03-13議事録8673-2024行にある観光協会Ljungdalen163の住所を照合。旧団体名と現行名の差は保持し、住所による地域対応として採用。
- Lanark「ラナーク（推定）」: 図書館75GeorgeStreetとLCBO99ClarenceStreet。75Georgeに同居する別組織を独立した住所アンカーに数えない。LCBOは公式検索本文を使用し直接取得失敗を記録。

個別の公式住所・方法・限界は `unnamed-world-batch386-anchor-plan.json`、`unnamed-world-batch387-anchor-plan.json`、`unnamed-world-batch388-anchor-plan.json` と各回adoptionsに保持。再現用 `scripts/apply_reviewed_address_text_batch.py --review <plan.json>` は採用件数と重複IDを検査し、適用済み計画の再実行を拒否する。失敗した住所検証はアンカー台帳を戻す。未処理20峰はGit管理外の `data/name-research/unnamed-world/reference-shortlist388-held.json`。

### 位置品質の個別証拠と試算

Karaköy LokantasıとGüllüoğluの公式運営者住所はイスタンブール。元POIの2件はlon35.5863/lat38.0393に置かれ、レストラン公式ページの埋め込み地図中心から約657.5km離れる。地図中心は厳密な施設座標の代用にせず、大きな離隔の確認に限った。他の65件を一括除外しない。

`docs/reviewed-poi-position386.json` に原ID・座標・住所・公式出典を固定し、`scripts/probe_reviewed_poi_positions.py` で現行の本番KDEを再現。元峰密度199件/km²が一致し、個別2件を除いた同一点の試算は191.54件/km²。これは峰選定やタイルの再生成ではない。配信中v5は変更していない。試算記録は `data/validation/reviewed-poi-position386-preview.json`。位置品質の修正配信と残る対象の確認は未完了。

## 第389–392回：さらに4峰の住所確認と3POIの密度試算

Trinity、Waterton、Redstone、スウェーデンLimaの4峰を追加採用し、元の保留25峰は9峰採用・16峰未確定。累計913名称、未登録4,441峰。全6手順の完了ではない。

- トリニティ（推定）: Bishop White Manor16Gallivan'sLaneとRising Tide Theatre40WestStの独立2運営者住所。宿の受付8WestStを宿の所在地として使わない。劇場資料は2025年ページで、現在の営業時間を認定しない。
- ウォータートン（推定）: Subway307WindflowerAvenueとWieners of Waterton301WindFlowerAve。公式郵便地名WatertonParkとParksCanadaのtownsite資料を対応させる。Pizza of Watertonは元303WindflowerからCameronFallsDriveへ移転したため住所アンカーから除外。
- レッドストーン（推定）: General Store292RedstoneBoulevardの州登録資料とRedstone Inn82RedstoneBlvdの州観光情報。前者は2021年資料、後者は公式検索本文の住所であり、直接取得本文には住所が出なかった。現在の営業・免許の認定はしない。
- リマ（推定）: Malung-Sälen自治体のLima UG/Kyrkbyn104と、林業組織Lima Besparingsskog/Kyrkbyn106の公式住所。ペルー同名都市と混同せず国SEの参照IDを使用。

資料・採用条件は各回 `unnamed-world-batch389-anchor-plan.json`、`unnamed-world-batch390-anchor-plan.json`、`unnamed-world-batch391-anchor-plan.json` とadoptionsに記録。未処理16峰は `data/name-research/unnamed-world/reference-shortlist392-held.json`。

位置品質の個別記録に、町中心の峰から28mに置かれたCameron Lakeの1POIを追加。ParksCanadaはCameron Lakeを町から16kmのAkamina Parkwayの終点と説明する。道路距離を直線距離として扱わず、湖の正確な代替座標を創作しない。地図範囲の追加確認と修正配信は保留。個別3POIによる試算で、Karaköy199→191.54件/km²、Waterton322→317.72件/km²を本番KDEで再現した。位置修正はまだv5に適用していない。

証拠: `docs/reviewed-poi-position392.json`、試算: `data/validation/reviewed-poi-position392-preview.json`。再現は `scripts/probe_reviewed_poi_positions.py --review docs/reviewed-poi-position392.json --output data/validation/reviewed-poi-position392-preview.json`。同調査フォルダの `reviewed-poi-position392.ipynb` からも実行可能。元ID・元座標を照合し、密度増加なしと元峰密度一致を検査。名称の採用と位置不整合の修正を区別して記録する。

## 第393–394回：1峰採用と矛盾する住所票の採用防止

Saulnierville「ソールニエルビル（推定）」を追加。NovaScotia州公開資料のClarence's Foodland10029MainStreetと、PharmaChoiceの9999Highway1の公式店舗住所を独立2施設として照合。MainStreet/Highway1の表記差を保持し、スーパーと同じ10029に登録されるメーカー各社を独立施設として数えない。州資料は2016年の歴史的住所証拠で、現在の営業認定ではない。[個別計画](unnamed-world-batch393-anchor-plan.json)。累計914名称、未登録4,440峰、元保留25峰は10採用・15未確定。

Lomondでは、Killin Cottage B&BのHelensburgh/LomondStreetという原住所がカナダの街名の支持として数えられていた。Scottish National LibraryのHelensburgh住所録にもKillin Cottage10LomondStreetがある。これは歴史的地名対応であり、現在の営業や正確な座標を証明しない。原ID5233341611d26cb3269412e5を住所支持として使わない個別の保留記録を `docs/reference-text-evidence-exclusions.json` に追加。19/22=86.4%から、その1件を支持から除くと18/22=81.8%。分母と密度は変更していない。試算は `data/validation/lomond-text-contamination394.json`。

`reviewed_address_text.py` はこの矛盾する票を含む採用を拒否する。既存の本文支持による採用13峰はすべて元POI照合を通過し、Lomondの誤採用拒否も検証した（記録 `data/validation/reference-text-guard394.json`）。これはPOIの密度除外ではない。地域対応の確定、位置品質の処置、全6手順の完了は継続調査。

第395–396回: Sainte-Agathe「サンタグアット・ド・ロトビニエール（推定）」を歴史的公式店舗住所と自治体住所から反映。累計915名称、地名未登録4,439峰、対象保留14峰。世界319,883峰・238地域×3表示下限の714チェックを再検証しPagesパッケージを同期。BandeirantesはUFG大学調査PDFの図3.2を画像で確認し、峰と街の位置の対応を追加証拠として記録したが、法的境界・個別POI位置を確定したとは扱わず保留。全6手順は未完了、配信密度はv5のまま。

第397回: Thorhild「ソーヒルド（推定）」を自治体庁舎801-1stStreetとCooperators2011公式事業所表6061Streetの独立住所照合で採用。住所のSt重複と歴史的資料の限界を記録。累計916名称、未登録4,438峰、対象保留13峰。世界319,883峰・714地域条件の検証とPagesパッケージ同期を完了。密度v5は変更せず、6手順全体は未完了。[個別照合計画](unnamed-world-batch397-anchor-plan.json)。

第398回: Leader「リーダー（推定）」を町公式1511stStreetWestとEatonia自治体広報2018年薬局広告1001stAvenueWestの独立住所照合で反映。水泳場の番地不一致は根拠に使わず保留。累計917名称、未登録4,437峰、対象保留12峰。世界319,883峰・714地域条件の検証と配信用パッケージ同期を完了。6手順全体は未完了。密度v5に変更なし。

第399回: Pacific Beachの宿泊施設45MainStreet公式本文と州立公園49SecondStreet公式検索本文を確認。近隣HighlandHeights参照候補が残るため採用ガードが拒否し、名称反映なし。独立施設住所だけで地域競合を消さず、位置範囲の追加確認を継続。累計917名称、未登録4,437峰、対象保留12峰、密度v5変更なし。

第400回: Getty TGN2116452の公開本文でHighlandHeightsをPacificBeach内のpart of inhabited placeとして確認。競合候補は地区と街の階層差。子地区票を街の支持票へ加算せず保持し、独立住所の根拠と併せた個別反映処理は次に実施。名称・密度は未変更、累計917名称、未登録4,437峰。

第401回: PacificBeach「パシフィックビーチ（推定）」を反映。GettyTGN2116452で確認した街/地区の階層を峰・参照ID・子地区POI座標に固定して検証。未確認の競合IDと子地区票の支持混入は拒否。独立2施設公式住所・支持率条件は維持。累計918名称、未登録4,436峰、対象保留11峰。密度v5変更なし、全6手順は未完了。

第402回: Linosa「リノーザ（推定）」を独立2事業者公式住所から反映。複合自治体名だけでなく島名と街路を照合し、Siremarの番地1は未確認、船着場と代理店は区別。累計919名称、未登録4,435峰、対象保留10峰。全世界319,883峰・714条件検証と配信用パッケージ同期完了。密度v5変更なし、6手順全体は継続中。

第403回: MilfordSound「ミルフォードサウンド（推定）」をターミナル公式住所と運輸省NZMF空港公式WGS84座標から反映。住所nullを保持し公式座標と元POIの差100m以内を必須検証。共有施設の会社数は加算しない。累計920名称、未登録4,434峰、対象保留9峰。世界319,883峰・714条件検証と配信用パッケージ同期完了。観測所等の位置品質確認は継続、密度v5変更なし。

第404回: Caramujoの議会公開2024街路名変更案174頁を取得し、22頁の本文と地図を画像で確認。第31条の街路起点は峰から約32m。DistrictCaramujoの直接的な地理証拠を追加。法案成立・座標測地系・学校旧住所の対応は未確認であり、施設独立2件の条件を満たしたとは扱わず反映保留。累計920名称、未登録4,434峰、対象保留9峰。

第405回: Caramujo「カラムジョ（推定）」を公的街路座標と本文住所支持27/30から採用。資料PDFハッシュ・峰座標・国・参照ID・街路起点50m以内を固定検証。施設2件確認方式とは別で、学校住所・法案成立・法的区域を認定しない。累計921名称、未登録4,433峰、対象保留8峰。全世界319,883峰・714条件検証と配信用パッケージ同期完了。密度v5変更なし。

第406回: Goias州2025公式資料のSaoJoseDosBandeirantes/NovaCrixas地名座標を確認。峰から269m。大学図3.2と別発行者の直接座標資料で地域対応を補強。街路起点50m条件とは別の地域代表点なので同方式で自動採用せず、図の範囲検証を続ける。28峰の初期候補から反映済みを除いた現保留8峰の一覧を再生成。名称・密度は変更なし。

第407回: Bandeirantes大学図3.2の経緯度格子と破線調査範囲を元解像度で再確認。保存した手動読取点から算出面積0.458km2（本文0.48km2）、峰の境界距離216.8m。80m内側縮小でも内側。州の代表点座標資料と合わせ地理対応を確認。80mは統計的誤差上限ではなく感度シナリオ、範囲は法的区域でない。点方式と混同せず範囲方式の再現検証を実装してから反映。累計921名称、未登録4,433峰、対象保留8峰。

第408回: SaoJoseDosBandeirantes「サンジョゼ・ドス・バンデイランテス（推定）」を大学地図範囲・州地名座標・住所支持46/54から反映。格子・範囲読取点とPDFハッシュを再検証、範囲外点の拒否も確認。行政境界や全POI位置の認定ではない。累計922名称、未登録4,432峰、対象保留7峰。世界319,883峰・714条件検証と配信用パッケージ同期完了。密度v5変更なし。

第409回: CensusTIGERweb2026地区境界MettlerCDP/GEOID0647164を公開APIから取得。峰の包含=True、境界まで39.57m。郵便表記Bakersfieldを元POIのまま保持し、統計地区としての地理対応を個別確認。名称反映は次の採用検証待ち。累計922名称、未登録4,432峰、対象保留7峰。

第410回: Mettler「メトラー（推定）」をCensus2026CDP境界包含と住所本文の照合から反映。GeoJSONハッシュ・GEOID・参照名・峰原座標を検証。境界外の近隣点は包含しないことも確認。郵便表記Bakersfieldは保持、全POI位置の認定ではない。累計923名称、未登録4,431峰、対象保留6峰。世界319,883峰・714条件検証と配信用パッケージ同期完了。密度v5変更なし。

第411回: Pavillion/WyomingのToyGarden/PavilionKLとTakeCareWellness/BaltejPavilion/Tamuningを公式モール本文・企業歴史的記事で個別確認。外国施設混入の2IDを位置品質保留候補へ追加。既存3IDと合わせ5IDを本番KDEで試算し元密度を再現。Pavillion峰地点74→66.13件/km2。新しい峰選定・配信タイルは未作成、密度v5は変更せず。名称累計923、未登録4,431峰、対象保留6峰。

第412回: 位置品質4IDのv6反映準備で、既存修正区画/配信パッケージとの重なりを確認。従来の増分生成は元の未修正区画を参照するため、そのまま流用すると過去修正を戻す可能性がある。v5基準の区画・峰を合成する処理を必要条件として記録。密度v5と名称923件は変更なし。

第413回: v6候補の4ID除外・3区画/2パッケージ再生成を完了。過去修正区画を最新版から合成し、v5の既存峰密度を再現。非対象ファイル38569件のSHA256一致と過去修正区画2件の継承を検証。v5は配信中のまま、新しい峰・名称対応・変更タイルの検証と公開切替は未完了。名称923件、未登録4,431峰、対象保留6峰はv5時点。

第414回: v6をS3/CloudFrontへ公開し、web/config.jsをv6へ切替。4IDの位置品質保留を反映。世界319,883峰・923名称・未登録4,431峰を再検証、714地域条件と変更247MVTタイルを確認。非変更2,945アーカイブは一致、過去13地点の修正も保持。7,052ファイル394,378,869bytes配信、Range/CORS確認済み。個別保留6峰とCameronLake位置確認など残候補の調査は継続。GitHubPages公開は未実施。

第416回: 画面説明を短縮しAboutへ集約。Foursquare登録情報・位置/営業状況の全件未検証・地名の非保証を短く明示。v6の未登録4,431峰はすべて800未満（最大798）、固定表示対象の未登録は0件と現データで確認。個別調査主体から国別区域の空間照合・参照ID単位の読み確認・検証バッチ反映へ方針を見直し。[効率化手順](unnamed-world-efficiency-plan.md)。

ユーザー指示（2026-10-12）: すべて・200m・800件/km2固定の表示対象に未登録が0件であるため、表示対象外4,431峰の追加名称調査を終了。保留6峰と未確定の位置品質資料は調査記録として保持。全件検証済みとは扱わない。画面説明短縮・About・表示説明の?を実装し、ブラウザで確認。
