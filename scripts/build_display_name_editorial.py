"""Attach reviewed display transliterations to explicit, unchanged reference IDs."""
import json
from pathlib import Path
def main():
    names={}
    for line in Path('docs/world-display-transliterations.tsv').read_text(encoding='utf-8').splitlines():
        original,ja=line.split('\t')
        if original in names:raise ValueError('Duplicate spelling in editorial table')
        names[original]=ja
    refs=json.loads(Path('data/name-translation/world/dictionary.json').read_text(encoding='utf-8'))['items']
    rows=[{**r,'ja':names[r['original']],'model':'Codex','provider':'editorial','kind':'transliteration','basis':'元表記・国の言語を参照した編集音写または略称の日本語読み。公的日本語登録名として確認した意味ではありません。'} for r in refs if r['original'] in names]
    Path('docs/world-display-name-corrections.json').write_text(json.dumps({'items':rows},ensure_ascii=False,indent=2),encoding='utf-8')
    print('Editorial source identities',len(rows))
if __name__=='__main__':main()
