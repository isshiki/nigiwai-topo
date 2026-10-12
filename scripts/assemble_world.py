"""Assemble global overview and exact viewport peak index from validated shards."""
import argparse,gzip,json,sqlite3
from pathlib import Path
import mapbox_vector_tile as mvt
from pmtiles.reader import MmapSource,all_tiles
from pmtiles.writer import write
from pmtiles.tile import Compression,TileType,zxy_to_tileid,tileid_to_zxy
from build_peak_index import write_index
ROOT=Path('data/distribution/foursquare-world')
def main():
    global ROOT
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,default=ROOT)
    parser.add_argument('--database',type=Path,default=Path('data/world-build/overview.sqlite'))
    args=parser.parse_args();ROOT=args.root
    validation=json.loads((ROOT/'validation.json').read_text(encoding='utf-8'))
    assert validation['complete']
    registry=json.loads((ROOT/'registry.json').read_text(encoding='utf-8'))['packages']
    args.database.parent.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect(args.database)
    db.execute('DROP TABLE IF EXISTS fragments')
    db.execute('CREATE TABLE fragments (id INTEGER, payload BLOB)')
    peaks=[]
    for i,entry in enumerate(registry,1):
        folder=ROOT/entry['id']
        with (ROOT/entry['pmtiles']).open('rb') as f:
            for coord,payload in all_tiles(MmapSource(f)):
                if coord[0]<=8: db.execute('INSERT INTO fragments VALUES (?,?)',(zxy_to_tileid(*coord),payload))
        peaks.extend(json.loads((folder/'200-all-peaks.json').read_text(encoding='utf-8'))['features'])
        if i%200==0: db.commit();print('Overview inputs',i,flush=True)
    db.commit();db.execute('CREATE INDEX IF NOT EXISTS fragments_id ON fragments(id)')
    # Derive z0..2 from z3 geometry in tile coordinates (decode uses y-up).
    coarse={}
    from shapely.geometry import shape,mapping
    from shapely.affinity import affine_transform
    for tileid,payload in list(db.execute('SELECT id,payload FROM fragments')):
        z,x,y=tileid_to_zxy(tileid)
        if z!=3: continue
        features=mvt.decode(gzip.decompress(payload))['density']['features']
        for parentz in range(3):
            scale=2**(3-parentz);parentid=zxy_to_tileid(parentz,x//scale,y//scale)
            bucket=coarse.setdefault(parentid,[])
            for f in features:
                geom=affine_transform(shape(f['geometry']),[1/scale,0,0,1/scale,(x%scale)*4096/scale,(scale-1-y%scale)*4096/scale]).simplify(.5,preserve_topology=True)
                if not geom.is_empty: bucket.append({'geometry':mapping(geom),'properties':f['properties']})
    for tileid,features in coarse.items():db.execute('INSERT INTO fragments VALUES (?,?)',(tileid,gzip.compress(mvt.encode({'name':'density','features':features}),mtime=0)))
    db.commit()
    with write(str(ROOT/'overview.pmtiles.tmp')) as writer:
        for (tileid,) in db.execute('SELECT DISTINCT id FROM fragments ORDER BY id'):
            features=[];seen=set()
            for (payload,) in db.execute('SELECT payload FROM fragments WHERE id=?',(tileid,)):
                for feature in mvt.decode(gzip.decompress(payload))['density']['features']:
                    key=json.dumps([feature['geometry'],feature['properties']],sort_keys=True)
                    if key not in seen: seen.add(key);features.append(feature)
            if features:
                writer.write_tile(tileid,gzip.compress(mvt.encode({'name':'density','features':features}),mtime=0))
        writer.finalize({'tile_type':TileType.MVT,'tile_compression':Compression.GZIP,'min_zoom':0,'max_zoom':8,
            'min_lon_e7':-1800000000,'max_lon_e7':1800000000,'min_lat_e7':-850500000,'max_lat_e7':850500000,
            'center_zoom':3,'center_lon_e7':0,'center_lat_e7':200000000},
            {'name':'World density overview','attribution':'© 2026 Foursquare Labs, Inc. / Apache 2.0',
             'notice':Path('web/licenses/Foursquare-NOTICE.txt').read_text(encoding='utf-8'),
             'vector_layers':[{'id':'density','fields':{'kind':'String','density':'Number'}}]})
    (ROOT/'overview.pmtiles.tmp').replace(ROOT/'overview.pmtiles')
    assert len(peaks)==validation['peaks']
    write_index(peaks,ROOT/'world-peak-index')
    sample=json.loads((ROOT/registry[0]['id']/'manifest.json').read_text(encoding='utf-8'))
    sample.update(region_id='world',bbox=[-180,-85.05,180,85.05],coverage='世界（極域を除く）',station_groups=0,
        packages=registry,reference_names=False)
    sample['datasets']=[dict(sigma=200,category='all',status='exclude',count=validation.get('source_count',101734535),peaks=len(peaks),
        pmtiles_file='overview.pmtiles',peaks_index='world-peak-index/index.json')]
    if validation.get('quality_excluded'):
        sample['density_quality']={'excluded_ids':validation['quality_excluded'],'policy_sha256':validation['density_policy_sha256'],'status':'reviewed_cluster_hold','notice_file':'Density-Quality-NOTICE.txt'}
    (ROOT/'manifest.json').write_text(json.dumps(sample,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
    regions={'world':{'name':'世界全域','bbox':sample['bbox']}}
    for id,name,bbox in [('asia','アジア',[25,-10,150,65]),('europe','ヨーロッパ',[-25,34,45,71]),('africa','アフリカ',[-20,-35,55,37]),('north-america','北米',[-170,7,-50,75]),('south-america','南米',[-82,-56,-34,13]),('oceania','オセアニア',[110,-48,180,0])]:regions[id]={'name':name,'bbox':bbox}
    (ROOT/'regions.json').write_text(json.dumps(regions,ensure_ascii=False),encoding='utf-8')
    (ROOT/'stations.json').write_text('[]')
    import shutil
    for name in ['Foursquare-NOTICE.txt','Apache-2.0.txt','World-Names-NOTICE.txt','OSM-NOTICE.txt']:shutil.copyfile(Path('web/licenses')/name,ROOT/name)
    if validation.get('quality_excluded'):
        notice=('Location quality processing / 2026-10-10\n'+str(validation['quality_excluded'])+' snapshot-pinned POI IDs in '+str(validation.get('quality_reviewed_groups',13))+' individually reviewed groups are withheld from density calculation. This is a conservative quality hold, not proof every record is wrong. Raw source retained; genuine local registrations with poor address evidence may be omitted. No POI relocated. Density remains registration density, not footfall.\nPolicy SHA256: '+validation['density_policy_sha256']+'\n')
        (ROOT/'Density-Quality-NOTICE.txt').write_text(notice,encoding='utf-8')
        with (ROOT/'Foursquare-NOTICE.txt').open('a',encoding='utf-8') as f:f.write('\n'+notice)
    print('World frontend assets complete',flush=True)
if __name__=='__main__':main()
