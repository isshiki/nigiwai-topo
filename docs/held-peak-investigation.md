> 履歴・調査記録：旧仕様、当時の件数、未完了事項を含みます。現在の公開仕様・完了状態は[現在の状態](current-state.md)を参照してください。

# 保留18峰の追加調査（2026-10-10）

18峰すべてを再調査し、5峰に参照名を追加、13峰を位置品質の確認待ちとした。元の60峰では47峰を命名・13峰を保留。密度・地形・順位は変更していない。

GeoNames国別資料の全地物種別を15km以内で照会。命名に採用する参照点は従来どおり2.5km以内。大学・鉱山キャンプは公式資料と近隣POI名称も照合し、必要に応じて公開OSMの限定照会を使った。範囲の中心は参照点であり、敷地・行政界への包含判定ではない。

## 名前を補えた5峰

|峰の緯度・経度|表示名|参照点との距離|根拠|
|---|---|---:|---|
|24.854, 46.719|ヌーラ王女大学付近|1,045m|[参照資料](https://download.geonames.org/export/dump/SA.zip)・[公式照合](https://pnu.edu.sa/en/Pages/Contact-US.aspx)|
|26.146, 50.092|ムハンマド・ビン・ファハド王子大学付近|46m|[参照資料](https://www.pmu.edu.sa/about/contact_us)|
|19.031, 99.890|パヤオ大学付近|361m|[参照資料](https://www.openstreetmap.org/way/579088013)・[公式照合](https://www.up.ac.th/contact.aspx)|
|28.649, 48.369|アン・ナーミ付近|1,089m|[参照資料](https://download.geonames.org/export/dump/KW.zip)|
|-4.109, 137.101|リッジ・キャンプ付近|288m|[参照資料](https://www.openstreetmap.org/way/505668631)・[公式照合](https://ptfi.co.id/id/news/detail/resmi-dibuka-mess-hall-kenanga-megah-di-super-block-ridge-camp)|

クウェートの峰は前回、最寄りの遠い地名に基づいてSAファイルだけを検査し0件だった。今回はKWも調べ587件を確認。国境で「最寄り地名の国＝POIの国」と仮定すると取りこぼす例だった。

パヤオ大学の公式ページにある地図の表示中心は峰から約3.8km離れるため、その中心だけを根拠に採用していない。大学公式名称・住所とOSM wayの大学名・website・電話番号を照合し、近傍の参照点を採用した。リッジ・キャンプも近い実在山・登山キャンプの名称へ置き換えず、OSMのRidge Campと運営主体PT Freeportの施設説明を照合した。

## 位置品質の確認待ち13峰

10峰で一次資料の名称・所在地との比較が得られ、3峰は局所データからの疑いにとどまる。一次資料で施設名が見つかっても、FSQの元住所・履歴・個別支店の対応を確認できていないため、全POIの誤位置確定数や世界全体の誤り率として扱わない。

### 22.106, 77.185

企業公式サイトはDelhiで設立と説明。対象点はDelhiから大きく南に離れる。個別店舗の住所・同一性は未確定。

[照合した一次資料](https://deconlighting.in/)。対象FSQ ID: `03a5dfcc19a44c52576bfc63`。

### 39.035, 35.244

761件中723件が同一座標。POI名には離れた道路・個人名等が混在。一次資料での施設同一性は未確定。

### 31.878, 53.438

431件中412件が同一座標。名称にはTabriz・Azerbaijanへの言及があるが、個別住所の一次照合は未完了。

### -13.001, -54.000

IFALの公式キャンパス資料はPalmeira dos Índios（Alagoas）。対象点は同州から離れる。PInの略称対応は推定。

[照合した一次資料](https://www2.ifal.edu.br/campus/palmeira)。対象FSQ ID: `4f9090c4e4b04fd33dd62bd7`。

### 22.106, 72.577

HCPの公式事務所はAhmedabad、Pune、Chennai。対象点はこれらから離れる。会社名称の対応は有力だがFSQ住所照合待ち。

[照合した一次資料](https://hcp.co.in/contact)。対象FSQ ID: `07e56c1dbcdb4789dca9fa2c`。

### 22.106, 72.565

公式住所はCivil Hospital Campus, Asarwa, Ahmedabad。対象点はAhmedabadから大きく南に離れる。

[照合した一次資料](https://gcriindia.org/contact.html)。対象FSQ ID: `0083cfd8cd244c59f6e5fd38`。

### -20.000, 145.000

施設公式サイトは9 Sherwood Road, Toowong, QLD 4066。RSEA Safety Gladstoneも公式住所55 Hanson Rd, Gladstoneと別途照合。両都市とも対象点から離れる。

[照合した一次資料](https://www.toowongvillage.com.au/stores/chatime)。対象FSQ ID: `688d20c4bfffa54f8b9adc99`。

### -33.000, 146.000

公式所在地はHaymarket NSW 2000等。対象点はHaymarketから離れる。分散型法律事務所のため全サービスの位置を代表するかは別途確認。

[照合した一次資料](https://teddingtonlegal.com.au/contact-us/)。対象FSQ ID: `53b283fd498e6360c18d084f`。

### 39.062, 35.124

公式サイトはNear East University Campus in Nicosia。対象点はNicosiaから離れる。275件中85件の同一座標集中もあり、単なる参照名不足から位置品質確認へ分類変更。

[照合した一次資料](https://medicine.neu.edu.tr/incoming/?lang=en)。対象FSQ ID: `574be5ee498edfad327d208e`。

### -14.235, -51.925

公式本店はOliva esquina Chile, Asunción。ブラジル中央の対象点に対し国・都市が一致しない。個別支店は特定していない。

[照合した一次資料](https://www.itau.com.py/paginas/atencionparavos)。対象FSQ ID: `5225f60711d22aec5796c65b`。

### 39.761, -98.501

ホテル公式住所は20 Tak Fung Street, Hunghom, Kowloon（香港）。Kansasの対象点と国が一致しない。

[照合した一次資料](https://www.harbourgrand.com/kowloon/en/contact-us/)。対象FSQ ID: `58aaaaae7ff1e46c189e5d43`。

### 22.106, 73.866

222件中82件が同一座標。別のインド3峰と緯度22.1058が共通。Puneを示唆する名称があるが一次資料で個別住所を確定できていない。

### -0.788, 113.921

州政府の病院サービス資料はPontianak。対象点はPontianakから東へ離れる。病院の同一性は名称照合による。

[照合した一次資料](https://polise.kalbarprov.go.id/layanan/73/standar-pelayanan-rawat-jalan-rsud-dr-soedarso)。対象FSQ ID: `4e4532e2d164821e116c2a5a`。

## 残る確認と修正方針

1. 13峰の元FSQ住所・locality・履歴を固定snapshotから追加取得し、名前だけの照合をIDごとの住所照合へ進める。現在のローカルParquetには住所が含まれない。
2. 誤位置と確認できた個別IDと、疑いのある代表座標・微小な散らばりを区別した除外候補リストを作る。同一座標だけで除外しない。
3. 除外前後のPOI件数・峰数・順位を対象区画で比較し、変更の影響と根拠を記録してからタイルを再生成する。現段階では位置を推測で修正しない。

詳細: `held-peak-investigation.json`。再現: `research_held_peak_features.py` → `research_held_osm.py`（ネットワーク）→ `build_held_peak_investigation.py` → `build_coordinate_name_review.py`。公式大学地図リンクは `data/name-research/held-official-map-links.json` に保存。公開資料の照合日は2026-10-10、FSQは2026-09-15 snapshot。住所変更・閉鎖・移転の時間差にも注意する。
