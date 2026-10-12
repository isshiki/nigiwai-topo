import unittest
import numpy as np
from scripts.global_density import density,latitude,longitude,DLAT,DLON,MAX_LAT


class GlobalDensity(unittest.TestCase):
    def test_shared_boundary_is_identical(self):
        size=32
        i,j=6250,4913
        lon=float(longitude(i*size));lat=float(latitude(j*size+16))
        points=[[lon,lat],[lon-.0003,lat+.0001],[lon+.0004,lat-.0002]]
        _,_,a=density(points,i-1,j,200,size)
        _,_,b=density(points,i,j,200,size)
        np.testing.assert_allclose(a[:,-1],b[:,0],rtol=1e-12,atol=1e-12)
        _,_,south=density(points,i,j-1,200,size)
        np.testing.assert_allclose(south[-1,:],b[0,:],rtol=1e-12,atol=1e-12)

    def test_date_line_wrap_and_metric_height(self):
        for requested in (0,51.5,80):
            size=20;j=round((requested+90)/DLAT)//size
            lat=float(latitude(j*size+10))
            _,_,z=density([[-180,lat]],0,j,200,size)
            expected=1e6/(2*np.pi*200**2)
            self.assertAlmostEqual(z[10,0]/expected,1,delta=.01)
        _,_,a=density([[179.9998,lat]],0,j,200,size)
        _,_,b=density([[-180.0002,lat]],0,j,200,size)
        np.testing.assert_allclose(a,b,rtol=1e-12)

    def test_polar_guard(self):
        with self.assertRaises(ValueError): density([],0,199,200,1000)

    def test_padding_keeps_core_density(self):
        points=[[0,51.5],[.001,51.5]]
        i,j,size=10000,7861,20
        _,_,a=density(points,i,j,200,size)
        _,_,b=density(points,i,j,200,size,padding=5)
        np.testing.assert_allclose(a,b[5:-5,5:-5],rtol=1e-12,atol=1e-12)
