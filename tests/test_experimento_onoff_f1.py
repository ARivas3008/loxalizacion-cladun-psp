#!/usr/bin/env python3
"""Guardas de candidatos ON/OFF. No acreditan el resultado en PPSSPP."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from experimento_onoff_f1 import EXPECTED, build, prepare_rows
from integrar_parche_seguro import source_rows
from menu_layout_es import GROUP_ID, LAYOUT_TRANSLATION


class TestExperimentoOnOffF1(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pairs = source_rows()

    def test_aislamiento_sin_alterar_005711_005712(self):
        updated, report = prepare_rows(self.pairs)
        differences = {}
        for (old_src, old_dest), (new_src, new_dest) in zip(self.pairs, updated):
            self.assertEqual(old_src, new_src)
            if old_dest != new_dest:
                self.assertEqual([k for k in old_dest if old_dest[k] != new_dest[k]], ["espanol"])
                differences[old_src["grupo_id"]] = new_dest["espanol"]
        self.assertEqual(set(differences), {GROUP_ID})
        self.assertEqual(differences[GROUP_ID], LAYOUT_TRANSLATION)
        self.assertEqual(next(d["espanol"] for a,d in updated if a["grupo_id"]=="005710"), "          Sí")
        self.assertEqual(next(d["espanol"] for a,d in updated if a["grupo_id"]=="005713"), "         No")
        self.assertEqual(report["ids_contexto_intactos"], ["005711", "005712"])

    def test_id_aislado_mantiene_otro_valor_original_del_borrador(self):
        updated, info = prepare_rows(self.pairs, selected=("005710",))
        changed = [a["grupo_id"] for (a, b), (_, c) in zip(self.pairs, updated) if b != c]
        self.assertEqual(changed, [GROUP_ID])
        other = next(d for s, d in updated if s["grupo_id"] == "005713")
        self.assertEqual(other["espanol"], "         No")

    def test_rechaza_preimagen_modificada(self):
        manipulated = list(self.pairs)
        at = next(i for i, (s, d) in enumerate(manipulated) if s["grupo_id"] == "005710")
        src, dst = manipulated[at]
        manipulated[at] = (src, {**dst, "espanol": "Otro"})
        with self.assertRaises(ValueError):
            prepare_rows(manipulated)

    def test_variante_espacio_final_mantiene_005709_y_005711_005712(self):
        original = {a["grupo_id"]: b for a, b in self.pairs}
        changed, report = prepare_rows(self.pairs, mode="si-no-espacio-final")
        diffs = {a["grupo_id"]: b["espanol"] for a,b in changed
                 if original[a["grupo_id"]] != b}
        self.assertEqual(set(diffs), {"005709", "005713"})
        self.assertEqual(diffs["005713"], "         No ")
        self.assertEqual(next(b["espanol"] for a,b in changed if a["grupo_id"] == "005710"), "          Sí")
        for gid in ("005711", "005712"):
            self.assertEqual(next(b for a,b in changed if a["grupo_id"] == gid),
                             original[gid])
        self.assertEqual(report["ids_contexto_intactos"], ["005711", "005712"])

    def test_no_sobrescribe_evidencia_ni_toca_maestros(self):
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "candidato.csv"
            report_path = Path(tmp) / "informe.json"
            info = build(csv_path, report_path, selected=("005710",))
            self.assertEqual(info["estado"], "CSV_PRIVADO_NO_PROBADO_EN_PPSSPP")
            self.assertEqual(info["entradas_conservadas"], 9237)
            self.assertEqual(len(info["cambios_onoff"]), 1)
            self.assertTrue(csv_path.is_file())
            with self.assertRaises(FileExistsError):
                build(csv_path, report_path, selected=("005710",))


if __name__ == "__main__":
    unittest.main()
