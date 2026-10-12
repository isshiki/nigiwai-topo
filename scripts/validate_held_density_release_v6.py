"""Verify unchanged archives and real MVT terrain at all 13 held summit points."""
import gzip,hashlib,json
from pathlib import Path
import mercantile,mapbox_vector_tile
from shapely.geometry import shape,Point
from pyproj import Transformer
from pmtiles.reader import Reader,MmapSource,all_tiles
from pmtiles.tile import Compression,TileType
from rebuild_held_density_v6 import load_policy
from rebuild_held_density import affected_chunks
from fetch_world import write_json

ROOT=Path('data/distribution/foursquare-world-v6');OLD=Path('data/distribution/foursquare-world-v5')
PROJECT=Transformer.from_crs(4326,3857,always_xy=True).transform
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def band_at(path,lon,lat,zoom):
    tile=mercantile.tile(lon,lat,zoom);b=mercantile.xy_bounds(tile);x,y=PROJECT(lon,lat)
    point=Point((x-b.left)/(b.right-b.left)*4096,(y-b.bottom)/(b.top-b.bottom)*4096)
    with path.open('rb') as f:payload=Reader(MmapSource(f)).get(tile.z,tile.x,tile.y)
    if not payload:return 0
    features=mapbox_vector_tile.decode(gzip.decompress(payload))['density']['features']
    return max([p['properties']['density'] for p in features if p['properties']['kind']=='band' and shape(p['geometry']).covers(point)]+[0])
def main():
    policy,ids,signature=load_policy();report=json.loads(Path('docs/held-density-rebuild-v6.json').read_text(encoding='utf-8'))
    assert report['complete'] and report['policy_sha256']==signature and report['excluded_ids']==len(ids)
    old_policy=json.loads(Path('docs/held-density-exclusions-v5.json').read_text(encoding='utf-8'));old_ids={r['id'] for r in old_policy['records']};delta=[r for r in policy['records'] if r['id'] not in old_ids];assert len(delta)==4;changed={f'global-{i//4}-{j//4}' for i,j in affected_chunks(delta)}
    manifest=json.loads((ROOT/'manifest.json').read_text(encoding='utf-8'))
    assert manifest['density_quality']['policy_sha256']==signature
    assert manifest['datasets'][0]['count']==101734535-len(ids)
    unchanged=tiles=0
    for package in manifest['packages']:
        path=ROOT/package['pmtiles']
        if package['id'] not in changed:
            assert sha(path)==sha(OLD/package['pmtiles']);unchanged+=1
        else:
            with path.open('rb') as f:
                source=MmapSource(f);reader=Reader(source)
                assert reader.header()['tile_type']==TileType.MVT and reader.header()['tile_compression']==Compression.GZIP
                count=0
                for (z,x,y),payload in all_tiles(source):
                    features=mapbox_vector_tile.decode(gzip.decompress(payload))['density']['features']
                    assert all(p['properties']['kind'] in ('band','contour') and p['properties']['density']>=100 for p in features)
                    if z<9:assert all(p['properties']['kind']=='band' and p['properties']['density']>=800 for p in features)
                    count+=1
                assert count==reader.header()['addressed_tiles_count'];tiles+=count
    assert unchanged==report['unchanged_packages']
    results=[]
    for target in json.loads(Path('docs/held-peak-display-decisions.json').read_text(encoding='utf-8'))['items']:
        lon,lat=target['coordinates']
        old_package=next(p for p in manifest['packages'] if p['bbox'][0]<=lon<=p['bbox'][2] and p['bbox'][1]<=lat<=p['bbox'][3])
        before=band_at(Path('data/distribution/foursquare-world')/old_package['pmtiles'],lon,lat,12)
        after=band_at(ROOT/old_package['pmtiles'],lon,lat,12)
        overview=band_at(ROOT/'overview.pmtiles',lon,lat,8)
        assert before>=800 and after<100 and overview<800,(target['peak'],before,after,overview)
        results.append({'peak':target['peak'],'old_detail_band':before,'new_detail_band':after,'new_overview_band':overview})
    from pyproj import Geod
    geod=Geod(ellps='WGS84')
    index=json.loads((ROOT/'world-peak-index/index.json').read_text())
    total=0;near=[];sapezal_near=[]
    for node_id in range(index['node_count']):
        node=json.loads((ROOT/f'world-peak-index/{node_id}.json').read_text(encoding='utf-8'))
        for feature in node.get('features',[]):
            total+=1
            lon,lat=feature['geometry']['coordinates']
            if geod.inv(-104.807,53.491,lon,lat)[2]<=1000:near.append(feature)
            if geod.inv(-58.764,-12.989,lon,lat)[2]<=1000:sapezal_near.append(feature)
    assert not near, 'Smeaton peak remains in assembled index'
    assert not sapezal_near, 'Sapezal coarse-coordinate artifact remains in assembled index'
    assert total==manifest['datasets'][0]['peaks']==json.loads((ROOT/'validation.json').read_text())['peaks']
    result={'complete':True,'policy_sha256':signature,'unchanged_archive_sha256_matches':unchanged,'changed_packages':len(changed),'decoded_changed_tiles':tiles,'target_mvt_results':results,'smeaton_peaks_within_1km':len(near),'sapezal_peaks_within_1km':len(sapezal_near),'all_index_leaf_peaks':total}
    write_json(Path('data/validation/held-density-release-v6.json'),result)
    print(json.dumps({'complete':True,'unchanged':unchanged,'changed':len(changed),'target_points':len(results),'tiles':tiles}),flush=True)
if __name__=='__main__':main()
