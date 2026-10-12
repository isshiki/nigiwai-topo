# 地名未登録の世界峰をPOIから調査（2026-10-11）

対象は全5,356峰。初期画面の表示下限は800件/km²固定となり、対象峰はいずれも表示対象外ですが、名称の根拠を調査します。日本の地方・都道府県選択は常時表示し、選択すると地域も日本へ変更します。

## 調査の現状

保存済みPOIは住所欄を含まないため、まず2026-09-15固定資料の全254国別パーティションから峰の周囲を抽出しました。全5,356峰で周辺POIを検出し、対象IDは340,645件。元の国別ファイルと重複する中間のworld-source.parquetは集計対象から除外しています。

同じスナップショットから対象IDの住所・locality・region等の取得が完了。340,645件のID・座標が完全一致。住所あり171,321件、localityあり213,933件。取得IDと座標の完全一致を確認してから、GeoNames国別資料の名前・別名と照合します。施設名・住所は調査根拠として保存し、施設名に文字が含まれるだけで名称を自動採用しません。

## 完了した照合と第1回反映

空欄同士を地名一致と誤認する処理を修正して、全5,356峰を再照合しました。候補の裏付けあり1,305峰、追加確認候補1,211峰、施設・住所の追加調査2,840峰。国欄がないPOIは国別地名の照合ができず保留です。

登録日本語別名が一意、住所一致率90%以上、支持12件以上、参照点まで500m以内、異なるPOI座標8以上、住所あり8件以上を満たす63峰を確認して反映。同名地との混同を避け、国・州などを併記します。[採用した63峰と根拠](unnamed-world-name-decisions.json)。これは参考地名の判断であり、各POIの位置精度や行政区域への所属の認定ではありません。残り5,293峰は未反映です。800件固定の画面には、この低密度63峰も表示されません。

## 第2回反映と追加調査

さらに53峰を反映（登録日本語名9峰、Codexによる編集音写44峰）。計116峰、残り5,240峰。追加の登録日本語名9峰は住所一致85%以上・支持6件以上・参照点まで1km以内・異なる座標4以上・住所あり4件以上を個別確認。編集音写44峰は第1回と同じ強い住所・位置条件を満たし、原名との対応を記録しました。音写は公式日本語名の認定ではありません。[第2回の判断](unnamed-world-batch2-review.json)。Everglades Cityの登録別名「小さな町」は意味訳と判断して保留しています。

残り全峰に対し、近距離のGeoNames地点名と施設名・住所本文を照合。文字の部分一致は候補抽出だけに用い、採用には個別確認が必要です。生成物 `facility-name-review.json`、進捗 `facility-progress.json`、スクリプト `scripts/research_unnamed_facility_names.py`。

## 第3回反映

施設名・住所本文の追加照合は全5,240峰で完了し、2,691峰に調査候補が見つかりました。原施設名・住所を確認して19峰を追加。計135峰、残り5,221峰。[第3回の判断・保留例](unnamed-world-batch3-review.json)。近距離300m以内の参照点、12件以上の文字対応、8以上の異なる座標、3件以上の施設名対応、8件以上の住所本文対応と一致85%以上を確認しました。これらの条件は位置品質の完全な認定ではありません。

