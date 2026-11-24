"""R24 security tests for a PRIVATE candidate, never runtime evidence."""
import struct
import unittest
from tools.f4_r21_ligature_capacity import read_canonical
from tools.f4_r21_ligature_overlay import make_plan
from tools.f4_r24_piloto_1650_ligaduras import (
 TARGET_EXTRA,BASE_INTEGRATED,BASE_DEFERRED,TOTAL_PLANNED,
 selection,metrics,replace_original_script,replace_member_payload,font_allowed_span,unchanged_resources_against_baseline
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
 def test_real_committed_corpus_yields_at_least_1650(self):
  from pathlib import Path
  corpus=Path(__file__).resolve().parents[1]/"traduccion/CLADUN_BORRADOR_ES.csv"
  candidates,meta=make_plan(read_canonical(corpus),ligature_count=44)
  self.assertEqual(len(candidates),2002)
  chosen=selection(candidates,1650)
  self.assertEqual(len(chosen),1650)
  self.assertEqual(metrics(candidates,chosen)["candidate_baseline_plus_experiment_count"],5374)
  self.assertEqual(len({i["offset"] for i in chosen}),1650)
 def test_all_selected_preserve_source_length(self):
  from pathlib import Path
  corpus=Path(__file__).resolve().parents[1]/"traduccion/CLADUN_BORRADOR_ES.csv"
  candidates,_=make_plan(read_canonical(corpus),ligature_count=44)
  for item in selection(candidates,1650):
   self.assertEqual(len(item["new"]),len(item["old"]))
   self.assertEqual(item["bytes"],len(item["old"]))
 def test_font_shrink_144352_to_144000_clears_only_old_font(self):
  # The R23 base 19-glyph font occupies 144352 bytes. New R24 compact
  # 19+44 occupies 144000; authorize the FULL original resource tail.
  off=11776
  self.assertEqual(
   font_allowed_span(off,144352,144000,156160),
   (off,off+144352))
 def test_font_growth_only_allowed_until_pspfs_neighbor(self):
  self.assertEqual(font_allowed_span(11776,143888,144000,156160),
                   (11776,11776+144000))
 def test_font_oversize_rejected_before_neighbor_corruption(self):
  with self.assertRaises(ValueError):
   font_allowed_span(11776,144352,145696,156160)
 def test_font_bool_or_negative_geometry_rejected(self):
  for args in [(True,10,10,100),(-1,10,20,100),(10,0,20,100)]:
   with self.subTest(args=args),self.assertRaises(ValueError):
    font_allowed_span(*args)
 def test_editorial_manifest_matches_exact_Python_1650_selected(self):
  import csv
  from pathlib import Path
  root=Path(__file__).resolve().parents[1]
  corpus=root/"traduccion/CLADUN_BORRADOR_ES.csv"
  manifest=root/"traduccion/propuestas/R24_COLA_EDITORIAL_1650.csv"
  plan,_=make_plan(read_canonical(corpus),ligature_count=44)
  expected=selection(plan,1650)
  with manifest.open(encoding="utf-8",newline="") as handle:
   rows=list(csv.DictReader(handle))
  self.assertEqual(len(rows),1650)
  for row,item in zip(rows,expected):
   self.assertEqual(row["grupo_id"],item["group_id"])
   self.assertEqual(int(row["offset_hex"],16),item["offset"])
   self.assertEqual(int(row["bytes_origen"]),item["bytes"])
   self.assertEqual(row["dictamen_editorial"],"PENDIENTE_CONTEXTUAL")
   self.assertEqual(row["verificacion_ppsspp"],"NOT_RUN")
   self.assertEqual(row["integracion_canonica"],"NO")
 def test_final_binary_comparison_uses_translated_baseline_not_original(self):
  # In a canonical baseline DATABASE.DAT, SYS.DAT2 and STAFFROLL.TXT
  # legitimately differ from the USA source: only the NEW FONT/SCRIPT
  # may differ between baseline and final experimental ISO.
  names=["DATA_%03d" %i for i in range(349)]
  names[10]="DATABASE.DAT"
  names[11]="STAFFROLL.TXT"
  names[12]="SYS.DAT2"
  names[231]="SCRIPT.SDT"
  names[308]="FONT.ARC"
  entries=[{"name":name,"index":i,"offset":i*8,"size_stored":8}
           for i,name in enumerate(names)]
  baseline=bytearray(b"o"*349*8)
  for i in [10,11,12]:baseline[i*8:(i+1)*8]=b"SPANISH!"
  candidate=bytearray(baseline)
  candidate[231*8:232*8]=b"SCRIPT!!"
  candidate[308*8:309*8]=b"FONT!!!!"
  self.assertEqual(
   unchanged_resources_against_baseline(entries,bytes(baseline),
    entries,bytes(candidate)),347)
 def test_reject_unrelated_neighboring_asset_mutation_after_baseline(self):
  entries=[{"name":"FONT.ARC" if i==308 else
            "SCRIPT.SDT" if i==231 else f"R_{i}",
            "index":i,"offset":i*8,"size_stored":8} for i in range(349)]
  old=b"x"*349*8
  modified=bytearray(old);modified[5*8]=0
  with self.assertRaises(ValueError):
   unchanged_resources_against_baseline(entries,old,entries,bytes(modified))
 def test_reject_other_metadata_mutation_after_baseline(self):
  entries=[{"name":"FONT.ARC" if i==308 else
            "SCRIPT.SDT" if i==231 else f"R_{i}",
            "index":i,"offset":i*8,"size_stored":8} for i in range(349)]
  wrong=[dict(x) for x in entries]
  wrong[10]["offset"]+=1
  with self.assertRaises(ValueError):
   unchanged_resources_against_baseline(entries,b"x"*2792,wrong,b"x"*2792)
 def test_reject_incomplete_349_inventory_after_baseline(self):
  entries=[{"name":f"R_{i}","index":i,"offset":i*8,"size_stored":8}
           for i in range(349)]
  with self.assertRaises(ValueError):
   unchanged_resources_against_baseline(entries[:-1],b"x"*2792,
                                        entries[:-1],b"x"*2792)
 def test_source_preimage_never_silently_falls_back(self):
  # Real source scan requires an exact 1625-block SCRIPT.TBL, not a guessed offset.
  with self.assertRaises(Exception):
   replace_original_script(b"",b"",[])
if __name__=="__main__": unittest.main()
