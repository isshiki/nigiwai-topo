"""Validate all archives and accurate peak lists, optionally test HTTP ranges."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import urllib.request

import mapbox_vector_tile
from pmtiles.reader import Reader, MmapSource, all_tiles
from pmtiles.tile import Compression, TileType


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',type=Path,default=Path('data/distribution/foursquare-japan'))
    parser.add_argument('--http-base',help='e.g. http://127.0.0.1:8820/tiles/foursquare-japan/')
    parser.add_argument('--original',type=Path,default=Path('web/data/foursquare-japan'))
    args=parser.parse_args()
    manifest=json.loads((args.input/'manifest.json').read_text(encoding='utf-8'))
    if manifest.get('world'):
        assert {(d['sigma'],d['category']) for d in manifest['datasets']} == {(200,'all')}
    else:
        assert len(manifest['datasets']) in (9,12)
    categories = ['all','food','shopping'] + (['service'] if len(manifest['datasets']) == 12 else [])
    if not manifest.get('world'):
        assert {(d['sigma'],d['category']) for d in manifest['datasets']} == {(s,c) for s in (200,400,800) for c in categories}
    rows=[]
    for item in manifest['datasets']:
        path=args.input/item['pmtiles_file']
        assert path.stat().st_size==item['bytes']
        peaks=json.loads((args.input/item['peaks_file']).read_text(encoding='utf-8'))['features']
        assert len(peaks)==item['peaks']
        original=args.original/item['peaks_file']
        assert peaks==json.loads(original.read_text(encoding='utf-8'))['features']
        with path.open('rb') as stream:
            source=MmapSource(stream)
            reader=Reader(source)
            header=reader.header()
            assert header['tile_type']==TileType.MVT
            assert header['tile_compression']==Compression.GZIP
            assert 3 <= header['min_zoom'] <= header['max_zoom'] <= 12
            assert 'Foursquare' in reader.metadata()['notice']
            tiles=0
            for coord,payload in all_tiles(source):
                uncompressed=gzip.decompress(payload)
                assert uncompressed
                if tiles % 100 == 0:
                    decoded=mapbox_vector_tile.decode(uncompressed)['density']['features']
                    assert decoded or item.get('empty_density')
                    assert all(f['properties']['kind'] in ['band','contour'] and f['properties']['density']>=100 for f in decoded)
                    if coord[0]<9:
                        assert all(f['properties']['kind']=='band' and f['properties']['density']>=800 for f in decoded)
                tiles+=1
            assert tiles==header['addressed_tiles_count']
        if args.http_base:
            url=args.http_base+item['pmtiles_file']
            request=urllib.request.Request(url,headers={'Range':'bytes=0-126','Origin':'https://example.github.io'})
            with urllib.request.urlopen(request) as response:
                assert response.status==206
                assert response.headers['Content-Range']==f'bytes 0-126/{path.stat().st_size}'
                assert response.headers['Access-Control-Allow-Origin']
                assert response.headers['ETag']
                assert response.read()==path.read_bytes()[:127]
        rows.append({'file':path.name,'bytes':path.stat().st_size,'tiles':tiles,'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
    output=Path('data/validation/pmtiles-summary.json')
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps({'archives':rows,'pmtiles_bytes':sum(r['bytes'] for r in rows)},indent=2),encoding='utf-8')
    print('Validated',len(rows),'archives;',sum(r['tiles'] for r in rows),'tiles;',sum(r['bytes'] for r in rows),'archive bytes; peak lists identical')


if __name__ == '__main__':
    main()
