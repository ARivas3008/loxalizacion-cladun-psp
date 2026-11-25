"""Synthetic PPSSPP v1.20.4 JSON/WS contract tests; never actual gameplay C."""
import json
import sys
import types
import unittest
from unittest.mock import patch
from tools.f4_r14_ppsspp_preflight import check_ws_readonly

class FakeWebSocket:
    def __init__(self, version='v1.20.4', gameid='NPUH10072', subprotocol='debugger.ppsspp.org', error=False, broadcast=False):
        self.version=version; self.gameid=gameid; self.subprotocol=subprotocol
        self.error=error;self.broadcast=broadcast;self.messages=[];self.closed=False
        self.sent=[]
    def getsubprotocol(self):return self.subprotocol
    def send(self,s):
        obj=json.loads(s);self.sent.append(obj)
        if self.broadcast:
            self.messages.append({'event':'game.pause'})
        if self.error and obj['event']=='version':
            self.messages.append({'event':'error','ticket':obj['ticket'],'message':'rejected'})
        elif obj['event']=='version':
            self.messages.append({'event':'version','ticket':obj['ticket'],'name':'PPSSPP','version':self.version})
        elif obj['event']=='game.status':
            self.messages.append({'event':'game.status','ticket':obj['ticket'],'game':{'id':self.gameid}})
        else:raise AssertionError('Read-only WS probe sent unexpected event')
    def recv(self):return json.dumps(self.messages.pop(0))
    def close(self):self.closed=True

def fake_run(ws):
    fake=types.SimpleNamespace(create_connection=lambda url,timeout,subprotocols,enable_multithread:ws)
    with patch.dict(sys.modules,{'websocket':fake}):
        return check_ws_readonly(24192)

class TestWsContract(unittest.TestCase):
    def test_version_game_handshake(self):
        ws=FakeWebSocket();r=fake_run(ws)
        self.assertEqual(r['ws_game_id'],'NPUH10072')
        self.assertEqual([s['event'] for s in ws.sent],['version','game.status'])
        self.assertTrue(ws.closed)
    def test_unsolicited_broadcast_ignored(self):
        ws=FakeWebSocket(broadcast=True)
        self.assertEqual(fake_run(ws)['ws_event_version'],'v1.20.4')
    def test_wrong_version_rejected(self):
        ws=FakeWebSocket(version='v1.21.0')
        with self.assertRaises(ValueError):fake_run(ws)
        self.assertTrue(ws.closed)
    def test_wrong_game_rejected(self):
        ws=FakeWebSocket(gameid='OTHERGAME')
        with self.assertRaises(ValueError):fake_run(ws)
    def test_bad_subprotocol_rejected(self):
        ws=FakeWebSocket(subprotocol=None)
        with self.assertRaises(ValueError):fake_run(ws)
    def test_debugger_error_rejected(self):
        ws=FakeWebSocket(error=True)
        with self.assertRaises(ValueError):fake_run(ws)
    def test_has_no_memory_writes(self):
        ws=FakeWebSocket();fake_run(ws)
        self.assertTrue(all(s['event'] in ('version','game.status') for s in ws.sent))
if __name__=='__main__':unittest.main()
