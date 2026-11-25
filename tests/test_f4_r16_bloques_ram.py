import random
import unittest
from dataclasses import dataclass
from tools.f4_r16_bloques_ram import recipes,metadata,scan,unique
@dataclass
class Cmd:
    block:int
    offset:int
    raw:bytes
class TestBlocks(unittest.TestCase):
    def setUp(self):
        rng=random.Random(16);self.a=rng.randbytes(34);self.b=rng.randbytes(90)
        self.data=self.a+b'\0'*14+self.b+b'\0'*6
        self.starts=[0,48,144];self.cmds=[Cmd(0,0,self.a),Cmd(1,48,self.b)]
        self.items=recipes(self.data,self.cmds,self.starts,(0,1));self.start=0x08800000
    def search(self,ram):
        return scan(lambda a,n:ram[a-self.start:a-self.start+n],self.start,self.start+len(ram),self.items,4096)
    def test_metadata_excludes_raw(self):
        self.assertEqual([m['command_bytes'] for m in metadata(self.items)],[34,90]);self.assertNotIn('raw',str(metadata(self.items)))
    def test_independent_blocks_reverse_order(self):
        ram=b'Z'*500+self.b+b'Z'*800+self.a+b'Z'*5000
        self.assertEqual([(r['block'],r['candidate_base']-self.start) for r in self.search(ram)],[(0,1390),(1,500)])
    def test_boundary_overlap(self):
        ram=b'Z'*4090+self.a+b'Z'*5000
        self.assertEqual(self.search(ram)[0]['candidate_base'],self.start+4090)
    def test_decoy_anchors_wrong_middle(self):
        decoy=self.b[:16]+b'X'*58+self.b[-16:]
        self.assertEqual(self.search(b'Z'*500+decoy+b'Z'*5000),[])
    def test_single_anchor_not_enough(self):self.assertEqual(self.search(b'Z'*500+self.a[:16]+b'Z'*5000),[])
    def test_two_copies_ambiguity_visible(self):self.assertEqual(len(self.search(self.a+b'Z'*40+self.a+b'Z'*5000)),2)
    def test_no_execution_claim(self):self.assertFalse(self.search(self.a+b'Z'*5000)[0]['mips_execution_proven'])
    def test_short_read_rejected(self):
        with self.assertRaises(ValueError):scan(lambda a,n:b'',self.start,self.start+5000,self.items)
    def test_bad_bounds(self):
        with self.assertRaises(ValueError):recipes(self.data,self.cmds,[0,48,145],(0,1))
    def test_padding_changed(self):
        data=self.a+b'X'*14+self.b+b'\0'*6
        with self.assertRaises(ValueError):recipes(data,self.cmds,self.starts,(0,1))
    def test_missing_commands(self):
        with self.assertRaises(ValueError):recipes(self.data,self.cmds[1:],self.starts,(0,1))
    def test_duplicate_blocks(self):
        with self.assertRaises(ValueError):recipes(self.data,self.cmds,self.starts,(0,0))
    def test_overlap_uniqueness(self):self.assertFalse(unique(b'AAA',b'AA'))
    def test_changing_second_read(self):
        ram=self.a+b'Z'*5000;calls=0
        def read(a,n):
            nonlocal calls
            if n==len(self.a):
                calls+=1
                if calls==2:return b'X'*n
            return ram[a-self.start:a-self.start+n]
        self.assertEqual(scan(read,self.start,self.start+len(ram),self.items,4096),[])
if __name__=='__main__':unittest.main()
