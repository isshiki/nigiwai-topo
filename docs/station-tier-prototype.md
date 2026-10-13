# 駅のにぎわいTier表：現在の実装

全国9,032駅の代表位置から半径800m以内の最大登録密度で評価する。全業種、Gaussian σ200m、世界共通格子、Foursquare OS Places 2026-09-15、閉店判明分除外と位置品質の計算保留は地形図と共有する。

世界の22,667参照点を計算し、日本の駅カードも地図の代表点索引も同じ結果から生成する。駅IDに名前付きの峰があるかどうかは評価条件にしない。全駅に計算値があり、「峰なし」の別枠は廃止した。

SS/S/A/B/C/Dは全国の密度分布の99/95/80/50/20パーセンタイル。絞り込みによらず全国基準を固定し、同点は分けない。地域・路線・駅名検索、全件表示、同名駅の路線補足、整数密度、電車SVG、詳細から最大密度地点へのリンクを備える。

同名・同一市区町村、全メンバー間500m以内で統合した駅の代表位置を中心とする。複数の入口の範囲を合算しない。近隣駅が同じ最大点を共有することはある。世界の地名資料は全駅の網羅を保証しない。

## 再生成

1. `node scripts/audit_shared_density_references.cjs` で参照資料を照合する。追加のGeoNames参照は `python scripts/extract_shared_geonames.py` で取得済み国別資料から補完し、監査を再実行する。
2. `python scripts/build_shared_world_density.py` で原POIを空間分割し、800m以内の最大密度を計算する。
3. `python scripts/build_shared_density_assets.py --apply` で共通索引・全国Tierデータ・CSVを生成する。
4. `python scripts/pack_station_tier_data.py` でブラウザ配信データを生成する。
5. `python scripts/make_station_tier_covers.py` で両カバーを再生成する。

旧 `match_station_tier_peaks.cjs` は過去の峰名照合方式の記録であり、現在の再生成には使わない。

[全体の共通化設計](shared-density-migration.md) / [執筆用メモ](station-tier-article-brief.md)
