"""No emulation: local synthetic ISO, memory responses, breakpoint broadcasts."""
import base64,hashlib,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from f2_ram_provenance_1204 import verified_signature,scan_ram,watch_address_once

class RAMClient:
    def __init__(self,start,raw,unreadable=()):
        self.start=start;self.raw=raw;self.unreadable=set(unreadable);self.calls=[]
    def request(self,event,**kw):
        self.calls.append((event,kw))
        assert event=='memory.read',event
        addr=kw['address'];size=kw['size']
        if addr in self.unreadable:raise RuntimeError('Unreadable PSP page')
        return {'base64':base64.b64encode(self.raw[addr-self.start:addr-self.start+size]).decode()}

class WatchClient:
    def __init__(self,paused=False,related=True,raise_in_disasm=False):
        self.paused=paused;self.related=related;self.raise_in_disasm=raise_in_disasm
        self.calls=[]
    def request(self,event,**kw):
        self.calls.append(event)
        if event=='cpu.status':return {'stepping':self.paused}
        if event in ('memory.breakpoint.add','memory.breakpoint.remove'):
            return {'event':event}
        if event=='memory.disasm':
            if self.raise_in_disasm:raise RuntimeError('disasm unavailable')
            return {'lines':[{'encoding':0x12345678}]}
        if event=='cpu.getAllRegs':return {'categories':[{'name':'GPR'}]}
        raise AssertionError(event)
    def wait_broadcast(self,event):
        self.calls.append('WAIT '+event)
        if event=='cpu.stepping':
            self.paused=True
            return {'pc':0x08808000,'reason':'memory.read',
                    'relatedAddress':0x08809000 if self.related else 0x0880A000}
        if event=='cpu.resume':self.paused=False;return {}
        raise AssertionError(event)
    def notify(self,event):self.calls.append(event)

class TestSignatureAndRAM(unittest.TestCase):
    def test_verified_fixture_exact_signature(self):
        raw=b'PRE'+b'K'*256+b'POST'
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.iso';p.write_bytes(raw)
            sig=verified_signature(p,expected_sha=hashlib.sha256(raw).hexdigest(),offset=3,size=256,
                                   expected_member_sha=hashlib.sha256(b'K'*256).hexdigest())
            self.assertEqual(sig,b'K'*256)
    def test_reject_modified_iso(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'test.iso';p.write_bytes(b'A'*512)
            with self.assertRaises(ValueError):verified_signature(p)
    def test_cross_chunk_signature_detected(self):
        start=0x08800000
        sig=b'\x99'*256
        payload=b'X'*(4096-90)+sig+b'Y'*(8192-(4096-90)-256)
        found=scan_ram(RAMClient(start,payload),sig,start,start+8192,chunk=4096)
        self.assertEqual(found['exact_ram_hits_max_32'],[start+4096-90])
        self.assertTrue(found['is_continuous_complete_scan'])
    def test_unreadable_chunk_breaks_boundary(self):
        start=0x08800000
        sig=b'P'*256
        raw=b'X'*4096+b'P'*128+b'X'*(4096-128)+b'P'*128+b'Y'*(4096-128)
        result=scan_ram(RAMClient(start,raw,unreadable={start+4096}),sig,start,start+12288,chunk=4096)
        self.assertFalse(result['exact_ram_hits_max_32'])
        self.assertEqual(result['unreadable_chunks_count'],1)
    def test_invalid_scan_range(self):
        with self.assertRaises(ValueError):scan_ram(RAMClient(0,b''),b'P'*256,0,4096)
    def test_watchpoint_pc_and_cleanup(self):
        c=WatchClient()
        observed=watch_address_once(c,0x08809000)
        self.assertEqual(observed['cpu_pc_at_pause'],0x08808000)
        self.assertTrue(observed['possible_matching_memory_break'])
        self.assertFalse(observed['ge_upload_proven'])
        self.assertIn('memory.breakpoint.remove',c.calls)
        self.assertIn('cpu.resume',c.calls)
    def test_watchpoint_unrelated_stop_not_attributed(self):
        c=WatchClient(related=False)
        result=watch_address_once(c,0x08809000)
        self.assertFalse(result['possible_matching_memory_break'])
    def test_watchpoint_external_pause_preserved(self):
        c=WatchClient(paused=True)
        with self.assertRaises(RuntimeError):watch_address_once(c,0x08809000)
        self.assertNotIn('memory.breakpoint.add',c.calls)
        self.assertTrue(c.paused)
    def test_watchpoint_failure_cleanup_and_resume(self):
        c=WatchClient(raise_in_disasm=True)
        with self.assertRaises(RuntimeError):watch_address_once(c,0x08809000)
        self.assertEqual(c.calls[-1],'WAIT cpu.resume')
        self.assertFalse(c.paused)
    def test_watchpoint_invalid_size(self):
        with self.assertRaises(ValueError):watch_address_once(WatchClient(),0x08809000,1000)

if __name__=='__main__':unittest.main()
