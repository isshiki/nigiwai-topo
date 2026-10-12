"""Extract source-ID-linked native aliases for locale review, without adopting them."""
import io,json,zipfile,hashlib
from pathlib import Path
from collections import defaultdict,Counter

def main():
    root=Path('data/name-research')
    archive=root/'alternateNamesV2.zip'
    targets=json.loads(Path('data/name-translation/world/locale-policy-input.json').read_text(encoding='utf-8'))['items']
    wanted={str(r['source_ids'][0]):r for r in targets if r['source']=='GeoNames'}
    aliases=defaultdict(list)
    with zipfile.ZipFile(archive) as z:
        filename=next(n for n in z.namelist() if n.endswith('alternateNamesV2.txt'))
        with z.open(filename) as stream:
            for line in io.TextIOWrapper(stream,encoding='utf-8'):
                f=line.rstrip('\n').split('\t')
                if len(f)<8 or f[1] not in wanted:continue
                country=wanted[f[1]]['country']
                if not ((country=='CN' and (f[2]=='zh' or f[2].startswith('zh-'))) or (country=='KR' and f[2]=='ko')):continue
                aliases[f[1]].append(dict(alternate_id=f[0],language=f[2],name=f[3],preferred=f[4]=='1',short=f[5]=='1',colloquial=f[6]=='1',historic=f[7]=='1',to=f[9] if len(f)>9 else ''))
    summary={'source_url':'https://download.geonames.org/export/dump/alternateNamesV2.zip','license':'CC BY 4.0','archive_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'target':len(wanted),'references_with_native_alias':len(aliases),'languages':dict(Counter(a['language'] for rows in aliases.values() for a in rows))}
    (root/'geonames-native-aliases.json').write_text(json.dumps({'summary':summary,'aliases':dict(aliases)},ensure_ascii=False,indent=2),encoding='utf-8')
    from build_reviewed_world_names import GLYPHS,policy
    pending=json.loads(Path('data/name-translation/world/locale-policy-review.json').read_text(encoding='utf-8'))['items']
    review=[]
    for ref in pending:
        rows=[a for a in aliases.get(str(ref['source_ids'][0]),[]) if not any(a.get(k) for k in ('historic','colloquial','short','to'))]
        names=sorted({a['name'].translate(GLYPHS) for a in rows if ref['country']=='CN' and policy('CN',a['name'].translate(GLYPHS))})
        review.append({**ref,'native_aliases':rows,'glyph_candidates':names,'native_review_status':'unique_glyph_candidate_needs_review' if len(names)==1 else 'conflicting_glyph_candidates' if names else 'reading_or_glyph_research_required'})
    review_summary=dict(Counter(r['native_review_status'] for r in review))
    (root/'native-locale-review.json').write_text(json.dumps({'summary':review_summary,'items':review},ensure_ascii=False,indent=2),encoding='utf-8')
    summary['pending_review']=review_summary
    (root/'geonames-native-aliases.json').write_text(json.dumps({'summary':summary,'aliases':dict(aliases)},ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(summary),flush=True)

if __name__=='__main__':main()
