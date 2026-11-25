"""Protocolo WebSocket v1.20.4 con respuestas sintéticas, no PPSSPP."""
import base64,json,tempfile,unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from f2_ppsspp_ws_1204 import Client,parse_uri,output_dir,exclusive
class Fake:
    def __init__(self,payload):self.payload=[json.dumps(x) for x in payload];self.sent=[]
    def send(self,x):self.sent.append(json.loads(x))
    def recv(self):return self.payload.pop(0)
class TestF2WS(unittest.TestCase):
    def test_ticket_matching(self):
        ws=Fake([{'event':'cpu.resume'},{'event':'version','ticket':1,'name':'PPSSPP'}])
        self.assertEqual(Client(ws).request('version')['name'],'PPSSPP')

    def test_unticketed_cpu_events_are_buffered_during_ticket_response(self):
        ws=Fake([{'event':'cpu.stepping','pc':0x08804000,'ticks':100},
                 {'event':'version','ticket':1,'name':'PPSSPP'}])
        client=Client(ws)
        self.assertEqual(client.request('version')['name'],'PPSSPP')
        self.assertEqual(client.wait_broadcast('cpu.stepping')['pc'],0x08804000)

    def test_unrelated_broadcasts_remain_available(self):
        ws=Fake([{'event':'cpu.resume'},
                 {'event':'cpu.stepping','pc':0x08804100},
                 {'event':'version','ticket':1,'name':'PPSSPP'}])
        c=Client(ws)
        c.request('version')
        self.assertEqual(c.wait_broadcast('cpu.stepping')['pc'],0x08804100)
        self.assertEqual(c.wait_broadcast('cpu.resume')['event'],'cpu.resume')

    def test_notify_invalidates_previous_broadcast_of_same_type(self):
        ws=Fake([{'event':'cpu.stepping','pc':42},
                 {'event':'version','ticket':1,'name':'PPSSPP'},
                 {'event':'cpu.stepping','pc':80}])
        c=Client(ws)
        c.request('version')
        c.notify('cpu.stepping')
        self.assertEqual(c.wait_broadcast('cpu.stepping')['pc'],80)

    def test_asynchronous_error_never_silently_ignored(self):
        ws=Fake([{'event':'error','message':'CPU not started'},
                 {'event':'version','ticket':1,'name':'PPSSPP'}])
        with self.assertRaises(RuntimeError):
            Client(ws).request('version')

    def test_errors_not_success(self):
        ws=Fake([{'event':'error','ticket':1,'message':'rejected'}])
        with self.assertRaises(RuntimeError):Client(ws).request('gpu.buffer.texture')
    def test_png_uri(self):
        data=b'\x89PNG\r\n\x1a\n'
        self.assertEqual(parse_uri('data:image/png;base64,'+base64.b64encode(data).decode()),data)
    def test_reject_bad_uri(self):
        with self.assertRaises(ValueError):parse_uri('data:text/html;base64,WA==')
    def test_output_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'x.png';exclusive(p,b'abc')
            with self.assertRaises(FileExistsError):exclusive(p,b'def')
    def test_output_not_in_git(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d);(p/'.git').mkdir()
            with self.assertRaises(ValueError):output_dir(p/'new',p)

class EmulatedProtocol:
    """Fake source-API messages; NO game or PPSSPP instance."""
    def __init__(self,stepping=False,invalid_png=False):
        self.stepping=stepping
        self.invalid_png=invalid_png
        self.messages=[]
        self.sent=[]
        self.ticks=300
    def send(self,value):
        req=json.loads(value)
        event=req['event']
        self.sent.append(event)
        ticket=req.get('ticket')
        if event=='cpu.status':
            self.messages.append({'event':event,'ticket':ticket,
                                  'stepping':self.stepping,'ticks':self.ticks})
        elif event=='cpu.stepping':
            if not self.stepping:
                self.stepping=True
                self.ticks+=1000
                self.messages.append({'event':'cpu.stepping','pc':0x08804000,'ticks':self.ticks})
        elif event=='cpu.resume':
            self.stepping=False
            self.messages.append({'event':'cpu.resume'})
        elif event=='gpu.buffer.screenshot':
            if not self.stepping:
                self.messages.append({'event':'error','ticket':ticket,'message':'Neither CPU or GPU is stepping'})
            else:
                image=(b'NOTPNG' if self.invalid_png else b'\x89PNG\r\n\x1a\nSYNTHETIC')
                uri='data:image/png;base64,'+base64.b64encode(image).decode()
                self.messages.append({'event':event,'ticket':ticket,'uri':uri,'width':480,'height':272})
        elif event=='gpu.record.dump':
            if self.stepping:
                self.messages.append({'event':'error','ticket':ticket,'message':'Recorder already busy'})
            else:
                uri='data:application/octet-stream;base64,'+base64.b64encode(b'PPSSPPGE'+b'SYNTHETIC').decode()
                self.messages.append({'event':event,'ticket':ticket,'uri':uri})
        else:
            raise AssertionError('Unexpected synthetic request: '+event)
    def recv(self):
        if not self.messages:
            raise AssertionError('Unexpected recv with no synthetic messages')
        return json.dumps(self.messages.pop(0))

