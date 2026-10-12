import unittest
from scripts.global_names import ReferenceTree


class GlobalNames(unittest.TestCase):
    def test_date_line_and_ellipsoid_distance(self):
        tree=ReferenceTree([{'name':'near','lon':179.999,'lat':0},{'name':'far','lon':0,'lat':0}])
        record,distance=tree.nearest(-179.999,0)
        self.assertEqual(record['name'],'near')
        self.assertAlmostEqual(distance,222.64,delta=.1)

    def test_empty_references(self):
        self.assertEqual(ReferenceTree([]).nearest(0,0),(None,None))
