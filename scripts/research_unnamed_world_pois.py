"""Scan every locally pinned country file around all remaining unnamed peaks.

All countries are scanned, including border cases. Facility names are evidence,
not automatic place-name decisions. No remote credentials are needed here.
"""
import json, math
from pathlib import Path
import duckdb

ROOT=Path('data/name-research/unnamed-world')

def main():
    rows=json.loads((ROOT/'targets.json').read_text(encoding='utf-8'))['items']
    con=duckdb.connect(config={'threads':4,'memory_limit':'2GB'})
    con.execute("SET temp_directory='data/cache/duckdb/unnamed-spill'")
    con.execute('CREATE TABLE targets(peak VARCHAR,lon DOUBLE,lat DOUBLE,dx DOUBLE,bx BIGINT,cell_y BIGINT)')
    bins=[]
    for r in rows:
        lon,lat=r['coordinates'];dx=.007/math.cos(math.radians(lat))
        for x in range(math.floor((lon-dx)/.02),math.floor((lon+dx)/.02)+1):
            for y in range(math.floor((lat-.007)/.02),math.floor((lat+.007)/.02)+1):
                bins.append((r['peak'],lon,lat,dx,x,y))
    import csv
    with (ROOT/'target-bins.csv').open('w',newline='') as stream:csv.writer(stream).writerows(bins)
    con.execute("INSERT INTO targets SELECT * FROM read_csv('data/name-research/unnamed-world/target-bins.csv',header=false)")
    out=ROOT/'local-parts';out.mkdir(exist_ok=True)
    manifest=json.loads(Path('data/raw/foursquare-global/manifest.json').read_text(encoding='utf-8'))
    files=sorted(Path('data/raw/foursquare-global')/p['file'] for p in manifest['parts'])
    for i,p in enumerate(files):
        target=out/p.name
        if not target.exists():
            pending=target.with_suffix('.pending.parquet')
            sql='''SELECT t.peak,p.* FROM read_parquet(?) p JOIN targets t
                ON floor(p.longitude/.02)::BIGINT=t.bx AND floor(p.latitude/.02)::BIGINT=t.cell_y
                AND p.longitude BETWEEN t.lon-t.dx AND t.lon+t.dx
                AND p.latitude BETWEEN t.lat-.007 AND t.lat+.007
                WHERE p.date_closed IS NULL'''
            con.execute("COPY ("+sql+") TO '"+pending.as_posix()+"' (FORMAT PARQUET)",[str(p)])
            pending.replace(target)
        count=con.execute('SELECT count(*) FROM read_parquet(?)',[str(target)]).fetchone()[0]
        (ROOT/'progress.json').write_text(json.dumps({'phase':'local_evidence','countries_completed':i+1,'countries_total':len(files),'last_country':p.stem,'last_records':count}),encoding='utf-8')
        print(json.dumps({'country':p.stem,'records':count,'progress':f'{i+1}/{len(files)}'}),flush=True)
    source=[str(out/p.name) for p in files]
    stats=con.execute('''SELECT peak,count(*),count(DISTINCT fsq_place_id),count(DISTINCT (longitude,latitude)),
      list(DISTINCT country) FROM read_parquet(?) GROUP BY peak''',[source]).fetchall()
    by_peak={r[0]:{'records':r[1],'unique_ids':r[2],'distinct_coordinates':r[3],'countries':r[4]} for r in stats}
    samples=con.execute('''SELECT peak,fsq_place_id,name,longitude,latitude,country FROM read_parquet(?)
      QUALIFY row_number() OVER(PARTITION BY peak ORDER BY fsq_place_id)<=12''',[source]).fetchall()
    grouped={}
    for peak,pid,name,lon,lat,country in samples:
        grouped.setdefault(peak,[]).append(dict(id=pid,name=name,lon=lon,lat=lat,country=country))
    report={'radius_note':'Boxes +/-0.007 degrees latitude, longitude adjusted for latitude; not geocoded addresses','source':'Foursquare OS Places pinned 2026-09-15, all 254 pinned country partitions','items':[{**r,**by_peak.get(r['peak'],{'records':0}),'samples':grouped.get(r['peak'],[])} for r in rows]}
    (ROOT/'local-evidence.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    ids=con.execute('SELECT DISTINCT fsq_place_id,longitude,latitude FROM read_parquet(?)',[source]).fetchall()
    (ROOT/'ids.json').write_text(json.dumps(ids),encoding='utf-8')
    print(json.dumps({'complete':True,'peaks':len(rows),'with_pois':len(stats),'unique_ids':len(ids)}),flush=True)

if __name__=='__main__':main()
