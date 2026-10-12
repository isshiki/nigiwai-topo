"""Inspect all named point features around the 18 held peaks; never auto-adopt."""
import io,json,zipfile,math,urllib.request,hashlib
from pathlib import Path
from pyproj import Geod
import duckdb

ROOT=Path('data/name-research/coordinate-countries')
GEOD=Geod(ellps='WGS84')
def main():
    all_rows=json.loads(Path('docs/world-coordinate-name-review.json').read_text(encoding='utf-8'))['items']
    pinned=Path('docs/held-peak-investigation.json')
    keys={r['peak'] for r in json.loads(pinned.read_text(encoding='utf-8'))['items']} if pinned.exists() else {r['peak'] for r in all_rows if r['decision']=='hold'}
    targets=[r for r in all_rows if r['peak'] in keys]
    if len(targets)!=18:raise ValueError('Original 18 investigation targets changed')
    con=duckdb.connect(config={'threads':2,'memory_limit':'2GB'})
    sources={};out=[]
    for r in targets:
        lon,lat=r['coordinates'];country=r['poi_cluster_evidence']['country']
        codes=[country,'KW'] if r['peak']=='28.649, 48.369' else [country]
        candidates=[];pois=[]
        for code in codes:
            archive=ROOT/(code+'.zip');url=f'https://download.geonames.org/export/dump/{code}.zip'
            if not archive.exists():
                with urllib.request.urlopen(url,timeout=60) as response:content=response.read()
                with zipfile.ZipFile(io.BytesIO(content)) as z:
                    if z.testzip():raise ValueError('Invalid ZIP')
                archive.write_bytes(content)
            sources[code]={'url':url,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'license':'CC BY 4.0'}
            with zipfile.ZipFile(archive) as z,z.open(code+'.txt') as stream:
                for line in io.TextIOWrapper(stream,encoding='utf-8'):
                    f=line.rstrip('\n').split('\t')
                    if len(f)!=19 or f[8]!=code:continue
                    x,y=float(f[4]),float(f[5])
                    if abs(x-lat)>0.15 or abs(y-lon)>0.15/math.cos(math.radians(lat)):continue
                    d=GEOD.inv(lon,lat,y,x)[2]
                    if d<=15000:candidates.append({'id':f[0],'name':f[1],'alternates':f[3],'class':f[6],'code':f[7],'country':code,'lon':y,'lat':x,'distance_m':round(d),'modified':f[18]})
            raw=Path('data/raw/foursquare-global')/(code+'.parquet')
            dx=0.005/math.cos(math.radians(lat))
            rows=con.execute('SELECT fsq_place_id,name,longitude,latitude FROM read_parquet(?) WHERE date_closed IS NULL AND longitude BETWEEN ? AND ? AND latitude BETWEEN ? AND ? ORDER BY fsq_place_id',[str(raw),lon-dx,lon+dx,lat-0.005,lat+0.005]).fetchall()
            pois.extend({'id':p[0],'name':p[1],'lon':p[2],'lat':p[3],'country_file':code} for p in rows)
        out.append({'peak':r['peak'],'coordinates':r['coordinates'],'density':r['density'],'candidates':sorted(candidates,key=lambda p:p['distance_m'])[:30],'active_poi_count':len(pois),'poi_samples':pois})
        print(json.dumps({'peak':r['peak'],'references':len(candidates),'pois':len(pois)}),flush=True)
    con.close()
    Path('data/name-research/held-peak-features.json').write_text(json.dumps({'scope':'18 held high peaks; all GeoNames feature classes within 15km; active FSQ local rectangle including KW border file','sources':sources,'items':out},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
if __name__=='__main__':main()
