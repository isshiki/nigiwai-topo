"""Connect source Japanese labels and explicitly attributed model transliterations.

Source IDs are retained. No spelling-based joins or invented geographic identities.
"""
import json,re,unicodedata
from pathlib import Path
from collections import Counter
from translate_names import save
from build_reviewed_world_names import GLYPHS

WORK=Path('data/name-translation/world')
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def js_object(path):
    text=Path(path).read_text(encoding='utf-8')
    return json.JSONDecoder().raw_decode(text[text.index('{'):])[0]
def clean(name):
    return unicodedata.normalize('NFC',name).strip().removesuffix('駅付近').removesuffix('付近')
TAIWAN_GLYPHS=str.maketrans(dict(zip('臺內區豐溪營壽峽來德關鄉國廣灣龍櫻澤雙廳','台内区豊渓営寿峡来徳関郷国広湾竜桜沢双庁')))
def japanese(name):
    if not isinstance(name,str) or not re.search('[ぁ-ヺ一-鿿]',name):return False
    for ch in name:
        if unicodedata.category(ch).startswith('L') and ch not in 'ー々' and not any(word in unicodedata.name(ch,'') for word in ('CJK UNIFIED IDEOGRAPH','CJK COMPATIBILITY IDEOGRAPH','HIRAGANA','KATAKANA')):return False
    return not re.search(r'[<>\r\n]',name)

