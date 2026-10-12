import json
from pathlib import Path
import tempfile
import unittest
import duckdb
from scripts.fetch_world import fetch_world, country_key


class WorldAcquisition(unittest.TestCase):
    def test_counts_resume_poles_and_unknown_country(self):
        base=Path('data/validation')
        base.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as temporary:
            con=duckdb.connect()
            con.execute('CREATE TABLE points(fsq_place_id VARCHAR,name VARCHAR,longitude DOUBLE,latitude DOUBLE,country VARCHAR,fsq_category_ids VARCHAR[],date_closed DATE)')
            con.execute("INSERT INTO points VALUES ('a','A',180,90,'JP',[],NULL),('b','B',-180,-90,'US',[],'2025-01-01'),('c','C',0,0,NULL,[],NULL),('d','D',0,91,'JP',[],NULL)")
            root=Path(temporary)
            fetch_world(con,'points',[],{'fixed':1},root=root)
            manifest=json.loads((root/'manifest.json').read_text())
            self.assertTrue(manifest['complete'])
            self.assertEqual(manifest['count'],3)
            self.assertEqual(manifest['invalid_coordinates'],1)
            self.assertEqual(manifest['known_closed'],1)
            before={p.name:p.stat().st_mtime_ns for p in root.glob('*.parquet')}
            fetch_world(con,'points',[],{'fixed':1},root=root)
            self.assertEqual(before,{p.name:p.stat().st_mtime_ns for p in root.glob('*.parquet')})
            with self.assertRaises(ValueError): fetch_world(con,'points',[],{'fixed':2},root=root)
            con.close()

    def test_safe_country_paths(self):
        self.assertEqual(country_key('JP'),'JP')
        self.assertNotIn('/',country_key('../unsafe'))
        self.assertNotEqual(country_key(None),country_key('NULL'))

    def test_duplicates_across_countries_never_complete(self):
        base=Path('data/validation')
        base.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=base) as temporary:
            con=duckdb.connect()
            con.execute('CREATE TABLE points(fsq_place_id VARCHAR,name VARCHAR,longitude DOUBLE,latitude DOUBLE,country VARCHAR,fsq_category_ids VARCHAR[],date_closed DATE)')
            con.execute("INSERT INTO points VALUES ('same','A',0,0,'JP',[],NULL),('same','B',1,1,'US',[],NULL)")
            root=Path(temporary)
            with self.assertRaises(ValueError): fetch_world(con,'points',[],{'fixed':1},root=root)
            self.assertFalse(json.loads((root/'manifest.json').read_text())['complete'])
            con.close()
