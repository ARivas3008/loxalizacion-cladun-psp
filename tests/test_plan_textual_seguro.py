#!/usr/bin/env python3
"""Pruebas de bytes sintéticos, sin activos comerciales."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from plan_textual_seguro import build_entries, assert_exact_member_replacements
from test_preinsercion_es import pair
from charset_es import encode_spanish


def fixture(en="Hello?", es="¿Hola?"):
    source, draft = pair(en, es)
    source["grupo_id"] = draft["grupo_id"] = "000001"
    source["offset_hex"] = draft["offset_hex"] = "0x4"
    return [source], [draft], b"ABCD" + en.encode("cp932") + b"\0TAIL"


class TestPlanTextualSeguro(unittest.TestCase):
    def test_compone_plan_solo_si_bytes_reales_coinciden(self):
        src, dst, script = fixture()
        rows = build_entries(src, dst, ["000001"], script)
        self.assertEqual(rows[0]["offset"], 4)
        self.assertEqual(rows[0]["length"], 6)

    def test_rechaza_modificacion_de_origen(self):
        src, dst, script = fixture()
        changed = script[:5] + b"X" + script[6:]
        with self.assertRaises(ValueError):
            build_entries(src, dst, ["000001"], changed)

    def test_rechaza_cambio_de_longitud(self):
        src, dst, script = fixture("Yes", "¿Una frase larga?")
        with self.assertRaises(ValueError):
            build_entries(src, dst, ["000001"], script)

    def test_rechaza_falsificar_metadatos(self):
        src, dst, script = fixture()
        dst[0]["original"] = "Falso"
        with self.assertRaises(ValueError):
            build_entries(src, dst, ["000001"], script)

    def test_rechaza_grupos_repetidos(self):
        src, dst, script = fixture()
        with self.assertRaises(ValueError):
            build_entries(src, dst, ["000001", "000001"], script)

    def test_rechaza_modificar_un_tile_como_si_fuera_texto(self):
        src, dst, script = fixture()
        src[0]["origen"] = dst[0]["origen"] = "MAP.ARC/TILES.DAT"
        with self.assertRaises(ValueError):
            build_entries(src, dst, ["000001"], script)

    def test_difiere_unicamente_en_reemplazo_declarado(self):
        src, dst, script = fixture()
        edits = build_entries(src, dst, ["000001"], script)
        new = script[:4] + encode_spanish("¿Hola?") + script[10:]
        self.assertTrue(assert_exact_member_replacements(script, new, edits))
        with self.assertRaises(ValueError):
            assert_exact_member_replacements(script, b"Z" + new[1:], edits)

    def test_tampoco_acepta_diferencias_dentro_del_span(self):
        src, dst, script = fixture()
        edits = build_entries(src, dst, ["000001"], script)
        with self.assertRaises(ValueError):
            assert_exact_member_replacements(script, script[:4] + b"XXXXXX" + script[10:], edits)


if __name__ == "__main__":
    unittest.main()
