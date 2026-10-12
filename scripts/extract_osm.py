"""Stream a dated Geofabrik PBF; no Overpass or online query needed."""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import osmium
from shapely import from_wkb

from region import FETCH_BBOX, FOOD_TAGS, in_bbox


class Handler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.points = []
        self.factory = osmium.geom.WKBFactory()
        self.skipped_geometry = 0

    def tags(self, obj):
        tags = dict(obj.tags)
        if not any(k in tags for k in ['shop', 'amenity', 'tourism', 'leisure', 'office']):
            return None
        if tags.get('disused') == 'yes' or tags.get('abandoned') == 'yes':
            return None
        return tags

    def save(self, kind, obj, lon, lat, tags):
        if in_bbox(lon, lat):
            cat = 'food' if tags.get('amenity') in FOOD_TAGS else 'shopping' if 'shop' in tags else 'other'
            self.points.append({'id': f'{kind}/{obj.id}', 'name': tags.get('name'), 'lon': lon, 'lat': lat, 'category': cat, 'tags': tags})

    def node(self, obj):
        tags = self.tags(obj)
        if tags and obj.location.valid():
            self.save('node', obj, obj.location.lon, obj.location.lat, tags)

    def area(self, obj):
        tags = self.tags(obj)
        if not tags:
            return
        try:
            p = from_wkb(self.factory.create_multipolygon(obj)).representative_point()
        except Exception:
            self.skipped_geometry += 1
            return
        kind = 'way' if obj.from_way() else 'relation'
        self.save(kind, type('Identity', (), {'id': obj.orig_id()})(), p.x, p.y, tags)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pbf', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True)
    args = parser.parse_args()
    digest = hashlib.file_digest(args.pbf.open('rb'), 'sha256').hexdigest()
    if digest != args.expected_sha256:
        raise ValueError('PBF hash mismatch')
    handler = Handler()
    keys = ['shop', 'amenity', 'tourism', 'leisure', 'office']
    processor = osmium.FileProcessor(str(args.pbf)).with_locations('flex_mem').with_areas(osmium.filter.KeyFilter(*keys)).with_filter(osmium.filter.KeyFilter(*keys))
    processed = 0
    for obj in processor:
        if isinstance(obj, osmium.osm.Node):
            handler.node(obj)
        elif isinstance(obj, osmium.osm.Area):
            handler.area(obj)
        processed += 1
        if processed % 50000 == 0:
            print(f'Filtered objects: {processed}; collected POIs: {len(handler.points)}', flush=True)
    # Collapse named node/area representations at <30m; retain unnamed features.
    from scipy.spatial import cKDTree
    from pyproj import Transformer
    projection = Transformer.from_crs(4326, 6677, always_xy=True)
    grouped = {}
    unique = {}
    for p in handler.points:
        unique[p['id']] = p
    for p in unique.values():
        if p['name']:
            grouped.setdefault((p['name'], p['category']), []).append(p)
    removed = set()
    for points in grouped.values():
        xy = [projection.transform(p['lon'], p['lat']) for p in points]
        for a, b in sorted(cKDTree(xy).query_pairs(30)):
            if points[a]['id'] not in removed:
                removed.add(points[b]['id'])
    records = [p for p in unique.values() if p['id'] not in removed]
    raw = {'source': f'OpenStreetMap / Geofabrik {args.pbf.name}', 'synthetic': False, 'bbox': FETCH_BBOX, 'points': records, 'retrieved_utc': datetime.now(timezone.utc).isoformat(), 'source_url': 'https://download.geofabrik.de/asia/japan/kanto.html', 'input_sha256': digest, 'duplicates_removed': len(removed), 'skipped_geometry': handler.skipped_geometry, 'count': len(records), 'quality': 'Named duplicates within 30m collapsed; tagging coverage differs from other sources. Non-area tagged ways omitted.'}
    out = Path('data/raw/osm')
    out.mkdir(parents=True, exist_ok=True)
    target = out / 'points.json'
    target.write_text(json.dumps(raw, ensure_ascii=False), encoding='utf-8')
    manifest = {k: v for k, v in raw.items() if k != 'points'}
    manifest['sha256'] = hashlib.sha256(target.read_bytes()).hexdigest()
    (out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{len(records)} POIs, {len(removed)} duplicates removed, {handler.skipped_geometry} geometry failures')


if __name__ == '__main__':
    main()
