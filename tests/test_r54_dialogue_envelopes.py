import unittest
from types import SimpleNamespace
from tools.r54_dialogue_envelopes import choose

def cmd(p,code,content=None,block=1):
    return SimpleNamespace(offset=p,code=code,content=content,block=block)

class R54Tests(unittest.TestCase):
    def test_balanced_envelope(self):
        commands=[cmd(0,0x64),cmd(5,0x66,b"a"),cmd(14,0x66,b"bbb"),cmd(25,0x65)]
        a,e=choose(commands,{12:(b"a",b"aa","r")},{21:(b"bbb",b"bb","d")})
        self.assertEqual(set(a),{12,21})
        self.assertEqual(e,[(1,0,25,"r")])
    def test_no_donor_outside(self):
        commands=[cmd(0,0x64),cmd(5,0x66,b"a"),cmd(14,0x65),cmd(19,0x64),cmd(24,0x66,b"bbb"),cmd(35,0x65)]
        self.assertEqual(choose(commands,{12:(b"a",b"aa","r")},{31:(b"bbb",b"bb","d")}),({},[]))
    def test_speaker_not_dialogue(self):
        commands=[cmd(0,0x6e,b"a"),cmd(9,0x64),cmd(14,0x66,b"bbb"),cmd(25,0x65)]
        self.assertEqual(choose(commands,{7:(b"a",b"aa","r")},{21:(b"bbb",b"bb","d")}),({},[]))
    def test_unbalanced(self):
        commands=[cmd(0,0x64),cmd(5,0x66,b"a"),cmd(14,0x66,b"bbb"),cmd(25,0x65)]
        self.assertEqual(choose(commands,{12:(b"a",b"aaa","r")},{21:(b"bbb",b"bb","d")}),({},[]))
