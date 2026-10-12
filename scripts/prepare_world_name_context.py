"""Japanese administrative aliases for distinguishing genuinely different namesakes."""
import io,json,zipfile
from pathlib import Path
from translate_names import save

def main():
    admin={}
    for line in Path('data/raw/geonames/admin1CodesASCII.txt').read_text(encoding='utf-8').splitlines():
        code,name,ascii_name,gid=line.split('\t');admin[code]={'id':gid,'original':name}
    wanted={r['id'] for r in admin.values()};aliases={}
    with zipfile.ZipFile('data/name-research/alternateNamesV2.zip') as z:
        with z.open('alternateNamesV2.txt') as stream:
            for line in io.TextIOWrapper(stream,encoding='utf-8'):
                f=line.rstrip('\n').split('\t')
                if f[1] in wanted and f[2]=='ja' and f[3] and f[6]!='1' and f[7]!='1':
                    aliases.setdefault(f[1],[]).append({'name':f[3],'preferred':f[4]=='1'})
    for row in admin.values():
        choices=aliases.get(row['id'],[])
        if choices:row['ja']=sorted(choices,key=lambda a:not a['preferred'])[0]['name']
    meta={}
    with zipfile.ZipFile('data/raw/geonames/cities500.zip') as z:
        with z.open('cities500.txt') as stream:
            for line in io.TextIOWrapper(stream,encoding='utf-8'):
                f=line.rstrip('\n').split('\t');meta['GeoNames:'+f[0]]={'country':f[8],'admin1_code':f[8]+'.'+f[10]}
    save(Path('data/name-research/world-name-context.json'),{'admin1':admin,'references':meta,'source':'GeoNames cities500 / admin1CodesASCII / alternateNamesV2 (CC BY 4.0)'})
    print('Admin1 Japanese aliases',sum('ja' in r for r in admin.values()),flush=True)
if __name__=='__main__':main()
