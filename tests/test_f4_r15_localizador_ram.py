"""Synthetic tests B for exact R15 RAM anchor location, not PPSSPP C."""
import base64
import hashlib
import json
import random
import unittest
from unittest.mock import patch
from tools import f4_r15_localizador_ram as mod

class TestR15Locator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.script=random.Random(20261124).randbytes(mod.SCRIPT_SIZE)
        cls.sha=hashlib.sha256(cls.script).hexdigest()
        cls.start=0x08800000
        cls.base=cls.start+756
        cls.ram=bytes([0x55])*756 + cls.script + bytes([0x55])*4096
        cls.end=cls.start+len(cls.ram)
        cls.anchors=[(o,cls.script[o:o+mod.ANCHOR_SIZE]) for o in mod.OFFSETS]
    def read(self,addr,size):
        if addr<self.start or addr+size>self.end:raise ValueError('out of synthetic RAM')
        return self.ram[addr-self.start:addr-self.start+size]
    def scan(self):return mod.candidate_bases(self.read,self.start,self.end,self.anchors,4096)
    def test_found_candidate_from_original_offsets(self):
        got=self.scan();self.assertEqual(got,{self.base:set(mod.OFFSETS)})
    def test_validated_nine_anchors_in_ram(self):
        got=mod.verify_candidates(self.read,self.scan(),self.anchors,full_hash=False)
        self.assertEqual(len(got),1);self.assertEqual(got[0]['anchors_matched'],9)
    def test_full_sha_check_positive(self):
        with patch.object(mod,'SCRIPT_SHA',self.sha):
            got=mod.verify_candidates(self.read,self.scan(),self.anchors)
        self.assertTrue(got[0]['complete_original_script_sha256_matched'])
    def test_full_sha_mismatch_rejected(self):
        got=mod.verify_candidates(self.read,self.scan(),self.anchors)
        self.assertFalse(got[0]['complete_original_script_sha256_matched'])
    def test_binary_fragment_crosses_chunks(self):
        self.assertEqual((self.base+7420-self.start)%4096,4096-16)
        self.assertIn(self.base,self.scan())
    def test_source_requires_exact_sha(self):
        with self.assertRaises(ValueError):mod.script_anchors(self.script)
    def test_source_exact_sha_can_prepare(self):
        with patch.object(mod,'SCRIPT_SHA',self.sha):
            r=mod.prepare_report(self.script)
        self.assertEqual(r['unique_in_original_count'],9)
        self.assertTrue(all('sha256' in x and 'bytes' not in x for x in r['fingerprints']))
        self.assertFalse(r['mips_trace_performed'])
    def test_source_bad_size(self):
        with patch.object(mod,'SCRIPT_SHA',self.sha):
            with self.assertRaises(ValueError):mod.script_anchors(self.script[:-1])
    def test_source_duplicate_offsets(self):
        with patch.object(mod,'SCRIPT_SHA',self.sha):
            with self.assertRaises(ValueError):mod.script_anchors(self.script,(7420,7420,218095))
    def test_source_offset_outside(self):
        with patch.object(mod,'SCRIPT_SHA',self.sha):
            with self.assertRaises(ValueError):mod.script_anchors(self.script,(7420,218095,mod.SCRIPT_SIZE-12))
    def test_forged_ram_wrong_length(self):
        with self.assertRaises(ValueError):mod.candidate_bases(lambda a,n:b'x',self.start,self.end,self.anchors)
    def test_no_hits(self):
        def zero(a,n):return b'\0'*n
        self.assertEqual(mod.candidate_bases(zero,self.start,self.end,self.anchors),{})
    def test_one_anchor_is_not_enough(self):
        fake=bytearray(b'X'*len(self.ram));fake[1000:1032]=self.anchors[0][1]
        def rr(a,n):return bytes(fake[a-self.start:a-self.start+n])
        results=mod.candidate_bases(rr,self.start,self.end,self.anchors)
        self.assertEqual(mod.verify_candidates(rr,results,self.anchors,full_hash=False),[])
    def test_nonunique_anchor_rejected(self):
        with self.assertRaises(ValueError):mod.candidate_bases(self.read,self.start,self.end,[(1,b'x'*32)]*3)
    def test_wrong_size_anchor_rejected(self):
        with self.assertRaises(ValueError):mod.candidate_bases(self.read,self.start,self.end,[(i,b'x'*16) for i in (1,2,3)])
    def test_too_short_range_rejected(self):
        with self.assertRaises(ValueError):mod.valid_scan_range(self.start,self.start+2,4096)
    def test_scan_upper_cap_rejected(self):
        with self.assertRaises(ValueError):mod.valid_scan_range(0x08000000,0x0C000000,4096)
    def test_scan_low_chunk_rejected(self):
        with self.assertRaises(ValueError):mod.valid_scan_range(self.start,self.end,1024)
    def test_scan_high_chunk_rejected(self):
        with self.assertRaises(ValueError):mod.valid_scan_range(self.start,self.end,65537)
    def test_scan_unexpected_memory_address_rejected(self):
        with self.assertRaises(ValueError):mod.valid_scan_range(0x07000000,0x08001000,4096)
    def test_double_anchor_minimum_fails(self):
        with self.assertRaises(ValueError):mod.verify_candidates(self.read,{},self.anchors,min_anchors=2)
    def test_nonpersistent_image_not_runtime_proof(self):
        x=mod.verify_candidates(self.read,self.scan(),self.anchors,full_hash=False)[0]
        self.assertFalse(x['mips_control_flow_observed']);self.assertFalse(x['event_calls_proven'])

