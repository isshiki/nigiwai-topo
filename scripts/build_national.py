"""Build resumable 50km density chunks with shared grid and 4-sigma halos."""
import argparse
import hashlib
import json
from pathlib import Path
import time

import contourpy
import duckdb
import numpy as np
from scipy.ndimage import gaussian_filter, maximum_filter
from scipy.spatial import cKDTree
from shapely.geometry import shape, mapping
from shapely import make_valid

try:
    from .build import LEVELS, feature
    from .national_grid import PROJECT, INVERSE, SIZE, CRS, tile_bbox
except ImportError:
    from build import LEVELS, feature
    from national_grid import PROJECT, INVERSE, SIZE, CRS, tile_bbox

STEP = 100


def geographic(ring, inverse=INVERSE):
    lon, lat = inverse.transform(ring[:, 0], ring[:, 1])
    return np.column_stack([lon, lat]).round(6).tolist()


def tile_density(points, i, j, sigma):
    halo = int(np.ceil(4 * sigma / STEP)) + 5
    xs = np.arange(i * SIZE - halo * STEP, (i + 1) * SIZE + (halo + 1) * STEP, STEP)
    ys = np.arange(j * SIZE - halo * STEP, (j + 1) * SIZE + (halo + 1) * STEP, STEP)
    hist = np.histogram2d([p['y'] for p in points], [p['x'] for p in points],
                          bins=(np.r_[ys - STEP / 2, ys[-1] + STEP / 2], np.r_[xs - STEP / 2, xs[-1] + STEP / 2]))[0]
    z = gaussian_filter(hist, sigma / STEP, mode='constant', truncate=4) * 1e6 / STEP**2
    maxima = (z == maximum_filter(z, size=9)) & (z >= 50)
    core = slice(halo, len(xs) - halo)
    return xs[core], ys[core], z[core, core], maxima[core, core]


def surface(points, i, j, sigma, station_tree, stations, *, inverse=INVERSE, namer=None):
    xs, ys, z, maxima = tile_density(points, i, j, sigma)
    contour = contourpy.contour_generator(x=xs, y=ys, z=z, fill_type='OuterOffset', line_type='Separate')
    features = []
    levels = LEVELS + [max(64000, float(z.max()) + 1)]
    for low, high in zip(levels[:-1], levels[1:]):
        rings, offsets = contour.filled(low, high)
        for ring, cuts in zip(rings, offsets):
            features.append(feature('Polygon', [geographic(ring[a:b], inverse) for a, b in zip(cuts[:-1], cuts[1:])], kind='band', density=low))
    for level in LEVELS:
        for line in contour.lines(level):
            features.append(feature('LineString', geographic(line, inverse), kind='contour', density=level, index=level in [1000, 2000, 4000, 8000, 16000, 32000]))
    # Half-open ownership avoids duplicate peaks at shared chunk edges.
    for row, col in np.argwhere(maxima[:-1, :-1]):
        lon, lat = inverse.transform(xs[col], ys[row])
        if namer is not None:
            features.append(feature('Point', [lon, lat], kind='peak', density=round(float(z[row, col])), **namer(lon, lat)))
            continue
        distance, index = station_tree.query([xs[col], ys[row]])
        station = stations[index]
        named = distance <= 1500
        name = station['name'] if named else f'{lat:.2f}°N {lon:.2f}°E'
        features.append(feature('Point', [lon, lat], kind='peak', density=round(float(z[row, col])), name=name,
            nearest_station=station['name'], station_distance_m=round(distance),
            name_basis='近隣駅（峰の座標は駅と異なる）' if named else '近隣駅が1.5km以内にないため座標表示'))
    return {'type': 'FeatureCollection', 'features': features}


def compact_write(path, value):
    temporary = path.with_suffix('.pending')
    temporary.write_text(json.dumps(value, ensure_ascii=False, separators=(',', ':')), encoding='utf-8')
    temporary.replace(path)


