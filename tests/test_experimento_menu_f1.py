#!/usr/bin/env python3
"""F1: pruebas de conservación de espacios y métrica (sin assets PSP)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from experimento_menu_f1 import (
    PREFIX_IDS, SUFFIX_IDS, TARGET_IDS, advance, match_suffix_width,
    preserve_prefix, variant,
)
from charset_es import encode_spanish


def sample_metrics(*texts):
    codes = {0x8140: 15}
    for text in texts:
        for char in text:
            raw = encode_spanish(char)
            value = raw[0] if len(raw) == 1 else (raw[0] << 8) | raw[1]
            codes[value] = 15 if char == "\u3000" else 7
    return codes


class TestMenuF1(unittest.TestCase):
    ORIGINAL = {
        "005695": "\u3000\u3000\u3000 Retro",
        "005696": "\u3000\u3000\u3000  Real",
        "005697": "          %2d ",
        "005698": "Run" + "\u3000" * 10,
        "005709": "Show decimal points for damage" + "\u3000" * 7,
    }
    SPANISH = {
        "005695": "Retro",
        "005696": "     Real",
        "005697": "%2d",
        "005698": "Correr          ",
        "005709": "Decimales de daño",
    }

    def setUp(self):
        self.metrics = sample_metrics(*self.ORIGINAL.values(),
                                      *self.SPANISH.values())

    def test_five_original_string_widths_preserved_by_variants(self):
        self.assertEqual(set(TARGET_IDS), set(self.ORIGINAL))
        for gid in TARGET_IDS:
            with self.subTest(gid=gid):
                original = self.ORIGINAL[gid]
                proposed = variant(original, self.SPANISH[gid],
                                   gid, self.metrics)
                self.assertEqual(advance(original, self.metrics),
                                 advance(proposed, self.metrics))
                self.assertNotEqual(proposed, self.SPANISH[gid])
                self.assertIn(self.SPANISH[gid].strip(), proposed)

    def test_only_prefix_ids_keep_original_leading_padding(self):
        for gid in PREFIX_IDS:
            with self.subTest(gid=gid):
                original = self.ORIGINAL[gid]
                proposed = variant(original, self.SPANISH[gid],
                                   gid, self.metrics)
                self.assertTrue(proposed.startswith(original[:len(original) -
                                                      len(original.lstrip(" \u3000"))]))
        self.assertEqual(preserve_prefix("          %2d ", "%2d"),
                         "          %2d ")

    def test_suffix_padding_does_not_replace_spanish_translation(self):
        for gid in SUFFIX_IDS:
            with self.subTest(gid=gid):
                proposed = match_suffix_width(self.ORIGINAL[gid],
                                               self.SPANISH[gid], self.metrics)
                self.assertEqual(proposed.rstrip(" \u3000"),
                                 self.SPANISH[gid].strip(" \u3000"))

    def test_refuse_placeholder_mismatch(self):
        with self.assertRaises(ValueError):
            preserve_prefix("          %2d ", "%s")

    def test_refuse_new_padding_where_original_had_none(self):
        with self.assertRaises(ValueError):
            match_suffix_width("Attack", "Ataque", self.metrics)

    def test_refuse_outside_menu_ids(self):
        with self.assertRaises(ValueError):
            variant("Original", "Español", "005687", self.metrics)


if __name__ == "__main__":
    unittest.main()
