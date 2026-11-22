"""Synthetic F2 controls; do not call them real PPSSPP screenshots."""
from pathlib import Path
import sys, unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from font_es_narrow import whiten_new_glyph_pixels

class TestF2Ink(unittest.TestCase):
    def test_pure_white_ink_replacement_only_15(self):
        old=[[0,1,15,3],[7,15,1,0]]
        snapshot=[row[:] for row in old]
        self.assertEqual(whiten_new_glyph_pixels(old),[[0,1,1,3],[7,1,1,0]])
        self.assertEqual(old,snapshot)
    def test_no_new_yellow_index_remains(self):
        old=[[15 if (x+y)%3==0 else (1 if x%2 else 0) for x in range(16)] for y in range(16)]
        out=whiten_new_glyph_pixels(old)
        self.assertEqual(sum(p==15 for row in out for p in row),0)
        self.assertEqual(sum(p!=q for a,b in zip(old,out) for p,q in zip(a,b)),
                         sum(p==15 for row in old for p in row))
