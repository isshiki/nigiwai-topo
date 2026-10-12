"""Record operator coordinate conflict; do not invent corrected coordinates."""
import json
from pathlib import Path
from pyproj import Geod


def main():
    prior = json.loads(Path('docs/unnamed-world-batch350-review.json').read_text(encoding='utf-8'))
    rows = [x for x in prior['items'] if x['decision'] == 'hold']
    assert len(rows) == 23
    item = next(x for x in rows if x['id'] == 'GeoNames:5968869')
    audit = json.loads(Path('data/name-research/reading-sources/hagensborg-position-review.json').read_text(encoding='utf-8'))
    poi = next(x for x in audit['pois'] if x['fsq_place_id'] == '1473f3e4e4de401fe8bbd44c')
    assert poi['address'] == '2375 Saloompt River Rd'
    g = Geod(ellps='WGS84')
    operator = [52.4001397, -126.5397015]
    distance = g.inv(poi['longitude'], poi['latitude'], operator[1], operator[0])[2]
    assert 2150 < distance < 2155
    item.update(external_research_batch=351,
                reason='BaileyBridge運営者公開Wix設定で住所2375SaloomptRiverRoad/HagensborgとbusinessLocationCoordinates52.4001397,-126.5397015を取得。単なる地図中心とは異なる所在地設定だが測量済み施設座標とはしない。原1473f3e4e4de401fe8bbd44cの完全共有座標から2152.1m。RV2021ディレクトリの検索抜粋は52.40800,-126.49971で原から1554.1m、運営者設定とも異なるため未閲覧本文の座標を正解として置換しない。TSBC2024末の収集施設公開PDF第36頁はMechamSales1843Chilcotin-BellaCoolaHwy/HagensborgをPhysicalAddressとして示し、原5f20bcb75acc0b52c55369eaの番地町と対応。別の州燃料供給者PDF検索抜粋1846は未解決差として保持、誤番地・移転と断定しない。町の読みはCBCで支持済みだが13同座標の問題を残し名称・密度変更なし。',
                research_urls=['https://www.baileybridgecampsite.ca/map',
                               'https://tsbc.ca/wp-content/uploads/2025/05/8-Collection-Facilities.pdf',
                               'https://www2.gov.bc.ca/assets/gov/government/services-for-government-and-broader-public-sector/buy-goods-services-and-construction/goods-and-services-catalogue/csa-assets/vehicle-fleet-management/fuel_suppliers.pdf'],
                next_research_lead='BaileyBridge所在地設定とキャンプ案内の座標差を施設区画で照合。Mechamは運営・収集機関の地図位置を確認。原座標を推測値へ置換しない。')
    item['operator_position_check'] = dict(fsq_place_id=poi['fsq_place_id'],
                                         operator_lat_lon=operator,
                                         separation_m=round(distance, 1),
                                         coordinate_type='operator_site_businessLocationCoordinates',
                                         decision='position_conflict_pending_exact_site_confirmation')
    s = dict(prior['summary'])
    s.update(candidate_peaks_before=20, previous_holds_before=3,
             adopted_candidate_peaks=0, resolved_previous_holds=0, added_total=0,
             individually_researched_held_references=1)
    out = dict(snapshot=prior['snapshot'], summary=s,
               policy='運営者所在地設定と元POIの差を個別記録。未確定座標に置換しない。', items=rows)
    Path('docs/unnamed-world-batch351-review.json').write_text(json.dumps(out, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(s))


if __name__ == '__main__':
    main()
