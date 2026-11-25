#!/usr/bin/env python3
"""F1: +1 U+3000 no debe tocar ningún ID adicional ni los maestros."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from experimento_menu_f1_residuo import (
    prepare_plus_one, build, LAYOUT_PLUS_ONE, LAYOUT_MINIMAL_HISTORICO, EXPECTED_ISO_PLUS_ONE,
)
from integrar_parche_seguro import source_rows
from menu_layout_es import GROUP_ID


class TestF1PlusOne(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = source_rows()

    def test_solo_id_005709_cambia_y_agrega_un_unico_ideografico(self):
        out = prepare_plus_one(self.rows)
        diff = [(a["grupo_id"], d["espanol"])
                for (a, b), (_s, d) in zip(self.rows, out) if b != d]
        self.assertEqual(diff, [(GROUP_ID, LAYOUT_MINIMAL_HISTORICO + "\u3000")])
        self.assertEqual(LAYOUT_PLUS_ONE, LAYOUT_MINIMAL_HISTORICO + "\u3000")
        self.assertEqual(LAYOUT_PLUS_ONE.count("\u3000"), 11)
        self.assertEqual(LAYOUT_PLUS_ONE.count(" "), 8)  # Dos espacios literarios + seis.
        self.assertEqual([s for s, d in out], [s for s, d in self.rows])

    def test_rechaza_preimagen_alterada(self):
        corrupted = list(self.rows)
        i = next(i for i, (a, _b) in enumerate(corrupted) if a["grupo_id"] == GROUP_ID)
        a, b = corrupted[i]
        corrupted[i] = (a, {**b, "espanol": "Cambio no autorizado"})
        with self.assertRaises(ValueError):
            prepare_plus_one(corrupted)

    def test_rechaza_recuento_incompleto(self):
        with self.assertRaises(ValueError):
            prepare_plus_one(self.rows[:-1])

    def test_exporta_csv_privado_9237_y_rechaza_sobrescritura(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "extra.csv"
            report = Path(tmp) / "extra.json"
            result = build(out, report)
            self.assertEqual(result["total_filas"], 9237)
            self.assertEqual(result["unico_id_modificado"], GROUP_ID)
            self.assertEqual(result["capturas_ppsspp"], "NO_EJECUTADAS")
            self.assertEqual(result["iso_variante_sha256_historico_esperado_NO_REPRODUCIDO"],
                             EXPECTED_ISO_PLUS_ONE)
            self.assertTrue(out.exists())
            with self.assertRaises(FileExistsError):
                build(out, report)

if __name__ == "__main__":
    unittest.main()
