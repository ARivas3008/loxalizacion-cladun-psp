import unittest
import struct
from types import SimpleNamespace
from tools.r54_dialogue_envelopes import choose
from tools.r55_private_accumulated import repack_min,canonical_plan
from tools.imy_repack_safe import compress_block
from tools.extract_cladun import imy_decode

class R55Tests(unittest.TestCase):
    def test_speaker_box_opt_in(self):
        def c(p,op,content=None,block=0):return SimpleNamespace(offset=p,code=op,block=block,content=content)
        commands=[c(0,0x6e,b"a"),c(9,0x64),c(14,0x66,b"bbb"),c(25,0x65)]
        residual={7:(b"a",b"aa","r")};donors={21:(b"bbb",b"bb","d")}
        self.assertEqual(choose(commands,residual,donors),({},[]))
        selected,envelopes=choose(commands,residual,donors,include_speakers=True)
        self.assertEqual(set(selected),{7,21})
        self.assertEqual(envelopes,[(0,0,25,"r")])
    def test_pending_literal_copy(self):
        h=bytearray(32);h[:4]=b"IMY\0";struct.pack_into("<H",h,8,16);h[10]=0x10;struct.pack_into("<H",h,12,2)
        raw=b"aa"+"bb".encode()+b"aa"+b"ccddeeffgghhiijjkkllmmnnoo"
        self.assertEqual(len(raw),32)
        old=compress_block(raw,h);new=compress_block(raw,h,pending_refs=True)
        self.assertEqual(imy_decode(old,0),raw);self.assertEqual(imy_decode(new,0),raw)
        container=struct.pack("<III",1,32,12)+old
        changed=raw[:-2]+b"pp";packed,ch=repack_min(container,changed)
        self.assertEqual(ch,[0]);self.assertEqual(imy_decode(packed,12),changed)
    def test_canonical_plan_counts(self):
        full,residual,donors=canonical_plan()
        self.assertEqual((len(full),len(residual),len(donors)),(4866,33,35))
        self.assertEqual(sum(len(n)-len(o) for o,n,_ in residual.values()),40)
        self.assertEqual(sum(len(o)-len(n) for o,n,_ in donors.values()),40)
