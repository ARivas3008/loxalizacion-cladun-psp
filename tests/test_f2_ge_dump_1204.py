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

    def test_ge_texture_clut_address_candidates_are_stateful_not_proof(self):
        words=[
            0x1E000001,       # textureMapEnable=1
            0xA0012340,       # texaddr0 low bits
            0xA8040020,       # texbufwidth0 carries 0x04000000
            0xB0005670,
            0xB1040000,
            0xC3000004,       # indexed 4-bit format
            0x04000006,       # prim
        ]
        report=inspect(fixture(words=words))
        obs=report['ge_address_candidates_limited_to_150']
        self.assertEqual(len(obs),1)
        self.assertEqual(obs[0]['texture_address_candidates'][0]['address_candidate'],'0x04012340')
        self.assertEqual(obs[0]['clut_address_candidate'],'0x04005670')
        self.assertTrue(obs[0]['texture_mapping_enabled_seen'])
        self.assertEqual(obs[0]['texture_format_seen'],4)
        self.assertEqual(obs[0]['primitive_vertex_count_seen'],6)
        self.assertFalse(report['texture_identity_proven'])
        self.assertFalse(report['vram_upload_proven'])
    def test_missing_upper_texture_bits_yield_no_fabricated_address(self):
        report=inspect(fixture(words=[0xA0012340,0x04000004]))
        self.assertNotIn('texture_address_candidates',
                         report['ge_address_candidates_limited_to_150'][0])
        self.assertNotIn('clut_address_candidate',
                         report['ge_address_candidates_limited_to_150'][0])
    def test_transfer_addresses_use_pspsdk_gpu_state_formula(self):
        words=[0xB2001000,0xB3040020,0xB4002000,0xB5040020,
               0xEE000000,0xEA000001]
        report=inspect(fixture(words=words))
        obs=report['ge_address_candidates_limited_to_150'][0]
        self.assertEqual(obs['trigger'],'TRANSFERSTART')
        self.assertEqual(obs['transfer_source_address_candidate'],'0x04001000')
        self.assertEqual(obs['transfer_destination_address_candidate'],'0x04002000')
        self.assertEqual(obs['transfer_width_pixels_seen'],1)
        self.assertEqual(obs['transfer_height_pixels_seen'],1)
        self.assertEqual(obs['transfer_bpp_bytes_seen'],4)
        self.assertTrue(obs['source_in_primary_2mib_vram_window'])
        self.assertFalse(report['vram_upload_proven'])
    def test_non_vram_address_classified_without_identity_claim(self):
        report=inspect(fixture(words=[0xA0001000,0xA8080020,0x04000001]))
        addr=report['ge_address_candidates_limited_to_150'][0]['texture_address_candidates'][0]
        self.assertEqual(addr['address_candidate'],'0x08001000')
        self.assertFalse(addr['in_primary_2mib_vram_window'])
        self.assertTrue(report['addresses_are_partial_unverified_candidates'])

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
