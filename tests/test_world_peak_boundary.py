import unittest
import numpy as np
from scripts.build_global_sample import peak_mask


class PeakBoundary(unittest.TestCase):
    def test_outside_higher_density_removes_false_edge_peak(self):
        yy,xx=np.mgrid[0:81,0:81]
        z=100*np.exp(-((xx-35)**2+(yy-50)**2)/200)
        ys=51.5+np.arange(81)*.0009
        local=peak_mask(z[40:81,40:81],ys[40:81])
        global_mask=peak_mask(z,ys)[40:81,40:81]
        self.assertTrue(local[10,0])
        self.assertFalse(global_mask[10,0])
