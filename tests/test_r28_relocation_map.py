import struct
import unittest
from types import SimpleNamespace
from tools.r28_relocation_map import relocation_map, identity_collisions, reference_triage

def cmd(block=0,order=0,offset=0,code=1,i=8,raw=b"abcde",content=None):
    return SimpleNamespace(block=block,order=order,offset=offset,code=code,
        instruction_id=i,raw=raw,content=content)

class RelocationMapTests(unittest.TestCase):
    def test_bijective(self):
        a=[cmd(),cmd(order=1,offset=5)]
        b=[cmd(),cmd(order=1,offset=7)]
        result=relocation_map(a,b)
        self.assertEqual(result[1]["new_offset"],7)
        self.assertFalse(result[0]["text"])
    def test_duplicate_instruction_not_identity(self):
        a=[cmd(),cmd(order=1,offset=5)]
        self.assertEqual(identity_collisions(a)["duplicate_instruction_ids_within_block_excess"],1)
        self.assertEqual(identity_collisions(a)["duplicate_block_opcode_instruction_id_excess"],1)
        self.assertEqual(len(relocation_map(a,a)),2)
    def test_duplicate_coordinates(self):
        a=[cmd(),cmd(order=1,offset=5)]
        with self.assertRaises(ValueError):
            relocation_map(a,[cmd(),cmd(order=1)])
    def test_duplicate_key(self):
        a=[cmd(),cmd(offset=5)]
        with self.assertRaises(ValueError):
            relocation_map(a,a)
    def test_mutation(self):
        with self.assertRaises(ValueError):
            relocation_map([cmd()],[cmd(raw=b"abcdf")])
    def test_wrong_order(self):
        with self.assertRaises(ValueError):
            relocation_map([cmd()],[cmd(order=1)])
    def test_count(self):
        with self.assertRaises(ValueError):
            relocation_map([cmd()],[])
    def test_classification(self):
        with self.assertRaises(ValueError):
            relocation_map([cmd()],[cmd(content=b"x")])
    def test_numeric_only(self):
        raw=b"abcde"+struct.pack("<I",9)
        a=[cmd(raw=raw),cmd(order=1,offset=9)]
        b=[cmd(raw=raw),cmd(order=1,offset=11)]
        r=reference_triage(a,relocation_map(a,b),[0,16],[0,16],[1])
        self.assertEqual(r["u32_absolute_matches_target_moves"],1)
        self.assertEqual(r["u32_relative_matches_target_moves"],1)
        self.assertFalse(r["semantic_references_proven"])
    def test_ambiguous_script_ids(self):
        with self.assertRaises(ValueError):
            reference_triage([],[],[0,16,32],[0,16,32],[1,1])
