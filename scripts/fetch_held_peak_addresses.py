"""Read address evidence from the pinned FSQ snapshot; never log credentials."""
import argparse,json,math,sys
from pathlib import Path
from datetime import datetime,timezone
import duckdb
from fetch_foursquare import load_token
from fetch_world import literal

ROOT=Path('data/name-research/held-poi-addresses')
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--env-file',type=Path,default=Path('C:/Projects-GitHub/geoai-open-lab/.env'))
    args=parser.parse_args();ROOT.mkdir(parents=True,exist_ok=True)
    pins=json.loads(Path('data/cache/foursquare/snapshots.json').read_text(encoding='utf-8'))
    sid=pins['places']['snapshot_id']
    if not sid.isascii() or not sid.isdigit():raise ValueError('Invalid snapshot')
    report=json.loads(Path('docs/held-peak-investigation.json').read_text(encoding='utf-8'))
    held={r['peak'] for r in report['items'] if r['decision']=='hold'}
    research=json.loads(Path('data/name-research/held-peak-features.json').read_text(encoding='utf-8'))
    groups={}
    for r in research['items']:
        if r['peak'] not in held:continue
        country=r['poi_samples'][0]['country_file']
        groups.setdefault(country,[]).append(r)
    if len(held)!=13:raise ValueError('Expected pinned 13 held peaks')
    con=duckdb.connect(config={'extension_directory':'data/cache/duckdb','threads':2,'memory_limit':'2GB'})
    phase='connect'
    try:
        con.execute('LOAD httpfs; LOAD iceberg')
        con.execute("SET temp_directory='data/cache/duckdb/held-address-spill'")
        token=load_token(args.env_file)
        con.execute("CREATE SECRET fsq_portal (TYPE iceberg, TOKEN '"+token.replace("'","''")+"')")
        del token
        con.execute("ATTACH 'places' AS places (TYPE iceberg, SECRET fsq_portal, ENDPOINT 'https://catalog.h3-hub.foursquare.com/iceberg', READ_ONLY)")
        table=f'places.datasets.places_os AT (VERSION => {sid})'
        schema=con.execute(f'DESCRIBE SELECT * FROM {table}').fetchall()
        fields=[r[0] for r in schema]
        ROOT.joinpath('schema.json').write_text(json.dumps(schema,indent=2),encoding='utf-8')
        wanted=['fsq_place_id','name','latitude','longitude','address','locality','region','postcode','admin_region','post_town','country','date_created','date_refreshed','date_closed','placemaker_url']
        selected=[f for f in wanted if f in fields]
        print(json.dumps({'phase':'schema','fields':selected,'snapshot':sid}),flush=True)
        # Remote country predicates can still scan many snapshot files. Combine
        # all 13 boxes into one pass, then split the small result locally.
        all_output=ROOT/'all.parquet';all_meta=ROOT/'all.json'
        if not (all_output.exists() and all_meta.exists() and json.loads(all_meta.read_text())['snapshot_id']==sid):
            clauses=[];params=[]
            for code,rows in groups.items():
                boxes=[];params.append(code)
                for r in rows:
                    lon,lat=r['coordinates'];dx=0.005/math.cos(math.radians(lat))
                    boxes.append('(longitude BETWEEN ? AND ? AND latitude BETWEEN ? AND ?)')
                    params.extend([lon-dx,lon+dx,lat-0.005,lat+0.005])
                clauses.append('(country=? AND ('+' OR '.join(boxes)+'))')
            sql=f'SELECT {", ".join(selected)} FROM {table} WHERE date_closed IS NULL AND ('+' OR '.join(clauses)+')'
            phase='combined_address_scan'
            print(json.dumps({'phase':phase,'peaks':13,'countries':list(groups)}),flush=True)
            pending=ROOT/'all.pending.parquet'
            con.execute('COPY ('+sql+') TO '+literal(pending.as_posix())+' (FORMAT PARQUET)',params)
            expected={p['id'] for r in research['items'] if r['peak'] in held for p in r['poi_samples']}
            actual=con.execute('SELECT fsq_place_id FROM read_parquet(?)',[str(pending)]).fetchall()
            if {p[0] for p in actual}!=expected or len(actual)!=len(expected):raise ValueError('Snapshot ID coverage differs from local evidence')
            pending.replace(all_output)
            all_meta.write_text(json.dumps({'snapshot_id':sid,'count':len(actual),'ids_verified':True,'query_template':sql,'query_parameters':params},indent=2),encoding='utf-8')
        for code,rows in groups.items():
            phase=code
            output=ROOT/(code+'.parquet');meta=ROOT/(code+'.json')
            if output.exists() and meta.exists() and json.loads(meta.read_text())['snapshot_id']==sid:
                print(json.dumps({'country':code,'cached':True}),flush=True);continue
            sql='SELECT * FROM read_parquet(?) WHERE country=?';params=[str(all_output),code]
            pending=output.with_suffix('.pending.parquet')
            # Bind predicate values; quote the fixed project-local output path.
            # COPY's filename parameter binds before SELECT placeholders.
            con.execute('COPY ('+sql+') TO '+literal(pending.as_posix())+' (FORMAT PARQUET)',params)
            count=con.execute('SELECT count(*) FROM read_parquet(?)',[str(pending)]).fetchone()[0]
            pending.replace(output)
            info={'snapshot_id':sid,'snapshot_timestamp':pins['places']['timestamp'],'retrieved_at':datetime.now(timezone.utc).isoformat(),'country':code,'fields':selected,'peaks':[r['peak'] for r in rows],'count':count,'query_template':sql,'query_parameters':params,'source_url':'https://docs.foursquare.com/data-products/docs/access-fsq-os-places','license':'Apache 2.0; Foursquare OS Places'}
            meta.write_text(json.dumps(info,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            print(json.dumps({'country':code,'phase':'complete','records':count}),flush=True)
        print('Address acquisition complete',flush=True)
    except Exception as exc:
        # Remote exceptions can include signed paths or tokens. Retain only
        # safe phase/type; do not print exception messages or tracebacks.
        print(json.dumps({'phase':phase,'error_type':type(exc).__name__,'error':'Read-only acquisition failed; remote details suppressed.'}),flush=True)
        return 1
    finally:con.close()
    return 0
if __name__=='__main__':sys.exit(main())
