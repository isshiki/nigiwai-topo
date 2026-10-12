"""Recover native-script names from same-ID country records missing language aliases."""
import io,json,zipfile,urllib.request,re,hashlib
from pathlib import Path
from datetime import datetime,timezone

def main():
    root=Path('data/name-research/coordinate-countries');root.mkdir(parents=True,exist_ok=True)
    wanted={r['id'].split(':')[-1]:r for r in json.loads(Path('data/name-research/native-locale-review.json').read_text(encoding='utf-8'))['items']}
    result={};sources=[]
    for code in ('CN','KR'):
        archive=root/(code+'.zip');url=f'https://download.geonames.org/export/dump/{code}.zip'
        if not archive.exists():
            pending=archive.with_suffix('.pending.zip')
            with urllib.request.urlopen(url,timeout=120) as src,pending.open('wb') as out:
                while data:=src.read(1024*1024):out.write(data)
            with zipfile.ZipFile(pending) as z:
                if z.testzip():raise ValueError('Corrupt country ZIP')
            pending.replace(archive)
        with zipfile.ZipFile(archive) as z:
            with z.open(code+'.txt') as src:
                for line in io.TextIOWrapper(src,encoding='utf-8'):
                    f=line.rstrip('\n').split('\t')
                    if f[0] not in wanted:continue
                    # No language attribution is claimed for the convenience
                    # aliases; use script identity and preserve all alternatives.
                    pattern=r'[一-鿿]+' if code=='CN' else r'[가-힣]+'
                    names=list(dict.fromkeys(n for n in [f[1],*f[3].split(',')] if re.fullmatch(pattern,n)))
                    result['GeoNames:'+f[0]]={'names':names,'source_name':f[1],'country':f[8],'lon':float(f[5]),'lat':float(f[4]),'feature_code':f[7],'modified':f[18],'source_url':url}
        sources.append({'source_url':url,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'license':'CC BY 4.0','checked_at':datetime.now(timezone.utc).isoformat()})
    Path('data/name-research/country-locale-aliases.json').write_text(json.dumps({'references':result,'sources':sources},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps({'references':len(result),'with_native_names':sum(bool(r['names']) for r in result.values())}))

if __name__=='__main__':main()
