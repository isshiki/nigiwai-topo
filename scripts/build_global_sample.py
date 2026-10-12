"""Real shared-grid contour samples; kept separate from published pilot data."""
import argparse
import json
from pathlib import Path
import time
import contourpy
import numpy as np
from scipy.ndimage import maximum_filter1d
try:
    from .global_density import density,DLON,DLAT,row_metrics
    from .prepare_world import connection
    from .build import LEVELS,feature
    from .build_national import sanitize_geo
    from .fetch_world import write_json
    from .world_names import WorldNamer
except ImportError:
    from global_density import density,DLON,DLAT,row_metrics
    from prepare_world import connection
    from build import LEVELS,feature
    from build_national import sanitize_geo
    from fetch_world import write_json
    from world_names import WorldNamer


def peak_mask(z,ys):
    dx,dy=row_metrics(ys)
    maxima=np.empty_like(z)
    for r in range(len(ys)):
        width=max(3,2*int(np.ceil(400/dx[r]))+1)
        maxima[r]=maximum_filter1d(z[r],size=width)
    maxima=maximum_filter1d(maxima,size=9,axis=0)
    return (z==maxima)&(z>=50)


def surface(xs,ys,z,namer):
    contour=contourpy.contour_generator(x=xs,y=ys,z=z,fill_type='OuterOffset',line_type='Separate')
    features=[]
    for low,high in zip(LEVELS,LEVELS[1:]+[max(64000,float(z.max())+1)]):
        rings,offsets=contour.filled(low,high)
        for ring,cuts in zip(rings,offsets):
            features.append(feature('Polygon',[ring[a:b].round(6).tolist() for a,b in zip(cuts[:-1],cuts[1:])],kind='band',density=low))
    for level in LEVELS:
        for line in contour.lines(level):
            rounded=line.round(6)
            if np.any(rounded!=rounded[0]):
                features.append(feature('LineString',rounded.tolist(),kind='contour',density=level,index=level in [1000,2000,4000,8000,16000,32000]))
    for r,c in np.argwhere(peak_mask(z,ys)[:-1,:-1]):
        features.append(feature('Point',[float(xs[c]),float(ys[r])],kind='peak',density=round(float(z[r,c])),**namer(float(xs[c]),float(ys[r]))))
    geo={'type':'FeatureCollection','features':features}
    sanitize_geo(geo)
    return geo


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--region',choices=['sg-singapore','gb-london','is-reykjavik'],required=True)
    args=parser.parse_args()
    region=next(r for r in json.loads(Path('scripts/world-pilots.json').read_text(encoding='utf-8'))['regions'] if r['id']==args.region)
    lon,lat=region['center'];i=int((lon+180)/DLON)//500;j=int((lat+90)/DLAT)//500
    w,s,e,n=-180+i*500*DLON,-90+j*500*DLAT,-180+(i+1)*500*DLON,-90+(j+1)*500*DLAT
    ref=Path('data/raw/world-names')/args.region
    namer=WorldNamer(json.loads((ref/'stations.json').read_text(encoding='utf-8')),json.loads((ref/'places.json').read_text(encoding='utf-8')))
    out=Path('data/world-build/samples')/args.region
    out.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter()
    with connection() as con:
        points=np.array(con.execute('SELECT longitude,latitude FROM read_parquet(?) WHERE date_closed IS NULL AND longitude BETWEEN ? AND ? AND latitude BETWEEN ? AND ?',
            ['data/raw/foursquare-global/world-source.parquet',w-.2,e+.2,s-.04,n+.04]).fetchall())
    report={'region':args.region,'experimental':True,'i':i,'j':j,'bbox':[w,s,e,n],'input_count':len(points),'datasets':[]}
    for sigma in (200,400,800):
        xs,ys,z=density(points,i,j,sigma)
        geo=surface(xs,ys,z,namer)
        path=out/f'{sigma}-all.json'
        write_json(path,geo)
        report['datasets'].append({'sigma':sigma,'features':len(geo['features']),'peaks':sum(f['properties']['kind']=='peak' for f in geo['features']),
                                   'bytes':path.stat().st_size,'max_density':float(z.max())})
        print(args.region,sigma,report['datasets'][-1],flush=True)
    report['seconds']=round(time.perf_counter()-started,2)
    write_json(out/'manifest.json',report)


if __name__=='__main__': main()
