"""Pruebas B sintéticas del perfil de opcodes; jamás PPSSPP."""
import unittest
import struct
from dataclasses import dataclass
from tools.f4_r9_perfil_opcodes import profile

@dataclass
class C:
    block:int
    offset:int
    code:int
    instruction_id:int
    order:int
    raw:bytes
    content:bytes|None=None

def command(block,offset,code,payload=b'',order=0,content=None):
    return C(block,offset,code,818,order,bytes([code])+b'\x32\x03'+struct.pack('<H',len(payload))+payload,content)

class F4R9(unittest.TestCase):
    def setUp(self):
        self.starts=[0,64,128];self.ids=[100100,69];self.names=['demo1001_00.dsf','scr01.dsf']
    def scan(self,cs):return profile(cs,self.starts,self.ids,self.names)
    def test_0a_positive_not_semantics(self):
        x=self.scan([command(1,80,0x0a,struct.pack('<I',100100))]);self.assertEqual(x['opcode_0a_u32_script_id_matches'],1);self.assertFalse(x['MIPS_semantics_proven'])
    def test_negative_0a_nonexistent_id(self):
        self.assertEqual(self.scan([command(1,80,0x0a,struct.pack('<I',555))])['opcode_0a_u32_script_id_matches'],0)
    def test_external_anchor(self):
        x=self.scan([command(1,80,0x0a,struct.pack('<I',100100))]);self.assertEqual(x['opcode_0a_external_demo1001_candidates'][0]['target_block'],0)
    def test_0a_internal_not_external(self):
        x=self.scan([command(0,0,0x0a,struct.pack('<I',100100))]);self.assertEqual(len(x['opcode_0a_external_demo1001_candidates']),0)
    def test_relative_hit_dedup_motifs(self):
        cs=[command(0,0,0x01,struct.pack('<I',32)),command(0,16,0x01,struct.pack('<I',32),order=1),command(0,32,0x08,order=2)]
        x=self.scan(cs);self.assertEqual(x['intro_relative_numeric_matches_total'],2);self.assertEqual(len(x['intro_relative_numeric_motifs']),1)
    def test_text_ignored(self):
        x=self.scan([command(1,80,0x0a,struct.pack('<I',100100),content=b'fake')]);self.assertEqual(x['opcode_0a_total_commands'],0)
    def test_incompatible_0a_size(self):
        with self.assertRaises(ValueError):self.scan([command(1,80,0x0a,b'\0\0')])
    def test_incompatible_02_size(self):
        with self.assertRaises(ValueError):self.scan([command(0,0,0x02,b'\0'*16)])
    def test_duplicate_ids(self):
        self.ids[1]=self.ids[0]
        with self.assertRaises(ValueError):self.scan([])
    def test_bad_table(self):
        self.starts=[0,64]
        with self.assertRaises(ValueError):self.scan([])
    def test_duplicate_offsets(self):
        with self.assertRaises(ValueError):self.scan([command(0,0,0x08),command(0,0,0x08)])
    def test_zero_not_relative_hit(self):
        self.assertEqual(self.scan([command(0,0,0x01,b'\0'*4)])['intro_relative_numeric_matches_total'],0)
    def test_op02_23_is_not_proof(self):
        p=bytearray(18);struct.pack_into('<I',p,2,23)
        x=self.scan([command(0,0,0x02,bytes(p))]);self.assertFalse(x['relocation_authorized']);self.assertEqual(x['opcode_02_field_2_common_values'][0]['value'],23)
if __name__=='__main__':unittest.main()
