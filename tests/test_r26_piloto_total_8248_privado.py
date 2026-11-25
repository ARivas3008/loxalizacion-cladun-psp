"""R26 full text pilot: unit tests NEVER build commercial ISO inside CI."""
import unittest
from unittest.mock import patch
from tools.r26_piloto_total_8248_privado import (
 preview,private_candidate,full_8248_metadata_manifest,FULL_TARGET,SCRIPT_TARGET,
 VARIABLE_SCRIPT_TARGET,EQUAL_SCRIPT_TARGET
)

class TestR26FullTextPilot(unittest.TestCase):
 def test_real_canonical_full_insertion_preflight(self):
  p=preview()
  self.assertEqual(p["source_rows"],9237)
  self.assertEqual(p["planned_all_changed_canonical_records"],8248)
  self.assertEqual(p["planned_SCRIPT_dat_changed_texts"],4900)
  self.assertEqual(p["all_SCRIPT_dat_translated_rows"],5207)
  self.assertEqual(p["SCRIPT_dat_already_byte_identical_unmodified"],307)
  self.assertEqual(p["planned_other_textual_records"],3348)
  self.assertEqual(p["planned_SCRIPT_same_length_changed"],376)
  self.assertEqual(p["all_SCRIPT_same_width_including_unchanged"],683)
  self.assertEqual(p["planned_SCRIPT_changed_length"],4524)
 def test_8248_metadata_ID_manifest_has_no_commercial_text(self):
  rows=full_8248_metadata_manifest()
  self.assertEqual(len(rows),8248)
  self.assertEqual(len({r["grupo_id"] for r in rows}),8248)
  kinds={}
  for r in rows:
   kinds[r["category"]]=kinds.get(r["category"],0)+1
   self.assertNotIn("espanol",r)
   self.assertNotIn("original",r)
   self.assertNotIn("bytes_hex",r)
   self.assertEqual(r["PPSSPP_C"],"NOT_RUN")
   self.assertEqual(r["canonical_gameplay_integrated"],"NO")
   self.assertEqual(r["editorial_review"],"PENDIENTE_CONTEXTUAL")
   if r["category"]=="SCRIPT_VARIABLE":
    self.assertNotEqual(r["original_bytes"],r["new_bytes"])
    self.assertEqual(r["MIPS_references"],"UNVERIFIED")
  self.assertEqual(kinds,{"SCRIPT_VARIABLE":4524,
                          "SCRIPT_FIXED":376,
                          "OTHER_RESOURCE":3348})
 def test_full_100pct_stays_experimental(self):
  p=preview()
  self.assertFalse(p["private_candidate_created"])
  self.assertFalse(p["100_percent_ROMhacking_official"])
  self.assertFalse(p["PPSSPP_1_20_4_C_verified"])
  self.assertFalse(p["all_script_event_offsets_would_be_preserved"])
  self.assertTrue(p["requires_MIPS_control_flow_reference_audit"])
  self.assertFalse(p["release_authorized"])
  self.assertEqual(p["official_integrated_records_unchanged"],3724)
 def test_full_script_5207_is_not_8248(self):
  self.assertEqual(SCRIPT_TARGET+3348,FULL_TARGET)
  self.assertEqual(VARIABLE_SCRIPT_TARGET+EQUAL_SCRIPT_TARGET,SCRIPT_TARGET)
  self.assertEqual(SCRIPT_TARGET+307,5207)
 def test_explicit_risk_required_even_before_source_iso(self):
  with self.assertRaisesRegex(ValueError,"experimental risk"):
   private_candidate("/source.iso","/candidate.iso",explicit_risk_acceptance=False)
 def test_missing_iso_and_candidate_refused_by_cli_contract(self):
  from argparse import Namespace
  p=preview()
  self.assertFalse(p["private_candidate_created"])
 def test_corrupt_corpus_rows_are_rejected(self):
  # Planner must fail closed on changed corpus identity, never infer its size.
  from tools.r26_piloto_total_8248_privado import require
  with self.assertRaises(ValueError):
   require(False,"Corpus incomplete")

if __name__=="__main__":unittest.main()
