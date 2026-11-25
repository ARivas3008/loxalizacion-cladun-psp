import unittest
import struct
from tools.r57_auxiliary_dialogues import dynamic_parse,native_call_pattern,encode_helper,repack_extended,REMAINING
from tools.r57_imy_refresh import prepare,encode_refresh
from tools.r55_private_accumulated import canonical_plan
from tools.r56_native_ellipsis import extend_donors
from tools.r35_ligaduras_acumuladas import PAIRS
from tools.f4_r21_ligature_capacity import decode_encoded
from tools.imy_repack_safe import compress_block
from tools.extract_cladun import imy_decode,decompress

class R57Tests(unittest.TestCase):
    def test_helper_shape(self):
        d=encode_helper((b"abc",b"de"),iter(range(3225,3230)))
        t=struct.pack("<I12xII24s",1,962160,0,b"r57_dialogue.dsf")
        c,s=dynamic_parse(d,t)
        self.assertEqual([x.code for x in c],[0x64,0x66,0x66,0x65,0x08])
        self.assertEqual([x.content for x in c if x.content is not None],[b"abc",b"de"])
        self.assertEqual(s,[0,len(d)])
    def test_table_guard(self):
        with self.assertRaises(ValueError):dynamic_parse(b"\0"*16,struct.pack("<I12x",1))
    def test_call_pair_only(self):
        d=b"\x0a"+struct.pack("<HHI",2,4,77)+b"\x05"+struct.pack("<HH",2,0)+b"\0"*2
        t=struct.pack("<I12xII24s",1,77,0,b"test.dsf")
        c,_=dynamic_parse(d,t);r=native_call_pattern(c,t)
        self.assertEqual((r["opcode_0a"],r["exact_following_05"],r["arg_matches_script_id"]),(1,1,1))
        self.assertFalse(r["semantics_proven"])
    def test_refresh_and_final_expansion(self):
        h=bytearray(32);h[:4]=b"IMY\0";struct.pack_into("<I",h,4,0x120);struct.pack_into("<H",h,8,16);h[10]=0x10;struct.pack_into("<H",h,12,2)
        raw=b"ab"*8+b"cd"*8
        refreshed=encode_refresh(raw,h,prepare(raw,h))
        self.assertEqual(imy_decode(refreshed,0),raw)
        old=struct.pack("<III",1,32,12)+compress_block(raw,h)
        expanded=raw+b"ef"*16
        new,ch=repack_extended(old,expanded)
        self.assertEqual(ch,[0]);self.assertEqual(decompress(new,len(expanded))[0],expanded)
    def test_canonical_companion_and_residuals(self):
        b,r,d=canonical_plan()
        self.assertEqual(len(REMAINING),11)
        self.assertTrue(REMAINING<={gid for _,_,gid in r.values()})
        companion=next(x for x in b.values() if x[2]=="003567")
        self.assertEqual(decode_encoded(companion[1],PAIRS),"¿Eh?")
        self.assertEqual(len(extend_donors(b,r,d)),36)
