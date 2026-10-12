# にぎわいの地形図【世界版】

お店と施設の登録密度を、山に見立てた地図です。

**公開サイト:** https://isshiki.github.io/nigiwai-topo/
**地図の見方:** https://isshiki.github.io/nigiwai-topo/about.html

Foursquare OS Placesの登録情報に基づく、街の姿を眺めて楽しむ地図です。人出・売上・実際の標高を示すものではありません。施設の位置や営業状況、地名の日本語表記の正確さを保証しません。

商圏を調べる入口として店舗・施設の集積を眺められます。商圏の境界・購買力・売上を判定するものではなく、他の資料との併用が必要です。

## 使い方

地域を選び、地図を移動・拡大して密度の山を探せます。表示中の地名トップ20、3D、名前検索、現在地に対応。山を押すと密度を表示し、Googleマップや経路検索へ移動できます。スマホでは操作パネルをタイトルから開閉できます。

名前検索は表示中の山名を対象とします。世界の任意の都市名を探す検索ではありません。

表示条件は全業種・ならす広さ200m・800件/km²以上に固定しています。200mは平滑化の標準偏差で、半径200m以内だけを数える方式ではありません。背景文字は元の地図の表記です。極域までの完全網羅ではありません。

## 公開構成

GitHub Pagesは `web/` の画面・辞書・ライセンスを配信します。地図データは非公開S3とCloudFrontからPMTiles・分割JSONで読みます。Pythonやデータ取得の認証情報を公開サイトに置く必要はありません。

`main`へのプッシュで[公開ワークフロー](.github/workflows/pages.yml)が画面をパッケージし、検証してデプロイします。地図データの再取得・再計算は行いません。[公開・更新手順](docs/github-pages.md)。

## ローカル確認

Python 3.14とuvを使います。計算し直す場合の依存は `uv.lock` に固定しています。公開済みデータを使って画面だけ確認するなら、Python標準ライブラリで起動できます。

```powershell
python scripts/serve.py --port 8820
```

http://127.0.0.1:8820/ を開きます。MapLibre、背景タイル、CloudFrontへのネット接続が必要です。

```powershell
python scripts/package_pages.py --data-url https://re.masahiko.info/nigiwai-topo/japan/2026-09-15-v2/ --config web/config.js
python scripts/validate_site.py --root data/site
```

## 文書の入口

[現在の仕様・検証](docs/current-state.md)／[計算方法](docs/method.md)／[記事の執筆用メモ](docs/blog-draft.md)。過去の試作・調査記録は現行仕様とは区別してください。

## データと再現

Foursquare OS Places 2026-09-15を使用。[出典・取得方針](docs/data-sources.md)、[世界の取得・生成・配信](docs/world-delivery.md)、[日本の試作・配信](docs/pmtiles-deployment.md)。認証情報は `.env` に保存し、コミットしません。原本・キャッシュ・生成データ・仮想環境はGit管理外です。

最新の配信データは世界v6。計算入力101,729,089件・峰319,883個。位置品質保留5,446件は原本を残して計算から除いています。全件の誤りを断定するものではありません。[位置品質判断](docs/held-density-exclusions-v6.json)。

固定表示条件の名称未登録は0件です。表示対象外4,431峰の追加名称調査はユーザー判断で終了しました。これは全件の読みや位置品質を保証する意味ではありません。[名称の方針](docs/world-name-quality-plan.md)、[調査状態](docs/unnamed-world-investigation-status.json)。

## 出典と記録

画面には背景・POIの出典を常時表示し、[ライセンスとNOTICE](web/licenses/)を配布します。[利用者向け説明](web/about.html)。

過去の進捗は[開発記録](docs/development-history.md)へまとめています。そこには旧版・当時の未完了事項も含まれます。突出度による独立峰の判定、経済センサスとの比較、ならす広さによる世界順位の感度比較は未実施です。

世界の登録密度CSVをGitHubから配布：[全峰23,187地点](https://github.com/isshiki/nigiwai-topo/raw/refs/heads/main/exports/world-2026-09-15/world-peaks.csv)／[地名ごとの代表14,563地点](https://github.com/isshiki/nigiwai-topo/raw/refs/heads/main/exports/world-2026-09-15/world-place-representatives.csv)。[列・条件・出典](exports/world-2026-09-15/README.md)。区域内のPOI登録件数の集計は別機能で未実装。
