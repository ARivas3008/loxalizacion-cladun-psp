"""F3: tests exclusivamente sintéticos, no prueban interpretación MIPS ni PPSSPP."""
from __future__ import annotations
from types import SimpleNamespace
import struct
import tempfile
import unittest
from pathlib import Path

try:
    from tools import f3_referencias_riesgo as f3
except ModuleNotFoundError:
    import f3_referencias_riesgo as f3


def cmd(block, offset, opcode, payload=None):
    return SimpleNamespace(block=block, offset=offset, code=opcode,
                           content=None if payload is not None else b"text",
                           raw=b"\x01\x01\x00" + struct.pack("<H", len(payload or b"")) + (payload or b""))


class NumericCandidateTests(unittest.TestCase):
    def test_zero_excluded(self):
        a = [cmd(0, 0, 1, b"\x00" * 4), cmd(0, 8, 0x66)]
        self.assertEqual(f3.numeric_candidates(a, [0, 20], [10])["candidate_counts_zero_excluded"], {})

    def test_abs_candidate_not_authorized(self):
        a = [cmd(0, 0, 1, struct.pack("<I", 12)), cmd(0, 12, 0x66)]
        r = f3.numeric_candidates(a, [0, 32], [999])
        self.assertEqual(r["candidate_counts_zero_excluded"]["coincide_offset_absoluto_comando"], 1)
        self.assertFalse(r["relocation_authorized"])

    def test_local_relative_candidate(self):
        a = [cmd(0, 100, 1, struct.pack("<I", 12)), cmd(0, 112, 0x66)]
        self.assertEqual(f3.numeric_candidates(a, [100, 128], [999])
                         ["candidate_counts_zero_excluded"]["coincide_offset_relativo_bloque"], 1)

    def test_block_start_and_id_match(self):
        a = [cmd(0, 0, 1, struct.pack("<II", 64, 100100))]
        r = f3.numeric_candidates(a, [0, 64, 96], [12, 100100])
        self.assertEqual(r["candidate_counts_zero_excluded"]["coincide_inicio_script"], 1)
        self.assertEqual(r["candidate_counts_zero_excluded"]["coincide_id_script"], 1)

    def test_other_block_candidate_does_not_imply_jump(self):
        a = [cmd(0, 0, 1, struct.pack("<I", 12)), cmd(0, 12, 0x66),
             cmd(1, 64, 1, struct.pack("<I", 12))]
        r = f3.numeric_candidates(a, [0, 64, 96], [1, 2], {1})
        self.assertEqual(r["intro_candidate_counts_zero_excluded"]["coincide_offset_absoluto_otro_bloque"], 1)
        self.assertFalse(r["mips_control_flow_proven"])

    def test_unaligned_numeric_window_only_hypothesis(self):
        a = [cmd(0, 0, 1, b"\xff" + struct.pack("<I", 12)), cmd(0, 12, 0x66)]
        self.assertEqual(f3.numeric_candidates(a, [0, 32], [7])
                         ["candidate_counts_zero_excluded"]["coincide_offset_absoluto_comando"], 1)

    def test_text_not_scanned(self):
        a = [cmd(0, 0, 0x66)]
        self.assertEqual(f3.numeric_candidates(a, [0, 20], [1])["candidate_counts_zero_excluded"], {})

    def test_short_nontext_payload(self):
        a = [cmd(0, 0, 1, b"\x04\x05")]
        self.assertEqual(f3.numeric_candidates(a, [0, 20], [1])["candidate_counts_zero_excluded"], {})

    def test_wrong_iso_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "fake.iso"
            p.write_bytes(b"dummy")
            with self.assertRaises(ValueError):
                f3.original_script_children(p)

    def test_report_requires_absolute(self):
        with self.assertRaises(ValueError):
            f3.report_path(Path("out.json"))

    def test_report_rejects_existing(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "already.json"
            p.write_text("{}")
            with self.assertRaises(ValueError):
                f3.report_path(p)


if __name__ == "__main__":
    unittest.main()
