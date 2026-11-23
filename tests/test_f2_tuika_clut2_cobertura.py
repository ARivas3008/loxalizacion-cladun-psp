"""Pruebas B sintéticas: NO emplean ISO, capturas ni PPSSPP."""
from __future__ import annotations
import sys,tempfile,unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import f2_tuika_clut2_cobertura as t


def raster(*coords):
    raw=bytearray(t.WIDTH*t.HEIGHT)
    for x,y in coords:raw[y*t.WIDTH+x]=2
    return bytes(raw)


class CLUT2CoverageTests(unittest.TestCase):
    def test_counts_protected_and_outside(self):
        a=t.summarize_indices(raster((2,2),(94,182),(5,220),(240,249),(250,250)))
        self.assertEqual(a['index2_pixels_affected'],5)
        self.assertEqual(a['index2_affected_in_all_seven_protected_regions'],4)
        self.assertEqual(a['index2_affected_in_strictly_locked_regions_and_gaps'],3)
        self.assertEqual(a['index2_affected_outside_seven_regions_and_gaps'],1)
        self.assertEqual(a['index2_affected_bbox_xyxy_inclusive'],[2,2,250,250])
        self.assertEqual(sum(a['by_16_atlas_rows']),5)
        self.assertFalse(a['clut_global_change_is_safe_translation_edit'])
        self.assertFalse(a['atlas_pixels_proven_to_be_rendered_in_game'])
        self.assertTrue(a['protected_icons_and_digits_can_change_color_if_rendered'])

    def test_empty_raster_is_not_false_positive(self):
        a=t.summarize_indices(bytes(t.WIDTH*t.HEIGHT))
        self.assertEqual(a['index2_pixels_affected'],0)
        self.assertIsNone(a['index2_affected_bbox_xyxy_inclusive'])
        self.assertEqual(a['index2_affected_fraction_of_atlas'],0)
        self.assertFalse(a['protected_icons_and_digits_can_change_color_if_rendered'])

    def test_histogram_nibble_indices(self):
        raw=bytearray(t.WIDTH*t.HEIGHT)
        raw[0]=1;raw[1]=2;raw[2]=15
        h=t.summarize_indices(bytes(raw))['index_histogram']
        self.assertEqual(h['0'],t.WIDTH*t.HEIGHT-3)
        self.assertEqual(h['1'],1)
        self.assertEqual(h['2'],1)
        self.assertEqual(h['15'],1)

    def test_reject_incorrect_raster_length(self):
        with self.assertRaises(ValueError):t.summarize_indices(b'\x00'*14)

    def test_reject_nonindexed_value(self):
        raw=bytearray(t.WIDTH*t.HEIGHT);raw[0]=16
        with self.assertRaises(ValueError):t.summarize_indices(bytes(raw))

    def test_reject_nonbytes_array(self):
        with self.assertRaises(ValueError):t.summarize_indices(bytearray(t.WIDTH*t.HEIGHT))

    def test_reject_nontransparent_separator(self):
        name,x0,y0,x1,y1=t.GAPS[0]
        with self.assertRaises(ValueError):t.summarize_indices(raster((x0,y0)))

    def test_region_counts_are_consistent(self):
        a=t.summarize_indices(raster((2,2),(94,182),(5,220)))
        impacted={r['region']:r['index2_pixels_affected'] for r in a['affected_counts_per_protected_region']}
        self.assertEqual(impacted['band00_mixed_japanese'],1)
        self.assertEqual(impacted['band10_control_icons'],1)
        self.assertEqual(impacted['band12_digits_0_to_9'],1)
        self.assertEqual(sum(impacted.values()),3)
        self.assertTrue(all(not r['region_edit_authorized'] for r in a['affected_counts_per_protected_region']))

    def test_output_path_outside_checkout_valid(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);repo=root/'repo';repo.mkdir()
            self.assertEqual(t.private_target(root/'outside.json',repo),root/'outside.json')

    def test_output_path_in_checkout_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            repo=Path(d)/'repo';repo.mkdir()
            with self.assertRaises(ValueError):t.private_target(repo/'inside.json',repo)

    def test_output_overwrite_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);repo=root/'repo';repo.mkdir()
            out=root/'existing.json';out.write_text('keep')
            with self.assertRaises(ValueError):t.private_target(out,repo)
            self.assertEqual(out.read_text(),'keep')

    def test_output_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);repo=root/'repo';repo.mkdir()
            orig=root/'a.json';orig.write_text('keep')
            link=root/'link.json';link.symlink_to(orig)
            with self.assertRaises(ValueError):t.private_target(link,repo)

    def test_output_suffix_and_absolute_required(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);repo=root/'repo';repo.mkdir()
            for p in (Path('relative.json'),root/'data.png'):
                with self.subTest(path=str(p)),self.assertRaises(ValueError):
                    t.private_target(p,repo)

    def test_output_other_git_repo_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);repo=root/'repo';repo.mkdir()
            other=root/'other';(other/'.git').mkdir(parents=True)
            with self.assertRaises(ValueError):t.private_target(other/'report.json',repo)


if __name__=='__main__':unittest.main()
