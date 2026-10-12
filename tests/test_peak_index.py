import random
import unittest
from scripts.build_peak_index import build_index, query_index


class PeakIndexTests(unittest.TestCase):
    def test_viewport_ranking_matches_full_scan_at_boundaries_and_floors(self):
        rng = random.Random(42)
        features = [{'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [rng.uniform(-2, 2), rng.uniform(-2, 2)]},
                     'properties': {'kind': 'peak', 'density': i+1}} for i in range(1200)]
        index = build_index(features, leaf_size=20)
        for bbox in [[-3,-3,3,3], [-.1,-2,.7,1], [0,0,0,0], [-2,-2,0,2]]:
            for floor in [0,800,1195]:
                expected = sorted([f for f in features if bbox[0] <= f['geometry']['coordinates'][0] <= bbox[2]
                    and bbox[1] <= f['geometry']['coordinates'][1] <= bbox[3] and f['properties']['density'] >= floor],
                    key=lambda f: -f['properties']['density'])[:20]
                self.assertEqual(query_index(index, bbox, floor=floor), expected)

    def test_identical_locations_preserve_all_records_and_empty_input(self):
        features = [{'geometry': {'coordinates': [1,1]}, 'properties': {'density': i}} for i in range(500)]
        index = build_index(features, leaf_size=10)
        self.assertEqual(len(query_index(index, [0,0,2,2], floor=0)), 20)
        self.assertEqual(query_index(build_index([]), [0,0,2,2]), [])
