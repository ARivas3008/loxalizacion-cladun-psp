"""Comprobar contrato fuente/códec sin incluir materiales protegidos de Cladun."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from charset_es import CODE_BASE as CODEC_BASE, ES_GLYPHS, ES_BYTES, encode_spanish, decode_spanish
from font_es_patch import CODE_BASE as FONT_BASE, CHARACTERS, BASE_GLYPHS


class TestSpanishFontContract(unittest.TestCase):
    def test_font_indices_match_codec_exactly(self):
        self.assertEqual(FONT_BASE, CODEC_BASE)
        self.assertEqual(CHARACTERS, ES_GLYPHS)
        self.assertEqual(len(CHARACTERS), len(BASE_GLYPHS))
        self.assertEqual(len(CHARACTERS), 19)
        self.assertEqual([int.from_bytes(ES_BYTES[c], "big") for c in CHARACTERS],
                         list(range(0xF5A0, 0xF5B3)))

    def test_normalization_does_not_silently_modify_translation(self):
        # Una entrada descompuesta debe normalizarse explícitamente por edición,
        # no alterarse al preparar un manifiesto de reinserción.
        composed = "Está"
        decomposed = "Esta\u0301"
        self.assertEqual(encode_spanish(composed), encode_spanish(decomposed))
        self.assertNotEqual(decode_spanish(encode_spanish(decomposed)), decomposed)

    def test_original_cp932_ascii_and_japanese_untouched(self):
        text = "Hiyoji, Pudding 日本語 ⑨"
        encoded = encode_spanish(text)
        self.assertEqual(encoded, text.encode("cp932"))
        self.assertEqual(decode_spanish(encoded), text)


if __name__ == "__main__":
    unittest.main()
