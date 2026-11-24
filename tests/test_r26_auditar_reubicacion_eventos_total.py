"""No real game ISO in CI: tests source planner and reject faked MIPS proof."""
import unittest
from tools.r26_auditar_reubicacion_eventos_total import (
 canonical_plan,audit,analyze_moving_offsets
)

class TestR26AllEventMoveAudit(unittest.TestCase):
 def test_all_changed_script_ids_and_lengths(self):
  plan,stats=canonical_plan()
  self.assertEqual(len(plan),4900)
  self.assertEqual(stats["all_canonical_candidate_changes"],8248)
  self.assertEqual(stats["SCRIPT_changed_length_texts"],4524)
  self.assertEqual(stats["SCRIPT_changed_bytes_same_length_texts"],376)
  self.assertEqual(stats["original_unchanged_SCRIPT_texts"],307)
  self.assertEqual(len({x[2] for x in plan.values()}),4900)
  self.assertTrue(stats["not_runtime_proven"])
 def test_preview_never_constructs_or_approves_ISO(self):
  info=audit()
  self.assertFalse(info["candidate_ISO_written"])
  self.assertFalse(info["A_authenticated_original"])
  self.assertFalse(info["gameplay_C_pass"])
  self.assertEqual(info["official_new_integrations"],0)
  self.assertFalse(info["commercial_text_or_bytes_exported"])
 def test_fake_incomplete_command_stream_rejected(self):
  with self.assertRaises(Exception):
   analyze_moving_offsets(b"\0"*16,b"\0"*64,b"\0"*16,b"\0"*64,{})
 def test_invalid_original_iso_rejected(self):
  from pathlib import Path
  with self.assertRaises(Exception):
   audit(Path("/no-such-private-iso.iso"))

if __name__=="__main__":unittest.main()
