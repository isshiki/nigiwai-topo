# GitHub Pages公開・更新

2026-10-12に公開成功。公開ページの地名・ランキング、About、静的ファイルと地図manifestのHTTP応答を確認済み。

公開URL: https://isshiki.github.io/nigiwai-topo/

公開対象は`web/`からパッケージした`data/site/`のみ。S3の世界v6は既存のCloudFront URLを使い、GitHubリポジトリへ地図アーカイブ・原本・認証情報を入れない。

リポジトリのPages設定はGitHub Actions。mainへコミット/プッシュすると.github/workflows/pages.ymlがPython標準ライブラリでパッケージ、ローカルリンクと設定を検証して公開する。ActionsへのAWS資格情報や個人トークンの登録は不要。

公開成功後はトップページ、About、ランキング、Googleマップリンク、スマホの開閉とロード表示を確認する。MapLibre/PMTilesはCDN、地図・ランキングはCloudFront、背景はOSMタイルから取得するため、ネット接続が必要。

画面の変更はweb/、配信データの版を変更するときは公開/Range/CORS検証後にweb/config.jsのworld.dataBaseを更新する。データ自体の取得・配信はdocs/world-delivery.mdを参照。

## ローカルの公開物検証

```powershell
python scripts/package_pages.py --data-url https://re.masahiko.info/nigiwai-topo/japan/2026-09-15-v2/ --config web/config.js
python scripts/validate_site.py --root data/site
```

`--config`指定時はそのファイルが接続先を決める。上の`--data-url`は必須引数だが設定を上書きせず、実際の世界接続先はweb/config.jsの世界v6。

[現在の仕様・検証](current-state.md)。
