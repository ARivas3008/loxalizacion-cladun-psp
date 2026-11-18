#!/usr/bin/env python3
"""No ISO or commercial game assets required for these tests."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent.parent/'tools'))
from charset_es import CODE_BASE,ES_GLYPHS,encode_spanish,decode_spanish,ascii_diagnostic_preview

class CharsetTest(unittest.TestCase):
    def test_roundtrip_all(self):
        text='¿Qué día es? ¡Sí, señor! Pudding: «ñandú», pingüino, ō. 日本語'
        self.assertEqual(decode_spanish(encode_spanish(text)),text)
    def test_cp932_private_codes(self):
        self.assertEqual(len(ES_GLYPHS),19)
        self.assertEqual(encode_spanish(ES_GLYPHS).hex().upper(),
                         ''.join(f'{CODE_BASE+i:04X}' for i in range(19)))
    def test_reject_damaged_source(self):
        with self.assertRaises(ValueError):
            encode_spanish('Texto perdido \ufffd')
    def test_preview_not_real_spanish(self):
        self.assertEqual(ascii_diagnostic_preview('¿Dónde está? ¡Sí!'),'?Donde esta? !Si!')
    def test_existing_cp932_unchanged(self):
        self.assertEqual(encode_spanish('Hiyoji'),b'Hiyoji')
        self.assertEqual(len(encode_spanish('á')),2)

if __name__=='__main__':unittest.main()
