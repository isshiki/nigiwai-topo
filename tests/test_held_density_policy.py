import json,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from held_density_policy import load_policy
from rebuild_held_density import affected_chunks
from build_pmtiles import cache_signature

class HeldDensityPolicy(unittest.TestCase):
    def test_world_cache_changes_when_policy_changes_even_with_same_file_sizes(self):
        item={'sigma':200,'category':'all','chunks':[{'file':'unchanged-name.json','bytes':100}]}
        manifest={'world':True,'region_id':'test-region','input_signature':'before'}
        before=cache_signature(manifest,item,12)
        manifest['input_signature']='after'
        self.assertNotEqual(before,cache_signature(manifest,item,12))

    def test_policy_pins_original_ids_and_coordinates_and_retains_raw(self):
        policy,ids,_=load_policy()
        audit=json.loads(Path('data/name-research/held-poi-addresses/audit-detail.json').read_text(encoding='utf-8'))
        original={r['fsq_place_id']:r for g in audit['items'] for r in g['records']}
        self.assertEqual(ids,set(original));self.assertEqual(len(ids),5436)
        self.assertEqual(len(policy['groups']),13)
        for r in policy['records']:
            source=original[r['id']]
            self.assertEqual(r['coordinates'],[source['longitude'],source['latitude']])
        self.assertTrue(Path('data/world-build/active.parquet').is_file())
        self.assertIn('not proof',policy['basis'])

    def test_affected_chunks_include_cross_boundary_kernel_support(self):
        self.assertEqual(affected_chunks([{'coordinates':[0,0]}]),[(399,199),(399,200),(400,199),(400,200)])

    def test_recomputed_peaks_and_raw_mvt_are_below_floor(self):
        report=json.loads(Path('docs/held-density-rebuild.json').read_text(encoding='utf-8'))
        mvt=json.loads(Path('data/validation/held-density-release.json').read_text(encoding='utf-8'))
        self.assertEqual(mvt['unchanged_archive_sha256_matches'],2935)
        self.assertEqual(len(report['targets']),13)
        for r in report['targets']:
            self.assertLess(r['after'],100)
            self.assertLess(r['max_within_2km'],800)
            self.assertEqual(r['peaks_800_within_2km'],0)
        for r in mvt['target_mvt_results']:
            self.assertGreaterEqual(r['old_detail_band'],800)
            self.assertLess(r['new_detail_band'],100)
            self.assertLess(r['new_overview_band'],800)
if __name__=='__main__':unittest.main()
