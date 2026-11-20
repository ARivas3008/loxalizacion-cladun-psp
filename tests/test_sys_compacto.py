#!/usr/bin/env python3
"""REGRESSION: six text PNGs must not be duplicated as a second archive."""
from __future__ import annotations
import struct
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from graficos_texto_es import GRAPHICS
from extract_cladun import dsarc_entries
from integrar_parche_seguro import rebuild_sys_arc_compact

PNG = b"\x89PNG\r\n\x1a\n"


def fixture():
    archive = bytearray(4096)
    archive[:8] = b"DSARC FL"
    struct.pack_into("<I", archive, 8, len(GRAPHICS))
    records = {}
    for i, name in enumerate(GRAPHICS):
        table = 16 + i * 48
        archive[table:table + len(name)] = name.encode("ascii")
        old = PNG + bytes((i,)) * 8
        start = 512 + i * 512
        archive[start:start + len(old)] = old
        struct.pack_into("<II", archive, table + 40, len(old), start)
        records[name] = [({"grupo_id": f"G{i}", "origen": "SYS.DAT2/" + name,
                          "original": "NO DATA" if "NODATA" in name else "This is an RPG!",
                          "tipo": "mensaje_grafico" if "NODATA" in name else "titulo_grafico"},
                          b"unused", b"replacement")]
    return bytes(archive), records


class CompactGraphicsTests(unittest.TestCase):
    @staticmethod
    def render(name, raw, spanish):
        return PNG + b"TRANSLATED" * 3, {"asset": name, "only_text_roi": True}

    def test_six_pngs_fit_original_slot_and_keep_sector_alignment(self):
        before, rows = fixture()
        with patch("integrar_parche_seguro.patch_png", side_effect=self.render):
            result, updated, audits = rebuild_sys_arc_compact(before, rows, 4096)
        self.assertLessEqual(len(result), len(before))
        self.assertEqual(len(audits), 6)
        self.assertEqual(len(updated), 6)
        entries = dsarc_entries(result)
        self.assertEqual([x["name"] for x in entries], list(GRAPHICS))
        self.assertTrue(all(x["offset"] % 512 == 0 for x in entries))
        self.assertTrue(all(x["offset"] < len(before) for x in entries))
        self.assertEqual(result[:16], before[:16])
        self.assertTrue(all(result[x["offset"]:x["offset"] + x["size"]].startswith(PNG)
                            for x in entries))

    def test_reject_overflow_before_neighboring_asset(self):
        before, rows = fixture()
        with patch("integrar_parche_seguro.patch_png", side_effect=self.render):
            with self.assertRaisesRegex(ValueError, "slot|overflow"):
                rebuild_sys_arc_compact(before, rows, 3584)

    def test_reject_unknown_graphical_member(self):
        before, rows = fixture()
        del rows["PIC1.PNG"]
        with self.assertRaises(ValueError):
            rebuild_sys_arc_compact(before, rows, 4096)


if __name__ == "__main__":
    unittest.main()
