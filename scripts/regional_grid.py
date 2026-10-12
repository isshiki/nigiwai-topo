"""Local equal-area grids for bounded world pilots (not one global CRS)."""
import math
from pyproj import Transformer


class RegionalGrid:
    def __init__(self, longitude, latitude, size=50000):
        if not (-180 <= longitude <= 180 and -80 <= latitude <= 80):
            raise ValueError('Pilot center outside supported latitude/longitude range')
        if size <= 0:
            raise ValueError('Grid size must be positive')
        self.longitude, self.latitude, self.size = longitude, latitude, size
        self.crs = f'+proj=laea +lat_0={latitude} +lon_0={longitude} +datum=WGS84 +units=m +no_defs'
        self.project = Transformer.from_crs(4326, self.crs, always_xy=True)
        self.inverse = Transformer.from_crs(self.crs, 4326, always_xy=True)

    def tile_key(self, x, y):
        return math.floor(x / self.size), math.floor(y / self.size)

    def tile_bounds(self, i, j):
        """Return one or two lon/lat envelopes, splitting at the date line."""
        points = []
        for n in range(41):
            t = n / 40
            for x, y in ((i+t, j), (i+t, j+1), (i, j+t), (i+1, j+t)):
                lon, lat = self.inverse.transform(x*self.size, y*self.size)
                # Unwrap around the projection center before finding an envelope.
                lon = self.longitude + (lon-self.longitude+180) % 360 - 180
                points.append((lon, lat))
        west, east = min(p[0] for p in points), max(p[0] for p in points)
        south, north = min(p[1] for p in points), max(p[1] for p in points)
        if west < -180:
            return [[west+360, south, 180, north], [-180, south, east, north]]
        if east > 180:
            return [[west, south, 180, north], [-180, south, east-360, north]]
        return [[west, south, east, north]]
