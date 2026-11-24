import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from f4_r21_ligature_capacity import read_canonical,decode_encoded
from f4_r21_ligature_collision_safe import analyze_collision_free
from f4_r21_ligature_overlay import make_plan,simulate_authenticated

class LigatureOverlaySafetyTests(unittest.TestCase):
 def test_public_corpus_plan_is_noncanonical(self):
  rows=read_canonical(ROOT/"traduccion/CLADUN_BORRADOR_ES.csv")
  plan,report=make_plan(rows)
  self.assertEqual(len(plan),2002)
  self.assertEqual(report["candidate_payload_bytes"],61723)
  self.assertEqual(report["growing_texts"],2883)
  self.assertEqual(report["candidate_rows_with_controls_excluded"],74)
  self.assertEqual(report["candidates_after_strict_source_controls"],len(plan))
  self.assertFalse(report["deployment_authorized"])
  self.assertFalse(report["canonical_approved"])
  pairs=analyze_collision_free(rows)["pairs"]
  for item in plan[:40]:
   self.assertEqual(len(item["old"]),len(item["new"]))
   self.assertEqual(len(item["old"]),item["bytes"])
   self.assertNotEqual(item["old"],item["new"])
   self.assertTrue(all(32<=b<=126 and b not in (37,92) for b in item["old"]))
  self.assertEqual(len(set(z["offset"] for z in plan)),len(plan))
 def test_source_controls_are_never_considered_for_overlay(self):
  rows=read_canonical(ROOT/"traduccion/CLADUN_BORRADOR_ES.csv")
  plan,_=make_plan(rows)
  self.assertTrue(all(37 not in p["old"] and 92 not in p["old"] for p in plan))
 def test_every_rewritten_slot_preserves_byte_length_and_utf8_ownership(self):
  rows=read_canonical(ROOT/"traduccion/CLADUN_BORRADOR_ES.csv")
  plan,_=make_plan(rows)
  self.assertTrue(all(len(p["old"])==len(p["new"])==p["bytes"] for p in plan))
  self.assertEqual(len({p["group_id"] for p in plan}),len(plan))
 def test_authenticated_replay_rejects_invalid_source(self):
  with self.assertRaises(ValueError):
   simulate_authenticated(b"Wrong",b"Wrong",[])
 def test_four_ligature_candidate_does_not_move_text_slots(self):
  rows=read_canonical(ROOT/"traduccion/CLADUN_BORRADOR_ES.csv")
  plan,summary=make_plan(rows,ligature_count=4)
  self.assertEqual(len(plan),542)
  self.assertEqual(summary["candidate_payload_bytes"],17076)
  self.assertEqual(summary["selected_ligatures"],4)
  self.assertFalse(summary["deployment_authorized"])
 def test_reject_bad_ligature_count(self):
  rows=read_canonical(ROOT/"traduccion/CLADUN_BORRADOR_ES.csv")
  for count in (0,45,-1):
   with self.assertRaises(ValueError):make_plan(rows,ligature_count=count)
 def test_reject_code_that_is_not_in_four_ligature_font(self):
  from f4_r21_ligature_capacity import decode_encoded
  with self.assertRaises(ValueError):decode_encoded(bytes([0xB8]),["es","en","de","er"])
if __name__=="__main__":unittest.main()
