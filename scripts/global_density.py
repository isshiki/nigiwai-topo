"""Experimental shared geographic lattice with latitude-aware metric kernels.

Not a Web Mercator metric grid. Longitude spacing gets finer toward the poles;
WGS84 row distances and cell areas convert the Gaussian to places/km2.
"""
import numpy as np
from pyproj import Geod
from scipy.ndimage import gaussian_filter1d

GEOD=Geod(ellps='WGS84')
LON_BINS=400000
LAT_BINS=200000
DLON=360/LON_BINS
DLAT=180/LAT_BINS
MAX_LAT=85.0511287798066


def longitude(index): return np.asarray(index)*DLON-180
def latitude(index): return np.asarray(index)*DLAT-90


def row_metrics(latitudes):
    latitudes=np.asarray(latitudes)
    zeros=np.zeros_like(latitudes)
    _,_,dx=GEOD.inv(zeros-DLON/2,latitudes,zeros+DLON/2,latitudes)
    _,_,dy=GEOD.inv(zeros,latitudes-DLAT/2,zeros,latitudes+DLAT/2)
    return dx,dy


def density(points,i,j,sigma,size=500,padding=0):
    if sigma<=0 or size<1: raise ValueError('Invalid kernel or size')
    core_x=np.arange(i*size,(i+1)*size+1)
    core_y=np.arange(j*size,(j+1)*size+1)
    if np.max(np.abs(latitude(core_y)))>MAX_LAT:
        raise ValueError('Tile exceeds supported display latitude')
    if padding<0: raise ValueError('Invalid output padding')
    core_x=np.arange(core_x[0]-padding,core_x[-1]+padding+1)
    core_y=np.arange(core_y[0]-padding,core_y[-1]+padding+1)
    # An extra five cells absorb histogram rounding and discrete filter support.
    halo_y=int(np.ceil(4*sigma/99))+5
    ys=np.arange(core_y[0]-halo_y,core_y[-1]+halo_y+1)
    lats=latitude(ys)
    dx,dy=row_metrics(lats)
    halo_x=int(np.ceil(4*sigma/dx.min()))+5
    xs=np.arange(core_x[0]-halo_x,core_x[-1]+halo_x+1)
    hist=np.zeros((len(ys),len(xs)))
    points=np.asarray(points,dtype=float).reshape(-1,2)
    if len(points):
        px=np.rint((points[:,0]+180)/DLON).astype(np.int64)%LON_BINS
        midpoint=(core_x[0]+core_x[-1])/2
        px=px+np.rint((midpoint-px)/LON_BINS).astype(np.int64)*LON_BINS
        py=np.rint((points[:,1]+90)/DLAT).astype(np.int64)
        select=(px>=xs[0])&(px<=xs[-1])&(py>=ys[0])&(py<=ys[-1])
        np.add.at(hist,(py[select]-ys[0],px[select]-xs[0]),1)
    horizontal=np.empty_like(hist)
    for r in range(len(ys)):
        horizontal[r]=gaussian_filter1d(hist[r],sigma/dx[r],mode='constant',truncate=4)/(dx[r]*dy[r])
    result=np.zeros((len(core_y),len(core_x)))
    for r,y in enumerate(core_y):
        target_lat=float(latitude(y))
        _,_,dist=GEOD.inv(np.zeros(len(lats)),lats,np.zeros(len(lats)),np.full(len(lats),target_lat))
        selected=dist<=4*sigma
        weights=np.exp(-.5*(dist[selected]/sigma)**2)*dy[selected]
        weights/=weights.sum()
        result[r]=weights@horizontal[selected,halo_x:halo_x+len(core_x)]*1e6
    return longitude(core_x),latitude(core_y),result
