"""Validate v4 only after assembly has fully finished; no publishing."""
import json, subprocess, sys
from pathlib import Path
root=Path('data/distribution/foursquare-world-v4')
m=json.loads((root/'manifest.json').read_text(encoding='utf-8'))
assert m['datasets'][0]['peaks']==319883, 'Assembly is not complete'
assert m['density_quality']['excluded_ids']==5441
subprocess.run([sys.executable,'scripts/validate_held_density_release_v4.py'],check=True)
subprocess.run([sys.executable,'scripts/validate_world_frontend.py','--root',str(root),'--report','data/validation/world-v4-frontend.json'],check=True)
print('V4 release validation complete; frontend and S3 switch remain separate')
