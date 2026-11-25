import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from f4_r21_ligature_capacity import (CAPACITY,CODE_START,WIDTHS,allowed_pair,
 matching,encode_fixed,decode_encoded,read_canonical,analyze,original_halfwidth_inventory)
PAIRS=["de","en","es","er","ue","ar","ra","os","te","qu","nt","do","ta","as","el","or",
"la","to","st","on","lo","re","an","al","co","un","na","ie","ca","ro","ad","me",
"da","in","pa","so","pe","ci","se","nd","mo","sa","po","ed"]
class LigatureFeasibilityTests(unittest.TestCase):
 def test_code_slots(self):
  self.assertEqual((CODE_START,CAPACITY,CODE_START+CAPACITY-1),(0xB4,44,0xDF))
 def test_dictionary_pairs_under_16_pixels(self):
  self.assertEqual(len(PAIRS),44)
  self.assertTrue(all(allowed_pair(s) for s in PAIRS))
  self.assertFalse(allowed_pair("mm"))
  self.assertFalse(allowed_pair("Ae"))
 def test_overlapping_pairs_not_double_counted(self):
  self.assertEqual(matching("dede",PAIRS),[(0,"de"),(2,"de")])
 def test_encode_decode_one_ligature(self):
  b=encode_fixed("dede",3,PAIRS)
  self.assertEqual(len(b),3)
  self.assertEqual(decode_encoded(b,PAIRS),"dede")
 def test_encode_decode_two_ligatures(self):
  b=encode_fixed("dede",2,PAIRS)
  self.assertEqual(decode_encoded(b,PAIRS),"dede")
 def test_cannot_shrink_more_than_available(self):
  with self.assertRaisesRegex(ValueError,"Not enough"):
   encode_fixed("dede",1,PAIRS)
 def test_shortenings_not_auto_padded(self):
  with self.assertRaises(ValueError):
   encode_fixed("dede",5,PAIRS)
 def test_same_width_not_altered(self):
  with self.assertRaises(ValueError):
   encode_fixed("dede",4,PAIRS)
 def test_invalid_dictionary_rejected(self):
  with self.assertRaises(ValueError):
   encode_fixed("dede",2,["de"]*44)
 def test_multibyte_truncation_rejected(self):
  with self.assertRaises(ValueError):
   decode_encoded(b"\x81",PAIRS)
 def test_shiftjis_trail_is_not_halfwidth_code(self):
  self.assertEqual(original_halfwidth_inventory([{"grupo_id":"1","bytes_hex":"81B4"}]),(0,[]))
  self.assertEqual(original_halfwidth_inventory([{"grupo_id":"1","bytes_hex":"B4"}]),(1,[]))
 def test_full_canonical_matrix(self):
  data=read_canonical(ROOT/"traduccion/CLADUN_BORRADOR_ES.csv")
  r=analyze(data)
  self.assertEqual((r["growing"],r["theoretically_fittable_growing"],r["shrinking"]),(2883,2120,1641))
  self.assertEqual(r["original_standalone_A1_DF_codepoints"],0)
  self.assertFalse(r["approved_for_reinsertion"])
  self.assertFalse(r["emulator_proven"])
if __name__=="__main__":unittest.main()
