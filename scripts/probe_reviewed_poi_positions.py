"""Preview exact-ID exclusions with production KDE; no active tiles are changed."""
import argparse,json,math
from pathlib import Path
import numpy as np
import duckdb
from global_density import density


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--review',default='docs/reviewed-poi-position386.json')
    parser.add_argument('--output',default='data/validation/reviewed-poi-position386-preview.json')
    args=parser.parse_args()
    output_path=Path(args.output)
    if not output_path.resolve().is_relative_to(Path.cwd().resolve()):
        raise ValueError('Preview output must remain within this project')
    review=json.loads(Path(args.review).read_text(encoding='utf-8'))
    ids={x['id'] for x in review['records']}
    assert len(ids)==len(review['records'])
    tasks={}
    for r in review['records']:
        lon,lat=r['coordinates'];i=math.floor((lon+180)/.45);j=math.floor((lat+90)/.45)
        tasks.setdefault((i,j),[]).append(r)
    con=duckdb.connect(config={'threads':2,'memory_limit':'2GB'})
    output=[]
    for (i,j),records in tasks.items():
        w,s=-180+i*.45,-90+j*.45
        rows=con.execute('SELECT fsq_place_id,longitude,latitude FROM read_parquet(?) WHERE longitude BETWEEN ? AND ? AND latitude BETWEEN ? AND ?',
                         ['data/world-build/active.parquet',w-.2,w+.65,s-.08,s+.53]).fetchall()
        by_id={r[0]:r for r in rows}
        for r in records:
            assert r['id'] in by_id and list(by_id[r['id']][1:])==r['coordinates']
        points=np.asarray([r[1:] for r in rows])
        keep=np.asarray([r[0] not in ids for r in rows])
        xs,ys,before=density(points,i,j,200,padding=64)
        _,_,after=density(points[keep],i,j,200,padding=64)
        assert np.all(after<=before+1e-8)
        peak=json.loads(Path('data/name-research/unnamed-world/address-name-review.json').read_text(encoding='utf-8'))
        target=next(x for x in peak['items'] if x['peak']==records[0]['peak'])
        lon,lat=target['coordinates'];c=int(np.argmin(abs(xs-lon)));r=int(np.argmin(abs(ys-lat)))
        assert round(float(before[r,c]))==target['density']
        output.append({'chunk':[i,j],'nearby_input':len(rows),'excluded_exact_ids':sorted(ids & set(by_id)),
                       'peak':target['peak'],'original_peak_density':target['density'],
                       'preview_density_at_original_point':float(after[r,c]),
                       'maximum_reduction':float((before-after).max()),
                       'density_increased':False,'original_density_reproduced':True})
    con.close()
    result={'status':'complete','active_density_changed':False,'records':len(ids),'checks':output,
            'limits':'Preview at original summit, not regenerated peak selection or tile release. Other suspicious POIs retained pending individual evidence.'}
    output_path.write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result))


if __name__=='__main__':main()
