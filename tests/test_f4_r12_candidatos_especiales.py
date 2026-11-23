"""F4 R12 tests de clasificación sintética (B); no son ejecución PPSSPP (C)."""
import struct
import unittest
from dataclasses import dataclass
from tools.f4_r12_candidatos_especiales import categorize

@dataclass
class Cmd:
    block:int
    order:int
    offset:int
    code:int
    instruction_id:int
    raw:bytes
    content:bytes|None=None

def make(op, value, block=0, order=0, offset=0, content=None, tail=100):
    p=struct.pack('<I',value)+(bytes([tail]) if op==0x0B else b'')
    return Cmd(block,order,offset,op,818,bytes([op])+struct.pack('<HH',818,len(p))+p,content)

class R12Tests(unittest.TestCase):
    def setUp(self):
        self.ids=[100000,100100,300,1]
        self.names=['demo1001_00.dsf','demo1001_00.dsf','ma.dsf','scr01.dsf']
    def c(self,commands):return categorize(commands,self.ids,self.names)
    def test_0a_shifted_id(self):
        r=self.c([make(0x0A,100100)])['opcode_profiles']['0x0A'];self.assertEqual(r['matches_id_after_minus100'],1)
    def test_0a_small_values_do_not_resolve(self):
        r=self.c([make(0x0A,0),make(0x0A,1,offset=9)])['opcode_profiles']['0x0A'];self.assertEqual(r['nonmatches_by_operand'],{'0':1,'1':1})
    def test_0b_value3_is_unmatched(self):
        r=self.c([make(0x0B,3)])['opcode_profiles']['0x0B'];self.assertEqual(r['nonmatches_by_operand'],{'3':1})
    def test_0c_value100_is_unmatched_when_id0_absent(self):
        r=self.c([make(0x0C,100)])['opcode_profiles']['0x0C'];self.assertEqual(r['nonmatches_by_operand'],{'100':1})
    def test_0c_positive_match(self):
        r=self.c([make(0x0C,400)])['opcode_profiles']['0x0C'];self.assertEqual(r['matches_id_after_minus100'],1)
    def test_0b_flag_cross(self):
        r=self.c([make(0x0B,3),make(0x0B,100100,offset=10,tail=101)])['opcode_profiles']['0x0B'];self.assertEqual(r['trailing_byte_by_match'],{'100:unmatched':1,'101:matches_id':1})
    def test_special_values_not_validated_as_semantics(self):
        r=self.c([make(0x0A,1)]);self.assertFalse(r['mips_semantics_proven']);self.assertFalse(r['relocalization_authorized'])
    def test_bad_length_rejected(self):
        c=make(0x0B,3);c.raw=c.raw[:-1]
        with self.assertRaises(ValueError):self.c([c])
    def test_bad_header_rejected(self):
        c=make(0x0A,100100);c.raw=c.raw[:3]+b'\0\0'+c.raw[5:]
        with self.assertRaises(ValueError):self.c([c])
    def test_duplicate_offsets_rejected(self):
        with self.assertRaises(ValueError):self.c([make(0x0A,1),make(0x0B,3)])
    def test_bad_block_rejected(self):
        with self.assertRaises(ValueError):self.c([make(0x0C,100,block=4)])
    def test_duplicate_ids_rejected(self):
        self.ids[1]=self.ids[0]
        with self.assertRaises(ValueError):self.c([])
    def test_wrong_names_length_rejected(self):
        self.names.pop()
        with self.assertRaises(ValueError):self.c([])
    def test_text_skipped(self):
        self.assertEqual(self.c([make(0x0A,100100,content=b'synthetic')])['opcode_profiles']['0x0A']['commands'],0)
    def test_correct_anchor(self):
        c=make(0x0A,100100,block=3,order=20,offset=7420)
        self.assertEqual(self.c([c])['anchor'],[])
    def test_fake_unknown_not_silently_allowed(self):
        r=self.c([make(0x0C,789)])['opcode_profiles']['0x0C'];self.assertEqual(r['unclassified_values_count'],1)
    def test_distinct_targets(self):
        r=self.c([make(0x0A,100100),make(0x0A,400,offset=9)])['opcode_profiles']['0x0A'];self.assertEqual(r['distinct_matched_ids'],2)
if __name__=='__main__':unittest.main()
