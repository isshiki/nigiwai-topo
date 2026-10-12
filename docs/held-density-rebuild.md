> 履歴・調査記録：旧仕様、当時の件数、未完了事項を含みます。現在の公開仕様・完了状態は[現在の状態](current-state.md)を参照してください。

# 保留13峰の密度・地形修正（2026-10-10）

13峰の名称を隠すだけでは疑わしい山が残るため、個別に調査した集中群の5,436件を位置品質による計算保留とし、密度・段彩・等高線・3D用形状を再生成した。原本は保存し、移動・削除していない。

**全件の誤位置が確定したという意味ではない。** 住所不足で正常な位置の登録が含まれる可能性もある。遠距離の都市名不整合候補3,470件だけでは5峰が残ったため、集中座標・多様な遠方住所・欠損・国の参照座標への近接を合わせた13群の編集上の品質保留に進んだ。世界中の住所欠損や同一座標を一律に除外する規則ではない。

元localityに一致する参照地点が2.5km以内の登録は、この13群では見つからなかった。ただし同名地点の未収録や、施設と地区参照点の距離はあり得る。この検査だけで位置の正誤を完全に証明したものではない。

## 結果

全13地点の頂の密度は100件/km²未満となり、半径2km内にも表示下限800以上の峰は残らない。周辺の残る登録は維持し、Pune周辺等には800未満の地形が残る。地点別の修正前後の値は [再生成結果JSON](held-density-rebuild.json) に保存。

世界の暫定峰数は319,897から319,885へ12減少。元の13峰の消失と、再計算による他の局所最大点の変化を合わせた差分であり、13件の単純減算ではない。計算入力は101,734,535件から101,729,099件になる。

## 限定更新と検証

- 同じ2026-09-15 snapshot、共通格子、σ200m、計算余白を維持。対象IDと原座標が原本に一致することを全件確認。
- 13区画、12パッケージを再生成。残り2,935パッケージは旧archiveをコピーし、SHA256一致を検査。
- 全比較格子で除外後の密度が増えないこと、変化した格子が保留POIのカーネル支持範囲（丸め込みで最大1.3km）内であることを検証。
- 元区画の峰の密度を再現。峰の再判定には区画外64セルを含め、端だけで局所最大を判定しない。
- 配信用MVTを実際に展開し、元13地点の詳細段彩と概観で高密度の山が消えたことを確認。
- 別ディレクトリとS3の別prefixに作成し旧版を保持。GitHub Pagesは公開しない。

## 再現手順

```powershell
.venv\Scripts\python.exe scripts/held_density_policy.py
.venv\Scripts\python.exe scripts/rebuild_held_density.py
.venv\Scripts\python.exe scripts/assemble_world.py --root data/distribution/foursquare-world-v2 --database data/world-build/quality-v2/overview.sqlite
.venv\Scripts\python.exe scripts/validate_held_density_release.py
.venv\Scripts\python.exe scripts/validate_world_frontend.py --root data/distribution/foursquare-world-v2 --report data/validation/world-v2-frontend.json
$env:NIGIWAI_TEST_WORLD_FOLDER='foursquare-world-v2'
node tests/world_area_check.cjs
.venv\Scripts\python.exe -m unittest discover -s tests -p 'test_held_density_policy.py'
```

元ID・原座標・住所検査の分類は [計算保留ポリシー](held-density-exclusions.json)。解除はIDごとに正しい位置根拠を確認してポリシーを改め、新しい版として再生成する。元住所の一次資料は [表示判断](held-peak-display-decisions.md)、その前の感度分析は [除外比較](held-peak-exclusion-impact.md) に保存。

## 配信状況

世界v2のS3配信は完了。7,052ファイル・394,293,518 bytesの全キーとサイズを照合し、CloudFrontのmanifest・峰索引・PMTiles Range（206）・CORSを検証した。画面は `https://re.masahiko.info/nigiwai-topo/world/2026-09-15-v2/` へ切替済み。旧S3版は保存、GitHub Pagesは未公開。検証記録は `data/validation/world-v2-published.json`。Pages用配布パッケージも接続先を同期する。

