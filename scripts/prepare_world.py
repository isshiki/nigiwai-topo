"""Local world input preparation and independent pilot-source equivalence checks."""
import argparse
import json
from pathlib import Path
import time
import duckdb
try:
    from .fetch_world import write_json, digest
except ImportError:
    from fetch_world import write_json, digest

ROOT=Path('data/raw/foursquare-global')
OUT=Path('data/world-build')
DISPLAY_LAT=85.0511287798066


def category_sql(cats):
    def ids(names):
        values=[str(c['category_id']) for c in cats if c.get('level1_category_name') in names]
        return '['+','.join("'"+v.replace("'","''")+"'" for v in values)+']'
    return ('CASE WHEN list_has_any(fsq_category_ids,'+ids(['Dining and Drinking'])+
            ") THEN 'food' WHEN list_has_any(fsq_category_ids,"+ids(['Retail'])+
            ") THEN 'shopping' WHEN list_has_any(fsq_category_ids,"+ids(['Business and Professional Services','Health and Medicine'])+
            ") THEN 'service' ELSE 'other' END")


def connection():
    Path('data/cache/duckdb/world-build-spill').mkdir(parents=True,exist_ok=True)
    return duckdb.connect(config={'threads':2,'memory_limit':'2GB','temp_directory':'data/cache/duckdb/world-build-spill'})


def check_pilots(con):
    report=[]
    for region in ('sg-singapore','gb-london','is-reykjavik'):
        folder=Path('data/raw/foursquare-world')/region
        meta=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
        w,s,e,n=meta['fetch_bbox']
        con.execute('CREATE OR REPLACE TEMP TABLE pilot AS SELECT * FROM read_parquet(?) WHERE longitude BETWEEN ? AND ? AND latitude BETWEEN ? AND ?',
                    [str(ROOT/'world-source.parquet'),w,e,s,n])
        con.execute("CREATE OR REPLACE TEMP TABLE previous AS SELECT * FROM read_json(?,format='newline_delimited',maximum_object_size=16777216)",[str(folder/'points.jsonl')])
        differences=con.execute('''SELECT count(*) FROM pilot p FULL JOIN previous o ON p.fsq_place_id=o.id
            WHERE p.fsq_place_id IS NULL OR o.id IS NULL OR p.name IS DISTINCT FROM o.name
            OR p.longitude IS DISTINCT FROM o.lon OR p.latitude IS DISTINCT FROM o.lat
            OR CAST(p.date_closed AS VARCHAR) IS DISTINCT FROM o.date_closed
            OR p.fsq_category_ids IS DISTINCT FROM o.category_ids''').fetchone()[0]
        count=con.execute('SELECT count(*) FROM pilot').fetchone()[0]
        if differences or count!=meta['count']: raise ValueError('Pilot source equivalence failed: '+region)
        report.append({'region':region,'count':count,'different_records':differences})
        print(region,'source equivalence verified',count,flush=True)
    return report


def prepare(con):
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    source_meta=json.loads((ROOT/'world-source.json').read_text(encoding='utf-8'))
    if not manifest['complete'] or manifest['count']!=source_meta['count']:
        raise ValueError('Global source is not complete')
    OUT.mkdir(parents=True,exist_ok=True)
    cats=json.loads((ROOT/'categories.json').read_text(encoding='utf-8'))
    signature=source_meta['sha256']
    metadata=OUT/'manifest.json'
    previous=json.loads(metadata.read_text()) if metadata.exists() else None
    target=OUT/'active.parquet'
    if previous and previous.get('complete'):
        if previous['source_sha256']!=signature or digest(target)!=previous['sha256']:
            raise ValueError('Prepared source mismatch')
        print('World inputs already prepared',flush=True)
        return
    print('Preparing active world records locally, with strict category hierarchy',flush=True)
    # Classify repeated category combinations once rather than evaluating four
    # large list intersections for every one of the 101 million active rows.
    con.execute(f'''CREATE TEMP TABLE patterns AS SELECT fsq_category_ids,{category_sql(cats)} AS category
        FROM (SELECT DISTINCT fsq_category_ids FROM read_parquet('{(ROOT/'world-source.parquet').as_posix()}')
        WHERE date_closed IS NULL)''')
    print('Category combinations:',con.execute('SELECT count(*) FROM patterns').fetchone()[0],flush=True)
    pending=OUT/'active.pending.parquet'
    # The two-degree cells are an input retrieval index, not final KDE grids.
    con.execute(f'''COPY (SELECT source.*,coalesce(patterns.category,'other') AS category,
        least(179,CAST(floor((longitude+180)/2) AS INTEGER)) AS cell_x,
        least(89,CAST(floor((latitude+90)/2) AS INTEGER)) AS cell_y
        FROM read_parquet('{(ROOT/'world-source.parquet').as_posix()}') AS source
        LEFT JOIN patterns ON source.fsq_category_ids=patterns.fsq_category_ids WHERE date_closed IS NULL)
        TO '{pending.as_posix()}' (FORMAT PARQUET,COMPRESSION ZSTD,ROW_GROUP_SIZE 100000)''')
    count=con.execute('SELECT count(*) FROM read_parquet(?)',[str(pending)]).fetchone()[0]
    if count!=manifest['count']-manifest['known_closed']: raise ValueError('Active count mismatch')
    pending.replace(target)
    print('Active records:',count,flush=True)
    rows=con.execute('''SELECT cell_x,cell_y,category,count(*) FROM read_parquet(?)
        GROUP BY cell_x,cell_y,category ORDER BY cell_y,cell_x,category''',[str(target)]).fetchall()
    cells={}
    for x,y,category,n in rows:
        key=f'{x}-{y}'
        cells.setdefault(key,{'id':key,'bbox':[-180+x*2,-90+y*2,-178+x*2,-88+y*2],'categories':{}})['categories'][category]=n
    outside=con.execute('SELECT count(*) FROM read_parquet(?) WHERE abs(latitude)>?',[str(target),DISPLAY_LAT]).fetchone()[0]
    write_json(OUT/'cells.json',{'version':1,'cell_degrees':2,'role':'input index only; KDE projection and seams require validation',
                              'cells':list(cells.values()),'outside_web_mercator':outside})
    report={'complete':True,'source_sha256':signature,'snapshots':manifest['snapshots'],'count':count,
            'bytes':target.stat().st_size,'sha256':digest(target),'occupied_cells':len(cells),'outside_web_mercator':outside,
            'categories':dict(con.execute('SELECT category,count(*) FROM read_parquet(?) GROUP BY category',[str(target)]).fetchall())}
    write_json(metadata,report)
    print('World preparation verified:',json.dumps(report),flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--check-pilots',action='store_true')
    args=parser.parse_args()
    started=time.perf_counter()
    with connection() as con:
        if args.check_pilots:
            report=check_pilots(con)
            Path('data/validation').mkdir(parents=True,exist_ok=True)
            write_json(Path('data/validation/world-source-equivalence.json'),report)
        else: prepare(con)
    print('Seconds:',round(time.perf_counter()-started,1),flush=True)
