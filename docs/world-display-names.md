# 世界の山の表示名（2026-10-11）

山の表示名から「付近」「駅付近」を除去しました。背景地図の文字は変更しません。地名は山の参考名であり、行政区域への所属や独立商圏を意味しません。

## 日本語辞書

113,083参照名を出典ID・原名・座標・国で照合し、日本語表示を接続。登録日本語名を優先し、不足分には既存のQwen・Granite候補と編集による音写を採用しました。音写は公式の日本語地名や正しい現地発音を保証するものではありません。元名と採用根拠はポップアップで確認できます。

台湾と中国では出典IDに対応するGeoNamesの原語漢字別名を優先し、限定的な字形対応で整えています。読みから漢字は推測しません。韓国の山の名前はカタカナを使用。exact-IDの漢字・別名選択は自動処理で、全件を人が現地資料に照らして確定した意味ではありません。個別編集は `world-display-transliterations.tsv`、`world-display-name-corrections.json`、`taiwan-display-name-corrections.json` に記録。

## 重複と順位

同じ名前の参考点に複数の局所最大点が割り当てられるため、元の峰は複数存在します。元データは消さず、表示名ごとに最高密度の峰1件を地図ラベルとランキングの代表としました。別の土地の同名地には国・州・県などを付けて区別します。ランキングは現在の表示範囲・表示下限での代表峰上位20件です。都市の総登録数や人口の順位ではありません。

索引の上位100峰が同じ名前で埋まっていても、子区画まで検索して異なる名前の上位20件を取得します。

## 検証と限界

全319,885峰の表示名について、禁止接尾辞0・日本語以外の文字が残る名前0。世界・大陸・国・日本の地方と県の238範囲×表示下限3段階、計714条件で索引の順位を全件走査と比較して一致しました。密度・位置・元資料は変更していません。

当初参照地名のなかった5,356峰のうち、住所と参照位置を確認した900峰を追加しました（登録日本語名74峰・公開資料の日本語表記29峰・編集表記797峰（うち16峰は推定））。[採用根拠](unnamed-world-name-decisions.json)。残る4,454峰は、創作せず「地名未登録」と座標を表示します。すべて初期表示下限800件/km²未満です。日本語文字だけという検査は意味・発音・字形が全件正しい保証ではありません。参考名の集約によって同じ街の内部の複数ピークは代表1件になりますが、段彩・等高線は残ります。

## 再現

```powershell
.venv\Scripts\python.exe scripts/build_display_name_editorial.py
.venv\Scripts\python.exe scripts/build_world_station_labels.py
.venv\Scripts\python.exe scripts/build_world_regions.py
.venv\Scripts\python.exe scripts/build_world_display_names.py
$env:NIGIWAI_PUBLIC_WORLD='1'
$env:NIGIWAI_TEST_WORLD_FOLDER='foursquare-world-v2'
$env:NIGIWAI_STRICT_NAMES='1'
$env:NIGIWAI_VERIFY_ALL_REGIONS='1'
node tests/world_display_names_check.cjs
node tests/distinct_peak_index_check.cjs
node tests/world_area_check.cjs
node tests/peak_locality_names_check.cjs
```

生成辞書 `web/world-display-names.js`、全件検査記録 `data/validation/world-display-audit.json`。監査記録と入力キャッシュはGit除外です。GeoNames別名・州名の原資料は https://download.geonames.org/export/dump/ （CC BY 4.0）。配信用画面は `scripts/package_pages.py` で生成。GitHub Pages公開は未実施。

世界v5公開後、初期未登録コホート5,356峰は採用900・未登録4,454・修正密度で消失2。消失峰の元資料は保持し、名称採用とは区別します。

了承済みの推定表記方針により15名称に「（推定）」を常時表示。詳細根拠にも現地発音未確認を明記。原綴り・参照ID・住所確認・座標品質の留保を保存します。指定候補群203峰・69件の保留は0件ですが、世界の全未登録地名や全POI品質の解決を意味しません。

追加調査の公式施設住所照合では、2独立施設・2発行元・異なる元住所・参照ID一致を必須とし、峰から750m以内、少なくとも1施設100m以内、100件以上の支持POI・街名支持80%以上・20住所と20独立座標以上を確認。元住所変更時は生成を拒否します。個別の承認済み記録がない候補には適用せず、一般基準の一括緩和は行いません。住所照合は法的境界包含や測量精度の保証ではありません。
