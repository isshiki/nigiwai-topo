import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts.fetch_world import write_json


class AtomicWorldJson(unittest.TestCase):
    def test_transient_windows_lock_retries(self):
        base=Path('data/validation');base.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as directory:
            target=Path(directory)/'progress.json'
            target.write_text('{"complete": false}',encoding='utf-8')
            original=Path.replace;attempts=[]
            def replace(source,destination):
                attempts.append(1)
                if len(attempts)<3: raise PermissionError('temporary lock')
                return original(source,destination)
            with patch.object(Path,'replace',autospec=True,side_effect=replace),patch('scripts.fetch_world.time.sleep'):
                write_json(target,{'complete':True})
            self.assertEqual(len(attempts),3)
            self.assertTrue(json.loads(target.read_text())['complete'])
