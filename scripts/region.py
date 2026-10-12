"""Shared Tokyo mainland study area, including all Tokyo rail stations."""
BBOX = (138.88, 35.44, 140.02, 35.96)
FETCH_BBOX = (138.82, 35.38, 140.08, 36.02)
FOOD_TAGS = {'restaurant', 'cafe', 'fast_food', 'bar', 'pub', 'food_court', 'ice_cream', 'biergarten'}


def in_bbox(lon, lat, bbox=FETCH_BBOX):
    return bbox[0] <= lon <= bbox[2] and bbox[1] <= lat <= bbox[3]
