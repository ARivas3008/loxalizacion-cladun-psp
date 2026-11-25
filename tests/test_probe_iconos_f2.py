"""Pure synthetic F2 palette controls; never use screenshots as fixtures."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from generar_probe_f2_iconos import recolor_palette_only

class TestIconProbeF2(unittest.TestCase):
    def make_imy(self):
        v=bytearray(2480)
        v[:4]=b'IMY\0'; v[4:8]=(0x2060).to_bytes(4,'little')
        for i in range(16):v[32+4*i:36+4*i]=bytes((12,34,56,255))
        return bytes(v)
    def test_only_palette_rgb_changes(self):
        original=self.make_imy()
        result, diff=recolor_palette_only(original)
        self.assertTrue(25<=len(diff)<=33)
        self.assertEqual(original[:32],result[:32])
        self.assertEqual(original[96:],result[96:])
        for i in range(16):
            self.assertEqual(original[32+4*i+3],result[32+4*i+3])
        for i in range(5,16):self.assertEqual(result[32+4*i:35+4*i],b'\xff\x00\xff')
    def test_rejects_wrong_format_and_alpha(self):
        with self.assertRaisesRegex(ValueError,'cabecera'):
            recolor_palette_only(b'not-an-IMY')
        bad=bytearray(self.make_imy());bad[32+5*4+3]=0
        with self.assertRaisesRegex(ValueError,'alpha'):
            recolor_palette_only(bytes(bad))
