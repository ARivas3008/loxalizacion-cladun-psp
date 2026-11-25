"""ONLY SYNTHETIC pixel arrays: does not assert PPSSPP was run."""
import hashlib
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools import f2_tuika_proteger_subregiones as g

SIZE=256*256
BASE=bytes(SIZE)

def position(x,y):return 256*y+x

def changed(x,y,value=2):
    z=bytearray(BASE);z[position(x,y)]=value
    return bytes(z)

class TestTuikaRegionProtection(unittest.TestCase):
    def test_partitions_are_fully_bounded(self):
        for _,x0,y0,x1,y1,_,_ in g.REGIONS:
            self.assertTrue(0<=x0<=x1<256 and 0<=y0<=y1<256)
    def test_control_icons_explicitly_locked(self):
        self.assertIn(position(95,190),g.protected_pixel_positions())
    def test_digits_row12_locked(self):
        self.assertIn(position(3,222),g.protected_pixel_positions())
    def test_digits_row13_locked(self):
        self.assertIn(position(70,242),g.protected_pixel_positions())
    def test_mixed_japanese_band_locked(self):
        self.assertIn(position(200,10),g.protected_pixel_positions())
    def test_band13_label_not_preapproved(self):
        self.assertNotIn(position(120,242),g.protected_pixel_positions())
    def test_gap_band13_locked(self):
        self.assertIn(position(110,243),g.protected_pixel_positions())
    def test_gap_band10_locked(self):
        self.assertIn(position(86,188),g.protected_pixel_positions())
    def test_default_no_changes_allowed(self):
        with self.assertRaises(ValueError):g.guard_candidate(BASE,changed(120,242))
    def test_explicit_allowed_text_pixel_synthetic(self):
        dest=position(120,242)
        r=g.guard_candidate(BASE,changed(120,242),frozenset((dest,)))
        self.assertEqual(r['changed_pixel_count'],1)
        self.assertFalse(r['gameplay_or_translation_safety_proven'])
    def test_approved_cannot_overlap_digit_lock(self):
        with self.assertRaises(ValueError):g.guard_candidate(BASE,BASE,frozenset((position(70,242),)))
    def test_approved_cannot_overlap_symbols_lock(self):
        with self.assertRaises(ValueError):g.guard_candidate(BASE,BASE,frozenset((position(95,190),)))
    def test_approved_cannot_overlap_gap(self):
        with self.assertRaises(ValueError):g.guard_candidate(BASE,BASE,frozenset((position(110,240),)))
    def test_unauthorized_other_changes_denied(self):
        with self.assertRaises(ValueError):g.guard_candidate(BASE,changed(250,252),frozenset((position(120,242),)))
    def test_candidate_invalid_index(self):
        with self.assertRaises(ValueError):g.guard_candidate(BASE,changed(120,242,16))
    def test_candidate_invalid_size(self):
        with self.assertRaises(ValueError):g.guard_candidate(BASE,BASE[:-1])
    def test_approved_mask_must_be_frozenset(self):
        with self.assertRaises(ValueError):g.guard_candidate(BASE,BASE,{position(120,242)})
    def test_approved_mask_bounds(self):
        with self.assertRaises(ValueError):g.guard_candidate(BASE,BASE,frozenset((SIZE,)))
    def test_approved_mask_boolean_forbidden(self):
        with self.assertRaises(ValueError):g.guard_candidate(BASE,BASE,frozenset((True,)))
    def test_protected_unchanged_no_modification(self):
        r=g.guard_candidate(BASE,BASE)
        self.assertEqual(r['changed_pixel_count'],0)
        self.assertTrue(r['no_unauthorized_pixel_change'])
    def test_crop_row_major(self):
        arr=bytearray(BASE);arr[position(1,3)]=7;arr[position(2,3)]=5
        self.assertEqual(g.crop_indices(bytes(arr),1,3,2,3),bytes([7,5]))
    def test_crop_refuses_invalid_bbox(self):
        with self.assertRaises(ValueError):g.crop_indices(BASE,20,3,10,5)
    def test_analyzer_empty_synthetic_not_authenticated(self):
        r=g.analyze_indexed(BASE,strict_original=False)
        self.assertFalse(r['any_editing_roi_approved'])
        self.assertFalse(r['runtime_texture_use_proven'])
        self.assertEqual(r['measured_region_count'],7)
    def test_analyzer_fail_closed_real_authentication(self):
        with self.assertRaises(ValueError):g.analyze_indexed(BASE,strict_original=True)
    def test_all_gaps_empty_synthetic(self):
        self.assertTrue(all(x['all_index0_transparent'] for x in g.analyze_indexed(BASE,strict_original=False)['separating_gaps']))
    def test_private_json_relative_rejected(self):
        with self.assertRaises(ValueError):g.validate_private_output(Path('relative.json'))
    def test_private_json_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);target=base/'real.json';link=base/'ln.json';link.symlink_to(target)
            with self.assertRaises(ValueError):g.validate_private_output(link,base/'checkout')
    def test_private_json_overwrite_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'exists.json';p.write_text('persist')
            with self.assertRaises(FileExistsError):g.validate_private_output(p,Path('/tmp/repo-other'))
            self.assertEqual(p.read_text(),'persist')
    def test_private_json_checkout_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            r=Path(d)
            with self.assertRaises(ValueError):g.validate_private_output(r/'inside.json',r)
    def test_private_json_nested_git_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'.git').mkdir()
            with self.assertRaises(ValueError):g.validate_private_output(p/'private.json',Path('/tmp/repo-other'))
    def test_default_sha_real_hex_lengths(self):
        for v in (g.ISO_SHA,g.MEMBER_SHA,g.INDEX_DECODED_SHA,g.LINEAR_PIXEL_INDEX_SHA,g.MASK_SHA):
            self.assertEqual(len(v),64);int(v,16)
    def test_no_embedded_commercial_data(self):
        self.assertTrue(all(len(t[6])==64 for t in g.REGIONS))

if __name__ == '__main__':unittest.main()
