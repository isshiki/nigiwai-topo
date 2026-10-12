"""Retry remaining display transliterations with strict Japanese output."""
import json,argparse
from pathlib import Path
from types import SimpleNamespace
import translate_names as t

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--model',default='qwen3.5:9b');parser.add_argument('--output',default='world-display-repair.json');args=parser.parse_args()
    work=Path('data/name-translation/world')
    items=json.loads((work/'world-display-pending.json').read_text(encoding='utf-8'))['items']
    t.COUNTRIES={'world':('World','various')}
    t.INSTRUCTION += '今回はすべての地名をカタカナまたは既知の日本語漢字表記で返す。アルファベットや外国文字を含めない。行政用語は日本語にする。冠詞も音写し、原表記の意味を勝手に置き換えない。原語自体が曖昧な符号ならunknownを返す。'
    t.run(SimpleNamespace(output=work/args.output,model=args.model,limit=0,batch_size=10,japanese_only=True),items)
if __name__=='__main__':main()
