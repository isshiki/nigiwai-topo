"""Resumable experimental world contours for the default 200m/all condition."""
import json
from pathlib import Path
import shutil
from build_global_sample import surface
from global_density import density,DLON,DLAT,LON_BINS
from prepare_world import connection
from fetch_world import write_json
import numpy as np


def main():
    root=Path('data/world-build/default')
    root.mkdir(parents=True,exist_ok=True)
    source='data/world-build/active.parquet'
    with connection() as con:
        rows=con.execute(f'''SELECT CAST(floor((least(399999,floor((longitude+180)/{DLON}+.5)))/500) AS INTEGER) AS i,
            CAST(floor(floor((latitude+90)/{DLAT}+.5)/500) AS INTEGER) AS j,count(*)
            FROM read_parquet(?) WHERE abs(latitude)<=85.05 GROUP BY i,j''',[source]).fetchall()
        tasks=sorted({((i+di)%800,j+dj) for i,j,_ in rows for di in (-1,0,1) for dj in (-1,0,1) if 11<=j+dj<=388},key=lambda p:(p[1],p[0]))
        write_json(root/'plan.json',{'experimental':True,'sigma':200,'category':'all','tasks':len(tasks),'occupied':len(rows),
            'names':'coordinate placeholders; worldwide references not yet attached','other_conditions':'pending','grid_version':1})
        print('Default world contour tasks:',len(tasks),flush=True)
        for number,(i,j) in enumerate(tasks,1):
            target=root/f'{i}-{j}.json'
            if target.exists(): continue
            if shutil.disk_usage(root).free<20*1024**3: raise ValueError('Low free disk space')
            w,s,e,n=-180+i*500*DLON,-90+j*500*DLAT,-180+(i+1)*500*DLON,-90+(j+1)*500*DLAT
            # 0.1 degree in longitude exceeds the 200m kernel support even at 85N.
            west,east=w-.1,e+.1
            clause='longitude BETWEEN ? AND ?';params=[west,east]
            if west<-180: clause='(longitude>=? OR longitude<=?)';params=[west+360,east]
            elif east>180: clause='(longitude>=? OR longitude<=?)';params=[west,east-360]
            points=np.array(con.execute(f'SELECT longitude,latitude FROM read_parquet(?) WHERE {clause} AND latitude BETWEEN ? AND ?',
                [source,*params,s-.015,n+.015]).fetchall())
            xs,ys,z=density(points,i,j,200)
            def name(lon,lat):
                return {'name':f'{lat:.3f}, {lon:.3f}','name_source':'coordinates',
                    'name_basis':'世界版生成中の座標仮表示・名称参照は未接続'}
            geo=surface(xs,ys,z,name)
            write_json(target,geo)
            write_json(root/'progress.json',{'completed_position':number,'tasks':len(tasks),'last_tile':[i,j],'complete':number==len(tasks),'experimental':True})
            if number%10==0: print(f'World default: {number}/{len(tasks)} tiles',flush=True)
        write_json(root/'progress.json',{'complete':True,'tasks':len(tasks),'experimental':True})


if __name__=='__main__': main()
