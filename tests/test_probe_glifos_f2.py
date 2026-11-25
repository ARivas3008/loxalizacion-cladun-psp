"""F2 isolated Spanish 19-glyph overlay: no edits to canonical CSV or events."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from integrar_parche_seguro import source_rows
from generar_probe_f2_glifos import prepare, DIAGNOSTIC_ID, DIAGNOSTIC_TEXT
from charset_es import ES_GLYPHS, decode_spanish, encode_spanish

class TestGlyphProbeF2(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.source=source_rows()
    def test_exact_changes_and_glyph_coverage(self):
        result,report=prepare(self.source)
        self.assertEqual(len(result),9237)
        self.assertEqual(report['one_diagnostic_id'],DIAGNOSTIC_ID)
        self.assertEqual(report['full_glyphs'],ES_GLYPHS)
        self.assertEqual(report['changes'],[('005694',['espanol']),('005709',['espanol']),('005713',['espanol'])])
        self.assertEqual(decode_spanish(encode_spanish(DIAGNOSTIC_TEXT)),DIAGNOSTIC_TEXT)
        self.assertEqual(''.join(c for c in DIAGNOSTIC_TEXT if c in ES_GLYPHS), ES_GLYPHS)
        for (source,old),(same,new) in zip(self.source,result):
            self.assertEqual(source,same)
            if source['grupo_id'] not in ('005694','005709','005713'):
                self.assertEqual(old,new)
    def test_preimage_rejection(self):
        broken=[(s,dict(d)) for s,d in self.source]
        for s,d in broken:
            if s['grupo_id']=='005694':d['espanol']='otro'
        with self.assertRaises(ValueError):prepare(broken)
