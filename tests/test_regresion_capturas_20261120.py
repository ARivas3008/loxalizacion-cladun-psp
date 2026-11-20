#!/usr/bin/env python3
"""Regresión de las capturas del 20/11/2026 (revisión estática, no PPSSPP).

La longitud máxima es una cota conservadora para rótulos compartidos con un
valor ON/OFF. Esta prueba NO equivale a medir píxeles con la fuente del juego.
"""
import csv
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from charset_es import encode_spanish, decode_spanish

EXPECTED = {
    "000778": "Así que esto es Arcanus Cella, ¡la tierra prohibida!",
    "000792": "Tus padres",
    "000793": "me pidieron que te cuidara.",
    "000794": "Si no, nunca habría faltado a clase",
    "000795": "para venir hasta aquí.",
    "000797": "¡Basta, Souma! ¡Cállate!",
    "000798": "Mamá y papá me dejaron hacer lo que quisiera",
    "000799": "durante los próximos seis meses.",
    "005687": "Vol. efectos",
    "005688": "Vol. música",
    "005689": "Tipo música",
    "005690": "Controles",
    "005691": "Ajusta el volumen de los efectos.",
    "005692": "Ajusta el volumen de la música.",
    "005693": "Elige música real o retro.",
    "005694": "Configura los botones.",
    "005709": "Decimales de daño",
    "005711": "Menos de 1: SÍ",
    "005712": "Menos de 10: SÍ",
    "005714": "Muestra decimales en el daño.",
    "005715": "Efectos círculo",
    "005716": "Muestra los efectos del círculo mágico.",
    "005717": "Capturas",
    "005718": "Activa el botón para hacer capturas.",
}
MENU_LABELS = {"005687", "005688", "005689", "005690",
               "005709", "005715", "005717"}
REVISION = "revision_capturas_2026-11-20"


class TestCapturas20261120(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        def rows(path):
            with path.open(encoding="utf-8-sig", newline="") as fp:
                return list(csv.DictReader(fp))
        cls.original = rows(ROOT / "corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv")
        cls.draft = rows(ROOT / "traduccion/CLADUN_BORRADOR_ES.csv")
        cls.readable = (ROOT / "traduccion/CLADUN_BORRADOR_ES.txt").read_text(encoding="utf-8")
        cls.bilingual = (ROOT / "traduccion/CLADUN_BORRADOR_BILINGUE_FAQ.txt").read_text(encoding="utf-8")

    def test_ids_and_originals_preserved(self):
        self.assertEqual(len(self.original), len(self.draft), 9237)
        self.assertEqual([r["grupo_id"] for r in self.original],
                         [r["grupo_id"] for r in self.draft])
        for a,b in zip(self.original, self.draft):
            self.assertEqual(a["original"], b["original"])
            self.assertEqual(a["bytes_hex"], b["bytes_hex"])
            self.assertEqual(a["offset_hex"], b["offset_hex"])

    def test_corrected_text_encoding_and_synchronized_views(self):
        index = {row["grupo_id"]: row for row in self.draft}
        for gid, desired in EXPECTED.items():
            with self.subTest(id=gid):
                record = index[gid]
                self.assertEqual(record["espanol"], desired)
                self.assertEqual(record["revision_es"], REVISION)
                self.assertEqual(decode_spanish(encode_spanish(desired)), desired)
                label = "DIÁLOGO" if record["origen"] == "SCRIPT.SDT/SCRIPT.DAT" else "INTERFAZ"
                self.assertIn(f"[{gid}] {label}\n{desired}\n", self.readable)
                self.assertIn(f"ESPAÑOL ({REVISION}):\n{desired}\n", self.bilingual)

    def test_option_labels_have_conservative_character_budget(self):
        index = {row["grupo_id"]: row for row in self.draft}
        for gid in MENU_LABELS:
            with self.subTest(id=gid):
                line = index[gid]["espanol"]
                self.assertLessEqual(len(line), 18)
                self.assertNotIn("\n", line)
                self.assertNotIn("%", line)
                self.assertEqual(index[gid]["origen"], "DATABASE.DAT/STRTBL.DAT")


if __name__ == "__main__":
    unittest.main()
