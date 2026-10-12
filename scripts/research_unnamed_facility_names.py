"""Check nearby gazetteer points against address and facility text.

Research only: proximity or a substring never publishes a name on its own.
"""
import io,json,zipfile,unicodedata,re
from pathlib import Path
from collections import defaultdict,Counter
import duckdb,numpy as np
from scipy.spatial import cKDTree
from pyproj import Geod
from research_coordinate_names import unit

ROOT=Path('data/name-research/unnamed-world')
OUT=ROOT/'facility-review-parts'
GEOD=Geod(ellps='WGS84')

def words(value):
    value=''.join(c for c in unicodedata.normalize('NFKD',value or '').casefold() if not unicodedata.combining(c))
    return ' '+re.sub(r'[^\w]+',' ',value).strip()+' '

def main():
    OUT.mkdir(exist_ok=True)
    targets=json.loads((ROOT/'address-name-review.json').read_text(encoding='utf-8'))['items']
    adopted={p['peak'] for p in json.loads(Path('docs/unnamed-world-name-decisions.json').read_text(encoding='utf-8'))['items']}
    targets=[p for p in targets if p['peak'] not in adopted]
    con=duckdb.connect(config={'threads':2,'memory_limit':'2GB'})
    parts=json.loads(Path('data/raw/foursquare-global/manifest.json').read_text(encoding='utf-8'))['parts']
    pairs=con.execute('SELECT DISTINCT peak,fsq_place_id FROM read_parquet(?)',[[str(ROOT/'local-parts'/p['file']) for p in parts]]).fetchall()
    cursor=con.execute('SELECT * FROM read_parquet(?)',[str(ROOT/'addresses.parquet')]);fields=[c[0] for c in cursor.description]
    pois={r[0]:dict(zip(fields,r)) for r in cursor.fetchall()};near=defaultdict(list);wanted={p['peak']:p for p in targets}
    for peak,pid in pairs:
        if peak not in wanted:continue
        p=pois[pid];lon,lat=wanted[peak]['coordinates'];distance=GEOD.inv(lon,lat,p['longitude'],p['latitude'])[2]
        if distance<=750:near[peak].append({**p,'distance_m':round(distance)})
    groups=defaultdict(list)
    for t in targets:
        codes=Counter(p['country'] for p in near[t['peak']] if p['country'])
        for code,count in codes.items():
            if count>=3:groups[code].append(t)
    sources=[]
    for i,(code,rows) in enumerate(sorted(groups.items())):
        output=OUT/(code+'.json');archive=Path('data/name-research/coordinate-countries')/(code+'.zip')
        if not archive.exists():
            sources.append({'country':code,'status':'missing_gazetteer'});continue
        # Country output is resumable and retains all remaining targets. Adoption
        # later filters records already published rather than mutating evidence.
        if output.exists():
            sources.append({'country':code,'status':'cached'});continue
        places=[]
        with zipfile.ZipFile(archive) as z,z.open(code+'.txt') as stream:
            for line in io.TextIOWrapper(stream,encoding='utf-8'):
                f=line.rstrip('\n').split('\t')
                if len(f)!=19 or f[8]!=code or not ((f[6]=='P' and f[7] not in ('PPLH','PPLQ','PPLW')) or f[7]=='AIRP'):continue
                places.append({'id':f[0],'name':f[1],'ascii':f[2],'lon':float(f[5]),'lat':float(f[4]),'admin1':code+'.'+f[10],'feature_code':f[7]})
        results=[]
        if places:
            tree=cKDTree(unit([p['lon'] for p in places],[p['lat'] for p in places]))
            for t in rows:
                lon,lat=t['coordinates'];indices=tree.query_ball_point(unit([lon],[lat])[0],r=2*np.sin(1500/6371000/2))
                candidates=[]
                for j in indices:
                    ref=places[j];distance=GEOD.inv(lon,lat,ref['lon'],ref['lat'])[2]
                    if distance>1500:continue
                    labels={words(ref['name']),words(ref['ascii'])}
                    labels={v for v in labels if len(re.sub(r'\W','',v))>=4}
                    matches=[]
                    for p in near[t['peak']]:
                        if p['country']!=code:continue
                        fields_matched=[field for field in ['name','address','locality','post_town'] if p.get(field) and any(label in words(p[field]) for label in labels)]
                        if fields_matched:matches.append({'id':p['fsq_place_id'],'name':p['name'],'address':p.get('address'),'locality':p.get('locality'),'fields_matched':fields_matched,'distance_m':p['distance_m'],'coordinates':[p['longitude'],p['latitude']]})
                    if matches:candidates.append({**ref,'reference_distance_m':round(distance),'text_matches':len(matches),'distinct_coordinates':len({tuple(p['coordinates']) for p in matches}),'facility_name_matches':sum('name' in p['fields_matched'] for p in matches),'address_matches':sum('address' in p['fields_matched'] for p in matches),'evidence':matches[:15]})
                candidates.sort(key=lambda r:(-r['text_matches'],r['reference_distance_m']))
                results.append({'peak':t['peak'],'coordinates':t['coordinates'],'density':t['density'],'near_pois':len(near[t['peak']]),'candidates':candidates[:5]})
        output.write_text(json.dumps({'country':code,'source_url':f'https://download.geonames.org/export/dump/{code}.zip','license':'CC BY 4.0','not_adopted':True,'items':results},ensure_ascii=False,indent=2),encoding='utf-8')
        sources.append({'country':code,'status':'complete','peaks':len(results)})
        (ROOT/'facility-progress.json').write_text(json.dumps({'phase':'research','countries_completed':i+1,'countries_total':len(groups),'last_country':code}),encoding='utf-8')
        print(json.dumps(sources[-1]),flush=True)
    combined=defaultdict(list)
    for p in OUT.glob('*.json'):
        for t in json.loads(p.read_text(encoding='utf-8'))['items']:combined[t['peak']].extend(t['candidates'])
    records=[{'peak':t['peak'],'coordinates':t['coordinates'],'candidates':sorted(combined[t['peak']],key=lambda r:(-r['text_matches'],r['reference_distance_m'])),'status':'candidate_needs_review' if combined[t['peak']] else 'no_text_supported_reference'} for t in targets]
    summary={'phase':'complete','remaining_peaks':len(targets),'with_candidate':sum(bool(p['candidates']) for p in records),'sources':sources,'names_published':0,'limits':'Names/addresses are evidence, not administrative containment or verified geocodes; substring matches require individual review.'}
    (ROOT/'facility-name-review.json').write_text(json.dumps({**summary,'items':records},ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'facility-progress.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({k:v for k,v in summary.items() if k!='sources'}),flush=True)

if __name__=='__main__':main()
