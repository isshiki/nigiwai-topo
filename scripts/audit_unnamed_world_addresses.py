"""Research candidate names, without publishing guessed or untranslated labels."""
import io,json,zipfile,urllib.request,hashlib,time
from pathlib import Path
from collections import Counter,defaultdict
from concurrent.futures import ThreadPoolExecutor
import duckdb
from pyproj import Geod
from audit_held_peak_addresses import normalized

ROOT=Path('data/name-research/unnamed-world')
GAZ=Path('data/name-research/coordinate-countries')
GEOD=Geod(ellps='WGS84')

def references(item):
    code,keys=item
    if not isinstance(code,str) or len(code)!=2 or not code.isalpha():return {},{'country':code,'status':'unsupported_country_code'}
    archive=GAZ/(code+'.zip')
    try:
        if not archive.exists():
            url=f'https://download.geonames.org/export/dump/{code}.zip'
            pending=archive.with_suffix('.pending.zip')
            req=urllib.request.Request(url,headers={'User-Agent':'NigiwaiTopo place-name research'})
            with urllib.request.urlopen(req,timeout=90) as response,pending.open('wb') as stream:
                while chunk:=response.read(1024*1024):stream.write(chunk)
            with zipfile.ZipFile(pending) as z:
                if z.testzip():raise ValueError('Corrupt archive')
            pending.replace(archive)
        index=defaultdict(dict)
        with zipfile.ZipFile(archive) as z,z.open(code+'.txt') as stream:
            for line in io.TextIOWrapper(stream,encoding='utf-8'):
                f=line.rstrip('\n').split('\t')
                if len(f)!=19 or f[8]!=code or not (f[6]=='P' and f[7] not in ('PPLH','PPLQ','PPLW') or f[7]=='AIRP'):continue
                for key in ({normalized(v) for v in [f[1],f[2],*f[3].split(',')]} - {''}) & keys:
                    index[key][f[0]]={'id':f[0],'name':f[1],'country':code,'lon':float(f[5]),'lat':float(f[4]),'feature_code':f[7],'source_url':f'https://download.geonames.org/export/dump/{code}.zip'}
        return {k:list(v.values()) for k,v in index.items()},{'country':code,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'status':'complete','license':'CC BY 4.0'}
    except Exception as exc:return {},{'country':code,'status':'failed','error_type':type(exc).__name__}

def main():
    # Can be launched alongside acquisition. Exit visibly on acquisition failure.
    while True:
        meta=json.loads((ROOT/'address-progress.json').read_text(encoding='utf-8')) if (ROOT/'address-progress.json').exists() else {}
        if meta.get('phase')=='complete':break
        if meta.get('status')=='failed':raise RuntimeError('Address acquisition failed; see safe progress file')
        time.sleep(15)
    con=duckdb.connect(config={'threads':2,'memory_limit':'2GB'})
    manifest=json.loads(Path('data/raw/foursquare-global/manifest.json').read_text(encoding='utf-8'))
    parts=[str(ROOT/'local-parts'/p['file']) for p in manifest['parts']]
    pairs=con.execute('SELECT DISTINCT peak,fsq_place_id FROM read_parquet(?)',[parts]).fetchall()
    cursor=con.execute('SELECT * FROM read_parquet(?)',[str(ROOT/'addresses.parquet')]);fields=[c[0] for c in cursor.description]
    pois={r[0]:dict(zip(fields,r)) for r in cursor.fetchall()}
    if len(pois)!=meta['verified_ids']:raise ValueError('Address coverage differs')
    groups=defaultdict(list);keys=defaultdict(set)
    for peak,pid in pairs:
        p=pois[pid];groups[peak].append(p)
        for field in ['locality','post_town']:
            if normalized(p.get(field)):keys[p['country']].add(normalized(p[field]))
    sources=[];index={}
    with ThreadPoolExecutor(max_workers=3) as pool:
        for (code,_),(refs,source) in zip(keys.items(),pool.map(references,keys.items())):
            index[code]=refs;sources.append(source)
            (ROOT/'audit-progress.json').write_text(json.dumps({'phase':'gazetteers','completed':len(sources),'total':len(keys),'last_country':code}),encoding='utf-8')
            print(json.dumps(source),flush=True)
    targets=json.loads((ROOT/'targets.json').read_text(encoding='utf-8'))['items'];records=[];statuses=Counter()
    for t in targets:
        lon,lat=t['coordinates'];near=[]
        for p in groups[t['peak']]:
            d=GEOD.inv(lon,lat,p['longitude'],p['latitude'])[2]
            if d<=750:near.append({**p,'distance_m':round(d)})
        near.sort(key=lambda p:p['distance_m']);votes=Counter();candidates={};far=0
        for p in near:
            found={}
            for field in ['locality','post_town']:
                key=normalized(p.get(field))
                if not key:continue
                for ref in index.get(p['country'],{}).get(key,[]):
                    d=GEOD.inv(lon,lat,ref['lon'],ref['lat'])[2]
                    if d<=2000:found[ref['id']]={**ref,'distance_m':round(d)}
                    elif d>50000:far+=1
            # One POI gets one vote for its closest independently named place.
            if found:
                ref=min(found.values(),key=lambda r:r['distance_m']);votes[ref['id']]+=1;candidates[ref['id']]=ref
        ranked=[{**candidates[rid],'supporting_pois':n,'support_share':round(n/max(len(near),1),3)} for rid,n in votes.most_common(3)]
        winner=ranked[0] if ranked else None
        status='candidate_supported' if winner and winner['supporting_pois']>=3 and winner['support_share']>=.6 and len({(p['longitude'],p['latitude']) for p in near})>=2 else 'candidate_needs_review' if winner else 'facility_or_address_review_required'
        if not near:status='no_pois_within_750m'
        statuses[status]+=1
        record={**t,'status':status,'near_pois':len(near),'with_address':sum(bool(p.get('address')) for p in near),'with_locality':sum(bool(p.get('locality')) for p in near),'distinct_coordinates':len({(p['longitude'],p['latitude']) for p in near}),'locality_counts':Counter(p.get('locality') or '(missing)' for p in near).most_common(8),'candidates':ranked,'distant_alias_matches':far,'samples':near[:12]}
        records.append(record)
    report={'scope':'All 5,356 previously unnamed world peaks','snapshot':meta['snapshot'],'status_counts':dict(statuses),'sources':sources,'rules':{'poi_radius_m':750,'reference_radius_m':2000,'candidate_min_pois':3,'candidate_min_share':.6,'minimum_distinct_coordinates':2},'not_adopted':True,'limits':'Reference points are not administrative polygons. Consensus is a research candidate, not proof of correct POI positions. Source POI text may be stale or wrong. Japanese names require separate source-ID translation and review.','items':records}
    (ROOT/'address-name-review.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    summary={'phase':'complete','peaks':len(records),'status_counts':dict(statuses),'source_failures':[s for s in sources if s['status']!='complete'],'names_published':0}
    (ROOT/'audit-progress.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
