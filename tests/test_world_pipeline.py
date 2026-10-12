import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from scripts.world_pipeline import active_points, classify_world


class WorldPipelineTests(unittest.TestCase):
    def test_unicode_line_separators_in_names_do_not_split_json_records(self):
        point={'name':'One\u2028Two','x':1,'y':2,'lon':0,'lat':0,'category':'food','date_closed':None}
        with TemporaryDirectory() as folder:
            p=Path(folder)/'points.jsonl'
            p.write_text(json.dumps(point,ensure_ascii=False)+'\n'+json.dumps({**point,'date_closed':'2020-01-01'})+'\n',encoding='utf-8')
            rows=list(active_points(p))
        self.assertEqual(len(rows),1)
        self.assertNotIn('name',rows[0])

    def test_world_classification_uses_top_level_not_public_or_bar_substrings(self):
        for name,expected in [('Community and Government','other'),('Business and Professional Services','service'),
                              ('Health and Medicine','service'),('Retail','shopping'),('Dining and Drinking','food')]:
            self.assertEqual(classify_world({'level1_category_name':name,'category_name':'Public Barber Shop'}),expected)
