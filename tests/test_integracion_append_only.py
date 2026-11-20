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
            payload = struct.pack("<H", 5) + b"Hello" + b"\0"
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

    def test_database_edits_only_text_field_not_adjacent_asset(self):
        from integrar_parche_seguro import rebuild_database_arc
        archive = bytearray(1536)
        archive[:8] = b"DSARC FL"
        struct.pack_into("<I", archive, 8, 2)
        archive[16:16 + 8] = b"ITEM.DAT"
        struct.pack_into("<II", archive, 16 + 40, 64, 512)
        archive[64:64 + 12] = b"PORTRAIT.BIN"
        struct.pack_into("<II", archive, 64 + 40, 64, 1024)
        archive[512:515] = b"ABC"
        archive[1024:1088] = bytes(range(64))
        source = {"grupo_id": "000001", "offset_hex": "0x0", "capacidad_campo": "8"}
        result, ids = rebuild_database_arc(bytes(archive), {"ITEM.DAT": [(source, b"ABC", b"BIEN")]})
        self.assertEqual(ids, {"000001"})
        self.assertEqual(result[512:520], b"BIEN\0\0\0\0")
        self.assertEqual(result[1024:1088], archive[1024:1088])
        self.assertEqual(result[:512], archive[:512])

    def test_database_rejects_nonzero_neighbor_or_overflow(self):
        from integrar_parche_seguro import rebuild_database_arc
        archive = bytearray(1024)
        archive[:8] = b"DSARC FL"
        struct.pack_into("<I", archive, 8, 1)
        archive[16:24] = b"ITEM.DAT"
        struct.pack_into("<II", archive, 16 + 40, 64, 512)
        archive[512:516] = b"ABC\0"
        source = {"grupo_id": "000001", "offset_hex": "0x0", "capacidad_campo": "8"}
        with self.assertRaises(ValueError):
            rebuild_database_arc(bytes(archive), {"ITEM.DAT": [(source, b"ABC", b"TOO LONG TO FIT")]})
        archive[517] = 0x99
        # The modeled capacity includes one nontext metadata byte. The writer
        # must trim its permitted span before that byte, not destroy the byte.
        result, ids = rebuild_database_arc(bytes(archive), {"ITEM.DAT": [(source, b"ABC", b"BIEN")]})
        self.assertEqual(ids, {"000001"})
        self.assertEqual(result[512:518], b"BIEN\x00\x99")
        with self.assertRaises(ValueError):
            rebuild_database_arc(bytes(archive), {"ITEM.DAT": [(source, b"ABC", b"LARGO")]})

    def test_database_exact_full_width_field_has_no_nul(self):
        from integrar_parche_seguro import rebuild_database_arc
        archive = bytearray(1024)
        archive[:8] = b"DSARC FL"
        struct.pack_into("<I", archive, 8, 1)
        archive[16:24] = b"ITEM.DAT"
        struct.pack_into("<II", archive, 16 + 40, 64, 512)
        archive[512:516] = b"ABCD"
        archive[516] = 0x55  # unrelated record byte
        source = {"grupo_id": "000002", "offset_hex": "0x0", "capacidad_campo": "4"}
        result, ids = rebuild_database_arc(bytes(archive), {"ITEM.DAT": [(source, b"ABCD", b"OK")]})
        self.assertEqual(ids, {"000002"})
        self.assertEqual(result[512:517], b"OK  \x55")

    def test_strtbl_rebuilds_pointers_without_editing_other_members(self):
        from integrar_parche_seguro import rebuild_database_arc
        first = 654 * 4
        table = bytearray(first)
        for i in range(651):
            struct.pack_into("<I", table, i * 4, first + 2 * i)
        old_strings = bytes(table) + (b"X\0" * 651)
        archive = bytearray(8192)
        archive[:8] = b"DSARC FL"
        struct.pack_into("<I", archive, 8, 2)
        archive[16:16 + 10] = b"STRTBL.DAT"
        struct.pack_into("<II", archive, 16 + 40, len(old_strings), 512)
        archive[64:64 + 9] = b"OTHER.DAT"
        struct.pack_into("<II", archive, 64 + 40, 64, 6144)
        archive[512:512 + len(old_strings)] = old_strings
        archive[6144:6208] = bytes(range(64))
        record = {"grupo_id": "123456", "indice_registro": "5",
                  "offset_hex": hex(first + 2 * 5)}
        result, used = rebuild_database_arc(
            bytes(archive), {"STRTBL.DAT": [(record, b"X", b"Hola")]})
        self.assertEqual(used, {"123456"})
        self.assertEqual(result[6144:6208], bytes(range(64)))
        self.assertEqual(struct.unpack_from("<I", result, 64 + 44)[0], 6144)
        target = struct.unpack_from("<I", result, 16 + 44)[0]
        self.assertGreaterEqual(target, 8192)
        self.assertEqual(struct.unpack_from("<I", result, 16 + 40)[0], len(old_strings) + 3)
        member = result[target:target + len(old_strings) + 3]
        self.assertEqual(member[struct.unpack_from("<I", member, 5 * 4)[0]:
                                struct.unpack_from("<I", member, 5 * 4)[0] + 5], b"Hola\0")
        self.assertEqual(struct.unpack_from("<I", member, 651 * 4)[0], 0)

    def test_real_psp_imy_envelope_header_is_chunk_capacity_not_total_size(self):
        """Reproduce the USA 8-block SCRIPT.SDT envelope semantics with 2 blocks."""
        header = synthetic_imy_header(stride=16, rows=2)
        chunk_size = 32
        chunk_a = compress_block(b"A" * 32, header)
        chunk_b = compress_block(b"B" * 32, header)
        off_a = 16
        off_b = (off_a + len(chunk_a) + 3) & ~3
        original = (struct.pack("<IIII", 2, chunk_size, off_a, off_b)
                    + chunk_a + b"\0" * (off_b - off_a - len(chunk_a)) + chunk_b)
        from extract_cladun import decompress
        restored, codec = decompress(original, 64)
        self.assertEqual(restored, b"A" * 32 + b"B" * 32)

        updated = recompress(original, b"C" * 32 + b"D" * 64)
        self.assertEqual(struct.unpack_from("<II", updated), (2, 32))
        restored, codec = decompress(updated, 96)
        self.assertEqual(restored, b"C" * 32 + b"D" * 64)

        # Force the previously unchecked format mismatch. Must fail closed.
        tampered = bytearray(original)
        struct.pack_into("<I", tampered, 4, 64)
        with self.assertRaises(ValueError):
            recompress(bytes(tampered), b"C" * 32 + b"D" * 64)

    def test_reject_odd_imy_expansion(self):
        header = synthetic_imy_header()
        raw = b"\x00\x01" * 16
        stored = struct.pack("<III", 1, len(raw), 12) + compress_block(raw, header)
        with self.assertRaises(ValueError):
            recompress(stored, raw + b"\x00")


if __name__ == "__main__":
    unittest.main()
