"""Build comparable density surfaces. Run from the project root."""
import argparse
import json
from pathlib import Path

import contourpy
import numpy as np
from pyproj import Transformer
from scipy.ndimage import gaussian_filter, maximum_filter
from scipy.spatial import cKDTree

try:
    from .region import BBOX
except ImportError:
    from region import BBOX
LEVELS = [100, 200, 400, 800, 1000, 1600, 2000, 3000, 4000, 6000, 8000, 12000, 16000, 20000, 24000, 32000]
PROJECT = Transformer.from_crs(4326, 6677, always_xy=True)
INVERSE = Transformer.from_crs(6677, 4326, always_xy=True)


def synthetic():
    rng = np.random.default_rng(20261005)
    points = []
    for lon, lat, count, spread in [(139.70, 35.69, 1900, .007), (139.702, 35.659, 1100, .006), (139.767, 35.681, 1300, .008), (139.775, 35.714, 650, .006)]:
        for x, y in rng.normal([lon, lat], spread, (count, 2)):
            points.append({'lon': float(x), 'lat': float(y), 'category': rng.choice(['food', 'shopping', 'other']).item()})
    return points


def density(points, bbox, sigma, step):
    # 4 sigma halo, aligned grid; output gets clipped only after convolution.
    cx, cy = PROJECT.transform([bbox[0], bbox[0], bbox[2], bbox[2]], [bbox[1], bbox[3], bbox[1], bbox[3]])
    x0, y0, x1, y1 = min(cx), min(cy), max(cx), max(cy)
    halo = int(np.ceil(4 * sigma / step))
    xs = np.arange(np.floor(x0 / step) * step - halo * step, x1 + (halo + 1) * step, step)
    ys = np.arange(np.floor(y0 / step) * step - halo * step, y1 + (halo + 1) * step, step)
    if points:
        px, py = PROJECT.transform([p['lon'] for p in points], [p['lat'] for p in points])
        hist = np.histogram2d(py, px, bins=(np.r_[ys - step / 2, ys[-1] + step / 2], np.r_[xs - step / 2, xs[-1] + step / 2]))[0]
    else:
        hist = np.zeros((len(ys), len(xs)))
    z = gaussian_filter(hist, sigma / step, mode='constant', truncate=4) * 1e6 / step**2
    ix = (xs >= x0) & (xs <= x1)
    iy = (ys >= y0) & (ys <= y1)
    return xs[ix], ys[iy], z[np.ix_(iy, ix)]


def feature(geometry_type, coords, **props):
    return {'type': 'Feature', 'geometry': {'type': geometry_type, 'coordinates': coords}, 'properties': props}


def geographic(ring):
    lon, lat = INVERSE.transform(ring[:, 0], ring[:, 1])
    return np.column_stack([lon, lat]).round(6).tolist()


def known_closed(point):
    return bool(point.get('date_closed')) or point.get('operating_status') in {'permanently_closed', 'temporarily_closed', 'closed'}


def osm_major_poi(point):
    tags = point.get('tags', {})
    if 'shop' in tags or 'office' in tags:
        return True
    minor_amenity = {'parking', 'parking_space', 'parking_entrance', 'bicycle_parking', 'bench', 'vending_machine', 'post_box', 'waste_basket', 'recycling', 'drinking_water', 'telephone', 'bicycle_rental', 'charging_station', 'toilets', 'shelter', 'water_point'}
    minor_leisure = {'garden', 'pitch', 'track', 'swimming_pool', 'picnic_table', 'fitness_station', 'bleachers'}
    return tags.get('amenity') not in minor_amenity and tags.get('leisure') not in minor_leisure


