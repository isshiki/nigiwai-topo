import unittest
import numpy as np
from scripts.build_national import tile_density
from scripts.national_grid import tile_key, SIZE


class NationalGridTests(unittest.TestCase):
    def test_negative_coordinates_use_floor(self):
        self.assertEqual(tile_key(-1, -1), (-1, -1))

    def test_adjacent_chunks_share_identical_density_at_border(self):
        points = [{'x': SIZE - 100, 'y': 20000}, {'x': SIZE + 200, 'y': 20000}]
        for sigma in [200, 400, 800]:
            _, _, left, _ = tile_density(points, 0, 0, sigma)
            _, _, right, _ = tile_density(points, 1, 0, sigma)
            np.testing.assert_array_equal(left[:, -1], right[:, 0])

    def test_density_integrates_to_one_place(self):
        _, _, z, _ = tile_density([{'x': 20000, 'y': 20000}], 0, 0, 200)
        self.assertAlmostEqual(float(z.sum()) * .01, 1, places=6)


if __name__ == '__main__':
    unittest.main()
