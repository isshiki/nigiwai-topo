"""Nearest reference naming across the date line, with source provenance."""
import json
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from pyproj import Geod

GEOD=Geod(ellps='WGS84')


def unit(lon,lat):
    lon,lat=np.radians(lon),np.radians(lat)
    return np.column_stack([np.cos(lat)*np.cos(lon),np.cos(lat)*np.sin(lon),np.sin(lat)])


class ReferenceTree:
    def __init__(self,records):
        self.records=records
        self.tree=cKDTree(unit([r['lon'] for r in records],[r['lat'] for r in records])) if records else None

    def nearest(self,lon,lat):
        if self.tree is None: return None,None
        _,indices=self.tree.query(unit([lon],[lat])[0],k=min(8,len(self.records)))
        candidates=[self.records[int(i)] for i in np.atleast_1d(indices)]
        distances=[GEOD.inv(lon,lat,r['lon'],r['lat'])[2] for r in candidates]
        best=int(np.argmin(distances))
        return candidates[best],distances[best]


class GlobalNamer:
    def __init__(self):
        self.places=ReferenceTree(json.loads(Path('data/raw/geonames/places.json').read_text(encoding='utf-8')))
        stations=[]
        for s in json.loads(Path('data/distribution/foursquare-japan/stations.json').read_text(encoding='utf-8')):
            stations.append({**s,'source':'国土数値情報 N02','source_ids':[s['id']]})
        for region in ('sg-singapore','gb-london','is-reykjavik'):
            for s in json.loads((Path('data/raw/world-names')/region/'stations.json').read_text(encoding='utf-8')):
                stations.append({**s,'source':'OpenStreetMap','source_ids':s['osm_ids']})
        self.stations=ReferenceTree(stations)

    def __call__(self,lon,lat):
        station,distance=self.stations.nearest(lon,lat)
        if station and distance<=1500:
            return {'name':station['name'],'name_source':station['source'],'name_source_ids':station['source_ids'],
                'nearest_station':station['name'],'station_distance_m':round(distance),
                'name_basis':'取得済み近隣駅（1.5km以内・世界の全駅は未収録）'}
        place,distance=self.places.nearest(lon,lat)
        if place and distance<=15000:
            return {'name':place['name']+'付近','name_source':'GeoNames','name_source_ids':[place['id']],
                'place_distance_m':round(distance),'name_basis':'GeoNames近隣都市・町村（15km以内・行政区域の包含ではない）'}
        return {'name':f'{lat:.3f}, {lon:.3f}','name_source':'coordinates','name_basis':'15km以内に参照地名なし'}
