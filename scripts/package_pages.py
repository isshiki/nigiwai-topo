"""Package just the Pages frontend; bulk map data remain outside the site."""
import argparse
from pathlib import Path
import json
import shutil

parser=argparse.ArgumentParser()
parser.add_argument('--data-url',required=True,help='Public HTTPS URL ending in /foursquare-japan/')
parser.add_argument('--config',type=Path,help='Copy the public frontend configuration including its region registry')
args=parser.parse_args()
if not args.data_url.startswith('https://') or not args.data_url.endswith('/'):
    raise SystemExit('Use a public HTTPS storage URL ending with /')
out=Path('data/site')
out.mkdir(parents=True,exist_ok=True)
for name in ['index.html','about.html','app.js','peak-index.js','peak-quality.js','japanese-names.js','world-japanese-names.js','world-name-overrides.js','world-reviewed-names.js','world-coordinate-names.js','unnamed-world-peak-names.js','unnamed-world-peak-names.js','world-peak-locality-names.js','world-regions.js','world-display-names.js','world-station-peak-names.js','world-reference-stations.js','japanese-names.json','style.css']:
    shutil.copyfile(Path('web')/name,out/name)
shutil.copytree('web/licenses',out/'licenses',dirs_exist_ok=True)
for name in ['station-tier.html','station-tier.css','station-tier.js','station-tier-public.json','train-icon.svg']:
    shutil.copyfile(Path('web')/name,out/name)
(out/'station-tier-data.json').unlink(missing_ok=True)
if args.config:
    shutil.copyfile(args.config,out/'config.js')
else:
    (out/'config.js').write_text('window.NIGIWAI_CONFIG = '+json.dumps({'dataBase':args.data_url})+';\n',encoding='utf-8')
(out/'.nojekyll').touch()
print('Pages frontend:',sum(p.stat().st_size for p in out.rglob('*') if p.is_file()),'bytes')
