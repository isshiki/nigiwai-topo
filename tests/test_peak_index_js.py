import json
from pathlib import Path
import random
import shutil
import subprocess
import unittest
from scripts.build_peak_index import build_index


class PeakIndexBrowserLogicTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('node'), 'Node.js is needed for production JS index checks')
    def test_production_js_matches_full_scan_using_python_built_tree(self):
        rng=random.Random(42)
        features=[{'geometry':{'coordinates':[rng.uniform(-2,2),rng.uniform(-2,2)]},
                   'properties':{'density':i+1}} for i in range(1200)]
        fixture={'features':features,'index':build_index(features,leaf_size=20),
                 'boxes':[[-3,-3,3,3],[-.1,-2,.7,1],[0,0,0,0],[-2,-2,0,2]]}
        path=Path('data/validation/peak-index-js-fixture.json')
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(json.dumps(fixture),encoding='utf-8')
        subprocess.run(['node','tests/peak_index_check.cjs',str(path)],check=True,capture_output=True)
