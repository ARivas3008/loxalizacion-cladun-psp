"""Synthetic IMY corruption tests; no proprietary data in test fixtures."""
import struct
import unittest

from tools.f2_auditar_dos_fuentes_imy import unpack_image, sha

def img(flags, lit, stride=2, rows=2, pointer=96, typ=0xA4):
    b = bytearray(98)
    b[:4] = b'IMY\x00'
    struct.pack_into('<H', b, 4, pointer)
    struct.pack_into('<H', b, 8, stride)
    b[10] = typ
    struct.pack_into('<H', b, 12, rows)
    struct.pack_into('<H', b, 96, len(flags))
    return bytes(b) + flags + lit

class TestF2DosFuentesIMY(unittest.TestCase):
    def test_four_pixel_words(self):
        raw, meta = unpack_image(img(b'\x01', b'\x10\x32\x54\x76'))
        self.assertEqual(raw, b'\x10\x32\x54\x76')
        self.assertEqual(meta['width_pixels_for_4bpp'], 4)
        self.assertEqual(sum(meta['pixel_index_counts']), 8)

    def test_neighbor_lookback(self):
        raw, meta = unpack_image(img(b'\x00\xC0', b'AB'))
        self.assertEqual(raw, b'ABAB')

    def test_literal_reference(self):
        raw, meta = unpack_image(img(b'\x00\x10', b'CD'))
        self.assertEqual(raw, b'CDCD')

    def test_reject_bad_header(self):
        with self.assertRaisesRegex(ValueError, 'signature'):
            unpack_image(b'bad')

    def test_reject_unsupported_flags_pointer(self):
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            unpack_image(img(b'\x01', b'0000', pointer=64))

    def test_accept_high_byte_flags(self):
        raw, meta = unpack_image(img(b'\x01', b'abcd', pointer=0x8060))
        self.assertEqual(meta['header_flags_field_hex'], '0x8060')

    def test_reject_unsupported_type(self):
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            unpack_image(img(b'\x01', b'0000', typ=0))

    def test_reject_zero_stride(self):
        with self.assertRaisesRegex(ValueError, 'stride'):
            unpack_image(img(b'\x01', b'0000', stride=0))

    def test_reject_odd_stride(self):
        with self.assertRaisesRegex(ValueError, 'stride'):
            unpack_image(img(b'\x01', b'0000', stride=3))

    def test_reject_truncated_flags(self):
        b = bytearray(img(b'\x00', b'AB'))
        struct.pack_into('<H', b, 96, 10000)
        with self.assertRaisesRegex(ValueError, 'Truncated'):
            unpack_image(bytes(b))

    def test_reject_bad_pixel_lookback(self):
        with self.assertRaisesRegex(ValueError, 'pixel lookback'):
            unpack_image(img(b'\xC0', b''))

    def test_reject_bad_literal_lookback(self):
        with self.assertRaisesRegex(ValueError, 'literal lookback'):
            unpack_image(img(b'\x10', b''))

    def test_reject_overrun(self):
        with self.assertRaisesRegex(ValueError, 'exceeds'):
            unpack_image(img(b'\x02', b'ABCDEF'))

    def test_reject_trailing(self):
        with self.assertRaisesRegex(ValueError, 'unconsumed trailing'):
            unpack_image(img(b'\x01', b'ABCD!'))

    def test_checksum_determinism(self):
        self.assertEqual(sha(b'AA'), sha(b'AA'))
        self.assertNotEqual(sha(b'AA'), sha(b'AB'))

    def test_meta_alone_not_gameplay_claim(self):
        raw, meta = unpack_image(img(b'\x01', b'ABCD'))
        self.assertIn('decoded_sha256', meta)
        self.assertNotIn('image_pixels', meta)
        self.assertNotIn('ppsspp_runtime', meta)
