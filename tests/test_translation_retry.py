import json,sys,tempfile,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import translate_names as t

class Retry(unittest.TestCase):
    def test_unknown_echo_is_preserved_as_null(self):
        items=[{'id':'0','region':'world','original':'SS2'}]
        good={'message':{'content':json.dumps({'items':[{'id':'0','ja':'SS2','kind':'unknown'}]})}}
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
        with tempfile.TemporaryDirectory(dir='data') as folder:
            args=SimpleNamespace(output=Path(folder)/'result.json',model='test',limit=0,batch_size=1)
            with patch.object(t,'COUNTRIES',{'world':('World','various')}),patch.object(t.urllib.request,'urlopen',return_value=Response()),patch.object(t.json,'load',return_value=good):
                t.run(args,items)
            saved=json.loads(args.output.read_text(encoding='utf-8'))
            self.assertIsNone(saved['items'][0]['ja'])
            self.assertEqual(saved['items'][0]['kind'],'unknown')

    def test_failed_batch_does_not_block_later_and_can_resume(self):
        items=[{'id':str(i),'region':'world','original':'Example'} for i in range(2)]
        good={'message':{'content':json.dumps({'items':[{'id':'1','ja':'例','kind':'transliteration'}]})}}
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
        with tempfile.TemporaryDirectory(dir='data') as folder:
            args=SimpleNamespace(output=Path(folder)/'result.json',model='test',limit=0,batch_size=1)
            with patch.object(t,'COUNTRIES',{'world':('World','various')}),patch.object(t.time,'sleep'),patch.object(t.urllib.request,'urlopen',side_effect=[ValueError('bad')]*3+[Response()]),patch.object(t.json,'load',return_value=good):
                t.run(args,items)
            saved=json.loads(args.output.read_text(encoding='utf-8'))
            self.assertEqual([r['id'] for r in saved['items']],['1'])
            self.assertEqual(saved['failures'][0]['ids'],['0'])

if __name__=='__main__':unittest.main()
