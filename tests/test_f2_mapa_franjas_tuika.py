"""All fixtures are SYNTHETIC, not screenshots of Cladun / PPSSPP."""
import hashlib, tempfile, unittest, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from f2_mapa_franjas_tuika import analyze_strips, safe_private_json

class ModuleFacade:
    analyze_strips = staticmethod(analyze_strips)
    safe_private_json = staticmethod(safe_private_json)
mod = ModuleFacade()

def fixture(w=10,h=8):
    m=bytearray(w*h)
    for y in (1,2,5,6):
        for x in (2,3,4):m[y*w+x]=255
    return bytes(m)

class TestMaskGeometry(unittest.TestCase):
    def test_bands_count(self):
        self.assertEqual(mod.analyze_strips(fixture(),10,8,strict_real=False)['stripe_count'],2)
    def test_exact_extent(self):
        s=mod.analyze_strips(fixture(),10,8,strict_real=False)['stripes'][0]
        self.assertEqual((s['y_first'],s['y_last_inclusive'],s['x_first_clut2'],s['x_last_clut2_inclusive']),(1,2,2,4))
    def test_gap(self):
        s=mod.analyze_strips(fixture(),10,8,strict_real=False)['stripes']
        self.assertEqual(s[0]['blank_rows_after'],2)
        self.assertEqual(s[1]['blank_rows_before'],2)
    def test_pixel_sum(self):
        r=mod.analyze_strips(fixture(),10,8,strict_real=False)
        self.assertEqual(r['total_clut2_pixels'],12)
        self.assertEqual(sum(x['pixels_clut2'] for x in r['stripes']),12)
    def test_hash_fingerprint(self):
        r=mod.analyze_strips(fixture(),10,8,strict_real=False)
        self.assertEqual(r['mask_sha256'],hashlib.sha256(fixture()).hexdigest())
    def test_occupied_x_runs(self):
        m=bytearray(7*5);m[7+0]=m[7+1]=m[7+4]=255
        s=mod.analyze_strips(bytes(m),7,5,strict_real=False)['stripes'][0]
        self.assertEqual(s['horizontal_occupied_runs'],2)
    def test_single_row(self):
        m=bytes([0,255,0,0]);self.assertEqual(mod.analyze_strips(m,4,1,strict_real=False)['stripe_count'],1)
    def test_active_bottom_row(self):
        m=bytes([0]*7+[255]);s=mod.analyze_strips(m,4,2,strict_real=False)['stripes'][0]
        self.assertEqual(s['blank_rows_after'],0)
    def test_refuse_nondense_width(self):
        with self.assertRaises(ValueError):mod.analyze_strips(fixture(),10,9,strict_real=False)
    def test_refuse_nonbinary(self):
        with self.assertRaises(ValueError):mod.analyze_strips(bytes([0,2,0,255]),2,2,strict_real=False)
    def test_refuse_empty(self):
        with self.assertRaises(ValueError):mod.analyze_strips(bytes(10),5,2,strict_real=False)
    def test_refuse_bad_type(self):
        with self.assertRaises(ValueError):mod.analyze_strips(bytearray(fixture()),10,8,strict_real=False)
    def test_refuse_bad_dimensions(self):
        with self.assertRaises(ValueError):mod.analyze_strips(bytes([255]),0,1,strict_real=False)
    def test_real_authenticity_rejects_synthetic(self):
        with self.assertRaises(ValueError):mod.analyze_strips(fixture(),10,8)
    def test_safe_report_refuses_relative(self):
        with self.assertRaises(ValueError):mod.safe_private_json(Path('report.json'))
    def test_safe_report_refuses_inside_git(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'.git').mkdir()
            with self.assertRaises(ValueError):mod.safe_private_json(p/'report.json',p/'some_other_repo')
    def test_safe_report_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/'exists.json';path.touch()
            with self.assertRaises(FileExistsError):mod.safe_private_json(path,Path('/tmp/otherrepo'))
    def test_no_claim_safe_translation(self):
        r=mod.analyze_strips(fixture(),10,8,strict_real=False)
        self.assertFalse(r['text_identity_per_band_proven'])
        self.assertFalse(r['translation_safe_rois_proven'])
        self.assertFalse(r['runtime_visibility_proven'])
if __name__=='__main__':unittest.main()
