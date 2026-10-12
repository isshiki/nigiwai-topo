import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from compare_held_peak_exclusions import validate_reviewed_ids

class ExclusionImpact(unittest.TestCase):
    def test_reviewed_ids_reject_changed_address_or_coordinates(self):
        review={'items':[{'id':'a','name':'Business','coordinates':[10,20],'locality':'Town','address_components':['12','Main']} ]}
        rows={'a':{'name':'Business','status':'locality_reference_far','longitude':10,'latitude':20,'locality':'Town','address':'12 Main Street'}}
        self.assertEqual(validate_reviewed_ids(review,rows),{'a'})
        rows['a']['address']='99 Different Street'
        with self.assertRaises(ValueError):validate_reviewed_ids(review,rows)

    def test_real_recomputed_baselines_and_nested_exclusion_effects(self):
        report=json.loads((ROOT/'docs/held-peak-exclusion-impact.json').read_text(encoding='utf-8'))
        self.assertEqual(len(report['items']),13)
        self.assertEqual(report['excluded_ids'],{'original':0,'reviewed_only':4,'all_distant_candidates':3470})
        for r in report['items']:
            values=r['scenarios']
            self.assertEqual(round(values['original']['density_at_original_summit']),r['published_density'])
            before=values['original']['density_at_original_summit']
            strict=values['reviewed_only']['density_at_original_summit']
            broad=values['all_distant_candidates']['density_at_original_summit']
            self.assertGreaterEqual(before+1e-8,strict)
            self.assertGreaterEqual(strict+1e-8,broad)
        self.assertEqual(sum(r['scenarios']['all_distant_candidates']['peaks_800_within_2km']==0 for r in report['items']),8)

if __name__=='__main__':unittest.main()
