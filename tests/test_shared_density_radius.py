import unittest
import numpy as np
from scripts.build_station_radius_density import maximum_at_station
from scripts.global_density import density, DLON, DLAT, GEOD


class SharedDensityRadiusTests(unittest.TestCase):
    def test_station_name_does_not_change_measurement(self):
        xy = np.array([[139.75, 35.70], [139.751, 35.701]])
        a = maximum_at_station(xy, {'lon': 139.75, 'lat': 35.70, 'name': 'A'})
        b = maximum_at_station(xy, {'lon': 139.75, 'lat': 35.70, 'name': 'B'})
        self.assertEqual(a, b)

    def test_same_surface_and_radius_in_tokyo_and_high_latitudes(self):
        for lon, lat in [(139.75, 35.70), (18.95, 69.65), (-179.999, 40)]:
            with self.subTest(lat=lat):
                xy = np.array([[lon, lat], [lon + .004, lat + .002]])
                station = {'lon': lon, 'lat': lat}
                result = maximum_at_station(xy, station)
                ix, iy = int(np.rint((lon + 180) / DLON)), int(np.rint((lat + 90) / DLAT))
                xs, ys, grid = density(xy, ix, iy, 200, size=1, padding=80)
                xx, yy = np.meshgrid(xs, ys)
                distances = np.array(GEOD.inv(np.full(xx.size, lon), np.full(xx.size, lat), xx.ravel(), yy.ravel())[2]).reshape(grid.shape)
                self.assertEqual(result['density'], round(float(grid[distances <= 800].max())))
                self.assertLessEqual(result['distance_m'], 800)

    def test_no_registered_points_is_computed_zero(self):
        result = maximum_at_station(np.empty((0, 2)), {'lon': 139, 'lat': 35})
        self.assertEqual(result['density'], 0)
        self.assertGreater(result['tested_cells'], 0)


if __name__ == '__main__':
    unittest.main()
