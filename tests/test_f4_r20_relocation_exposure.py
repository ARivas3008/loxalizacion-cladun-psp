"""Synthetic relocation-exposure regression; no commercial bytes."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from f4_r20_relocation_exposure import exposure
from test_script_event_guard import fixture

class RelocationExposureTests(unittest.TestCase):
 def setUp(self):
  self.data,self.table=fixture()
 def test_text_precedes_nontext(self):
  result=exposure(self.data,self.table)
  self.assertEqual(result['text_commands'],1)
  self.assertEqual(result['minimum_following_commands'],1)
  self.assertEqual(result['sum_following_nontext_commands_per_one_text_edit'],1)
  self.assertEqual(result['text_without_following_nontext'],0)
 def test_never_authorizes_relocation(self):
  result=exposure(self.data,self.table)
  self.assertFalse(result['variable_length_insertion_authorized'])
  self.assertFalse(result['control_flow_reference_model_verified'])
  self.assertFalse(result['ppsspp_runtime_verified'])
 def test_bad_script_table_rejected(self):
  with self.assertRaises(ValueError):
   exposure(self.data,self.table[:32])
 def test_bad_command_length_rejected(self):
  broken=bytearray(self.data);broken[3]=255
  with self.assertRaises(ValueError):
   exposure(bytes(broken),self.table)
 def test_text_only_block_exposes_no_following_nontext(self):
  # One text command in first block, all later blocks empty.
  source=bytearray(self.data)
  source[13:22]=b'\0'*9
  result=exposure(bytes(source),self.table)
  self.assertEqual(result['text_without_following_nontext'],1)
  self.assertEqual(result['text_last_command'],1)

if __name__=='__main__':unittest.main()
