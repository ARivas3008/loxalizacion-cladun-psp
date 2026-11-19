#!/usr/bin/env python3
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'tools'))
from iso_guard_global import spans_from_args,exact_except

class GuardTextTests(unittest.TestCase):
    def test_reject_overlapping_ranges(self):
        with self.assertRaises(ValueError):
            spans_from_args(['SCRIPT.SDT/SCRIPT.DAT:10:4','SCRIPT.SDT/SCRIPT.DAT:13:5'])
    def test_reject_tiles_portraits_and_unmodelled_tables(self):
        for path in ('PORTRAIT.ARC/PIC.DAT:0:8','MAP.ARC/TILE.DAT:3:5','DATABASE.DAT/WEAPON.DAT:0:4'):
            with self.assertRaises(ValueError):
                spans_from_args([path])
    def test_reject_font_edits(self):
        with self.assertRaises(ValueError):
            spans_from_args(['FONT.ARC/FONT.BIN:0:4'])
    def test_unchanged_outside_one_span(self):
        self.assertEqual(exact_except(b'123456',b'12ABC6',[(2,5)],'demo'),3)
        with self.assertRaises(ValueError):
            exact_except(b'123456',b'12ABCX',[(2,5)],'demo')

if __name__=='__main__':unittest.main()