class TestF2CaptureStepping(unittest.TestCase):
    def test_pause_before_every_screenshot_and_resume(self):
        from f2_ppsspp_ws_1204 import capture
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d,patch('f2_ppsspp_ws_1204.time.sleep'):
            ws=EmulatedProtocol()
            r=capture(Client(ws),'CONTROLES',Path(d))
            self.assertEqual(len(r['screenshots']),2)
            self.assertEqual(ws.sent.count('cpu.stepping'),2)
            self.assertEqual(ws.sent.count('cpu.resume'),2)
            self.assertTrue(r['two_distinct_frames_proven'])
            self.assertFalse(r['f1_960x544_window_regression_proven'])
            self.assertEqual(r['screenshots'][0]['psp_framebuffer_width'],480)
            self.assertFalse(ws.stepping)
    def test_ge_dump_recorded_while_cpu_running_first(self):
        from f2_ppsspp_ws_1204 import capture
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d,patch('f2_ppsspp_ws_1204.time.sleep'):
            ws=EmulatedProtocol()
            r=capture(Client(ws),'CONTROLES',Path(d),True)
            self.assertLess(ws.sent.index('gpu.record.dump'),ws.sent.index('cpu.stepping'))
            self.assertEqual(r['gpu_record']['bytes'],len(b'PPSSPPGE'+b'SYNTHETIC'))
    def test_existing_debugger_pause_preserved(self):
        from f2_ppsspp_ws_1204 import capture
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d,patch('f2_ppsspp_ws_1204.time.sleep'):
            ws=EmulatedProtocol(stepping=True)
            r=capture(Client(ws),'OPTIONS',Path(d))
            self.assertEqual(ws.sent.count('cpu.resume'),0)
            self.assertEqual(ws.sent.count('cpu.stepping'),0)
            self.assertFalse(r['two_distinct_frames_proven'])
            self.assertTrue(ws.stepping)
    def test_ge_dump_not_allowed_when_already_paused(self):
        from f2_ppsspp_ws_1204 import capture
        with tempfile.TemporaryDirectory() as d:
            ws=EmulatedProtocol(stepping=True)
            with self.assertRaises(RuntimeError):
                capture(Client(ws),'OPTIONS',Path(d),True)
            self.assertNotIn('gpu.record.dump',ws.sent)
    def test_capture_failure_restores_running_cpu(self):
        from f2_ppsspp_ws_1204 import capture
        with tempfile.TemporaryDirectory() as d:
            ws=EmulatedProtocol(invalid_png=True)
            with self.assertRaises(ValueError):
                capture(Client(ws),'DIALOGUE',Path(d))
            self.assertEqual(ws.sent.count('cpu.resume'),1)
            self.assertFalse(ws.stepping)
    def test_ge_only_saves_synthetic_dump_without_buffer_or_pause(self):
        from f2_ppsspp_ws_1204 import capture
        with tempfile.TemporaryDirectory() as d:
            ws=EmulatedProtocol()
            r=capture(Client(ws),'HABILIDAD',Path(d),ge_dump=True,ge_only=True)
            self.assertEqual(r['screenshots'],[])
            self.assertEqual(r['gpu_record']['bytes'],len(b'PPSSPPGE'+b'SYNTHETIC'))
            self.assertEqual(r['source'],'gpu.record.dump on running PPSSPP (GE-only; no framebuffer PNG)')
            self.assertFalse(r['gpu_framebuffer_readback_attempted'])
            self.assertFalse(r['two_distinct_frames_proven'])
            self.assertFalse(r['mips_ram_ge_vram_proven'])
            self.assertFalse(r['texture_identity_proven'])
            self.assertFalse(r['f1_960x544_window_regression_proven'])
            self.assertEqual(ws.sent, ['cpu.status', 'gpu.record.dump'])
            self.assertFalse(ws.stepping)
            self.assertEqual(sorted(p.name for p in Path(d).iterdir()), ['HABILIDAD_GE_PRIVATE.dump'])
    def test_ge_only_requires_explicit_record(self):
        from f2_ppsspp_ws_1204 import capture
        with tempfile.TemporaryDirectory() as d:
            ws=EmulatedProtocol()
            with self.assertRaises(ValueError):
                capture(Client(ws),'HABILIDAD',Path(d),ge_only=True)
            self.assertEqual(ws.sent,[])
    def test_ge_only_rejects_paused_cpu_without_writing(self):
        from f2_ppsspp_ws_1204 import capture
        with tempfile.TemporaryDirectory() as d:
            ws=EmulatedProtocol(stepping=True)
            with self.assertRaises(RuntimeError):
                capture(Client(ws),'HABILIDAD',Path(d),ge_dump=True,ge_only=True)
            self.assertEqual(ws.sent,['cpu.status'])
            self.assertEqual(list(Path(d).iterdir()),[])
    def test_paused_cpu_rejects_running_gpu_recorder(self):
        from f2_ppsspp_ws_1204 import capture
        with tempfile.TemporaryDirectory() as d:
            ws=EmulatedProtocol(stepping=True)
            with self.assertRaises(RuntimeError):
                capture(Client(ws),'COMBATE',Path(d),True)
            self.assertEqual(ws.sent,['cpu.status'])

if __name__=='__main__':unittest.main()