class FakeWS:
    def __init__(self,response=None):
        self.sent=[];self.response=response;self.backlog=[]
    def send(self,s):
        p=json.loads(s);self.sent.append(p)
        if self.response is None:
            self.backlog.append({'event':'memory.read','ticket':p['ticket'],'base64':base64.b64encode(b'X'*p['size']).decode()})
        else:self.backlog.extend(self.response(p))
    def recv(self):return json.dumps(self.backlog.pop(0))

class TestReadOnlyWS(unittest.TestCase):
    def test_base64_read_from_official_shape(self):
        w=FakeWS();r=mod.ReadonlyWS(w)
        self.assertEqual(r(0x08800000,16),b'X'*16)
        self.assertEqual([x['event'] for x in w.sent],['memory.read'])
        self.assertTrue(w.sent[0]['replacements'])
    def test_async_unrelated_ticket_ignored(self):
        def produce(p):
            return [{'event':'game.paused','ticket':p['ticket']+7},
                    {'event':'memory.read','ticket':p['ticket'],'base64':base64.b64encode(b'X'*p['size']).decode()}]
        self.assertEqual(mod.ReadonlyWS(FakeWS(produce))(0x08800000,5),b'X'*5)
    def test_invalid_base64_fails(self):
        with self.assertRaises(ValueError):mod.ReadonlyWS(FakeWS(lambda p:[{'event':'memory.read','ticket':p['ticket'],'base64':'no!!'}]))(0x08800000,4)
    def test_bad_length_fails(self):
        with self.assertRaises(ValueError):mod.ReadonlyWS(FakeWS(lambda p:[{'event':'memory.read','ticket':p['ticket'],'base64':'QQ=='}]))(0x08800000,4)
    def test_missing_base64_fails(self):
        with self.assertRaises(ValueError):mod.ReadonlyWS(FakeWS(lambda p:[{'event':'memory.read','ticket':p['ticket']}]))(0x08800000,4)
    def test_debugger_error_fails(self):
        with self.assertRaises(RuntimeError):mod.ReadonlyWS(FakeWS(lambda p:[{'event':'error','ticket':p['ticket']}]))(0x08800000,4)
    def test_unexpected_ticketed_event_fails(self):
        with self.assertRaises(ValueError):mod.ReadonlyWS(FakeWS(lambda p:[{'event':'wrong','ticket':p['ticket']}]))(0x08800000,4)
    def test_zero_size_disallowed(self):
        with self.assertRaises(ValueError):mod.ReadonlyWS(FakeWS())(0x08800000,0)
    def test_over_max_size_disallowed(self):
        with self.assertRaises(ValueError):mod.ReadonlyWS(FakeWS())(0x08800000,65537)
    def test_ram_overflow_disallowed(self):
        with self.assertRaises(ValueError):mod.ReadonlyWS(FakeWS())(0x0BFFFFFF,100)
    def test_no_write_calls(self):
        w=FakeWS();r=mod.ReadonlyWS(w)
        r(0x08800000,4);r(0x08800010,4)
        self.assertTrue(all(x['event']=='memory.read' for x in w.sent))

if __name__=='__main__':unittest.main()
