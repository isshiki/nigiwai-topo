import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_reviewed_world_names import policy,alias_names

class LocalePolicy(unittest.TestCase):
    def test_reviewed_major_korean_cities(self):
        root=Path(__file__).resolve().parents[1]
        entries=json.loads((root/'docs/reviewed-world-names.json').read_text(encoding='utf-8'))
        for key,name in [('1835553','スウォン'),('1843564','インチョン'),('1835329','テグ'),('1835235','テジョン'),('1842616','コンジュ')]:
            entry=entries['GeoNames:'+key]
            self.assertEqual(entry['name'],name)
            self.assertEqual(entry['country'],'KR')
            self.assertTrue(entry['source_url'].startswith('https://'))
    def test_korean_katakana(self):
        self.assertTrue(policy('KR','コチャン'))
        self.assertFalse(policy('KR','高敞'))
        self.assertFalse(policy('KR','Guri'))
    def test_chinese_japanese_characters(self):
        self.assertTrue(policy('CN','広州'))
        self.assertTrue(policy('CN','黄山'))
        self.assertTrue(policy('CN','湾'))
        self.assertFalse(policy('CN','广州'))
        self.assertFalse(policy('CN','コウシュウ'))
        self.assertFalse(policy('CN',None))
    def test_glyph_normalization_requires_source_alias(self):
        ref={'country':'CN','source_ids':['1']}
        self.assertEqual(alias_names(ref,{'1':[{'name':'金桥'}]}),{'金橋':'金桥'})
        self.assertEqual(alias_names(ref,{'2':[{'name':'金桥'}]}),{})
        self.assertEqual(alias_names(ref,{'1':[{'name':'金桥','historic':True}]}),{})

if __name__=='__main__':unittest.main()
