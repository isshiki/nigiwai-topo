# 出典・取得条件

公式情報再確認: 2026-10-06。以下の取得実績は検証記録に記載。取得成功は品質保証を意味しません。

同日、Foursquareを全国版の主データとして採用。東京比較版と同snapshot、JP登録・離島を含む地理範囲を抽出。取得・対象範囲・除外・全国N02参照の詳細は [全国版](national.md)。既存の3データ比較は東京版に保持しています。

- Overture Places: https://docs.overturemaps.org/guides/places/ 、取得方法 https://docs.overturemaps.org/getting-data/ 。試作対象版2026-09-23.1。CDLA Permissive 2.0 / Apache 2.0など提供元別の条件を保持。公開前に対象レコードのsourcesとライセンス・NOTICEを確認し、配布物と画面に同梱・表示する。現在は未加工原本の再配布なし。
- OpenStreetMap: https://www.openstreetmap.org/copyright 。ODbL 1.0、© OpenStreetMap contributors。2026-10-06は取得済み公開関東PBF kanto-261001.osm.pbf（515,684,430 bytes）をローカル抽出。提供元 https://download.geofabrik.de/asia/japan/kanto.html 、原本SHA-256 5e0b1bec8d8754a18db3950c6a39e4921e8c19069106a1ac038731f3d250ca83。派生データ公開時はODbL条件と機械可読データの提供方法を整備。初期のOverpass取得は504で失敗し、現在の比較には使用しません。
- 地理院タイル（淡色）: https://maps.gsi.go.jp/development/ichiran.html 。ブラウザから読み、出典を地図に表示。背景と密度データは別の出典。
- 経済センサス候補: https://www.stat.go.jp/data/mesh/pdf/r3gaiyo.pdf 。令和3年500m/1kmメッシュ。未取得・未実装。
- FSQは比較源として採用。公式Portal経由、Apache 2.0とNOTICE保持。https://docs.foursquare.com/data-products/docs/access-fsq-os-places 。Places snapshot 2325979374271449319、Categories snapshot 5006175908264532092（いずれも2026-09-15の履歴）。利用者が許可した個人用トークンをメモリ内だけで使用、接続SQL・署名付きURL・秘密値は保存しません。COUNTと一意ID一致を検査。公式NOTICE全文はdocs/licenses/Foursquare-NOTICE.txt、Apache本文はdocs/licenses/Apache-2.0.txt、画面用web/licensesには追加の加工表示を保持。
- 命名・東京都内駅の判定: 国土数値情報N02-25（CC BY 4.0、https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N02-2025.html）とN03-20260101_13（CC BY 4.0、https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html）。公開原本をrail-gap-map/data/rawから読取再利用。SHA-256と元manifestをdata/raw/names/manifest.jsonに保持。国土交通省のデータを加工したもので、国による地図ではありません。

実データ地図は現時点でローカル検証用途。公表前にOverture出典を画面へ追加し、利用条件を満たす配布用NOTICE等を用意する。


### 全国行政区域の名称補完（2026-10-06）

[国土数値情報 N03 2026年版](https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html) の全国原本を使用（2026-01-01時点、CC BY 4.0）。scripts/enrich_admin.pyで包含区域・県コード・地方と県の表示範囲を作成し、駅が遠い峰の市区町村名を補完。原本SHA-256を全国manifestに保存。画面の常時表示と出典欄に国土交通省の出典、加工、ライセンスを明示。FSQ NOTICEの加工追記は全国抽出も含む表記へ更新。

[地理院タイル公式利用案内](https://maps.gsi.go.jp/development/ichiran.html) に従い、リアルタイムで淡色地図を読み込む本アプリでは地理院タイルへの出典リンクを常時表示。透過表示・密度図重ね合わせも出典欄に記載。

### 海外試作（2026-10-06）

海外・世界版へのトークン読取利用の許可後、同じ2026-09-15 FSQ snapshotから3地域を取得した。国境で入力を切らず、地域中心の正積投影と3,750mの計算余白を使う。密度はFSQのみ、駅・都市・地区名の参照はOSM。原本のクエリ・更新時点・SHA-256、OSM IDと名前の根拠を記録。OSM参照表をODbLとして配布し、画面の常時出典とOSM-NOTICEを追加。日本のN02/N03と地理院背景は継続。[海外試作の範囲・方法・検証](world-pilots.md) / [駅・都市名の抽出](world-names.md)。
