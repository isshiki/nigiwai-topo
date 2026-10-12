"""Reproducible stratified review sample; flags are not verified errors."""
import hashlib,json,re,unicodedata,html
from collections import Counter,defaultdict
from pathlib import Path
from translate_names import save
WORK=Path('data/name-translation/world')

def script_group(text):
    for label,pattern in [('hangul','[가-힣]'),('cjk','[一-鿿]'),('arabic','[\u0600-\u06ff]'),('cyrillic','[\u0400-\u04ff]'),('thai','[\u0e00-\u0e7f]'),('indic','[\u0900-\u0dff]')]:
        if re.search(pattern,text):return label
    return 'latin_or_other'

def flags(row):
    name=row.get('ja');out=[]
    if name is None:return ['unknown']
    if row['kind']=='conventional':out.append('unsourced_conventional_claim')
    if row['country']=='KR' and re.search(r'-(si|gun|gu)$',row['original']):
        out.append('korean_suffix')
        if re.search('(スイ|シイ|グン|グー)$',name):out.append('possible_suffix_misreading')
    if re.search('[A-Za-z]',name):out.append('latin_in_japanese')
    if len(name)<=2 and len(row['original'])>=12:out.append('possible_truncation')
    if re.search('[\u0600-\u06ff\u0400-\u04ff가-힣]',name):out.append('unconverted_foreign_script')
    return out

def build():
    rows=json.loads((WORK/'all-candidates.json').read_text(encoding='utf-8'))['items']
    groups=defaultdict(list);counts=Counter();flagged=[]
    for row in rows:
        reasons=flags(row);counts.update(reasons)
        if reasons:flagged.append({**row,'flags':reasons})
        groups[(row['country'] or 'unknown',script_group(row['original']))].append(row)
    selected={}
    def add(row,reason):
        selected.setdefault(row['id'],{**row,'flags':flags(row),'sample_reasons':[]})['sample_reasons'].append(reason)
    # Two deterministic hashed selections per country/script stratum.
    for key,group in sorted(groups.items()):
        for row in sorted(group,key=lambda r:hashlib.sha256(('nigiwai-audit-v1:'+r['id']).encode()).digest())[:2]:add(row,'country_script_stratum')
    for row in sorted(rows,key=lambda r:(-r['peak_count'],r['id']))[:50]:add(row,'high_peak_coverage')
    for reason in counts:
        for row in sorted((r for r in flagged if reason in r['flags']),key=lambda r:(-r['peak_count'],r['id']))[:5]:add(row,'flag:'+reason)
    sample=list(selected.values())
    report={'total':len(rows),'country_count':len({r['country'] for r in rows}),'strata':len(groups),'sample':len(sample),'flags':dict(counts),'semantic_accuracy_measured':False,'sample_method':'2 hashed IDs per country/script; top 50 by peak_count; top 5 per flag; deduplicated. Not a proportional random sample.'}
    save(WORK/'quality-audit-summary.json',report)
    save(WORK/'quality-audit-sample.json',{'version':1,'items':sample})
    save(WORK/'quality-audit-flags.json',{'items':flagged})
    cells=[]
    for r in sample:
        values=[r['id'],r['country'] or 'unknown',r['original'],r['ja'] or '不明',str(r['peak_count']),', '.join(r['flags']),', '.join(r['sample_reasons'])]
        cells.append('<tr>'+''.join('<td>'+html.escape(v)+'</td>' for v in values)+'</tr>')
    page='<!doctype html><meta charset="utf-8"><title>世界の山名：翻訳候補の品質確認</title><style>body{font:16px sans-serif;margin:24px}table{border-collapse:collapse;width:100%}td,th{border:1px solid #ccc;padding:8px;vertical-align:top}th{position:sticky;top:0;background:#edf3f8}input{font:inherit;padding:8px;width:24em}tr.hide{display:none}</style><h1>世界の山名：翻訳候補の品質確認</h1><p>未検証候補。フラグは誤訳の証明ではありません。国・文字体系別のサンプルと表示への影響が大きい名前を選定。単純な正答率の推定には使えません。</p><p>'+html.escape(json.dumps(report,ensure_ascii=False))+'</p><input id="filter" placeholder="国コード・元の名前・候補などで絞り込み"><table><thead><tr>'+''.join('<th>'+v+'</th>' for v in ['ID','国','元の名前','候補','参照峰数','確認フラグ','抽出理由'])+'</tr></thead><tbody>'+''.join(cells)+'</tbody></table><script>document.querySelector("#filter").addEventListener("input",e=>{for(const r of document.querySelectorAll("tbody tr"))r.classList.toggle("hide",!r.textContent.toLowerCase().includes(e.target.value.toLowerCase()))});</script>'
    (WORK/'quality-review.html').write_text(page,encoding='utf-8')
    print(json.dumps(report))

if __name__=='__main__':build()
