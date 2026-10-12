"""Retain native Chinese aliases by exact GeoNames identity for editorial review."""
import io,json,zipfile
from pathlib import Path
from translate_names import save
def main():
    refs=[r for r in json.loads(Path('data/name-translation/world/dictionary.json').read_text(encoding='utf-8'))['items'] if r['country']=='TW']
    wanted={r['source_ids'][0] for r in refs};aliases={}
    with zipfile.ZipFile('data/name-research/alternateNamesV2.zip') as z:
        with z.open('alternateNamesV2.txt') as stream:
            for line in io.TextIOWrapper(stream,encoding='utf-8'):
                f=line.rstrip('\n').split('\t')
                if f[1] in wanted and f[2] in ('zh','zh-TW','zh-Hant','ja') and f[6]!='1' and f[7]!='1':
                    aliases.setdefault(f[1],[]).append({'name':f[3],'language':f[2],'preferred':f[4]=='1','to':f[9] if len(f)>9 else ''})
    save(Path('data/name-research/taiwan-native-names.json'),{'items':[{**r,'aliases':aliases.get(r['source_ids'][0],[])} for r in refs]})
    print('Taiwan references',len(refs))
if __name__=='__main__':main()
