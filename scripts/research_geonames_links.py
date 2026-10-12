import io,json,re,zipfile
from pathlib import Path
root=Path('data/name-research')
items=json.loads(Path('data/name-translation/world/input.json').read_text(encoding='utf-8'))['items'];wanted={r['source_ids'][0] for r in items if r['source']=='GeoNames'}
links={}
with zipfile.ZipFile(root/'alternateNamesV2.zip') as z:
 with z.open('alternateNamesV2.txt') as stream:
  for line in io.TextIOWrapper(stream,encoding='utf-8'):
   f=line.rstrip('\n').split('\t')
   if f[1] in wanted and f[2]=='wkdt' and re.fullmatch('Q[0-9]+',f[3]):links.setdefault(f[1],[]).append(f[3])
summary={'pending_geonames':len(wanted),'with_explicit_wikidata_link':len(links),'ambiguous_links':sum(len(set(v))>1 for v in links.values()),'japanese_label_coverage':'not measured; link does not imply Japanese label'}
(root/'geonames-wikidata-links.json').write_text(json.dumps({'summary':summary,'links':links}),encoding='utf-8');print(summary)
