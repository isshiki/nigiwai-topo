"""Inspect local, open POI source records around the 60 unnamed high peaks.

Coincident points can be legitimate malls; this reports evidence, never removes
records or declares the locations false solely because coordinates coincide.
"""
import json,math
from pathlib import Path
from collections import Counter
import duckdb

def main():
    targets=json.loads(Path('data/name-research/coordinate-local-review.json').read_text(encoding='utf-8'))['items']
    con=duckdb.connect(config={'threads':2,'memory_limit':'2GB'})
    con.execute('CREATE TEMP TABLE targets(label VARCHAR,lon DOUBLE,lat DOUBLE,dx DOUBLE)')
    groups={}
    for r in targets:groups.setdefault(r['nearest_registered_place']['country'],[]).append(r)
    records=[]
    for country,rows in groups.items():
        con.execute('DELETE FROM targets')
        con.executemany('INSERT INTO targets VALUES (?,?,?,?)',[(r['properties']['name'],*r['coordinates'],0.005/math.cos(math.radians(r['coordinates'][1]))) for r in rows])
        source=Path('data/raw/foursquare-global')/(country+'.parquet')
        result=con.execute('''SELECT t.label,p.fsq_place_id,p.name,p.longitude,p.latitude
          FROM read_parquet(?) p JOIN targets t
          ON p.longitude BETWEEN t.lon-t.dx AND t.lon+t.dx
          AND p.latitude BETWEEN t.lat-0.005 AND t.lat+0.005
          WHERE p.date_closed IS NULL ORDER BY t.label,p.fsq_place_id''',[str(source)]).fetchall()
        for r in rows:
            label=r['properties']['name'];pois=[p for p in result if p[0]==label]
            counts=Counter((p[3],p[4]) for p in pois);top=counts.most_common(3)
            clusters=[]
            for (lon,lat),count in top:
                samples=[{'id':p[1],'name':p[2]} for p in pois if (p[3],p[4])==(lon,lat)][:8]
                clusters.append({'lon':lon,'lat':lat,'count':count,'samples':samples})
            records.append({'peak':label,'country':country,'source':str(source),'bbox_half_height_degrees':0.005,'active_records':len(pois),'distinct_ids':len({p[1] for p in pois}),'distinct_coordinate_pairs':len(counts),'max_coincident_records':top[0][1] if top else 0,'top_coordinate_clusters':clusters})
        print(json.dumps({'country':country,'peaks':len(rows)}),flush=True)
    con.close()
    output={'grain':'one active Foursquare place ID; source snapshot 2026-09-15','scope':'60 coordinate-only peaks with density >=800; local boxes approximately 1.1 km square','country_scope_caveat':'Country files chosen using the nearest gazetteer reference; border cases can exclude POIs registered in adjacent countries. Zero records do not establish an empty location.','not_a_worldwide_coordinate_quality_rate':True,'items':records}
    Path('data/name-research/coordinate-poi-cluster-audit.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')

if __name__=='__main__':main()
