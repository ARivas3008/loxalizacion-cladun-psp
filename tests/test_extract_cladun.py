import sys,unittest,struct,gzip
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import extract_cladun as c

class ExtractorTests(unittest.TestCase):
    def test_instruction_and_text(self):
        text='Hola!'.encode('cp932')
        payload=struct.pack('<H',len(text))+text+b'\0'
        data=b'\x66'+struct.pack('<HH',7,len(payload))+payload+b'\x00'*3
        blocks=[{'index':0,'script_id':41,'start':0,'name':'scr01.dsf','table':'SCRIPT.TBL'}]
        cmds,strings=c.parse_commands(data,blocks,'SCRIPT.SDT/SCRIPT.DAT')
        self.assertEqual(len(cmds),1);self.assertEqual(len(strings),1)
        self.assertEqual(strings[0]['original'],text.decode('cp932'))
        self.assertEqual(strings[0]['offset'],7)
    def test_gzip(self):
        original=b'abcdef'*400
        stored=struct.pack('<III',1,0,12)+gzip.compress(original)
        unpacked,codec=c.decompress(stored,len(original))
        self.assertEqual(unpacked,original);self.assertEqual(codec,'gzip')
    def test_strtbl(self):
        data=struct.pack('<II',8,14)+b'Hello\0World\0'
        rows,n=c.strtbl_entries(data,'x')
        self.assertEqual(n,2);self.assertEqual([r['original'] for r in rows],['Hello','World'])
    def test_pspfs_index(self):
        name=b'A.TXT'+b'\0'*15
        blob=b'PSPFS_V1'+struct.pack('<II',1,0)+name+struct.pack('<III',0,2,48)+b'xy'
        rows=c.pspfs_entries(blob)
        self.assertEqual(rows[0]['name'],'A.TXT');self.assertEqual(rows[0]['offset'],48)

if __name__=='__main__':
    import gzip
    unittest.main()
