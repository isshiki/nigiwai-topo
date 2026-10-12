"""Research coordinate-only peaks using complete country gazetteers, not distant cities."""
import io,json,zipfile,urllib.request,hashlib,math
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from datetime import datetime,timezone
import numpy as np
from scipy.spatial import cKDTree
from pyproj import Geod

ROOT=Path('data/name-research/coordinate-countries')
GEOD=Geod(ellps='WGS84')
def unit(lon,lat):
    lon,lat=np.radians(lon),np.radians(lat)
    return np.column_stack([np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)])

def country(code,targets):
    archive=ROOT/(code+'.zip');url=f'https://download.geonames.org/export/dump/{code}.zip'
    if not archive.exists():
        req=urllib.request.Request(url,headers={'User-Agent':'NigiwaiTopo place-name research'})
        pending=archive.with_suffix('.pending.zip')
        with urllib.request.urlopen(req,timeout=120) as response,pending.open('wb') as out:
            while data:=response.read(1024*1024):out.write(data)
        with zipfile.ZipFile(pending) as z:
            if z.testzip():raise ValueError('Corrupt country ZIP')
        pending.replace(archive)
    places=[]
    with zipfile.ZipFile(archive) as z:
        with z.open(code+'.txt') as stream:
            for line in io.TextIOWrapper(stream,encoding='utf-8'):
                f=line.rstrip('\n').split('\t')
                if len(f)!=19:raise ValueError('Unexpected GeoNames fields')
                if not ((f[6]=='P' and f[7] not in ('PPLH','PPLQ','PPLW')) or f[7]=='AIRP'):continue
                if f[8]!=code:continue
                places.append(dict(id=f[0],name=f[1],ascii=f[2],lat=float(f[4]),lon=float(f[5]),country=code,feature_code=f[7],population=int(f[14] or 0),modified=f[18]))
    tree=cKDTree(unit([p['lon'] for p in places],[p['lat'] for p in places]))
    records=[]
    for target in targets:
        lon,lat=target['coordinates'];_,idx=tree.query(unit([lon],[lat])[0],k=min(10,len(places)))
        candidates=[]
        for i in np.atleast_1d(idx):
            p=places[int(i)];distance=round(GEOD.inv(lon,lat,p['lon'],p['lat'])[2])
            candidates.append({**p,'distance_m':distance})
        records.append({**target,'local_candidates':sorted(candidates,key=lambda p:p['distance_m'])[:3]})
    provenance={'country':code,'source_url':url,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'bytes':archive.stat().st_size,'license':'CC BY 4.0','retrieved_or_checked_at':datetime.now(timezone.utc).isoformat(),'eligible_places':len(places)}
    print(json.dumps({'country':code,'peaks':len(targets),'places':len(places)}),flush=True)
    return records,provenance

def main():
    ROOT.mkdir(parents=True,exist_ok=True)
    targets=json.loads(Path('data/name-translation/world/coordinate-priority-review.json').read_text(encoding='utf-8'))['items']
    groups={}
    for r in targets:groups.setdefault(r['nearest_registered_place']['country'],[]).append(r)
    records=[];sources=[];errors=[]
    with ThreadPoolExecutor(max_workers=3) as pool:
        jobs={pool.submit(country,code,rows):code for code,rows in groups.items()}
        for job in as_completed(jobs):
            try:
                rows,source=job.result();records+=rows;sources.append(source)
            except Exception as exc:errors.append({'country':jobs[job],'error':str(exc)})
    records.sort(key=lambda r:-r['properties']['density'])
    output={'items':records,'sources':sources,'errors':errors,'adopted':False}
    (ROOT.parent/'coordinate-local-review.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'reviewed_peaks':len(records),'errors':errors}),flush=True)

if __name__=='__main__':main()
