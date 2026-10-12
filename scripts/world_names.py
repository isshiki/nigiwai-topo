"""OSM reference names, separate from the Foursquare density input."""
import math
import unicodedata
from pyproj import Geod

GEOD = Geod(ellps='WGS84')


def display_name(tags):
    for key in ('name:ja', 'name', 'name:en'):
        if tags.get(key, '').strip():
            return tags[key].strip(), key
    return None, None


def station_candidate(tags):
    if tags.get('railway') in ('platform', 'stop', 'subway_entrance', 'construction', 'disused', 'abandoned'):
        return False
    if any(key in tags for key in ('disused:railway', 'abandoned:railway', 'construction:railway', 'proposed:railway')):
        return False
    if any(tags.get(key) == 'yes' for key in ('disused', 'abandoned', 'construction')):
        return False
    if tags.get('passenger') == 'no' or tags.get('usage') == 'freight':
        return False
    return tags.get('railway') in ('station', 'halt') or (
        tags.get('public_transport') == 'station' and
        (tags.get('train') == 'yes' or tags.get('subway') == 'yes' or tags.get('light_rail') == 'yes'))


def distance(a, b):
    return GEOD.inv(a['lon'], a['lat'], b['lon'], b['lat'])[2]


def reference_records(elements):
    stations, places = [], []
    for element in elements:
        tags = element.get('tags', {})
        name, key = display_name(tags)
        coordinates = element if 'lon' in element else element.get('center', {})
        if not name or not all(k in coordinates for k in ('lon', 'lat')):
            continue
        lon, lat = coordinates['lon'], coordinates['lat']
        if not (math.isfinite(lon) and math.isfinite(lat) and -180 <= lon <= 180 and -90 <= lat <= 90):
            continue
        record = {'name': name, 'local_name': tags.get('name', name), 'name_key': key,
                  'lon': lon, 'lat': lat, 'osm_ids': [f"{element['type']}/{element['id']}"],
                  'source': 'OpenStreetMap', 'wikidata': tags.get('wikidata'),
                  'match_name': unicodedata.normalize('NFKC', tags.get('name', name)).casefold().strip()}
        if station_candidate(tags):
            stations.append(record)
        elif tags.get('place') in ('city', 'town', 'village', 'suburb', 'quarter', 'neighbourhood'):
            places.append({**record, 'place': tags['place']})
    # Avoid transitive chains: every duplicate must be close to the original
    # representative. Wikidata only helps within this same distance guard.
    groups = []
    for record in sorted(stations, key=lambda r: r['osm_ids'][0]):
        match = next((g for g in groups if distance(g, record) <= 300 and (
            g['match_name'] == record['match_name'] or
            (g.get('wikidata') and g['wikidata'] == record.get('wikidata')))), None)
        if match:
            match['osm_ids'].extend(record['osm_ids'])
            if record['name_key'] == 'name:ja' and match['name_key'] != 'name:ja':
                match['name'], match['name_key'] = record['name'], record['name_key']
        else:
            groups.append(record)
    return groups, places


class WorldNamer:
    def __init__(self, stations, places):
        self.stations, self.places = stations, places

    def __call__(self, lon, lat):
        point = {'lon': lon, 'lat': lat}
        station = min(self.stations, key=lambda s: distance(point, s), default=None)
        result = {}
        if station:
            metres = distance(point, station)
            result.update(nearest_station=station['name'], station_distance_m=round(metres))
            if metres <= 1500:
                return result | {'name': station['name'], 'name_basis': 'OSM近隣駅（1.5km以内・峰の位置は駅と異なる）',
                    'name_source': 'OpenStreetMap', 'name_source_ids': station['osm_ids'], 'name_key': station['name_key']}
        # Local settlement points are reference names, not containing boundaries.
        nearby = [(distance(point, p), p) for p in self.places]
        nearby = [(d,p) for d,p in nearby if d <= (3000 if p['place'] in ('suburb','quarter','neighbourhood') else 15000)]
        if nearby:
            metres, place = min(nearby, key=lambda item: item[0])
            return result | {'name': place['name'] + '付近', 'name_basis': 'OSM近隣都市・地区の参考名（行政区域の包含判定ではない）',
                'name_source': 'OpenStreetMap', 'name_source_ids': place['osm_ids'],
                'place_distance_m': round(metres), 'name_key': place['name_key']}
        return result | {'name': f"{abs(lat):.2f}°{'N' if lat >= 0 else 'S'} {abs(lon):.2f}°{'E' if lon >= 0 else 'W'}",
                         'name_basis': '参照範囲内に駅・都市・地区名がないため座標表示', 'name_source': 'coordinates'}
