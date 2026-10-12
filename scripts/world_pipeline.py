"""Bounded world pilots: equal-area density, halo inputs, clipped outputs."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time

from shapely.geometry import box, shape, mapping
try:
    from .build_national import surface, sanitize_geo, compact_write
    from .regional_grid import RegionalGrid
    from .world_names import WorldNamer
except ImportError:
    from build_national import surface, sanitize_geo, compact_write
    from regional_grid import RegionalGrid
    from world_names import WorldNamer


def region_config(region_id):
    region = next(r for r in json.loads(Path('scripts/world-pilots.json').read_text(encoding='utf-8'))['regions'] if r['id'] == region_id)
    w,s,e,n = region['bbox']
    if not (-180 <= w < e <= 180 and -80 <= s < n <= 80):
        raise ValueError('Pilot must be a non-wrapping bbox within supported latitudes')
    grid = RegionalGrid(*region['center'])
    bounds = projected_bounds(grid,region['bbox'])
    if bounds[2]-bounds[0] > 250000 or bounds[3]-bounds[1] > 250000:
        raise ValueError('Pilot exceeds 250km; subdivide before using this bounded prototype')
    return region


def projected_bounds(grid, bbox):
    west,south,east,north = bbox
    coords = []
    for n in range(41):
        t = n/40
        coords += [grid.project.transform(west+t*(east-west),lat) for lat in (south,north)]
        coords += [grid.project.transform(lon,south+t*(north-south)) for lon in (west,east)]
    return [min(c[0] for c in coords),min(c[1] for c in coords),max(c[0] for c in coords),max(c[1] for c in coords)]


def geographic_bounds(grid, bounds):
    west,south,east,north = bounds
    coords = []
    for n in range(41):
        t = n/40
        coords += [grid.inverse.transform(west+t*(east-west),y) for y in (south,north)]
        coords += [grid.inverse.transform(x,south+t*(north-south)) for x in (west,east)]
    return [min(c[0] for c in coords),min(c[1] for c in coords),max(c[0] for c in coords),max(c[1] for c in coords)]


def classify_world(c):
    return {'Dining and Drinking':'food','Retail':'shopping',
            'Business and Professional Services':'service','Health and Medicine':'service'}.get(c['level1_category_name'],'other')


def active_points(path):
    # splitlines() also splits Unicode line separators inside valid JSON names.
    # Iterate physical JSONL lines and keep only density fields in memory.
    with path.open(encoding='utf-8') as stream:
        for line in stream:
            point = json.loads(line)
            if not point['date_closed']:
                yield {k:point[k] for k in ('x','y','lon','lat','category')}


def fetch_pilot(con, table, cats, pins, region_id):
    region = region_config(region_id)
    grid = RegionalGrid(*region['center'])
    bounds = projected_bounds(grid,region['bbox'])
    bounds = [bounds[0]-3750,bounds[1]-3750,bounds[2]+3750,bounds[3]+3750]
    fetch_bbox = geographic_bounds(grid,bounds)
    if fetch_bbox[2]-fetch_bbox[0] > 180:
        raise ValueError('Pilot input crosses date line; split regions before acquisition')
    out = Path('data/raw/foursquare-world')/region_id
    out.mkdir(parents=True,exist_ok=True)
    manifest_path = out/'manifest.json'
    if manifest_path.exists():
        previous = json.loads(manifest_path.read_text(encoding='utf-8'))
        if previous.get('complete') and previous['snapshots'] == pins and previous['region'] == region:
            if hashlib.sha256((out/'points.jsonl').read_bytes()).hexdigest() != previous['sha256']:
                raise ValueError('Raw pilot hash mismatch')
            print(region_id,'reusing complete pilot',flush=True)
            return
        raise ValueError('Different pilot version; use a fresh directory')
    west,south,east,north = fetch_bbox
    # No country filter: adjacent-country places must contribute across borders.
    predicate = 'longitude BETWEEN ? AND ? AND latitude BETWEEN ? AND ?'
    params = [west,east,south,north]
    expected,unique = con.execute(f'SELECT count(*),count(DISTINCT fsq_place_id) FROM {table} WHERE {predicate}',params).fetchone()
    if expected != unique:
        raise ValueError('Duplicate pilot IDs')
    print(region_id,'expected',expected,flush=True)
    con.execute(f'SELECT fsq_place_id,name,longitude,latitude,fsq_category_ids,date_closed FROM {table} WHERE {predicate}',params)
    category_map = {c['category_id']:classify_world(c) for c in cats}
    counts,closed,actual = {},0,0
    target = out/'points.jsonl'
    pending = out/'points.pending.jsonl'
    with pending.open('w',encoding='utf-8') as stream:
        while rows := con.fetchmany(20000):
            xs,ys = grid.project.transform([r[2] for r in rows],[r[3] for r in rows])
            for r,x,y in zip(rows,xs,ys):
                categories = {category_map.get(cid,'other') for cid in r[4] or []}
                category = next((c for c in ('food','shopping','service') if c in categories),'other')
                point = {'id':r[0],'name':r[1],'lon':r[2],'lat':r[3],'x':x,'y':y,'category':category,
                         'category_ids':r[4],'date_closed':str(r[5]) if r[5] else None}
                stream.write(json.dumps(point,ensure_ascii=False,separators=(',',':'))+'\n')
                actual += 1
                closed += bool(r[5])
                if not r[5]:
                    counts[category] = counts.get(category,0)+1
    if actual != expected:
        raise ValueError('Pilot count mismatch')
    pending.replace(target)
    compact_write(out/'categories.json',cats)
    compact_write(manifest_path,{'complete':True,'source':'Foursquare OS Places','region':region,'bbox':region['bbox'],
        'fetch_bbox':fetch_bbox,'input_halo_m':3750,'projection':grid.crs,'count':actual,'known_closed':closed,
        'active_categories':counts,'category_mapping':'level1 hierarchy; food > shopping > service; other retained in all',
        'snapshots':pins,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'sha256':hashlib.sha256(target.read_bytes()).hexdigest()})
    print(region_id,'verified',actual,'known closed',closed,flush=True)


def build_pilot(region_id):
    started = time.perf_counter()
    root = Path('data/raw/foursquare-world')/region_id
    raw = json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    if not raw['complete'] or hashlib.sha256((root/'points.jsonl').read_bytes()).hexdigest() != raw['sha256']:
        raise ValueError('Incomplete/corrupt pilot input')
    region = raw['region']
    grid = RegionalGrid(*region['center'])
    records = list(active_points(root/'points.jsonl'))
    names_root = Path('data/raw/world-names')/region_id
    stations = json.loads((names_root/'stations.json').read_text(encoding='utf-8'))
    places = json.loads((names_root/'places.json').read_text(encoding='utf-8'))
    names_meta = json.loads((names_root/'manifest.json').read_text(encoding='utf-8'))
    namer = WorldNamer(stations,places)
    out = Path('web/data')/f'foursquare-{region_id}'
    out.mkdir(parents=True,exist_ok=True)
    signature = hashlib.sha256((root/'manifest.json').read_bytes()+(names_root/'manifest.json').read_bytes()).hexdigest()
    manifest_path = out/'manifest.json'
    previous = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
    if previous and previous['input_signature'] != signature:
        raise ValueError('Changed inputs; use a new build directory')
    manifest = {'source':'Foursquare OS Places','bbox':region['bbox'],'coverage':region['name'],
        'region_id':region_id,'pilot':True,'input_signature':signature,'snapshots':raw['snapshots'],
        'known_closed':raw['known_closed'],'station_groups':len(stations),'projection':grid.crs,
        'grid_m':100,'chunk_m':50000,'input_halo_m':3750,'fetch_bbox':raw['fetch_bbox'],
        'category_mapping':raw['category_mapping'],'reference_names':names_meta,
        'background':'osm','datasets':[],'delivery':'viewport-chunks'}
    compact_write(out/'stations.json',stations)
    compact_write(out/'places.json',places)
    compact_write(out/'regions.json',{region_id:{'name':region['name'],'bbox':region['bbox'],'pref_codes':[]}})
    lowx,lowy,highx,highy = projected_bounds(grid,region['bbox'])
    mini,minj = grid.tile_key(lowx,lowy)
    maxi,maxj = grid.tile_key(highx,highy)
    keys = [(i,j) for i in range(mini,maxi+1) for j in range(minj,maxj+1)]
    clip = box(*region['bbox'])
    for sigma in (200,400,800):
        for category in ('all','food','shopping','service'):
            name = f'{sigma}-{category}-exclude'
            folder = out/name
            folder.mkdir(exist_ok=True)
            chunks,peaks,overview = [],[],[]
            reach = 4*sigma+550
            subset = [p for p in records if category=='all' or p['category']==category]
            for i,j in keys:
                path = folder/f'{i}_{j}.json'
                if path.exists():
                    geo = json.loads(path.read_text(encoding='utf-8'))
                else:
                    points = [p for p in subset if i*50000-reach <= p['x'] <= (i+1)*50000+reach and j*50000-reach <= p['y'] <= (j+1)*50000+reach]
                    geo = surface(points,i,j,sigma,None,[],inverse=grid.inverse,namer=namer)
                    # Six-decimal coordinate rounding can create touching holes;
                    # repair before intersection as well as after clipping.
                    sanitize_geo(geo)
                    clipped = []
                    for f in geo['features']:
                        geometry = shape(f['geometry']).intersection(clip)
                        if geometry.is_empty:
                            continue
                        f['geometry'] = mapping(geometry)
                        clipped.append(f)
                    geo['features'] = clipped
                    sanitize_geo(geo)
                    compact_write(path,geo)
                if geo['features']:
                    chunks.append({'file':f'{name}/{path.name}','bytes':path.stat().st_size,'bbox':region['bbox']})
                    peaks.extend(f for f in geo['features'] if f['properties']['kind']=='peak')
                    for f in geo['features']:
                        if f['properties']['kind']=='band' and f['properties']['density']>=800:
                            geometry = shape(f['geometry']).simplify(.0005,preserve_topology=True)
                            overview.append({**f,'geometry':mapping(geometry)})
            peaks.sort(key=lambda f:-f['properties']['density'])
            compact_write(out/f'{name}-peaks.json',{'type':'FeatureCollection','features':peaks})
            compact_write(out/f'{name}-overview.json',{'type':'FeatureCollection','features':overview})
            core_count = sum(region['bbox'][0] <= p['lon'] <= region['bbox'][2] and region['bbox'][1] <= p['lat'] <= region['bbox'][3] for p in subset)
            manifest['datasets'].append({'sigma':sigma,'category':category,'status':'exclude','count':len(subset),
                'core_count':core_count,'peaks':len(peaks),'chunks':chunks,'peaks_file':f'{name}-peaks.json','overview_file':f'{name}-overview.json'})
            compact_write(manifest_path,manifest)
            print(region_id,name,'peaks',len(peaks),flush=True)
    manifest['build_seconds'] = round(time.perf_counter()-started,2)
    compact_write(manifest_path,manifest)


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--region',required=True,choices=['sg-singapore','gb-london','is-reykjavik'])
    args = parser.parse_args()
    build_pilot(args.region)
