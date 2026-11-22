"""Synthetic IMY fixtures only. No Cladun resources included in tests."""
import struct
import unittest
from tools.f2_auditar_27_imy_sysgra import decode_imy, sha

def fixture(mode=0x60, flags=b'\x01', literals=b'\x12\x34\x56\x78',
            stride=2, rows=2, image_type=0xA4, pad=b''):
    flags_at = 0x420 if mode == 0x20 else 0x60
    raw = bytearray(flags_at)
    raw[:4] = b'IMY\x00'
    raw[4] = mode
    struct.pack_into('<H', raw, 8, stride)
    raw[10] = image_type
    struct.pack_into('<H', raw, 12, rows)
    return bytes(raw) + struct.pack('<H', len(flags)) + flags + literals + pad

class TestF2Sysgra27(unittest.TestCase):
    def test_16_color_palette_image(self):
        raw, m = decode_imy(fixture())
        self.assertEqual(raw, b'\x12\x34\x56\x78')
        self.assertEqual(m['palette_entries'], 16)
        self.assertEqual(m['flag_offset_hex'], '0x0060')
        self.assertFalse(m['runtime_resource_use_proven'])
    def test_256_color_palette_image(self):
        raw, m = decode_imy(fixture(mode=0x20))
        self.assertEqual(raw, b'\x12\x34\x56\x78')
        self.assertEqual(m['palette_entries'], 256)
        self.assertEqual(m['flag_offset_hex'], '0x0420')
    def test_84_variant(self):
        _, m = decode_imy(fixture(mode=0x20, image_type=0x84))
        self.assertEqual(m['imagedata_format_byte'], '0x84')
    def test_two_rgba_tables_same_index_surface(self):
        a = bytearray(fixture(mode=0x20)); b = bytearray(a)
        a[40] = 22; b[40] = 99
        raw_a, meta_a = decode_imy(bytes(a)); raw_b, meta_b = decode_imy(bytes(b))
        self.assertEqual(sha(raw_a), sha(raw_b))
        self.assertNotEqual(meta_a['palette_sha256'], meta_b['palette_sha256'])
    def test_two_zero_padding_bytes(self):
        _, m = decode_imy(fixture(pad=b'\0\0'))
        self.assertEqual(m['zero_tail_padding_bytes'], 2)
    def test_reject_nonzero_padding(self):
        with self.assertRaisesRegex(ValueError, 'padding'):
            decode_imy(fixture(pad=b'\0\x01'))
    def test_reject_long_padding(self):
        with self.assertRaisesRegex(ValueError, 'padding'):
            decode_imy(fixture(pad=b'\0'*4))
    def test_reject_bad_header(self):
        with self.assertRaisesRegex(ValueError, 'header'):
            decode_imy(b'bad')
    def test_reject_mode(self):
        with self.assertRaisesRegex(ValueError, 'mode'):
            decode_imy(fixture(mode=0x60).replace(b'IMY\x00\x60', b'IMY\x00\x70', 1))
    def test_reject_type(self):
        with self.assertRaisesRegex(ValueError, 'format'):
            decode_imy(fixture(image_type=0x94))
    def test_reject_short_palette(self):
        with self.assertRaisesRegex(ValueError, 'palette|length'):
            decode_imy(fixture(mode=0x20)[:400])
    def test_reject_zero_stride(self):
        with self.assertRaisesRegex(ValueError, 'geometry'):
            decode_imy(fixture(stride=0))
    def test_reject_odd_stride(self):
        with self.assertRaisesRegex(ValueError, 'geometry'):
            decode_imy(fixture(stride=3))
    def test_reject_empty_flags(self):
        with self.assertRaisesRegex(ValueError, 'flags'):
            decode_imy(fixture(flags=b''))
    def test_reject_truncated_flags(self):
        a = bytearray(fixture()); struct.pack_into('<H', a, 0x60, 6000)
        with self.assertRaisesRegex(ValueError, 'flags'):
            decode_imy(bytes(a))
    def test_reject_pixel_lookback(self):
        with self.assertRaisesRegex(ValueError, 'pixel lookback'):
            decode_imy(fixture(flags=b'\xC0', literals=b''))
    def test_reject_literal_lookback(self):
        with self.assertRaisesRegex(ValueError, 'literal lookback'):
            decode_imy(fixture(flags=b'\x10', literals=b''))
    def test_reject_overrun(self):
        with self.assertRaisesRegex(ValueError, 'target'):
            decode_imy(fixture(flags=b'\x02', literals=b'012345'))
    def test_reject_underrun(self):
        with self.assertRaisesRegex(ValueError, 'length'):
            decode_imy(fixture(flags=b'\x00', literals=b'AB'))
    def test_accept_two_zero_padding_flag_commands(self):
        _, m = decode_imy(fixture(flags=b'\x01\x00\x00', literals=b'ABCD'))
        self.assertEqual(m['unused_flag_command_count'], 2)
        self.assertTrue(m['unused_flags_are_zero'])
    def test_reject_four_unused_zero_flag_commands(self):
        with self.assertRaisesRegex(ValueError, 'unused'):
            decode_imy(fixture(flags=b'\x01' + b'\x00'*4, literals=b'ABCD'))
    def test_reject_unused_flag_commands(self):
        with self.assertRaisesRegex(ValueError, 'unused'):
            decode_imy(fixture(flags=b'\x01\x01', literals=b'01234567'))
    def test_reject_truncated_literal(self):
        with self.assertRaisesRegex(ValueError, 'source'):
            decode_imy(fixture(literals=b'AB'))
    def test_pixel_backreference(self):
        raw, _ = decode_imy(fixture(flags=b'\x00\xC0', literals=b'AB'))
        self.assertEqual(raw, b'ABAB')
    def test_literal_backreference(self):
        raw, _ = decode_imy(fixture(flags=b'\x00\x10', literals=b'AB'))
        self.assertEqual(raw, b'ABAB')
