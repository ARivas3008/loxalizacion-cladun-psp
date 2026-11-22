"""Synthetic-only 4bpp/CLUT effect QA: NO original game assets in fixtures."""
from pathlib import Path
import hashlib
import struct
import tempfile
import unittest
from tools import f2_cotejar_impacto_clut_tuika as p

def synthetic_member(stride=16,rows=8):
    total=stride*rows
    raw=bytearray(98)
    raw[:4]=b'IMY\0';raw[4]=0x60;raw[10]=0xA4
    struct.pack_into('<H',raw,8,stride)
    struct.pack_into('<H',raw,12,rows)
    for i in range(16):raw[32+i*4:36+i*4]=bytes((i,i,i,255))
    raw[40:44]=bytes(p.ORIGINAL_RGBA)
    # Four 32-byte literal commands reconstruct one synthetic 16-byte x8 PSP tile.
    flags=b'\x0f'*(total//32)
    literals=bytes((0x12,0x20))*(total//2)
    original=bytes(raw[:96])+struct.pack('<H',len(flags))+flags+literals
    probe=bytearray(original);probe[40:43]=bytes(p.PROBE_RGBA[:3])
    return original,bytes(probe)

class TestCLUTCounterfactual(unittest.TestCase):
    def test_palette_only_validated(self):
        a,b=synthetic_member();p.verify_palette_only_change(a,b)
    def test_wrong_rgb_rejected(self):
        a,b=synthetic_member();b=bytearray(b);b[40]=0
        with self.assertRaisesRegex(ValueError,'palette'):
            p.verify_palette_only_change(a,bytes(b))
    def test_wrong_alpha_rejected(self):
        a,b=synthetic_member();b=bytearray(b);b[43]=0
        with self.assertRaisesRegex(ValueError,'palette'):
            p.verify_palette_only_change(a,bytes(b))
    def test_other_image_data_rejected(self):
        a,b=synthetic_member();b=bytearray(b);b[-1]^=1
        with self.assertRaisesRegex(ValueError,'outside'):
            p.verify_palette_only_change(a,bytes(b))
    def test_unsupported_format_rejected(self):
        a,b=synthetic_member();a=bytearray(a);a[10]=0x84
        with self.assertRaisesRegex(ValueError,'Unsupported'):
            p.verify_palette_only_change(bytes(a),b)
    def test_synthetic_counts_and_mask(self):
        a,b=synthetic_member()
        r,mask,_,_=p.compare_members(a,b,enforce_real_sha=False)
        self.assertEqual(r['texture_dimensions_px'],[32,8])
        self.assertEqual(r['source_index_histogram'][2],128)
        self.assertEqual(r['counterfactual_changed_pixel_count'],128)
        self.assertEqual(r['all_unchanged_pixel_count'],128)
        self.assertEqual(len(mask),256)
        self.assertEqual(r['rows_with_affected_pixels'],8)
        self.assertFalse(r['gameplay_ppsspp_executed'])
    def test_source_decode_is_unchanged(self):
        a,b=synthetic_member()
        r,_,linear,_=p.compare_members(a,b,enforce_real_sha=False)
        self.assertTrue(r['indices_unchanged_between_isos'])
        self.assertEqual(r['decoded_pixel_index_sha256'],hashlib.sha256(linear).hexdigest())
    def test_wrong_real_sha_fails_closed(self):
        a,b=synthetic_member()
        with self.assertRaisesRegex(ValueError,'SHA'):p.compare_members(a,b)
    def test_row_band_aggregation(self):
        spans=[(2,2),(1,4),None,(5,7),None]
        rows=[1,2,0,3,0]
        self.assertEqual(p.group_active_rows(rows,spans),[
          {'y_start':0,'y_end_inclusive':1,'pixel_count':3,'x_min':1,'x_max_inclusive':4},
          {'y_start':3,'y_end_inclusive':3,'pixel_count':3,'x_min':5,'x_max_inclusive':7}])
    def test_trailing_band(self):
        self.assertEqual(len(p.group_active_rows([0,1],[None,(0,1)])),1)
    def test_no_band(self):
        self.assertEqual(p.group_active_rows([0,0],[None,None]),[])
    def test_invalid_rows_inconsistent(self):
        with self.assertRaisesRegex(ValueError,'inconsistent'):
            p.group_active_rows([1],[None])
    def test_invalid_row_extent_len(self):
        with self.assertRaisesRegex(ValueError,'geometry'):
            p.group_active_rows([1],[])
    def test_report_private_absolute_only(self):
        with self.assertRaisesRegex(ValueError,'absolute'):
            p.validate_private_output(Path('relative.json'))
    def test_report_inside_repository_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'repo').mkdir()
            with self.assertRaisesRegex(ValueError,'GitHub checkout'):
                p.validate_private_output(root/'repo'/'r.json',repository_root=root/'repo')
    def test_symlink_into_repository_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'repo').mkdir()
            (root/'alias').symlink_to(root/'repo')
            with self.assertRaisesRegex(ValueError,'GitHub checkout'):
                p.validate_private_output(root/'alias'/'r.png',repository_root=root/'repo',
                                          extension='.png')
    def test_private_image_not_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'existing.png').write_bytes(b'X')
            with self.assertRaises(FileExistsError):
                p.validate_private_output(root/'existing.png',repository_root=root/'repo',
                                          extension='.png')
    def test_original_probe_paths_must_differ(self):
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/'same.iso';f.write_bytes(b'')
            with self.assertRaisesRegex(ValueError,'different'):
                p.inspect_source_and_probe(f,f)
    def test_expected_true_64hex(self):
        self.assertEqual(len(p.SOURCE_SHA),64)
        self.assertEqual(len(p.PROBE_SHA),64)
        self.assertEqual(p.MEMBER_ABSOLUTE,114744832)
