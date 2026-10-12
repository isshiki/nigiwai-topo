"""Assess registered Japanese GeoNames aliases; do not apply names to the app."""
import io,json,zipfile,urllib.request,hashlib,time
from pathlib import Path
from collections import defaultdict,Counter
ROOT=Path('data/name-research');ROOT.mkdir(parents=True,exist_ok=True)
def main():
    archive=ROOT/'alternateNamesV2.zip'
    if not archive.exists():
        req=urllib.request.Request('https://download.geonames.org/export/dump/alternateNamesV2.zip',headers={'User-Agent':'NigiwaiTopo/0.1 (name coverage study)'})
        with urllib.request.urlopen(req,timeout=120) as response,archive.with_suffix('.pending.zip').open('wb') as out:
            total=0
            while data:=response.read(1024*1024):
                out.write(data);total+=len(data)
                if total%(20*1024*1024)==0:print('Downloaded MiB',total//1024//1024,flush=True)
        with zipfile.ZipFile(archive.with_suffix('.pending.zip')) as z:
            if z.testzip():raise ValueError('Corrupt archive')
        archive.with_suffix('.pending.zip').replace(archive)
    dictionary=json.loads(Path('data/name-translation/world/dictionary.json').read_text(encoding='utf-8'))['items']
    wanted={r['source_ids'][0]:r for r in dictionary if r['source']=='GeoNames'}
    aliases=defaultdict(list);japanese_rows=0
    with zipfile.ZipFile(archive) as z:
        file=next(n for n in z.namelist() if n.endswith('alternateNamesV2.txt'))
        with z.open(file) as stream:
            for line in io.TextIOWrapper(stream,encoding='utf-8'):
                f=line.rstrip('\n').split('\t')
                if len(f)<8:raise ValueError('Invalid alias row')
                if f[2]!='ja':continue
                japanese_rows+=1
                if f[1] not in wanted:continue
                aliases[f[1]].append({'alternate_id':f[0],'name':f[3],'preferred':f[4]=='1','short':f[5]=='1','colloquial':f[6]=='1','historic':f[7]=='1','from':f[8] if len(f)>8 else '', 'to':f[9] if len(f)>9 else ''})
    usable={key:[r for r in rows if not r['historic'] and not r['colloquial'] and not r['short'] and not r['to']] for key,rows in aliases.items()}
    usable={k:v for k,v in usable.items() if v}
    pending={k:r for k,r in wanted.items() if r['status']=='pending'}
    covered=set(pending)&set(usable)
    conflict={k:v for k,v in usable.items() if len({r['name'] for r in v})>1}
    countries=Counter(pending[k]['country'] for k in covered)
    summary={'source_url':'https://download.geonames.org/export/dump/alternateNamesV2.zip','license':'CC BY 4.0',
        'archive_bytes':archive.stat().st_size,'archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),
        'japanese_alias_rows_worldwide':japanese_rows,'used_geonames_references':len(wanted),'any_ja_alias':len(aliases),
        'usable_ja_references':len(usable),'pending_references_covered':len(covered),'pending_peaks_covered':sum(pending[k]['peak_count'] for k in covered),
        'remaining_pending':sum(r['status']=='pending' for r in dictionary)-len(covered),'multiple_usable_labels':len(conflict),'covered_by_country':dict(countries)}
    (ROOT/'geonames-ja-aliases.json').write_text(json.dumps({'summary':summary,'aliases':dict(aliases)},ensure_ascii=False,indent=2),encoding='utf-8')
    (ROOT/'geonames-ja-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    print(summary,flush=True)
if __name__=='__main__':main()
