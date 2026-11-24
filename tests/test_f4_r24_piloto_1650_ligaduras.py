"""R24 security tests for a PRIVATE candidate, never runtime evidence."""
import struct
import unittest
from tools.f4_r24_piloto_1650_ligaduras import (
 TARGET_EXTRA,BASE_INTEGRATED,BASE_DEFERRED,TOTAL_PLANNED,
 selection,metrics,replace_original_script,replace_member_payload
)
from tools.extract_cladun import dsarc_entries

def fake_plan(n=2002):
 return [
  {"offset":100+i*64,"bytes":6,"old":b"test00",
   "new":b"\xb4test0","group_id":f"{i+1:06d}"}
  for i in range(n)
 ]

def dsarc_fixture():
 content={
  "AISCRIPT.DAT":b"\x01\x02\x03\x04",
  "AISCRIPT.TBL":b"\x05\x06\x07\x08",
  "SCRIPT.DAT":b"DATA_ORIGINAL",
  "SCRIPT.TBL":b"\x09\x0A\x0B\x0C"
 }
 names=list(content);out=bytearray(1024)
 out[:8]=b"DSARC FL";struct.pack_into("<I",out,8,len(names))
 for i,name in enumerate(names):
  off=512+i*100;row=16+i*48;body=content[name]
  out[row:row+40]=name.encode().ljust(40,b"\0")
  struct.pack_into("<II",out,row+40,len(body),off)
  out[off:off+len(body)]=body
 return bytes(out),dsarc_entries(out)

class TestR24Pilot(unittest.TestCase):
 def test_target_requires_1650(self):
  self.assertEqual(TARGET_EXTRA,1650)
  self.assertEqual(TOTAL_PLANNED,8248)
  self.assertEqual(BASE_INTEGRATED+BASE_DEFERRED,TOTAL_PLANNED)
 def test_target_gain_exceeds_20_percentage_points(self):
  plan=fake_plan()
  m=metrics(plan,selection(plan,1650))
  self.assertGreaterEqual(m["pilot_gain_percentage_points"],20.0)
  self.assertEqual(m["candidate_baseline_plus_experiment_count"],5374)
 def test_official_progress_is_not_incremented(self):
  plan=fake_plan()
  m=metrics(plan,selection(plan,1650))
  self.assertEqual(m["new_official_integrations"],0)
  self.assertTrue(m["not_PPSSPP_proven"])
  self.assertTrue(m["not_canonical"])
  self.assertFalse(m["not_release_authorized"] is False)
 def test_take_only_1650(self):
  plan=fake_plan()
  chosen=selection(plan,1650)
  self.assertEqual(len(chosen),1650)
  self.assertEqual(chosen[0]["group_id"],"000001")
  self.assertEqual(chosen[-1]["group_id"],"001650")
 def test_small_pool_rejected(self):
  with self.assertRaises(ValueError):
   selection(fake_plan(1649),1650)
 def test_zero_limit_rejected(self):
  with self.assertRaises(ValueError):
   selection(fake_plan(),0)
 def test_boolean_limit_rejected(self):
  with self.assertRaises(ValueError):
   selection(fake_plan(),True)
 def test_duplicate_span_rejected(self):
  plan=fake_plan()
  plan[42]["offset"]=plan[41]["offset"]
  with self.assertRaises(ValueError):
   selection(plan,1650)
 def test_overlap_span_rejected(self):
  plan=fake_plan()
  plan[42]["offset"]=plan[41]["offset"]+2
  with self.assertRaises(ValueError):
   selection(plan,1650)
 def test_metric_refuses_misreport(self):
  plan=fake_plan()
  with self.assertRaises(ValueError):
   metrics(plan,selection(plan,1649))
 def test_fake_event_layout_rejected(self):
  with self.assertRaises(ValueError):
   replace_original_script(b"\0"*100,b"\0"*30,selection(fake_plan(),1650))
 def test_script_child_same_size_replacement(self):
  old,children=dsarc_fixture()
  changed=replace_member_payload(old,children,"SCRIPT.DAT",b"DATA_MODIFIED")
  self.assertEqual(len(old),len(changed))
  self.assertEqual(dsarc_entries(changed),children)
  self.assertIn(b"DATA_MODIFIED",changed)
 def test_script_child_different_size_rejected(self):
  old,children=dsarc_fixture()
  with self.assertRaises(ValueError):
   replace_member_payload(old,children,"SCRIPT.DAT",b"too short")
 def test_script_child_unrelated_preserved(self):
  old,children=dsarc_fixture()
  new=replace_member_payload(old,children,"SCRIPT.DAT",b"DATA_MODIFIED")
  for m in children:
   if m["name"]=="SCRIPT.DAT":continue
   start=m["offset"];end=start+m["size"]
   self.assertEqual(old[start:end],new[start:end])
 def test_no_script_child_rejected(self):
  old,children=dsarc_fixture()
  with self.assertRaises(StopIteration):
   replace_member_payload(old,children,"WRONG_NAME",b"x")
 def test_source_preimage_never_silently_falls_back(self):
  # Real source scan requires an exact 1625-block SCRIPT.TBL, not a guessed offset.
  with self.assertRaises(Exception):
   replace_original_script(b"",b"",[])
if __name__=="__main__": unittest.main()
