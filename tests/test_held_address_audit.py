import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_held_peak_addresses import normalized,match_locality

class AddressAudit(unittest.TestCase):
    def test_locality_unicode_normalization(self):
        self.assertEqual(normalized('São Paulo'),normalized('Sao Paulo'))
        self.assertEqual(normalized('New-Delhi'),normalized('NEW DELHI'))
        self.assertEqual(normalized('كيش'),normalized('کیش'))

    def test_same_named_nearby_place_prevents_distant_flag(self):
        candidates=[{'id':'far','name':'Springfield','lon':-77,'lat':38},
                    {'id':'near','name':'Springfield','lon':-98.5,'lat':39.76}]
        result=match_locality(-98.5,39.76,candidates)
        self.assertEqual(result['status'],'locality_reference_not_far')
        self.assertEqual(result['candidate_count'],2)
        self.assertEqual(result['nearest_references'][0]['id'],'near')

    def test_missing_match_is_unknown_and_distance_is_only_screening(self):
        self.assertEqual(match_locality(0,0,[])['status'],'unmatched_locality')
        result=match_locality(145,-20,[{'id':'brisbane','name':'Brisbane','lon':153.028,'lat':-27.468}])
        self.assertEqual(result['status'],'locality_reference_far')
        self.assertGreater(result['nearest_references'][0]['distance_m'],50000)
        self.assertNotIn('exclude',result)

if __name__=='__main__':unittest.main()
