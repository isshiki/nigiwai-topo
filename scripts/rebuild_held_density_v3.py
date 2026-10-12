"""Recompute only kernel-affected world chunks into a separate v2 release."""
import json,hashlib,shutil,subprocess,sys,math
from pathlib import Path
import numpy as np
from shapely.geometry import shape,mapping,box
from shapely import make_valid
def load_policy():
    policy_path=Path('docs/held-density-exclusions-v3.json')
    p=json.loads(policy_path.read_text(encoding='utf-8'))
    ids={r['id'] for r in p['records']}
    if len(ids)!=5437 or len(p['records'])!=5437:raise ValueError('Unexpected exclusion population')
    return p,ids,hashlib.sha256(policy_path.read_bytes()).hexdigest()
from global_density import density,DLON,DLAT,GEOD
from global_names import GlobalNamer
from build_global_sample import surface,peak_mask
from build import feature
from prepare_world import connection
from fetch_world import write_json

BUILD=Path('data/world-build/quality-v3')
ROOT=Path('data/distribution/foursquare-world-v3')
OLD=Path('data/distribution/foursquare-world')

def load(path):return json.loads(Path(path).read_text(encoding='utf-8'))

def affected_chunks(records):
    # 200m kernel (800m support), histogram rounding, 400m peak comparison.
    # 0.04 longitude / 0.03 latitude exceed combined support at all 13 sites.
    result=set()
    for record in records:
        lon,lat=record['coordinates']
        for i in range(math.floor((lon-.04+180)/(.45)),math.floor((lon+.04+180)/(.45))+1):
            for j in range(math.floor((lat-.03+90)/(.45)),math.floor((lat+.03+90)/(.45))+1):result.add((i,j))
    return sorted(result)

