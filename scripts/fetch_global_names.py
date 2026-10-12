"""Cache GeoNames city/town references; no paid API or language-model calls."""
from datetime import datetime,timezone
import io
import json
from pathlib import Path
import urllib.request
import zipfile
from fetch_world import write_json,digest


def main():
    root=Path('data/raw/geonames');root.mkdir(parents=True,exist_ok=True)
    archive=root/'cities500.zip'
    if not archive.exists():
        request=urllib.request.Request('https://download.geonames.org/export/dump/cities500.zip',headers={'User-Agent':'NigiwaiTopo/0.1'})
        pending=archive.with_suffix('.pending.zip')
        with urllib.request.urlopen(request,timeout=120) as response,pending.open('wb') as stream:
            while block:=response.read(1024*1024): stream.write(block)
        with zipfile.ZipFile(pending) as z:
            if z.testzip(): raise ValueError('GeoNames archive corruption')
        pending.replace(archive)
    records=[]
    with zipfile.ZipFile(archive) as z:
        with z.open('cities500.txt') as stream:
            for line in io.TextIOWrapper(stream,encoding='utf-8'):
                fields=line.rstrip('\n').split('\t')
                if len(fields)!=19: raise ValueError('GeoNames column mismatch')
                records.append({'id':fields[0],'name':fields[1],'lat':float(fields[4]),'lon':float(fields[5]),
                    'country':fields[8],'feature_code':fields[7],'population':int(fields[14]),'source':'GeoNames'})
    write_json(root/'places.json',records)
    write_json(root/'manifest.json',{'count':len(records),'sha256':digest(archive),'retrieved_utc':datetime.now(timezone.utc).isoformat(),
        'source_url':'https://download.geonames.org/export/dump/','license':'CC-BY-4.0','role':'nearby city/town reference, not containing administrative boundary'})
    print('GeoNames references:',len(records),flush=True)


if __name__=='__main__': main()
