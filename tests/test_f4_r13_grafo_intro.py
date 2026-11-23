"""Synthetic B tests of static graph, not authentic PPSSPP."""
import struct
import unittest
from dataclasses import dataclass
from tools.f4_r13_grafo_intro import analyze_static_links

@dataclass
class Cmd:
    block:int
    order:int
    offset:int
    code:int
    instruction_id:int
    raw:bytes
    content:bytes|None=None

def cmd(op,value,block=0,order=0,offset=0,tail=100,content=None):
    p=struct.pack('<I',value)+(bytes([tail]) if op==0x0b else b'')
    return Cmd(block,order,offset,op,8,bytes([op])+struct.pack('<HH',8,len(p))+p,content)

class GraphTests(unittest.TestCase):
    def setUp(self):
        self.ids=[100000,100100,100190,100101,100191]
        self.names=['intro_a','intro_a','intro_a','intro_b','intro_b']
        self.starts=[0,50,100,150,200,250]
    def scan(self,cmds):return analyze_static_links(cmds,self.ids,self.names,self.starts)
    def test_shifted_0a_link(self):
        self.assertEqual(self.scan([cmd(10,100200)])['opcode_counts']['0x0A']['minus100_id_matches'],1)
    def test_literal_misleading(self):
        x=self.scan([cmd(10,100100)])
        self.assertEqual(x['selected_intro_edges'],[])
        self.assertEqual(x['opcode_counts']['0x0A']['minus100_id_matches'],1)
    def test_0b_same_script(self):
        self.assertEqual(self.scan([cmd(11,100200)])['opcode_counts']['0x0B']['same_script_name_matches'],1)
    def test_0c_same_script(self):
        self.assertEqual(self.scan([cmd(12,100290)])['opcode_counts']['0x0C']['same_script_name_matches'],1)
    def test_0c_unmatched_value_100(self):
        self.assertEqual(self.scan([cmd(12,100)])['opcode_counts']['0x0C']['nonmatching_operands'],{'100':1})
    def test_0b_unmatched_three(self):
        self.assertEqual(self.scan([cmd(11,3)])['opcode_counts']['0x0B']['nonmatching_operands'],{'3':1})
    def test_no_semantic_proof(self):
        x=self.scan([cmd(10,100200)])
        self.assertFalse(x['runtime_MIPS_execution_proven'])
        self.assertFalse(x['event_relocation_permitted'])
    def test_source_and_target_cardinality(self):
        x=self.scan([cmd(10,100200),cmd(10,100290,offset=9)])['opcode_counts']['0x0A']
        self.assertEqual((x['distinct_source_blocks_mapped'],x['distinct_target_blocks_mapped']),(1,2))
    def test_duplicate_offsets_fail(self):
        with self.assertRaises(ValueError):self.scan([cmd(10,100200),cmd(10,100200)])
    def test_outside_block_fail(self):
        with self.assertRaises(ValueError):self.scan([cmd(10,100200,offset=51)])
    def test_invalid_length_fail(self):
        c=cmd(11,3);c.raw=c.raw[:-1]
        with self.assertRaises(ValueError):self.scan([c])
    def test_duplicate_script_ids_fail(self):
        self.ids[1]=self.ids[0]
        with self.assertRaises(ValueError):self.scan([])
    def test_empty_source_fail(self):
        self.ids=[];self.names=[];self.starts=[0]
        with self.assertRaises(ValueError):self.scan([])
    def test_text_ignored(self):
        self.assertEqual(self.scan([cmd(10,100200,content=b'synthetic')])['opcode_counts']['0x0A']['total'],0)
    def test_source_in_selected_intro_empty_small_synthetic(self):
        self.assertEqual(self.scan([cmd(10,100200)])['selected_intro_edges'],[])
    def test_same_block_numeric_count_no_semantics(self):
        self.assertEqual(self.scan([cmd(10,100100)])['opcode_counts']['0x0A']['same_block_matches'],1)
    def test_intro_chain_with_765_synthetic_blocks(self):
        self.ids=list(range(1000,1765))
        self.ids[757]=100000;self.ids[758]=100100;self.ids[759]=100190
        self.ids[760]=100101;self.ids[761]=100191
        self.names=['other.dsf']*765
        for i in (757,758,759):self.names[i]='demo1001_00.dsf'
        for i in (760,761):self.names[i]='demo1001_01.dsf'
        self.starts=[32*i for i in range(766)]
        cs=[cmd(10,100200,block=757,order=2,offset=self.starts[757]+9),
            cmd(12,100290,block=758,order=1,offset=self.starts[758]+9),
            cmd(10,100201,block=758,order=416,offset=self.starts[758]+18),
            cmd(12,100291,block=760,order=1,offset=self.starts[760]+9)]
        edges={(e['source_block'],e['minus100_target_block']) for e in self.scan(cs)['selected_intro_edges']}
        self.assertEqual(edges,{(757,758),(758,759),(758,760),(760,761)})
    def test_starts_not_monotonic_fail(self):
        self.starts[2]=0
        with self.assertRaises(ValueError):self.scan([])
if __name__=='__main__':unittest.main()
