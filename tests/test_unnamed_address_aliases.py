"""Regression: blank locality must never match blank GeoNames aliases."""
import sys, tempfile, unittest, zipfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import audit_unnamed_world_addresses as audit

class AliasTests(unittest.TestCase):
    def test_empty_aliases_are_not_place_matches(self):
        with tempfile.TemporaryDirectory(dir='data/validation') as folder:
            root=Path(folder)
            fields=['123','Example Town','Example Town','','1','2','P','PPL','ZZ','','01','','','','10','','','UTC','2026-01-01']
            with zipfile.ZipFile(root/'ZZ.zip','w') as archive:archive.writestr('ZZ.txt','\t'.join(fields)+'\n')
            previous=audit.GAZ;audit.GAZ=root
            try:
                refs,source=audit.references(('ZZ',{'','exampletown'}))
                self.assertNotIn('',refs)
                self.assertEqual(refs['exampletown'][0]['id'],'123')
                self.assertEqual(source['status'],'complete')
            finally:audit.GAZ=previous
    def test_missing_country_is_reported_without_abort(self):
        refs,source=audit.references((None,{'town'}))
        self.assertEqual(refs,{})
        self.assertEqual(source['status'],'unsupported_country_code')

if __name__=='__main__':unittest.main()
