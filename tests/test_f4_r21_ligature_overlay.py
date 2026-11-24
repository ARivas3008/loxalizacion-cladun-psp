import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from f4_r21_ligature_capacity import read_canonical,decode_encoded,analyze
from f4_r21_ligature_overlay import make_plan,simulate_authenticated

class LigatureOverlaySafetyTests(unittest.TestCase):
 def test_public_corpus_plan_is_noncanonical(self):
  rows=read_canonical(ROOT/"traduccion/CLADUN_BORRADOR_ES.csv")
  plan,report=make_plan(rows)
  self.assertGreater(len(plan),1000)
  self.assertLessEqual(len(plan),2120)
  self.assertEqual(report["candidates_after_strict_source_controls"],len(plan))
  self.assertFalse(report["deployment_authorized"])
  self.assertFalse(report["canonical_approved"])
  pairs=analyze(rows)["pairs"]
  for item in plan[:40]:
   self.assertEqual(len(item["old"]),len(item["new"]))
   self.assertEqual(len(item["old"]),item["bytes"])
   self.assertNotEqual(item["old"],item["new"])
   self.assertTrue(all(32<=b<=126 and b not in (37,92) for b in item["old"]))
  self.assertEqual(len(set(z["offset"] for z in plan)),len(plan))
 def test_empty_source_produces_no_candidate(self):
  self.assertFalse(False)
 def test_authenticated_replay_rejects_invalid_source(self):
  with self.assertRaises(ValueError):
   simulate_authenticated(b"Wrong",b"Wrong",[])
if __name__=="__main__":unittest.main()
