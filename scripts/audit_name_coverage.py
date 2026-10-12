"""Audit coordinate labels/Japan English names; official N03 fallback overlays.

N03 fallback labels describe the municipality of the reference point, not an
exact translation of the GeoNames locality. Density/peak coordinates stay intact.
"""
import io,json,re,sys
from pathlib import Path
from zipfile import ZipFile
from collections import Counter,defaultdict
import shapefile
from shapely import STRtree
from shapely.geometry import shape,Point
from shapely.ops import nearest_points
from pyproj import Geod
from translate_names import save
WORK=Path('data/name-translation/world')

def write_overlay(overrides,coordmap):
    curated=json.loads(Path('docs/japan-name-overrides.json').read_text(encoding='utf-8'))
    combined={**overrides,**curated}
    Path('web/world-name-overrides.js').write_text('Object.assign(window.NIGIWAI_JAPANESE_NAMES.world,'+json.dumps(combined,ensure_ascii=False,separators=(',',':'))+');\nwindow.NIGIWAI_COORDINATE_NAMES = '+json.dumps(coordmap,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

def audit_national():
    root=Path('data/distribution/foursquare-japan')
    manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    total=0;coord=[];roman=[]
    for dataset in manifest['datasets']:
        for f in json.loads((root/dataset['peaks_file']).read_text(encoding='utf-8'))['features']:
            total+=1;name=f['properties'].get('name','')
            record={'dataset':dataset['peaks_file'],'feature':f}
            if re.fullmatch(r'[\d\s.,°NSEW+\-]+',name or 'x'):coord.append(record)
            elif re.search('[A-Za-z]',name):roman.append(record)
    report={'total_peak_records_across_12_datasets':total,'coordinate_only_before':len(coord),'coordinate_missing_municipality':sum(not r['feature']['properties'].get('municipality') for r in coord),'station_or_other_names_with_latin':len(roman)}
    save(WORK/'japan-dataset-coverage.json',{'summary':report,'coordinate_only':coord,'latin_names':roman})
    print(json.dumps(report))

def main():
    geometries=[];attrs=[]
    with ZipFile('data/raw/admin/N03-20260101_GML.zip') as archive:
        base=next(n[:-4] for n in archive.namelist() if n.endswith('.shp') and 'prefecture' not in n)
        encoding=archive.read(base+'.cpg').decode().strip() if base+'.cpg' in archive.namelist() else 'cp932'
        reader=shapefile.Reader(shp=io.BytesIO(archive.read(base+'.shp')),dbf=io.BytesIO(archive.read(base+'.dbf')),encoding=encoding)
        for row in reader.iterShapeRecords():
            p=row.record.as_dict()
            if not p.get('N03_004'):continue
            geometries.append(shape(row.shape.__geo_interface__))
            attrs.append({'prefecture':p['N03_001'],'municipality':p['N03_004']+(p.get('N03_005') or '')})
    tree=STRtree(geometries)
    def locate(coords,allow_near=False):
        x,y=coords
        if not (122<=x<=154 and 20<=y<=46):return None
        hits=tree.query(Point(coords),predicate='intersects')
        if len(hits):return {**attrs[int(hits[0])],'nearby':False}
        if allow_near:
            index=int(tree.nearest(Point(coords)))
            edge=nearest_points(Point(coords),geometries[index])[1]
            if Geod(ellps='WGS84').inv(x,y,edge.x,edge.y)[2]<=1500:
                return {**attrs[index],'nearby':True}
        return None
    refs=json.loads((WORK/'dictionary.json').read_text(encoding='utf-8'))['items']
    mapping=json.loads((WORK/'registered-names.json').read_text(encoding='utf-8'))
    candidates={r['id']:r for r in json.loads((WORK/'all-candidates.json').read_text(encoding='utf-8'))['items']}
    overrides={};jp=[];locale=[]
    for r in refs:
        entry=mapping.get(r['id']);label=entry['name'] if entry else r['original']
        if r['country']=='JP' and re.search('[A-Za-z]',label):
            admin=locate([r['lon'],r['lat']],allow_near=True);record={**r,'display_before':label,'admin':admin}
            jp.append(record)
            if admin and not entry:
                overrides[r['id']]={'name':admin['municipality'],'source':'国土数値情報 N03 / CC BY 4.0','status':'administrative_reference_fallback','basis':('GeoNames参照点から1.5km以内の行政区域名で補完。' if admin['nearby'] else 'GeoNames参照点が属する市区町村名で補完。')+'元の地区名の翻訳ではありません。'}
        if r['country'] in ('KR','CN'):
            proposed=candidates.get(r['id'],{}).get('ja');value=proposed or label
            invalid=bool(re.search('[一-鿿가-힣]',value)) if r['country']=='KR' else (not bool(re.search('[一-鿿]',value)) or bool(re.search('[广门龙东车马风岛阳阴云汉乡县湾边进华庆兴宁黄齐济吴苏郑叶刘赵张陈钟归]',value)))
            if invalid:locale.append({**r,'current_registered_name':entry,'candidate':proposed,'reason':'Korean_requires_katakana' if r['country']=='KR' else 'Chinese_requires_Japanese_kanji'})
    root=Path('data/distribution/foursquare-world');manifest=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
    coordinates=[];missing=[];coordinate_groups=defaultdict(list);total=0
    for package in manifest['packages']:
        fs=json.loads((root/package['id']/'200-all-peaks.json').read_text(encoding='utf-8'))['features']
        for f in fs:
            total+=1;p=f['properties'];ids=p.get('name_source_ids') or []
            coordinate_label=bool(re.fullmatch(r'\s*-?\d+(?:\.\d+)?\s*[,，]\s*-?\d+(?:\.\d+)?\s*',p.get('name','')))
            if p.get('name_source')=='coordinates' or coordinate_label or not p.get('name'):
                admin=locate(f['geometry']['coordinates'])
                record={'package':package['id'],'coordinates':f['geometry']['coordinates'],'properties':p,'admin':admin}
                coordinates.append(record)
                if admin:coordinate_groups[p['name']].append(admin['municipality'])
            elif not ids:
                missing.append({'package':package['id'],'properties':p})
    coordmap={name:{'name':names[0],'source':'国土数値情報 N03 / CC BY 4.0','basis':'峰が属する行政区域の市区町村名'} for name,names in coordinate_groups.items() if len(set(names))==1}
    save(WORK/'coverage-coordinate-peaks.json',{'items':coordinates})
    save(WORK/'coverage-japan-english.json',{'items':jp})
    save(WORK/'coverage-locale-policy.json',{'items':locale})
    save(WORK/'official-name-overrides.json',{'references':overrides,'coordinates':coordmap})
    summary={'world_peaks':total,'coordinate_only':len(coordinates),'coordinate_floor800':sum(r['properties']['density']>=800 for r in coordinates),'coordinate_in_japan_admin':sum(bool(r['admin']) for r in coordinates),'japan_english_references':len(jp),'okinawa_english_references':sum(r['admin'] is not None and r['admin']['prefecture']=='沖縄県' for r in jp),'official_japan_reference_fallbacks':len(overrides),'official_coordinate_labels':len(coordmap),'locale_review':dict(Counter(r['country'] for r in locale)),'noncoordinate_no_source_ids':len(missing)}
    save(WORK/'coverage-summary.json',summary)
    write_overlay(overrides,coordmap)
    print(json.dumps(summary))

if __name__=='__main__':
    if '--overlay-only' in sys.argv:
        saved=json.loads((WORK/'official-name-overrides.json').read_text(encoding='utf-8'))
        write_overlay(saved['references'],saved['coordinates'])
    elif '--national-only' in sys.argv:audit_national()
    else:main()
