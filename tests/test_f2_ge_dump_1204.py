"""Only synthetic PPSSPP v6 dump fixtures, no game data."""
import ctypes
import hashlib
import struct
import unittest
from tools.f2_ge_dump_1204 import inspect, MAGIC, VERSION, GE_NAMES

def compress(part):
    z=ctypes.CDLL('libzstd.so.1')
    z.ZSTD_compressBound.argtypes=[ctypes.c_size_t]
    z.ZSTD_compressBound.restype=ctypes.c_size_t
    z.ZSTD_compress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t,ctypes.c_int]
    z.ZSTD_compress.restype=ctypes.c_size_t
    src=ctypes.create_string_buffer(part)
    dest=ctypes.create_string_buffer(z.ZSTD_compressBound(len(part)))
    size=z.ZSTD_compress(dest,len(dest),src,len(part),1)
    return struct.pack('<I',size)+dest.raw[:size]

def fixture(ty=1,ptr=0,sz=None,words=None,extra=b''):
    if words is None:
        words=[0xA0001234,0xB0000004,0x04000004]
    raw=b''.join(struct.pack('<I',x) for x in words)
    cmd=struct.pack('<BII',ty,len(raw) if sz is None else sz,ptr)
    hdr=MAGIC+struct.pack('<I',VERSION)+b'ULUS12345'+b'\0'*3
    return hdr+struct.pack('<II',1,len(raw))+compress(cmd)+compress(raw)+extra

class TestGEV6(unittest.TestCase):
    def test_static_extracts_ge_register_metadata(self):
        data=fixture()
        r=inspect(data)
        self.assertEqual(r['recorded_command_count'],1)
        self.assertEqual(r['ge_register_opcode_counts'],{'CLUTADDR':1,'PRIM':1,'TEXADDR0':1})
        self.assertEqual(r['dump_sha256'],hashlib.sha256(data).hexdigest())
        self.assertFalse(r['mips_pc_proven'])
        self.assertFalse(r['vram_upload_proven'])
    def test_invalid_header(self):
        with self.assertRaises(ValueError):
            inspect(b'NO'+fixture()[2:])
    def test_invalid_version(self):
        b=bytearray(fixture())
        struct.pack_into('<I',b,8,5)
        with self.assertRaises(ValueError):
            inspect(bytes(b))
    def test_truncated_blocks(self):
        with self.assertRaises(ValueError):
            inspect(fixture()[:-10])
    def test_trailing_data(self):
        with self.assertRaises(ValueError):
            inspect(fixture()+b'a')
    def test_unknown_recorder_command(self):
        with self.assertRaises(ValueError):
            inspect(fixture(ty=12))
    def test_span_overrun(self):
        with self.assertRaises(ValueError):
            inspect(fixture(sz=400000))
    def test_unaligned_register_block(self):
        with self.assertRaises(ValueError):
            inspect(fixture(sz=7))
    def test_ge_opcode_definitions(self):
        self.assertEqual(GE_NAMES[0xB0],'CLUTADDR')
        self.assertEqual(GE_NAMES[0xEA],'TRANSFERSTART')

if __name__=='__main__':
    unittest.main()
