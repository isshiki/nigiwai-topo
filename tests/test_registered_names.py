import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from build_world_japanese_names import select_registered

class RegisteredNames(unittest.TestCase):
    def test_historic_excluded(self):
        result,reason=select_registered([{'name':'旧名','historic':True},{'name':'現名'}])
        self.assertEqual(result['name'],'現名');self.assertIsNone(reason)
    def test_punctuation_equivalence(self):
        result,reason=select_registered([{'name':'サン・ホセ'}],'サンホセ')
        self.assertIsNotNone(result);self.assertIsNone(reason)
    def test_conflicts_held(self):
        self.assertEqual(select_registered([{'name':'甲'},{'name':'乙'}])[1],'multiple_geonames_labels')
        self.assertEqual(select_registered([{'name':'甲'}],'乙')[1],'source_disagreement')

if __name__=='__main__':unittest.main()
