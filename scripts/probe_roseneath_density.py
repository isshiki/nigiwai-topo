"""Reproducible sensitivity experiments; never edits published density data."""
import json
from pathlib import Path
import duckdb
import numpy as np
from global_density import density, DLON, DLAT, GEOD
from build_global_sample import peak_mask

def main():
    prior = json.loads(Path('data/name-research/reading-sources/roseneath-density-probe269.json').read_text())
    all_ids = set(prior['excluded_for_probe_only'])
    colocated = {'8f140d2a612449d6175dd49b', '330841b9e65b4126ac45b0a5'}
    lon, lat = -78.058, 44.193
    i = int(round((lon+180)/DLON))//500
    j = int(round((lat+90)/DLAT))//500
    w, s = -180+i*500*DLON, -90+j*500*DLAT
    con = duckdb.connect()
    rows = con.execute('SELECT fsq_place_id,longitude,latitude FROM read_parquet(?) WHERE longitude BETWEEN ? AND ? AND latitude BETWEEN ? AND ?', ['data/world-build/active.parquet', w-.2, w+.65, s-.08, s+.53]).fetchall()
    assert all_ids <= {r[0] for r in rows}
    results = {}
    for label, excluded in [('original',set()), ('exclude_13_trial',all_ids), ('preserve_colocated_2_trial',all_ids-colocated)]:
        points = np.array([[r[1],r[2]] for r in rows if r[0] not in excluded])
        xs, ys, z = density(points,i,j,200)
        c, r = np.argmin(abs(xs-lon)), np.argmin(abs(ys-lat))
        xx, yy = np.meshgrid(xs,ys)
        _, _, distance = GEOD.inv(np.full_like(xx,lon),np.full_like(yy,lat),xx,yy)
        nearby = distance<=1000
        maxima = peak_mask(z,ys)
        results[label] = dict(excluded_ids=sorted(excluded), density_at_original_peak=float(z[r,c]), max_within_1km=float(z[nearby].max()), original_is_peak=bool(maxima[r,c]), peaks_within_1km=[[float(xs[b]),float(ys[a]),float(z[a,b])] for a,b in np.argwhere(maxima & nearby)])
    assert abs(results['original']['density_at_original_peak']-prior['before_at_original_peak'])<1e-6
    assert abs(results['exclude_13_trial']['density_at_original_peak']-prior['after_at_original_peak'])<1e-6
    output = dict(kind='sensitivity_only_not_production', sigma_m=200, limitation='Co-location of library and fire station is supported by municipal address and floor plan; exact source coordinates and the other 11 IDs remain unverified. Trial exclusions are not an error determination.', sources=['https://www.ahtwp.ca/s/Infrastructure-Report-Phase-I-2014.pdf','https://www.ahtwp.ca/fenella-community-hall'], results=results)
    Path('data/name-research/reading-sources/roseneath-density-probe270.json').write_text(json.dumps(output,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(results))

if __name__=='__main__':
    main()