def sanitize_geo(geo):
    """Repair sub-metre rounding artefacts, retaining polygonal components only."""
    result, repaired = [], 0
    def polygons(geometry):
        if geometry.geom_type == 'Polygon':
            return [geometry] if not geometry.is_empty else []
        if hasattr(geometry, 'geoms'):
            return [p for g in geometry.geoms for p in polygons(g)]
        return []
    for f in geo['features']:
        if f['properties']['kind'] != 'band' or shape(f['geometry']).is_valid:
            result.append(f)
            continue
        repaired += 1
        parts = polygons(make_valid(shape(f['geometry'])))
        if parts:
            geometry = mapping(parts[0]) if len(parts) == 1 else {'type': 'MultiPolygon', 'coordinates': [mapping(p)['coordinates'] for p in parts]}
            result.append(dict(f, geometry=geometry))
    geo['features'] = result
    return repaired


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=Path('data/raw/foursquare-japan'))
    parser.add_argument('--output', type=Path, default=Path('web/data/foursquare-japan'))
    parser.add_argument('--sigmas', type=int, nargs='+', default=[200, 400, 800])
    parser.add_argument('--categories', nargs='+', choices=['all', 'food', 'shopping', 'service'], default=['all', 'food', 'shopping'])
    args = parser.parse_args()
    if any(s not in [200, 400, 800] for s in args.sigmas):
        parser.error('Supported sigmas: 200/400/800')
    raw_path = args.input / 'manifest.json'
    raw = json.loads(raw_path.read_text(encoding='utf-8'))
    if not raw.get('complete'):
        raise ValueError('Acquisition not complete')
    signature = hashlib.sha256(raw_path.read_bytes()).hexdigest()
    stations = json.loads(Path('data/raw/names-japan/stations.json').read_text(encoding='utf-8'))
    station_tree = cKDTree([PROJECT.transform(s['lon'], s['lat']) for s in stations])
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    compact_write(out / 'stations.json', stations)
    manifest_path = out / 'manifest.json'
    previous = json.loads(manifest_path.read_text(encoding='utf-8')) if manifest_path.exists() else {}
    if previous and previous.get('input_signature') != signature:
        raise ValueError('Different input snapshot; use a fresh output directory')
    metadata = dict(previous) if previous else {'source': raw['source'], 'bbox': raw['bbox'], 'coverage': '日本全国（JP登録・離島を含む。座標異常の可能性あり）', 'input_signature': signature, 'datasets': [], 'known_closed': raw['known_closed'], 'snapshots': raw['snapshots'], 'retrieved_utc': raw['retrieved_utc'], 'station_groups': len(stations), 'projection': CRS, 'delivery': 'viewport-chunks', 'grid_m': STEP, 'chunk_m': SIZE}
    parts = {(p['i'], p['j']): p for p in raw['parts']}
    con = duckdb.connect(config={'threads': 2, 'memory_limit': '1GB'})
    cache = Path('data/cache/national') / signature[:16]
    cache.mkdir(parents=True, exist_ok=True)
    for p in parts.values():
        origin = args.input / p['file']
        if hashlib.sha256(origin.read_bytes()).hexdigest() != p['sha256']:
            raise ValueError('Raw shard hash mismatch')
        target = cache / (origin.stem + '.parquet')
        if not target.exists():
            sql_path = str(target).replace("'", "''")
            con.execute("COPY (SELECT x, y, category, date_closed FROM read_json(?, format='newline_delimited', columns={x:'DOUBLE',y:'DOUBLE',category:'VARCHAR',date_closed:'VARCHAR'})) TO '" + sql_path + "' (FORMAT PARQUET)", [str(origin)])
        p['cache'] = str(target)
    # Include empty neighbouring cores: POIs within a halo can create bands across a border.
    keys = sorted({(i + a, j + b) for i, j in parts for a in [-1, 0, 1] for b in [-1, 0, 1]})
    for sigma in args.sigmas:
      for category in args.categories:
        name = f'{sigma}-{category}-exclude'
        folder = out / name
        folder.mkdir(exist_ok=True)
        chunks, peaks, overview_features = [], [], []
        start = time.perf_counter()
        for ordinal, (i, j) in enumerate(keys, 1):
            target = folder / f'{i}_{j}.json'
            if target.exists():
                geo = json.loads(target.read_text(encoding='utf-8'))
            else:
                points = []
                reach = 4 * sigma + 550
                paths = [parts[(i+a, j+b)]['cache'] for a in [-1,0,1] for b in [-1,0,1] if (i+a,j+b) in parts]
                if paths:
                    rows = con.execute('SELECT x,y FROM read_parquet(?) WHERE date_closed IS NULL AND (?=\'all\' OR category=?) AND x BETWEEN ? AND ? AND y BETWEEN ? AND ?', [paths, category, category, i*SIZE-reach, (i+1)*SIZE+reach, j*SIZE-reach, (j+1)*SIZE+reach]).fetchall()
                    points = [{'x': x, 'y': y} for x,y in rows]
                geo = surface(points, i, j, sigma, station_tree, stations) if points else {'type': 'FeatureCollection', 'features': []}
                sanitize_geo(geo)
                compact_write(target, geo)
            if sanitize_geo(geo):
                compact_write(target, geo)
            if geo['features']:
                chunks.append({'bbox': tile_bbox(i, j), 'file': f'{name}/{target.name}', 'bytes': target.stat().st_size})
                peaks.extend(f for f in geo['features'] if f['properties']['kind'] == 'peak')
                # Geographic simplification is a display aid, not a density recalculation.
                for f in geo['features']:
                    if f['properties']['kind'] == 'band' and f['properties']['density'] >= 800:
                        simplified = shape(f['geometry']).simplify(.002, preserve_topology=True)
                        if not simplified.is_empty:
                            overview_features.append(dict(f, geometry=mapping(simplified)))
            if ordinal % 25 == 0:
                print(f'{name}: {ordinal}/{len(keys)} chunks ({time.perf_counter() - start:.0f}s)', flush=True)
        peaks.sort(key=lambda f: -f['properties']['density'])
        compact_write(out / f'{name}-peaks.json', {'type': 'FeatureCollection', 'features': peaks})
        compact_write(out / f'{name}-overview.json', {'type': 'FeatureCollection', 'features': overview_features})
        item = {'sigma': sigma, 'category': category, 'status': 'exclude', 'count': raw['count'] - raw['known_closed'] if category == 'all' else raw['active_categories'].get(category, 0), 'peaks': len(peaks), 'chunks': chunks, 'peaks_file': f'{name}-peaks.json', 'overview_file': f'{name}-overview.json'}
        metadata['datasets'] = [d for d in metadata['datasets'] if (d['sigma'], d['category']) != (sigma, category)] + [item]
        compact_write(manifest_path, metadata)
        print(f'Completed {name}: {len(chunks)} nonempty chunks, {len(peaks)} peaks', flush=True)


if __name__ == '__main__':
    main()
