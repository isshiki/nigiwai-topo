"""Recompute a manually reviewed map fit; no dictionary or density mutations."""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from pyproj import Transformer
from shapely.geometry import Point, Polygon


def verify(path):
    r = json.loads(Path(path).read_text(encoding='utf-8'))
    assert hashlib.sha256(Path(r['source_pdf']).read_bytes()).hexdigest() == r['source_pdf_sha256']
    assert r['original_resolution_reviewed']
    xc, yc = np.asarray(r['longitude_controls']), np.asarray(r['latitude_controls'])
    ax, bx = np.polyfit(xc[:, 0], xc[:, 1], 1)
    ay, by = np.polyfit(yc[:, 0], yc[:, 1], 1)
    coords = [[float(ax*x+bx), float(ay*y+by)] for x,y in r['manually_traced_pixels']]
    assert np.allclose(coords, r['derived_polygon_lonlat'], atol=1e-10, rtol=0)
    t = Transformer.from_crs('EPSG:4326', r['projected_crs'], always_xy=True)
    polygon = Polygon([t.transform(*p) for p in coords])
    point = Point(*t.transform(*r['peak_coordinates']))
    assert polygon.is_valid and polygon.contains(point)
    assert abs(polygon.area/1e6-r['report_stated_area_km2']) <= .05
    assert polygon.buffer(-r['sensitivity_buffer_m']).contains(point)
    return {'area_km2':round(polygon.area/1e6,3),
            'boundary_margin_m':round(point.distance(polygon.boundary),2)}


if __name__ == '__main__':
    print(json.dumps(verify(sys.argv[1])))
