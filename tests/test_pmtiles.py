import gzip
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from tempfile import TemporaryDirectory
import threading
import unittest
import urllib.error
import urllib.request

import mapbox_vector_tile
import mercantile
from shapely import STRtree
from shapely.geometry import box

from scripts.build_pmtiles import encode_tile
import scripts.serve as serve


class PMTilesTests(unittest.TestCase):
    def test_clipped_tile_keeps_density_value(self):
        tile=mercantile.tile(139.7,35.66,12)
        b=mercantile.xy_bounds(tile)
        geom=box(b.left-100,b.bottom-100,b.right+100,b.top+100)
        payload=encode_tile(tile,[geom],[{'kind':'band','density':1600}],STRtree([geom]))
        decoded=mapbox_vector_tile.decode(gzip.decompress(payload))['density']['features']
        self.assertEqual(len(decoded),1)
        self.assertEqual(decoded[0]['properties']['density'],1600)
        points=decoded[0]['geometry']['coordinates'][0]
        self.assertTrue(all(-8<=c<=4104 for p in points for c in p))

    def test_range_and_if_match(self):
        class Quiet(serve.Handler):
            def log_message(self,*args):
                pass
        Path('data/validation').mkdir(parents=True,exist_ok=True)
        with TemporaryDirectory(dir='data/validation') as temp:
            original=serve.STORAGE
            serve.STORAGE=Path(temp).resolve()
            (serve.STORAGE/'test.pmtiles').write_bytes(bytes(range(256))*2)
            server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(serve.WEB)))
            thread=threading.Thread(target=server.serve_forever,daemon=True)
            thread.start()
            url=f'http://127.0.0.1:{server.server_port}/tiles/test.pmtiles'
            try:
                req=urllib.request.Request(url,headers={'Range':'bytes=10-19'})
                with urllib.request.urlopen(req) as response:
                    self.assertEqual(response.status,206)
                    self.assertEqual(response.headers['Content-Range'],'bytes 10-19/512')
                    self.assertEqual(response.read(),bytes(range(10,20)))
                    etag=response.headers['ETag']
                req=urllib.request.Request(url,headers={'Range':'bytes=-2','If-Match':etag})
                with urllib.request.urlopen(req) as response:
                    self.assertEqual(response.read(),bytes([254,255]))
                for headers,code in [({'Range':'bytes=512-'},416),({'If-Match':'"wrong"'},412)]:
                    with self.assertRaises(urllib.error.HTTPError) as error:
                        urllib.request.urlopen(urllib.request.Request(url,headers=headers))
                    self.assertEqual(error.exception.code,code)
                    error.exception.close()
            finally:
                server.shutdown()
                server.server_close()
                thread.join()
                serve.STORAGE=original
