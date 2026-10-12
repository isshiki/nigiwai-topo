> 履歴・調査記録：旧仕様、当時の件数、未完了事項を含みます。現在の公開仕様・完了状態は[現在の状態](current-state.md)を参照してください。

# 保留13峰：元POI住所と座標の照合

固定snapshot `2325979374271449319`（2026-09-15）の13峰近傍、計5,436個のFSQ IDを取得。前回局所監査とID集合・座標の一致を全件検証した。住所・都市名・地域・郵便番号を追加取得した。閉店判明分は対象外。

## 照合結果

元localityをGeoNames同国の集落・都市・地区の名称および別名と照合。全候補の代表点から50kmを超えて離れるものは3,470件。50km以内の候補があるものは40件。都市名未登録1,550件、名称未照合334件、国名だけの値42件。国名だけの値は都市への別名一致に使わない。

**これは誤位置の確定件数ではない。** 距離は住所の正確な緯度経度ではなく地名代表点との距離。近い候補があることも正しい住所の保証ではない。未照合・未登録を正常として扱わない。同名地の候補が一つでも近ければ遠距離の旗を立てない。住所変更、広いlocality範囲、古い別名、別支店、国コードの誤りは追加確認が必要。

|峰の緯度・経度|POI|住所あり|都市名あり|全照合候補から50km超|50km以内の候補あり|未照合・未登録|
|---|---:|---:|---:|---:|---:|---:|
|22.106, 77.185|904|902|877|876|0|28|
|39.035, 35.244|761|448|649|445|34|282|
|31.878, 53.438|431|365|245|215|0|216|
|-13.001, -54.000|436|47|50|42|0|394|
|22.106, 72.577|289|289|289|289|0|0|
|22.106, 72.565|368|368|368|368|0|0|
|-20.000, 145.000|306|304|304|291|0|15|
|-33.000, 146.000|307|299|300|292|0|15|
|39.062, 35.124|275|62|49|39|2|234|
|-14.235, -51.925|292|289|34|5|0|287|
|39.761, -98.501|435|378|414|328|4|103|
|22.106, 73.866|222|222|222|222|0|0|
|-0.788, 113.921|410|101|85|58|0|352|

## 一次資料を照合済みの施設レコード

以下は前回の施設名検索と同じFSQ IDの元住所。元データ内の住所文字列と座標の整合性、公式資料の施設所在地との対応をそれぞれ確認するための証拠であり、名前の一致だけで全レコードを除外しない。

### 22.106, 77.185 — Decon Lighting Pvt. Ltd.

FSQ ID: `03a5dfcc19a44c52576bfc63`。元住所: Y - 43, Okhla Industrial Area, Phase - Ii / locality: New Delhi / region: Delhi / country: IN。