スレドボの日本語表記は[オーストラリア政府観光局](https://www.australia.com/ja-jp/things-to-do/seasonal-travel/best-ski-resorts-in-australia.html)でも確認。それ以外の第3回表記18峰は編集音写です。PavillionはTamuning等の別地域住所や一般的な商業施設名が混じるため採用せず、トルコ5候補・スウェーデン2候補も追加確認を保留理由に記録しました。

既存の住所一致・近距離参照の強い条件を満たす未反映535参照名を、ローカルOllama Qwen3.5:9bで日本語候補生成は完了。生成結果は `translation-qwen35-9b.json`、進捗ログ `translation.log`。モデルの一致だけでは採用せず、確認前の自動公開は行いません。

## 第4回：535参照名の候補確認

日本語候補を全535件確認し、431峰を追加。モデル表記から59件を修正しました。[全候補の採否・修正前後](unnamed-world-batch4-review.json)。別名の取り違え（Noblefordがバシャウ）、脱落・混同（Durbinがダブリン）、地名のLakeを実際の湖の名称へ変える例等を修正。モデルの不明20件と、読みの資料が足りない84件を保留しています。日本語文字だけで表記が正しいと認定した意味ではありません。

反映済みは計874峰（登録日本語別名74・公開資料の日本語表記29・確認した編集表記771）、未反映4,482峰。第4回の地理的対応は住所一致率90%以上・支持8件以上・参照地点まで500m以内・異なる座標8以上・住所あり8件以上を再検証。各候補の出典ID・原名・国・座標の一致と、原峰の位置・密度不変を確認します。

明示的な採用判断は[承認済み名称一覧](unnamed-world-name-approvals.json)を入力にして `scripts/build_unnamed_world_names.py` で再生成できます。モデル候補は自動で採用しません。全319,885峰の表示名と714条件の順位検証を再実行しています。

## 判断

峰から750m以内のPOIを確認。住所のlocality/post_townと同じ国の登録地名別名を照合し、峰から2km以内の参照点を候補とします。3件以上・60%以上の一致と複数座標の条件は調査の優先度分類であり、正しい場所だという認定ではありません。遠い同名地、住所欠損、代表座標への集中も記録します。未確定名は公開辞書に加えません。日本語表記は別途出典IDで確認します。

## 実行と記録

```powershell
.venv\Scripts\python.exe scripts/research_unnamed_world_pois.py
.venv\Scripts\python.exe scripts/fetch_unnamed_world_addresses.py
.venv\Scripts\python.exe scripts/audit_unnamed_world_addresses.py
.venv\Scripts\python.exe scripts/build_unnamed_world_names.py
```

取得処理は許可済みのgeoai-open-labの個人トークンをメモリで使用する読み取り専用処理です。値は保存・表示しません。

調査出力はすべてGit除外の `data/name-research/unnamed-world/` 配下：

- `targets.json`：5,356峰の元座標・密度。
- `local-evidence.json`：周辺POI数・施設名サンプル。
- `address-progress.json`：原住所の取得中／完了／失敗、ID検証結果。
- `addresses.parquet`：検証後の住所原資料。
- `audit-progress.json`：地名照合の進捗と分類件数。
- `address-name-review.json`：全峰の住所・施設名・地名候補・保留理由。処理完了後に生成。

国名登録、住所文字列、GeoNames参照点はいずれも誤りや古さの可能性があります。行政境界への包含や住所のジオコーディングを保証する処理ではありません。

## 第5回：保留104件の再確認（2026-10-11）

104件すべての住所支持・参照ID・位置・登録日本語別名を再確認しました。政府観光局の日本語表記2件、州政府・州立大学・歴史委員会資料の発音を使った編集音写8件を採用。累計576峰、未反映4,780峰です。保留94件は地理的対応の条件を満たしますが、読みの個別資料確認は未完了です。[全件の再確認記録](unnamed-world-batch5-review.json)。モデル出力を公式名として扱いません。今回追加も800件/km²未満で、表示下限は変更していません。

## 第6回：現地読みと次の住所候補（2026-10-11）

保留94件から発音根拠を得た8件を追加。残る86件の個別の読み調査は未完了です。住所一致率85%以上・支持6件以上・参照点1km以内・異なるPOI座標4以上・住所あり4件以上（既存の個別確認用条件）の231峰を抽出し、そのうちホールズ・ギャップ、ニュー・デンバー、セリグマンを公的日本語資料で確認・追加しました。個別POIの地域・施設・道路名も確認し、不一致POIは支持割合に含めません。累計587峰（登録72・公的日本語6・編集音写509）、未反映4,769峰。[第6回の記録](unnamed-world-batch6-review.json)。

残る229峰・226参照名は `scripts/prepare_next_unnamed_candidates.py` で候補入力を準備できます。`--run` ではローカルQwen3.5:9bで候補生成し、`next-translation-qwen35-9b.json` に逐次保存します。`next-translation-progress.json` とログで状態を確認し、失敗分は再実行で再開します。候補生成は読み・地域の確定ではなく、辞書への自動反映はしません。

候補生成器の文字種検証で失敗した応答が保存され得る不具合を修正しました。3回の再試行を使い切った候補は未完了に戻し、辞書には反映しません。`tests/test_translation_failed_character_validation.py` で不正な応答が保存されないことを検査します。今回の8参照名は不正候補を退避し、`--batch-size 2` で再生成します。追加採用したセリグマンを除く現在の候補対象は228峰・225参照名です。

## 第7回：候補228峰と従来の保留86件

候補225参照名・228峰のモデル入力と出力の原名・国・座標・参照IDを比較し、全峰の原POI住所の支持割合・参照点距離・異なる座標数を再検証しました。住所対応の条件通過は現地読みの確定を意味しません。外部の読み・表記資料で確認できた13峰を反映し、215峰は引き続き保留しました。モデルの誤読（Titonka、Chamois、Rudyard、Wellston、Penneshawなど）を修正しました。

従来の保留86件も住所対応を再検証し、CopemishとNaicamの2件を追加、残る84件は読みの調査中です。Meeteetse、San Jonは観光局資料で地域を確認しましたが、当該ページには文字の発音説明を確認できず保留しています。84件すべての外部資料調査が完了したわけではありません。Naicamは現地で公演した著者本人の記事、Lutsenは地域著者の発音資料に基づく編集音写で、公式日本語名とは区別しています。

累計602峰（登録72・公的日本語10・編集音写520）、未反映4,754峰。今回の15峰も密度800件/km²未満で、固定した表示下限では表示されません。位置・密度・等高線は変更していません。[第7回の住所と読みの記録](unnamed-world-batch7-review.json)。反映処理は `scripts/review_unnamed_batch7.py`、配信辞書の生成は `scripts/build_unnamed_world_names.py`。前者は既存採用と重複した場合に停止する、一回の明示的採用処理です。

## 第8回：保留215峰と84件の継続調査

299峰の原住所の支持割合・参照ID・国・参照点距離・異なるPOI座標数を再検証。今回の外部資料調査で13峰の読みを確認して反映しました。新候補から6峰を採用し残り209峰、従来の保留から7件を採用し残り77件です。全299峰の読みの外部調査が完了したわけではありません。

地域観光局・州観光ガイドのほか、現地取材者・訪問者・近隣在住者の一次記録を参照。これらは現地発音を確認した上での編集音写で、公式日本語名として扱いません。資料URLと資料の性格、原POI住所との対応を個別に記録しています。一般名詞・姓・別の国や州の同名地の発音は採用根拠にしません。Alsea、Bengough、San Jon、Killaloeは個人の訪問記録に基づくため、公的発音資料による確認より出典強度が低い点も明示しています。

Corolla、Acharacle、Ogemaなどモデル候補の誤読を修正。Ione、Uriah、Nevisなども同名の人・別地域からの推測を避けています。Lac-Etcheminは公的資料で地域を確認しましたが読みは未確定。Kulinについては同綴りの先住民集団の発音を、別の州の町に転用せず保留。Cuparはスコットランドとサスカチュワンで読みが異なる可能性があるため保留。人名の自動音声・赤ちゃんの名前サイト・モデルのIPAは確認資料に採用していません。

累計615峰（登録72・公的日本語10・編集音写533）、未反映4,741峰。今回も全追加峰が800件/km²未満。峰の位置・密度や等高線は変更していません。[第8回の個別記録](unnamed-world-batch8-review.json)。採用処理は `scripts/review_unnamed_batch8.py`。

## 第9回：州別発音ガイドと観光機関の発行資料

保留209峰と77件の住所条件・原参照IDの一致を再検証しました。AP通信のミネソタ州発音ガイドの保存版でGrygla、Bricelyn、Rothsay、Tofteを確認し、Tourism Australiaの2006年の発行資料でWyalkatchemを確認。5峰を編集音写として追加しました。公式日本語名ではありません。元の州・町名・原POI住所と対応する資料だけを採用し、人名や他州の同名地の発音は転用していません。

累計620峰（登録72・公的日本語10・編集音写538）、未反映4,736峰。保留候補209峰と以前の保留72件は読みの個別確認が未完了です。今回も追加5峰は800件/km²未満であり、固定下限の通常画面には現れません。密度・峰の位置・等高線は変更していません。[第9回の個別記録](unnamed-world-batch9-review.json)。採用処理は `scripts/review_unnamed_batch9.py`（重複採用を拒否する一回限りの処理）です。

## 第10回：地域ガイドと同名地の区別

保留209峰・72件の住所条件と原参照IDを再検証し、Wirrabara（ウィラブラ）、Walhalla（ウォルハラ）、Kulin（クーリン）の3峰を追加しました。Park Trekの地域ガイドと対象地域を訪問した著者の記録で読みを確認。米国のWalhallaやVictoriaのKulin集団の発音を転用していません。モデル表記と異なる場合は資料の読みを採用しています。公式日本語名ではなく編集音写です。さらに14参照地名について、姓・他国の町・河川・語源の発音など対象が異なる資料や裏付け不足を個別に記録し、保留を維持しました。

累計623峰（登録72・公的日本語10・編集音写541）、未反映4,733峰。対象の保留は207峰と71件で、読みの調査は未完了です。追加3峰はすべて800件/km²未満です。密度・位置・等高線は変更していません。[第10回の個別記録](unnamed-world-batch10-review.json)。採用処理は `scripts/review_unnamed_batch10.py`（重複採用を拒否する一回限りの処理）。

## 第11回：地域の発音資料と原住所の照合

Cabri（ケイブリー）は町公式サイト、Aguilar（アグウィラー）はDenver7のColorado発音ガイド、Marquez（マーケイ）はKathleen Rice AdamsのTexas地域発音記事に基づく編集音写です。公式日本語名ではありません。住所の支持数はそれぞれ41/45、23/27、36/37件。Aguilarの1件は州がAKとなっており、COの地域特定の根拠から除外しました。元POIの密度・位置・等高線は変更していません。

11参照地名では別地域・姓・語源・施設名・自動推定などと対象地名の現地読みを区別し、根拠不足を記録して保留を維持しました。累計626峰（登録72・公的日本語10・編集音写544）、未反映4,730峰。対象の保留は204峰と71件で、調査は未完了です。追加3峰は800件/km²未満。[第11回の個別記録](unnamed-world-batch11-review.json)。採用処理は `scripts/review_unnamed_batch11.py`（一回限り、重複を拒否）。

## 第12回：政府の読みと日本語の現地報告

Wikwemikongはカナダ政府First Nation ProfilesのWik-we-mi-kongからウィクウェミコンと編集音写。Riksgränsenは全日本スキー連盟安全対策委員会の2024年事業報告に基づきリックスグレンセン、Porjusは現地訪問記と観測記録に基づきポルユスとしました。いずれも自治体公式日本語名と断定せず編集表記として記録。元住所地名はそれぞれ28/31、28/29、52/52件で、ON・Norrbottenの住所と参照位置を再確認しました。

9参照地名は旧名・姓・別対象の発音や表記混在などを記録して保留を維持。累計629峰（登録72・公的日本語10・編集表記547）、未反映4,727峰。候補群は203峰と69件で未完了です。追加3峰は800件/km²未満。位置・密度・等高線は変更なし。[第12回の個別記録](unnamed-world-batch12-review.json)。`scripts/review_unnamed_batch12.py` は重複を拒否する一回限りの採用処理です。

第11回スクリプト作成時の広い文字列置換により、住所条件1000mが1100m、Kitscotyの参照URLのIDが1000156から1100156に変わっていました。本回で原値に修正し、第11回の採用3峰が元の1000m条件を満たすことを再検証しました。採用判断・表示名への影響はありません。

## 第13回：スウェーデンの地名発音辞典

Sahlgren・Bergman著、Svenska språknämnden刊『Svenska ortnamn med uttalsuppgifter』第2版（1968年、1979年刷）の各項目を原画像とOCRで確認。Alsterbro・Byxelkrok・Degerhamn・Glommersträsk・Junosuando・Lofsdalen・Ljugarn・Åmseleの8峰に編集音写を追加しました。辞典の所属県をPOI住所のKalmar・Norrbotten・Jämtland・Gotland・Västerbottenと照合。読み記号は2–3頁を確認し、oを常にローマ字のオ音と読むなどの誤りを避けています。数字は強勢・長母音位置を示すもので日本語名には含めません。古い標準語発音資料であり、現代の全方言を確認済みとはしません。

累計637峰（登録72・公的日本語10・編集表記555）、未反映4,719峰。対象候補群は198峰と66件で未完了です。密度・位置・等高線は変更なし。[第13回の個別記録](unnamed-world-batch13-review.json)、[辞典の読み・県との照合記録](unnamed-world-batch13-reading-evidence.json)。採用処理は `scripts/review_unnamed_batch13.py`。調査用の原ページ・画像はGit除外の `data/name-research/reading-sources/` に保存し、アプリには記事本文・画像を配信しません。


## 第14回：郷土資料と日本語の現地訪問記録

残る198峰と66件の住所条件を再検証し、Aignay-le-Duc（エニェ・ル・デュック）とOmeo（オメオ）の2峰を追加。前者は郷土研究の現地読みとIPAを照合、後者は町を訪れた日本語旅行記とDay Aveの施設住所を照合しました。公式日本語名ではなく編集表記です。Legal・Birtle・Recey-sur-Ourceは資料不足で保留を維持。

累計639峰（登録72・公的日本語10・編集557）、未反映4,717峰。対象候補群は197峰と65件で未完了。[個別根拠と住所](unnamed-world-batch14-review.json)。位置・密度・等高線は変更していません。


## 第15回：観光局の日本語資料

残る197峰と65件の住所条件を再検証し、ローレンス（NZ）とエバーグレーズ・シティ（US）の2峰を採用。政府・地域観光局の日本語ページが町を対象とすることを確認し、原POIのOtago・Lancaster Street、FL・Begonia St・郵便番号34139との対応を確認しました。公的資料の日本語使用表記であり法定日本語名の意味ではありません。

累計641峰（登録72・公的日本語12・編集557）、未反映4,715峰。候補群は195峰と65件で未完了。[個別根拠と住所](unnamed-world-batch15-review.json)。位置・密度・等高線は変更なし。


## 第16回：カナダの個別読み資料の再調査

195峰と65件の住所条件を再検証し、Boston Barを「ボストンバー」として追加。BC州を走行した日本語現地訪問記録とTrans Canada Hwyの原POIを照合した編集表記です。St. Brieuxは議会記録で現地・フランス語の読みが異なることが判明し、音韻未確定のため保留。Cuparも英国の読みを流用せず保留。Fairmont Hot Springsは観光局パンフレットの転載が見つかりましたが、原発行資料の確認は未完了です。

CBCの1959年地名発音辞典はInternet Archiveの書誌で同定しましたが、本文は閲覧制限・OCR非公開のため取得していません。公開地域資料の調査を続けます。累計642峰（登録72・公的日本語12・編集558）、未反映4,714峰。対象候補群194峰と65件は未完了。[個別根拠と住所](unnamed-world-batch16-review.json)。位置・密度・等高線は変更なし。


## 第17回：町の辞書項目と自治体資料の照合

194峰と65件の住所条件を再検証。Onanoleは町固有のon–a–(k)nollという読み解説と自治体の由来・所在地資料を照合し「オナノール」。WolseleyはSaskatchewanの町を含む発音辞書項目と町公式の由来・所在地資料を照合し「ウルズリー」。辞書・解説資料による編集音写であり、当該町の現地音声確認や公式日本語名とは扱いません。人名だけの読みを位置確認なしに町へ流用する採用はしません。

累計644峰（登録72・公的日本語12・編集560）、未反映4,712峰。候補群193峰と64件は未完了。[個別資料と住所](unnamed-world-batch17-review.json)。位置・密度・等高線は変更なし。


## 第18回：公開辞書の町語義と発音を照合

残る193峰と64件の住所条件を再検証。223の英語辞書項目を公開APIで収集して候補を探し、Legal（リガル）・Mundare（マンデア）・Stoughton（ストートン）・Morell（モレル）・Chéticamp（シェティキャンプ）の5峰を採用。各項目が当該カナダの町を明記することと、自治体・地域観光資料、原POIの州・住所との対応を個別確認しました。辞書発音の編集表記であり現地音声確認や公的日本語名ではありません。Cuparは辞書と現地投稿の読みが異なるため保留。

辞書の収集は候補探索だけで自動採用はしません。Git除外の `data/name-research/reading-sources/wiktionary-held-discovery.json` に調査用結果を保存。アプリに辞書本文・音声は配信しません。累計649峰（登録72・公的日本語12・編集565）、未反映4,707峰。候補群188峰と64件は未完了。[個別資料と住所](unnamed-world-batch18-review.json)。位置・密度・等高線は変更なし。

### 第19回：町の語義と住所の再照合

Bieber（ビーバー）、Acme（アクミー）、Vaughn（ヴォーン）の3峰を辞書発音に基づく編集表記として採用。Vaughnは学校住所のEast/West差を記録し、周辺26件の住所支持と町の参照位置で対応を確認。現地音声確認済みとは扱いません。累計652峰、未反映4,704峰、候補群186峰と63件。[個別根拠](unnamed-world-batch19-review.json)。S3の公開画面は未更新です。

### 第20回：町を特定した辞書発音と施設住所

Breton（ブレトン）、Borden（ボーデン）、Odessa（オデッサ）、Chambers（チェンバーズ）を編集音写として採用。辞書に当該国・州の町が明示されていることを確認し、自治体・保健施設・銀行の公式所在地と原POIを照合。辞書発音であり現地音声を聴取した確認ではありません。累計656峰、未反映4,700峰、候補群183峰と62件。[個別根拠](unnamed-world-batch20-review.json)。S3公開画面は未更新。

### 第21回：DresdenとHiggins

OntarioのDresden（ドレスデン）2峰とTexasのHiggins（ヒギンズ）1峰を編集音写として採用。TD銀行の公式住所、州自治体協会・地域行政の町資料を原POIと照合。ヒギンズの資料は私書箱でありMain St番地の完全一致とは扱いません。累計659峰、未反映4,697峰、候補群181峰と61件。[根拠](unnamed-world-batch21-review.json)。S3公開画面は未更新。

### 第22回：KincaidとWestport

キンケイドとウェストポートの2峰を編集音写として採用。州政府自治体名簿と施設公式住所を照合。Kincaidの政府住所は私書箱、Westportは17 Church Streetの完全一致を根拠に採用。累計661峰、未反映4,695峰、候補群179峰と61件。[個別根拠](unnamed-world-batch22-review.json)。S3公開画面は未更新。

### 第23回：米国の3峰

Crowder（クラウダー）、Orr（オーア）、Presque Isle（プレスクアイル）を編集音写として採用。対象の州・郡の辞書語義を確認。CrowderはChoctaw Nationの公式施設住所が原POIと一致。ほかは行政資料の町所在地と周辺POIの町名支持を照合し、サンプルの番地一致とは区別。累計664峰、未反映4,692峰、候補群176峰と61件。[根拠](unnamed-world-batch23-review.json)。S3未更新。

### 第24回：カナダの3峰

Arthur（アーサー）、Durham（ダラム）、Victoria（ヴィクトリア）を編集音写として採用。自治体・飲食店・チョコレート店の住所を原POIと照合。Ontarioの町Durhamと広域自治体、PEIのVictoriaとBC州都を区別。累計667峰、未反映4,689峰、候補群173峰と61件。[根拠](unnamed-world-batch24-review.json)。S3未更新。

### 第25回：McHenryとBrighton

マクヘンリー3峰、ブライトン1峰を編集音写として採用。McHenryはMarylandの町語義と飲食店・郡政府施設住所を照合し、姓のみのモデル候補による以前の保留を解消。BrightonはOntarioの町語義と自治体所在地・Main Streetを照合。累計671峰、未反映4,685峰、候補群169峰と61件。[根拠](unnamed-world-batch25-review.json)。S3未更新。

### 第26回：HopeとCaledonia

ホープとカレドニア2峰を編集音写として採用。HopeはAlaskaの町語義・地元資料、CaledoniaはNova Scotia西部の町語義・薬局公式9849 Hwy8・州観光資料Queens Countyを照合。同名の別州・別地域を区別。累計673峰、未反映4,683峰、候補群167峰と61件。[根拠](unnamed-world-batch26-review.json)。S3未更新。

### 第27回：NashとLeslie

ナッシュとレスリーの2峰を編集音写として採用。対象の町語義・州交通局資料・市公式郵送先を照合。Leslieは辞書の/s/変種を選択し、/z/変種の存在と唯一の現地発音未確認を記録。108 Commerce Streetは郵送先、物理所在地111と区別。累計675峰、未反映4,681峰、候補群166峰と60件。[根拠](unnamed-world-batch27-review.json)。S3未更新。

## 第28回の追加調査

ミッチェル（オンタリオ州）とミルトン（ノースカロライナ州）の2峰を町語義と自治体所在地に照合し、辞書発音に基づく編集表記として追加。個別番地の完全一致や現地録音による確定とは区別。サマセットは対象のカナダの町の発音資料が不足し保留。累計677峰、未反映4,679峰、候補群164峰と60件。[根拠](unnamed-world-batch28-review.json)。S3未更新。

## 第29回の追加調査

キラーニー1峰を追加。Herbert Fisheriesの21 Channel Streetを自治体施設案内で照合し、辞書の英語発音から編集表記を採用。原住所に混在した別の通りの番地は根拠にしない。Polandは銀行年報本文取得失敗、Veronaは当該町語義不足で継続調査。累計678峰、未反映4,678峰、候補群163峰と60件。[根拠](unnamed-world-batch29-review.json)。S3未更新。

## 第30回の追加調査

ハーフウェイ1峰を施設公式の170 South Main Streetに照合し追加。一般英語辞書に基づく編集表記で、現地録音の検証済みとは扱わない。Protectionは銀行公式302 N. Broadwayと原POIの一致を確認、Climaxは当該町語義を確認し保留継続。累計679峰、未反映4,677峰、候補群162峰と60件。[根拠](unnamed-world-batch30-review.json)。S3未更新。

## 第31回の追加調査

プロテクション1峰を追加。大学公開の地名資料で英語語義の由来を確認し、銀行公式302 N. Broadwayと原POIを照合。辞書発音に基づく編集表記で、現地録音の確認済みとは区別。累計680峰、未反映4,676峰、候補群162峰と59件。[根拠](unnamed-world-batch31-review.json)。S3未更新。

## 第32回の追加調査

NatomaのUnited National Bank、702 N. 2nd StreetをOCC評価書で一致確認。現銀行公式所在地も同じ。地域対応が確定し、残る課題は町の読み。Courtlandは対象町語義・由来を確認したが辞書の発音記載がなく、一次住所資料も追加確認する。今回は採用0、候補群162峰と59件。[根拠](unnamed-world-batch32-review.json)。表示辞書とS3は変更なし。

## 第33回の追加調査

Warwickは第2のwを発音する地域としない地域が辞書で区別され、Georgiaの町では未確定。GMA資料でWorth Countyの町と確認。Fairfieldは元POIの店舗公式URLを特定したが本文が取得できず保留。採用0、候補群162峰と59件。[根拠](unnamed-world-batch33-review.json)。表示辞書とS3は変更なし。

## 第34回の追加調査

ボイル1峰を追加。辞書の村語義と州議会記録の人名由来、村公式の地域を照合。英語辞書発音の編集表記で、個別番地一致や現地録音とは区別。累計681峰、未反映4,675峰、候補群161峰と59件。[根拠](unnamed-world-batch34-review.json)。S3未更新。

## 第35回の追加調査

Avonleaは小説・別州観光施設の日本語を対象町へ流用しない。州許可一覧本文は404で追加確認が必要。Hagensborgは16 POIが4座標に集中し、Lodgeの郵便地名と実所在地の区別を次回検証する。採用0、候補群161峰と59件。[根拠](unnamed-world-batch35-review.json)。表示辞書とS3は変更なし。

### 第35回追加の位置品質監査

Hagensborgは16 POI中13件が完全同一座標（81.25%）。異なる住所の施設がまとめられており、Lodge公式アクセスと照合して位置要確認と記録。全保留候補で、国・locality一致かつ峰から1km以内の取得済みPOIについて同一座標6件以上・集中50%以上を検査し6峰を抽出。これは調査候補であり、自動除外や修正座標の確定ではない。詳細はdata/name-research/reading-sources/remaining-exact-coordinate-concentration.json、hagensborg-position-review.json。表示・名称採用数は変更なし。

### 第35回追加の施設・住所照合

Adulienaは同じ学校の教室等25件が同一点に登録され、自治体学校規則で地域対応を確認。位置誤りと施設内登録の粒度問題を区別し、読みは保留。Sapezalは17件中12件が同一点で、CNESにより病院と診療所の異なる街路・番地を原POIと照合。市の由来資料と辞書発音も保存したが位置品質が未確定。採用追加0、候補群161峰と59件、累計681峰。表示辞書・S3は変更なし。個別根拠はbatch35-review.jsonのfocused_quality_reviewおよびdata/name-research/reading-sources内の個別監査JSON。

## 第36回の追加調査

アクシデント1峰を追加。町公式の英語名由来と辞書発音を照合し、原POIの418 S Main Stを店舗公式住所と一致確認。現地録音ではなく辞書に基づく編集表記。累計682峰、未反映4,674峰、候補群160峰と59件。根拠はunnamed-world-batch36-review.json。S3未更新。

## 第37回の追加調査

クーガーとクレセント2峰を追加。地域資料の対象地名と、Lone Fir Resort・Dollar General公式住所を原POIと照合。英語辞書に基づく編集表記で現地録音ではない。クレセントの/s/・/z/両形は採用理由に記録。累計684峰、未反映4,672峰、候補群158峰と59件。根拠はunnamed-world-batch37-review.json。S3未更新。

## 第38回の追加調査

レインボーレイク1峰を追加。Albertaの町公式の同名湖由来と英語辞書の読みを照合。教区公式9 Church Roadと原POIのSt Peter & St Paul Catholic Churchが番地・町・州で一致。町と離れた湖の座標を区別。累計685峰、未反映4,671峰、候補群157峰と59件。根拠はunnamed-world-batch38-review.json。S3未更新。

## 第39回の追加調査

ムーンビーム1峰を追加。自治体計画本文PDF79頁（冊子77頁）が英語moonbeamの意味と由来の公式文書未確認を説明。英語辞書発音と学校教育委員会公式55 rue St-Aubinを照合。原POIはAve表記で通り種別に差があり、完全文字列一致とは区別。累計686峰、未反映4,670峰、候補群156峰と59件。根拠はunnamed-world-batch39-review.json。S3未更新。

## 第40回の追加調査

イエローグラス1峰を追加。地名局の町レコード、州観光資料の湿地由来、英語辞書のカナダ発音を確認。元POI Libraryの213 Sourisを国立図書館・公文書館の名簿と番地・町・州一致確認。累計687峰、未反映4,669峰、候補群155峰と59件。根拠はunnamed-world-batch40-review.json。S3未更新。

## 第41回の追加調査

旧保留のマウンテン1件・1峰を追加。地名辞書がOconto County Wisconsinの町とCDPを明記し、町公式資料で対応地域を確認。教会公式会報8頁の14153 Church Roadと原POI Tabor Lutheran Churchを番地・町・州一致確認。米語辞書に基づく編集表記で現地録音ではない。累計688峰、未反映4,668峰、候補群155峰と58件。根拠はunnamed-world-batch41-review.json。S3未更新。

## 第42回の追加調査

旧保留クライマックス1件・1峰を追加。地名辞書のPolk County Minnesota語義と英語発音を確認。学校公式111 East Broadwayと元POI学校名・番地・町・州を照合。複数の学校名登録を独立学校数と誤解しない。市役所105 W Broadwayの一次照合は未完了で根拠に使わない。累計689峰、未反映4,667峰、候補群155峰と57件。根拠はunnamed-world-batch42-review.json。S3未更新。

### Vantage 追加照合

リゾート公式サイトで551 Main Stの住所を確認しましたが、元のリゾートPOIは住所欠損でした。同じ551番地の別施設と街路名の差を同一住所一致とは扱わず、保留を継続します。米国英語の辞書発音は確認済みで、モデル候補の長母音表記をそのまま採用しません。参照URLと判断理由はbatch42の当該項目に記録しました。

### 第43回：Kenoの読みと学校住所

州教育局のKeno Elementary Schoolの11110 Keno-Worden Rdと元POIを照合しました。地名由来資料と米国辞書のゲーム名発音に基づき、キーノーを編集表記として1峰追加しました。モデル候補ケノは採用しません。累計690峰、未反映4,666峰、対象候補154峰と57件です。採用根拠はunnamed-world-batch43-review.json。S3は未更新です。

### 第44回：Sumpterの読みと図書館住所

図書館公式の245 S Mill Stと元POI図書館245 Mill Stを照合しました。方位Sの省略を明記し、文字列完全一致とは扱いません。博物館の地名由来資料と辞書発音に基づき、サンプターを編集表記として1峰追加。累計691峰、未反映4,665峰、対象候補153峰と57件です。採用根拠はunnamed-world-batch44-review.json。S3は未更新です。

### Colomeの追加住所照合

州教育局の学校住所105 Carr Stと原POI学校105 W Carr Stの施設名・番地・通り・町・州を照合しました。公式は方位Wを省略しています。現地発音の資料は未確定のため採用しません。州司法局PDFはHTTP403で未読であり、その本文に対象地名が載るとは確認できていません。保留数は153峰と57件のままです。詳細はbatch44のColome項目に記録しました。

### 第45回：Cornucopiaの州資料と施設住所

州DNRの地名由来記述と辞書発音に基づき、コーナコーピアを編集表記として追加。郡の観光資料に記されたSiskiwit Bay MarinaとFo’c’sle Innの22580 State Hwy13を元POIと照合しました。2名称を独立2地点と数えません。累計692峰、未反映4,664峰、対象候補152峰と57件です。採用根拠はunnamed-world-batch45-review.json。S3未更新。

### 第46回：Trout Creekの施設住所と編集表記

Sinclair公式2954 Mt Highway200と元POIを施設名・番地・町・州まで照合。辞書の単語発音に基づきトラウトクリークを編集表記として1峰追加しました。creekには別の読みもあり現地地名発音の確定とは区別します。累計693峰、未反映4,663峰、対象候補151峰と57件です。採用根拠はunnamed-world-batch46-review.json。S3未更新。

### 第47回：Grand Viewの教会住所と編集表記

教会公式の54655 Raymond Ave, Grand View WIと元POIを照合し、教団公式2024年名簿でも確認しました。辞書のgrandとviewの発音に基づく編集表記「グランドビュー」を1峰追加。現地録音による地名発音の確定とは区別します。累計694峰、未反映4,662峰、対象候補150峰と57件です。採用根拠はunnamed-world-batch47-review.json。S3未更新。

### 第48回：Swan Valleyの施設住所と編集表記

元POI Snake River Roadhouseの2998 Swan Valley Hwyと公式サイトの番地・通り・町・州を照合しました。本文の現店舗名Snake River Side Channelとの名称差を記録し、同一ブランドとは断定しません。辞書のswanとvalleyの発音に基づく編集表記「スワンバレー」を1峰追加。現地録音の地名発音確定とは区別します。累計695峰、未反映4,661峰、対象候補149峰と57件。採用根拠はunnamed-world-batch48-review.json。S3未更新。

### 第49回：Silver Creek Nebraskaの教会実所在地

教団公式名簿PDF65頁のSilver Creek UMC実所在地509 4th Stと元POIを照合。郵送先PO Box331とは区別しました。辞書silverとcreekの発音を根拠に編集表記「シルバークリーク」を1峰追加。creekの発音には別形もあり、現地録音による地名発音確定とは区別します。WAの同名郵便局、Iowaの同名教会は除外。累計696峰、未反映4,660峰、対象候補148峰と57件。採用根拠はunnamed-world-batch49-review.json。S3未更新。

### 第50回：Sandy Lake Manitobaの店舗住所

Heritage Co-op公式の114 Railway Avenue Eと元POI Co-op Food Storeを照合。FCLとの同番地を独立2施設とは扱いません。辞書のsandyとlakeを根拠に編集表記「サンディレイク」を1峰追加。CGNDB GAYGZは集落でなく湖のため参照IDに流用しません。現地録音による地名発音確定とは区別。累計697峰、未反映4,659峰、対象候補148峰と56件。採用根拠はunnamed-world-batch50-review.json。S3未更新。

### 第51回：Larder Lake Ontarioの会社所在地

州公開報告GM65811のPDF2頁に記されたLarder Geophysics Ltd所在地14579 Government Roadを元POIと照合。ケベック州の調査対象地とオンタリオ州の会社所在地、郵送先PO Box219を区別しました。辞書のlarderとlakeを根拠に編集表記「ラーダーレイク」を1峰追加。現地録音による地名発音確定とは区別します。累計698峰、未反映4,658峰、対象候補148峰と55件。採用根拠はunnamed-world-batch51-review.json。S3未更新。

### 第52回：Lynn Lake Manitobaの人名由来と住所

町公式資料の役場503 Sherritt Avenueと宿515 Sherritt Avenueを元POIと照合し、町名のLynn Smith由来を確認。英語人名Lynnとlakeの辞書発音に基づく編集表記「リンレイク」を1峰追加。現地地名録音確定とは区別。BCの同名湖やCornishの小文字lynnは根拠にしません。累計699峰、未反映4,657峰、対象候補148峰と54件。採用根拠はunnamed-world-batch52-review.json。S3未更新。

### Sandy Bay SKの追加位置監査

Slim’s Cabinsの元POIを公式観光局の緯度55.434352・経度-102.444399と照合し、約13kmの位置差を確認しました。運営者もSandy Bayの道路終点から20kmのbasecampと説明。12件が完全同一座標に集中しており保留を維持します。一方、診療所の公式地図位置は元POIから約85mで、すべてのPOIが誤りとは判断しません。Bowls Clubと豪州同名施設の同一性は未確定。対象候補148峰と54件、表示データは変更していません。詳細はdata/name-research/reading-sources/sandy-bay-sk-position-review.json。

### Cumberland Houseの追加照合

州公式自治体名簿の役場所在地Cumberland Streetと元POI Town Officeを通り・町・州まで照合しました。番地がなく地点一致とは断定しません。辞書のCumberlandには英国地域別の異なる発音があり、カナダの当地での読みを確定する根拠としては未十分。由来資料にも異説の指摘があるため保留を維持。対象候補148峰と54件のままです。詳細はdata/name-research/reading-sources/cumberland-house-next-review.json。

### 第53回：Centennial Wyomingの公式住所と由来

郡公式2025年営業許可更新資料のThe Friendly Store2758 HWY130と元POIを照合。州図書館地名資料の1876年百周年由来と辞書発音を根拠に編集表記「センテニアル」を1峰追加。現地録音による地名発音確定とは区別し、Colorado同名市資料は転用しません。累計700峰、未反映4,656峰、対象候補147峰と54件。採用根拠はunnamed-world-batch53-review.json。S3未更新。

### Pick Cityの州公式住所照合

州司法長官局の2025年名簿PDF45頁でDam Bar35 Main Rd EとScott’s Bait and Tackle71 Main Rd Eを元POIと照合しました。後者の余分な末尾#Eを記録し、郵送先PO Boxは区別。市公式のLewis A. Pick由来を確認しましたが、英語姓の辞書項目に発音はなく、他言語IPAは転用せず読みを保留。対象候補147峰と54件、累計反映700峰のままです。

## 第54回：Armstrong Creekの公式住所照合

Laona State Bank公式所在地497 US Highway 8, Armstrong Creek WI54103と元POIの同名銀行・番地・通りが一致。Collinsの姓ArmstrongとMerriam-Websterのcreek発音に基づく編集表記「アームストロングクリーク」を1峰に追加しました。現地録音の地名発音確認ではありません。同住所の銀行は店舗内窓口のため、別地点の裏付けとして重複加算しません。計701峰、対象群は残り146峰と54件。[判断記録](unnamed-world-batch54-review.json)。

## 保留群の追加公式住所確認（Treherne・Ashern）

Treherneは自治体事業者名簿のSunrise Credit Union197 Broadway Stと原POIが一致しました。AshernのSiglunes District Libraryは公立図書館・自治体資料と番地61 Main Streetが一致する一方、原POIの部屋番号5と運営者の3が異なるため完全一致とは認定していません。両町とも現地読みの根拠は未確定で、モデルや同名人名の発音を転用せず保留。次の確認対象を現地音声と図書館部屋番号履歴へ絞りました。反映数701・残り146峰と54件は不変です。

## 第55回：Poland Indianaの年次報告書住所照合

銀行発行2008年次報告書PDF51頁にPoland支店8490 East State Road42を確認。原POI First Financial Bankの同番地・通りと一致し、辞書の当該Indiana町語義と米語発音に基づき編集表記ポーランドを追加。2008年所在地の裏付けで現在の営業継続を認定するものではありません。計702峰、対象群残り145峰と54件。[判断記録](unnamed-world-batch55-review.json)。

## Saint Marksの追加位置品質調査

Terminal21第四階と記されたKonayaが米国Saint Marks座標に登録されていることを確認。タイ政府観光庁の商業施設所在地とasianbeat店舗取材から不整合が疑われるため、名称付与の前に位置品質監査を進めます。同名Shields Marinaの2IDは住所・座標が同じで独立地点として裏付けません。未確認のまま削除はしていません。Ewen州発音ガイドの本文取得はHTTP403で未読のままです。今回新たな名称反映なし、残り145峰と54件。

## 第56回：Seagroveの公的日本語資料

滋賀県立陶芸の森の2020年1月11日講演記録PDF12頁にノースカロライナ州シーグローブを確認。Village Pottery公式205 East Main Stと原POI同名同住所も一致し「シーグローブ」を追加しました。公的資料の日本語用例であり米国自治体の公式日本語名認定ではありません。計703峰（登録72・公的13・編集618）、対象群残り144峰と54件。[判断記録](unnamed-world-batch56-review.json)。

## Nimmitabelの追加公式住所照合

Sundowner Cafe運営者サイトの検索抽出に45-47 Bombala Streetがあり、元POI45 Bombala Stとの照合候補を得ました。本文取得はタイムアウトで未読のため確定住所証拠とはしません。NSW観光局日本語版検索にニミタベルを発見しましたが、本文・翻訳方式の確認は未完了で採用していません。現地読み調査を継続します。計703峰、対象群残り144峰と54件は不変。

## 第57回：Nimmitabelの本文取得と反映

前回未読だった店舗公式サイトとNSW観光局日本語ページを取得。Sundowner Cafe45-47 Bombala Streetと原POI45BombalaStの範囲対応、日本語町名ニミタベルと所在地NimmitabelNSW2631を本文で確認し保留1件を反映。公的サイトの日本語用例であり正式地名認定・人手翻訳方式保証とは区別します。計704峰（登録72・公的14・編集618）、対象群残り144峰と53件。[判断記録](unnamed-world-batch57-review.json)。

## Warooka・Tooleybucの追加公式住所照合

WarookaはFoodWorks公式39 Main Street、TooleybucはMurray River Council防災計画PDF30頁のCaravan Park63 Murray Streetと元POIの施設・番地・通りを照合しました。両町の現地読み・公的日本語用例は引き続き保留で、モデル候補や同名人名の発音は採用していません。累計704峰、対象群残り144峰と53件は不変です。

## 第58回：Petit-Saguenayの自治体資料と編集表記

自治体2024収集カレンダーPDF2頁のCOOP MINUIT MOINS CINQ37 rue Dumasを元POIと照合。州地名委員会の自治体登録とフランス語辞書を参照しプティ・サグネを編集表記として追加。Quebecのpetit異音も記録し、現地録音や公式日本語名とは区別。計705峰（登録72・公的14・編集619）、対象群残り144峰と52件。[判断記録](unnamed-world-batch58-review.json)。

### 第59回：Baie-des-Sables

MRC de la Matanieの自治体住所20 rue du Couventを原POIと照合（原データの#132は未確認）。フランス語辞書の発音・複数形を参照し「ベ・デ・サーブル」を編集表記として追加。公式日本語名や現地録音の認定とは区別します。計706峰、対象群は残り144峰と51件。[判断記録](unnamed-world-batch59-review.json)。

### 第60回：Fairmont Hot Springs

Prana Wellness Spa公式4985 Hot Springs Rdを原POIの基礎住所と照合。月刊ふれいざー2018年4月号PDF34頁の日本語旅行記事にフェアモント温泉とFairmont Hot Springsの対応を確認。フェアモント・ホットスプリングスを編集表記として追加（この全カタカナ形の出典掲載・公式日本語名とはしません）。計707峰、対象群残り143峰と51件。[判断記録](unnamed-world-batch60-review.json)。

### Recey-sur-Ource追加照合

BANATICのSIVOM現住所はImpasse du Marché、元POIは7 place de Hôtel de Villeで一致しません。BP10は郵便箱として区別。町名全体IPAと古Larousse発音注記が見つかりましたが、原版凡例・現地発音の確認を残し保留を維持。次は移転履歴または別POIの一次住所と発音原資料を確認します。対象群143峰と51件は不変。

### Cremona Alberta追加照合

村公式で学校206 3rd Street Eastと図書館205 1st Street Eastを元POIと照合し、住所の対応を確認。ホテルの公式ページ同士には街路表記の相違があり、学校・図書館を確認根拠としました。イタリア同名都市由来は確認できましたが、対象町の現地発音・日本語一次掲載を引き続き調べます。対象群143峰と51件、採用707峰は不変。

### 第61回：Tärnaby

サーミ議会公式Industrivägen14を元POIと照合。コトバンク配信ブリタニカ百科事典の掲載日本語「ターナビー」を採用（自治体公式の日本語指定・現地録音認定とは区別）。計708峰、対象群残り143峰と50件。[判断記録](unnamed-world-batch61-review.json)。

### 第62回：Adaminaby

地元Lake Eucumbene商工会案内のSelwyn Star Lodge15 Denison Stを元POIと照合。NSW観光局日本語ページを取得し見出し・本文のアダミナビー表記を確認して反映。Old Adaminabyと区別し、掲載日本語を自治体法的名称・現地録音認定とはしません。計709峰、対象群残り142峰と50件。[判断記録](unnamed-world-batch62-review.json)。

### 第63回：Tarago

Ampol公式Braidwood Road2を元POIの番地・街路・町名と照合。NSW観光局日本語HTMLの見出しと本文のタラゴ表記を確認して反映。番地なしの同系列POIを独立した住所証拠とはしません。計710峰、対象群残り141峰と50件。[判断記録](unnamed-world-batch63-review.json)。

### Northcliffe WA追加照合

General Store運営者公式55 Zamia Stと元POIを照合し、公式掲載座標との差22.0mも確認。同住所Gather & Grazeは店舗内カフェで、二つの独立地点とは数えません。日本語検索にはGold Coastの同名施設が混在しており転用せず、対象町の読みは保留。対象群141峰と50件は不変。

### 第64回：Northcliffe WA

運営者の住所・座標照合に加え、WA観光局英語ページのhreflang ja-jpから正式な日本語URLを確認。取得HTMLの埋め込み日本語説明データにノースクリフ表記を確認して反映。日本語見出し・翻訳手作業・現地録音確認とはしません。計711峰、対象群残り140峰と50件。[判断記録](unnamed-world-batch64-review.json)。

### 第65回：ダーカン

自治体の文化財台帳にあるPutland Motorsの35 Burrowes Stと元POI住所を照合し、WA観光局正式日本語ページのダーカン表記を1峰に反映。台帳は過去の所在地資料で、現在の営業状況を認定しません。計712峰、対象群残り139峰と50件。[判断記録](unnamed-world-batch65-review.json)。

### 第66・67回：旧保留2件を反映

Tooleybucは自治体防災計画の63 Murray Streetと原POIを照合し、NSW観光局Murraywood日本語本文のトゥーリーバック表記を採用。宿泊地Goodnightと町名を区別。JerramungupはIGA公式31 Tobruk Roadと原POIを照合し、WA観光局正式日本語版の埋め込み説明にあるジェラマンガップ表記を採用。現地録音や法的日本語指定ではありません。Treherneの新検索は人名発音が中心で町名に転用せず、Warooka/Natimukの旅行サイト自動翻訳表記も単独採用しません。計714峰、候補群残り139峰と48件。[第66回](unnamed-world-batch66-review.json)・[第67回](unnamed-world-batch67-review.json)。

### ワルワ追加調査（未採用）

NSW観光局日本語ツアーページにワルワの表記を確認。Garageの38 Main Stに対応する広報紙広告は画像で文字層に住所がなく、旧PDF実取得先もエラーページのため未検証。検索の画像説明だけでは確定せず、移転後アーカイブまたは運営者住所を次に確認します。Natimukの宿泊サイトは同一ページでナティマック/ナティムクが混在し自動翻訳明記、Derrinallum検索のpronouncedは別名Gnurad-Gundidjの説明なので町の読みに転用しません。採用数714、対象群139峰と48件は不変。

### 第68回：ワルワを反映

元POI全件を見直し、Walwa Primary School4 Main Stが州政府School Building Authorityの4 Main Streetと一致。NSW観光局日本語本文のワルワを採用。Garageの旧広報紙画像は根拠に使わず、看護施設18 Main St #16と公式16–18 Main Streetも完全一致とはしません。計715峰、対象群139峰と47件。[判断記録](unnamed-world-batch68-review.json)。

### 第69回：フレストロプを反映

銀行原POIのSøndergade14をSparekassen Thy公式ATM住所と照合。大阪大学公開の新谷・大辺・間瀬編デンマーク語固有名詞カナ表記小辞典（IDUN SupplementNo2 2009）印刷85頁、PDF93頁index92に対象村Frøstrupのフレストロプ表記を確認。旧行政区分と同姓人名を区別し、モデル表記や法的日本語指定とは扱いません。計716峰、対象群139峰と46件。[判断記録](unnamed-world-batch69-review.json)。

### Burgsvik追加住所確認（読み保留）

元POI ICA Nära HoburgshallenのHoburgsvägen35をICA運営者公式と照合。Tangorinのブリスビク表記は原辞書・対象町対応を確認してから採用します。次はJMnedict原エントリまたは地名発音資料。反映数716、対象群139峰と46件は不変。

### 第70回：ブリスビクを反映

ICA元POI住所と運営者公式住所を照合。JMnedict2026-10-05版の公開JSONミラーentry5072079にブリスビク/Burgsvik/placeを確認。辞書に国・座標はないため位置は原POI・GeoNamesで別途確認しました。EDRDG出典とCC BY-SA4.0を画面に追加し、抜粋エントリを同条件で分離配布。辞書全件は配信せず、次の名称再生成時には最新版を再取得して採用エントリの変更も確認します。同辞書の他15ヒットはWarwick等の同名地域や表記差があり一括採用せず、候補ファイルに保存。計717峰、対象群139峰と45件。[判断記録](unnamed-world-batch70-review.json)。

### 第71回: Hines Creek

図書館原POIの212 10 Stを図書館公式・村役場の事業所一覧と照合。JMnedictのハインズクリーク表記を対象町に適用する編集判断を記録しました。辞書は国や座標を含まず、同名のAlaska河川を識別できないため、所在地の根拠とは分けています。FamilySearch本文は取得不可、自動翻訳百科事典は採用根拠から除外。累計718峰、候補群138峰・旧保留45件。[判断記録](unnamed-world-batch71-review.json)。

追加照合: Theodoreは学校住所が村資料に一致する一方で元POI localityがInvermay。Elm CreekはMa’s Drive-Inの元住所と現在の予約先住所が不一致。Hawkerは運行会社の時刻表で元店舗住所を確認。3件とも辞書が国・座標を含まず、同名他地域の読みを取り違えないため保留を維持しました。

### 第72回: Hawker

元店舗16 Wilpena RdをGenesis Transport公式時刻表と照合。文科省PDF65頁の南オーストラリア州ホーカー地区の表記と、豪州政府のWallerberdina Station/Hawker町の位置関係を照合しました。地区と町の範囲が完全同一とは扱わず、日本語表記の使用例として反映。累計719峰、候補137峰・旧保留45件。[判断記録](unnamed-world-batch72-review.json)。

### 第73回: Calayan

元地域POIのBabuyan Islands/Cagayan住所、港湾庁PDF画像のCalayan Port所在地、百科事典の港名カラヤンを照合して1峰追加。Kalayaanとは区別しました。個々のレストラン街路住所は外部で全件確認したものではありません。KausaniはHotel Sagar公式住所が一致する一方、日本語観光局本文の取得に失敗。Monheganは日本語用例に複数の表記差があり保留。計720峰、対象群136峰・旧保留45件。[判断記録](unnamed-world-batch73-review.json)。

### 第74回: Aiguilles

病院原POI225 rue Saint-Jacquesを運営者公式住所と照合。著者北村峠一の実訪紀行で対象村のエギーユ表記を確認し、編集表記として採用。公的日本語名・現地録音の根拠とは区別し、editorial_usage_urlを保存。元モデルアイニュールは採用しません。計721峰（編集622）、対象135峰・旧保留45件。[判断記録](unnamed-world-batch74-review.json)。Valldalの旅行サイト自動翻訳の表記差、LismoreのNSW/VIC同名地域、Suratのインド同名都市は対象を識別できる資料を確認してから判断します。

### 第75回: フランス3件の再照合

Molines-en-Queyrasは元銀行POIの235 rue du Serreが郵便局公式の所在地・銀行サービスに一致。日本語実訪紀行のモリーヌは短縮名なので全称の読みは未確定。La Chapelle-en-Valgaudémarはスポーツ店所在地の本文再取得と地名録音が必要。Lus-la-Croix-HauteはORTOLANGの現地調査資料42頁を発見しましたが文字層がなく、画像・原録音を次に確認します。自動翻訳サイトにある表記差は単独採用しません。今回の追加反映0、累計721峰、候補135峰・旧保留45件。[根拠・次の照合先](unnamed-world-batch75-review.json)。

### 第76回: Lus-la-Croix-Hauteの画像確認

ORTOLANG実取得PDF41頁（印刷203）の会話は風の呼び名が対象で、町名の発音は確認できませんでした。Wiktionnaireも発音欄が未登録。元キャンプ場住所l’Allevaは地域自然公園公式の840 route de l’Allevaと対応し、元POIに番地がない点を記録。読みは引き続き保留、次は地方観光局・自治体の音声資料。採用721、残る候補135峰・旧保留45件。[画像確認結果](unnamed-world-batch76-review.json)。

### 第77回: モリーヌ（ケーラス）

元郵便銀行POIの235 rue du Serreを公式郵便局所在地・銀行サービスと照合。日本語紀行のモリーヌと地域名ケーラス、観光局のMolines短称を照合し、同名他地域を識別する編集ラベル「モリーヌ（ケーラス）」を採用しました。正式名称全体の現地発音や引用元翻訳書を直接確認したとは扱いません。計722峰（編集623）、対象134峰・旧保留45件。[判断記録](unnamed-world-batch77-review.json)。

## 第78回：カナダの住所と実訪日本語用例

Bruce Minesは地域観光記事の9172 Hwy17と元店舗住所が一致。オンタリオ州の実訪記の日本語・英語併記から「ブルース・マインス」を編集表記として反映しました。現地録音や法定日本語名の認定ではありません。AvonleaとGogamaは一次資料で住所対応を確認しましたが、読みは保留。計723峰（編集624）、対象133峰・旧保留45件。[判断記録](unnamed-world-batch78-review.json)。

## 第79回：同名別地域の除外と住所の再照合

Lismoreの薬局32 High StはVIC地域サイト本文と一致しました。NSWの日本語名は別都市なので転用しません。Valldalの企業登記・自治体計画、Suratの団体住所は新たな照合先を記録しましたが、本文未取得部分を確定扱いにはしていません。今回追加0、計723峰、対象133峰・旧保留45件。[個別の次の調査先](unnamed-world-batch79-review.json)。表示変更はありません。

## 第80回：Valldalの一次資料本文

自治体計画PDF16頁でFjellro TuristhotellとSyltegata、企業登記本文で同道路・旧Fjellro名を確認。取得資料を保存しました。日本語紀行で読めた表記はGudbrandsjuvetの滝を指すため町名へ自動転用せず、別の町名用例の本文確認を続けます。追加0、計723峰、対象133峰・旧保留45件。[照合記録](unnamed-world-batch80-review.json)。

## 第81回：北米の原施設住所

ChemultのDawson House Lodge109455 Highway97NとWawanesaのRBC銀行147 4thStを資料本文で確認。Wawanesa保険会社の同町創業は確認できましたが会社名の日本語用例を町の現地発音認定とは扱っていません。Valldal実訪記の未取得本文は403であり回避しません。追加0、計723峰、対象133峰・旧保留45件。[詳細と次の調査先](unnamed-world-batch81-review.json)。

## 第82回：NRK地名発音辞典の対象照合

NRK辞典本文を取得。Valldal項目は別位置の農場ですがSylte項目は対象村の座標と対応。Namdalseid項目もGeoNames参照の座標・集落種別に一致します。1960年頃の発音記録という注意を保持し、音価と原施設住所を次に確認します。追加0、計723峰、対象133峰・旧保留45件。[新たな根拠資料と判断](unnamed-world-batch82-review.json)。

## 第83回：Namdalseidの読みカードと郵送先問題

NRKカードを目視確認。一方、ホテルのTrøavegen14は公式登記の郵送先で実施設所在地Sjøåsenとは異なると判明。住所文字の一致を位置一致と誤認しないため、このPOIをホテル所在地の確認根拠から外して別施設を調べます。元データの密度・座標は変更していません。追加0、計723峰、対象133峰・旧保留45件。[個別根拠と次の確認](unnamed-world-batch83-review.json)。

## 第84回：Namdalseidを反映

自治体学校の同名施設と訪問住所、参照座標と一致するNRK歴史発音カードを照合し「ナムダルセイド」を編集音写として採用。末尾dの任意性と1960年頃の記録である点を明記。ホテル郵送先は位置根拠にしません。計724峰（編集625）、対象132峰・旧保留45件。[採用判断](unnamed-world-batch84-review.json)。

## 第85回：Gäddedeを反映

運営会社のStorgatan20と元Kiosk&Taxi住所、NRKのJämtland対象発音表記を照合して「イェッデデ」を編集音写として採用。モデルの語頭ガは不採用。計725峰（編集626）、対象131峰・旧保留45件。[採用判断](unnamed-world-batch85-review.json)。

## 第86回：Venjanの政府店舗住所と方言辞典

政府TSFS2014:29 PDF59頁と元VenjansHandelのTennängsvägen5が一致。方言辞典PDF56頁は教区・湖を定義し複数地域の読みを掲載するため集落名の編集音写は保留。Hedekasは業界団体の郵送先が別市で施設所在地の確証には用いません。追加0、計725峰、対象131峰・旧保留45件。[根拠と次の確認](unnamed-world-batch86-review.json)。

## 第87回：Glennallenの施設住所と日本語講演資料

American Legionの元POI住所186 Glenn Hwyを、アラスカ州教育局の施設一覧（American Legion Post 27 Hall、Glennallen AK 99588）と照合。Greg Jones（Alyeska Pipeline）の公開日本語講演資料PDF2・3ページの「グレンナレン対応基地」を確認し、グレンナレンを編集表記として追加。基地の位置そのものを峰と同一視せず、地域の名称使用例として参照する。公式日本語指定・発音録音とは区別する。公開講演資料に対応する出典種別を生成コードに追加し、実訪記という誤った説明を付けない。

追加1峰、計726峰、未登録4,630峰。この候補群は130峰と45件。Venjanの方言辞典は教区・湖を説明し集落の標準読みに直接対応しないため保留。Furudalの電話料金表の日本語表記は周辺項目に不自然な訳があり、単独で採用しない。

住所：https://education.alaska.gov/apps/AlternateTestCenter/Search?DistrictId=34
日本語講演：https://www.pcs.gr.jp/doc/jsymposium/2010/Mr_Greg_Jones_PPT.pdf

## 第88回：Monheganの日本語公的記事とホテル住所

元POI The Island Inn（4c5f11b1048b9521d0252578、1 Ocean Ave）を州観光局Visit Maineの同名・同住所・同島に照合。運営者も島の位置と港を説明する。郵送先PO Boxを所在地としない。自治体国際化協会の2015年6月号、酒井晋一郎の記事PDF7頁（印刷8頁）本文と画像で「メーン州モンヘガン島」を確認して追加した。掲載日本語表記を使用し、公式な標準表記指定や発音実聴とは主張しない。Brackett店舗の旧販売店PDFはログイン転送となり、住所の直接確認根拠としては採用せず別施設で補った。

追加1峰、累計727峰（登録日本語別名72、公開資料の日本語表記28、編集表記627）、未登録4,629峰。この候補群は129峰と45件。原位置・密度は変更していない。

住所：https://visitmaine.com/organization/the-island-inn/4259/
日本語記事：https://www.clair.or.jp/j/forum/forum/pdf_308/04_sp.pdf
同回にKälarneも再調査。自治体2024年投票所資料のHotell Östjemten、Stationsvägen 6を元POIと照合。ISOF辞典は集落の同一性と駅名由来を説明するが直接の読みはなく、現地音声の確認対象として保留を維持。

## 第89回：Cremonaの村公式住所と全酪連の産地報告

アルバータ州CremonaのBumper to Bumper（原POI4e371c141838d056d26ee5bf、126 2 St W）を村公式事業者一覧の同名・同番地に照合。KC Foodsも214 Railway Avenue Westが一致するが元区画5は公式資料にないため断定しない。ホテルのRailway Avenueと2nd Streetの住所差異は一致として扱わない。全酪連の2022年11月号No.686 PDF20頁はカナダ産チモシーの産地を「アルバータ州中部クレモナ地区」と明記する。同州の産地名用例を村の編集表記に使用し、正式日本語指定や発音録音とは区別する。

追加1峰、累計728峰（登録日本語72、公開資料の日本語表記28、編集表記628）、未登録4,628峰。対象候補は128峰と45件。原位置・密度は変更しない。

住所：https://www.cremona.ca/business
日本語産地報告：https://zenrakuren.or.jp/wp/wp-content/uploads/01no686_22_11.pdf

## 第90回：Wawanesaの社名由来と日本語業界用例

元POI RBC Royal Bank、147 4 Stを同行公式の147-4th St、Wawanesa MBと照合。AOAの日本語会員ニュースはワワネサ保険をWawanesaに対応させるが、社名の用例である。2026年9月の同社担当者Tessa Peterson署名記事が社名は創業地のマニトバ州の町に由来すると明記し、会社公式史の創業地とも整合する。この橋渡しを根拠に町の編集表記をワワネサとした。町名の公的日本語指定や音声実聴とは主張せず、社名からの編集上の対応であることを生成データにも明記した。旧名Sipiweskeの読みは流用しない。

今回の2峰を含め累計729峰（登録日本語72・公開資料の日本語表記28・編集表記629）、未登録4,627峰。この候補群は127峰と45件。元密度と位置は不変。

住所：https://maps.rbcroyalbank.com/MB-WAWANESA-branch-6767
日本語：https://www.icmifasiaoceania.coop/jp/wp/?p=26832
名称由来：https://www.yycdata.ca/post/i-thought-my-technical-days-were-behind-me-by-tessa-peterson-director-advanced-analytics-exploration-wawanesa-insurance

## 第91回：Meteghanの学術論文用例と銀行住所

元POI RBC Royal Bank（5e6aa3d74fc6e300085c9b5f）の8249 Hwy 1、Meteghanを同行公式の同名・同住所に照合。大石太郎（2006）地学雑誌115(4)、431–447頁の論文PDF11頁（印刷441頁）の表2を画像で確認し、メテガン（NS）とメテガンリバー（NS）を区別した。NSがノヴァスコシア州である脚注も確認した。著者の現地調査に基づく用例から「メテガン」を編集表記として反映。発音実聴や公式日本語指定とは区別する。原サンプルの同一座標に集中した造船施設等を独立位置根拠には数えず、銀行の個別所在地で補った。

追加1峰、累計730峰（登録日本語72・公開資料の日本語表記28・編集表記630）、未登録4,626峰。この候補群は126峰と45件。

住所：https://maps.rbcroyalbank.com/NS-METEGHAN-branch-4513
日本語論文：https://dl.ndl.go.jp/view/prepareDownload?contentNo=1&itemId=info%3Andljp%2Fpid%2F8767212

## 第92回：Niobraraの図書館住所とVantageの読みの再確認

Niobraraは元POIの図書館住所25414 Park Ave Ste 3を図書館公式本文に一致確認した。村公式の歴史本文には読みがなく、同名の川やワイオミング州の郡の発音資料を村の確定読みに転用しない。Vantageは原サンプル3施設が401 South Mainを共有しており独立証拠と数えない。一般語の発音、別企業の日本語名、自動翻訳の宿泊ページのみでは地名を確定しない。今回の名称追加は0峰。累計730峰、未登録4,626峰、対象候補126峰と45件を維持。冒頭の未登録件数に残っていた旧値4,630を現在の4,626に訂正した。地図用データは変更していない。

[個別記録](unnamed-world-batch92-review.json)。住所出典：https://libs.ne.gov/niobrara 、村公式：https://niobrarane.com/history/ 。

## 第93回：Mindemoyaの日本語所在地と元POIの公式住所

Destination Ontarioの日本語旅行案内の所在地欄で「ミンデモヤ」を直接確認。湖名だけから転用せず、地域名を表す住所欄の用例を採用した。元POIのBMO銀行6103 Hwy542とWelcome Centre2207 Hwy551はそれぞれ銀行・自治体公式本文に一致した。日本語指定や発音実聴の認定ではなく、公開資料の日本語表記として1峰を反映した。累計731峰（登録72・公開資料29・編集630）、未登録4,625峰。候補群は125峰と45件。

[個別記録](unnamed-world-batch93-review.json)。日本語：https://www.destinationontario.com/ja-jp/travel-resources/family-road-trip-northeastern-ontario 、住所：https://branches.bmo.com/on/mindemoya/b2373/ 、https://www.centralmanitoulin.ca/recreation-culture/visiting-central-manitoulin/welcome-centre/ 。

## 第94回：Cloyneの居住者用例と自治体住所

Canada Journalの著者かほるヌーナンのプロフィール本文で、オンタリオ州クロイン(CLOYNE)への居住を確認。アイルランド同名町の読みを転用せず「クロイン」を編集表記として採用。モデルのクローヌを修正した。元POI Barrie Community Hall14225 Highway41を自治体の公開ページ本文に一致確認。Web閲覧ツールでは403だったが通常のInvoke-WebRequestで本文を取得でき、調査用HTMLをプロジェクト内に保存した。公式日本語指定や発音録音認定ではない。追加1峰、累計732峰（登録72・公開資料29・編集631）、未登録4,624峰、対象候補125峰と44件。

[個別記録](unnamed-world-batch94-review.json)。日本語：https://canadajournal.com/backnumber/1304/article_canadalife_1304.html 、住所：https://www.northfrontenac.com/our-community/facilities-and-community-halls/ 。

Natimukは劇団公式のナティマックという公演地名用例を確認したが、元小学校のJury Rdと公式38 Old Noradjuha Rdが異なり、郵便局の公式住所本文は未取得。採用を急がず保留を維持。Gogamaの日本語鉄道一覧はゴガマと記すが、他項目の州区分に誤りがあり、単独の確定根拠にしない。

## 第95回：Natimukの店舗住所と劇団公演記録

原POI The Climbing Shopの67 Main Stを店舗公式所在地に一致確認。同住所の旧店名は独立位置証拠として二重計上しない。原学校Jury Rdは公式38 Old Noradjuha Rdと異なるため位置根拠に使用しない。自治体郵便局PDFはアクセス拒否で本文未取得なので出典に採用しない。Theatre Group GUMBO公式プロフィールの2009年公演記録にNatimuk Soldiers Memorial Hall／ナティマック、オーストラリアという直接用例があり、モデルのナティムクを修正した。正式日本語指定・発音実聴の認定とは区別する。追加1峰、累計733峰（登録72・公開資料29・編集632）、未登録4,623峰。この候補群は125峰と43件。

[個別記録](unnamed-world-batch95-review.json)。住所：https://www.theclimbingshop.com.au/ 、公演記録：https://theatregroupgumbo.wixsite.com/japanese/profile 。

## 第96回：Birtleの論文用例と原施設住所

細川道久の鹿児島大学公開論文PDF3頁にバートル校(Birtle residential school)、マニトバ州との記述を確認。NCTRが同施設をBirtle MB1888-1970と記すことと対応させ、同形の所在地名に基づく編集表記バートルを採用。町の公式日本語指定や発音実聴とは区別する。原ゴルフ場115 Alexandria Stは州観光局の公式住所に一致。モデルのビルトルを修正。追加1峰、累計734峰（登録72・公開資料29・編集633）、未登録4,622峰、候補125峰と42件。Colomeの速記者協会2024年新版165頁は公開閲覧できたが対象語が検出されず、読みの確定には使えないことを記録した。

[個別記録](unnamed-world-batch96-review.json)。日本語：https://ir.kagoshima-u.ac.jp/record/15034/files/AN00041730_v67_p1-13.pdf 、施設対応：https://nctr.ca/residential-schools/manitoba/birtle/ 、住所：https://www.travelmanitoba.com/directory/birtle-riverside-golf-club/ 。


## 第97回：Dundurnの住所と訪問記録（2026-10-11）

Prairie Spirit School Division公式のDundurn School、302–3rd Ave、Dundurn SKが原POIの学校住所に一致。P signの2024年公開記事は2017年の同町訪問を記録し、サスカチュワン州Dundurnをダンダーンと記す。別州の同名城ではなく、この町の日本語用例として編集表記を採用。自治体サイトの共通フッターや6施設の同一座標群を独立位置証拠にせず、取得404の旧ニュースレターも本文確認根拠から除外した。追加1峰、累計735峰（登録72・公開資料29・編集634）、未登録4,621峰。対象候補は残り124峰と42件。正式日本語指定や音声の確認ではない。

- 日本語訪問記録: https://p-sign123.jp/entry/2024/03/08/225100
- 元学校住所: https://www.spiritsd.ca/dun/
- 詳細記録: [第97回照合](unnamed-world-batch97-review.json)


## 第98回：Church Pointの大学所在地と地理学論文（2026-10-11）

大石太郎2020地理空間13(3)161–177、PDF15頁・印刷175頁の注9に、ノヴァスコシア州南西部チャーチポイント（ポワントゥ・ドゥ・レグリーズ）とサンタンヌ大学を確認。日本語用例に基づく編集表記チャーチポイントを追加。大学公式スポーツセンター住所1695 route1が元大学プールPOI1695 Route1に対応し、大学英語ページでも同番地Church Point Nova Scotiaを確認。元大学POIの1649番地は現住所と不一致のため根拠にしない。大学内の教室・私室の細分登録が多いことを記録し、独立施設の裏付けとは扱わない。追加1峰、累計736峰（登録72・公開資料29・編集635）、未登録4,620峰、対象残り123峰と42件。

- 日本語論文: https://www.jstage.jst.go.jp/article/jags/13/3/13_161/_pdf
- スポーツ施設公式住所: https://www.usainteanne.ca/contact/centre-sportif
- 英語所在地: https://www.usainteanne.ca/en/research/units/lqc
- [第98回照合](unnamed-world-batch98-review.json)


## 第99回：Guysboroughの州公開店舗住所と日本語資料（2026-10-11）

原NSLCの10018 Highway16を州公開RFP SR-26-FY23 PDF21頁の店舗2317に一致確認。原Robin/Cooksの10016 Highway16は観光協会がGuysborough集落内と記す。リクルートワークス研究所2022週休3日で働くPDF19頁・印刷18頁は検索索引のガイズバラと異なり、本文でガイスバラと記載。画像とPDFiumを確認し本文表記を採用した。地区自治体の用例を同形集落名に対応させた編集表記であり、両者の範囲が同じという意味ではない。モデルのギーズボロを修正。追加1峰、累計737峰（登録72・公開資料29・編集636）、未登録4,619峰、対象残り122峰と42件。

- 日本語資料: https://www.works-i.com/research/labour/item/four-day_workweek2022.pdf
- 原店舗住所: https://procurement.novascotia.ca/pt_files/tenders/SR-26-FY23.pdf
- 集落・原店舗住所: https://visitguysborough.ca/cooks-gas-bar-robins/
- [第99回照合](unnamed-world-batch99-review.json)


## 第100回：Duck Lakeの自治体住所と現地取材日本語記事（2026-10-11）

クーリエジャポン2018年2月11日のAllen Abel／マクリーンズ現地取材記事本文にサスカチュワン州ダックレイクの村と確認。元RM Duck Lake No463の209 Front Streetは自治体公式本文と一致。町役場・Arena等の同一座標群は独立根拠にしない。日本語取材記事の用例に基づく編集表記ダックレイクを追加。正式指定や音声確認とは区別する。追加1峰、累計738峰（登録72・公開資料29・編集637）、未登録4,618峰、対象残り121峰と42件。

- 日本語記事: https://courrier.jp/news/archives/111641/
- 元POI公式住所: https://rmducklake.com/employee_information.html
- [第100回照合](unnamed-world-batch100-review.json)


## 第101回：Kitscotyの学校住所と訳詩資料の地理注（2026-10-11）

松田寿一訳カナダ詩人訳詩集III PDF7頁・印刷137頁でキッツコティ(Kitscoty)を画像確認。注にサスカトゥーンからエドモントンへ向かう16号沿いの町とあり、対象集落に対応。元小学校の4910 51Streetも学校公式住所に一致。編集表記キッツコティを追加しモデルのキスコティを修正した。旧調査の保健機関住所は原POIにないので今回の住所根拠には使わない。追加1峰、累計739峰（登録72・公開資料29・編集638）、未登録4,617峰、対象残り120峰と42件。

- 日本語訳詩資料: https://hmjc.repo.nii.ac.jp/record/396/files/KJ00004253717.pdf
- 元学校住所: https://kes.btps.ca/contact
- [第101回照合](unnamed-world-batch101-review.json)

### 第102回：Elbowの追加照合

日本語候補「エルボー」は原子力産業新聞の地域用例で確認し、SaskPower資料38頁で同地域にVillage of Elbowが含まれることを照合しました。自治体公式201 Saskatchewan Streetは元POIと一致しますが、12施設の共有座標のため独立位置証拠にはしません。図書館402 Minto Streetは検索索引で候補を得た段階で、公開資料本文を取得できていません。採用追加は0、残り120峰・42件、累計739峰です。[詳細](unnamed-world-batch102-review.json)。

### 第103回：Elbowをエルボーとして反映

信用組合運営者の公開支店一覧2ページ目で209 Saskatchewan Streetを直接確認し、元POIの別座標の支店と照合しました。原子力産業新聞の日本語地域用例とSaskPowerの同名村記載を対応させ、編集表記として1峰を追加。累計740峰、残り119峰・42件です。[根拠](unnamed-world-batch103-review.json)。図書館の新旧住所は未解決で採用根拠に使用しません。

### 第104回：Burstallの住所根拠を補強

CER公開通知PDF1頁のChinook Regional Library Burstall Branch39、425 Martin Streetを元POIと直接照合しました。現営業を証明する資料ではありません。同名人名・別州の峠・英国Birstallの読みは町へ転用せず保留。追加反映0、残り119峰・42件、累計740峰。[照合記録](unnamed-world-batch104-review.json)。

### 第105回：Cumberland Houseの根拠を追加

阿部隆夫教授の大学公式研究業績で「カンバーランドハウス」の歴史交易用例を確認し、元警察署416 McKenzie AvenueをRCMP公式住所に直接照合しました。歴史交易所と現在の町の対応、同一座標を共有する別施設の扱いを確認して採用を判断します。追加0、残り119峰・42件、累計740峰。[記録](unnamed-world-batch105-review.json)。

### 第106回：カンバーランドハウスを反映

RCMP公式番地付き住所を原POIに照合。阿部隆夫教授の大学公開研究題名にある日本語用例と、公的史跡資料が説明する交易所から現在集落への対応を確認して1峰を追加しました。論文本文・発音録音の確認ではありません。累計741峰、残り119峰・41件。[根拠](unnamed-world-batch106-review.json)。

### 第107回：Lysvikの施設住所を確認

Coop公式本文のGamla Vägen 40、68697 Lysvikを元POIに直接照合しました。同住所のPostnord受取所は独立地点として数えません。宿泊サイトの自動翻訳日本語のみでは採用せず、読みを継続確認。追加0、残り119峰・41件、累計741峰。[記録](unnamed-world-batch107-review.json)。

### 第108回：La Doréの住所・参照位置を確認

宿泊施設4829 rue des Peupliersを自治体公式案内に直接照合し、州地名委員会の登録座標48.71317,-72.64957との近接を確認しました。日本の陸上クラブ名の「ラ・ドレ」は当該町の読み証拠に転用しません。追加0、残り119峰・41件、累計741峰。[詳細](unnamed-world-batch108-review.json)。

### 第109回：Cut Knife図書館の番地不一致

元POI115 Broad Stに対し自治体公式図書館住所は113 Broad Street。電話番号は一致しますが番地を同一扱いせず、別施設の住所照合に切り替えます。組織求人のNorth Battleford本部住所も当地住所に転用しません。追加0、残り119峰・41件、累計741峰。[記録](unnamed-world-batch109-review.json)。

### 第110回：Cut Knife別施設住所・カウサニ日本語資料の再確認

Cut KnifeのLucerne Hotelは元POIの211 Broad Stと自治体案内の211 Broad Streetが一致。図書館113/115番地の不一致とは別の照合結果として保存した。町の日本語用例は未確定。カウサニは政府観光サイトの検索キャッシュに日本語本文があるが直接取得は失敗し、取得成功として扱わない。新規反映0峰、累計741峰。残り119峰と旧保留41件。詳細は `unnamed-world-batch110-review.json`。表示データの変更はない。

### 第111回：Onowayをオノウェイとして反映

州政府のOnoway Registries4912 50 STと元POIの同施設住所・座標を直接照合。Gizmodo Japanの福田ミホ訳記事本文（2017-03-13）にあるアルバータ州オノウェイの表記を採用。日本語報道訳の用例であり現地実訪や発音実聴とは区別した。1峰追加、累計742峰、未反映4,614峰。対象候補は残り118峰と旧保留41件。根拠は `unnamed-world-batch111-review.json`。

### 第112回：フランスの施設住所本文とノルウェー実訪記

La Chapelle-en-ValgaudémarのGalland Sports所在地を地方観光局本文で直接確認。以前の検索結果のみから直接本文の確認に進んだ。番地なしの地区住所であり完全な番地一致ではない。Valldalの日本語実訪記は町で一泊した記述があるが地名はラテン文字のままで読みの採用根拠にしない。追加0峰、累計742峰、残り118峰と旧保留41件。`unnamed-world-batch112-review.json`に保存。表示データ変更なし。

### 第113回：Gogamaをゴガマとして反映

佐々木邦昭「北米内陸部で頻発する非在来型原油漏出事故」安全工学54巻5号2015年、PDF2頁・印刷375頁表1行12のオンタリオ・ゴガマを画像で直接確認。銀行公式住所の前回確認と地域サイトの併設店住所を照合。事故地点が峰と一致するという主張ではなく町名の日本語用例として採用。1峰追加、累計743峰、未反映4,613峰。対象候補は残り117峰と旧保留41件。詳細は `unnamed-world-batch113-review.json`。

### 第114回：Chemultの名称由来資料

Oregon Geographic Names1952年の転記本文でChemultがKlamath首長名由来と確認。発音は載っておらず原本画像未確認。日本語予約サイトのケモルト/チェマルト及びゲームのチェモーは単独の実在集落読みの根拠にせず、Klamath地域・鉄道駅音声へ調査先を絞る。新規0峰、累計743峰、残り117峰と旧保留41件。`unnamed-world-batch114-review.json`に記録。

### 第115回：Chemult音声経路

Forvoに米国投稿者ajhaydenusのChemult録音1件があることを本文確認。録音は未実聴、当地居住・対象集落も未確認。地域観光協会のCentral Oregon Daily映像リンクも確認したが取得失敗。発音確認済みとは扱わず、次の検証経路を記録した。新規0峰、累計743峰、残り117峰・旧保留41件。`unnamed-world-batch115-review.json`。

### 第116回：Rockglen（2026-10-11）

元POIのTown of Rockglen、1013 Centerと自治体公開の町役場1013 Centre Streetを照合。日本気象協会2024-07-22 WDA-Global地点一覧23頁のロックグレン［サスカチュワン］を画像で確認し、編集表記「ロックグレン」を1峰に反映。気象地点と峰は約2.5km離れており、同一地点や公式日本語指定・音声検証とは扱いません。採用合計744峰、今回対象の残り116峰と41件、全体未登録4,612峰。根拠はunnamed-world-batch116-review.jsonに保存。

### 第117回：Coronach住所再確認（2026-10-11）

自治体公開事業所一覧と元POIのCanada Post、7 1st Ave Wを直接照合し、町の住所対応を確認。銀行は番地が同じでも旧名称と現名称が異なるため同一営業主体とは認定しません。日本語検索で出た競走馬・機械翻訳・百科転載を町の読みとして採用せず、地域史・発音資料の確認へ継続。今回追加0、残り116峰と41件、反映累計744峰。詳細はunnamed-world-batch117-review.json。

### 第118回：Snelling（2026-10-11）

元Boland Market15904California59と州CDTFA告示の店名・番地・州道59を直接照合。環境省報告書PDF322頁（印刷資161）付表3-2のカリフォルニア州スネリング市を画像確認し、編集表記スネリングを1峰に反映。行政区分や実証地点と峰の同一性・現営業・公式日本語指定・音声検証は認定しません。反映745峰、今回対象残り115峰と41件、全体未登録4,611峰。根拠unnamed-world-batch118-review.json。

### 第119回：Ryley住所・歴史資料対訳照合（2026-10-11）

図書館公式の5113 50st Ryleyと元POIを直接照合。EJCA日本語歴史講演4頁のライリーを確認したが、同団体英語版5頁はRileyと綴り、Ryleyへの対応は未確定。原典照合へ継続し反映を保留。Forestburgの日本語検索で見つかったバイオマス資料は米国サウスダコタ州の同名地・品種を対象としており、カナダ候補に転用しない。今回追加0、残り115峰と41件、反映745峰。詳細unnamed-world-batch119-review.json。

### 第120回：Ryley引用原典の特定（2026-10-11）

EJCA2014報告原本33・35頁から、中山訊四郎編著1921年7月『加奈陀同胞発展大鑑』515頁がRiley農場記述の引用元と確認。公式history-projectでは関連原文リンクを確認できず、別の公開1929年名簿784頁のRiley/Ryley文字検索も該当なし（画像文字を含む不存在の証明ではない）。原文の地名・地理対応確認へ継続。今回追加0、115峰と41件を保留、反映745峰。詳細unnamed-world-batch120-review.json。

### 第121回：Forestburg（2026-10-11）

BMO公式掲載の4816 50th St Forestburg ABと元POIを照合。自治体国際化協会の2025交流事業概要1頁にあるアルバータ州フォレストバーグ村を原本確認し1峰に編集表記を反映。銀行現営業や正式日本語指定・音声検証は認定しません。累計746峰、今回対象残り114峰と41件、全体未登録4,610峰。根拠unnamed-world-batch121-review.json。

### 第122回：Ashern薬局の住所照合（2026-10-11）

元Guardian-Ashern Pharmacy43 Main Stをマニトバ州公式一覧と直接照合し、図書館の部屋番号差に依存しない所在地一致を確認。日本語アシャーンの俳優紹介用例は、記事本文と集落・居留地の対応を確認する必要があり保留。今回追加0、対象残り114峰と41件、累計746峰。詳細unnamed-world-batch122-review.json。

### 第123回：Ashern（2026-10-11）

原薬局住所と州資料の一致を引き継ぎ、成田陽子の日本語取材記事本文のアシャーン出生地名を確認。大学の本人取材記事が出生地Ashernと幼少期居住の居留地を区別しており、日本語記事の居留地分類を採用せず出生地名用例として編集表記アシャーンを1峰に反映。公式日本語指定・音声検証ではありません。累計747峰、対象残り114峰と40件、未登録4,609峰。根拠unnamed-world-batch123-review.json。

### 第124回：Treherne・Eatoniaの命名資料追加調査

Treherneはマニトバ歴史協会の自治体沿革でGeorge Treherne由来と確認。人名発音は町名に移用しない。Eatoniaは自治体沿革で旧称Eatonからの1921年改称を確認。原FCL217 Railway Aveと運営者資料のEatonia Farm Supply217 Railway Avenueが対応するが、法人同一性や日本語読みの確定とは区別する。日本語自動翻訳ミラー、町役場の郵送先は根拠として採用しない。追加採用0、反映累計747峰、今回対象残114峰と40件。詳しい参照URLと未確定理由はunnamed-world-batch124-review.json。表示データは変更していない。

### 第125回：Valldal中心部の集落名Sylteを確認

NRK地名辞典のSylte集落62.29798,7.26260と推奨発音表記を再取得して照合。自治体2026年7月案内もSylte/Valldal中心部と併記。原ホテルSyltegataと登記上所在地の対応を引き継ぎ、別農場Valldalの読みを転用せずシルテを編集音写として1峰に反映。NRKは約1960年の資料であり現在の録音や公式日本語名の認定ではない。累計748峰、対象残113峰と40件、全体未登録4,608峰。根拠unnamed-world-batch125-review.json。

### 第126回：Daysland・Kinuso・Donaldaの一次資料

Daysland原KaplerHardware5038 50thStを地域観光案内10頁と直接照合。KinusoはDersch2011博士論文本文90頁を確認し、由来人名と現行町名の読みを同一視しないことを確定。Donalda自治体35頁の画像PDFを取得し、テキスト抽出無検出を住所不在と誤認せず画像照合に進める。追加0、累計748峰、対象残113峰と40件。参照URLと次工程はunnamed-world-batch126-review.json。表示データ変更なし。

### 第127回：Donalda元施設の画像原本照合

自治体2021-22事業観光案内PDF33頁（印刷31頁）のTERESAS広告を目視確認。Catering・5019 Main Street Donalda ABが原Theresas Cateringの業務・番地・村名に対応。綴り差は明記し、同広告のStettler別店舗や元ATB所在地と混同しない。住所照合を完了し、残工程を村名の読み確認へ更新。追加採用0、累計748峰、対象残113峰と40件。原本画像と理由はunnamed-world-batch127-review.json。

### 第128回：Marnardalの参照範囲の確認

ISOF公開NORNA2023のRuneRøsstad要旨18-19頁本文で、旧自治体名と駅周辺の集落呼称を区別。自治体廃止のみを理由に村名を棄却しない。元Marnarbilの番地を登記索引と照合し、原POI5施設の共有座標も記録。NRKの別地域Måndalen/Heddalの読みは転用しない。追加0、累計748峰、対象残113峰と40件。詳しくはunnamed-world-batch128-review.json。

### 第129回：ABC公開発音辞典によるDerrinallum

CarolAltmannの店主取材記事で原FrontPaddockCafe24MainStDerrinallumを照合。ABC公開辞典のVictoriaを明記した推奨発音de-rin-AL-uhmからデリナラムを編集音写として反映。SuratもQueensland項目suh-RATが見つかり、インド項目SOOH-rutと区別。Warooka・Lismore・Texasは今回検索で一致項目がなく類似候補を転用しない。追加1、累計749峰、対象残113峰と39件、全体未登録4,607峰。録音聴取・公式日本語認定ではない。

### 第130回：Suratの州別発音と住所

Queensland Healthの2025年通知記録で原POIと同じ76 Burrowes Street・Surat・QLDの薬局住所を確認。資料名Surat Pharmacyと原名Radiance Pharmacyの違いを記録し、法人同一性や現営業は認定せず地域の照合に利用。ABCのQueensland項目suh-RATから「サラット」を編集音写として追加。インドの同名都市とは区別。追加1、累計750峰、対象残112峰と39件、全体未登録4,606峰。

### 第131回：Kausaniの原語表記と現地大学住所

Bageshwar県政府のヒンディー語本文कौसानीとUttarakhand Open University観光教材BTTMN301 PDF223頁のSuman Royal Resort・VIP Road・View Point・Kausaniを確認。原POIの施設名とView Point住所が対応。原語長母音を含むカウサーニーを編集表記として追加。旧日本語ページやHotel Sagarの取得失敗は未解消のまま別一次資料を利用。追加1、累計751峰、対象残111峰と39件、全体未登録4,605峰。

### 第132回：Lazdukalnsの施設粒度・同名地域を監査

峰500m内の原Lazdukalns登録14件を住所Parquetから確認。Oskaraの部屋・ベッド・机・テレビ、台所や客間等の私的な物・部屋を示す名称が集中し、住所は旧町域名のみ。異なる座標の数だけでは独立した店舗群とは判定できない。Tēzaurs本文は同名集落3件とBenislavaを中心とする町域を区別。西方の学校や郵便局を本峰の住所根拠に転用しない。追加0、累計751峰、対象残111峰と39件。元POI監査JSONと第132回報告に次の確認事項を保存。密度変更・除外は未実施。

### 第133回：Craigmont図書館住所と北米発音辞典検索

Idaho State Libraryの図書館名簿（ERIC ED433853、PDF106頁）本文で原Craigmont City Libraryの112W Main・Craigmont IDを直接照合。古い名簿であり現営業は保証しない。ABC公開発音辞典でCraigmont、Niobrara、Colome、Wikieup、Myrnam、Irma、Daysland、Granumを検索し一致項目0。検索結果はreading-sourcesの各JSONに保存。町の読みが掲載されていないことの全資料にわたる証明ではない。別地域や姓の発音を転用せず追加0、累計751、対象残111峰と39件。

### 第134回：Valgaudémarの母音と参照辞典

地方登山団体の2024年記事本文から、村LaChapelleのValgaudémarと谷名Valgaudemar・他村Valgodemardの区別、éの由来を確認。引用元はVallouimagesの説明とDavidMartin1909辞典216–217頁。Vallouimages本文取得は502、原辞典へのGallicaリンクをLexilogosで特定。二次引用の谷名IPAだけで村名全体を確定せず保留。追加0、累計751、対象残111峰と39件。

### 第135回：Venjan方言辞典の原画像確認

DiVA方言辞典PDF56頁（印刷3070）保存画像を目視確認。Venjan項の対象は教区と湖で、複数の音写には地域別略記が付く。抽出テキストの特殊記号の崩れを画像で確認できたが、現在の集落の標準読み一つを選ぶ根拠には不足。既存の施設住所確認は維持し、次に略記・音写凡例を確認する。追加0、累計751、対象残111峰と39件。

### 第136回：Pense役場の公的住所を照合

RMofPenseNo160公式2025-07-08議事録2頁148/25の324ElderStreetPenseを原POIの役場名・番地・街路・町に直接照合。行政区域RMと役場所在町を区別。韻辞典は町名対象を明示せず読み根拠には採用しない。追加0、累計751、対象残111峰と39件。

### 第137回：Missouri州地名発音ガイドの対象範囲確認

Kansas大学公開Missouri Place Names Pronunciation Guide全4頁・193行を直接確認。Urich、Ellsinore、Marquand、Grovespring、Eaglevilleは掲載されていない。対象外の同名町や姓のIPAを転用せず、州歴史協会の郡別地名資料・地元取材へ調査先を変更。追加0、累計751、対象残111峰と39件。

### 第138回：Missouri州歴史協会の3郡別調査を直接確認

Ramsay地名資料Henry/Madison/Carter郡本文を取得。Urichは仏将軍Uhrich由来と綴り簡略化、Marquandは鉄道役員由来。Ellsinoreは聞き取りごとに由来説が異なり、資料も未確定とする。これらは現地町名の発音を直接示さず、人名・外国地名の読みを代用しない。追加0、累計751、対象残111峰と39件。

### 第139回：SãoMartinho dasAmoreirasの公式施設所在地とnh

MonteMaravilhas運営者公式本文で施設・町・郵便番号・GPSを確認。ただし原RuaMaravilhasBaixo0Sの街路文字列は公式にない。UniversidadeAberta発音教材のMartinhoと鼻子音ɲ課題から、元モデルマルティンのnh欠落を確認。地名全体の読み確定および薬局番地の一次照合は保留。追加0、累計751、対象残111峰と39件。

教材は検索抽出のみで、直接PDF取得は34MB容量制限によって失敗。全文・解答を閲覧したとは扱わず、nhの確認は採用前の予備的指摘とする。

2026-10-11 batch154: Furudalをフールダールとして1峰反映。ISOF Ore地名調査カード1922年・1932年の発音記録とVisit DalarnaのSnitths Hantverksbageri訪問住所Järnvägsgatan9を原POIに照合。歴史資料に基づく編集表記であり公式日本語名ではない。累計757峰、残108峰・36件、全体未登録4599峰。S3未更新。

2026-10-11 batch159：Dayslandをデイズランドとして1峰反映。1994年州地名資料VolumeIII印刷68頁のDay命名由来とMerriamWebster day/land発音に基づく編集音写。Flagstaff観光案内のKaplersHomeHardware5038-50Streetと元POIを照合。現地録音の直接確認とは区別。累計758峰、残107峰・36件、全体未登録4598峰。S3未更新。

2026-10-12 batch160：Alliance CA ABをアライアンスとして1峰反映。州地名資料VolumeIII印刷3頁のOhio都市由来とMerriamWebster地名項目の命名元の発音に基づく編集表記。村公式信用組合117MainStWestと原POIを照合。カナダ村の現地発音直接確認とは区別。累計759峰、残106峰・36件、全体未登録4597峰。S3未更新。

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

2026-10-12 batch216：Vonda原HUB301MainStと運営者公開住所を照合。Mortlach原教会203RoseStと教区2020年議事録1頁を直接照合、売却承認と現在営業を区別。Strasbourg大学資料で命名・改綴を確認、町広告住所は画像未取得のため照合未完了。3件とも当地の読みは未確定。追加0、累計811、残61峰・29件。判断unnamed-world-batch216-review.json。表示辞書・S3変更なし。

2026-10-12 batch217：オーストラリアTexas Rural Agencies40HighStを運営者公式同施設40HighStreet Texas Qld4385に照合。QueenslandPlacesで町名本体Texasを確認、参照データのGoodiwindiは町名へ含めない。CMU texasによる編集音写テキサスを1峰反映、当地音声実聴とは区別。累計812、候補61峰・保留28件、全体未登録4544。判断unnamed-world-batch217-review.json。S3未更新。

2026-10-12 batch218：Urich原Auto & Tractor105E GrahamRdとNAPA店舗資料PDFindex78の同施設同住所を照合。CMU全語urichに基づく編集表記ユーリックを1峰追加。人名由来や現地録音実聴とは区別。累計813、対象残60峰・28件、全体未登録4543。判断unnamed-world-batch218-review.json。S3未更新。

2026-10-12 batch219：Neilburgニールバーグ、Hodgevilleホッジビル2峰を反映。原ManitouHealthCentre1052ndAveWと原HodgevilleHealthCentre105MainStを州保健当局同施設同番地に直接照合。Neilburg村公式も医療施設街路住所を確認。CMU neil/burg・hodge/villeの構成語読みから編集音写、当地全語録音実聴とは区別。累計815、対象残58峰・28件、全体未登録4541。判断unnamed-world-batch219-review.json。S3未更新。

2026-10-12 batch220：Bethuneベスューン1峰反映。原Co-op607FordStとParmakメーカー公式販売店一覧同組織同番地を照合。CMU全語bethuneに基づく編集表記、当地録音実聴とは区別。モデルベスヌー不採用。同住所の複数部門を別地点証拠に数えない。累計816、対象残57峰・28件、全体未登録4540。判断unnamed-world-batch220-review.json。S3未更新。

2026-10-12 batch221：Lus-la-Croix-Hauteの地域公園施設住所を再確認し全町名IPAの検索資料を検出。発音記事の取得は本文未完了で採用保留。Warookaは由来語と現在発音を区別し観光局・州拠点を次の資料先に特定。追加0、累計816、対象残57峰・28件。判断unnamed-world-batch221-review.json。表示辞書・S3変更なし。

2026-10-12 batch222：Auclairオークレール1峰反映。原Camping dEauClaire1096Route295と州政府公式観光サイト同施設同番地を照合。フランス語au /o/とUsito clair /klɛʀ/の辞書に基づく編集音写、当地全語録音とは区別。前回Lus発音記事取得は停滞で中断し本文未確認を維持。累計817、対象残57峰・27件、全体未登録4539。判断unnamed-world-batch222-review.json。S3未更新。

2026-10-12 batch223：La Doréラ・ドレ1峰反映。元宿泊施設4829rue desPeupliersと自治体公式の同施設同番地を照合。Larousse doré [dɔre]から編集音写。現地録音・公的日本語名とは区別。累計818、対象残57峰・26件、全体未登録4538。判断unnamed-world-batch223-review.json。S3未更新。

2026-10-12 batch224：Lac-Droletラック・ドロレ1峰反映。原Co-Op670PrincipaleRueと自治体公式Magasin COOP670ruePrincipaleを照合。Wiktionnaire固有姓Droletの読みから編集音写、当地録音とは区別。累計819、対象残57峰・25件、全体未登録4537。判断unnamed-world-batch224-review.json。S3未更新。

2026-10-12 batch225：Sainte-Justineサント・ジュスティーヌ1峰反映。元Familiprix135-7RuePrincipaleと運営者住所・保存済み公式座標を照合。sainte/Justine辞書読みから編集音写。末尾#135冗長表記、別国同名町やMontreal病院の証拠とは区別。累計820、対象残56峰・25件、全体未登録4536。判断unnamed-world-batch225-review.json。S3未更新。

2026-10-12 batch226：Saint-Jean-de-Dieuサン・ジャン・ド・デュー1峰反映。原SAQ代理店AlimentationJ.-Y.Belzil56ruePrincipaleNordとSAQ公式同施設同番地を照合。saint/Jean/Dieu辞書から編集音写。Saint-Hilarion住所再確認、読み未確認を維持。累計821、対象残55峰・25件、全体未登録4535。判断unnamed-world-batch226-review.json。S3未更新。

2026-10-12 batch227：Saint-Patrice-de-Beaurivageサン・パトリス・ド・ボーリバージュ1峰反映。原SAQ代理店AccommodationCybélair526ruePrincipaleとSAQ公式同施設同番地を照合。Patrice/beau/rivage辞書から編集音写、当地全語録音とは区別。累計822、対象残54峰・25件、全体未登録4534。判断unnamed-world-batch227-review.json。S3未更新。

2026-10-12 batch228：ChristopherLakeクリストファー・レイク1峰反映。原LakelandLiquor215MainStWと製造者公式販売店一覧同施設同番地を照合。役場の南北住所不一致は保持。USPS組織名とCA所在不整合は別途監査事項。CMU構成語による編集音写。NewEffington州申請資料住所検索確認、本文実読と読みは継続。累計823、対象残53峰・25件、全体未登録4533。判断unnamed-world-batch228-review.json。S3未更新。

2026-10-12 batch229：Irmaアーマ1峰反映。原IrmaCo-operativeAssociationLtd5005 50thStとCampbell公式同組織同番地を照合。CMU英語irma ER1 M AH0から編集音写、当地録音や公的日本語指定とは区別。Ewen州読み資料は検索確認のみで本文Timeout、保留維持。累計824、対象残52峰・25件、全体未登録4532。判断unnamed-world-batch229-review.json。S3未更新。

2026-10-12 batch230：Benitoベニート1峰反映。原BenitoHomeCentre1231StAveEとSupplyBuild公式1231stAveEastを照合。CMU英語辞書による編集音写。図書館番地相違とAgShield道路表記差は解消済みとは扱わない。累計825、対象残51峰・25件、全体未登録4531。判断unnamed-world-batch230-review.json。S3未更新。

2026-10-12 batch231：Consulパン店同施設105CentreStを州観光局本文で再確認。博物館口述史DarlingTranscript・IraBlakley記録を新規調査先として追加。文字資料から読みは断定せず保留継続。累計825、残51峰・25件不変。判断unnamed-world-batch231-review.json。表示変更なし。

2026-10-12 batch232：Pangmanパングマン1峰反映。村公式ServiceStation101MergensStと元Co-opGasBarを照合。辞書構成音による編集音写、当地録音とは区別。累計826、対象残50峰・25件、全体未登録4530。Canwood/Debden学校住所を含む教育委員会2014資料は検索結果のみ、本文404で未確認。判断unnamed-world-batch232-review.json。S3未更新。

2026-10-12 batch233：Canwoodキャンウッド1峰反映。原PublicSchool8501stStEと村公式学校同名同番地本文を照合。CMU構成音から編集音写。役場番地不一致は別途保持、補助辞書の国誤記は位置根拠にしない。累計827、対象残49峰・25件、全体未登録4529。判断unnamed-world-batch233-review.json。S3未更新。

2026-10-12 batch234：Manitoba Miamiマイアミ1峰反映。CallInsurance453NortonAveと自治体公式同組織同番地を照合。CMU英語読みから編集音写、当地録音とは区別。Florida市由来とはしない。累計828、対象残48峰・25件、全体未登録4528。判断unnamed-world-batch234-review.json。S3未更新。

2026-10-12 batch235：Ontario Veronaヴェローナ1峰反映。原RONA6723MainStreetと運営公式周年記事同組織同番地を照合。CMU英語読みから編集音写、当地録音とは区別。10件の同一座標集中を個別監査JSONに保存し名称根拠から分離。密度は変更せず。累計829、対象残47峰・25件、全体未登録4527。判断unnamed-world-batch235-review.json。S3未更新。

2026-10-12 batch236：Manseau原Residence260StAlphonseと自治体同施設同番地を本文照合。辞書当該姓発音未記載、別住民呼称の音を直接転用せず保留。Milverton運営公式現店舗一覧に原15MainStNがなく、旧店舗一次資料確認へ調査を切替。追加0、累計829、対象残47峰・25件。判断unnamed-world-batch236-review.json。表示・S3変更なし。

2026-10-12 batch237：Edamイーダム1峰反映。原ArnoldsSandGravel8181stStEと運営公式同施設同番地本文を照合。Wiktionary英語IPAと当該村語義から編集音写、UK読みを当地録音とは区別。Vonda公式直接取得はCache missで未解消。累計830、対象残46峰・25件、全体未登録4526。判断unnamed-world-batch237-review.json。S3未更新。

2026-10-12 batch238：Lyster原Desjardins635rueLaurierを運営公式本文と照合、別言語小文字lysterは読み根拠にしない。LacEtchemin銀行2222eAvenue検索一致、自治体本文429で未実読。三銀行登録は同一施設として区別。追加0、累計830、残46峰・25件。判断unnamed-world-batch238-review.json。表示・S3変更なし。

2026-10-12 batch239：RedversをVictoria大学収蔵Saskatchewan英語研究435頁PDFで調査。該当箇所はindex111移民史・index119地図で地名発音資料ではない。大学町百科を補助確認、原施設番地と読みは継続。追加0、累計830、残46峰・25件。判断unnamed-world-batch239-review.json。表示・S3変更なし。

2026-10-12 batch240：Redvers原GoldenAgeCentre11BroadwayStを町公式同施設同番地本文に照合。命名元人物録音ページは検索候補のみで未聴取、読みは継続。追加0、累計830、残46峰・25件。判断unnamed-world-batch240-review.json。表示・S3変更なし。

2026-10-12 batch241：Cupar原WheatlandAgencies210StanleyStを町事業一覧と照合。州求人企業自己掲載を追加資料候補に登録。辞書と当地匿名読みの差は未解決。Mortlach町公式118RoseStは町連絡先で郵便施設原住所一致の独立証明とはしない。追加0、累計830、残46峰・25件。判断unnamed-world-batch241-review.json。表示・S3変更なし。

2026-10-12 batch242：Ituna町2012CommunityProfile自治体収蔵PDFを新規発見、直接取得不能で本文未確認。KozyKitchen第三者住所一致はFoursquare循環引用・郵便番号差を区別。町プロフィール原資料確認へ調査先を更新。追加0、累計830、残46峰・25件。判断unnamed-world-batch242-review.json。表示・S3変更なし。

2026-10-12 batch243：Ituna町公式事業一覧と町史本文を確認。原KozyKitchen404MainStNと同番地には別の商店が掲載され、同施設一致とはしない。町長インタビュー紹介は音声未聴取、英語辞書は発音未掲載。読みと住所の照合を継続。追加0、累計830、残46峰・25件、全体未登録4526。判断unnamed-world-batch243-review.json。表示・S3変更なし。

2026-10-12 batch244：Kenaston学校公式4005thAveと原学校7023rdStの住所差を確認し、同施設名だけで住所一致としない。次に図書館・信用組合を照合。Warooka自治体公式座標で地域対応を補強、州立図書館13頁は語源資料、既存ABC完全一致語なし。両件の読みは保留。追加0、累計830、残46峰・25件、全体未登録4526。判断unnamed-world-batch244-review.json。表示・S3変更なし。

2026-10-12 batch245：Avonleaアボンリー1峰反映。CCIA同施設住所300McRorieAveを再確認し、地元図書館委員会及びPalliserRegionalLibrary2018資料7頁で命名元がAnneofGreenGables架空村であることを確認。JMnedict既存日本語を命名元に基づく編集表記に採用しSK現地録音とは区別。累計831、対象残45峰・25件、全体未登録4525。判断unnamed-world-batch245-review.json。S3未更新。

2026-10-12 batch246：Kenaston原図書館5013rdStを村公式同施設同番地と照合。原#309は公式郵便Box309との対応可能性を記録し部屋番号一致とは認定しない。学校住所差を保持し、町史から命名元F.E.Kenastonを確認。次は当該姓・町の読みを照合。追加0、累計831、残45峰・25件、全体未登録4525。判断unnamed-world-batch246-review.json。表示・S3変更なし。

2026-10-12 batch247：Leedey州歴史協会町百科で命名元AmosLeedeyを確認。原504Grocery504SMainStは地域キャンプ場一覧で補助照合、店舗公式とは区別。1997州方言研究12頁PDFに対象名検索一致なし、大学記事合成音声を現地録音としない。追加0、累計831、残45峰・25件、全体未登録4525。判断unnamed-world-batch247-review.json。表示・S3変更なし。

2026-10-12 batch248：ReceyLarousse公開PDF取得、4頁画像（印刷1634）を直接確認し注記[sé]を確認。OCR[se]とアクセントを区別。全体IPAでなく省略凡例未確認、原施設一次住所差も残るため保留。PDFと画像はproject-local reading-sourcesに保存、SHA256は判断記録に記載。追加0、累計831、残45峰・25件、全体未登録4525。判断unnamed-world-batch248-review.json。表示・S3変更なし。

2026-10-12 batch249：Recey全原住所から別SIVOM登録4f1da0d5e4b0889e0787a559Impasse duMarchéを確認、内務省BANATIC同施設同街路と直接照合。番地なし及び旧登録7placeHoteldeVille差を保持。Larousse公開index.htmで1925と原PDFリンクを確認、凡例は未取得。追加0、累計831、残45峰・25件、全体未登録4525。判断unnamed-world-batch249-review.json。表示・S3変更なし。

2026-10-12 batch250：Recey同版A章62頁を取得、冒頭画像は印刷37a地理項目で凡例未収録と確認。次は1925全版巻頭または対象町現代辞書を確認、章冒頭再検索を繰り返さない。取得PDF・画像SHA256を判断記録に保存。追加0、累計831、残45峰・25件、全体未登録4525。判断unnamed-world-batch250-review.json。表示・S3変更なし。

2026-10-12 batch251：Receyは内務省住所を再確認し、Nénufar利用案内・Aux lecteursでは対象町の全名読み・同版凡例を確定できなかった。NiobraraはCollinsの川の発音と旅行記事の表記差を確認し、村への自動転用を保留。Vantageは原住所全39件を再検索し、401 South Mainを共有する複数ブランドを独立証拠にしないことを記録。新しい住所照合対象はBlustery's 301 Main StとVantage Coffee Co. 321 Vantage Hwy。3参照名を個別再調査、追加0、累計831、対象残45峰・25件、全体未登録4525。判断は[unnamed-world-batch251-review.json](unnamed-world-batch251-review.json)。表示・S3変更なし。

2026-10-12 batch252：Burstallバーストール1峰反映。Wikidata Q855486原JSONの日本語ラベルとGeoNames5912226を直接確認（revision2543753042）。原図書館425MartinStをCER資料1頁の同施設同番地と再照合。登録日本語名として採用し公的指定・当地録音の保証と区別。累計832峰（登録73・公開日本語29・編集730）、候補残44峰・25件、全体未登録4524。判断docs/unnamed-world-batch252-review.json。S3未更新。

第252回の反映後検証：全319,885峰・238地域×3表示下限=714検査を通過。登録名の分類、832峰の採用重複なし、画面と配信用パッケージの辞書・NOTICE一致を確認。ログdata/validation/world-display-address832-test.log。

2026-10-12 batch253：残る69参照名をGeoNamesIDでWikidata一括照合。56対応項目を取得、日本語ラベル一致はLismore2160062のみ。Q6559021原JSONでVIC町・リズモア・座標を確認し、原薬局32HighStを地域共同体本文同施設同住所で再照合。NSW同名都市から転用せず1峰採用。累計833峰（登録74・公開日本語29・編集730）、候補残43峰・25件、全体未登録4523。判断docs/unnamed-world-batch253-review.json。S3未更新。

2026-10-12 batch254：Ewen原BigValleyFord HighwayM-28を運営者同施設同道路・町・州に追加照合。州BTBLガイド抽出本文のĒYOO-inを確認、同版記号凡例は未取得。一般人名の読みから自動採用せず保留。追加0、累計833、候補43峰・25件、全体未登録4523。判断unnamed-world-batch254-review.json。表示・S3変更なし。

第255回：Redversの元POI Golden Age Centre・11 Broadway Stを町公式の同施設同番地と照合。命名元Sir Redvers BullerのOCLC日本語名から編集表記「レッドヴァーズ」1峰追加。異表記「レドバース」と公式日本語指定未確認も記録。累計834（登録74・公開29・編集731）、候補42峰・25件、未登録4522。判断unnamed-world-batch255-review.json。S3未更新。

第256回：Niobraraは州図書館委員会と連邦USACE本文で原図書館住所25414 Park Ave Ste3を直接再照合。村発音掲載ページの脚注は推定と明記し確定根拠から除外。Dinsmoreは命名元土地所有者と初代郵便局長を区別し、別州・他国の同姓人物を転用しない。追加0、累計834、候補42峰・25件、全体未登録4522。[個別記録](unnamed-world-batch256-review.json)。表示・S3変更なし。

第257回：VenjanはNEの現集落tätort項に語頭発音[vɛʹn-]を確認。教区・湖のみを定義する歴史方言辞典と区別。公式Transportstyrelsen住所Tennängsvägen5を原Venjans Handelと再照合し、語頭注記と残りの綴りを参考に編集表記ヴェンヤン1峰追加。全語IPA・当地録音を確認したものではない。累計835（登録74・公開29・編集732）、候補41峰・25件、未登録4521。判断unnamed-world-batch257-review.json。S3未更新。

第258回：Eatoniaは町公式でEaton Company由来と改称理由を確認。原Lutheran Church113 2nd Ave Eを町公式の同番地教会と照合。カナダ百貨店の公開日本語表記イートンズと追加綴りiaから編集表記イートニア1峰追加。現地全語録音・公的日本語指定未確認。原FCLと現Co-op法人同一性を断定せず教会で補強。累計836（登録74・公開29・編集733）、候補41峰・24件、未登録4520。判断unnamed-world-batch258-review.json。S3未更新。

第259回：Trussuの原学校POIを自治体の同名学校・地区に照合。Ciberdúvidasの対象地区の綴り解説とIBGEの旧表記Trussúを参考にトルスー1峰追加。語源・全語録音・公的日本語名は未確定。番地一致や移転を断定しない。累計837（登録74・公開29・編集734）、候補40峰・24件、未登録4519。判断unnamed-world-batch259-review.json。S3未更新。

第260回：政府観光局VisitPortugal日本語本文のSão Martinho do Portoにサン・マルティーニョを直接確認。ただし別町の共通語部分であり当地全名の公的日本語指定ではない。ホテル団体UnitedHotelsの公開検索PDF本文にはAmoreirasのアモレイラス表記。編集案サン・マルティーニョ・ダス・アモレイラスを得たが住所品質を再検査。2006年官報のFarmácia Vargues LadeiraはRua do Cruzeiro1で原POIのRua Dr.António Calapez Gomes Garcia1と街路不一致。自治体2023店一覧PDF2頁のMinimercado de Dulcina DuarteはLargo Adelino Ribeiro da Costa3で原Loja DulcinaのLargo Adelino Amaro da Costaと相違。誤記・改称・移転を断定しない。Monte Maravilhas運営者公式contact本文のGPS37度38分36秒N/8度23分46秒Wを確認し原POI37.651361521885,-8.40422399374588との球面距離1143mを再計算。原位置は同一施設の公式位置から約1.1km離れる。外部資料で地域名は支持されるが峰の付近の独立施設位置の確認には足りず保留。単に全語録音を待つ状態から、住所・位置の不一致の解決へ調査方針変更。表示追加0、密度・座標不変。 残り40峰・24件。判断unnamed-world-batch260-review.json。

第261回：Saint-HilarionはLoisirs運営者公式346Route138を元POIに直接照合。カナダ掲載のトラベルコ地域一覧とHotels.com同町QC住所のサンティラリオンを参考に編集表記1峰追加。別国同名町の表記は根拠に転用せず、現地録音・公的日本語指定の未確認を明記。累計838（登録74・公開29・編集735）、候補39峰・24件、未登録4518。判断unnamed-world-batch261-review.json。S3未更新。

第262回：Ulf Lundström2015、Umeå universitet Nordsvenska23 Bebyggelsenamnen i Bureå Burträsks och Lövångers socknar358頁公開PDFを取得。本文86頁Bygdsiljum項の原画像と87頁の地理説明を確認。BNに複数の全名方言形、Lindgrenに短縮形、IIに別の全名形が併記されるため一つを現標準形として選ばない。87頁Bygdsiljetは湾内側の別地名でありBygdsiljumの読みへ転用しない。ISOF現行地名辞典のBygdsiljum項は当該集落、旧SiljumとBygdの識別理由、湖湾の関係を説明するがIPAなし。NEも現集落情報のみ。SverigesRadio6365170は2016年2月11日の当該地名を扱う2分48秒の研究職員出演番組であることを本文確認、録音未聴取。PDFの文字抽出では独自音声字形が私用領域に化けるため原画像を保存、IPAとして自動変換しない。今回新たにまとまった大学研究と現行公的辞典の対象対応を確保。凡例・現標準形と古い方言形の対応が未解決で保留。住所ICA Robertsforsvägen4照合の既存根拠は維持、周辺郵便都市のPOIを町中心施設とみなさない。追加0。 累計838、残り39峰・24件。判断unnamed-world-batch262-review.json。

第263回：Saint-Ludgerの原Nazareth学校POI302 rue de l’Égliseを公的学校計画に直接照合。カナダ対象町の公開日本語用例サン リュジェを参考に編集表記サン・リュジェ1峰追加。英語IPAや別町の表記は当地フランス語の証明に転用しない。原Confection Lapierreの現営業は未確認、閉鎖転載情報を断定せず学校で補強。累計839（登録74・公開29・編集736）、候補38峰・24件、未登録4517。判断unnamed-world-batch263-review.json。S3未更新。

第264回：Manseauの原Résidence260St-Alphonseを自治体一覧に直接照合。ケベック研究14(2022)96頁公開検索本文の対象町マンソーを参考に編集表記1峰。Lysterの原Desjardins635Laurierを運営者現行本文に直接照合。Traveloka同町ホテル住所とリスターの日本語用例を参考に編集表記1峰。直接取得失敗と公開検索本文の区別を記録。別町・人名の読みを転用しない。累計841（登録74・公開29・編集738）、候補38峰・22件、未登録4515。判断unnamed-world-batch264-review.json。位置・密度不変。S3未更新。

第265回：Les Méchinsの原SAQ/JMP184BellevueOuestをSAQ現行Tag Dépanneur同住所と旧公式代理店PDFのJMP同住所に照合。三サンプルは同店舗所在地で独立三施設とは扱わない。英語版Wiktionary当該自治体全名IPA /le me.ʃɛ̃/の公開検索本文を参考に編集音写レ・メシャン1峰追加。直接取得失敗、現地録音・公的日本語指定未確認、フランス語版は発音未記載。語源から発音を推測せずモデルレメシヌを不採用。累計842（登録74・公開29・編集739）、候補38峰・21件、未登録4514。判断unnamed-world-batch265-review.json。密度・位置不変。S3未更新。

第266回：Lac-Etchemin原銀行2222eAvenueを運営者支店一覧本文・自治体索引に照合。Trip.com、Tripadvisor、Airbnb対象町の日本語表記を参考にラック・エトゥシュマン1峰。Saint-Paul-de-Montminy原Desjardins3054eAveを運営者公式検索本文とPDFに照合。Traveloka地域一覧の日本語用例を参考にサン・ポール・ド・モンミニ1峰。公開用例を参考にした編集表記で現地録音や公式日本語指定とは区別。原ABCは自治体同番地だけで同一施設としない。Saint-Just-de-BretenièresはAirbnb用例と原LHeureux367route204の二次住所を得たが一次住所未確認で保留。累計844（登録74・公開29・編集741）、候補38峰・19件、未登録4512。判断unnamed-world-batch266-review.json。密度・位置不変。S3未更新。

第267回：Saint-Just-de-Bretenières原Eglise Chrétienne Evangiliqueの204 Rte RR1 #130を自治体公式同教会130 Route204と施設名・番地・路線で照合。Airbnb対象町の公開検索本文の日本語用例を参考にサン・ジュスト・ド・ブレトニエール1峰追加。別人名の読みを無条件転用しない。原presbytère210Bと自治体Fabrique210Bは同一施設とは断定しない。現地録音や公的日本語指定未確認、編集表記として区別。累計845（登録74・公開29・編集742）、候補38峰・18件、未登録4511。判断unnamed-world-batch267-review.json。密度・位置不変。S3未更新。

第268回：Milverton原Gerbers15MainStNを会社自身のLinkedIn公開検索全文店舗一覧に照合。現公式Contactに掲載なしのため現営業は主張しない。AutoReserve同ON町のミルバートン用例を参考に編集表記1峰。直接取得失敗と公開検索本文を区別。Roseneathにローズニースの用例とEPAのKaHeatRR4住所を確認したが元RR施設7件完全同座標と別6件完全同座標を検出、Langs参考マリーナ位置約5.4km相違。名前の翻訳だけで位置品質を解決したとしない。町中心学校・FairGroundを次に照合。累計846（登録74・公開29・編集743）、候補37峰・18件、未登録4510。判断unnamed-world-batch268-review.json。密度・位置不変。S3未更新。

第269回：Roseneath原学校9047CountyRoad45を学校運営者公式9047Highway45に、FairGround9109CountyRoad45とCarouselを運営者公式所在地に直接照合。元2群完全同座標13件はworld active原本で13/13確認。sigma200mの同一shared格子で試験除外した場合、元頂点106.560866から54.826031、1km内最大55.697119、元位置はpeak_maskの頂点でなくなる。別点-78.057,44.1927に55.697119の峰が残る。名前と地域は支持されるが元の峰の位置品質に影響があり保留。試験のみであり全13件誤位置とは主張せず、配信密度・位置・辞書は変更していない。プローブroseneath-density-probe269.json、判断unnamed-world-batch269-review.json。次は13IDの公的住所・実位置を個別照合。累計846、残り37峰・18件、全体未登録4510。S3未更新。

第270回：自治体InfrastructureReport印刷6–8頁でRoseneath図書館と消防署3の同居を直接確認。元13IDの一括誤位置判定は避け、同居2IDを残した試験除外を再現可能スクリプトprobe_roseneath_density.pyに追加。元頂点106.560866から62.785236、1km最大63.157574、元位置は頂点でなくなる。残り11件全部の誤位置を確定した結果ではない。FenellaHall公式所在地8071CountyRoad45も確認したが公式地図リンク取得失敗で実座標未確定。名称追加0、累計846、候補37峰・保留18件、全体未登録4510。製品の密度・位置・辞書は変更なし。記録unnamed-world-batch270-review.json、実測roseneath-density-probe270.json。S3未更新。

第271回：Coronach原CanadaPost7 1stAveWを現自治体事業者一覧CanadaPostOffice7 1stAvenueWestに再照合。AutoReserve対象国州町の公開検索本文にコロナックと町内住所を確認、直接取得Cachemissを明記。町の日本語使用例を参考に編集表記コロナック1峰追加、公的日本語指定・当地音声とは区別。累計847（登録74・公開29・編集744）、候補36峰・保留18件、全体未登録4509。密度・座標不変、S3未更新。根拠unnamed-world-batch271-review.json。

第272回：Warooka原FoodWorks39MainStを現運営公式39MainStreet WarookaSA5577に直接照合。Airbnb対象AU SA町宿泊頁の公開検索本文ワルーカを編集表記に採用、都市頁ワルッカとの揺れ・自動翻訳・直接取得失敗を明記、公的指定や現地録音とはしない。追加1、累計848（登録74・公開29・編集745）、候補36峰・保留17件、全体未登録4508。密度・座標不変、S3未更新。根拠unnamed-world-batch272-review.json。

第273回：CA SK Strasbourg原町役場200MtnStを自治体December2025広報PDF1頁#1-200MountainStreet直接本文に照合、unit未記載を区別。EveryLittleThing広告は検索画像説明のみで主根拠にしない。AutoReserve当該カナダ町のストラスブール（サスカチュワン州）用例を公開検索本文に確認、直接取得失敗を記録。編集表記1峰追加、正式指定や当地音声とは区別。累計849（登録74・公開29・編集746）、候補35峰・保留17件、全体未登録4507。密度・座標不変、S3未更新。根拠unnamed-world-batch273-review.json。

第274回：McKenney原BP21101BoydtonPlankRdを取得済み郡公開契約PDF127頁BP9794132同番地同町に照合。店番号未記載やWallaceとの主体差は断定しない。AutoReserve対象町のマッケニーを編集表記追加、混在するMcLean誤分類店舗は根拠から除外。直接取得失敗と検索本文を区別。累計850（登録74・公開29・編集747）、候補34峰・保留17件、全体未登録4506。密度・座標不変、S3未更新。根拠unnamed-world-batch274-review.json。

第275回：Niobrara原図書館25414ParkAveSte3と州図書館委員会ホスト公式を直接照合。Mortlach原教会203RoseStと運営団体2020議事録PDF1頁の同施設住所を再照合、現在営業は主張しない。AutoReserve対象USNE村/CanadaSK町を明示した日本語用例ナイオブララ・モートラックを参考に編集表記2峰追加。公開検索本文と直接取得Cachemissを区別し公的指定・当地録音とはしない。累計852（登録74・公開29・編集749）、候補32峰・保留17件、全体未登録4504。密度・座標不変、S3未更新。根拠unnamed-world-batch275-review.json。

第276回：Chemultで育った鉄道関係者JackBowdenの2010-12-04口述記録PDFを直接確認。1-3、5頁の本人の居住・社宅・父の鉄道勤務の記述から当地との対応を確認。文字起こしは発音証拠ではなく、ケモルト/チェマルト等の揺れは未解消。原録音が次の確認対象。追加0、累計852、残り32峰・17件、全体未登録4504。表示・密度・位置変更なし、S3未更新。根拠unnamed-world-batch276-review.json、chemult-oral-history276.json。

第277回：OregonTech公式JackBowden OH021頁に文字起こしと音声リンクを直接確認。公開metadata id11はPDF文字起こし、id6はBowden_audio3_12-4-10 audio/mpeg7.mp3。公式案内WAVとの差、分割第三録音とPDF冒頭の発話対応が未確認で実聴なし。動画は図書館内閲覧という公式記載。録音存在を発音確定とはしない。次は分割対応と対象発話の検証。追加0、累計852、残り32峰・17件、全体未登録4504。表示・密度・位置不変、S3未更新。根拠unnamed-world-batch277-review.jsonとchemult-oral-recording277.json。

第278回：Ellsinore原East Carter小学校の24 S Herren Ave、Ellsinore MOを原parquetと学校運営公式本文で直接照合。別学校ID同番地を独立施設とは数えない。Airbnb対象町の検索本文エルサイノアと別宿泊タイトルエルシノアの揺れを記録。直接取得失敗・旅行翻訳用例と現地発音の区別を保持し読みは保留。追加0、累計852、候補32峰・保留17件、全体未登録4504。表示・密度・位置不変、S3未更新。根拠unnamed-world-batch278-review.json、ellsinore-address-reading278.json。

第279回：Rivière-au-Tonnerre原Complexe Locatif la Familia450Jacques-CartierRueを自治体公式宿泊一覧の同施設450rueJacques-Cartierと直接照合。併記29rue de l’Égliseは別住所として区別。CHOSEKI対象ケベック沿岸集落の座標付き日本語用例リヴィエール・オー・トネールを参考に編集表記1峰追加。Travelokaのオ／オー差と両サイト直接取得Cachemissを記録。修道会日本語町史の地名はLatin表記で読み証拠にはしない。公的指定・当地録音ではない。累計853（登録74・公開29・編集750）、候補32峰・保留16件、全体未登録4503。密度・位置不変、S3未更新。根拠unnamed-world-batch279-review.json、riviere-au-tonnerre-address-japanese279.json。

第280回：Mankota原学校4c745f7344d395214659f4be2401stAveを州選挙管理機関2020告示PDF1頁MankotaSchool2401stAvenueと直接照合。現PrairieSouth学校公式は2401stStreetEastで道路名差を保持。MankatoMNレビューの誤綴り日本語マンコタを転用しない。次は現学校地図と旧住所位置、当地の読みを確認。追加0、累計853、候補32峰・保留16件、全体未登録4503。表示・密度・位置不変、S3未更新。根拠unnamed-world-batch280-review.json、mankota-school-address280.json。

第280回の追確認：現学校公式掲載GoogleMapのURL内place座標49.4195783,-107.0673562は原学校から8.5m。地図本文未取得とURL掲載座標を区別。学校の位置は近接しAvenue/Street差だけで誤位置扱いしない。次の主課題は対象町の読み。

第281回：Lus-la-Croix-Haute原キャンプlAllevaと地域自然公園840route de lAlleva、LaChapelle原GallandSports Pont de la placeと観光局Pont la placeを再照合。元番地欠落・地区表記差は維持。Vrbo対象村の公開検索日本語用例を参考にリュス・ラ・クロワ・オート、ラ・シャペル・アン・ヴァルゴデマールの編集表記2峰追加。直接取得Cachemiss、自動翻訳用例、当地音声未聴取を明記、公的指定とはしない。累計855（登録74・公開29・編集752）、候補30峰・保留16件、全体未登録4501。密度・位置不変、S3未更新。根拠unnamed-world-batch281-review.json、french-villages-address-japanese281.json。

第282回：SãoMartinho原役場Largo de ValeBriqueを政府BEP2026公告とDGAL名簿のLargo do/ValeBriqueに地区照合。de/do差・番地欠落・郵便番号差、名簿座標と原役場約380m差を保持。薬局道路不一致とMonteMaravilhas約1143m差は未解消、名称証拠から外す。Airbnb対象PTBeja村の全名日本語用例サン・マルティーニョ・ダス・アモレイラスを参考に編集1峰追加。宿は村8km外で峰住所根拠にしない。検索本文・自動翻訳・直接取得失敗を区別。名称追加は全POIの品質保証ではない。累計856（登録74・公開29・編集753）、候補29峰・保留16件、全体未登録4500。密度・位置不変、S3未更新。根拠unnamed-world-batch282-review.json、sao-martinho-address-japanese282.json。

### 第283回：ヘデカス

診療所Dinglevägen6は1177、設備会社Hällekas väg1は運営者住所と照合。日本語の町名用例からヘデカスを編集表記で追加。図書館と掘削会社の現在住所は原POIと異なるため根拠から除外し、不一致を記録。現地音声の確認ではありません。累計857峰、今回対象の残り29峰・15件、全体未登録4,499峰。[個別記録](unnamed-world-batch283-review.json)。

### 第284回：ビスプガーデン

原ATMのForsvägen33をRagunda自治体2016–2020サービス計画12頁と照合。JTBの町名用例ビスプガーデンを参考に編集表記を追加。宿名ビスプゴーデンとの揺れ、自動翻訳の可能性、音声未確認を保持。現在の施設稼働や個体一致の保証ではありません。累計858、候補28峰・保留15件、全体未登録4,498峰。[判断記録](unnamed-world-batch284-review.json)。

### 第285回：ディカナス

原商店Albins väg5を政府Transportstyrelsen2014公告43頁、原学校Skolvägen1をSkolverket学校名簿16889382と直接照合。AFP2017-01-12現地取材記事3112743の発信地・本文にDikanas村のディカナスを確認し追加。遠隔郵便住所は今回根拠から除外。現地音声・公的日本語指定の保証とは区別。累計859（登録74・公開29・編集756）、候補28峰・保留14件、全体未登録4,497峰。[判断記録](unnamed-world-batch285-review.json)。

### 第286回：エルシノア

原学校24 S Herren Aveを学校運営公式と再照合。日本語宿泊紹介本文・別宿紹介に対象ミズーリ町のエルシノアを確認し、編集名として選択。エルサイノアとの揺れを保持し、同サービスの複数頁を独立した音声証拠とはしない。現地発音の未確認は残り、標準・公的日本語指定とは区別。累計860（登録74・公開29・編集757）、候補28峰・保留13件、全体未登録4,496峰。[判断記録](unnamed-world-batch286-review.json)。

### 第287回：ペンス

原役場324 Elder Stを自治体公式議事録の会議所在地・次回会議場所と直接照合。見出し2025年と内部2024年の日付差を保持。Expedia対象町のペンスへの旅行、日本語Airbnb町頁のペンス用例を参考に編集名を追加。直接日本語頁取得失敗、検索本文、自動翻訳の可能性、現地音声未確認を記録。累計861（登録74・公開29・編集758）、候補27峰・保留13件、全体未登録4,495峰。[判断記録](unnamed-world-batch287-review.json)。

### 第288回：Itunaの住所照合を補強

元劇場407 Main Street North、信用組合315 Main Street North、SARCAN511 Main Street North、Bailey’s Funeral Home103 Main Street Northを自治体名簿と施設名・番地まで直接照合。同番地別店舗、Co-op223対233、図書館の道路・番地差を保持。町対応の根拠は増えたが現地読み・日本語地名用例は不足して保留。新規追加なし、残り27峰・13件。表示データを変更していないため全域表示テストは再実行せず。[判断記録](unnamed-world-batch288-review.json)。

### 第289回：チルクート

原郵便局94217 CA-70をUSPS2021-07-14公式再開公告の同施設94217 State Highway70 ChilcootCA96105と直接照合。AutoReserve対象California町の日本語用例チルクートを参考に編集名を追加。直接日本語頁取得失敗、音声未確認、過去公告と現在稼働の区別を保持。Alaskaの峠・河川読みは使わない。累計862（登録74・公開29・編集759）、候補27峰・保留12件、全体未登録4,494峰。[判断記録](unnamed-world-batch289-review.json)。

## 第290回：コールレイン（North Carolina）
元小学校202 N Academy Stと教会202 N Main Stをそれぞれ運営者公式住所と直接照合。FamilySearch対象町の日本語用例を参考に編集名コールレインを追加。資料の翻訳表示・現地音声未確認を保持し、墓地を峰所在地証拠には使用しない。累計863（登録74・公開29・編集760）、候補27峰・保留11件、全体未登録4,493峰。S3未更新。[判断記録](unnamed-world-batch290-review.json)。

## 第291回：イトゥナ（Saskatchewan）
自治体名簿で劇場・信用組合・SARCAN・葬祭施設の元住所を再確認。Tripadvisor日本語地域宿泊一覧のItuna Motelに対応する町名イトゥナを確認し、自治体と同サービス英語個別施設の住所で対象町を確認。日本語検索本文・直接取得失敗・自動翻訳可能性を区別して編集名に採用。Zambia/Brazil同名地と自動Wikiは根拠にしない。累計864（登録74・公開29・編集761）、候補26峰・保留11件、全体未登録4,492峰。S3未更新。[判断記録](unnamed-world-batch291-review.json)。

## 第292回：ケナストン（Saskatchewan）
原図書館501 3rd St #309を自治体Location501 3rdStreetと照合。#309は公式Box309混入の可能性を残し、部屋番号とは認定しない。Tripadvisor対象町の個別宿泊施設日本語用例から編集名ケナストンを採用。検索本文・直接取得不能・翻訳可能性・音声未確認を保持。Winnipeg同名道路等は除外。累計865（登録74・公開29・編集762）、候補25峰・保留11件、全体未登録4,491峰。S3未更新。[判断記録](unnamed-world-batch292-review.json)。

## 第293回：マーカンド（Missouri）
元郵便局105 Whitener StをUSPS公式2013会議予定表105 S Whitenerと直接照合。方位S省略、過去資料と現在稼働を区別。対象町のTripadvisor日本語旅行情報と飲食一覧のマーカンドを参考に編集名を採用。日本語直接取得失敗、検索本文・翻訳可能性・音声未確認を保持。人名用例は根拠にしない。累計866（登録74・公開29・編集763）、候補25峰・保留10件、全体未登録4,490峰。S3未更新。[判断記録](unnamed-world-batch293-review.json)。

## 第294回：Beauvalの学校名と位置集中を再調査
原23件を再取得し、消防・浄水・住宅・医療等8施設と別の学校・商店・郵便等5施設が各群で完全同一座標と確認（第299回再集計で当初6件の記述を訂正）。位置精度を保証せず保留。鹿児島大学論文検索本文のボーヴァル校はIle-a-la-Crosse別称を含み、LaPlongeへの学校移転を記す資料も見つかった。町名への転用を避け、PDF本文と集中施設の実所在地を次に確認。追加なし、候補25峰・保留10件、累計866。表示データは変更せず表示検査の再実行なし。[判断記録](unnamed-world-batch294-review.json)。

## 第295回：Beauvalのキャンプ実所在地と郵送先を区別
集中8件中のPine Ridge Bible Campは公式directionsでCunnings Lake沿いHwy965、郵送先はPOBox160Beauval。市街共通座標に置く根拠にならない。湖代表点は実施設座標ではないため置換や精密誤差認定はしない。学区の学校町対応とNCTR学校期間を直接確認したが日本語名の追加なし。残25峰・10件、累計866。表示不変につき表示検査再実行なし。[判断記録](unnamed-world-batch295-review.json)。

## 第296回：Ewenの公式発音ガイドを検証
州BTBL検索本文Ewen(ĒYOO-in)を再確認。Kinderhook欄とKrug,Torey欄が同じような人名音写になる不整合を確認し、無批判な表記転用を避ける。Ewen自体の誤記とは断定しない。記号凡例本文・別根拠を次に確認し、人名の日本語用例は除外。追加なし、候補25峰・10件、累計866。表示データ不変につき検査再実行なし。[判断記録](unnamed-world-batch296-review.json)。

## 第297回：リーディー（Oklahoma）
原高校505 E SixthStを運営学校公式505 E6THStLeedeyOK73654に直接照合。Airbnb対象町の公開検索日本語用例リーディーから編集名を採用。直接取得失敗・翻訳可能性・現地音声未確認を保持。人名読みや生成音声は根拠から除外。累計867（登録74・公開29・編集764）、候補25峰・保留9件、全体未登録4,489峰。S3未更新。[判断記録](unnamed-world-batch297-review.json)。

## 第298回：ビュグズィリュム（Bygdsiljum）
原ICA Robertsforsvägen4を運営者公式同店舗同住所に直接照合。Airbnb周辺宿泊説明のビュグズィリュム(Bygdsiljum)を参考に編集名追加。同一説明の広域頁再掲を独立証拠にせず、8km離れた宿泊を峰所在地証拠にしない。検索本文・翻訳可能性・現地音声未確認を保持。累計868（登録74・公開29・編集765）、候補25峰・保留8件、全体未登録4,488峰。S3未更新。[判断記録](unnamed-world-batch298-review.json)。

## 第299回：Denare Beachの日本語候補と住所不一致、Beauvalの集計訂正
Airbnb対象町宿泊の検索本文にデナレ・ビーチがあるが直接取得は失敗。原22 POI中14件が異なる住所で完全同一座標。DenarePlexの原PA Geddes Drに対し州SPSA公式本文は1700 Wigwam Drive、PBCN公告検索本文は1718 Wigwam Driveで、同名だけで一致認定しない。町の日本語候補と峰位置の妥当性を分け、採用保留。Beauval全23件を再集計し最大8件・次5件、2件群2組・単独6件と確認し、以前の次群6件を訂正。追加0、累計868、候補25峰・保留8件、全体未登録4,488峰。表示データ不変のため再生成・表示検査・S3更新なし。[判断記録](unnamed-world-batch299-review.json)。

## 第300回：Myrnamの飲食店住所照合
原20件を再取得しC J s Restaurant5009 49Stと観光ガイド・自治体会議資料検索本文の同町同番地を照合。Cafe/Restaurantの屋号差と資料年を保持。観光ガイド直接取得404のため検索本文のみと明記。原住所nullの村役場を番地一致に数えず、ウクライナ語語源を現地英語読みとして転用しない。MyrnamとMyanmar、Granum商品の日本語、Vonda人名、クロアチア同名宿泊を除外。日本語読みの追加なし。累計868、対象25峰・保留8件、全体未登録4,488峰。表示変更がないため再生成・S3更新なし。[判断記録](unnamed-world-batch300-review.json)。

## 第301回：セントブルー（St. Brieux）
カナダ議会LANG第11回記録のファイル10頁で対象町をSt. Brewと呼ぶという具体的表記を直接確認。以前のPROC記録の現地読み・仏語読みの差に対し根拠を補完。原AffinityCreditUnion208MainStは運営者AffinityWealthの所在地一覧同町同番地に直接一致。原住所nullの学校は番地一致に数えない。英語Brewに基づく編集音写セントブルーを採用し、モデルのセントブリューと仏Saint-Brieucからの転用を避けた。公的日本語指定・音声実聴とは区別。累計869（登録74・公開29・編集766）、候補24峰・保留8件、全体未登録4,487峰。S3未更新。[判断記録](unnamed-world-batch301-review.json)。

## 第302回：トレハーン（Treherne）
原Sunrise Credit Union197BroadwayStを運営者2014決算資料登録事務所と検索本文で照合。現在営業とは区別。Tripadvisor個別宿泊頁の所在地カナダマニトバ州トレハーン、Latin住所TreherneManitobaから対象町日本語用例を確認し編集名採用。直接取得失敗・翻訳可能性・音声未確認を保持。宿泊郵便箱は峰所在地証拠にせず、由来の人名だけから読みを認定しない。累計870（登録74・公開29・編集767）、候補24峰・保留7件、全体未登録4,486峰。S3未更新。[判断記録](unnamed-world-batch302-review.json)。

## 第303回：チェマルト（Chemult）
原DawsonHouseLodge109455Highway97Nを運営者本文同番地同町と直接照合。Tripadvisor個別宿泊頁の所在地アメリカ合衆国オレゴン州チェマルトとLatin住所から町用例を確認して編集名追加。日本語直接取得失敗・検索本文・翻訳可能性を保持。用例施設WhisperingPinesは原POIにないため峰住所根拠には数えず、DawsonHouseで照合。OIT音声未聴取、ゲーム用例や公的日本語指定とは区別。累計871（登録74・公開29・編集768）、対象23峰・保留7件、全体未登録4,485峰。S3未更新。[判断記録](unnamed-world-batch303-review.json)。

## 第304回：Vantage Coffee Co.の店主取材と道路名不一致
原POI321VantageHwyを再取得。PalominoSunの店主取材本文は321MainStVantageWA98950で、対象町の対応を補強するが道路名の同一性未確定。元401SouthMainの複数ブランドを独立証拠にはせず、Blustery301MainStや自治体街路資料を次に確認する。Ohio同名CareerCenter、ノルウェーGranumGard、イタリア同名店舗の日本語用例は対象地域外として除外。追加なし、累計871、候補23峰・保留7件、全体未登録4,485峰。表示変更・S3更新なし。[判断記録](unnamed-world-batch304-review.json)。

## 第305回：Natomaの発音候補資料の矛盾確認
Namepediaは同名艦NatomaBayがKansas町由来とするが、米海軍DANFSはAlaskaの湾を定義し矛盾。この頁の人名発音を町の読み根拠から除外。California湖・Chicago道路・英国Ewen・AustraliaSmeatonの日本語表記は対象地域へ転用しない。Vantage郡考古調査PDFは公開参照できたがテキスト0行・スクリーンショットcache missで図面内容未確認、道路別名の確定根拠に数えない。追加なし、累計871、候補23峰・保留7件、全体未登録4,485峰。表示変更・S3更新なし。[判断記録](unnamed-world-batch305-review.json)。

## 第306回：Debdenの学校住所を学区PDF本文と照合
原学校2登録3153rdAveEを学区2024-2025学校連絡先PDF2024-12-02版1頁本文と直接照合。同施設の別登録を独立証拠に数えない。学校ホームはtimeout、学区SchoolFinder直接本文には動的学校一覧が欠落しているため、検索本文と区別してPDFを根拠とした。日本語デブドン用例は英国Essexで対象外。DinsmoreHotelは対象州の施設掲載があるが町名日本語未確認、人名・Virginia同名宿の読みを転用しない。追加0、累計871、候補23峰・保留7件、全体未登録4,485峰。表示データ・S3変更なし。[判断記録](unnamed-world-batch306-review.json)。

## 第307回：Hagensborgの対象町日本語候補
対象町・州・住所を伴うTripadvisor宿泊検索本文でハーゲンツボーグを確認し編集候補を記録。同提供者の複数頁を独立証拠に数えない。原16中13同座標の位置品質保留を維持。TweedsmuirParkLodge公式旅案内本文のBellaCoola空港から45分・港から63km車を再確認したが、道路距離を直線誤差と認定せず全13件の一括除外もしない。次は原施設別の所在地監査と除外感度計算。追加0、累計871、候補23峰・保留7件、全体未登録4,485峰。表示・S3変更なし。[判断記録](unnamed-world-batch307-review.json)。

## 第308回：Hagensborgの密度感度を再計算
[scripts/probe_hagensborg_density.py](../scripts/probe_hagensborg_density.py)で本番入力active.parquetと200mKDEを使い同区画を再計算。元頂59.9318件/km²、遠方ロッジ1件を除く試算55.9522で峰存続。集中13件すべて除く試算8.1971で1km以内極大なし。13施設全ての誤位置は未確定なので、一括除外や本番密度変更は行わない。次は残12件の住所位置を個別監査し確証ある除外集合で再計算。結果はdata/name-research/reading-sources/hagensborg-density-probe308.jsonに保存。追加0、累計871、候補23峰・保留7件、全体未登録4,485峰。表示・S3不変。[判断記録](unnamed-world-batch308-review.json)。

## 第309回：Hagensborgの施設別住所監査
Bailey Bridge Campsitesの2375 Saloompt River Rdは運営者と地域観光公式、商店1801 Hwy20は地域観光公式に一致。共有座標が正しいという認定とは区別。School District49は原1847に対し州公式2012資料1961で不一致。Lower Dean River Lodgeは空港からヘリ移動する宿泊施設と町の会社連絡先を分け、宿泊地が遠方という理由だけで会社登録を除外しない。追加0、累計871、候補23峰・保留7件、全体未登録4,485峰。表示変更なし、再生成・S3更新なし。[判断記録](unnamed-world-batch309-review.json)。

## 第310回：New Effingtonの住所対応を直接確認
州PUC2014申請PDF11頁のファイル2頁本文でRC Communications主事務所205 Main Street New Effington South Dakota57255を直接確認。原POI同法人同番地に一致。親法人同住所を独立位置証拠にせず、5頁POBox197は郵送先と区別。古い資料なので現在の営業は証明しない。住所対応は確定したが、日本語読みは保留。追加0、累計871、候補23峰・保留7件、全体未登録4,485峰。表示・S3変更なし。[判断記録](unnamed-world-batch310-review.json)。

## 第311回：Cuparの独立施設住所とColomeの自治体史料
Cuparの町公式でWheatland Agencies210 Stanley Stを再確認し、原Lee Funeral Home105 Stanley Stも同名同番地に直接照合。併記Regina店は区別。Lucky DollarとCupar Foodsは同番地でも屋号差があり同一認定しない。Colome公式About UsでChris Colombeからの町名由来と1908/1909年経緯を直接確認。由来確認を現地読みの証明にはしない。追加0、累計871、候補23峰・保留7件、全体未登録4,485峰。表示・S3変更なし。[判断記録](unnamed-world-batch311-review.json)。

## 第312回：Smeatonのキャンプ郵送先と実所在地
原St John Bosco CampはSmeaton中心でNorth Haven・Rainbow Lodgeと完全同一座標。運営者公式の夏季POBox217Smeatonは郵送先で、キャンプ本体はNarrow Hills州立公園Zeden/Ispuchaw湖畔。公式埋込地図リンク対象53.990598,-104.663023は原からWGS84直線56,535.7m。地図画像は取得失敗でリンク点を測量座標とは扱わない。町中心施設の根拠から除外し、密度への影響を次に検証。本番除外規則・密度・S3は未変更。追加0、累計871、候補23峰・保留7件、全体未登録4,485峰。[判断記録](unnamed-world-batch312-review.json)。

## 第313回：Smeatonの誤位置キャンプによる抽出しきい値への影響
本番入力active.parquetから200mKDEを再計算。元頂52.183883、Camp1件除外48.673297、CampとRainbow2件除外45.162711、集中全3件除外41.652125件/km²。峰抽出は50以上を条件とするため1件除外だけで1km以内の抽出峰0。幾何的極大の消失を意味しない。NorthHavenを誤位置扱いせず、全3件除外は感度試算のみ。本番再計算へまだ適用していないので残数は維持。追加0、累計871、候補23峰・保留7件、全体未登録4,485峰。S3変更なし。[再計算スクリプト](../scripts/probe_smeaton_density.py)、[判断記録](unnamed-world-batch313-review.json)。

## 第315回：Dinsmoreの保健運営者所在地と学校住所
原Dinsmore Health Care Centre1st St Eを州保健運営者207 1st Street Eに道路・町・州で直接照合。原番地欠落を完全一致に数えない。公式掲載地図リンク対象とのWGS84距離139.5m。Box338は郵送先。学校3rd Ave Wは学校公式200 3rd Ave Wと部分一致、別登録の住所nullは一致認定しない。読みは保留。追加0、累計871、候補23峰・保留7件。世界v3検証済み、S3配信はAWS再ログイン待ち。第314回は配信後の残数更新用として予約し未実行。[判断記録](unnamed-world-batch315-review.json)。

## 第316回：Myrnamの施設運営者住所との対応
元Eagle View Lodge4802 49 Aveを運営者Eagle Hill Foundation公式の同名施設・同番地・同町・同州に直接照合。Box280は郵送先。同住所の診療所は建物内併設と公式本文に記載され、独立した位置証拠に数えない。Servus5016 49Stの空室を示す二次物件検索結果は直接取得失敗で、原データ時点の営業状態や閉鎖時期を断定しない。町名の読みは未確定。追加0、累計871、候補23峰・保留7件。表示データは変更せず、全域表示検査の再実行は不要。第314回の配信後処理は最新316記録を引き継ぐ。[判断記録](unnamed-world-batch316-review.json)。

## 第317回：Recey-sur-Ourceの全名発音を編集表記へ反映
対象町の英語Wikipedia直接本文に全名IPA [ʁəsɛ syʁ uʁs]とINSEE21519を確認。既存Larousse部分表記を全IPAへ拡張せず、新たな全名資料から「レセ・シュル・ウルス」を編集音写。発音行に個別脚注がない百科事典であり、公式日本語名・実聴済みとは扱わない。住所31件・26座標・支持31/32・参照81mと既照合BANATIC SIVOM所在地を再確認。町役場5番はSIVOM7番と別施設。認証PDF RD928は検索本文のみ、直接404を明記。1峰追加、累計872、候補23峰・保留6件、全体未登録4,484峰。世界v3では未登録4,483峰。S3切替は未実施。[判断記録](unnamed-world-batch317-review.json)。

## 第318回：Roseneathの集会所位置の照合
自治体Fenella Community Hall8071 County Road45の公式リンク対象44.1506858,-78.0886228を取得。原Fenela Hall RR4からWGS84直線5,293.8m。地図画像未取得・リンク対象の測量保証なし。原郵便住所は番地欠落、綴り差と二次名簿11910CountyRoad24の不整合を保持。同一施設を断定して除外せず、他集中施設の個別照合へ進む。図書館・消防2件の正当な同居は保持。追加0、累計872、候補23峰・保留6件。審査スクリプトの前回参照を修正し、採用済み峰の保留再混入を拒否する検査を追加。表示データ変更なし。[判断記録](unnamed-world-batch318-review.json)。

## 第319回：Roseneathのリゾート実所在地
Lang’s Resortの原RR3と運営者25 Langs Road RR#3を部分照合。公式地図リンクの検索対象N44.24089 W78.07162と原座標のWGS84距離5,450.6m。地図画像は未取得で測量保証なし。原番地欠落を完全一致として扱わず、町中心の座標集中を引き続き監査する。図書館・消防の同居は保持。追加0、累計872、候補23峰・保留6件。表示データ・S3変更なし。[判断記録](unnamed-world-batch319-review.json)。

## 第320回：自治体計画による施設住所の補強
2015年採択の自治体道路計画PDFを直接確認し、Lang’s Resort & Campground25 Lang’s Roadを運営者住所と照合。前回公式地図リンクの原POIから5,450.6mの不整合を補強。Osprey Cottagesは外部Breken/YLM名簿の1026 Merrill Road RR3まで部分照合し、運営者サイトは未取得。計画にないことを閉鎖証拠にしない。追加0、累計872、候補23峰・保留6件。表示データ・S3変更なし。[判断記録](unnamed-world-batch320-review.json)。

## 第321回：New Effingtonの対象町と由来の区別
NPSの1989年歴史登録申請を直接確認。旧EffingtonはEffie Staufferに由来し、1913年に現在地へ移転。由来を全町名の発音根拠としない。原22POIを再照合。USPS検索本文211 Main Stと原住所は一致するが直接本文が別地域の表示となり、追加の確定住所証拠には数えない。既存の州PUC法人所在地の直接照合は保持。追加0、累計872、候補23峰・保留6件。表示変更なし。[判断記録](unnamed-world-batch321-review.json)。

## 第322回：Ewenの全体発音を編集表記へ反映
対象Michigan町の英語Wikipedia直接本文で全IPA /ˈjuːən/ とYEW-inを確認し、IPAからユーアンを編集音写。発音行の個別脚注なし、固定版URL取得失敗、公式日本語名や音声を聴いた認定ではない限界を記録。州BTBLの未知記号を推測削除せず別資料に基づく。原Big Valley Fordと運営者所在地の道路・町・州を再照合し、双方番地なしを保持。支持16/18・住所14・18座標・参照85m。1峰追加、累計873、候補22峰・保留6件、現行v2未登録4,483。v3では4,482でSmeaton消失1を区別。配信切替未実施。[判断記録](unnamed-world-batch322-review.json)。

## 第323回：Kinusoの公式保健施設住所の差異
州ANSPの2026-03-11更新PDFは230 Centre Street、公式施設詳細ページは40 Centre Streetで同電話。原Athabasca Health Unit230番との番地・道路・町・州対応を補強するが、屋号一致や移転・改番は未確定。Wiktionaryの由来欄には発音欄がなく、既存の由来人名と町の読みを区別する論文根拠を維持。追加0、累計873、候補22峰・保留6件。表示変更なし。[判断記録](unnamed-world-batch323-review.json)。


### 第324回（2026-10-12）

Kinuso、Vonda、Wikieupの3件を再確認。Kinusoは原V&S店舗227CentreStと運営者KinusoMercantileの物理住所227CenterStreetを照合し、仕入先一覧のVandS併記で屋号対応を補強。同店舗の複数ブランドは独立施設の追加根拠にしません。保健施設230/40番地問題は未解消です。Vondaは町公式204MainStを補助資料として確認しましたが、原HUB301MainStとは別施設です。Vonda辞書とWikieup百科事典に町固有の発音情報はなく、人名・近隣地名・一般名詞の発音は採用しません。今回の新規採用0、累計873、候補22峰・保留6件、現行v2未命名4483。調査継続中です。詳細はunnamed-world-batch324-review.json。


### 第325回（2026-10-12）

Colome（SD、43.260,-99.715）を「コローム」で1峰追加。1949年の地名発音資料What's that Name?のGoogleBooks公開書籍内検索応答を直接取得し、PP11のColome(kuh-LOHM)を確認。ページ全画像・音声は未確認で、編集音写として採用します。従来の自己近似KAH-lohmの資料とはアクセントが異なるため、この専門資料を根拠に選びました。元ColomeHighSchool01の105WCarrStと州教育局・市公式105CarrStを対応確認し、方向Wの記載差は保持。同校別登録を独立施設として二重計上しません。支持29/30、住所25、25座標、参照50mの条件を再検証。

Myrnamの町公式2025-09-16候補者資料は直接取得、3頁の由来句mir namを保存。由来句と現在町名の発音を区別して保留。Natomaは大学出版局の発音を含む地名辞典と1955年大学ジャーナリズム学部の専門発音辞典を発見したが、Natoma項目は未閲覧。Hathiの403を回避せず、個別項目の正規公開参照を次の調査先にします。

累計874（登録74・公開日本語29・編集771）、候補22峰・保留5件。現行v2未登録4482。原峰座標・密度不変。v3のSmeaton除外による未登録数差1は別管理で、配信切替は未実施。

第325回反映後、現行v2の全319885峰と238地域×3下限=714条件を実アプリの表示名・索引処理で再検証。禁止接尾辞0、外国文字名0、800以上の座標のみ表示0、元位置・密度不変を確認しました。ログはdata/validation/world-display-address874-test.log。静的配信用辞書の一致確認済み。


### 第326回：住所対応と発音資料の対象確認

MarnardalのMarnarbil所在地は、公式事業者登録と運営者の訪問先住所が元POIの番地・道路名・町名に対応。経路リンクは住所検索なので座標の裏付けとは扱わない。Kälarneの地域広報PDF第2頁の発音表記は町名ではなく人名Gjurdの説明であり、町名の根拠から除外した。新規採用0件、既存承認874峰、調査対象22峰と保留5件は継続。詳細はunnamed-world-batch326-review.json。


### 第327回：New Effingtonを確定

1949年South Dakota町名発音資料の公開検索応答PP17でNEW–EFF–ing–tunを直接確認。州PUC申請PDF第2頁の205 Main Street所在地と元POIを再照合し「ニューエフィントン」を編集表記として反映。モデル候補の余分なガ音を修正。累計875峰、残る候補22峰・保留4件。現行v2の地名未登録は4,481峰。調査対象群と全地名未登録件数は別の集計。


### 第328回：Wikieupの施設住所と位置を補強

Shell公式店舗の18183 S HWY 93、WIKIEUPと公式掲載座標が元サンプル住所・峰近傍に対応。町名の読みは未確定。出版社公開キャンプ資料には対象町名の発音表記がなく、自動翻訳百科事典の日本語表記も独立根拠として採用しない。新規0、承認875峰、候補22峰・保留4件。


### 第329回：カナダ公的地名資料の確認

連邦地名DBでMyrnamの正式名称・Alberta所在・座標を直接確認。発音資料ではないため読みの根拠にしない。州Directory of Communitiesは担当区域表で、名称横の記号は発音表記ではない。採用875、候補22峰・保留4件を維持。AWS STSを再実行したところセッション失効が継続しており、作成済みv3のS3公開は未実行。


### 第330回：Natomaの辞典掲載ページを特定

Google Booksの正規ISBN書誌から1001 Kansas Place Namesの版ID iKclAAAAMAAJを特定。公開検索はNatomaを139頁と222頁に検出したが抜粋本文は空。通常の139頁HTMLにも対象本文は公開されていないため読み未確定。次の確認先を具体的な139頁に絞った。採用875、候補22峰・保留4件。生応答はdata/name-research/reading-sources/natoma-google-search330.json。


### 第331回：Sapezalの日本語表記を確定、位置監査は継続

農林水産省公開資料のPDF180頁（印刷181頁）のスキャン画像を目視し、対象マット・グロッソ州のサペザル（Sapezal）表記を確認。読みは公開日本語用例として確定しreading_reviewに記録。読み検索を終え、同一座標12施設の位置監査を次の作業とする。峰表示はまだ未採用で、875峰・候補22峰・保留4件の件数は変わらない。


### 第332回：Sapezalの集中座標は公的台帳にも存在

CNES病院地図のhidden latitude/longitudeが元POIと同じ-12.989,-58.764と直接確認。公的台帳との一致だけでは実建物位置の裏付けにならない。地図初期中心のブラジリア座標も対象位置と区別。運営者の番地と自治体議会の別保健施設開院・地区を直接確認したが、独立した建物位置検証は継続。新規採用0、875峰、候補22峰・保留4件。


### 第333回：Sapezalの経路ページの位置不整合

病院併設Doyon Sapezal Iの公式住所を確認。公式リンクは住所検索のみ。Waze同名同番地HTMLは峰から62512.2m離れた座標を返すため補正に採用しない。別支店Campo Novoの地図も対象から除外した。新規採用0、875峰、候補22峰・保留4件。詳細sapezal-route-conflict333.json。


### 第334回：Sapezalの元集中点と正式市街位置の不整合

IBGE地図04/2021版を直接取得し市街所在地-13.55,-58.82を本文で確認。元集中点との差は62674.2m。第333回の経路との不一致を、経路側の誤りと判断してはいけないことが判明した。新しい公的町位置と経路は近接し、元POI側を疑って検証する。正確な施設位置はまだ未確認で、一括座標補正・除外は未実施。新規採用0、875峰、候補22峰・保留4件。


### 第335回：Sapezalの除外感度試算

同一計算法・200mで試算。元62.966件/km²、病院のみ58.987、4公共施設47.049、12件15.217。4施設の試算で1km内の抽出峰は0。市公式で市立検査所Curimba所在とMarlenaのJardim Sapezal地区を直接確認。全施設の位置確定や公開反映は未完了で本番未変更。875峰、候補22峰・保留4件。


### 第336回：Sapezalの公共施設4件を位置品質保留方針へ追加

旧市座標に集中した4公共施設を個別審査による位置品質保留としてv4方針へ追加。累計5441ID、原データ保持、残る8同点施設は維持、架空の座標補正なし。これは再計算方針でありv4生成・公開は未実施。候補群875採用/22峰・4件は公開完了まで据え置く。


### 第338回：v4の配信パッケージ生成完了、全体組立中

5441ID保留方針で影響15区画・14パッケージ生成完了。変更外2933パッケージを保持。概観と全峰索引組立は実行中（world-v4-assembly.log）。組立前のmanifestによる検証は未成立のため組立後に検証する。公開データと候補群の解決件数はまだ変更なし。


### 第339回：v4全体検証完了、公開は未実施

全世界319883峰、対象2峰不在、変更外2933アーカイブSHA一致、702変更タイル復号確認。採用875峰は全件存続し、原5356対象のv4未登録4479・再計算消失2。全238地域×3条件714表示検査通過。配信中v2は未登録4481のまま。公開後に2峰を候補群から退役するため、現在の残り22峰・4件は据え置き。


### 第341回：Vantageの地域発音資料を直接確認

大学作成のWashington Names第5版1987を許可付き公開先から取得。印刷39頁(PDF40頁)画像でVantage Ferry,KittitasのVAN-tij FAIR-eeを目視確認。一般名詞の発音転用ではなく地域地名資料。渡船名項目であることと現代町名単独の音声未確認を明記し、施設住所品質の審査は継続。新規採用0、承認875、候補22峰・4件。


### 第342回：Vantageの別屋号と施設位置資料

現運営者The Ranchの301VantageHwyを直接確認。元Blusterys301MainStとは屋号・道路名差があるため同一施設と未確定。郡公開の2006文化資源調査にBlusterysを位置目印とする記載を発見し、次の本文図確認先とする。既存の地域発音資料は保持。新規採用0、875承認、候補22峰・4件。


### 第343回：Vantage図面取得と代替公的文書の参照先

郡調査PDFは直接取得接続タイムアウト、web本文なし・画像Cachemissで図面未確認。同一事業BCSCBNの州SEPA200607345登録を新発見し3添付資料の題名を検索本文で確認。直接州ページ502で添付本文未取得。地図確認・新規採用と誤記しない。次は州の正規添付取得。875承認、候補22峰・4件。


### 第344回：Vantageを編集音写で採用

大学地域地名資料のVAN-tijと対象町・旧渡船の対応を基にヴァンティジと音写。Riverstoneは運営者551MainStと公営GrantPUD資料PDF201頁B161の町・西岸・渡船場近接を直接確認。原Riverstone住所nullは番地一致と扱わず、CoffeeCo道路名差と401Mainブランド問題も保持。施設一覧の正確さを全件保証する命名ではない。1峰追加、876採用、候補21峰・4件。現行v2未登録4480、未公開v4未登録4478・再計算消失2。


### 第345回：Cuparの発音欄と公的サイトの対象範囲

Wiktionaryはカナダ町語義を含むが発音欄の地域町との対応は不明示。cup/coop差は未解決、地域投稿直接403。国連2007カナダ報告PDFを直接確認し当時の公的発音サイトは3地域の限定先住民名対象と把握、Saskatchewanの全町名辞典と誤認しない。新規0、876採用、候補21峰・4件。


### 第346回：CBCカナダ地名発音辞典のスキャンを特定

1959年CBC発音ガイドのArchive識別子guidetopronuncia0000canaと書誌を直接メタデータで確認。PDF/OCRはprivate、access-restricted-item trueで本文未取得。ERIC公開書誌の改訂1959とも対応。Cupar・Granum・Myrnamの正規個別項目確認先を具体化したが記載有無・読みは未確認。新規採用0、承認876、候補21峰・4件。


### 第347回：CBC1959のCupar掲載頁と公開検索を確認

Cornell所蔵版GoogleBooks sbEvAAAAYAAJは1959改訂32頁。公開検索でCuparSask/PA12と発音列の抜粋を取得。ただし平坦化された二列の対応は未検証、本文画像は閲覧不可なので制限回避しない。Granum/Myrnam/Dinsmore/Consul/Mankotaは公開検索0件（未収録と断定しない）。新規0、876承認、候補21峰・4件。


### 第348回：CuparをCBC資料に基づく編集表記で採用

1959CBC公開抜粋の隣接順序Cumshewa/Cupar/Czarと対応する発音列を照合しクーパーを採用。ページ画像や現代音声は未確認と明記。町公式Wheatland210StanleyとLeeFuneral105Stanleyを原POIに再照合。cup型地域投稿は未確認異表記として保持。1峰追加、877採用、候補20峰・4件。現行v2未登録4479、未公開v4未登録4477、再計算消失2。

### 第349回：Kälarneの所在地を公的資料で再確認

Bräcke自治体2024-01-26選挙会場資料VN2024/9のHotell Östjemten・Stationsvägen 6・Kälarneと、元POI c5da9cdd3655486ee7a14bf3の施設名・Stationsv.6を照合。町との対応は補強できた。Nordisk familjebok第4版13巻163–164頁の町名個別項目を直接取得したが音声表記なし。地域一般の方言説明、人物の発音を町名に転用しない。Riksarkivet書誌でCarl Lindberg「Kälarne」Jämten1934 pp177–193を確認、本文と発音掲載は未確認。新規採用0、承認877、候補20峰・保留4件。辞書・配信内容は変更していない。[確認記録](unnamed-world-batch349-review.json)。

### 第350回：Wikieupの読みを採用、Hagensborgの発音根拠を確認

The Mooney Flyer 2015年6月号の公開原PDF（42頁、2,995,740 bytes）を直接取得。PDF第17頁／印刷17頁に対象アリゾナ町名Wikieupの発音「Wick-ee-up」があり、目次の執筆者Jim Priceは同誌教官一覧でアリゾナ州Chandlerの教官として確認できる。これに基づく「ウィキアップ」を編集表記として採用。Shell公式18183 S HWY 93と原4c45ea8f342c1b8d9613b589、BLM2016告知の郵便局18170 US Highway 93と原5eea0b887bfc290008ee1bcaを照合した。公式日本語名や実聴確認とは扱わない。

CBC1959の公開検索8町のうちHagensborg BC／PA15でhăg-ens-burgを確認。編集候補ハゲンズバーグを記録したが、13施設の完全同座標問題が残るため名称反映は保留。他7町の検索0件は未収録の証明ではない。累計878、候補20峰・保留3件。現行v2未登録4478、未公開v4未登録4476、再計算による消失2を区別。両版の全世界名称検査と238地域×3条件＝714検査が各々成功。辞書を公開用ローカルパッケージへ反映、S3地形の版切替は未実施。[判断記録](unnamed-world-batch350-review.json)。

### 第351回：Hagensborgの運営者所在地設定を照合

Bailey Bridgeの公開サイト設定は住所2375 Saloompt River RoadにbusinessLocationCoordinates 52.4001397,-126.5397015を対応させており、原1473f3e4e4de401fe8bbd44cから2,152.1m離れる。単なる地図中心とは異なる所在地設定だが、測量済み施設座標とは扱わない。RV2021の検索抜粋は52.40800,-126.49971で原から1,554.1m、運営者設定とも異なる。原座標・密度は変更せず確認継続。TSBCの2024年末収集施設一覧PDF第36頁はMecham SalesのPhysical Addressを1843 Chilcotin-Bella Coola Hwy/Hagensborgと示し、元POIの番地町を補強。別の州燃料供給者資料の1846という番地差は未解決。新規採用0、878採用、候補20峰・保留3件。[確認記録](unnamed-world-batch351-review.json)。

### 第352回：地域発音辞典からMankota・Consulを採用

Bill Barryが自著の発音ガイドを紹介する[公開記事](https://www.virtualsk.com/current_issue/billnew.html)を確認。2003年People Places: Contemporary Saskatchewan Place Names（ISBN1894022920）のGoogle Books識別子VPwRAQAAIAAJを取得し、通常の公開検索を利用した。PA4の著者説明は対象地を知る人の読みを実聴した場合に発音を掲載すると示す。PA151のMankotaの発音表記から「マンコータ」、PA55のConsulから「カンサル」を編集音写として採用。全頁画像・現代音声の実聴や公式日本語指定とは区別。元POIと学校公式240番地、州観光局Manley105CentreStの住所対応を再確認した。

州地名データを読取専用で取得し、8町の命名由来と公式キーを保存。Mankotaの州HAKXEと辞典の由来が一致する。Consulの州HAUWHは官職由来を示す。Beauval／PA21・Denare Beach／PA64も対象の読みを確認したが施設座標集中が未解消で保留。Debden／PA63、Dinsmore／PA66、Vonda／PA257、Sandy Bay／PA222の公開抜粋には発音が見えず、未掲載と断定しない。保存先はdata/name-research/reading-sources/saskatchewan-*.json。

2峰追加、累計880（登録74・公開日本語29・編集777）、候補18峰・保留3件。現行v2未登録4476、未公開v4未登録4474・再計算消失2。両版の全世界名称検査・714地域条件検査を通過。ローカル公開用パッケージへ反映、配信地形の版切替は未実施。[採用判断](unnamed-world-batch352-review.json)。

### 第353回：4町の発音検索を追加照合

Debden・Vonda・Dinsmore・Sandy Bayについて辞典VPwRAQAAIAAJの公開検索を追加。Sandy Bayとpronunciationを含むPA208の発音はReginaの説明であり、対象町へ転用しない。他3町の追加検索も発音未確認（未収録とは断定しない）。新版公開書誌APIとWiktionary直接取得はHTTPエラー、制限回避は行わない。カナダ町語義を含むDebdenのweb本文は発音欄なし。住所判断・辞書・キューは変更せず、地域の個別発音資料の確認を継続。新規0、880採用、候補18峰・保留3件。[確認記録](unnamed-world-batch353-review.json)。

### 第354回：Adulienaの方言調査本文を確認

ラトビア大学Edmunds Trumpaの公開PDFを直接取得（23,287,599 bytes）、本文のAduliena記載頁を抽出。Aduliena408は調査地点番号であり、音声転写はlogs/griežu/rietなどの例語を対象としている。町名の発音ではないため音写の根拠に転用しない。元住所ParquetのAduliena25件の学校内部登録とLazdukalnsの個人部屋・家具等の登録を再取得して既存粒度問題を確認。原座標・密度・名称は変更なし。累計880、候補18峰・保留3件。[本文確認記録](unnamed-world-batch354-review.json)。

### 第355回：Marnardalの集落名としての対象範囲を確認

ISOF公開NORNA2023要旨のRune Røsstad発表は、復元地名Marnardalが1920年頃に谷域名、1943年から駅名、その後駅周囲集落名へ広がったと説明。旧自治体名に限らないことを補強できるが、現代全語の発音転写はない。隣接するGotlandのr脱落の発表をノルウェー町名へ転用しない。SNL旧自治体記事とWiktionaryも発音欄なし。住所判断は保持、名称・密度変更なし。累計880、候補18峰・保留3件。[確認記録](unnamed-world-batch355-review.json)。

### 第356回：Saint Marksの外国店舗混入を個別判断

元4f1e4b2fe4b03ae3651832dbは古奈屋Konaya Curry Udon & Tempura／4th Fl., Terminal21、countryUS、SaintMarks座標。The Nation2013-07-12の経営者取材本文はBangkokのKonaya店舗を紹介しTerminal21第四階支店を明示。タイ政府観光庁の建物所在地とも対応するため、米国の峰を裏付けるPOIとして使えず、次の密度修正版でこの1IDを計算保留する判断を確定。精密なタイ店舗座標へ推測移動はしない。営業状態の判断や周辺米国施設の一括除外ではない。配信データへはまだ未適用。AWS認証の再確認はsession expired、S3切替は再認証待ち。名称採用880・候補18峰・保留3件は維持。[個別判断](saint-marks-location-review356.json)。

### 第357回：Saint Marksの1ID保留による密度影響を計算

scripts/probe_saint_marks_density.pyで原点の周辺区画をσ200mで再計算。Konaya1IDの保留前80.5052件/km²、保留後79.9617件/km²、1km内の峰は両方で同じ格子点に残る。外国店舗1件を除くだけでは、この峰全体を削除する根拠にはならない。周辺施設の位置確認と町名読みは引き続き必要。原本・配信は未変更。累計880、候補18峰・保留3件。[再計算を含む判断](unnamed-world-batch357-review.json)。

### 第358回：Saint Marksの現地マリーナを運営者・郡資料で照合

現運営者BowlineのShields Marinaページは95 Riverside Drive／Saint Marks FL32355をVisit Usとして明示。郡の公開観光ガイドも同施設同住所を示し、原2ID5fd1328594d6587ab00f42a7・5fd1670a3c03e267997002e5と一致する。2IDを別施設として二重計上しない。Waterway Guideの公開地点は原から28.6mで補助的に対応するが、運営者地点や測量点とは扱わない。外国店舗混入と正しい米国施設を分ける根拠を補強、周辺全件と読みは未確定。新規採用0、累計880、候補18峰・保留3件。[個別照合記録](unnamed-world-batch358-review.json)。

### 世界v5：確認済み外国店舗の追加保留を生成

docs/held-density-exclusions-v5.jsonはv4の5441IDに確認済みKonaya1IDを加え、5442IDを原スナップショット・座標付きで保留する。scripts/rebuild_held_density_v5.pyはv4に対し影響の重ならない2区画・1パッケージだけ再計算、生成完了。残る2946パッケージはv4をコピーし、検証ではSHA256一致を確認する。入力101729093件。全世界索引・概観の組立と地形検証が完了。2946未変更パッケージのSHA256一致、変更88タイル、旧13峰の保留、Smeaton/Sapezalの消失、SaintMarks存続を確認。880名称の全世界検査と238地域×3条件の714検査も成功。配信への反映は未実施。処理状態はdata/validation/world-v5-workflow-status.jsonとライブプロセスを合わせて確認し、状態ファイルだけで完了としない。名称880・候補18峰・保留3件は維持。

### 世界v5の公開後の残数更新を準備

v5に実在する初期5356峰を再集計し、採用880・未登録4474・再計算消失2（Smeaton、Sapezal）を確認。scripts/retire_unnamed_world_v5.pyは、S3公開成功・Range/CORS検証・画面のv5選択を必須条件として、この2峰を候補キューから更新する。未公開のため未実行、現行v2の候補18峰・保留3件は維持。公開後も未確定16峰・3件の調査が残る。v4用の旧手順に最新結果を誤って混在させない。新規名称採用なし。

AWS再認証完了後の配信コマンド（現時点では未実行）:

```powershell
.venv\Scripts\python.exe scripts/publish_world.py --root data/distribution/foursquare-world-v5 --stage data/world-release-v5 --prefix nigiwai-topo/world/2026-09-15-v5/ --frontend-report data/validation/world-v5-frontend.json --report data/validation/world-v5-published.json
```

配信結果の検査後に画面のURLを切り替え、名称辞書の選択版を更新してから候補キューを更新する。

### 第360回：Roseneathの旧キャンプ名と現運営者住所を区別

旧Osprey Cottages原6f42d024ccb943bb8c7d47d6は郵送RR3を持つ。従来第三者掲載の1026MerrillRoadUnit12について、現AwayCabins運営者のWelcomeManual・OurStoryに同番地同Unit・Roseneathを確認。80年前の5小屋を改修した説明はあるが、Ospreyからの継承を明記しておらず同一事業者・移転・閉店とは断定しない。FenellaHallも自治体現ページと2014インフラ資料の8071CountyRoad45／Concession9PartLot21を確認、別の第三者番地を混同しない。名称・位置・密度変更なし、880採用、候補18峰・保留3件。[調査記録](unnamed-world-batch360-review.json)。

### 第361回：Granumの郵便局改名と町名の語源を区別

郵便史学会JAPH7の公開PDF第58–61頁を確認。The Leavings郵便局は1907-10-01にGranumへ改名、穀物栽培の普及に伴うラテン語grain由来と記す。1894年の別The Leavings／New Oxley郵便局とは区別する。郵便局の改名日と1908年の自治体改名日を混同しない。対象地と語源は補強できたが現地発音の記載はなく新規採用0。住所が確認できた読み未確定名について、標準発音規則による推定編集表記を採用するか、地域の読み資料まで保留するかをユーザーへ質問中。位置品質の確認は別に続ける。累計880、候補18峰・保留3件。[確認記録](unnamed-world-batch361-review.json)。

### 第362回：Denare Beachの施設区画を公的計画書で確認

Official Community Plan PDF第62頁／印刷48頁は博物館Parcel L Plan CS5884／BeaverDrive、Denareplex Lots9–12 Block36 Plan72PA18348／WigwamDriveを明示。博物館原POIの道路・施設対応を補強、Denareplex原PaGeddesDrとの差は未解消。SPSA2025の1700と選挙資料検索抜粋1718の番地差も保持。原22件中14件の完全同座標を再確認したが正確な施設点は未確定。次にMap1A/1Bの区画と原共有座標を比較する。新規0、880採用、候補18峰・保留3件。[区画対応記録](unnamed-world-batch362-review.json)。

### 第363回：Denare Beach計画書の別添地図欠落を確認

原PDFを直接取得（6,442,770 bytes、106頁）し全頁本文を確認。末尾は印刷92頁Referencesで、目次にあるMap1/1A/1Bの印刷93–95頁はこの公開ファイルに含まれない。PDF第105頁を地図と取り違えない。区画番号の本文根拠は有効だが、元共有座標と区画図の照合は未実施。次は別添計画図の取得先を確認する。名前・密度変更なし、880採用、候補18峰・保留3件。[資料範囲の確認](unnamed-world-batch363-review.json)。


### 追加確認364：Denare Beach区画図との照合

自治体計画事業が公開する1頁の基図（604,864 bytes）を取得し、PDFに埋め込まれたGEO viewportを用いて14施設の共有座標を近似投影した。描画した区画図では共有点はBlock19北東側にあり、OCPがDenareplexの敷地とするBlock36 Lots9–12とは一致しない。道路名だけの照合から、区画を使った位置不整合の確認に進んだ。

14施設すべての誤りを示した結果ではないため、一括除外や代替座標への移動は行っていない。今回の新規名称採用は0件。累計880峰、個別保留18峰と3参照。詳細は`unnamed-world-batch364-review.json`、投影条件は`data/name-research/reading-sources/denare-basemap364-georef.json`。


### 追加確認365：Denareplex単独除外の密度感度

`probe_denare_density.py`で元POIを再計算し、区画不一致が確認できたDenareplexの1 IDのみ除外した場合を比較した。200m平滑化の近傍極大は65.9262から61.9467件/km²に低下するが、同じ格子位置の極大は残る。入力した丸め座標自体は元から極大点ではない。1件の問題から峰全体の削除は正当化できないため、公開データや除外ポリシーは変更しない。新規名称採用0件、累計880峰、個別保留18峰と3参照。


### 追加確認366：Northern Gateway Museumの敷地照合

OCP第62頁のParcel Lを基図の区画記号と照合し、博物館も共有POI点Block19とは異なる区画にあることを確認。MAS公開本文では所在地の説明がMoody Driveで、OCPと元POIのBeaver Drとの道路表現差は残す。区画記号を正確な施設入口座標として扱わない。Denareplexと博物館の2 IDだけ除く感度計算でも、近傍極大は65.9262から57.9671に下がるが同じ位置に残る。公開データ変更なし、名称採用0件。詳細は`unnamed-world-batch366-review.json`。


### 追加確認367：村役場の住所と共有点

州政府Municipal DirectoryのPhysical Addressは512 - 7 Avenueで、元POIの512 7th Aveと一致する。施設の同定は補強されたが、基図の共有点は9AV〜10AV間のBlock19にあり、7AVとの位置対応を確認できない。OCP本文では村役場はDenareplexの向かい。自治体位置の地図リンクを役場建物位置の証明には使わない。新規名称採用0件、累計880峰、個別保留18峰と3参照。


### 第368回：デネアビーチの名称採用

地域の読み資料と21/22件のPOI所在地対応、村域内の座標を根拠にデネアビーチを編集音写として採用した。名称確認と個別施設の座標品質を分離する。3施設の位置不整合は解決済みにはせず、batch364〜367の記録を保持する。累計881峰、個別保留17峰と3参照、初期5,356峰コホートの現行v2未登録4,475峰。


### 第369回：ボーヴァルの名称採用

地域発音辞典の対象村[bo VAL]、23/23件の住所所在地、参照距離710m、州基図の村域内への峰位置の近似投影と目視照合を根拠にボーヴァルを編集音写として採用。基図は参考用で法的境界の判定には使わない。キャンプの郵送先と実所在地差、座標集中の品質課題は解決扱いにしない。累計882峰、個別保留16峰と3参照。


### 第370回：ハゲンズバーグの名称採用

CBC1959の対象町HagensborgBCの読みhăg-ens-burgと地域観光局のMercantile1801BC20を再照合し、ハゲンズバーグを編集音写として採用。16/16所在地対応、15住所、4座標、参照距離467m。13件同座標や遠隔施設の位置品質を解決済みとはしない。累計883峰、個別保留15峰と3参照。


### 第371〜372回：国立図書館発音辞書によるMarnardal確定

NB Uttale（CC0）の公開ZIP165,273,254 bytesを取得し、10 CSVすべてでMarnardalの地名項目を確認。南西・西ノルウェーIPA mɑːr.nɑr.ˌdɑːlを根拠にマールナルダールを編集音写として採用。音声実聴や正式日本語指定ではなく、辞書の方言転写は文字列置換であることを明記する。原POI住所とBrreg・Sjekkpunktの対象事業者住所の既存対応を保持。スウェーデン発音辞典のK見出し13〜15頁ではKälarneが見つからず保留。累計884峰、個別保留14峰と3参照。


### 追加確認373：方言論文の対象地名を区別

Mid Sweden Universityの公開論文を取得しPDF33頁のKälarne言及前後を確認。IPA çaɳおよびGuɭçaɳ/GuɭçaɭはGultjäl/Gulkälの議論で、Kälarne全語の転写ではないため採用根拠に使わない。新規名称採用0件。累計884峰、個別保留14峰と3参照を維持。


### 追加確認374：ISOF個別カードの参照先

Håsjö索引のKälarneカード117〜121を移転後のISOF公開サーバーから取得し原画像を確認。鉄道駅・旧教区総称・集落の参照カードには全語発音転写がない。E.Lindberg NoB1930 p73ff、Jämten1934 p177、StSL3:2 p100を確認。NoB1930本文を次の探索対象とする。新規採用0件、累計884峰、個別保留14峰と3参照。


### 追加確認375：参照年の訂正

カード117を拡大し参照はNoB1950 s73ffと再読。第374回の1930という転記を訂正する。発行元の正式無料フォームで取得した1930冊子114頁では印刷73〜76頁はSahlgrenの別論文だったため、採用根拠には使わない。次は1950年本文を照合する。新規採用なし。

訂正後の1950冊子も発行元の無料フォームから取得（6,358,464 bytes、82頁）。原画像で印刷71〜74頁を確認し、Carl Lindbergの対象論文と印刷73頁のKälen/Kälarneから鉄道駅名への説明を確認。地域対応の歴史根拠は補強されたが、確認範囲に全語発音転写はなく名称採用は行わない。


### 追加確認376：Jämtenのデジタル化と公開範囲

受託者Skriptorietの2025-05-23記録でJamtli向け約113冊のOCR付きPDF納品を確認。ただし公開本文取得の証拠ではない。博物館の販売ページに1934冊子があるが、購入は行わず、公開本文への導線は未確認。Latvia地名検索で出たlazdaの発音ボタンも姓Lazdukalnsの一覧と一般語の読みであり対象地名全語の根拠には使わない。新規採用0件。累計884峰、個別保留14峰と3参照。


### 追加確認377：個別カードの略語照合

現行ISOF公式略語表でSLの説明を確認したが、カードのStSL/SvSLという転記から参照書誌を確定するには不足する。SLの展開だけを元に別資料を対象資料と認定しない。新規採用0件、累計884峰、個別保留14峰と3参照。


### 世界v5配信・2峰の解決

AWSログインを確認後、世界v5を新しいS3プレフィックスに配信。7,052ファイル394,378,824 bytesのキーとサイズ一致、Range206、CORSとプリフライトを確認。web/config.jsをv5へ切替し、公開・選択を必須とするガード付き処理でSmeaton/Sapezalの2峰を解決。884採用、未登録4,470、消失2、個別保留12峰と3参照。


### 第380回：推定表記15件・原対象全体の監査

ユーザーの了承に基づき、残る12候補峰と3参照を推定音写として採用し、画面の名称に「（推定）」を必須とした。根拠文と辞書のreading_statusも推定を明示。元のbatch12の保留203峰・69参照を全件個別照合したところ、269参照に対応する272峰は255確認表記・15推定表記・2修正密度消失で解決され、未説明の対象0件。計899名称、初期未登録コホート5,356峰の残り4,455、密度消失2。POI座標集中や施設内登録、推定読みは確定現地発音と区別し、記録を保持。


### 追加調査381：残る4,455峰の再照合

優先度1は406、優先度2は1,210、優先度3は2,839峰。従来の85%等の条件をそのまま満たす未採用峰は0件。住所地名一致率80%以上などを探索用に用いた91峰を抽出したが、採用基準の自動引下げは行わない。Port CarlingはLCBO115MedoraStreet（公式検索抜粋、直接403）と公共図書館69JosephStreet（公式公開本文）を元POIに照合。各施設の重複IDを独立施設として水増ししない。Kemptvilleの広域自治体名混在とDharwadの複合都市名・欠損欄を確認中。AxisBankの直接取得はPDFでなくHTMLが返り、PDF本文確認扱いにはしない。調査候補`frontier381.json`、結果`unnamed-world-frontier381-review.json`。追加採用0件。

その後、Webツールの公開PDF抽出本文（全44頁、第36頁）でDharwadの5CharantimathArcade/CBT向かい/580001を確認し、対象元ATMとの対応を補強。ローカル直接取得のHTMLをPDFとして扱った結果ではない。


### 追加調査382：Port Carlingの個別採用

LCBO115MedoraStreet公式検索抜粋（直接403）と図書館69JosephStreet公式本文を元POIに照合し、独立2施設の位置が峰から27m・370mであることを確認。個別記録に対する公式住所照合手順を追加し、重複施設を拒否する検証と元住所の一致を確認。街名支持169/211、156独立座標、180住所、参照628m。ポートカーリング（推定）を反映。全体900採用、残り4,454峰。Kemptville・Dharwadは引き続き保留。
