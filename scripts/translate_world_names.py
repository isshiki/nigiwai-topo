"""Run world name candidates using existing Ollama, keeping display names separate."""
import argparse,json
from pathlib import Path
import translate_names as translation

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--run',action='store_true')
    parser.add_argument('--model',default='qwen3.5:9b')
    parser.add_argument('--limit',type=int,default=300,help='0 means all; default is a limited trial')
    parser.add_argument('--batch-size',type=int,default=10)
    args=parser.parse_args()
    if args.limit<0 or args.batch_size<1:parser.error('Invalid limit/batch size')
    work=Path('data/name-translation/world')
    items=json.loads((work/'model-input.json').read_text(encoding='utf-8'))['items']
    assert len({r['id'] for r in items})==len(items)
    for r in items:r['region']='world'
    # Preserve frequency order rather than the old three-pilot interleave.
    translation.COUNTRIES={'world':('World','various')}
    args.output=work/('candidates-'+args.model.replace(':','-').replace('/','-')+'.json')
    print('Available names:',len(items),'trial limit:',args.limit,'model:',args.model,flush=True)
    if args.run:translation.run(args,items)
    else:print('Prepared only; use --run to call local Ollama. Candidates are not applied to the map.')
if __name__=='__main__':main()