[施設の一次資料](https://deconlighting.in/)。地名照合状態: `locality_reference_far`。

最短の照合候補: New Delhi（GeoNames 1261481）、元座標から約721.8km。

### -13.001, -54.000 — IFAL Campus PIn

FSQ ID: `4f9090c4e4b04fd33dd62bd7`。元住所: Palmeira De Fora / locality: Palmeira Dos Índios / region: AL / country: BR。

[施設の一次資料](https://www2.ifal.edu.br/campus/palmeira)。地名照合状態: `locality_reference_far`。

最短の照合候補: Palmeira dos Índios（GeoNames 3393242）、元座標から約1,937.8km。

### 22.106, 72.577 — Hcp Interior Architecture Pvt. Ltd.

FSQ ID: `07e56c1dbcdb4789dca9fa2c`。元住所: 302 Paritosh Building, Usman Pura, Naranpura Opposite Fortune Landmark Hotel / locality: Ahmedabad / region: Gujarat / country: IN。

[施設の一次資料](https://hcp.co.in/contact)。地名照合状態: `locality_reference_far`。

最短の照合候補: Ahmedabad（GeoNames 1279233）、元座標から約101.9km。

### 22.106, 72.565 — Gujarat Cancer and Research Institute (gcri)

FSQ ID: `0083cfd8cd244c59f6e5fd38`。元住所: N/A, New Civil Hospital Campus, Asarwa / locality: Ahmadabad / region: Gujarat / country: IN。

[施設の一次資料](https://gcriindia.org/contact.html)。地名照合状態: `locality_reference_far`。

最短の照合候補: Ahmedabad（GeoNames 1279233）、元座標から約101.9km。

### -20.000, 145.000 — Chatime Toowong Village

FSQ ID: `688d20c4bfffa54f8b9adc99`。元住所: 9 Sherwood Rd / locality: Toowong / region: QLD / country: AU。

[施設の一次資料](https://www.toowongvillage.com.au/stores/chatime)。地名照合状態: `locality_reference_far`。

最短の照合候補: Toowong（GeoNames 2146270）、元座標から約1,160.9km。

### -33.000, 146.000 — Teddington Legal

FSQ ID: `53b283fd498e6360c18d084f`。元住所: Suite 513, Level 5, 55 Holt Street / locality: Surry Hills / region: NSW / country: AU。

[施設の一次資料](https://teddingtonlegal.com.au/contact-us/)。地名照合状態: `locality_reference_far`。

最短の照合候補: Surry Hills（GeoNames 2147821）、元座標から約494.5km。

### 39.062, 35.124 — NEU Hospital (International Patients Department)

FSQ ID: `574be5ee498edfad327d208e`。元住所: 未登録 / locality: 未登録 / region: 未登録 / country: TR。

[施設の一次資料](https://medicine.neu.edu.tr/incoming/?lang=en)。地名照合状態: `missing_locality`。

### -14.235, -51.925 — Banco Itau Paraguay S.A.

FSQ ID: `5225f60711d22aec5796c65b`。元住所: Brasilia / locality: 未登録 / region: 未登録 / country: BR。

[施設の一次資料](https://www.itau.com.py/paginas/atencionparavos)。地名照合状態: `missing_locality`。

### 39.761, -98.501 — Harbour Grand Kowloon

FSQ ID: `58aaaaae7ff1e46c189e5d43`。元住所: California / locality: USA / region: KS / country: US。

[施設の一次資料](https://www.harbourgrand.com/kowloon/en/contact-us/)。地名照合状態: `country_only_locality`。

### -0.788, 113.921 — RS. Soedarso

FSQ ID: `4e4532e2d164821e116c2a5a`。元住所: 未登録 / locality: 未登録 / region: Indonesia / country: ID。

[施設の一次資料](https://polise.kalbarprov.go.id/layanan/73/standar-pelayanan-rawat-jalan-rsud-dr-soedarso)。地名照合状態: `missing_locality`。

## 根拠・再現・今後

- 元FSQ情報: `data/name-research/held-poi-addresses/*.parquet`（Git管理外）。同じsnapshotから住所を取得したSQLと非機密パラメータを `all.json` に保存。認証情報は保存しない。
- 全IDごとの照合: `data/name-research/held-poi-addresses/audit-detail.json`。集計と公式資料照合ID: `docs/held-peak-address-audit.json`。
- 地名参照: [GeoNames国別資料](https://download.geonames.org/export/dump/)、CC BY 4.0。歴史集落PPLH/PPLQ/PPLWは候補から除外。Unicode・大小文字・記号を正規化した完全一致だけを使い、曖昧な類似検索は使わない。
- 誤位置の候補リストは検査用に保存したが、元POI・密度・峰・順位・配信タイルは変更していない。まず具体的な事業所の住所対応を確認し、確認済みIDの除外前後を区画単位で比較する。

```powershell
.venv\Scripts\python.exe scripts/fetch_held_peak_addresses.py
.venv\Scripts\python.exe scripts/audit_held_peak_addresses.py
.venv\Scripts\python.exe -m unittest discover -s tests -p test_held_address_audit.py
```
