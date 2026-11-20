#!/usr/bin/env python3
"""Regresiones de corpus, conciliación y post-edición Cladun."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from aplicar_revision_consolidada import check
from aplicar_correcciones_editor import leer_csv


class RevisionConsolidadaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.rows, cls.plan, cls.pending, cls.done = check(ROOT)
        cls.current = {r["grupo_id"]: r for r in cls.rows}
        cls.patches = {p["grupo_id"]: p for p in cls.plan}

    def text(self, group_id):
        return self.patches.get(group_id, {}).get(
            "es_corregido", self.current[group_id]["espanol"])

    def test_full_inventory_and_plan_uniqueness(self):
        self.assertEqual(len(self.rows), 9237)
        self.assertGreaterEqual(len(self.plan), 220)
        self.assertEqual(len(set(p["grupo_id"] for p in self.plan)), len(self.plan))
        self.assertIn(len(self.pending), (0, len(self.plan)))
        self.assertIn(len(self.done), (0, len(self.plan)))

    def test_keep_manual_reviewed_names(self):
        # Los CLD-NNNNNN son text_id, NO el grupo de seis cifras.
        # Buscar por clave canónica evita falsos fallos al probar el glosario.
        by_text_id = {r["text_id"]: r for r in self.rows}
        for tid, expected in (
            ("CLD-006688", "Sunday"),
            ("CLD-006663", "Coco"),
            ("CLD-006682", "Bob"),
            ("CLD-006657", "Sherbet"),
        ):
            self.assertIn(tid, by_text_id)
            group_id = by_text_id[tid]["grupo_id"]
            self.assertEqual(self.text(group_id), expected)

    def test_clear_dialogue_mistranslations(self):
        self.assertEqual(self.text("000793"), "me pidieron que te cuidara.")
        self.assertEqual(self.text("000835"), "mientras busco un tesoro.")
        self.assertEqual(self.text("000922"), "Y-Yo soy... Despina.")
        self.assertEqual(self.text("001055"), "a cualquiera en personaje principal...")
        self.assertEqual(self.text("002763"), "Ojalá alguien me enseñara nuevas técnicas.")

    def test_ui_shortened_and_corrected(self):
        self.assertEqual(self.text("005687"), "Vol. efectos")
        self.assertEqual(self.text("005690"), "Controles")
        self.assertEqual(self.text("005712"), "Menos de 10: SÍ")
        self.assertEqual(self.text("005764").splitlines()[0], "Aún no se puede leer.")
        self.assertEqual(self.text("005365"), "Pj. de apoyo")

    def test_names_mistranslated_as_common_words(self):
        self.assertEqual(self.text("009017"), "Espadón")
        self.assertEqual(self.text("009025"), "Némesis")
        self.assertEqual(self.text("009027"), "Dragnade")
        self.assertEqual(self.text("008325"), "¡No me arrepiento de nada en mi vida!")

    def test_only_two_truncated_sources_are_untranslated(self):
        self.assertEqual([r["grupo_id"] for r in self.rows if not r["espanol"]],
                         ["008723", "008724"])


if __name__ == "__main__":
    unittest.main()
