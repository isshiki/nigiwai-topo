"""Publish only curated corrections or policy-valid registered aliases.

Model agreement is insufficient: exact Japanese alias and source ID must match.
"""
import json,re
from pathlib import Path
from collections import Counter
from translate_names import save,validate
WORK=Path('data/name-translation/world')

# Deliberately limited glyph substitutions. Ambiguous pairs such as 发/后/干
# and 钟 are not inferred. This is typography, not a pronunciation translation.
GLYPHS=str.maketrans(dict(zip('广门东桥马岛阳阴县边进华庆兴宁齐济吴苏郑刘赵张陈','広門東橋馬島陽陰県辺進華慶興寧斉済呉蘇鄭劉趙張陳')))

def alias_names(ref,aliases):
    result={}
    for alias in aliases.get(ref['source_ids'][0],[]):
        if any(alias.get(k) for k in ('historic','colloquial','short','to')):continue
        original=alias['name'];name=original.translate(GLYPHS) if ref['country']=='CN' else original
        if policy(ref['country'],name):result[name]=original
    return result

def policy(country,name):
    if not name:return False
    if country=='KR':return bool(re.fullmatch(r'[ァ-ヺー・\s（）()0-9]+',name))
    if country=='CN':return bool(re.search('[一-鿿]',name)) and not re.search('[A-Za-zァ-ヺ广门龙东车马风岛阳阴云汉乡县边进华庆兴宁齐济吴苏郑叶刘赵张陈钟归]',name)
    return True

def main():
    refs={r['id']:r for r in json.loads((WORK/'dictionary.json').read_text(encoding='utf-8'))['items']}
    target={r['id']:r for r in json.loads((WORK/'locale-policy-input.json').read_text(encoding='utf-8'))['items']}
    rows=json.loads((WORK/'locale-policy-qwen3.5-9b.json').read_text(encoding='utf-8'))['items']
    extra=WORK/'locale-policy-granite4.2-8b.json'
    if extra.exists():
        done={r['id'] for r in rows}
        rows+= [r for r in json.loads(extra.read_text(encoding='utf-8'))['items'] if r['id'] not in done]
    validate(rows,{'items':rows})
    aliases=json.loads(Path('data/name-research/geonames-ja-aliases.json').read_text(encoding='utf-8'))['aliases']
    accepted={};review=[];direct_count=0
    for key,ref in target.items():
        valid=alias_names(ref,aliases)
        if len(valid)==1:
            name=next(iter(valid))
            accepted[key]={'name':name,'source':'GeoNames alternateNames ja / CC BY 4.0','status':'registered_policy_selected','source_name':valid[name],'basis':'同じ出典IDの登録済み日本語別名を国別表記方針で選択。中国の字形は限定的な対応表で日本語字形へ整理し、読みや曖昧な漢字は推測していません。'}
            direct_count+=1
    for row in rows:
        ref=refs[row['id']]
        if row['id'] not in target or any(row.get(k)!=ref.get(k) for k in ('original','country','lon','lat')):raise ValueError('Source reference mismatch')
        if row['id'] in accepted:continue
        name=None if row['kind']=='unknown' else row['ja']
        if not policy(ref['country'],name):review.append({**row,'reason':'unknown_or_policy_mismatch'});continue
        allowed=alias_names(ref,aliases)
        if name in allowed:
            accepted[row['id']]={'name':name,'source':'GeoNames alternateNames ja / CC BY 4.0','status':'registered_policy_selected','source_name':allowed[name],'basis':'出典IDに対応する登録別名と限定的な中国字形対応表で確認。国別表記方針で選択。'}
        else:review.append({**row,'reason':'no_exact_registered_alias'})
    editorial=json.loads(Path('docs/world-native-name-review.json').read_text(encoding='utf-8'))
    for key,entry in editorial.items():
        if key not in target or any(entry[k]!=refs[key][k] for k in ('original','country','lon','lat')):raise ValueError('Editorial source reference mismatch')
        if entry['decision']!='adopt':continue
        if not policy(entry['country'],entry['name']):raise ValueError('Invalid editorial spelling: '+key)
        accepted[key]={k:v for k,v in entry.items() if k not in ('native_aliases','decision','review_method','reviewed_at')}
    manual=json.loads(Path('docs/reviewed-world-names.json').read_text(encoding='utf-8'))
    for key,entry in manual.items():
        if any(entry[k]!=refs[key][k] for k in ('original','country')) or any(entry[k]!=refs[key][k] for k in ('lon','lat') if k in entry) or not policy(entry['country'],entry['name']):raise ValueError('Invalid curated correction')
        accepted[key]={**entry,'status':'reviewed_correction'}
    final_path=Path('docs/held-locale-final-review.json')
    final={}
    if final_path.exists():
        for entry in json.loads(final_path.read_text(encoding='utf-8'))['items']:
            key=entry['id']
            if key in final or key not in editorial or any(entry[k]!=refs[key][k] for k in ('original','country','lon','lat')):
                raise ValueError('Final review source reference mismatch: '+key)
            if entry['decision']=='adopt':
                if not policy(entry['country'],entry['name']) or not entry.get('basis') or not entry.get('source_url'):
                    raise ValueError('Invalid final review evidence: '+key)
                accepted[key]={k:v for k,v in entry.items() if k not in ('id','decision')}
                accepted[key]['status']='reviewed_final_locale'
            elif entry['decision']=='hold' and entry.get('reason'):
                accepted.pop(key,None)
            else:raise ValueError('Invalid final review decision: '+key)
            final[key]=entry
    review=[r for r in review if r['id'] not in accepted]
    # Preserve a final decision for every entry of the original 476-item audit,
    # including native holds subsequently resolved with public official sources.
    save(WORK/'final-locale-review-decisions.json',{'items':[{'id':key,'original':entry['original'],'country':entry['country'],'decision':'adopt' if key in accepted else 'hold','display_entry':accepted.get(key),'reason':None if key in accepted else final.get(key,entry).get('reason')} for key,entry in editorial.items()]})
    missing=[r for key,r in target.items() if key not in {r['id'] for r in rows}]
    save(WORK/'reviewed-name-overrides.json',accepted)
    save(WORK/'locale-policy-review.json',{'items':review,'missing':missing})
    summary={'target':len(target),'saved':len(rows),'missing':len(missing),'exact_registered_aliases':sum(r['status']=='registered_policy_selected' for r in accepted.values()),'unique_policy_aliases':direct_count,'curated_corrections':len(manual),'editorial_corrections':sum(r['status'].startswith('reviewed_native') or r['status']=='reviewed_roman_transliteration' for r in accepted.values()),'applied_overrides':len(accepted),'review_pending':len(review),'review_reasons':dict(Counter(r['reason'] for r in review))}
    summary['final_review_adopted']=sum(r['decision']=='adopt' for r in final.values())
    summary['final_review_hold']=sum(r['decision']=='hold' for r in final.values())
    save(WORK/'locale-policy-summary.json',summary)
    Path('web/world-reviewed-names.js').write_text('Object.assign(window.NIGIWAI_JAPANESE_NAMES.world,'+json.dumps(accepted,ensure_ascii=False,separators=(',',':'))+');\n',encoding='utf-8')
    print(json.dumps(summary))

if __name__=='__main__':main()
