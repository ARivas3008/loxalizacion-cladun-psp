"""R26 independent coverage/capacity regressions; no proprietary ISO in CI."""
import unittest
from pathlib import Path
from tools.f4_r21_ligature_capacity import read_canonical
from tools.r26_script_full_capacity_audit import (
 BLOCKS,TRACKED,OFFICIAL_DONE,TOTAL_CHANGES,
 census,optimized_44_census,block_costs,audit,authentic_block_metadata
)

ROOT=Path(__file__).resolve().parents[1]
SOURCE=ROOT/"traduccion/CLADUN_BORRADOR_ES.csv"

def blocks_fixture():
 return [{
   "index":i,"name":f"sample_{i}","script_id":i+1,"padding":5
 } for i in range(BLOCKS)]

class TestR26ScriptFullCapacity(unittest.TestCase):
 def test_source_corpus_completeness(self):
  sums,h=census(read_canonical(SOURCE))
  self.assertEqual(len(sums),586)
  self.assertEqual(h["growing"],2883)
  self.assertEqual(h["shrinking"],1641)
  self.assertEqual(h["equal"],683)
  self.assertEqual(h["positive_byte_delta"],17108)
  self.assertEqual(h["negative_byte_delta"],7414)
  self.assertEqual(sum(sums.values()),9694)
  self.assertEqual(h["growing"]+h["shrinking"]+h["equal"],TRACKED)
 def test_real_corpus_44_ligatures_lowers_net_pressure(self):
  sums,info=optimized_44_census(read_canonical(SOURCE))
  self.assertEqual(len(sums),586)
  self.assertEqual(sum(sums.values()),-4382)
  self.assertEqual(info["safe_ligature_savings_bytes"],14076)
  self.assertEqual(info["growing_rows_preserved_without_ligatures_due_controls"],74)
  self.assertEqual(info["safe_growing_rows_still_resized_after_max_matches"],807)
  self.assertEqual(info["safe_remaining_positive_text_byte_growth"],2482)
  self.assertTrue(info["source_script_commands_would_move_in_this_mode"])
  self.assertFalse(info["safe_to_deploy_or_claim_100pct"])
 def test_compression_does_not_turn_B_into_100pct(self):
  report=audit(SOURCE)
  self.assertFalse(report["100pct_reached"])
  self.assertFalse(report["game_tested_ppsspp_C"])
  self.assertEqual(report["optimized_44_theoretical"][
      "full_script_theoretical_net_delta_bytes"],-4382)
 def test_B_only_does_not_claim_authenticated_runtime(self):
  report=audit(SOURCE)
  self.assertEqual(report["source_original_status"],"NOT_SUPPLIED")
  self.assertFalse(report["100pct_reached"])
  self.assertEqual(report["historical_integrated_unchanged"],3724)
  self.assertEqual(report["net_text_growth_bytes"],9694)
  self.assertFalse(report["game_tested_ppsspp_C"])
  self.assertNotIn("local_script_capacity",report)
 def test_known_history_is_consistent(self):
  self.assertEqual((OFFICIAL_DONE,TOTAL_CHANGES),(3724,8248))
  self.assertEqual(OFFICIAL_DONE+4524,TOTAL_CHANGES)
 def test_simple_local_capacity_exceeded(self):
  b=blocks_fixture()
  g={("sample_0",1):9,("sample_1",2):-15,
     ("sample_2",3):5}
  r=block_costs(b,g)
  self.assertEqual(r["corpus_script_ids_matched"],3)
  self.assertEqual(r["original_all_blocks_padding_bytes"],BLOCKS*5)
  self.assertEqual(r["net_total_translated_script_growth_bytes"],-1)
  self.assertEqual(r["positive_per_block_net_growth_bytes"],14)
  self.assertEqual(r["negative_per_block_net_growth_bytes"],-15)
  self.assertEqual(r["blocks_exceeding_original_local_padding"],1)
  self.assertEqual(r["minimum_extra_bytes_needed_across_overflow_blocks"],4)
  self.assertEqual(r["largest_single_block_overflow_bytes"],4)
  self.assertFalse(r["source_script_fixed_block_starts_full_english_to_spanish_feasible"])
 def test_exact_capacity_is_admissible_necessary_not_sufficient(self):
  r=block_costs(blocks_fixture(),{("sample_0",1):5})
  self.assertEqual(r["blocks_exceeding_original_local_padding"],0)
  self.assertTrue(r["source_script_fixed_block_starts_full_english_to_spanish_feasible"])
  self.assertFalse(r["runtime_mips_event_reference_model_verified"])
 def test_reject_missing_script_id_in_index(self):
  with self.assertRaises(ValueError):
   block_costs(blocks_fixture(),{("unknown",999):3})
 def test_reject_duplicate_table_key(self):
  b=blocks_fixture()
  b[1]["script_id"]=1;b[1]["name"]="sample_0"
  with self.assertRaises(ValueError):
   block_costs(b,{})
 def test_reject_shrinking_script_table(self):
  with self.assertRaises(ValueError):
   block_costs(blocks_fixture()[:-1],{})
 def test_reject_invalid_negative_padding(self):
  b=blocks_fixture();b[0]["padding"]=-1
  with self.assertRaises(ValueError):
   block_costs(b,{})
 def test_reject_invalid_overlarge_padding(self):
  b=blocks_fixture();b[0]["padding"]=33
  with self.assertRaises(ValueError):
   block_costs(b,{})
 def test_reject_boolean_padding(self):
  b=blocks_fixture();b[0]["padding"]=False
  with self.assertRaises(ValueError):
   block_costs(b,{})
 def test_reject_incomplete_original_script_structure(self):
  with self.assertRaises(Exception):
   authentic_block_metadata(b"",b"")
 def test_no_unspecified_dialogues_in_corpus(self):
  rows=read_canonical(SOURCE)
  script=[r for r in rows if r["origen"]=="SCRIPT.SDT/SCRIPT.DAT"]
  self.assertEqual(len(script),TRACKED)
  self.assertTrue(all(r["espanol"] and r["bytes_hex"] for r in script))

if __name__=="__main__":unittest.main()