def main():
    policy,excluded,signature=load_policy()
    source_manifest=load('data/world-build/manifest.json')
    if source_manifest['snapshots']['places']['snapshot_id']!=policy['snapshot_id']:raise ValueError('Snapshot changed')
    BUILD.mkdir(parents=True,exist_ok=True)
    if (BUILD/'state.json').exists() and load(BUILD/'state.json')['policy_sha256']!=signature:raise ValueError('Build policy changed; use a new build directory')
    write_json(BUILD/'state.json',{'policy_sha256':signature,'complete':False})
    tasks=affected_chunks(policy['records']);print('Affected chunks:',len(tasks),flush=True)
    input_file=BUILD/'input.parquet'
    if not input_file.exists():
        clauses=[];params=['data/world-build/active.parquet']
        for i,j in tasks:
            w,s=-180+i*.45,-90+j*.45
            clauses.append('(longitude BETWEEN ? AND ? AND latitude BETWEEN ? AND ?)')
            params += [w-.2,w+.65,s-.08,s+.53]
        with connection() as con:
            con.execute("COPY (SELECT fsq_place_id,longitude,latitude FROM read_parquet(?) WHERE "+' OR '.join(clauses)+") TO '"+input_file.as_posix()+"' (FORMAT PARQUET)",params)
    with connection() as con:rows=con.execute('SELECT * FROM read_parquet(?)',[str(input_file)]).fetchall()
    by_id={r[0]:r for r in rows}
    for r in policy['records']:
        if r['id'] not in by_id or list(by_id[r['id']][1:])!=r['coordinates']:raise ValueError('Excluded ID/coordinate differs from source')
    points=np.asarray([[r[1],r[2]] for r in rows]);keep=np.asarray([r[0] not in excluded for r in rows])
    namer=GlobalNamer();chunks=BUILD/'chunks';chunks.mkdir(exist_ok=True)
    revised_peaks={};checks=[]
    for number,(i,j) in enumerate(tasks,1):
        w,s=-180+i*.45,-90+j*.45;e,n=w+.45,s+.45
        region=(points[:,0]>=w-.2)&(points[:,0]<=e+.2)&(points[:,1]>=s-.08)&(points[:,1]<=n+.08)
        xs,ys,before=density(points[region],i,j,200,padding=64)
        _,_,after=density(points[region&keep],i,j,200,padding=64)
        if np.any(after>before+1e-8):raise ValueError('Density increased after exclusion')
        delta=before-after
        # Every changed cell must be close to a held source coordinate.
        changed=np.argwhere(delta>1e-8)
        held=points[region&~keep]
        if len(changed):
            affected_xy=np.column_stack((xs[changed[:,1]],ys[changed[:,0]]))
            nearest=np.full(len(changed),np.inf)
            for lon,lat in np.unique(held,axis=0):
                distance=GEOD.inv(np.full(len(changed),lon),np.full(len(changed),lat),affected_xy[:,0],affected_xy[:,1])[2]
                nearest=np.minimum(nearest,distance)
            if nearest.max()>1300:raise ValueError('Density changed beyond kernel support')
        original=load(Path('data/world-build/default')/f'{i}-{j}.json')
        for f in original['features']:
            if f['properties']['kind']=='peak':
                lon,lat=f['geometry']['coordinates'];c=int(np.argmin(abs(xs-lon)));r=int(np.argmin(abs(ys-lat)))
                if round(float(before[r,c]))!=f['properties']['density']:raise ValueError('Old summit density not reproduced')
        geo=surface(xs[64:565],ys[64:565],after[64:565,64:565],namer)
        bounds=box(w,s,e,n).buffer(.000002)
        for f in geo['features']:
            if not shape(f['geometry']).is_valid or not bounds.covers(shape(f['geometry'])):raise ValueError('Invalid revised geometry')
        write_json(chunks/f'{i}-{j}.json',geo)
        mask=peak_mask(after,ys)[64:564,64:564]
        revised_peaks[(i,j)]=[feature('Point',[float(xs[c+64]),float(ys[r+64])],kind='peak',density=round(float(after[r+64,c+64])),**namer(float(xs[c+64]),float(ys[r+64]))) for r,c in np.argwhere(mask)]
        checks.append({'chunk':[i,j],'changed_cells':len(changed),'excluded_input_count':int(np.count_nonzero(region&~keep)),'max_reduction':float(delta.max()),'original_density_reproduced':True})
        print('Recomputed',number,'/',len(tasks),i,j,flush=True)
    # Check all 13 original positions, using the same shared lattice and halo.
    target_results=[]
    for target in load('docs/held-peak-display-decisions.json')['items']:
        lon,lat=target['coordinates'];i=int(round((lon+180)/DLON))//500;j=int(round((lat+90)/DLAT))//500
        w,s=-180+i*.45,-90+j*.45
        region=(points[:,0]>=w-.2)&(points[:,0]<=w+.65)&(points[:,1]>=s-.08)&(points[:,1]<=s+.53)
        xs,ys,z=density(points[region&keep],i,j,200,padding=64)
        c=int(np.argmin(abs(xs-lon)));r=int(np.argmin(abs(ys-lat)))
        xx,yy=np.meshgrid(xs,ys);distance=GEOD.inv(np.full(xx.shape,lon),np.full(xx.shape,lat),xx,yy)[2]
        near=distance<=2000
        target_results.append({'peak':target['peak'],'before':target['density'],'after':float(z[r,c]),'max_within_2km':float(z[near].max()),'peaks_800_within_2km':int(np.count_nonzero(peak_mask(z,ys)&near&(z>=800)))})
    if any(r['peaks_800_within_2km'] for r in target_results):raise ValueError('Held artifact still above display threshold')
    # Original production folders remain intact. Unaffected PMTiles copied as-is.
    if not ROOT.exists():shutil.copytree(OLD,ROOT)
    registry=load(OLD/'registry.json');groups={}
    for i,j in tasks:groups.setdefault((i//4,j//4),[]).append((i,j))
    for a,b in groups:
        package=f'global-{a}-{b}';folder=BUILD/'packages'/package;folder.mkdir(parents=True,exist_ok=True)
        source=Path('data/world-build/packages')/package
        manifest=load(source/'manifest.json');item=manifest['datasets'][0]
        overview=[];new_chunks=[]
        for old_chunk in item['chunks']:
            old_path=Path(old_chunk['file']);i,j=map(int,old_path.stem.split('-'))
            path=chunks/old_path.name if (i,j) in revised_peaks else old_path
            geo=load(path)
            new_chunks.append({**old_chunk,'file':str(path.resolve()),'bytes':path.stat().st_size,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
            for f in geo['features']:
                if f['properties']['kind']=='band' and f['properties']['density']>=800:
                    geometry=make_valid(shape(f['geometry']).simplify(.0005,preserve_topology=True))
                    if not geometry.is_empty:overview.append({**f,'geometry':mapping(geometry)})
        old_peaks=load(source/item['peaks_file'])['features']
        taskset=set(tasks)
        peaks=[f for f in old_peaks if (int(round((f['geometry']['coordinates'][0]+180)/DLON))//500,int(round((f['geometry']['coordinates'][1]+90)/DLAT))//500) not in taskset]
        peaks += [f for t in groups[(a,b)] for f in revised_peaks[t]]
        peaks.sort(key=lambda f:-f['properties']['density'])
        if len({tuple(f['geometry']['coordinates']) for f in peaks})!=len(peaks):raise ValueError('Duplicate revised peaks')
        write_json(folder/item['peaks_file'],{'type':'FeatureCollection','features':peaks})
        write_json(folder/item['overview_file'],{'type':'FeatureCollection','features':overview})
        item.update(chunks=new_chunks,peaks=len(peaks),count=source_manifest['count']-len(excluded))
        manifest['input_signature']=signature;manifest['density_quality']={'policy_sha256':signature,'excluded_ids':len(excluded),'status':'reviewed_cluster_hold','reviewed_groups':len(policy['groups'])}
        write_json(folder/'manifest.json',manifest)
        for name in ['stations.json','regions.json']:shutil.copyfile(source/name,folder/name)
        subprocess.run([sys.executable,'scripts/build_pmtiles.py','--input',str(folder),'--output',str(ROOT/package),'--choice','200-all'],check=True)
        from pmtiles.reader import Reader,MmapSource
        archive=ROOT/package/'200-all.pmtiles'
        with archive.open('rb') as f:tiles=Reader(MmapSource(f)).header()['addressed_tiles_count']
        entry=next(r for r in registry['packages'] if r['id']==package)
        entry.update(bytes=archive.stat().st_size,peaks=len(peaks),tiles=tiles)
    validation=load(OLD/'validation.json')
    validation.update(peaks=sum(r['peaks'] for r in registry['packages']),bytes=sum(r['bytes'] for r in registry['packages']),tiles=sum(r['tiles'] for r in registry['packages']),source_count=source_manifest['count']-len(excluded),quality_excluded=len(excluded),quality_reviewed_groups=len(policy['groups']),density_policy_sha256=signature)
    write_json(ROOT/'registry.json',registry);write_json(ROOT/'validation.json',validation)
    report={'complete':True,'snapshot_id':policy['snapshot_id'],'policy_sha256':signature,'excluded_ids':len(excluded),'retained_count':validation['source_count'],'recomputed_chunks':len(tasks),'recomputed_packages':len(groups),'unchanged_packages':len(registry['packages'])-len(groups),'targets':target_results,'checks':checks,'root':str(ROOT)}
    write_json(BUILD/'report.json',report);write_json(Path('docs/held-density-rebuild-v3.json'),report)
    write_json(BUILD/'state.json',{'policy_sha256':signature,'complete':True})
    print('Local corrected world release prepared',flush=True)
if __name__=='__main__':main()
