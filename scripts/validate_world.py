"""Check real pilot inputs, clipped geometry, names and exact shard rankings."""
import hashlib
import json
from pathlib import Path
import random
from collections import Counter
from shapely.geometry import shape
from build_peak_index import query_index
from regional_grid import RegionalGrid
from world_names import GEOD


def main():
    report = []
    for region in json.loads(Path('scripts/world-pilots.json').read_text(encoding='utf-8'))['regions']:
        region_id = region['id']
        raw_root = Path('data/raw/foursquare-world')/region_id
        raw = json.loads((raw_root/'manifest.json').read_text(encoding='utf-8'))
        assert raw['complete'] and hashlib.sha256((raw_root/'points.jsonl').read_bytes()).hexdigest() == raw['sha256']
        ids,count,closed,active = set(),0,0,Counter()
        with (raw_root/'points.jsonl').open(encoding='utf-8') as stream:
            for line in stream:
                point = json.loads(line)
                assert point['id'] not in ids
                ids.add(point['id']); count+=1
                if point['date_closed']: closed+=1
                else: active[point['category']]+=1
        assert count==raw['count'] and closed==raw['known_closed'] and dict(active)==raw['active_categories']
        build_root = Path('web/data')/f'foursquare-{region_id}'
        delivery_root = Path('data/distribution')/f'foursquare-{region_id}'
        manifest = json.loads((build_root/'manifest.json').read_text(encoding='utf-8'))
        delivery = json.loads((delivery_root/'manifest.json').read_text(encoding='utf-8'))
        assert len(manifest['datasets'])==len(delivery['datasets'])==12
        clip = shape({'type':'Polygon','coordinates':[[[region['bbox'][0],region['bbox'][1]],[region['bbox'][2],region['bbox'][1]],
              [region['bbox'][2],region['bbox'][3]],[region['bbox'][0],region['bbox'][3]],[region['bbox'][0],region['bbox'][1]]]]})
        rng=random.Random(6)
        features=queries=0
        for d in manifest['datasets']:
            peaks=json.loads((build_root/d['peaks_file']).read_text(encoding='utf-8'))['features']
            assert len(peaks)==d['peaks'] and len({tuple(f['geometry']['coordinates']) for f in peaks})==len(peaks)
            assert all('name_source' in f['properties'] and 'name_basis' in f['properties'] for f in peaks)
            for chunk in d['chunks']:
                geo=json.loads((build_root/chunk['file']).read_text(encoding='utf-8'))
                assert (build_root/chunk['file']).stat().st_size==chunk['bytes']
                for f in geo['features']:
                    geometry=shape(f['geometry'])
                    assert geometry.is_valid and clip.buffer(1e-8).covers(geometry)
                    features+=1
            item=next(i for i in delivery['datasets'] if i['sigma']==d['sigma'] and i['category']==d['category'])
            p=delivery_root/item['peaks_index']
            meta=json.loads(p.read_text(encoding='utf-8'))
            index={'root':meta['root'],'nodes':[json.loads((p.parent/f'{i}.json').read_text(encoding='utf-8')) for i in range(meta['node_count'])]}
            assert meta['count']==len(peaks)
            for _ in range(20):
                w,s,e,n=region['bbox']
                x1,x2=sorted([rng.uniform(w,e),rng.uniform(w,e)])
                y1,y2=sorted([rng.uniform(s,n),rng.uniform(s,n)])
                bbox=[x1,y1,x2,y2]
                for floor in (100,800,1600):
                    actual=query_index(index,bbox,floor=floor)
                    expected=sorted([f for f in peaks if x1<=f['geometry']['coordinates'][0]<=x2 and y1<=f['geometry']['coordinates'][1]<=y2 and f['properties']['density']>=floor],key=lambda f:-f['properties']['density'])[:20]
                    assert [f['properties']['density'] for f in actual]==[f['properties']['density'] for f in expected]
                    queries+=1
        grid=RegionalGrid(*region['center'])
        errors=[]
        for lon in (region['bbox'][0],region['center'][0],region['bbox'][2]):
            for lat in (region['bbox'][1],region['center'][1],region['bbox'][3]):
                x,y=grid.project.transform(lon,lat)
                for dx,dy in [(1000,0),(0,1000)]:
                    lo,la=grid.inverse.transform(x+dx,y+dy)
                    errors.append(abs(GEOD.inv(lon,lat,lo,la)[2]/1000-1))
        assert max(errors)<.01
        report.append({'region':region_id,'input_count':count,'active_with_halo':count-closed,'geometry_features':features,
            'rank_queries':queries,'max_sampled_1km_distance_error_percent':max(errors)*100,
            'distribution_bytes':sum(p.stat().st_size for p in delivery_root.rglob('*') if p.is_file()),
            'build_seconds':manifest['build_seconds']})
        print(region_id,'validated',features,'features and',queries,'rankings',flush=True)
    Path('data/validation/world-summary.json').write_text(json.dumps(report,indent=2),encoding='utf-8')


if __name__ == '__main__':
    main()
