import unittest
from types import SimpleNamespace
from tools.r53_relative_bidir import relative_scan,movement

def cmd(p,order,payload=b"",block=0,text=False):
    return SimpleNamespace(offset=p,order=order,block=block,code=0x66 if text else 1,
        instruction_id=order,raw=b"\x00"*5+payload,content=b"x" if text else None)

class R53Tests(unittest.TestCase):
    def test_target_moves(self):
        a,b=cmd(100,0,b"\x14\x00"),cmd(120,1)
        hits=relative_scan([a,b],{120:{"delta":1}})
        self.assertEqual(len(hits),1)
        self.assertEqual(hits[0]["difference"],1)
    def test_source_moves_target_fixed(self):
        a,b=cmd(100,0,b"\x14\x00"),cmd(120,1)
        hits=relative_scan([a,b],{100:{"delta":-1}})
        self.assertEqual(len(hits),1)
        self.assertEqual(hits[0]["difference"],1)
    def test_both_move_same_is_not_candidate(self):
        a,b=cmd(100,0,b"\x14\x00"),cmd(120,1)
        self.assertEqual(relative_scan([a,b],{100:{"delta":1},120:{"delta":1}}),[])
    def test_cross_block_not_local(self):
        a,b=cmd(100,0,b"\x14\x00"),cmd(120,1,block=1)
        self.assertEqual(relative_scan([a,b],{120:{"delta":1}}),[])
    def test_movement_and_net_guard(self):
        a,b,c=cmd(100,0,text=True),cmd(120,1),cmd(140,2,text=True)
        self.assertEqual(set(movement([a,b,c],{107:1,147:-1})),{120,140})
        with self.assertRaises(ValueError): movement([a,b,c],{107:1})
    def test_negative_relative_end(self):
        a,b=cmd(100,0),cmd(120,1,b"\xe5\xff")
        hits=relative_scan([a,b],{100:{"delta":1}})
        self.assertEqual(len(hits),1)
        self.assertEqual(hits[0]["base"],"end")
        self.assertEqual(hits[0]["signed_value"],-27)
