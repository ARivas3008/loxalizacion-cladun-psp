"""Synthetic byte-width classification and source-authentication failures."""
import sys,unittest,csv,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from f4_r20_script_width_deltas import classify

def row(gid,english,spanish,offset='0x0'):
 return {'grupo_id':gid,'origen':'SCRIPT.SDT/SCRIPT.DAT','espanol':spanish,'bytes_hex':english.encode('ascii').hex(),'offset_hex':offset}

class WidthDeltaTests(unittest.TestCase):
 def test_same_width(self):
  x=classify([row('000001','Hello','Adios')])
  self.assertEqual(x['same_byte_width'],1)
  self.assertEqual(x['variable_byte_width'],0)
 def test_one_byte_growth_and_shrink(self):
  x=classify([row('1','Hello','Adiós!'),row('2','Hello','Hola')])
  self.assertEqual(x['growing'],1)
  self.assertEqual(x['shrinking'],1)
  self.assertEqual(x['variable_within_3_bytes'],2)
 def test_empty_translation_not_counted(self):
  x=classify([row('1','Hello','')])
  self.assertEqual(x['without_spanish'],1)
  self.assertEqual(x.get('translated_script_rows',0),0)
 def test_duplicate_gid_rejected(self):
  with self.assertRaises(ValueError):classify([row('1','Hi','Sí'),row('1','Hi','No')])
 def test_bad_original_preimage_not_counted(self):
  with self.assertRaisesRegex(ValueError,'authenticated source preimage mismatch'):
   classify([row('1','Hello','Adios')],b'Wrong')
 def test_authentic_preimage_success(self):
  x=classify([row('1','Hello','Adios')],b'Hello')
  self.assertEqual(x['evidence'],'A_AUTHENTIC_SCRIPT_PREIMAGE')
 def test_never_authorizes_variable_length(self):
  x=classify([row('1','Hi','Hola')])
  self.assertFalse(x['variable_length_insertion_authorized'])
  self.assertFalse(x['ppsspp_verified'])
 def test_non_script_ignored(self):
  x=classify([{'grupo_id':'1','origen':'FONT.ARC','espanol':'Hola','bytes_hex':'00','offset_hex':'0'}])
  self.assertEqual(x.get('translated_script_rows',0),0)

 def test_repository_corpus_static_metrics(self):
  path=Path(__file__).resolve().parents[1]/'traduccion'/'CLADUN_BORRADOR_ES.csv'
  with path.open(encoding='utf-8-sig',newline='') as stream:
   result=classify(csv.DictReader(stream))
  self.assertGreater(result.get('translated_script_rows',0),5000)
  self.assertGreater(result.get('variable_byte_width',0),4000)
  self.assertFalse(result['variable_length_insertion_authorized'])
  print('R20_SCRIPT_WIDTH_METRICS='+json.dumps({k:v for k,v in result.items() if k not in ('delta_histogram','invalid_examples_without_text')},sort_keys=True))
if __name__=='__main__':unittest.main()
