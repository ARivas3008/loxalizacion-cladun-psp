"""Pruebas B sinteticas: no hay PPSSPP ni relocacion en estos casos."""
import struct
import unittest
from dataclasses import dataclass
from tools.f4_r11_desfase_ids import infer_static_deltas

@dataclass
class Cmd:
    block:int
    order:int
    offset:int
    code:int
    instruction_id:int
    raw:bytes
    content:bytes|None=None

def cmd(op,value,block=0,order=0,offset=0,n=None,content=None):
    if n is None:n=5 if op==0x0b else 4
    payload=struct.pack('<I',value)+b'\x64'*(n-4)
    return Cmd(block,order,offset,op,818,
      bytes([op])+struct.pack('<HH',818,n)+payload,content)

class DeltaTests(unittest.TestCase):
    def setUp(self):
        self.ids=[100000,100100,200000,300000]
        self.names=['demo1001_00.dsf','demo1001_00.dsf','scr01.dsf','town.dsf']
        self.starts=[0,32,64,96,128]
    def scan(self,commands,**kw):
        return infer_static_deltas(commands,self.ids,self.names,self.starts,**kw)
    def test_plus100_outperforms_literal(self):
        r=self.scan([cmd(0x0a,100100),cmd(0x0a,200100,offset=9)])['opcode_profiles']['0x0a']
        self.assertEqual((r['literal_matches'],r['minus_100_matches']),(1,2))
        self.assertEqual(r['best_deltas'][0]['delta'],100)
    def test_0a_exceptions_0_and_1(self):
        r=self.scan([cmd(0x0a,0),cmd(0x0a,1,offset=9)])['opcode_profiles']['0x0a']
        self.assertEqual(r['minus_100_exceptions'],{'0':1,'1':1})
    def test_0b_exception_3(self):
        self.assertEqual(self.scan([cmd(0x0b,3)])['opcode_profiles']['0x0b']['minus_100_exceptions'],{'3':1})
    def test_0b_offset100(self):
        self.assertEqual(self.scan([cmd(0x0b,200100)])['opcode_profiles']['0x0b']['minus_100_matches'],1)
    def test_0c_literal_is_not_obligatorily_shifted(self):
        self.assertEqual(self.scan([cmd(0x0c,100000)])['opcode_profiles']['0x0c']['literal_matches'],1)
    def test_never_proves_semantics(self):
        r=self.scan([cmd(0x0a,100100)])
        self.assertFalse(r['mips_control_flow_proven'])
        self.assertFalse(r['relocalization_authorized'])
    def test_anchor_two_target_hypotheses(self):
        self.ids=list(range(1000,1021))
        self.ids[7]=100000
        self.ids[8]=100100
        self.names=['other.dsf']*21
        self.names[20]='scr01.dsf'
        self.starts=[32*i for i in range(22)]
        a=self.scan([cmd(0x0a,100100,block=20,order=20,offset=7420)])['source_anchor'][0]
        self.assertEqual((a['literal_target_block'],a['minus_100_target_block']),(8,7))
    def test_duplicate_ids_fail(self):
        self.ids[1]=self.ids[0]
        with self.assertRaises(ValueError):self.scan([])
    def test_inconsistent_table_fail(self):
        self.starts.pop()
        with self.assertRaises(ValueError):self.scan([])
    def test_bad_scan_fail(self):
        with self.assertRaises(ValueError):self.scan([],deltas=[0,0,100])
        with self.assertRaises(ValueError):self.scan([],deltas=[0])
    def test_bad_payload_fail(self):
        with self.assertRaises(ValueError):self.scan([cmd(0x0a,100100,n=5)])
    def test_duplicate_offsets_fail(self):
        with self.assertRaises(ValueError):self.scan([cmd(0x0a,100100),cmd(0x0b,3)])
    def test_ignores_text(self):
        self.assertEqual(self.scan([cmd(0x0a,100100,content=b'synthetic')])['opcode_profiles']['0x0a']['commands'],0)
    def test_empty_stays_unproven(self):
        r=self.scan([])
        self.assertEqual(r['opcode_profiles']['0x0a']['minus_100_matches'],0)
        self.assertFalse(r['relocalization_authorized'])
    def test_distinct_target_ids(self):
        r=self.scan([cmd(0x0a,100100),cmd(0x0a,100100,offset=9),cmd(0x0a,200100,offset=18)])
        self.assertEqual(r['opcode_profiles']['0x0a']['minus_100_distinct_script_ids'],2)
if __name__=='__main__':unittest.main()