def main():
    refs=read(WORK/'dictionary.json')['items']
    prior={}
    for name in ['world-japanese-names','world-name-overrides','world-reviewed-names']:
        prior.update(js_object('web/'+name+'.js'))
    wiki=read(WORK/'wikidata-names.json')
    aliases=read('data/name-research/geonames-ja-aliases.json')['aliases']
    models={r['id']:r for r in read(WORK/'all-candidates.json')['items']}
    corrections=WORK/'world-display-repair.json'
    repaired={r['id']:r for r in read(corrections)['items']} if corrections.exists() else {}
    strict=WORK/'world-display-repair-strict.json'
    if strict.exists():repaired.update({r['id']:r for r in read(strict)['items'] if japanese(r.get('ja'))})
    editorial=Path('docs/world-display-name-corrections.json')
    if editorial.exists():repaired.update({r['id']:r for r in read(editorial)['items']})
    tw_path=Path('data/name-research/taiwan-native-names.json')
    tw={r['id']:r for r in read(tw_path)['items']} if tw_path.exists() else {}
    tw_corrections=Path('docs/taiwan-display-name-corrections.json')
    tw_edited={r['id']:r for r in read(tw_corrections)['items']} if tw_corrections.exists() else {}
    native_path=Path('data/name-research/east-asian-native-names.json')
    native={r['id']:r for r in read(native_path)['items']} if native_path.exists() else {}
    mapping={};pending=[];counts=Counter()
    for r in refs:
        key=r['id'];entry=prior.get(key)
        if not entry or not japanese(entry['name']):
            entry=None
            if r['source']=='GeoNames':
                w=wiki.get(r['source_ids'][0])
                if w and japanese(w['name']):entry={**w,'basis':'出典IDにリンクされたWikidataの日本語登録名を採用。別名の表記揺れは元資料に保持。'}
                if not entry:
                    choices=[a for a in aliases.get(r['source_ids'][0],[]) if not any(a.get(k) for k in ('historic','colloquial','short','to')) and japanese(a['name'])]
                    if choices:
                        a=sorted(choices,key=lambda a:(not a.get('preferred'),a['alternate_id']))[0]
                        entry={'name':a['name'],'source':'GeoNames alternateNames ja / CC BY 4.0','status':'registered_variant_selected','basis':'同じ参照IDの日本語登録別名を採用。複数の表記候補は元資料に保持。'}
            if not entry:
                candidate=repaired.get(key) or models.get(key)
                if candidate and japanese(candidate.get('ja')):
                    if any(candidate.get(field)!=r.get(field) for field in ('original','country','lon','lat')):raise ValueError('Candidate source identity mismatch: '+key)
                    edited=candidate.get('provider')=='editorial'
                    name=candidate['ja']
                    if not edited and '(' not in r['original'] and '（' not in r['original']:name=re.sub(r'[（(][^()（）]*[)）]','',name)
                    entry={'name':name,'source':'Codex 編集音写' if edited else 'Local Ollama / '+candidate.get('model','editorial'),'status':'editorial_transliteration' if edited else 'machine_transliteration','basis':candidate.get('basis') if edited else '日本語の音写候補。言語モデルによる表記で、公的な登録名として確認した意味ではありません。','model':candidate.get('model')}
        if r['country']=='CN' and r['id'] in native and entry and (entry.get('status')=='machine_transliteration' or re.search('[ァ-ヺ]',entry['name'])):
            choices=[a for a in native[r['id']]['aliases'] if a['language'].startswith('zh') and not a['to'] and re.fullmatch('[一-鿿]+',a['name'])]
            if choices:
                a=sorted(choices,key=lambda a:(not a['preferred'],-len(a['name'])))[0]
                glyphs={**dict(GLYPHS),**dict(TAIWAN_GLYPHS),**str.maketrans({'龙':'竜','临':'臨','鲁':'魯','驿':'驛','云':'雲','汉':'漢','乡':'郷','风':'風','车':'車','叶':'葉','崃':'崍'})}
                entry={'name':a['name'].translate(glyphs),'source':'GeoNames native Chinese alias / CC BY 4.0','status':'reviewed_native_glyphs','source_name':a['name'],'basis':'原語の登録漢字別名を出典IDで照合。限定的な字形対応で日本語表記を整え、ピンインから漢字は推測していません。'}
        if r['id'] in tw:
            choices=[a for a in tw[r['id']]['aliases'] if a['language']!='ja' and not a['to'] and re.search('[一-鿿]',a['name'])]
            if choices:
                a=sorted(choices,key=lambda a:(not a['preferred'],{'zh-Hant':0,'zh-TW':1,'zh':2}[a['language']],-len(a['name'])))[0]
                entry={'name':a['name'].translate(TAIWAN_GLYPHS),'source':'GeoNames native Chinese alias / CC BY 4.0','status':'reviewed_native_glyphs','source_name':a['name'],'basis':'出典IDに対応する原語の漢字別名を使用し、限定的な字形対応表で日本語字形へ整理。読みから漢字を推測していません。'}
        if r['id'] in tw_edited:
            correction=tw_edited[r['id']]
            if any(correction[field]!=r[field] for field in ('original','country','lon','lat')):raise ValueError('Taiwan source mismatch')
            entry={k:correction[k] for k in ('name','basis','source_url')};entry.update(source='台湾自治体資料・GeoNames参照点',status='reviewed_locality_label')
        if entry:
            entry={**entry,'name':clean(entry['name'])}
            mapping[key]=entry;counts[entry.get('status','existing')]+=1
        else:pending.append({**r,'region':'world'})
    save(WORK/'world-display-pending.json',{'items':pending})
    # Metadata distinguishes identical names belonging to different places.
    groups={}
    for r in refs:
        if r['id'] in mapping:
            groups.setdefault(mapping[r['id']]['name'],[]).append(r)
    context_path=Path('data/name-research/world-name-context.json')
    context=read(context_path) if context_path.exists() else {'admin1':{},'references':{}}
    countries=js_object('web/world-regions.js')
    country_names={r['country_code']:r['name'] for r in countries.values() if r.get('country_code')}
    jp_stations={s['id']:s for s in read('data/distribution/foursquare-japan/stations.json')}
    for r in refs:
        if r['id'] not in mapping:continue
        e=mapping[r['id']];e['country']=r['country'];e['reference_coordinates']=[r['lon'],r['lat']]
        if len(groups[e['name']])<2:continue
        meta=context['references'].get(r['id'],{})
        admin=context['admin1'].get(meta.get('admin1_code'),{})
        country=r['country'];parts=[country_names.get(country,'')]
        if r['source']=='国土数値情報 N02':
            station=jp_stations.get(r['source_ids'][0],{})
            pref=countries.get('pref-'+station.get('pref_code',''),{}).get('name','')
            parts=[pref,station.get('municipality','')]
        elif country!='TW' and japanese(admin.get('ja')):parts.append(clean(admin['ja']))
        # A geographic qualifier distinguishes unrelated places sharing a spelling.
        # Neighbouring same-name station platforms are intentionally represented once.
        e['display_name']=e['name']+'（'+'・'.join(p for p in parts if p)+'）' if any(parts) else e['name']
    colliding={}
    for key,e in mapping.items():colliding.setdefault(e.get('display_name',e['name']),[]).append(key)
    refs_by_id={r['id']:r for r in refs}
    for keys in colliding.values():
        if len(keys)<2:continue
        # Administrative fallback names deliberately refer to the same municipality.
        # Different geographic references retain a coordinate qualifier when names
        # and their administrative qualifiers are otherwise identical.
        from global_names import GEOD
        base=refs_by_id[keys[0]]
        distant=any(GEOD.inv(base['lon'],base['lat'],refs_by_id[k]['lon'],refs_by_id[k]['lat'])[2]>1500 for k in keys[1:])
        if not distant or all(mapping[k].get('status')=='administrative_reference_fallback' for k in keys):continue
        for key in keys:
            e=mapping[key];r=refs_by_id[key]
            geographic=f"{'北緯' if r['lat']>=0 else '南緯'}{abs(r['lat']):.3f}度・{'東経' if r['lon']>=0 else '西経'}{abs(r['lon']):.3f}度"
            e['display_name']=e.get('display_name',e['name'])+'〔'+geographic+'〕'
    # Share repeated provenance text rather than shipping it 100,000 times.
    definitions=[];definition_ids={};rows=[]
    for key,e in mapping.items():
        provenance={k:v for k,v in e.items() if k not in ('name','display_name','country','reference_coordinates','qid','original','lon','lat')}
        encoded=json.dumps(provenance,ensure_ascii=False,sort_keys=True,separators=(',',':'))
        if encoded not in definition_ids:definition_ids[encoded]=len(definitions);definitions.append(provenance)
        rows.append([key,e['name'],e.get('display_name'),definition_ids[encoded],e.get('country'),e.get('qid')])
    js='(()=>{const rules='+json.dumps(definitions,ensure_ascii=False,separators=(',',':'))+';const rows='+json.dumps(rows,ensure_ascii=False,separators=(',',':'))+';for(const [id,name,display_name,rule,country,qid] of rows)window.NIGIWAI_JAPANESE_NAMES.world[id]={...rules[rule],name,display_name,country,qid};})();\n'
    Path('web/world-display-names.js').write_text(js,encoding='utf-8')
    save(WORK/'world-display-summary.json',{'references':len(refs),'japanese':len(mapping),'pending':len(pending),'statuses':dict(counts)})
    print(json.dumps({'references':len(refs),'japanese':len(mapping),'pending':len(pending),'statuses':dict(counts)}),flush=True)
if __name__=='__main__':main()
