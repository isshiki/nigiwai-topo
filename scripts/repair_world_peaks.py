"""Re-evaluate boundary peaks with output padding; preserve contour geometry."""
import json
from pathlib import Path
import numpy as np
from global_density import density,DLON,DLAT,row_metrics
from build_global_sample import peak_mask
from build import feature
from prepare_world import connection
from fetch_world import write_json


def main():
    source=Path('data/world-build/default')
    out=Path('data/world-build/peak-repair');out.mkdir(parents=True,exist_ok=True)
    files=sorted(p for p in source.glob('*.json') if p.stem.count('-')==1 and all(x.isdigit() for x in p.stem.split('-')))
    changed=processed=0
    with connection() as con:
        for number,path in enumerate(files,1):
            i,j=map(int,path.stem.split('-'))
            target=out/path.name
            if target.exists(): processed+=1;continue
            geo=json.loads(path.read_text(encoding='utf-8'))
            peaks=[f for f in geo['features'] if f['properties']['kind']=='peak']
            if not peaks: continue
            w,s,e,n=-180+i*500*DLON,-90+j*500*DLAT,-180+(i+1)*500*DLON,-90+(j+1)*500*DLAT
            needs_repair=False
            for peak in peaks:
                lon,lat=peak['geometry']['coordinates'];dx,_=row_metrics(np.array([lat]))
                if min(lon-w,e-lon)<(400/dx[0]+2)*DLON or min(lat-s,n-lat)<.0054:
                    needs_repair=True;break
            if not needs_repair: continue
            west,east=w-.2,e+.2
            clause='longitude BETWEEN ? AND ?';params=[west,east]
            if west<-180: clause='(longitude>=? OR longitude<=?)';params=[west+360,east]
            elif east>180: clause='(longitude>=? OR longitude<=?)';params=[west,east-360]
            points=np.array(con.execute(f'SELECT longitude,latitude FROM read_parquet(?) WHERE {clause} AND latitude BETWEEN ? AND ?',
                ['data/world-build/active.parquet',*params,s-.08,n+.08]).fetchall())
            pad=64
            xs,ys,z=density(points,i,j,200,padding=pad)
            mask=peak_mask(z,ys)[pad:pad+500,pad:pad+500]
            revised=[feature('Point',[float(xs[c+pad]),float(ys[r+pad])],kind='peak',density=round(float(z[r+pad,c+pad])),
                name=f'{ys[r+pad]:.3f}, {xs[c+pad]:.3f}',name_source='coordinates',name_basis='名称参照前の仮表示')
                for r,c in np.argwhere(mask)]
            before={(tuple(f['geometry']['coordinates']),f['properties']['density']) for f in peaks}
            after={(tuple(f['geometry']['coordinates']),f['properties']['density']) for f in revised}
            changed+=before!=after;processed+=1
            write_json(target,{'type':'FeatureCollection','features':revised})
            if processed%25==0: print('Boundary repair files',processed,'scanned',number,'/',len(files),flush=True)
            write_json(out/'progress.json',{'complete':False,'scanned':number,'total':len(files),'repair_files':processed})
    write_json(out/'progress.json',{'complete':True,'scanned':len(files),'repair_files':processed,'changed_this_run':changed})
    print('Boundary peak repair complete',processed,flush=True)


if __name__=='__main__': main()
