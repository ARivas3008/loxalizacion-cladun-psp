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
if __name__=='__main__':unittest.main()
