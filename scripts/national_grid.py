"""Japan-wide equal-area, metre-based grid. Not a global projection."""
from pyproj import Transformer
import math

CRS = '+proj=laea +lat_0=37 +lon_0=137 +datum=WGS84 +units=m +no_defs'
PROJECT = Transformer.from_crs(4326, CRS, always_xy=True)
INVERSE = Transformer.from_crs(CRS, 4326, always_xy=True)
SIZE = 50000
JAPAN_BBOX = (122, 20, 154, 46)


def tile_key(x, y):
    return math.floor(x / SIZE), math.floor(y / SIZE)


def tile_bbox(i, j):
    # Sample the edges because projected rectangles have curved geographic edges.
    coordinates = []
    for t in range(11):
        a = t / 10
        for x, y in [(i + a, j), (i + a, j + 1), (i, j + a), (i + 1, j + a)]:
            coordinates.append(INVERSE.transform(x * SIZE, y * SIZE))
    return [min(p[0] for p in coordinates), min(p[1] for p in coordinates),
            max(p[0] for p in coordinates), max(p[1] for p in coordinates)]
