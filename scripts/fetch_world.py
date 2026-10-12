"""Bounded-memory world acquisition, atomic country files and snapshot resume."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import shutil
import time

VALID = 'coalesce(isfinite(longitude) AND isfinite(latitude) AND longitude BETWEEN -180 AND 180 AND latitude BETWEEN -90 AND 90, false)'
COLUMNS = 'fsq_place_id, name, longitude, latitude, country, fsq_category_ids, date_closed'


def write_json(path, data):
    temporary=path.with_suffix('.pending.json')
    temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
    for attempt in range(8):
        try:
            temporary.replace(path)
            break
        except PermissionError:
            if attempt==7: raise
            time.sleep(min(1,.1*(attempt+1)))


def digest(path):
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda:stream.read(8*1024*1024),b''): h.update(chunk)
    return h.hexdigest()


def country_key(country):
    if country is None: return 'country-null'
    if re.fullmatch('[A-Z]{2}',country): return country
    return 'country-'+hashlib.sha256(country.encode()).hexdigest()[:16]


def literal(value):
    return "'"+str(value).replace("'","''")+"'"


def fetch_world(con,table,cats,pins,plan_only=False,root=Path('data/raw/foursquare-global')):
    root.mkdir(parents=True,exist_ok=True)
    con.execute("SET temp_directory='data/cache/duckdb/world-spill'")
    con.execute('SET preserve_insertion_order=false')
    plan_path=root/'plan.json'
    if plan_path.exists():
        plan=json.loads(plan_path.read_text(encoding='utf-8'))
        if plan['snapshots']!=pins: raise ValueError('World snapshot changed; use a fresh directory')
    else:
        print('World: inventorying fixed snapshot by country',flush=True)
        rows=con.execute(f'''SELECT country,count(*),count(*) FILTER (WHERE {VALID}),
            count(*) FILTER (WHERE {VALID} AND date_closed IS NOT NULL)
            FROM {table} GROUP BY country''').fetchall()
        parts=[{'country':r[0],'file':country_key(r[0])+'.parquet','source_count':r[1],
                'count':r[2],'known_closed':r[3]} for r in rows]
        parts.sort(key=lambda p:(p['count'],p['file']))
        plan={'version':1,'snapshots':pins,'parts':parts,'source_count':sum(p['source_count'] for p in parts),
              'count':sum(p['count'] for p in parts),'invalid_coordinates':sum(p['source_count']-p['count'] for p in parts),
              'created_utc':datetime.now(timezone.utc).isoformat()}
        write_json(plan_path,plan)
    write_json(root/'categories.json',cats)
    print(f"World inventory: {plan['source_count']} source rows, {plan['count']} valid coordinates, {len(plan['parts'])} country groups",flush=True)
    if plan_only: return
    # A country predicate still scans remote files. Cache the world once, then
    # partition locally instead of repeating that transfer hundreds of times.
    stage=root/'world-source.parquet'
    stage_meta=root/'world-source.json'
    if stage_meta.exists():
        saved=json.loads(stage_meta.read_text(encoding='utf-8'))
        if saved['snapshots']!=pins or not stage.exists() or digest(stage)!=saved['sha256']:
            raise ValueError('World source cache mismatch')
    else:
        if shutil.disk_usage(root).free<40*1024**3: raise ValueError('Less than 40GiB free before world transfer')
        pending_stage=root/'world-source.pending.parquet'
        print('Downloading world source once; country partitioning will be local',flush=True)
        con.execute(f"COPY (SELECT {COLUMNS} FROM {table} WHERE {VALID}) TO {literal(pending_stage.as_posix())} (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 100000)")
        acquired,closed=con.execute('SELECT count(*),count(*) FILTER (WHERE date_closed IS NOT NULL) FROM read_parquet(?)',[str(pending_stage)]).fetchone()
        if acquired!=plan['count'] or closed!=sum(p['known_closed'] for p in plan['parts']):
            raise ValueError('World source cache counts mismatch')
        pending_stage.replace(stage)
        write_json(stage_meta,{'snapshots':pins,'count':acquired,'known_closed':closed,'bytes':stage.stat().st_size,'sha256':digest(stage)})
        print(f'World source downloaded and count-verified: {acquired} rows, {stage.stat().st_size} bytes',flush=True)
    table=f'read_parquet({literal(stage.as_posix())})'
    manifest_path=root/'manifest.json'
    manifest=json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {
        'version':1,'source':'Foursquare OS Places','snapshots':pins,'complete':False,'parts':[],
        'invalid_coordinates':plan['invalid_coordinates'],'source_count':plan['source_count'],
        'quality':'Country is a source attribute, not a spatial boundary. Known closed retained; active filtering is downstream.',
        'source_url':'https://docs.foursquare.com/data-products/docs/access-fsq-os-places'}
    if manifest['snapshots']!=pins: raise ValueError('Manifest snapshot mismatch')
    completed={p['file']:p for p in manifest['parts']}
    for part in plan['parts']:
        if part['count']==0: continue
        target=root/part['file']
        if part['file'] in completed:
            stored=completed[part['file']]
            if stored['count']!=part['count'] or not target.exists() or digest(target)!=stored['sha256']:
                raise ValueError('Completed world file is corrupt')
            continue
        if shutil.disk_usage(root).free<20*1024**3: raise ValueError('Less than 20GiB free disk space')
        pending=target.with_suffix('.pending.parquet')
        country_filter='country IS NULL' if part['country'] is None else 'country='+literal(part['country'])
        started=time.perf_counter()
        print(f"Acquiring {part['file']}: {part['count']} rows",flush=True)
        con.execute(f"COPY (SELECT {COLUMNS} FROM {table} WHERE {country_filter} AND {VALID}) TO {literal(pending.as_posix())} (FORMAT PARQUET, COMPRESSION ZSTD, ROW_GROUP_SIZE 100000)")
        count,unique,closed,bad=con.execute(f'''SELECT count(*),count(DISTINCT fsq_place_id),
            count(*) FILTER (WHERE date_closed IS NOT NULL),count(*) FILTER (WHERE NOT ({VALID}) OR fsq_place_id IS NULL)
            FROM read_parquet(?)''',[str(pending)]).fetchone()
        if (count,unique,closed,bad)!=(part['count'],part['count'],part['known_closed'],0):
            raise ValueError('World file count, IDs or coordinates mismatch')
        pending.replace(target)
        entry={**part,'sha256':digest(target),'bytes':target.stat().st_size,'seconds':round(time.perf_counter()-started,2)}
        completed[part['file']]=entry
        manifest.update(parts=list(completed.values()),count=sum(p['count'] for p in completed.values()),
                        bytes=sum(p['bytes'] for p in completed.values()),updated_utc=datetime.now(timezone.utc).isoformat())
        write_json(manifest_path,manifest)
        print(f"Verified {part['file']}; saved {manifest['count']}/{plan['count']} rows; {manifest['bytes']} bytes",flush=True)
    if sum(p['count'] for p in completed.values())!=plan['count']: raise ValueError('World total mismatch')
    # Catch duplicate IDs even across source country groups, with disk spill allowed.
    count,unique=con.execute('SELECT count(*),count(DISTINCT fsq_place_id) FROM read_parquet(?)',
                           [[str(root/p['file']) for p in completed.values()]]).fetchone()
    if count!=unique: raise ValueError('Duplicate IDs across world files')
    manifest.update(complete=True,global_unique_ids=unique,known_closed=sum(p['known_closed'] for p in completed.values()))
    write_json(manifest_path,manifest)
    print('World acquisition complete and globally verified',flush=True)