def surface(points, sigma, category):
    selected = points if category == 'all' else [p for p in points if p['category'] == category]
    xs, ys, z = density(selected, BBOX, sigma, 100)
    contour = contourpy.contour_generator(x=xs, y=ys, z=z, fill_type='OuterOffset', line_type='Separate')
    features = []
    levels = LEVELS + [max(64000, float(z.max()) + 1)]
    for low, high in zip(levels[:-1], levels[1:]):
        rings, offsets = contour.filled(low, high)
        for ring, cuts in zip(rings, offsets):
            features.append(feature('Polygon', [geographic(ring[a:b]) for a, b in zip(cuts[:-1], cuts[1:])], kind='band', density=low))
    for level in LEVELS:
        for line in contour.lines(level):
            features.append(feature('LineString', geographic(line), kind='contour', density=level, index=level in [1000, 2000, 4000, 8000, 16000, 32000]))
    # Preview only: local maxima + separation, NOT topographic prominence.
    candidates = np.argwhere((z == maximum_filter(z, size=9)) & (z >= 50))
    candidates = sorted(candidates, key=lambda p: -z[tuple(p)])
    for rank, (row, col) in enumerate(candidates, 1):
        lon, lat = INVERSE.transform(xs[col], ys[row])
        features.append(feature('Point', [lon, lat], kind='peak', density=round(float(z[row, col])), name=f'峰 {rank}'))
    return {'type': 'FeatureCollection', 'features': features}, len(selected)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, help='Normalized JSON: points, source, bbox, synthetic')
    parser.add_argument('--output', type=Path, default=Path('web/data'))
    args = parser.parse_args()
    raw = json.loads(args.input.read_text(encoding='utf-8')) if args.input else {'points': synthetic(), 'source': '架空データ（動作確認専用）', 'synthetic': True}
    input_points = [p for p in raw['points'] if osm_major_poi(p)] if raw['source'].startswith('OpenStreetMap') else raw['points']
    active_points = [p for p in input_points if not known_closed(p)]
    if not raw.get('synthetic', False):
        coverage = raw['bbox']
        if not (coverage[0] <= BBOX[0] - .04 and coverage[1] <= BBOX[1] - .04 and coverage[2] >= BBOX[2] + .04 and coverage[3] >= BBOX[3] + .04):
            raise ValueError('Input coverage lacks the extended Tokyo bounds and kernel halo; refetch before building.')
    stations_path = Path('data/raw/names/stations.json')
    stations = json.loads(stations_path.read_text(encoding='utf-8')) if stations_path.exists() else []
    towns_path = Path('data/raw/names/towns.json')
    towns = json.loads(towns_path.read_text(encoding='utf-8')) if towns_path.exists() else []
    station_tree = cKDTree([PROJECT.transform(s['lon'], s['lat']) for s in stations]) if stations else None
    town_tree = cKDTree([PROJECT.transform(s['lon'], s['lat']) for s in towns]) if towns else None
    out = args.output
    out.mkdir(parents=True, exist_ok=True)
    metadata = {'source': raw['source'], 'synthetic': raw.get('synthetic', False), 'bbox': BBOX, 'datasets': [], 'tokyo_station_groups': sum(s['tokyo'] for s in stations), 'input_bbox': raw.get('bbox'), 'quality': raw.get('quality'), 'retrieved_utc': raw.get('retrieved_utc'), 'known_closed': len(input_points) - len(active_points), 'snapshots': raw.get('snapshots')}
    metadata.update(raw_input_count=len(raw['points']), excluded_minor_features=len(raw['points']) - len(input_points))
    (out / 'stations.json').write_text(json.dumps(stations, ensure_ascii=False), encoding='utf-8')
    for sigma in [200, 400, 800]:
        for category in ['all', 'food', 'shopping']:
          for status in ['all', 'exclude']:
            if status == 'exclude' and len(active_points) == len(input_points):
                previous = metadata['datasets'][-1]
                metadata['datasets'].append(dict(previous, status='exclude'))
                continue
            geo, count = surface(input_points if status == 'all' else active_points, sigma, category)
            for f in geo['features']:
                if f['properties']['kind'] != 'peak':
                    continue
                xy = PROJECT.transform(*f['geometry']['coordinates'])
                if station_tree is not None:
                    distance, index = station_tree.query(xy)
                    f['properties'].update(nearest_station=stations[index]['name'], station_distance_m=round(distance))
                    if distance <= 1500:
                        f['properties'].update(name=stations[index]['name'], name_basis='近隣駅（峰の座標は駅と異なる）')
                        continue
                if town_tree is not None:
                    distance, index = town_tree.query(xy)
                    f['properties'].update(name=towns[index]['name']+'付近', name_basis='自治体代表点への近さによる参考名（行政区域判定ではない）')
            name = f'{sigma}-{category}.json' if status == 'all' else f'{sigma}-{category}-exclude.json'
            (out / name).write_text(json.dumps(geo, ensure_ascii=False), encoding='utf-8')
            metadata['datasets'].append({'sigma': sigma, 'category': category, 'status': status, 'count': count, 'file': name, 'peaks': sum(f['properties']['kind'] == 'peak' for f in geo['features'])})
    (out / 'manifest.json').write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(metadata, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
