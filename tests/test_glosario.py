#!/usr/bin/env python3
"""Integridad del glosario y de términos sensibles del borrador."""
import csv
from pathlib import Path
import unittest

BASE = Path(__file__).resolve().parents[1]


def read(path):
    with path.open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


class GlossaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.glossary = read(BASE / "traduccion/GLOSARIO_CANONICO.csv")
        cls.draft = read(BASE / "traduccion/CLADUN_BORRADOR_ES.csv")

    def test_canonico_unico_y_consistente(self):
        terms = [row["original"] for row in self.glossary]
        self.assertEqual(len(terms), len(set(terms)))
        self.assertGreaterEqual(len(terms), 60)
        terms_map = {row["original"]: row["espanol"] for row in self.glossary}
        for en, es in {
            "Pudding": "Pudding", "Widen": "Widen",
            "New-geon": "New-geon", "Ran-geon": "Ran-geon",
            "Magic Circle": "Círculo mágico", "Job": "clase",
            "Ward": "Protección", "Sub Character": "personaje de apoyo",
        }.items():
            self.assertEqual(terms_map[en], es)

    def test_ward_no_se_traduce_como_pabellon(self):
        effects = [r for r in self.draft if r["original"] == "Ward"]
        self.assertEqual(len(effects), 3)
        self.assertTrue(all(r["espanol"] == "Protección" for r in effects))

    def test_nombre_propio_new_geon_en_dialogos(self):
        entries = [r for r in self.draft
                   if "New-geon" in r["original"] and r["tipo"] in ("dialogo", "opcion")]
        self.assertTrue(entries)
        self.assertTrue(all("New-geon" in r["espanol"] for r in entries))


if __name__ == "__main__":
    unittest.main()
