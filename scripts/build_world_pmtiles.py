"""Resume bounded world archive builds; preserve Japan and pilot releases."""
import json
from pathlib import Path
import subprocess
import sys
from fetch_world import write_json


def main():
    registry=json.loads(Path('data/world-build/packages/registry.json').read_text(encoding='utf-8'))
    root=Path('data/distribution/foursquare-world')
    root.mkdir(parents=True,exist_ok=True)
    for number,entry in enumerate(registry,1):
        output=root/entry['id']
        subprocess.run([sys.executable,'scripts/build_pmtiles.py','--input',entry['input'],'--output',str(output),'--choice','200-all'],check=True)
        write_json(root/'progress.json',{'complete':False,'packages':len(registry),'completed_position':number,
            'last_package':entry['id'],'experimental':True,'peak_boundary_correction':'pending'})
        print('World PMTiles packages',number,'/',len(registry),flush=True)
    write_json(root/'progress.json',{'complete':True,'packages':len(registry),'experimental':True,'peak_boundary_correction':'pending'})


if __name__=='__main__': main()
