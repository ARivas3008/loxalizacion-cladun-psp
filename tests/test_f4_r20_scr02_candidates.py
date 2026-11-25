"""R20: six scr02 review-only candidates must preserve exact CP932 byte width."""
import csv,sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from charset_es import encode_spanish,decode_spanish
class Scr02Candidates(unittest.TestCase):
 def test_all_candidate_widths_and_roundtrips(self):
  with (ROOT/'traduccion/propuestas/SCRIPT_SCR02_LONGITUD_FIJA_R20.csv').open(encoding='utf-8',newline='') as f:
   rows=list(csv.DictReader(f))
  self.assertEqual(len(rows),6)
  self.assertEqual(len({r['grupo_id'] for r in rows}),6)
  for r in rows:
   with self.subTest(group=r['grupo_id']):
    raw=encode_spanish(r['propuesta_es'])
    self.assertEqual(len(raw),int(r['original_bytes']))
    self.assertEqual(decode_spanish(raw),r['propuesta_es'])
    self.assertEqual(r['estado'],'PROPUESTA_NO_CANONICA_PENDIENTE_CONTEXTO')
 def test_reject_oversized_synthetic(self):
  with self.assertRaises(AssertionError):
   self.assertEqual(len(encode_spanish('¡Hola! largo')),6)
if __name__=='__main__':unittest.main()
