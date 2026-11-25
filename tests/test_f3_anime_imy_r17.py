import struct
import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from f3_anime_imy_r17 import records, decode_bounded, analyze


def image(kind=2, stride=8, rows=1, flags=b'\0\xc0', literal=b'ABCD', tail=b''):
    h=bytearray(34);h[:4]=b'IMY\0'
    struct.pack_into('<IHBBH',h,4,stride*rows+32,stride,kind,4,rows)
    struct.pack_into('<H',h,32,len(flags))
    return bytes(h)+flags+literal+tail


def record(data):
    size=(60+len(data)+3)//4*4
    return struct.pack('<I',size)+bytes(56)+data+bytes(size-60-len(data))


class R17Tests(unittest.TestCase):
    def test_four_byte_repeat(self):
        b=image();self.assertEqual(decode_bounded(b,0,len(b),unit=4)[0],b'ABCDABCD')
    def test_two_byte_repeat(self):
        b=image(kind=0,stride=4,literal=b'AB');self.assertEqual(decode_bounded(b,0,len(b),unit=2)[0],b'ABAB')
    def test_literal_reference(self):
        b=image(flags=b'\0\x10');self.assertEqual(decode_bounded(b,0,len(b),unit=4)[0],b'ABCDABCD')
    def test_literal_width_ambiguous_tail(self):
        b=image();self.assertRaises(ValueError,decode_bounded,b,0,len(b),unit=4,literal_unit=2)
    def test_nonzero_unused_flags(self):
        b=image(flags=b'\0\xc0\x01');self.assertRaises(ValueError,decode_bounded,b,0,len(b),unit=4)
    def test_zero_unused_flags(self):
        b=image(flags=b'\0\xc0\0',tail=b'\0'*8);self.assertEqual(decode_bounded(b,0,len(b),unit=4)[2],2)
    def test_output_lookback(self):
        b=image(flags=b'\xc1',literal=b'');self.assertRaises(ValueError,decode_bounded,b,0,len(b),unit=4)
    def test_literal_lookback(self):
        b=image(flags=b'\x10\x10',literal=b'');self.assertRaises(ValueError,decode_bounded,b,0,len(b),unit=4)
    def test_truncation(self):
        b=image();self.assertRaises(ValueError,decode_bounded,b,0,len(b)-1,unit=4)
    def test_overflow(self):
        b=image(flags=b'\0\xc1');self.assertRaises(ValueError,decode_bounded,b,0,len(b),unit=4)
    def test_nonzero_tail(self):
        b=image(tail=b'X');self.assertRaises(ValueError,decode_bounded,b,0,len(b),unit=4)
    def test_record_exact(self):
        b=struct.pack('<I',1)+bytes(12)+record(image());self.assertEqual(records(b),[(16,len(b))]);self.assertEqual(analyze(b)['types_pass_bounded_candidate'],{2:1})
    def test_record_unaccounted_tail(self):
        b=struct.pack('<I',1)+bytes(12)+record(image())+b'\0';self.assertRaises(ValueError,records,b)
    def test_record_bad_count(self):
        b=struct.pack('<I',2)+bytes(12)+record(image());self.assertRaises(ValueError,records,b)
    def test_two_records(self):
        b=struct.pack('<I',2)+bytes(12)+record(image())+record(image(kind=0,stride=4,literal=b'AB'));self.assertEqual(analyze(b)['types_pass_bounded_candidate'],{0:1,2:1})
    def test_wrong_geometry(self):
        b=bytearray(image());b[4]=0;self.assertRaises(ValueError,decode_bounded,bytes(b),0,len(b),unit=4)


if __name__=='__main__':unittest.main()
