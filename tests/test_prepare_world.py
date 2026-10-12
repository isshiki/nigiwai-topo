import unittest
import duckdb
from scripts.prepare_world import category_sql


class WorldPreparation(unittest.TestCase):
    def test_category_priority_and_other_retention(self):
        cats=[{'category_id':'f','level1_category_name':'Dining and Drinking'},
              {'category_id':'s','level1_category_name':'Retail'},
              {'category_id':'p','level1_category_name':'Business and Professional Services'},
              {'category_id':'h','level1_category_name':'Health and Medicine'}]
        con=duckdb.connect()
        actual=con.execute('SELECT '+category_sql(cats)+" FROM (VALUES (['f','s','p']),(['s','h']),(['h']),(['unknown']), (NULL)) AS t(fsq_category_ids)").fetchall()
        self.assertEqual(actual,[('food',),('shopping',),('service',),('other',),('other',)])
        con.close()

    def test_cell_edges_have_unique_ownership(self):
        con=duckdb.connect()
        result=con.execute('''SELECT least(179,CAST(floor((longitude+180)/2) AS INTEGER)),
            least(89,CAST(floor((latitude+90)/2) AS INTEGER))
            FROM (VALUES (-180,-90),(180,90),(0,0),(-178,-88)) AS p(longitude,latitude)''').fetchall()
        self.assertEqual(result,[(0,0),(179,89),(90,45),(1,1)])
        con.close()
