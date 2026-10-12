"""Recover address columns for the exact POI IDs near 5,356 unnamed peaks.

Pinned snapshot, read-only catalog, local output, no credential logging.
"""
import json, sys
from pathlib import Path
import duckdb
from fetch_foursquare import load_token

ROOT=Path('data/name-research/unnamed-world')

def main():
    pins=json.loads(Path('data/cache/foursquare/snapshots.json').read_text(encoding='utf-8'))
    sid=str(pins['places']['snapshot_id'])
    if not sid.isdigit():raise ValueError('Invalid snapshot')
    expected={r[0]:(r[1],r[2]) for r in json.loads((ROOT/'ids.json').read_text(encoding='utf-8'))}
    con=duckdb.connect(config={'extension_directory':'data/cache/duckdb','threads':4,'memory_limit':'2GB'})
    con.execute("SET temp_directory='data/cache/duckdb/unnamed-address-spill'")
    phase='connect'
    output=ROOT/'addresses.parquet'
    try:
        if not output.exists():
            con.execute('LOAD httpfs; LOAD iceberg')
            token=load_token(Path('C:/Projects-GitHub/geoai-open-lab/.env'))
            con.execute("CREATE SECRET fsq_portal (TYPE iceberg, TOKEN '"+token.replace("'","''")+"')")
            del token
            con.execute("ATTACH 'places' AS places (TYPE iceberg, SECRET fsq_portal, ENDPOINT 'https://catalog.h3-hub.foursquare.com/iceberg', READ_ONLY)")
            table=f'places.datasets.places_os AT (VERSION => {sid})'
            fields={r[0] for r in con.execute(f'DESCRIBE SELECT * FROM {table}').fetchall()}
            wanted=['fsq_place_id','name','longitude','latitude','country','address','locality','region','admin_region','postcode','post_town','date_closed']
            selected=[f'p.{f}' for f in wanted if f in fields]
            phase='address_scan'
            (ROOT/'address-progress.json').write_text(json.dumps({'phase':phase,'snapshot':sid,'expected_ids':len(expected)}),encoding='utf-8')
            print(json.dumps({'phase':phase,'snapshot':sid,'expected_ids':len(expected)}),flush=True)
            # Equality join recovers precisely the locally observed IDs; no
            # nearest-country assumption or address-to-coordinate inference.
            sql=f'''SELECT {', '.join(selected)} FROM (SELECT * FROM {table}) p SEMI JOIN
              (SELECT DISTINCT fsq_place_id FROM read_parquet('data/name-research/unnamed-world/local-parts/*.parquet')) t
              ON p.fsq_place_id=t.fsq_place_id WHERE p.date_closed IS NULL'''
            pending=output.with_suffix('.pending.parquet')
            con.execute("COPY ("+sql+") TO '"+pending.as_posix()+"' (FORMAT PARQUET)")
            output_candidate=pending
        else:
            meta=json.loads((ROOT/'address-progress.json').read_text(encoding='utf-8'))
            if meta.get('snapshot')!=sid:raise ValueError('Snapshot differs')
            output_candidate=output
        actual={pid:(lon,lat) for pid,lon,lat in con.execute('SELECT fsq_place_id,longitude,latitude FROM read_parquet(?)',[str(output_candidate)]).fetchall()}
        if actual!=expected:raise ValueError('IDs or coordinates differ')
        if output_candidate!=output:output_candidate.replace(output)
        totals=con.execute("SELECT count(*),count(*) FILTER(WHERE nullif(trim(address),'') IS NOT NULL),count(*) FILTER(WHERE nullif(trim(locality),'') IS NOT NULL) FROM read_parquet(?)",[str(output)]).fetchone()
        meta={'phase':'complete','snapshot':sid,'verified_ids':len(actual),'records':totals[0],'with_address':totals[1],'with_locality':totals[2],'source':'Foursquare OS Places / Apache 2.0','ids_and_coordinates_verified':True}
        (ROOT/'address-progress.json').write_text(json.dumps(meta,indent=2),encoding='utf-8')
        print(json.dumps(meta),flush=True)
    except Exception as exc:
        info={'phase':phase,'snapshot':sid,'status':'failed','error_type':type(exc).__name__,'details':'Remote details suppressed to protect credentials'}
        (ROOT/'address-progress.json').write_text(json.dumps(info),encoding='utf-8')
        print(json.dumps(info),flush=True);return 1
    finally:con.close()
    return 0

if __name__=='__main__':sys.exit(main())
