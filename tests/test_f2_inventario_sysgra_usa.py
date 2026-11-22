"""Synthetic DSARC checks only; no copyrighted image data."""
import struct
import unittest

from tools.f2_inventario_sysgra_usa import inspect_dsarc

def fake_imy(stride=32, rows=8, payload=b'A' * 16):
    raw = bytearray(b'IMY\0' + b'\x20\0\0\0' + b'\0' * 8 + payload)
    struct.pack_into('<H', raw, 8, stride)
    struct.pack_into('<H', raw, 12, rows)
    return bytes(raw)

def make_arc(names=('HP_BAR.IMY', 'DAMAGE.IMY'), contents=None):
    if contents is None:
        contents = (fake_imy(), fake_imy(payload=b'B' * 16))
    total = len(names)
    buf = bytearray(16 + 48 * total)
    buf[:8] = b'DSARC FL'
    struct.pack_into('<I', buf, 8, total)
    for index, (name, content) in enumerate(zip(names, contents)):
        offset = len(buf)
        buf.extend(content)
        pos = 16 + 48 * index
        buf[pos:pos + len(name)] = name.encode('ascii')
        struct.pack_into('<II', buf, pos + 40, len(content), offset)
    return bytes(buf)

class TestSysgraStaticInventory(unittest.TestCase):
    def test_two_valid_members_metadata_only(self):
        rows = inspect_dsarc(make_arc(), expected_count=2)
        self.assertEqual([r['name'] for r in rows], ['HP_BAR.IMY', 'DAMAGE.IMY'])
        self.assertEqual(rows[0]['imy_header_stride_bytes'], 32)
        self.assertEqual(rows[0]['imy_header_rows'], 8)
        self.assertFalse(rows[0]['rendered_in_ppsspp_proven'])
        self.assertEqual(rows[0]['context_hint_only'], 'nombre_sugiere_HUD_o_combate_NO_PROBADO')
    def test_exclusive_shas_not_payload(self):
        rows = inspect_dsarc(make_arc(), expected_count=2)
        self.assertNotEqual(rows[0]['sha256'], rows[1]['sha256'])
        self.assertNotIn('pixels', rows[0])
        self.assertNotIn('palette_bytes', rows[0])
    def test_duplicate_names_rejected(self):
        with self.assertRaisesRegex(ValueError, 'duplicados'):
            inspect_dsarc(make_arc(names=('FONT.IMY', 'FONT.IMY')), expected_count=2)
    def test_missing_member_rejected(self):
        with self.assertRaisesRegex(ValueError, 'Número DSARC'):
            inspect_dsarc(make_arc(), expected_count=27)
    def test_member_overlaps_directory_rejected(self):
        a = bytearray(make_arc())
        struct.pack_into('<I', a, 16 + 40 + 4, 40)
        with self.assertRaisesRegex(ValueError, 'overlaps directory'):
            inspect_dsarc(bytes(a), expected_count=2)
    def test_member_overlaps_other_member_rejected(self):
        a = bytearray(make_arc())
        struct.pack_into('<I', a, 16 + 48 + 40 + 4, 113)
        with self.assertRaisesRegex(ValueError, 'overlap'):
            inspect_dsarc(bytes(a), expected_count=2)
    def test_unsupported_member_magic_rejected(self):
        a = make_arc(contents=(b'FAKE' + fake_imy()[4:], fake_imy()))
        with self.assertRaisesRegex(ValueError, 'no es IMY'):
            inspect_dsarc(a, expected_count=2)
    def test_invalid_image_geometry_rejected(self):
        a = make_arc(contents=(fake_imy(stride=0), fake_imy()))
        with self.assertRaisesRegex(ValueError, 'Dimensiones IMY'):
            inspect_dsarc(a, expected_count=2)
