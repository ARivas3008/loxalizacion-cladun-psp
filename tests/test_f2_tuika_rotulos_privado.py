"""SYNTHETIC raster fixtures; tests do NOT claim PPSSPP or game rendering."""
from __future__ import annotations
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import f2_tuika_rotulos_privado as mod


def sample():
    # 8x5 synthetic: whites separated by index1 black for bbox collision.
    idx=[0]*40
    idx[8+1]=2;idx[8+2]=1;idx[8+3]=2
    idx[16+1]=2;idx[16+2]=1;idx[16+3]=2
    idx[32+4]=2
    return idx


LABELS=(('message','FAKE message', 'BORRADOR NO JUGABLE'),('digits','FAKE digits',None))


class TuikaVisualInventoryTests(unittest.TestCase):
    def run_sample(self):
        return mod.inspect_indices(sample(),8,5,LABELS,strict=False)
    def test_two_synthetic_bands(self):
        self.assertEqual(self.run_sample()['stripe_count'],2)
    def test_total_white(self):
        self.assertEqual(self.run_sample()['clut2_pixels'],5)
    def test_mask_sha(self):
        m=bytes(255 if x==2 else 0 for x in sample())
        self.assertEqual(self.run_sample()['clut2_mask_sha256'],hashlib.sha256(m).hexdigest())
    def test_region_clut1_black_count(self):
        r=self.run_sample()['stripes'][0]
        self.assertEqual(r['clut1_opaque_black_pixels_inside_bbox'],2)
    def test_region_pixel_coverage(self):
        r=self.run_sample()['stripes'][0]
        self.assertEqual(r['bbox_pixel_count'],6)
        self.assertEqual(r['non_clut2_pixels_inside_bbox'],2)
    def test_classification(self):
        self.assertEqual(self.run_sample()['visual_category_counts'],{'digits':1,'message':1})
    def test_source_unverified_by_gameplay(self):
        self.assertFalse(self.run_sample()['visual_transcriptions_verified_by_gameplay'])
    def test_no_real_emulator_claim(self):
        self.assertFalse(self.run_sample()['ppsspp_1204_ran'])
    def test_no_bitmap_export(self):
        self.assertFalse(self.run_sample()['bitmap_indices_or_pixels_exported'])
    def test_draft_not_applied(self):
        self.assertFalse(self.run_sample()['translations_applied_to_iso'])
    def test_each_band_bbox_blocked(self):
        for v in self.run_sample()['stripes']:
            self.assertFalse(v['safe_to_replace_whole_band'])
            self.assertFalse(v['safe_to_replace_bbox'])
            self.assertFalse(v['safe_to_replace_clut2_only'])
    def test_label_count_rejected(self):
        with self.assertRaises(ValueError):mod.inspect_indices(sample(),8,5,LABELS[:1],strict=False)
    def test_wrong_surface_size_rejected(self):
        with self.assertRaises(ValueError):mod.inspect_indices(sample(),8,6,LABELS,strict=False)
    def test_bad_index_rejected(self):
        idx=sample();idx[0]=16
        with self.assertRaises(ValueError):mod.inspect_indices(idx,8,5,LABELS,strict=False)
    def test_bool_index_rejected(self):
        idx=sample();idx[0]=True
        with self.assertRaises(ValueError):mod.inspect_indices(idx,8,5,LABELS,strict=False)
    def test_empty_mask_rejected(self):
        with self.assertRaises(ValueError):mod.inspect_indices([0]*40,8,5,LABELS,strict=False)
    def test_private_reject_relative(self):
        with self.assertRaises(ValueError):mod.verify_output(Path('new.json'))
    def test_private_reject_git_checkout(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with self.assertRaises(ValueError):mod.verify_output(root/'r.json',root)
    def test_private_reject_any_git_workspace(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'.git').mkdir()
            with self.assertRaises(ValueError):mod.verify_output(root/'r.json',Path('/tmp/nonexistent12345'))
    def test_private_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'r.json';p.write_text('do not delete')
            with self.assertRaises(FileExistsError):mod.verify_output(p,Path('/tmp/nonexistent12345'))
    def test_14_visual_labels_have_explicit_uncertainty(self):
        self.assertEqual(len(mod.LABELS),14)
        self.assertTrue(any(k=='mixed_digits_message' for k,_,_ in mod.LABELS))
        self.assertTrue(any(k=='control_symbols' for k,_,_ in mod.LABELS))
    def test_source_english_and_es_are_not_dangerously_equal(self):
        for kind,src,es in mod.LABELS:
            self.assertNotEqual(src,es)
    def test_strict_auth_rejects_synthetic(self):
        with self.assertRaises(ValueError):mod.inspect_indices(sample(),8,5,LABELS,strict=True)


if __name__ == '__main__':unittest.main()