```powershell
aws login --profile nigiwai-topo
.venv\Scripts\python.exe scripts/publish_world.py --root data/distribution/foursquare-world-v2 --stage data/world-release-v2 --prefix nigiwai-topo/world/2026-09-15-v2/ --frontend-report data/validation/world-v2-frontend.json --report data/validation/world-v2-published.json
```

上記は再配信時のコマンド。今回の配信と接続先切替は完了。

## 世界v3の追加再生成（2026-10-12、地形検証完了）
SmeatonのSt John Bosco Camp1件を個別の運営者所在地根拠で計算保留に追加。旧13群5,436件の規則は維持し、新規則は計5,437件。`docs/held-density-exclusions-v3.json`にID・原座標・根拠を保存。`scripts/rebuild_held_density_v3.py`で別出力`data/distribution/foursquare-world-v3`へ14区画の再生成とPMTiles作成が完了。計算入力101,729,098件、峰319,884件。全世界の概観タイルと319,884峰・4,095ノードの索引組立も完了。13パッケージを再生成。2,934パッケージのSHA256一致、686変更タイルの展開検査、元13地点の地形確認、全319,884索引葉の集計とSmeaton半径1kmの峰0を検証済み。概観3,604タイルも整合。表示名871峰の対応をv3に照合済み。日本語表示の地域別検査は別ログに記録。世界v2の配信・原本・旧規則は保持。生成・地形検証は完了したが、配信切替は未実施。名称審査残数は配信変更時まで旧版の23峰・6件を維持。v3では未登録峰は4,483件、v2の4,484件との差1は名前追加ではなく密度再計算による峰消失。

世界v3配信はAWSセッション期限切れにより未実施（2026-10-12確認）。S3書込み前の本人確認で停止。`aws login --profile nigiwai-topo`後に新prefixへ配信し、CloudFront/Range/CORSを検証する。第314回の残数更新スクリプトは配信検証記録がなければ動かないよう準備済みで、まだ実行していない。

第317回の名称追加により現行辞書は872峰。v3の872峰対応と全319,884峰・238地域×3表示下限の714検査が完了。未登録4,483峰、外国語名・禁止接尾辞・高密度未登録はいずれも0。旧871峰時点の検証ログは履歴として保持。

## 選択データ版に対応する名称集計の修正
`build_unnamed_world_names.py`の固定5,356引算を、原審査対象と選択版に実在する峰の照合へ変更。採用・未登録・選択版から消失を別集計し、採用済みの欠落、重複キー、座標不整合を拒否する。v3で採用872・未登録4,483・消失1（Smeaton）を実データ全パッケージで確認、検証記録は`data/validation/world-v3-name-cohort-accounting.json`。実行後は現行v2の採用872・未登録4,484・消失0へ生成メタデータを戻す。AWS認証の再確認はセッション期限切れ、配信変更なし。

第322回のEwen追加後、名称辞書873峰をv3にも照合。v2の未登録4,483、v3の未登録4,482、差1はSmeatonの密度再計算。v2の全319,885峰・238地域×3下限714検査が完了。v3の全域表示検査は872峰時点の記録を保持し、873峰の対応は別の原審査対象集計検査で確認。


### v4：Sapezalの4公共施設を追加保留

除外方針は5441件・15群。影響15区画・14パッケージのローカル生成は完了し、変更外2933パッケージはコピーを保持している。全世界の概観・索引組立はセッション46661で実行中（data/validation/world-v4-assembly.log）。変更外ファイルSHA照合・319883峰の索引確認・Smeaton/Sapezal対象峰不在の検証は組立完了後に実行する。現段階で検証済み・公開済みとは扱わない。v3のみの未実行退役処理にあった残数4481→4480の検査不整合は修正したが、処理は実行していない。


v4全体検証完了：data/validation/held-density-release-v4.json、world-v4-frontend.json、world-v4-display-address875-test.log。319883峰、Sapezal/Smeaton対象峰0、変更外2933パッケージSHA一致、875承認存続。未登録4479はv4内の件数であり配信中v2の4481と区別。S3公開と画面切替は未実施。
