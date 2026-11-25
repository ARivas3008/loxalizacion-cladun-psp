import struct,unittest,sys,gzip
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from f3_anime_ldt_r18 import records,imy_extent,gzip_payload,nested_geometry,analyze

def ldt(items,kind):
    return struct.pack('<I',len(items))+bytes(12)+b''.join(struct.pack('<4I',len(body),i,kind,2)+body for i,body in items)

def imy(tail=b'\0\0'):
    h=bytearray(34);h[:4]=b'IMY\0';struct.pack_into('<IHBBH',h,4,96,64,0,8,1);struct.pack_into('<H',h,32,2)
    return bytes(h)+b'\x0f\x0f'+bytes(range(64))+tail

def nested(ident=1):
    raw=b'AB'*16;compressed=gzip.compress(raw,mtime=0);start=80
    h=struct.pack('<13I',ident,0,0,0,0,1,1,52,52,52,52,52,56)
    data=h+bytes(4)+struct.pack('<IHHBBH',start,8,8,4,16,272)+bytes(12)+struct.pack('<II',len(compressed),len(raw))+compressed
    return data+bytes((-len(data))%4)

class LDTTests(unittest.TestCase):
    def test_record_length_excludes_header(self):self.assertEqual(records(ldt([(1,b'abcd')],2),2),[(1,b'abcd')])
    def test_record_truncated(self):self.assertRaises(ValueError,records,ldt([(1,b'abcd')],2)[:-1],2)
    def test_record_duplicate_id(self):self.assertRaises(ValueError,records,ldt([(1,b'abcd'),(1,b'abcd')],2),2)
    def test_record_wrong_type(self):self.assertRaises(ValueError,records,ldt([(1,b'abcd')],2),0)
    def test_record_tail(self):self.assertRaises(ValueError,records,ldt([(1,b'abcd')],2)+b'\0',2)
    def test_imy_tail_nonzero(self):self.assertEqual(imy_extent(imy(b'XY')),(64,b'XY'))
    def test_imy_bad_kind(self):
        d=bytearray(imy());d[10]=2;self.assertRaises(ValueError,imy_extent,bytes(d))
    def test_imy_wrong_stride(self):
        d=bytearray(imy());d[8]=32;self.assertRaises(ValueError,imy_extent,bytes(d))
    def test_imy_truncation(self):self.assertRaises(ValueError,imy_extent,imy()[:-3])
    def test_nested_valid(self):self.assertEqual(nested_geometry(1,nested())[0][:2],(4,32))
    def test_nested_id(self):self.assertRaises(ValueError,nested_geometry,2,nested())
    def test_nested_wrong_section(self):
        d=bytearray(nested());struct.pack_into('<I',d,32,53);self.assertRaises(ValueError,nested_geometry,1,bytes(d))
    def test_nested_bad_pointer(self):
        d=bytearray(nested());struct.pack_into('<I',d,56,81);self.assertRaises(ValueError,nested_geometry,1,bytes(d))
    def test_nested_bad_bpp(self):
        d=bytearray(nested());d[64]=2;self.assertRaises(ValueError,nested_geometry,1,bytes(d))
    def test_gzip_crc(self):
        d=bytearray(nested());n=struct.unpack_from('<I',d,80)[0];d[88+n-8]^=1;self.assertRaises(ValueError,nested_geometry,1,bytes(d))
    def test_gzip_wrong_length(self):
        d=bytearray(nested());struct.pack_into('<I',d,84,31);self.assertRaises(ValueError,nested_geometry,1,bytes(d))
    def test_gzip_nonzero_tail(self):self.assertRaises(ValueError,nested_geometry,1,nested()+b'X')
    def test_combined(self):
        a=analyze(ldt([(1,imy(b'XYZW'))],2),ldt([(1,nested())],0));self.assertEqual(a['ldt002_nested_gzip_payloads'],1);self.assertEqual(a['ldt001_nonzero_tails'],1);self.assertFalse(a['repacking_authorized'])

if __name__=='__main__':unittest.main()
