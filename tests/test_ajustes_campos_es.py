#!/usr/bin/env python3
"""Actual game-corpus assertions; no proprietary resources required."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from ajustes_campos_es import effective, audit_effective, INCOMPLETE_RAW
from auditar_preinsercion_es import SOURCE, DRAFT, read_csv
from charset_es import encode_spanish
from integrar_parche_seguro import plan_rows


class TestFixedFieldSpanish(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = read_csv(SOURCE)
        cls.draft = read_csv(DRAFT)
        cls.by_id = {x["grupo_id"]: (x, y) for x, y in zip(cls.src, cls.draft)}

    def test_insertion_labels_fit_100_percent_of_fixed_fields(self):
        translated, counts = audit_effective(self.src, self.draft)
        self.assertEqual(len(translated), 9237)
        self.assertEqual(counts.get("etiqueta_compacta_para_campo_fijo"), 269)
        self.assertEqual(counts.get("original_truncado_verificado_por_bytes"), 2)
        for src, draft in zip(self.src, translated):
            if src["origen"].startswith("DATABASE.DAT/") and src["capacidad_campo"]:
                if draft["espanol"]:
                    self.assertLessEqual(len(encode_spanish(draft["espanol"])) + 1,
                                         int(src["capacidad_campo"]), src["grupo_id"])

    def test_literary_draft_and_source_are_immutable(self):
        adjusted, counts = audit_effective(self.src, self.draft)
        for source, original, compiled in zip(self.src, self.draft, adjusted):
            if source["grupo_id"] not in INCOMPLETE_RAW and original["espanol"] == compiled["espanol"]:
                continue
            self.assertEqual(original["grupo_id"], compiled["grupo_id"])
            self.assertEqual(original["original"], compiled["original"])
            self.assertEqual(source["bytes_hex"], compiled["bytes_hex"])

    def test_missing_source_bytes_are_exact_and_confined(self):
        for gid, expected in (("008723", "Aceite animado"), ("008724", "Agua animada")):
            src, dst = self.by_id[gid]
            text, why = effective(src, dst)
            self.assertEqual(text, expected)
            self.assertEqual(why, "original_truncado_verificado_por_bytes")
            self.assertEqual(len(bytes.fromhex(src["bytes_hex"])) + 1, int(src["capacidad_campo"]))

    def test_all_text_and_graphical_entries_are_plannable(self):
        changes, blocked, identical = plan_rows(list(zip(self.src, self.draft)))
        self.assertEqual(len(blocked), 0)
        self.assertEqual(len([x for k, v in changes.items() if k.startswith("SYS.DAT2/") for x in v]), 6)
        self.assertEqual(sum(len(v) for v in changes.values()) + len(blocked) + identical, 9237)


if __name__ == "__main__":
    unittest.main()
