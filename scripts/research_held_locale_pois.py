"""Inspect pinned local POIs near four held references and their assigned peaks."""
import json, math, sys
from pathlib import Path
import duckdb
from pyproj import Geod
from fetch_foursquare import load_token
from fetch_world import literal

ROOT=Path('data/name-research/held-locale-pois')
def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    targets=[r for r in json.loads(Path('docs/held-locale-final-review.json').read_text(encoding='utf-8'))['items'] if r['decision']=='hold']
    if len(targets)!=4:raise ValueError('Expected four held references')
    manifest=json.loads(Path('data/distribution/foursquare-world-v2/manifest.json').read_text(encoding='utf-8'))
    for r in targets:r['peaks']=[]
    for package in manifest['packages']:
        for f in json.loads(Path('data/distribution/foursquare-world-v2',package['id'],'200-all-peaks.json').read_text(encoding='utf-8'))['features']:
            p=f['properties']
            for r in targets:
                if p.get('name_source')=='GeoNames' and r['id'].split(':')[1] in map(str,p.get('name_source_ids',[])):
                    r['peaks'].append({'coordinates':f['geometry']['coordinates'],'density':p['density']})
    con=duckdb.connect(config={'extension_directory':'data/cache/duckdb','threads':2,'memory_limit':'2GB'})
    geod=Geod(ellps='WGS84');ids={};boxes=[]
    for r in targets:
        centers=[('reference',r['lon'],r['lat'])]+[(f'peak{i}',*p['coordinates']) for i,p in enumerate(r['peaks'])]
        r['samples']=[]
        for label,lon,lat in centers:
            dx=.01/math.cos(math.radians(lat));boxes.append((lon-dx,lon+dx,lat-.01,lat+.01))
            rows=con.execute('SELECT fsq_place_id,name,longitude,latitude FROM read_parquet(?) WHERE date_closed IS NULL AND longitude BETWEEN ? AND ? AND latitude BETWEEN ? AND ?',[str(Path('data/raw/foursquare-global/CN.parquet')),lon-dx,lon+dx,lat-.01,lat+.01]).fetchall()
            for pid,name,x,y in rows:
                d=geod.inv(lon,lat,x,y)[2]
                if d<=1000:
                    r['samples'].append({'center':label,'id':pid,'name':name,'lon':x,'lat':y,'distance_m':round(d)})
                    ids[pid]=(x,y)
        r['samples'].sort(key=lambda p:(p['center'],p['distance_m']))
    ROOT.joinpath('local.json').write_text(json.dumps({'radius_m':1000,'items':targets,'unique_pois':len(ids)},ensure_ascii=False,indent=2),encoding='utf-8')
    pins=json.loads(Path('data/cache/foursquare/snapshots.json').read_text(encoding='utf-8'));sid=pins['places']['snapshot_id']
    if not str(sid).isdigit():raise ValueError('Invalid snapshot')
    output=ROOT/'addresses.parquet';phase='connect'
    try:
        if output.exists():
            cache_meta=ROOT/'addresses.json'
            if not cache_meta.exists() or json.loads(cache_meta.read_text(encoding='utf-8')).get('snapshot_id')!=sid:
                raise ValueError('Address cache snapshot is unverified or differs')
        if not output.exists():
            con.execute('LOAD httpfs; LOAD iceberg')
            token=load_token(Path('C:/Projects-GitHub/geoai-open-lab/.env'))
            con.execute("CREATE SECRET fsq_portal (TYPE iceberg, TOKEN '"+token.replace("'","''")+"')");del token
            con.execute("ATTACH 'places' AS places (TYPE iceberg, SECRET fsq_portal, ENDPOINT 'https://catalog.h3-hub.foursquare.com/iceberg', READ_ONLY)")
            table=f'places.datasets.places_os AT (VERSION => {sid})'
            fields={r[0] for r in con.execute(f'DESCRIBE SELECT * FROM {table}').fetchall()}
            selected=[f for f in ['fsq_place_id','name','latitude','longitude','address','locality','region','postcode','admin_region','post_town','country','date_closed'] if f in fields]
            clauses=[];params=[]
            for box in boxes:clauses.append('(longitude BETWEEN ? AND ? AND latitude BETWEEN ? AND ?)');params.extend(box)
            sql=f'SELECT {", ".join(selected)} FROM {table} WHERE country=\'CN\' AND date_closed IS NULL AND ('+' OR '.join(clauses)+')'
            phase='address_scan';print(json.dumps({'phase':phase,'unique_local_ids':len(ids),'centers':len(boxes),'snapshot':sid}),flush=True)
            pending=ROOT/'addresses.pending.parquet'
            con.execute('COPY ('+sql+') TO '+literal(pending.as_posix())+' (FORMAT PARQUET)',params);pending.replace(output)
        cursor=con.execute('SELECT * FROM read_parquet(?)',[str(output)]);keys=[p[0] for p in cursor.description]
        rows=[dict(zip(keys,p)) for p in cursor.fetchall() if p[0] in ids]
        actual={r['fsq_place_id']:(r['longitude'],r['latitude']) for r in rows}
        if actual!=ids or len(rows)!=len(ids):raise ValueError('Pinned IDs or coordinates differ')
        ROOT.joinpath('addresses.json').write_text(json.dumps({'snapshot_id':sid,'ids_and_coordinates_verified':True,'count':len(rows),'items':rows},ensure_ascii=False,indent=2),encoding='utf-8')
        print(json.dumps({'complete':True,'verified_records':len(rows)}),flush=True)
    except Exception as exc:
        print(json.dumps({'phase':phase,'error_type':type(exc).__name__,'details':'Remote details suppressed'}),flush=True);return 1
    finally:con.close()
    return 0
if __name__=='__main__':sys.exit(main())
