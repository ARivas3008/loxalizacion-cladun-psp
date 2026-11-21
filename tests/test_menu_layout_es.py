#!/usr/bin/env python3
"""F1: la corrección de ventana afecta SOLO a la presentación de 005709."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from menu_layout_es import (
    GROUP_ID, SOURCE_ORIGINAL, SOURCE_TRANSLATION, LAYOUT_TRANSLATION,
    patch_canonical_menu_layout, patch_canonical_menu_values,
)
from experimento_menu_f1 import advance, load_metrics_snapshot
from integrar_parche_seguro import source_rows, plan_rows


class TestMenuLayoutCanonico(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = source_rows()

    def test_solo_una_traduccion_de_presentacion_cambia(self):
        updated, report = patch_canonical_menu_layout(self.rows)
        self.assertEqual(len(updated), 9237)
        self.assertEqual(report["id"], GROUP_ID)
        changed = []
        for (src1, old), (src2, new) in zip(self.rows, updated):
            self.assertEqual(src1, src2)
            if old != new:
                changed.append((src1["grupo_id"], [k for k in old if old[k] != new[k]]))
                self.assertEqual(old["espanol"], SOURCE_TRANSLATION)
                self.assertEqual(new["espanol"], LAYOUT_TRANSLATION)
                self.assertEqual(src1["original"], SOURCE_ORIGINAL)
        self.assertEqual(changed, [(GROUP_ID, ["espanol"])])

    def test_mantiene_anchura_del_original_segun_font(self):
        path = Path(__file__).resolve().parents[1] / "reports/menu_f1_metricas_subconjunto_2026-11-20.json"
        metricas, _ = load_metrics_snapshot(path)
        self.assertEqual(advance(SOURCE_ORIGINAL, metricas), 303)
        self.assertEqual(advance(LAYOUT_TRANSLATION, metricas), 310)

    def test_plan_integracion_unico_cambio_binario(self):
        original_changes, original_blocked, original_same = plan_rows(self.rows)
        patched_rows, _ = patch_canonical_menu_layout(self.rows)
        next_changes, next_blocked, next_same = plan_rows(patched_rows)
        self.assertEqual(original_blocked, next_blocked)
        self.assertEqual(original_same, next_same)
        self.assertEqual(original_changes.keys(), next_changes.keys())
        for source in original_changes:
            before = {r["grupo_id"]: b for r, a, b in original_changes[source]}
            after = {r["grupo_id"]: b for r, a, b in next_changes[source]}
            self.assertEqual(before.keys(), after.keys())
            for gid in before:
                if gid != GROUP_ID:
                    self.assertEqual(before[gid], after[gid])
                else:
                    self.assertNotEqual(before[gid], after[gid])

    def test_valores_onoff_y_margen_solo_en_presentacion(self):
        rows, report = patch_canonical_menu_values(self.rows)
        differences = [(a["grupo_id"], d["espanol"]) for (a,b), (_s,d)
                       in zip(self.rows, rows) if b != d]
        self.assertEqual(differences, [("005713", "         No ")])
        self.assertEqual(report["IDs_verificados"], ["005710", "005713"])
        self.assertEqual(next(d["espanol"] for s,d in rows if s["grupo_id"]=="005710"),
                         "          Sí")
        for gid in ("005711","005712"):
            self.assertEqual(next(d for s,d in rows if s["grupo_id"]==gid),
                             next(d for s,d in self.rows if s["grupo_id"]==gid))

    def test_falla_si_cambia_fuente_o_espanol_esperado(self):
        modified = list(self.rows)
        at = next(i for i, (a, b) in enumerate(modified) if a["grupo_id"] == GROUP_ID)
        src, dst = modified[at]
        modified[at] = (src, {**dst, "espanol": "Otra redacción"})
        with self.assertRaises(ValueError):
            patch_canonical_menu_layout(modified)
        modified[at] = ({**src, "original": "Sorpresa"}, dst)
        with self.assertRaises(ValueError):
            patch_canonical_menu_layout(modified)


if __name__ == "__main__":
    unittest.main()
