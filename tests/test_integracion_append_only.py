#!/usr/bin/env python3
"""Append-only and IMY tests use synthetic bytes, not game resources."""
import struct
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from integrar_parche_seguro import text_command_rebuild, locate_iso_dir_record
from imy_repack_safe import compress_block, recompress
from extract_cladun import decompress


def synthetic_imy_header(stride=16, rows=2):
    header = bytearray(32)
    header[:4] = b"IMY\x00"
    struct.pack_into("<I", header, 4, 0x20 | ((rows // 2) << 8))
    struct.pack_into("<H", header, 8, stride)
    header[10] = 0x10
    struct.pack_into("<H", header, 12, rows)
    return bytes(header)


def synthetic_script():
    table = bytearray(16 + 32 * 1625)
    struct.pack_into("<I", table, 0, 1625)
    script = bytearray()
    for index in range(1625):
        struct.pack_into("<I", table, 16 + index * 32 + 4, len(script))
        if index == 0:
            payload = struct.pack("<H", 6) + b"Hello" + b"\0"
            script.extend(b"\x66\x01\x00" + struct.pack("<H", len(payload)) + payload)
            script.extend(b"\0" * (16 - len(script) % 16))
        else:
            script.extend(b"\0" * 16)
    return bytes(script), bytes(table)


class TestsSafeAppend(unittest.TestCase):
    def test_noop_script_rebuilder_is_byte_exact(self):
        raw, table = synthetic_script()
        a, b = text_command_rebuild(raw, table, {})
        self.assertEqual(a, raw)
        self.assertEqual(b, table)

    def test_rebuilds_script_text_and_updates_command_length(self):
        raw, table = synthetic_script()
        a, b = text_command_rebuild(raw, table, {7: (b"Hello", b"Buenos dias", "000001")})
        self.assertEqual(a[7:18], b"Buenos dias")
        self.assertNotEqual(a, raw)
        self.assertEqual(struct.unpack_from("<H", a, 3)[0], 14)
        self.assertEqual(struct.unpack_from("<I", b, 16 + 32 + 4)[0], 32)

    def test_rejects_unmatched_or_corrupt_script_slot(self):
        raw, table = synthetic_script()
        with self.assertRaises(ValueError):
            text_command_rebuild(raw, table, {7: (b"World", b"Hola", "000001")})
        with self.assertRaises(ValueError):
            text_command_rebuild(raw, table, {100: (b"Unknown", b"Hola", "000002")})

    def test_reencode_imy_and_resized_final_chunk_roundtrip(self):
        header = synthetic_imy_header()
        original = b"\x00\x01" * 16
        encoded = compress_block(original, header)
        stored = struct.pack("<III", 1, len(original), 12) + encoded
        decoded, codec = decompress(stored, len(original))
        self.assertEqual(decoded, original)
        self.assertTrue(codec.startswith("IMY"))
        replacement = (b"AA" * 32)
        modified = recompress(stored, replacement)
        result, kind = decompress(modified, len(replacement))
        self.assertEqual(result, replacement)
        self.assertEqual(struct.unpack_from("<H", modified, 12 + 12)[0], 4)

    def test_reject_odd_imy_expansion(self):
        header = synthetic_imy_header()
        raw = b"\x00\x01" * 16
        stored = struct.pack("<III", 1, len(raw), 12) + compress_block(raw, header)
        with self.assertRaises(ValueError):
            recompress(stored, raw + b"\x00")


if __name__ == "__main__":
    unittest.main()
