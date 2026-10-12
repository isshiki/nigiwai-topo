"""Compare the same 30 existing candidates sequentially on local models."""
import json
import unicodedata
from types import SimpleNamespace
from translate_names import WORK, run, save


def normalized(value):
    if not value: return None
    return unicodedata.normalize('NFKC',value).replace('・','').replace(' ','').replace('　','').removesuffix('駅')


def main():
    baseline=json.loads((WORK/'candidates-qwen3.5-4b.json').read_text(encoding='utf-8'))
    originals={r['id']:r for r in json.loads((WORK/'input.json').read_text(encoding='utf-8'))['items']}
    baseline_sample=baseline['items'][:30]
    sample=[originals[r['id']] for r in baseline_sample]
    save(WORK/'comparison-independent/input.json',sample)
    outputs={'qwen3.5:4b':baseline_sample}
    timings={'qwen3.5:4b':sum(b['seconds'] for b in baseline['batches'][:3])}
    for model in ('qwen3.5:9b','granite4.2:8b'):
        path=WORK/'comparison-independent'/('candidates-'+model.replace(':','-')+'.json')
        run(SimpleNamespace(model=model,limit=0,batch_size=10,output=path),sample)
        data=json.loads(path.read_text(encoding='utf-8'))
        outputs[model]=data['items']
        timings[model]=sum(b['seconds'] for b in data['batches'])
    models=list(outputs)
    tables={model:{r['id']:r for r in rows} for model,rows in outputs.items()}
    rows=[]
    for item in sample:
        names={model:tables[model][item['id']]['ja'] for model in models}
        values=list(names.values())
        rows.append({'id':item['id'],'region':item['region'],'original':item['original'],'names':names,
            'all_exact':bool(all(values) and len(set(values))==1),
            'all_normalized':bool(all(values) and len({normalized(v) for v in values})==1)})
    report={'sample_count':len(rows),'models':{model:{'seconds':timings[model],
        'answered':sum(r['ja'] is not None for r in outputs[model])} for model in models},
        'all_exact':sum(r['all_exact'] for r in rows),'all_normalized':sum(r['all_normalized'] for r in rows),
        'note':'Model agreement is not source verification. Normalization removes spaces, middle dots, station suffix only.', 'items':rows}
    save(WORK/'comparison-independent/report.json',report)
    print(json.dumps({k:v for k,v in report.items() if k!='items'},ensure_ascii=True),flush=True)


if __name__=='__main__': main()
