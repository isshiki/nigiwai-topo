import unittest
from pyproj import Geod
from scripts.regional_grid import RegionalGrid


class RegionalGridTests(unittest.TestCase):
    def test_roundtrip_and_local_metre_scale_at_different_latitudes(self):
        geod = Geod(ellps='WGS84')
        for lon, lat in [(103.82, 1.35), (-0.12, 51.5), (-21.9, 64.13)]:
            grid = RegionalGrid(lon, lat)
            x, y = grid.project.transform(lon, lat)
            self.assertAlmostEqual(x, 0, places=5)
            self.assertAlmostEqual(y, 0, places=5)
            lon2, lat2 = grid.inverse.transform(1000, 0)
            self.assertAlmostEqual(geod.inv(lon, lat, lon2, lat2)[2], 1000, delta=.01)
            xx, yy = grid.project.transform(lon2, lat2)
            self.assertAlmostEqual(xx, 1000, places=5)
            self.assertAlmostEqual(yy, 0, places=5)

    def test_date_line_envelope_is_split_instead_of_covering_world(self):
        bounds = RegionalGrid(179.9, 0).tile_bounds(0, 0)
        self.assertEqual(len(bounds), 2)
        for west, south, east, north in bounds:
            self.assertLess(east-west, 1)
            self.assertTrue(-180 <= west <= east <= 180)
        self.assertEqual(bounds[0][2], 180)
        self.assertEqual(bounds[1][0], -180)

    def test_negative_grid_coordinates_and_rejected_polar_center(self):
        self.assertEqual(RegionalGrid(0, 0).tile_key(-1, -1), (-1, -1))
        with self.assertRaises(ValueError):
            RegionalGrid(0, 90)
