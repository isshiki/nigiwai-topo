import json,re,unicodedata
from pathlib import Path
root=Path('data/name-research')
items=json.loads(Path('data/name-translation/world/input.json').read_text(encoding='utf-8'))['items'];byid={r['source_ids'][0]:r for r in items if r['source']=='GeoNames'}
geo=json.loads((root/'geonames-ja-aliases.json').read_text(encoding='utf-8'))['aliases']
usable={k:[r for r in v if not r['historic'] and not r['colloquial'] and not r['short'] and not r['to'] and re.search('[ぁ-ゖァ-ヺ一-鿿]',r['name'])] for k,v in geo.items()};usable={k:v for k,v in usable.items() if v and k in byid}
natural=json.loads((root/'natural-earth-matches.json').read_text(encoding='utf-8'));natural=[r for r in natural if re.search('[ぁ-ゖァ-ヺ一-鿿]',r['ja'])];ne={r['geonames_id']:r for r in natural}
wiki=json.loads((root/'wikidata-frequent.json').read_text(encoding='utf-8'))['results']['bindings'];wd={r['gid']['value']:r for r in wiki if 'ja' in r}
conflicts=[]
for key in set(usable)&set(ne):
 if ne[key]['ja'] not in {r['name'] for r in usable[key]}:conflicts.append({'id':key,'original':byid[key]['original'],'country':byid[key]['country'],'geonames':[r['name'] for r in usable[key]],'natural_earth':ne[key]['ja']})
covered=set(usable)|set(ne)
summary={'pending':len(items),'geonames_with_japanese_characters':len(usable),'natural_earth_pending':len(ne),'natural_earth_additional':len(set(ne)-set(usable)), 'combined_registered_candidates':len(covered),'remaining_after_registered_candidates':len(items)-len(covered),'covered_peaks':sum(byid[k]['peak_count'] for k in covered),'geonames_natural_earth_disagreements':len(conflicts),'frequent_300_geonames_coverage':sum(r['source_ids'][0] in usable for r in items[:300]),'wikidata_sample_additional':len(set(wd)-covered)}
(root/'comparison-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
(root/'geonames-natural-earth-conflicts.json').write_text(json.dumps(conflicts,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(summary));print(json.dumps(conflicts[:8],ensure_ascii=True))
