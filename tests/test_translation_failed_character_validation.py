"""Invalid character responses must remain pending after retries."""
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import translate_names as t


class FailedCharacterValidation(unittest.TestCase):
    def test_exhausted_character_retries_do_not_save_candidate(self):
        item = dict(id='GeoNames:test', region='world', original='Test', country='SE')
        body = dict(message=dict(content=json.dumps(dict(items=[
            dict(id=item['id'], ja='Test', kind='transliteration')]))))
        with tempfile.TemporaryDirectory(dir=ROOT / 'data/validation') as folder:
            output = Path(folder) / 'result.json'
            args = SimpleNamespace(output=output, model='test', limit=0,
                                   batch_size=1, japanese_only=True)
            with patch.object(t, 'COUNTRIES', {'world': ('World', 'various')}), \
                 patch.object(t.time, 'sleep'), \
                 patch.object(t.urllib.request, 'urlopen', side_effect=lambda *a, **k:
                    io.BytesIO(json.dumps(body).encode())):
                t.run(args, [item])
            result = json.loads(output.read_text(encoding='utf-8'))
            self.assertEqual(result['items'], [])
            self.assertEqual(result['failures'][0]['status'], 'retry_pending')


if __name__ == '__main__':
    unittest.main()
