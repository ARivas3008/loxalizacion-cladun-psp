#!/usr/bin/env python3
"""Tests de aislamiento diagnóstico A/B (no certifican jugabilidad)."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from integrar_parche_seguro import filtrar_recurso_diagnostico


class TestDiagnosticExclusion(unittest.TestCase):
    def setUp(self):
        self.changes = {
            "SCRIPT.SDT/SCRIPT.DAT": [({"grupo_id": "s1"}, b"A", b"B")],
            "DATABASE.DAT/STRTBL.DAT": [({"grupo_id": "u1"}, b"C", b"D")],
            "DATABASE.DAT/DEFAULTTALK.DAT": [({"grupo_id": "u2"}, b"E", b"F")],
            "STAFFROLL.TXT": [({"grupo_id": "c1"}, b"G", b"H")],
            "SYS.DAT2/PIC1.PNG": [({"grupo_id": "g1"}, b"I", b"J")],
        }
        self.blocked = []

    def test_excludes_scripts_only(self):
        n = filtrar_recurso_diagnostico(self.changes, self.blocked, "SCRIPT.SDT")
        self.assertEqual(n, 1)
        self.assertNotIn("SCRIPT.SDT/SCRIPT.DAT", self.changes)
        self.assertIn("DATABASE.DAT/STRTBL.DAT", self.changes)
        self.assertEqual(self.blocked[0]["grupo_id"], "s1")

    def test_excludes_entire_database_not_just_strtbl(self):
        n = filtrar_recurso_diagnostico(self.changes, self.blocked, "DATABASE.DAT")
        self.assertEqual(n, 2)
        self.assertFalse(any(k.startswith("DATABASE.DAT/") for k in self.changes))
        self.assertEqual({r["grupo_id"] for r in self.blocked}, {"u1", "u2"})

    def test_excludes_graphics_without_touching_scripts(self):
        self.assertEqual(filtrar_recurso_diagnostico(self.changes, self.blocked, "SYS.DAT2"), 1)
        self.assertIn("SCRIPT.SDT/SCRIPT.DAT", self.changes)

    def test_rejects_unknown_or_unchanged_resource(self):
        with self.assertRaises(ValueError):
            filtrar_recurso_diagnostico(self.changes, self.blocked, "EBOOT.BIN")
        with self.assertRaises(ValueError):
            filtrar_recurso_diagnostico({"SCRIPT.SDT/SCRIPT.DAT": self.changes["SCRIPT.SDT/SCRIPT.DAT"]}, [],
                                         "DATABASE.DAT")


if __name__ == "__main__":
    unittest.main()
