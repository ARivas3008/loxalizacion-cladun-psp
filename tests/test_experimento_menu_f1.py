#!/usr/bin/env python3
"""F1: pruebas de conservación de espacios y métrica (sin assets PSP)."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from experimento_menu_f1 import (
    PREFIX_IDS, SUFFIX_IDS, TARGET_IDS, advance, match_suffix_width,
    preserve_prefix, variant, load_metrics_snapshot, build,
    read_rows, SOURCE, DRAFT,
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



class TestSnapshotSinISO(unittest.TestCase):
    """Generación CI con métricas derivadas, sin afirmar que se ejecutó la ISO."""
    SNAPSHOT = Path(__file__).resolve().parents[1] / "reports/menu_f1_metricas_subconjunto_2026-11-20.json"

    def test_snapshot_matches_five_font_advances(self):
        metrics, font_hash = load_metrics_snapshot(self.SNAPSHOT)
        self.assertEqual(font_hash,
                         "1f1f5692fecb3b4a66c50f4b20191c1f2658a32ca1220902a5888ae9a11afb46")
        for gid, (original, spanish, width) in {
            "005695": ("\u3000\u3000\u3000 Retro", "Retro", 85),
            "005696": ("\u3000\u3000\u3000  Real", "     Real", 83),
            "005697": ("          %2d ", "%2d", 99),
            "005698": ("Run" + "\u3000" * 10, "Correr          ", 170),
            "005709": ("Show decimal points for damage" + "\u3000" * 7,
                       "Decimales de daño", 303),
        }.items():
            with self.subTest(gid=gid):
                self.assertEqual(advance(original, metrics), width)
                self.assertEqual(advance(variant(original, spanish, gid, metrics), metrics),
                                 width)

    def test_generates_alternative_csv_without_mutating_9237_records(self):
        _, draft = read_rows(DRAFT)
        with tempfile.TemporaryDirectory(prefix="cladun-menu-f1-") as temp:
            csv_out = Path(temp) / "variante.csv"
            json_out = Path(temp) / "variante.json"
            report = build(SOURCE, DRAFT, None, csv_out, json_out,
                           ("005709",), metricas_snapshot=self.SNAPSHOT)
            self.assertEqual(report["numero_registros"], 9237)
            self.assertFalse(report["metricas_verificadas_con_iso_esta_ejecucion"])
            self.assertEqual([x["grupo_id"] for x in report["filas_cambiadas"]],
                             ["005709"])
            _, variant_rows = read_rows(csv_out)
            self.assertEqual(len(variant_rows), len(draft))
            delta = []
            for before, after in zip(draft, variant_rows):
                differences = [key for key in before if before[key] != after[key]]
                if differences:
                    delta.append((before["grupo_id"], differences))
            self.assertEqual(delta, [("005709", ["espanol"])])
            with self.assertRaises(FileExistsError):
                build(SOURCE, DRAFT, None, csv_out, json_out,
                      ("005709",), metricas_snapshot=self.SNAPSHOT)

if __name__ == "__main__":
    unittest.main()
