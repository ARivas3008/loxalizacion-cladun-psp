"""R19 fail-closed regression cases for event-safe SCRIPT rebuilding (synthetic)."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from script_event_guard import audit_script_rebuild,read_commands
from test_script_event_guard import fixture

class EventNegativeR19(unittest.TestCase):
    def setUp(self):
        self.source,self.table=fixture()

    def rejected(self,position,new_value,expected=None):
        changed=bytearray(self.source)
        changed[position]=new_value
        with self.assertRaises(ValueError):
            audit_script_rebuild(self.source,self.table,bytes(changed),self.table,
                                 {} if expected is None else expected,require_fixed_offsets=True)

    def test_mutated_opcode(self):
        self.rejected(0,0x01)

    def test_mutated_instruction_id(self):
        self.rejected(1,0x02)

    def test_mutated_command_length(self):
        self.rejected(3,0xff)

    def test_mutated_text_length(self):
        self.rejected(5,0xff)

    def test_mutated_text_terminator(self):
        self.rejected(12,0x01)

    def test_mutated_nontext_argument(self):
        self.rejected(18,0x55)

    def test_mutated_table_offset(self):
        changed=bytearray(self.table)
        changed[16+32+4]=1
        with self.assertRaises(ValueError):
            audit_script_rebuild(self.source,self.table,self.source,bytes(changed),{},require_fixed_offsets=True)

    def test_mutated_table_name(self):
        changed=bytearray(self.table)
        changed[16+8]=ord('X')
        with self.assertRaises(ValueError):
            audit_script_rebuild(self.source,self.table,self.source,bytes(changed),{},require_fixed_offsets=True)

    def test_wrong_preimage_even_when_new_text_matches(self):
        changed=bytearray(self.source)
        changed[7:12]=b'Adios'
        with self.assertRaises(ValueError):
            audit_script_rebuild(self.source,self.table,bytes(changed),self.table,
                                 {7:(b'Wrong',b'Adios','000001')},require_fixed_offsets=True)

    def test_approved_fixed_width_only(self):
        changed=bytearray(self.source)
        changed[7:12]=b'Adios'
        info=audit_script_rebuild(self.source,self.table,bytes(changed),self.table,
                                 {7:(b'Hello',b'Adios','000001')},require_fixed_offsets=True)
        self.assertEqual(info['text_commands_replaced'],1)
        self.assertEqual(info['moved_command_offsets'],0)
        self.assertEqual(info['nontext_commands_byte_exact'],1)
        self.assertFalse(info['event_logic_runtime_certified'])

if __name__=='__main__':unittest.main()
