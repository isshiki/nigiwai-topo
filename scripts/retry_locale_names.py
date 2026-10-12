"""Try only missing locale responses with an existing second model."""
import json
from pathlib import Path
from types import SimpleNamespace
import translate_names as t

w=Path('data/name-translation/world')
rows=json.loads((w/'locale-policy-input.json').read_text(encoding='utf-8'))['items']
prior=json.loads((w/'locale-policy-qwen3.5-9b.json').read_text(encoding='utf-8'))['items']
done={r['id'] for r in prior}
pending=[{**r,'region':'world'} for r in rows if r['id'] not in done]
t.COUNTRIES={'world':('World','various')}
print('Granite locale missing:',len(pending),flush=True)
t.run(SimpleNamespace(output=w/'locale-policy-granite4.2-8b.json',model='granite4.2:8b',limit=0,batch_size=1),pending)
