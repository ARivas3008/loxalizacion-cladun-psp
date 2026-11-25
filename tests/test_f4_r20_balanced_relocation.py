"""Balanced-size edits can still relocate interior event commands."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from script_event_guard import audit_script_rebuild
from integrar_parche_seguro import text_command_rebuild
from test_script_event_guard import fixture

def two_text_fixture():
 data,table=fixture()
 # Replace the nine-byte nontext command with a one-character text command.
 modified=bytearray(data)
 modified[13:22]=b'\x66\x02\x00\x04\x00\x01\x00X\x00'
 return bytes(modified),table

class BalancedRelocationTests(unittest.TestCase):
 def setUp(self):
  self.original,self.table=two_text_fixture()
  self.expected={7:(b'Hello',b'Hello!','000001'),20:(b'X',b'','000002')}
 def test_balanced_lengths_preserve_total_size_but_move_internal_command(self):
  result,new_table=text_command_rebuild(self.original,self.table,self.expected)
  self.assertEqual(len(result),len(self.original))
  self.assertEqual(new_table,self.table)
  info=audit_script_rebuild(self.original,self.table,result,new_table,self.expected)
  self.assertEqual(info['moved_script_starts'],0)
  self.assertEqual(info['moved_command_offsets'],1)
  self.assertFalse(info['all_command_offsets_preserved'])
 def test_balanced_lengths_still_rejected_event_safe_only(self):
  result,new_table=text_command_rebuild(self.original,self.table,self.expected)
  with self.assertRaisesRegex(ValueError,'Bloqueo de seguridad'):
   audit_script_rebuild(self.original,self.table,result,new_table,self.expected,require_fixed_offsets=True)
 def test_unapproved_second_text_rejected(self):
  result,new_table=text_command_rebuild(self.original,self.table,self.expected)
  with self.assertRaises(ValueError):
   audit_script_rebuild(self.original,self.table,result,new_table,{7:self.expected[7]},require_fixed_offsets=True)
 def test_wrong_preimage_rejected_before_rebuild(self):
  wrong=dict(self.expected)
  wrong[20]=(b'Y',b'','000002')
  with self.assertRaisesRegex(ValueError,'Original string mismatch'):
   text_command_rebuild(self.original,self.table,wrong)

if __name__=='__main__':unittest.main()
