"""F4 R10: tests B sintéticos; no son test de PPSSPP."""
import struct
import unittest
from dataclasses import dataclass
from tools.f4_r10_cruce_script_ai import profile_opcode_namespaces,parse_script_table_ids

@dataclass
class Command:
    block:int
    order:int
    offset:int
    code:int
    instruction_id:int
    raw:bytes
    content:bytes|None=None

def command(op,arg,pad=b'',block=1,order=20,offset=7420,instruction_id=818,content=None):
    payload=struct.pack('<I',arg)+pad
    return Command(block,order,offset,op,instruction_id,bytes([op])+struct.pack('<H',instruction_id)+struct.pack('<H',len(payload))+payload,content)

class CrossTablesTests(unittest.TestCase):
    def setUp(self):
        self.s=[1,100100,610000]
        self.a=[610000,990100]
        self.names=['abc.dsf','scr01.dsf','demo1001_00.dsf']
    def scan(self,cmds):return profile_opcode_namespaces(cmds,self.s,self.a,self.names)
    def test_0a_script_match(self):
        x=self.scan([command(0x0a,100100)])
        self.assertEqual(x['opcodes']['0x0a']['matches_SCRIPT_TBL'],1)
        self.assertEqual(x['opcodes']['0x0a']['matches_AISCRIPT_TBL'],0)
    def test_source_100100_candidate(self):
        self.s=list(range(1000,1021));self.s[3]=100100
        self.names=['other.dsf']*21;self.names[20]='scr01.dsf'
        x=self.scan([command(0x0a,100100,block=20)])
        self.assertEqual(len(x['source_100100_candidates']),1)
        self.assertEqual(x['source_100100_candidates'][0]['source_script_name'],'scr01.dsf')
    def test_0b_fifth_byte(self):
        x=self.scan([command(0x0b,610000,b'\x65')])
        self.assertEqual(x['opcode_0b_trailing_byte_counts'],{'101':1})
    def test_0b_wrong_payload(self):
        with self.assertRaises(ValueError):self.scan([command(0x0b,610000)])
    def test_0c_script(self):
        self.assertEqual(self.scan([command(0x0c,100100)])['opcodes']['0x0c']['matches_SCRIPT_TBL'],1)
    def test_ai_only(self):
        self.assertEqual(self.scan([command(0x0a,990100)])['opcodes']['0x0a']['matches_AISCRIPT_TBL'],1)
    def test_ai_script_overlap(self):
        self.assertEqual(self.scan([command(0x0a,610000)])['opcodes']['0x0a']['matches_both_tables'],1)
    def test_neither(self):
        self.assertEqual(self.scan([command(0x0a,42)])['opcodes']['0x0a']['matches_neither_table'],1)
    def test_text_skipped(self):
        self.assertEqual(self.scan([command(0x0a,100100,content=b'foo')])['opcodes']['0x0a']['commands'],0)
    def test_duplicate_script_id(self):
        self.s=[1,1,610000]
        with self.assertRaises(ValueError):self.scan([])
    def test_duplicate_ai_id(self):
        self.a=[1,1]
        with self.assertRaises(ValueError):self.scan([])
    def test_short_table(self):
        with self.assertRaises(ValueError):parse_script_table_ids(b'\0'*48,2,128)
    def test_out_of_order(self):
        b=bytearray(16+3*32);struct.pack_into('<I',b,0,3)
        for i,(sid,off) in enumerate([(1,0),(2,32),(3,16)]):
            struct.pack_into('<II',b,16+32*i,sid,off)
        with self.assertRaises(ValueError):parse_script_table_ids(bytes(b),3,128)
    def test_valid_table(self):
        b=bytearray(16+2*32);struct.pack_into('<I',b,0,2)
        for i,(sid,off) in enumerate([(1,0),(2,16)]):
            struct.pack_into('<II',b,16+32*i,sid,off)
        self.assertEqual(parse_script_table_ids(bytes(b),2,128),[1,2])
    def test_never_authorize_relocation(self):
        x=self.scan([command(0x0a,100100)])
        self.assertFalse(x['mips_semantics_proven'])
        self.assertFalse(x['relocalization_authorized'])
if __name__=='__main__':unittest.main()
