# 駅のにぎわいTier表のカバー

1600×900。全国共通の半径800m内の最大登録密度とTierで生成。地形図と同じ値を使用する。

- `cover-sobu.png`：総武線46駅。SS1/S9/A12/B12/C8/D4。
- `cover-osaka-chuo.png`：大阪メトロ中央線15駅。SS0/S2/A6/B6/C0/D1。
- `metadata.json`：元データSHA256、掲載駅ID、路線ID、Tierごとの件数。
- 再生成：`python scripts/make_station_tier_covers.py`。

登録の集まりを楽しむ表で、実際の人出・人気の順位ではない。地図の名前付き峰に対応しない駅も同じ条件で計算した。
