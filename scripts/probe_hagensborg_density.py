"""Reproducible sensitivity experiments; never edits published density data."""
import json
from pathlib import Path
import duckdb
import numpy as np
from global_density import density, DLON, DLAT, GEOD
from build_global_sample import peak_mask

def main():
    con = duckdb.connect()
    cluster = con.execute("SELECT fsq_place_id,name,address FROM read_parquet('data/name-research/unnamed-world/addresses.parquet') WHERE longitude=? AND latitude=?", [-126.50910308526763,52.39527019835298]).fetchall()
    assert len(cluster)==13
    all_ids={r[0] for r in cluster}
    distant_lodge={'208172bc132746689c568d27'}
    assert distant_lodge <= all_ids
    lon, lat = -126.509,52.395
    i = int(round((lon+180)/DLON))//500
    j = int(round((lat+90)/DLAT))//500
    w, s = -180+i*500*DLON, -90+j*500*DLAT
    con = duckdb.connect()
    rows = con.execute('SELECT fsq_place_id,longitude,latitude FROM read_parquet(?) WHERE longitude BETWEEN ? AND ? AND latitude BETWEEN ? AND ?', ['data/world-build/active.parquet', w-.2, w+.65, s-.08, s+.53]).fetchall()
    assert all_ids <= {r[0] for r in rows}
    results = {}
    for label, excluded in [('original',set()), ('exclude_distant_lodge_trial',distant_lodge), ('exclude_all_13_trial',all_ids)]:
        points = np.array([[r[1],r[2]] for r in rows if r[0] not in excluded])
        xs, ys, z = density(points,i,j,200)
        c, r = np.argmin(abs(xs-lon)), np.argmin(abs(ys-lat))
        xx, yy = np.meshgrid(xs,ys)
        _, _, distance = GEOD.inv(np.full_like(xx,lon),np.full_like(yy,lat),xx,yy)
        nearby = distance<=1000
        maxima = peak_mask(z,ys)
        results[label] = dict(excluded_ids=sorted(excluded), density_at_original_peak=float(z[r,c]), max_within_1km=float(z[nearby].max()), original_is_peak=bool(maxima[r,c]), peaks_within_1km=[[float(xs[b]),float(ys[a]),float(z[a,b])] for a,b in np.argwhere(maxima & nearby)])
    output=dict(kind='sensitivity_only_not_production',sigma_m=200,cluster=cluster,limitation='One known distant lodge and full cluster removal are sensitivity experiments. Not every colocated facility has been proven wrong; this does not edit published data.',sources=['https://www.tweedsmuirparklodge.com/trip-planning/plan-your-trip/?active-details-tab=here'],results=results)
    Path('data/name-research/reading-sources/hagensborg-density-probe308.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(results))

if __name__=='__main__':
    main()
