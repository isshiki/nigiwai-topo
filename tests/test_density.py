import unittest
import numpy as np
from scripts.build import density, PROJECT, BBOX, surface, known_closed, osm_major_poi


class DensityTests(unittest.TestCase):
    def test_osm_excludes_street_furniture_but_retains_shops(self):
        self.assertFalse(osm_major_poi({'tags': {'amenity': 'bench'}}))
        self.assertFalse(osm_major_poi({'tags': {'amenity': 'parking_space'}}))
        self.assertTrue(osm_major_poi({'tags': {'shop': 'supermarket', 'amenity': 'parking'}}))
        self.assertTrue(osm_major_poi({'tags': {'amenity': 'restaurant'}}))
    def test_missing_status_does_not_assert_closed(self):
        self.assertFalse(known_closed({'date_closed': None}))
        self.assertTrue(known_closed({'date_closed': '2024-01-01'}))
        self.assertTrue(known_closed({'operating_status': 'permanently_closed'}))
    def test_empty_is_zero(self):
        _, _, z = density([], BBOX, 400, 100)
        self.assertEqual(float(z.sum()), 0)

    def test_integrated_density_is_one_place(self):
        _, _, z = density([{'lon': 139.74, 'lat': 35.69}], BBOX, 400, 100)
        self.assertAlmostEqual(z.sum() * .01, 1, places=6)

    def test_duplicate_doubles_density(self):
        point = {'lon': 139.74, 'lat': 35.69}
        _, _, one = density([point], BBOX, 400, 100)
        _, _, two = density([point, point], BBOX, 400, 100)
        np.testing.assert_allclose(two, one * 2)

    def test_category_excludes_other_points(self):
        geo, count = surface([{'lon': 139.74, 'lat': 35.69, 'category': 'shopping'}], 400, 'food')
        self.assertEqual(count, 0)
        self.assertFalse(any(f['properties']['kind'] == 'peak' for f in geo['features']))


if __name__ == '__main__':
    unittest.main()
