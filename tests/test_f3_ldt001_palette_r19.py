import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from f3_ldt001_palette_r19 import inspect_tail,compare_candidate_quads
class PaletteCandidateTests(unittest.TestCase):
 def test_60_bytes(self):self.assertEqual(inspect_tail(bytes([3,4,5,255])*15)['alpha_histogram'],{255:15})
 def test_62_bytes(self):self.assertEqual(inspect_tail(b'\0\0'+bytes([0,0,0,255])*15)['alignment_bytes'],2)
 def test_bad_alignment(self):
  with self.assertRaises(ValueError):inspect_tail(b'\1\0'+bytes(60))
 def test_bad_length(self):
  with self.assertRaises(ValueError):inspect_tail(bytes(64))
 def test_short(self):
  with self.assertRaises(ValueError):inspect_tail(bytes(59))
class CandidateRelationTests(unittest.TestCase):
 def test_one_step_shift(self):
  a=[(i,0,0,255) for i in range(15)]
  b=a[1:]+[(255,0,0,255)]
  r=compare_candidate_quads(a,b)
  self.assertEqual(r['one_step_shift'],14)
  self.assertEqual(r['same_index'],0)
  self.assertFalse(r['runtime_palette_confirmed'])
 def test_identical_candidates(self):
  a=[(0,0,0,0)]*15
  self.assertEqual(compare_candidate_quads(a,a)['same_index'],15)
 def test_reject_invalid_candidate_count(self):
  with self.assertRaises(ValueError):compare_candidate_quads([(0,0,0,0)]*14,[(0,0,0,0)]*15)
if __name__=='__main__':unittest.main()
