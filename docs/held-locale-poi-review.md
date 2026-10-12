# 保留4参照名の周辺POI確認

4参照名に割り当てられた6峰と参照地点の各1kmを調査。重複を除く2,065件の施設名を確認し、公的資料の所在地と照合した。各峰の商圏・周辺地域を確認できた。元の曖昧な地名がこの街区の正式名だという判定ではない。

|元参照名|確認した地域|峰別の参照候補|
|---|---|---|
|Hudi|深圳市南山区・蛇口／海上世界と太子湾|海上世界周辺／太子湾・蛇口クルーズ母港周辺|
|Dalingxia|深圳市福田区・農林路と竹子林周辺|印力中心（深国投広場）周辺／竹子林・東方銀座ホテル周辺|
|Haoye|深圳市宝安区・沙井中心地区西側|沙井・京基百納広場周辺|
|Hongshulin|深圳市南山区・前海桂湾|万象前海・前海卓悦INTOWN周辺|

## 根拠

### Hudi

虎地という自然地形の参照同定は未解決だが、峰の店舗群は蛇口の実在商圏と対応する。2峰に同じ施設名を一括適用しない。

- 海上世界周辺：1km内1164件、300m内327件。代表施設：海上世界 Sea World、海上世界明华游轮 Minghua、HuangJiHuang 黄记煌, minghua ship, new seaworld、海上世界地铁站 Sea World Metro Sta.。
- 太子湾・蛇口クルーズ母港周辺：1km内150件、300m内57件。代表施設：太子灣花園、蛇口口岸 Shekou Port、蛇口邮轮母港 Shekou Cruise & Ferry Terminal、Kofu Coffee Roaster(太子湾Villa店)。
- [所在地の資料](https://qh.sz.gov.cn/en/life-in-qianhai/malls-and-places-for-leisure/content/post_10660073.html)：海上世界商圏の匯港は蛇口工業三路1号。太子湾も別項目で紹介。
- [所在地の資料](https://www.hilton.com/zh-hant/hotels/szxsshi-hilton-shenzhen-shekou-nanhai/hotel-location/)：ヒルトン蛇口南海は南山区望海路1177号、海上世界広場近隣。
- [所在地の資料](https://www.cmskchp.com/)：母港運営者の所在地は南山区海運路1号。
- 元住所欄あり：441件／周辺固有ID 1275件。

### Dalingxia

大嶺下という山の同定は未解決だが、名前が割り当てられた2峰の商業・宿泊施設群はそれぞれ別の街区として確認できる。

- 印力中心（深国投広場）周辺：1km内191件、300m内74件。代表施設：深国投广场 SCP Plaza、中影国际影城（印力中心店）、牛角（印力中心店）、gaga（印力中心店）。
- 竹子林・東方銀座ホテル周辺：1km内237件、300m内44件。代表施設：深圳东方银座酒店、Grand Mercure Oriental Ginza、如家快捷酒店_竹子林店、中国移动 （竹子林服务厅）。
- [所在地の資料](https://www.szzx.gov.cn/szzx/zwhdt/tawyh/content/post_1220865.html)：印力中心は福田区農林路69号・僑香路交差点。
- [所在地の資料](https://www.sz.gov.cn/cn/xxgk/zfxxgj/zcfg/content/post_9584291.html)：深国投広場の公的郵送先は同じ農林路69号。
- [所在地の資料](https://wtl.sz.gov.cn/ggfw/lyl/xjbgjdylb/)：東方銀座ホテルの所在地は福田区深南大道竹子林。
- 元住所欄あり：163件／周辺固有ID 376件。

### Haoye

西郷の蚝業社区という候補は採用しない。周辺の沙井店舗・施設群と公的商圏資料が対応するため、地域を沙井として確認できる。

- 沙井・京基百納広場周辺：1km内118件、300m内46件。代表施設：华润万家 Vanguard、京基.百纳广场(沙井店)、京基、沙头宾馆。
- [所在地の資料](https://jtys.sz.gov.cn/zwgk/xxgkml/ghjh/zxgh/content/post_4278186.html)：京基百納周辺は宝安区沙井街道中心区西区と記載。周辺のスーパー・病院・バス施設も記載。
- [所在地の資料](https://www.sz.gov.cn/cn/xxgk/zfxxgj/gqdt/content/mpost_12131470.html)：沙井街道と沙井京基百納広場の活動を確認。
- 元住所欄あり：64件／周辺固有ID 156件。

### Hongshulin

福田の紅樹林保護区を参照する根拠はない。POI群は万象前海と隣接施設で、前海桂湾の商圏と確認できる。

- 万象前海・前海卓悦INTOWN周辺：1km内216件、300m内76件。代表施設：朴里(万象前海店)、鲜潭蒸汽石锅鱼(万象前海店)、清莱湾 CHIN RAI(万象前海店)、SCIA Tower。
- [所在地の資料](https://qh.sz.gov.cn/en/life-in-qianhai/malls-and-places-for-leisure/content/post_10660073.html)：万象前海は前海桂湾・桂湾四路169号、前海卓悦INTOWNは夢海大道5033号。
- 元住所欄あり：112件／周辺固有ID 258件。

## 住所欄と限界

同じFSQ snapshotの住所欄を取得し、2,065件全てのIDと原座標をローカル原本と一致検証。住所のある数とlocality内訳、代表ID・住所・峰からの距離はJSONに保存。

峰から施設までの距離は元FSQ座標に対するWGS84測地距離で、位置精度の保証ではない。公的住所・商圏資料と複数の店舗名が対応するため地域同定の根拠とした。個々の全店舗の誤位置・重複を検査したわけではない。曖昧な近隣地名だけを理由にPOIや密度面を削除する根拠は得られなかった。画面の名称は、6峰それぞれの原座標と参照IDを照合して確認済み商圏・施設名へ変更。元地名はポップアップに残す。

[ID・原座標・住所欄・判定記録](held-locale-poi-review.json)。再現：`scripts/research_held_locale_pois.py` → `scripts/report_held_locale_pois.py`。取得記録はGit除外の `data/name-research/held-locale-pois/`。
