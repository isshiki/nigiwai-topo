import json,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from prepare_chat_name_review import GLYPHS
from build_reviewed_world_names import policy
from pyproj import Geod

class ReviewedNames(unittest.TestCase):
    def test_source_characters_not_model_invented_homophones(self):
        entries=json.loads((ROOT/'docs/world-native-name-review.json').read_text(encoding='utf-8'))
        for key,name in [('7843633','高境'),('6958825','石岩'),('7843640','九亭鎮'),('9275564','幸福路'),('6825132','呉家営'),('7048101','席王')]:
            self.assertEqual(entries['GeoNames:'+key]['name'],name)
        for key,entry in entries.items():
            if entry['decision']!='adopt':continue
            self.assertTrue(policy(entry['country'],entry['name']),key)
            if entry['status']=='reviewed_native_glyphs':
                self.assertIn(entry['source_name'],[a['name'] for a in entry['native_aliases']],key)
                self.assertEqual(entry['name'],entry['source_name'].translate(GLYPHS),key)
                self.assertNotIn('公式日本語名確認済み',entry['basis'])

    def test_unresolved_old_exonyms_are_not_guessed(self):
        entries=json.loads((ROOT/'docs/world-native-name-review.json').read_text(encoding='utf-8'))
        for key in ['1842754','1840379']:
            self.assertEqual(entries['GeoNames:'+key]['decision'],'hold')

    def test_coordinate_decisions_preserve_distance_and_quality_holds(self):
        report=json.loads((ROOT/'docs/world-coordinate-name-review.json').read_text(encoding='utf-8'))
        geod=Geod(ellps='WGS84')
        self.assertEqual(len(report['items']),60)
        for r in report['items']:
            if r['decision']=='adopt':
                ref=r['reference']
                self.assertLessEqual(geod.inv(*r['coordinates'],ref['lon'],ref['lat'])[2],2500)
                self.assertTrue(r['name'].endswith('付近'))
            elif r['peak']=='31.878, 53.438':
                self.assertEqual(r['poi_cluster_evidence']['max_coincident_records'],412)
                self.assertIn('誤位置と断定',r['reason'])

    def test_held_peak_facilities_and_border_references(self):
        report=json.loads((ROOT/'docs/held-peak-investigation.json').read_text(encoding='utf-8'))
        self.assertEqual(len(report['items']),18)
        rows={r['peak']:r for r in report['items']}
        self.assertEqual(rows['28.649, 48.369']['reference']['country'],'KW')
        self.assertEqual(rows['28.649, 48.369']['active_poi_count'],587)
        for peak,source in [('19.031, 99.890','OpenStreetMap:way/579088013'),('-4.109, 137.101','OpenStreetMap:way/505668631'),('26.146, 50.092','Official:pmu-contact-map')]:
            self.assertEqual(rows[peak]['source_id'],source)
            self.assertLessEqual(rows[peak]['reference_distance_m'],2500)
        self.assertEqual(rows['39.062, 35.124']['classification'],'location_quality')
        self.assertEqual(sum(r['decision']=='adopt' for r in rows.values()),5)

if __name__=='__main__':unittest.main()
