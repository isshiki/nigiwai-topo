"""Validate completed world geometries and prepare bounded PMTiles inputs."""
from collections import defaultdict,Counter
import json
from pathlib import Path
import time
import math
import argparse
from shapely.geometry import shape,mapping,box
from shapely import make_valid
from fetch_world import write_json
from global_density import DLON,DLAT
from global_names import GlobalNamer

SOURCE=Path('data/world-build/default')
OUTPUT=Path('data/world-build/packages')


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--package-only',action='store_true',help='Reuse completed geometry validation while rebuilding package names/peaks')
    args=parser.parse_args()
    state=json.loads((SOURCE/'progress.json').read_text(encoding='utf-8'))
    if not state.get('complete'): raise ValueError('World build incomplete')
    groups=defaultdict(list)
    paths=[p for p in SOURCE.glob('*.json') if p.stem.count('-')==1 and all(s.isdigit() for s in p.stem.split('-'))]
    if len(paths)!=state['tasks']: raise ValueError('Missing world chunks')
    verified=json.loads((OUTPUT/'validation.json').read_text(encoding='utf-8')) if args.package_only else None
    if verified and (not verified['complete'] or verified['chunks']!=len(paths) or verified['bytes']!=sum(p.stat().st_size for p in paths)):
        raise ValueError('Verified source inventory changed')
    totals=Counter();started=time.perf_counter()
    for number,path in enumerate(sorted(paths),1):
        i,j=map(int,path.stem.split('-'))
        geo=json.loads(path.read_text(encoding='utf-8'))
        if geo['type']!='FeatureCollection': raise ValueError('Invalid collection')
        bounds=box(-180+i*500*DLON,-90+j*500*DLAT,-180+(i+1)*500*DLON,-90+(j+1)*500*DLAT).buffer(.000002)
        for f in geo['features']:
            if args.package_only: continue
            geometry=shape(f['geometry']);props=f['properties']
            if props['kind']=='contour' and geometry.geom_type=='LineString' and geometry.length==0:
                totals['collapsed_contours']+=1
                continue  # Coordinate rounding collapsed a sub-metre line.
            if not geometry.is_valid or geometry.is_empty or not bounds.covers(geometry):
                raise ValueError('Invalid/outside geometry: '+path.name)
            if props['kind'] not in ('band','contour','peak') or not math.isfinite(props['density']) or props['density']<0:
                raise ValueError('Invalid density/kind: '+path.name)
            totals[props['kind']]+=1
        if geo['features']: groups[(i//4,j//4)].append(path)
        if number%5000==0: print('Validated',number,'/',len(paths),flush=True)
    print('All world geometries validated; preparing packages',flush=True)
    OUTPUT.mkdir(parents=True,exist_ok=True)
    registry=[]
    namer=GlobalNamer()
    for (a,b),files in sorted(groups.items()):
        region=f'global-{a}-{b}'
        root=OUTPUT/region;root.mkdir(parents=True,exist_ok=True)
        bbox=[-180+a*2000*DLON,max(-85.05,-90+b*2000*DLAT),-180+(a+1)*2000*DLON,min(85.05,-90+(b+1)*2000*DLAT)]
        peaks=[];overview=[];chunks=[]
        for path in files:
            geo=json.loads(path.read_text(encoding='utf-8'))
            chunks.append({'file':str(path.resolve()),'bytes':path.stat().st_size,'bbox':bbox})
            repaired=Path('data/world-build/peak-repair')/path.name
            if repaired.exists():
                peaks.extend(json.loads(repaired.read_text(encoding='utf-8'))['features'])
            else:
                peaks.extend(f for f in geo['features'] if f['properties']['kind']=='peak')
            for f in geo['features']:
                if f['properties']['kind']=='band' and f['properties']['density']>=800:
                    geometry=make_valid(shape(f['geometry']).simplify(.0005,preserve_topology=True))
                    if not geometry.is_empty: overview.append({**f,'geometry':mapping(geometry)})
        if len({tuple(f['geometry']['coordinates']) for f in peaks})!=len(peaks):
            raise ValueError('Duplicate peak coordinates in '+region)
        for f in peaks:
            f['properties'].update(namer(*f['geometry']['coordinates']))
        peaks.sort(key=lambda f:-f['properties']['density'])
        write_json(root/'200-all-peaks.json',{'type':'FeatureCollection','features':peaks})
        write_json(root/'200-all-overview.json',{'type':'FeatureCollection','features':overview})
        write_json(root/'stations.json',[])
        write_json(root/'regions.json',{region:{'name':region,'bbox':bbox,'pref_codes':[]}})
        manifest={'world':True,'experimental':True,'region_id':region,'bbox':bbox,'coverage':region,
            'source':'Foursquare OS Places','snapshots':json.loads(Path('data/world-build/manifest.json').read_text(encoding='utf-8'))['snapshots'],
            'names':'N02/OSM cached stations; GeoNames nearby cities/towns','delivery':'viewport-chunks',
            'name_sources':['GeoNames CC BY 4.0','国土数値情報 N02 CC BY 4.0','OpenStreetMap ODbL'],
            'datasets':[{'sigma':200,'category':'all','status':'exclude','count':101734535,'peaks':len(peaks),
                'peaks_file':'200-all-peaks.json','overview_file':'200-all-overview.json','chunks':chunks}]}
        write_json(root/'manifest.json',manifest)
        registry.append({'id':region,'bbox':bbox,'chunks':len(chunks),'peaks':len(peaks),'input':str(root)})
    report={'complete':True,'chunks':len(paths),'nonempty_chunks':sum(len(v) for v in groups.values()),
        'bytes':sum(p.stat().st_size for p in paths),'features':verified['features'] if verified else dict(totals),'packages':len(registry),
        'seconds':round(time.perf_counter()-started,1),'peak_boundary_validation':'pending; not publication-ready'}
    write_json(OUTPUT/'registry.json',registry)
    write_json(OUTPUT/'validation.json',report)
    print(json.dumps(report),flush=True)


if __name__=='__main__': main()
