import sys
import unittest
from pathlib import Path
import csv

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import build_translation_corpus as c

class TranslationCorpusTests(unittest.TestCase):
    def test_counts_and_order(self):
        s=c.run(ROOT)
        self.assertEqual(s['total_para_traducir_y_revisar'],9212)
        self.assertEqual(s['confirmados_no_vacios'],6397)
        self.assertEqual(s['candidatos_no_vacios'],2803)
        self.assertEqual(s['falsos_positivos_descartados'],56)
        self.assertEqual(s['vacios_descartados'],391)
        with (ROOT/'corpus/textos_para_traducir.csv').open(encoding='utf-8-sig',newline='') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),len({x['text_id'] for x in rows}))
        self.assertFalse(any(x['fuente']=='DATABASE.DAT/LV.DAT' for x in rows))
        self.assertTrue(all(x['texto_original'].strip() for x in rows))
        self.assertEqual(rows[0]['texto_original'], 'Is this the tavern?')
        self.assertNotIn('opcode_hex',rows[0])
    def test_graphics_are_separate(self):
        with (ROOT/'corpus/textos_graficos.csv').open(encoding='utf-8-sig',newline='') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows),12)
        self.assertEqual(sum(x['texto_original']=='NO DATA' for x in rows),2)

if __name__=='__main__':unittest.main()
