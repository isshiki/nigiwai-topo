import unittest
from scripts.translate_names import validate


class TranslationValidation(unittest.TestCase):
    def test_ids_and_japanese_required(self):
        items=[{'id':'one'}]
        result={'items':[{'id':'one','ja':'レイキャビク','kind':'transliteration'}]}
        self.assertEqual(validate(items,result)['one']['ja'],'レイキャビク')
        for row in ({'id':'wrong','ja':'レイキャビク','kind':'transliteration'},
                    {'id':'one','ja':'Reykjavik','kind':'transliteration'},
                    {'id':'one','ja':None,'kind':'conventional'}):
            with self.assertRaises(ValueError): validate(items,{'items':[row]})

    def test_unknown_and_duplicate_ids(self):
        self.assertIsNone(validate([{'id':'one'}],{'items':[{'id':'one','ja':None,'kind':'unknown'}]})['one']['ja'])
        with self.assertRaises(ValueError):
            validate([{'id':'one'},{'id':'two'}],{'items':[{'id':'one','ja':None,'kind':'unknown'}]*2})
