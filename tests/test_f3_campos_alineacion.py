"""F3-R4: sintéticos. Un PASS no autoriza cambiar longitudes SCRIPT.DAT."""
from __future__ import annotations
import struct
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from tools import f3_campos_alineacion as f3


def command(block, offset, code, payload=None, *, text=False):
    raw = bytes([code]) + b"\x00\x00" + struct.pack("<H", len(payload or b"")) + (payload or b"")
    return SimpleNamespace(block=block, offset=offset, code=code,
                           raw=raw, content=b"string" if text else None)


class AlignedFieldTests(unittest.TestCase):
    def test_op2_hypothesized_offsets_and_width(self):
        self.assertEqual(f3.LAYOUTS[2], (18, (2, 6, 10, 14)))

    def test_unaligned_alias_is_not_independent_reference(self):
        p = struct.pack("<HIIII", 0, 23, 32, 100, 10000)
        self.assertEqual(len(p), 18)
        self.assertEqual(struct.unpack_from("<I", p, 5)[0], 8192)
        rows = [command(0, 0, 2, p), command(1, 8192, 8, b"")]
        r = f3.profile_hypothesized_fields(rows, [0, 8192, 16384], [0, 1])
        alias = r["legacy_opcode_02_unaligned_u32_byte5"]
        self.assertEqual(alias["occurrences_matching_an_absolute_command_offset"], 1)
        self.assertEqual(alias["distinct_numeric_values"], 1)
        self.assertTrue(alias["all_opcode02_byte5_equals_field6_times_256"])
        self.assertFalse(r["mips_semantics_proven"])
        self.assertFalse(r["script_relocation_authorized"])
        self.assertNotIn("absolute_command_offset", r["totals_selected_fields_only"])

    def test_op2_rejects_nonstandard_arity(self):
        with self.assertRaises(ValueError):
            f3.profile_hypothesized_fields([command(0, 0, 2, b"\x00" * 17)], [0, 100], [1])

    def test_op7_one_byte_lead_then_u32(self):
        rows = [command(0, 0, 7, struct.pack("<BI", 9, 345))]
        r = f3.profile_hypothesized_fields(rows, [0, 50], [345])
        self.assertEqual(r["totals_selected_fields_only"]["script_id"], 1)
        self.assertEqual(r["field_profiles"][0]["hypothesized_u32_byte_offset"], 1)

    def test_opcode01_u32_match_but_never_relocation(self):
        rows = [command(0, 0, 1, struct.pack("<I", 5000))]
        r = f3.profile_hypothesized_fields(rows, [0, 25], [5000])
        self.assertEqual(r["totals_selected_fields_only"]["script_id"], 1)
        self.assertFalse(r["mips_semantics_proven"])

    def test_text_opcodes_excluded(self):
        rows = [command(0, 0, 0x66, struct.pack("<I", 5000), text=True)]
        r = f3.profile_hypothesized_fields(rows, [0, 25], [5000])
        self.assertEqual(r["field_profiles"], [])

    def test_unknown_opcodes_not_treated_as_safe(self):
        rows = [command(0, 0, 99, struct.pack("<I", 5000))]
        r = f3.profile_hypothesized_fields(rows, [0, 25], [5000])
        self.assertTrue(r["untested_opcodes_not_cleared"])
        self.assertFalse(r["script_relocation_authorized"])

    def test_zero_excluded_from_numeric_matches(self):
        rows = [command(0, 0, 1, struct.pack("<I", 0))]
        r = f3.profile_hypothesized_fields(rows, [0, 25], [0])
        self.assertFalse(r["totals_selected_fields_only"])

    def test_absolute_other_block_is_not_jump_proven(self):
        rows = [command(0, 0, 10, struct.pack("<I", 512)), command(1, 512, 0x64)]
        r = f3.profile_hypothesized_fields(rows, [0, 512, 1024], [123, 456], {0})
        self.assertEqual(r["totals_selected_fields_only"]["absolute_other_block"], 1)
        self.assertEqual(r["intro_totals_selected_fields_only"]["absolute_other_block"], 1)
        self.assertFalse(r["script_relocation_authorized"])

    def test_duplicate_offset_rejected(self):
        rows = [command(0, 0, 1, b"\x01\0\0\0"), command(0, 0, 1, b"\x01\0\0\0")]
        with self.assertRaises(ValueError):
            f3.profile_hypothesized_fields(rows, [0, 25], [0])

    def test_encrypted_psp_header_not_elf(self):
        e = f3.classify_executables(b"\x00" * 16, b"~PSP" + b"\0" * 32)
        self.assertTrue(e["boot_all_zero"])
        self.assertEqual(e["eboot_magic"], "PSP_ENCRYPTED_HEADER")
        self.assertFalse(e["mips_interpreter_disassembled"])

    def test_real_elf_signature_does_not_imply_mips_interpreter(self):
        e = f3.classify_executables(b"\x7fELF" + b"\0" * 16, b"\x7fELF" + b"\0" * 16)
        self.assertTrue(e["mips_elf_plaintext_in_these_iso_members"])
        self.assertFalse(e["mips_interpreter_disassembled"])

    def test_original_executable_guard_rejects_fake(self):
        with self.assertRaises(ValueError):
            f3.classify_executables(b"\0" * 12, b"~PSP", require_original=True)

    def test_report_does_not_contain_byte_sequences_or_text(self):
        rows = [command(0, 0, 2, struct.pack("<HIIII", 0, 23, 32, 100, 10000))]
        r = f3.profile_hypothesized_fields(rows, [0, 50], [5000])
        self.assertNotIn("payload_hex", str(r))
        self.assertNotIn("translation_es", str(r))
        self.assertFalse(r["script_relocation_authorized"])

    def test_existing_private_path_protected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "exists.json"
            p.write_text("{}")
            with self.assertRaises(ValueError):
                f3.base.report_path(p)


if __name__ == "__main__":
    unittest.main()
