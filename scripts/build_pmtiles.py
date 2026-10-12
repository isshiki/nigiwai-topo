"""Convert national contours to PMTiles v3 on Windows, preserving density values."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import sqlite3

import mapbox_vector_tile
import mercantile
from pmtiles.writer import write
from pmtiles.tile import Compression, TileType, zxy_to_tileid
from pyproj import Transformer
from shapely.geometry import shape, box
from shapely.ops import transform
from shapely import STRtree, make_valid

PROJECT = Transformer.from_crs(4326, 3857, always_xy=True).transform


def parts(geometry):
    if geometry.is_empty:
        return
    if geometry.geom_type == 'GeometryCollection':
        for child in geometry.geoms:
            yield from parts(child)
    elif geometry.geom_type in ('Polygon', 'MultiPolygon', 'LineString', 'MultiLineString'):
        yield geometry


def encode_tile(tile, geometries, properties, tree):
    bounds = mercantile.xy_bounds(tile)
    unit = (bounds.right - bounds.left) / 4096
    clip = box(bounds.left-8*unit, bounds.bottom-8*unit, bounds.right+8*unit, bounds.top+8*unit)
    features = []
    for index in sorted(tree.query(clip)):
        geom = geometries[index].intersection(clip).simplify(unit*.5, preserve_topology=True)
        for component in parts(geom):
            if component.geom_type in ('Polygon', 'MultiPolygon') and component.area < unit**2:
                continue
            features.append({'geometry':component, 'properties':properties[index]})
    if not features:
        return None
    payload = mapbox_vector_tile.encode({'name':'density', 'features':features},
        default_options={'quantize_bounds':tuple(bounds), 'extents':4096})
    return gzip.compress(payload, mtime=0)


def load(path, geometries, properties):
    data = json.loads(path.read_text(encoding='utf-8'))
    for feature in data['features']:
        p = feature['properties']
        if p['kind'] == 'peak':
            continue
        geom = transform(PROJECT, make_valid(shape(feature['geometry'])))
        for component in parts(geom):
            geometries.append(component)
            properties.append({k:p[k] for k in ['kind','density','index'] if k in p})


def cache_signature(manifest,item,maxzoom):
    identity={'item':item,'maxzoom':maxzoom,'algorithm':1}
    if (manifest.get('pilot') or manifest.get('world')) and manifest.get('input_signature'):
        identity.update(region=manifest['region_id'],input=manifest['input_signature'])
    return hashlib.sha256(json.dumps(identity,sort_keys=True).encode()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=Path('web/data/foursquare-japan'))
    parser.add_argument('--output', type=Path, default=Path('data/distribution/foursquare-japan'))
    parser.add_argument('--maxzoom', type=int, default=12)
    parser.add_argument('--choice', help='e.g. 200-all (default: all nine)')
    args = parser.parse_args()
    manifest = json.loads((args.input/'manifest.json').read_text(encoding='utf-8'))
    args.output.mkdir(parents=True, exist_ok=True)
    delivery = {k:v for k,v in manifest.items() if k != 'datasets'}
    delivery['datasets'] = []
    delivery['delivery'] = 'pmtiles-v3'
    for item in manifest['datasets']:
        choice = f"{item['sigma']}-{item['category']}"
        archive = args.output / f'{choice}.pmtiles'
        signature = cache_signature(manifest,item,args.maxzoom)
        cache_path = Path('data/cache/pmtiles')/f'{choice}-{signature[:16]}.sqlite'
        cache_path.parent.mkdir(parents=True,exist_ok=True)
        if not args.choice or args.choice == choice:
            con = sqlite3.connect(cache_path)
            con.execute('CREATE TABLE IF NOT EXISTS tiles (id INTEGER PRIMARY KEY, payload BLOB)')
            con.execute('CREATE TABLE IF NOT EXISTS completed (zoom INTEGER PRIMARY KEY)')
            for overview in [True, False]:
                zooms = range(3,9) if overview else range(9,args.maxzoom+1)
                todo = [z for z in zooms if not con.execute('SELECT 1 FROM completed WHERE zoom=?',(z,)).fetchone()]
                if not todo:
                    continue
                geometries, properties = [], []
                paths = [item['overview_file']] if overview else [c['file'] for c in item['chunks']]
                for path in paths:
                    load(args.input/path,geometries,properties)
                tree = STRtree(geometries)
                for z in todo:
                    tiles = set()
                    for geom in geometries:
                        # Candidate tiles from geographic bounds, after inverse projection.
                        b = transform(Transformer.from_crs(3857,4326,always_xy=True).transform,geom).bounds
                        tiles.update(mercantile.tiles(*b,z))
                    for tile in sorted(tiles, key=lambda t:zxy_to_tileid(t.z,t.x,t.y)):
                        payload = encode_tile(tile,geometries,properties,tree)
                        if payload:
                            con.execute('INSERT OR REPLACE INTO tiles VALUES (?,?)',(zxy_to_tileid(z,tile.x,tile.y),payload))
                    con.execute('INSERT INTO completed VALUES (?)',(z,))
                    con.commit()
                    print(choice, 'zoom',z,'candidate tiles',len(tiles),flush=True)
            tile_count = con.execute('SELECT count(*) FROM tiles').fetchone()[0]
            no_density = tile_count == 0 or (tile_count == 1 and not mapbox_vector_tile.decode(gzip.decompress(con.execute('SELECT payload FROM tiles LIMIT 1').fetchone()[0]))['density']['features'])
            if tile_count == 0:
                # pmtiles-python requires one tile entry. An explicit empty MVT
                # is transparent, and distinguishes zero density from failure.
                lon,lat = (manifest['bbox'][0]+manifest['bbox'][2])/2,(manifest['bbox'][1]+manifest['bbox'][3])/2
                tile = mercantile.tile(lon,lat,args.maxzoom)
                payload = gzip.compress(mapbox_vector_tile.encode({'name':'density','features':[]}),mtime=0)
                con.execute('INSERT INTO tiles VALUES (?,?)',(zxy_to_tileid(tile.z,tile.x,tile.y),payload))
                con.commit()
            with write(str(archive)+'.tmp') as writer:
                for tileid, payload in con.execute('SELECT id,payload FROM tiles ORDER BY id'):
                    writer.write_tile(tileid,payload)
                bbox = manifest['bbox']
                writer.finalize({'tile_type':TileType.MVT, 'tile_compression':Compression.GZIP,
                    'min_zoom':3, 'max_zoom':args.maxzoom, 'min_lon_e7':round(bbox[0]*1e7),
                    'min_lat_e7':round(bbox[1]*1e7), 'max_lon_e7':round(bbox[2]*1e7), 'max_lat_e7':round(bbox[3]*1e7),
                    'center_zoom':5, 'center_lon_e7':round((bbox[0]+bbox[2])/2*1e7), 'center_lat_e7':round((bbox[1]+bbox[3])/2*1e7)},
                    {'name':choice, 'empty_density':no_density, 'attribution':'© 2026 Foursquare Labs, Inc. / Apache 2.0; modified density contours',
                     'license':'Apache-2.0', 'notice':Path('web/licenses/Foursquare-NOTICE.txt').read_text(encoding='utf-8'),
                     'vector_layers':[{'id':'density','fields':{'kind':'String','density':'Number','index':'Boolean'}}]})
            Path(str(archive)+'.tmp').replace(archive)
            con.close()
            print(choice,'archive bytes',archive.stat().st_size,flush=True)
        if archive.exists():
            peaks = json.loads((args.input/item['peaks_file']).read_text(encoding='utf-8'))
            # Keep accurate peak coordinates and naming provenance for viewport ranking.
            (args.output/item['peaks_file']).write_text(json.dumps(peaks,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
            entry = {k:item[k] for k in ['sigma','category','status','count','peaks','peaks_file']} | {'pmtiles_file':archive.name,'bytes':archive.stat().st_size}
            if manifest.get('pilot') or manifest.get('world'):
                from pmtiles.reader import Reader, MmapSource
                with archive.open('rb') as stream:
                    entry['empty_density'] = Reader(MmapSource(stream)).metadata().get('empty_density',False)
                from build_peak_index import write_index
                index_folder = f'{choice}-peak-index'
                write_index(peaks['features'],args.output/index_folder)
                entry['peaks_index'] = f'{index_folder}/index.json'
            if 'core_count' in item:
                entry['core_count'] = item['core_count']
            delivery['datasets'].append(entry)
    for name in ['stations.json','regions.json']:
        (args.output/name).write_bytes((args.input/name).read_bytes())
    for name in ['Foursquare-NOTICE.txt','Apache-2.0.txt']:
        (args.output/name).write_bytes((Path('web/licenses')/name).read_bytes())
    if manifest.get('world'):
        (args.output/'World-Names-NOTICE.txt').write_bytes(Path('web/licenses/World-Names-NOTICE.txt').read_bytes())
        (args.output/'OSM-NOTICE.txt').write_bytes(Path('web/licenses/OSM-NOTICE.txt').read_bytes())
    if manifest.get('reference_names'):
        (args.output/'places.json').write_bytes((args.input/'places.json').read_bytes())
        (args.output/'OSM-NOTICE.txt').write_bytes(Path('web/licenses/OSM-NOTICE.txt').read_bytes())
    (args.output/'manifest.json').write_text(json.dumps(delivery,ensure_ascii=False,separators=(',',':')),encoding='utf-8')


if __name__ == '__main__':
    main()
