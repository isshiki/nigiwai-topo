"""One-shot pipeline continuation after contour packing and peak correction."""
import gzip
import json
from pathlib import Path
import subprocess
import sys
import time
import mapbox_vector_tile
from pmtiles.reader import Reader,MmapSource,all_tiles
from pmtiles.tile import TileType,Compression
from fetch_world import write_json


def complete(path):
    if not path.exists(): return False
    return bool(json.loads(path.read_text(encoding='utf-8')).get('complete'))


def main():
    root=Path('data/distribution/foursquare-world')
    deadline=time.monotonic()+72*3600
    dependencies=[Path('data/world-build/peak-repair/progress.json'),root/'progress.json']
    print('Waiting for boundary peak correction and initial PMTiles conversion',flush=True)
    while not all(complete(p) for p in dependencies):
        if time.monotonic()>deadline: raise RuntimeError('World pipeline dependencies did not finish in 72 hours')
        time.sleep(30)
    subprocess.run([sys.executable,'scripts/prepare_world_packages.py','--package-only'],check=True)
    # Existing density archives are retained; peak lists/indexes/notices refreshed.
    subprocess.run([sys.executable,'scripts/build_world_pmtiles.py'],check=True)
    registry=json.loads(Path('data/world-build/packages/registry.json').read_text(encoding='utf-8'))
    rows=[]
    for number,entry in enumerate(registry,1):
        folder=root/entry['id'];manifest=json.loads((folder/'manifest.json').read_text(encoding='utf-8'))
        item=manifest['datasets'][0];path=folder/item['pmtiles_file']
        if path.stat().st_size!=item['bytes']: raise ValueError('Archive size mismatch')
        peakfile=folder/item['peaks_file']
        peaks=json.loads(peakfile.read_text(encoding='utf-8'))['features']
        original=json.loads((Path(entry['input'])/item['peaks_file']).read_text(encoding='utf-8'))['features']
        if peaks!=original or len(peaks)!=item['peaks']: raise ValueError('Peak delivery mismatch')
        with path.open('rb') as stream:
            source=MmapSource(stream);reader=Reader(source);header=reader.header()
            if header['tile_type']!=TileType.MVT or header['tile_compression']!=Compression.GZIP:
                raise ValueError('Unexpected PMTiles format')
            if 'Foursquare' not in reader.metadata()['notice']: raise ValueError('Missing source notice')
            tiles=0
            for coord,payload in all_tiles(source):
                raw=gzip.decompress(payload)
                if tiles%100==0:
                    features=mapbox_vector_tile.decode(raw)['density']['features']
                    if any(f['properties']['kind'] not in ('band','contour') or f['properties']['density']<100 for f in features):
                        raise ValueError('Invalid density tile')
                    if coord[0]<9 and any(f['properties']['kind']!='band' or f['properties']['density']<800 for f in features):
                        raise ValueError('Invalid overview tile')
                tiles+=1
            if tiles!=header['addressed_tiles_count']: raise ValueError('PMTiles count mismatch')
        rows.append({'id':entry['id'],'bbox':entry['bbox'],'pmtiles':entry['id']+'/'+item['pmtiles_file'],
            'peaks_index':entry['id']+'/'+item['peaks_index'],'bytes':path.stat().st_size,'tiles':tiles,'peaks':len(peaks)})
        if number%100==0: print('World delivery validation',number,'/',len(registry),flush=True)
    write_json(root/'registry.json',{'condition':{'sigma':200,'category':'all'},'packages':rows})
    write_json(root/'validation.json',{'complete':True,'archives':len(rows),'bytes':sum(r['bytes'] for r in rows),
        'tiles':sum(r['tiles'] for r in rows),'peaks':sum(r['peaks'] for r in rows),
        'names':'nearby city/town, cached stations preferred; translation deferred',
        'publication':'not uploaded; browser/global overview integration pending'})
    print('World default delivery prepared and locally validated',flush=True)


if __name__=='__main__': main()
