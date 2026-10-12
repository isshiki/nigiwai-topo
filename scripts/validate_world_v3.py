"""Validate v3 only after assembly has fully finished; no publishing."""
import json, subprocess, sys
from pathlib import Path
root=Path('data/distribution/foursquare-world-v3')
m=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
assert m['datasets'][0]['peaks']==319884, 'Assembly is not complete'
assert m['density_quality']['excluded_ids']==5437
subprocess.run([sys.executable,'scripts/validate_held_density_release_v3.py'],check=True)
subprocess.run([sys.executable,'scripts/validate_world_frontend.py','--root',str(root),'--report','data/validation/world-v3-frontend.json'],check=True)
print('V3 release validation complete; frontend and S3 switch remain separate')
