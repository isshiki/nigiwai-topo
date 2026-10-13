"""Validate station completeness, accounting, and fixed nationwide Tier decisions."""
import json
import math
import unittest
from pathlib import Path
from scripts.build_station_tiers import merge_same_name_stations


class StationTierDataTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(Path('web/station-tier-data.json').read_text(encoding='utf-8'))
        cls.reference = json.loads(Path('data/distribution/foursquare-japan/stations.json').read_text(encoding='utf-8'))

    def test_complete_station_ids_and_routes(self):
        rows = self.data['stations']
        self.assertEqual(len({s['id'] for s in rows}), len(rows))
        members = [source_id for s in rows for source_id in s['source_station_ids']]
        self.assertEqual(len(members), len(set(members)))
        self.assertEqual(set(members), {s['id'] for s in self.reference})
        for s in rows:
            self.assertTrue(s['lines'])
            self.assertTrue(s['municipality'])
            self.assertTrue(s['prefecture'])

    def test_ikebukuro_is_one_card_with_all_routes(self):
        rows = [s for s in self.data['stations'] if s['name'] == '池袋' and s['pref_code'] == '13']
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(rows[0]['source_station_ids']), 2)
        self.assertEqual(len(rows[0]['lines']), 7)

    def test_merge_preserves_far_same_names_and_does_not_chain(self):
        def station(i, lon, name='同名'):
            return {'id': str(i), 'name': name, 'pref_code': '13', 'municipality': '試験区', 'lon': lon, 'lat': 35, 'lines': [{'id': str(i)}]}
        original = [station(1, 139), station(2, 139.004), station(3, 139.008), station(4, 140), station(5, 139, '異名')]
        merged, owners = merge_same_name_stations(original)
        self.assertEqual(len(merged), 4)
        self.assertEqual(owners[0], owners[1])
        self.assertNotEqual(owners[0], owners[2])
        self.assertNotEqual(owners[0], owners[3])
        self.assertNotEqual(owners[0], owners[4])

    def test_map_density_and_unmatched_accounting(self):
        d = self.data
        self.assertEqual(d['metric'], 'map_peak_density')
        self.assertEqual(d['matched_count'] + d['unmatched_count'], len(d['stations']))
        for s in d['stations']:
            if s['score'] is None:
                self.assertIsNone(s['tier'])
                self.assertIsNone(s['peak'])
            else:
                self.assertTrue(math.isfinite(s['score']))
                self.assertEqual(s['score'], s['peak']['density'])
                self.assertIn(s['peak']['reference_station_id'], s['source_station_ids'])
        ikebukuro = next(s for s in d['stations'] if s['name'] == '池袋' and s['pref_code'] == '13')
        self.assertEqual(ikebukuro['score'], 15952)

    def test_tiers_are_nationwide_and_filter_invariant(self):
        for s in self.data['stations']:
            expected = None if s['score'] is None else next((t for t, cutoff in self.data['thresholds'].items() if s['score'] >= cutoff), 'D')
            self.assertEqual(s['tier'], expected)
        tokyo = [s for s in self.data['stations'] if s['pref_code'] == '13']
        nerima = [s for s in tokyo if s['municipality'] == '練馬区']
        self.assertTrue(nerima)
        national = {s['id']: s['tier'] for s in self.data['stations']}
        self.assertTrue(all(s['tier'] == national[s['id']] for s in nerima))

    def test_density_matches_published_map_csv(self):
        import csv
        with Path('exports/world-2026-09-15/world-peaks.csv').open(encoding='utf-8-sig', newline='') as stream:
            published = {(float(r['経度']), float(r['緯度'])): float(r['登録密度_件_per_km2']) for r in csv.DictReader(stream)}
        for s in self.data['stations']:
            if s['score'] is not None and s['score'] >= 800:
                peak = s['peak']
                self.assertEqual(s['score'], published[(peak['lon'], peak['lat'])])


if __name__ == '__main__':
    unittest.main()
