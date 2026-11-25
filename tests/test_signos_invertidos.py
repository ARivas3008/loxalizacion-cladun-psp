"""Regression for 16x16 Spanish inverted punctuation; no commercial assets."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from font_es_patch import make_glyph

class InvertedPunctuationTests(unittest.TestCase):
    def test_question_and_exclamation_keep_original_left_bearing(self):
        for ch in "¿¡":
            with self.subTest(mark=ch):
                original = [[0] * 16 for _ in range(16)]
                original[6][0] = 15
                original[7][1] = 15
                result = make_glyph(original, ch)
                xcoords = [x for row in result for x,v in enumerate(row) if v]
                self.assertEqual(min(xcoords), 0)
                self.assertEqual(max(xcoords), 1)
                self.assertTrue(all(not any(row[8:]) for row in result))

    def test_input_is_immutable(self):
        src = [[0] * 16 for _ in range(16)]
        src[3][0] = 15
        before = [row[:] for row in src]
        for mark in "¿¡":
            make_glyph(src, mark)
        self.assertEqual(src, before)

if __name__ == "__main__":
    unittest.main()
