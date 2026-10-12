"""Measure independent regional-grid phase error before a world mosaic."""
import json
from pathlib import Path
import numpy as np
from scipy.ndimage import gaussian_filter
from scipy.interpolate import RegularGridInterpolator
try:
    from .prepare_world import connection
    from .regional_grid import RegionalGrid
    from .fetch_world import write_json
except ImportError:
    from prepare_world import connection
    from regional_grid import RegionalGrid
    from fetch_world import write_json


def main():
    with connection() as con:
        points=np.array(con.execute('''SELECT longitude,latitude FROM read_parquet(?)
            WHERE date_closed IS NULL AND longitude BETWEEN -.19 AND -.05 AND latitude BETWEEN 51.44 AND 51.56''',
            ['data/raw/foursquare-global/world-source.parquet']).fetchall())
    samples=np.column_stack([np.full(41,-.12),np.linspace(51.47,51.53,41)])
    values={}
    for center in (-1,1):
        grid=RegionalGrid(center-.12,51.5)
        px,py=grid.project.transform(points[:,0],points[:,1])
        sx,sy=grid.project.transform(samples[:,0],samples[:,1])
        xs=np.arange(np.floor(min(sx)/100)*100-3800,np.ceil(max(sx)/100)*100+3900,100)
        ys=np.arange(np.floor(min(sy)/100)*100-3800,np.ceil(max(sy)/100)*100+3900,100)
        hist=np.histogram2d(py,px,bins=(np.r_[ys-50,ys[-1]+50],np.r_[xs-50,xs[-1]+50]))[0]
        values[center]={}
        for sigma in (200,400,800):
            density=gaussian_filter(hist,sigma/100,mode='constant',truncate=4)*100
            values[center][sigma]=RegularGridInterpolator((ys,xs),density)(np.column_stack([sy,sx]))
    report={'location':'London longitude -0.12; regional centers -1.12 and +0.88 degrees',
            'source_count':len(points),'samples':len(samples),'interpretation':'Independent local grid phase test, not a global seam solution', 'results':[]}
    for sigma in (200,400,800):
        a,b=values[-1][sigma],values[1][sigma]
        selected=(a+b)/2>=800
        percent=np.abs(a[selected]-b[selected])/((a[selected]+b[selected])/2)*100
        report['results'].append({'sigma':sigma,'above_floor_samples':int(selected.sum()),
            'mean_difference_percent':float(percent.mean()) if len(percent) else None,
            'max_difference_percent':float(percent.max()) if len(percent) else None})
    Path('data/validation').mkdir(parents=True,exist_ok=True)
    write_json(Path('data/validation/world-seams.json'),report)
    print(json.dumps(report),flush=True)


if __name__=='__main__': main()
