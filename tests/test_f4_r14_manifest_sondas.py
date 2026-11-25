"""Synthetic B tests for R14 observation manifest (NOT PPSSPP evidence)."""
import struct
import unittest
from dataclasses import dataclass
from tools.f4_r14_manifest_sondas import build_manifest,PROBES

@dataclass
class Cmd:
    block:int
    order:int
    offset:int
    code:int
    instruction_id:int
    raw:bytes
    content:bytes|None=None

def cmd(b,o,op,val,offset,content=None):
    payload=struct.pack('<I',val)
    return Cmd(b,o,offset,op,818,bytes([op])+struct.pack('<HH',818,len(payload))+payload,content)

class TestR14(unittest.TestCase):
    def setUp(self):
        self.ids=list(range(2000,2800))
        self.ids[757]=100000;self.ids[758]=100100;self.ids[759]=100190
        self.ids[760]=100101;self.ids[761]=100191
        self.names=['other.dsf']*800
        for b in (757,758,759):self.names[b]='demo1001_00.dsf'
        for b in (760,761):self.names[b]='demo1001_01.dsf'
        self.starts=[i*100 for i in range(801)]
        self.cmds=[cmd(b,o,op,val,100*b+(i+1)*9) for i,(b,o,op,val,dest) in enumerate(PROBES)]
        # Keep every command inside its block; probe count may exceed per-block capacity in a fixture.
        n={}
        for c in self.cmds:
            n[c.block]=n.get(c.block,0)+1
            c.offset=100*c.block+n[c.block]*9
    def run_check(self):return build_manifest(self.cmds,self.ids,self.names,self.starts)
    def test_nine_exact_probes(self):self.assertEqual(self.run_check()['probe_count'],9)
    def test_no_mips_proof(self):
        x=self.run_check();self.assertFalse(x['mips_execution_verified']);self.assertFalse(x['patching_allowed'])
    def test_offsets_not_ram(self):
        x=self.run_check();self.assertTrue(all(p['ram_address'] is None for p in x['probes']))
    def test_covers_sentinels_as_unknown(self):
        x=self.run_check();self.assertEqual(sum(p['candidate_target_block'] is None for p in x['probes']),4)
    def test_mismatched_payload(self):
        self.cmds[0].raw=self.cmds[0].raw[:-1]
        with self.assertRaises(ValueError):self.run_check()
    def test_wrong_operand(self):
        self.cmds[0].raw=cmd(20,20,10,123,100*20+9).raw
        with self.assertRaises(ValueError):self.run_check()
    def test_wrong_opcode(self):
        self.cmds[0].code=0x0B
        with self.assertRaises(ValueError):self.run_check()
    def test_deleted_probe(self):
        self.cmds.pop()
        with self.assertRaises(ValueError):self.run_check()
    def test_duplicate_probe(self):
        with self.assertRaises(ValueError):build_manifest(self.cmds,self.ids,self.names,self.starts,PROBES+PROBES[:1])
    def test_duplicate_command(self):
        self.cmds.append(self.cmds[0])
        with self.assertRaises(ValueError):self.run_check()
    def test_invalid_block(self):
        self.cmds[0].block=900
        with self.assertRaises(ValueError):self.run_check()
    def test_duplicate_ids(self):
        self.ids[0]=self.ids[1]
        with self.assertRaises(ValueError):self.run_check()
    def test_wrong_starts(self):
        self.starts=self.starts[:-1]
        with self.assertRaises(ValueError):self.run_check()
    def test_textual_command_fail(self):
        self.cmds[0].content=b'synthetic'
        with self.assertRaises(ValueError):self.run_check()
    def test_source_names_preserved(self):
        x=self.run_check();self.assertEqual(x['probes'][2]['script_name'],'demo1001_00.dsf')
    def test_literal_vs_shifted_target(self):
        x=self.run_check();self.assertEqual(x['probes'][0]['candidate_target_block'],757)
        self.assertEqual(x['probes'][0]['literal_target_block'],758)
if __name__=='__main__':unittest.main()
