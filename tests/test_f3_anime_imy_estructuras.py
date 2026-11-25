"""F3: solo tests sintéticos; no ISO comercial ni PPSSPP en CI."""
from __future__ import annotations
import struct
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
import f3_anime_imy_estructuras as f3


def fake_imy(*, kind=0, stride=2, rows=1, flags=b'\x00', literal=b'\x01\x02'):
    h = bytearray(34)
    h[:4] = b'IMY\x00'
    struct.pack_into('<I', h, 4, stride * rows + 32)
    struct.pack_into('<H', h, 8, stride)
    h[10] = kind
    struct.pack_into('<H', h, 12, rows)
    struct.pack_into('<H', h, 32, len(flags))
    return bytes(h) + flags + literal


def fake_pspfs(*, index=234, name=b'ANIME000.IDT', size=12, offset=14000):
    b = bytearray(16 + 349 * 32)
    b[:8] = b'PSPFS_V1'
    struct.pack_into('<I', b, 8, 349)
    p = 16 + 32 * index
    b[p:p + len(name)] = name
    struct.pack_into('<III', b, p + 20, 0, size, offset)
    return bytes(b)


class AnimeStructureTests(unittest.TestCase):
    def test_scans_one_valid_header(self):
        blob = b'ABCD' + fake_imy() + b'other'
        headers = f3.scan_imy_headers(blob)
        self.assertEqual(len(headers), 1)
        self.assertEqual((headers[0]['offset'], headers[0]['typ']), (4, 0))
        self.assertEqual(f3.legacy_flag_probe(blob, headers[0]), 'ALGORITMO_LEGADO_CONSUME_FLAGS')

    def test_type_02_not_assumed_to_decode(self):
        blob = fake_imy(kind=2, stride=64, rows=1, flags=b'\xd0')
        head = f3.scan_imy_headers(blob)[0]
        self.assertEqual(head['typ'], 2)
        self.assertEqual(f3.legacy_flag_probe(blob, head), 'LOOKBACK_INVALIDO')

    def test_zero_imy_headers_in_non_image_member(self):
        self.assertEqual(f3.scan_imy_headers(b'not an imy'), [])

    def test_incomplete_imy_rejected(self):
        with self.assertRaises(ValueError):
            f3.scan_imy_headers(b'xxxxIMY\x00\x00\x00')

    def test_imy_wrong_expanded_geometry_rejected(self):
        blob = bytearray(fake_imy())
        struct.pack_into('<I', blob, 4, 500)
        with self.assertRaises(ValueError):
            f3.scan_imy_headers(bytes(blob))

    def test_imy_empty_flags_rejected(self):
        with self.assertRaises(ValueError):
            f3.scan_imy_headers(fake_imy(flags=b''))

    def test_imy_flags_overrun_rejected(self):
        blob = bytearray(fake_imy())
        struct.pack_into('<H', blob, 32, 1000)
        with self.assertRaises(ValueError):
            f3.scan_imy_headers(bytes(blob))

    def test_legacy_decode_length_mismatch(self):
        blob = fake_imy(stride=4, flags=b'\x00')
        self.assertEqual(f3.legacy_flag_probe(blob, f3.scan_imy_headers(blob)[0]), 'LONGITUD_DISTINTA')

    def test_legacy_decode_lookback_good(self):
        blob = fake_imy(stride=4, flags=b'\x00\xc0')
        self.assertEqual(f3.legacy_flag_probe(blob, f3.scan_imy_headers(blob)[0]), 'ALGORITMO_LEGADO_CONSUME_FLAGS')

    def test_original_header_accepted(self):
        b = fake_pspfs()
        self.assertEqual(f3.parse_pspfs_entry(b, 234, 20000)['name'], 'ANIME000.IDT')

    def test_pspfs_magic_rejected(self):
        b = bytearray(fake_pspfs());b[0] = 0
        with self.assertRaises(ValueError):f3.parse_pspfs_entry(bytes(b), 234, 20000)

    def test_pspfs_file_beyond_boundary_rejected(self):
        with self.assertRaises(ValueError):f3.parse_pspfs_entry(fake_pspfs(offset=20000), 234, 20000)

    def test_pspfs_file_overlaps_table_rejected(self):
        with self.assertRaises(ValueError):f3.parse_pspfs_entry(fake_pspfs(offset=11100), 234, 20000)

    def test_member_expected_number_of_headers(self):
        self.assertEqual(f3.inventory_member(fake_imy(), 1)['header_types'], {'0x00': 1})
        with self.assertRaises(ValueError):f3.inventory_member(fake_imy(), 2)


if __name__ == '__main__':unittest.main()
