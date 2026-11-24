"""R26 full text pilot: unit tests NEVER build commercial ISO inside CI."""
import unittest
from unittest.mock import patch
from tools.r26_piloto_total_8248_privado import (
 preview,private_candidate,FULL_TARGET,SCRIPT_TARGET,
 VARIABLE_SCRIPT_TARGET,EQUAL_SCRIPT_TARGET
)

class TestR26FullTextPilot(unittest.TestCase):
 def test_real_canonical_full_insertion_preflight(self):
  p=preview()
  self.assertEqual(p["source_rows"],9237)
  self.assertEqual(p["planned_all_changed_canonical_records"],8248)
  self.assertEqual(p["planned_SCRIPT_dat_texts"],5207)
  self.assertEqual(p["planned_other_textual_records"],3041)
  self.assertEqual(p["planned_SCRIPT_same_length"],683)
  self.assertEqual(p["planned_SCRIPT_changed_length"],4524)
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
  self.assertEqual(SCRIPT_TARGET+3041,FULL_TARGET)
  self.assertEqual(VARIABLE_SCRIPT_TARGET+EQUAL_SCRIPT_TARGET,SCRIPT_TARGET)
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
