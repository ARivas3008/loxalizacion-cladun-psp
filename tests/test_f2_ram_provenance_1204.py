"""No emulation: local synthetic ISO, memory responses, breakpoint broadcasts."""
import base64,hashlib,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from f2_ram_provenance_1204 import verified_signature,scan_ram,scan_ram_snapshot,watch_address_once,assert_watchpoint_free

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
        self.calls=[];self.existing_checks=[];self.reason='memory.breakpoint'
    def request(self,event,**kw):
        self.calls.append(event)
        if event=='cpu.status':return {'stepping':self.paused}
        if event=='memory.breakpoint.list':return {'breakpoints':self.existing_checks}
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
            return {'pc':0x08808000,'reason':self.reason,
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
        self.assertTrue(c.paused, 'Una pausa ajena nunca debe reanudarse automáticamente')
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


class SnapshotClient(RAMClient):
    def __init__(self,start,raw,stepping=False,mutate_ticks=False):
        super().__init__(start,raw)
        self.stepping=stepping
        self.ticks=200
        self.mutate_ticks=mutate_ticks
        self.requests=0
        self.notifications=[]
    def request(self,event,**kwargs):
        if event=='cpu.status':
            self.requests+=1
            if self.mutate_ticks and self.requests>=3:
                self.ticks+=10
            return {'stepping':self.stepping,'ticks':self.ticks}
        return super().request(event,**kwargs)
    def notify(self,event):
        self.notifications.append(event)
    def wait_broadcast(self,event):
        if event=='cpu.stepping':self.stepping=True;return {'event':event}
        if event=='cpu.resume':self.stepping=False;return {'event':event}
        raise AssertionError(event)

class TestSnapshotConsistency(unittest.TestCase):
    def test_scans_paused_and_resumes_if_client_paused(self):
        start=0x08800000
        sig=b'Z'*256
        c=SnapshotClient(start,b'A'*(4096-50)+sig+b'B'*(4096-206))
        report=scan_ram_snapshot(c,sig,start,start+8192,chunk=4096)
        self.assertEqual(report['exact_ram_hits_max_32'],[start+4096-50])
        self.assertTrue(report['snapshot_cpu_stepping_confirmed'])
        self.assertFalse(report['pause_preexisted'])
        self.assertEqual(c.notifications,['cpu.stepping','cpu.resume'])
        self.assertFalse(c.stepping)
    def test_preserves_external_pause(self):
        start=0x08800000
        c=SnapshotClient(start,b'A'*4096,stepping=True)
        report=scan_ram_snapshot(c,b'Z'*256,start,start+4096,chunk=4096)
        self.assertTrue(report['pause_preexisted'])
        self.assertTrue(c.stepping)
        self.assertEqual(c.notifications,[])
    def test_rejects_scan_if_emulated_ticks_advance(self):
        start=0x08800000
        c=SnapshotClient(start,b'A'*4096,mutate_ticks=True)
        with self.assertRaisesRegex(RuntimeError,'CPU avanzó'):
            scan_ram_snapshot(c,b'Z'*256,start,start+4096,chunk=4096)
        self.assertFalse(c.stepping)
        self.assertEqual(c.notifications,['cpu.stepping','cpu.resume'])


class TestWatchpointOwnership(unittest.TestCase):
    def test_overlapping_existing_breakpoint_rejected_without_side_effect(self):
        client=WatchClient()
        client.existing_checks=[{'address':0x08809002,'size':4,'enabled':False}]
        with self.assertRaisesRegex(RuntimeError,'breakpoint del operador'):
            watch_address_once(client,0x08809000,4)
        self.assertNotIn('memory.breakpoint.add',client.calls)
        self.assertNotIn('memory.breakpoint.remove',client.calls)
        self.assertNotIn('cpu.resume',client.calls)
    def test_adjacent_previous_breakpoint_allowed(self):
        client=WatchClient()
        client.existing_checks=[{'address':0x08809004,'size':4,'enabled':True}]
        result=watch_address_once(client,0x08809000,4)
        self.assertTrue(result['possible_matching_memory_break'])
        self.assertIn('memory.breakpoint.remove',client.calls)
    def test_zero_size_old_breakpoint_fails_closed(self):
        client=WatchClient()
        client.existing_checks=[{'address':0x08809000,'size':0}]
        with self.assertRaisesRegex(RuntimeError,'ambiguo'):
            watch_address_once(client,0x08809000,4)
        self.assertNotIn('memory.breakpoint.add',client.calls)
    def test_unrelated_reason_same_address_does_not_resume(self):
        client=WatchClient()
        client.reason='cpu.breakpoint'
        result=watch_address_once(client,0x08809000)
        self.assertFalse(result['possible_matching_memory_break'])
        self.assertTrue(client.paused)
        self.assertNotIn('cpu.resume',client.calls)
        self.assertIn('memory.breakpoint.remove',client.calls)
    def test_memory_breakpoint_reason_with_wrong_address_is_unrelated(self):
        client=WatchClient(related=False)
        result=watch_address_once(client,0x08809000)
        self.assertEqual(result['broadcast_reason'],'memory.breakpoint')
        self.assertFalse(result['possible_matching_memory_break'])
        self.assertTrue(client.paused)
    def test_invalid_breakpoint_list_is_rejected(self):
        class NoList:
            def request(self,event,**kwargs):
                return {'breakpoints':'invalid'}
        with self.assertRaises(RuntimeError):
            assert_watchpoint_free(NoList(),0x08809000,4)

if __name__=='__main__':unittest.main()
