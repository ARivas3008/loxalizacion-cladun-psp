"""Synthetic-only tests for isolated private TUIKA palette probe."""
import hashlib
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from tools import f2_probe_tuika_palette_privado as p

def fixture_member():
    m=bytearray(128)
    m[:4]=b'IMY\x00';m[4]=0x60;m[10]=0xA4
    m[40:44]=p.BEFORE
    return bytes(m)

def fixture_arc():
    n=27;head=16+48*n;a=bytearray(head+16*n)
    a[:8]=b'DSARC FL'
    struct.pack_into('<I',a,8,n)
    for i in range(n):
        off=16+48*i
        name=f'MEMBER_{i}.IMY'.encode()
        a[off:off+len(name)]=name
        struct.pack_into('<II',a,off+40,16,head+16*i)
    return bytes(a)

class TestTUIKAPrivateProbe(unittest.TestCase):
    def test_three_rgb_bytes_only(self):
        raw=fixture_member()
        with patch.object(p,'TUIKA_SIZE',len(raw)),patch.object(p,'ORIGINAL_MEMBER_SHA',p.sha(raw)):
            changed,at=p.patch_member(raw)
        self.assertEqual(at,[40,41,42])
        self.assertEqual(changed[40:44],p.AFTER)
        self.assertEqual(changed[43],raw[43])
        self.assertEqual([i for i in range(len(raw)) if changed[i]!=raw[i]],at)
    def test_source_member_immutable(self):
        raw=fixture_member()
        with patch.object(p,'TUIKA_SIZE',len(raw)),patch.object(p,'ORIGINAL_MEMBER_SHA',p.sha(raw)):
            p.patch_member(raw)
        self.assertEqual(raw[40:44],p.BEFORE)
    def test_wrong_member_checksum(self):
        with patch.object(p,'TUIKA_SIZE',128):
            with self.assertRaisesRegex(ValueError,'SHA'):
                p.patch_member(fixture_member())
    def test_wrong_rgba(self):
        m=bytearray(fixture_member());m[40]=1;raw=bytes(m)
        with patch.object(p,'TUIKA_SIZE',128),patch.object(p,'ORIGINAL_MEMBER_SHA',p.sha(raw)):
            with self.assertRaisesRegex(ValueError,'RGBA'):
                p.patch_member(raw)
    def test_wrong_texture_type(self):
        m=bytearray(fixture_member());m[10]=0x84;raw=bytes(m)
        with patch.object(p,'TUIKA_SIZE',128),patch.object(p,'ORIGINAL_MEMBER_SHA',p.sha(raw)):
            with self.assertRaisesRegex(ValueError,'IMY type'):
                p.patch_member(raw)
    def test_dsarc_rows(self):
        self.assertEqual(len(p.parse_dsarc(fixture_arc())),27)
    def test_dsarc_overlap_rejected(self):
        a=bytearray(fixture_arc())
        struct.pack_into('<I',a,16+24*48+44,16+27*48+23*16)
        with self.assertRaisesRegex(ValueError,'overlap'):
            p.parse_dsarc(bytes(a))
    def test_dsarc_duplicate_rejected(self):
        a=bytearray(fixture_arc())
        a[16+24*48:16+24*48+40]=a[16+23*48:16+23*48+40]
        with self.assertRaisesRegex(ValueError,'Duplicate'):
            p.parse_dsarc(bytes(a))
    def test_dsarc_out_of_bounds(self):
        a=bytearray(fixture_arc())
        struct.pack_into('<I',a,16+24*48+44,len(a)+10)
        with self.assertRaisesRegex(ValueError,'bounds'):
            p.parse_dsarc(bytes(a))
    def test_dsarc_bad_magic(self):
        with self.assertRaisesRegex(ValueError,'DSARC'):
            p.parse_dsarc(b'NOPE')
    def test_delta_exact(self):
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/'a';b=Path(td)/'b'
            a.write_bytes(b'abcdefgh');b.write_bytes(b'abcDEFgh')
            self.assertEqual(p.exact_deltas(a,b,{3:(100,68),4:(101,69),5:(102,70)}),[3,4,5])
    def test_delta_unexpected(self):
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/'a';b=Path(td)/'b'
            a.write_bytes(b'abc');b.write_bytes(b'xbc')
            with self.assertRaisesRegex(ValueError,'Unauthorized'):
                p.exact_deltas(a,b,{1:(98,90)})
    def test_delta_missing(self):
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/'a';b=Path(td)/'b'
            a.write_bytes(b'abc');b.write_bytes(b'abc')
            with self.assertRaisesRegex(ValueError,'Missing'):
                p.exact_deltas(a,b,{1:(98,90)})
    def test_delta_length_change(self):
        with tempfile.TemporaryDirectory() as td:
            a=Path(td)/'a';b=Path(td)/'b'
            a.write_bytes(b'abc');b.write_bytes(b'ab')
            with self.assertRaisesRegex(ValueError,'length'):
                p.exact_deltas(a,b,{})
    def test_output_must_be_absolute(self):
        with self.assertRaisesRegex(ValueError,'absolute'):
            p.check_private(Path('probe.iso'),'.iso')
    def test_output_wrong_extension(self):
        with self.assertRaisesRegex(ValueError,'absolute'):
            p.check_private(Path('/tmp/x.png'),'.iso')
    def test_reject_repo_path(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td)
            with self.assertRaisesRegex(ValueError,'GitHub'):
                p.check_private(root/'sub'/'probe.iso','.iso',repo=root)
    def test_reject_overwrite(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);f=root/'probe.iso';f.write_bytes(b'xyz')
            with self.assertRaises(FileExistsError):
                p.check_private(f,'.iso',repo=root/'repo')
    def test_reject_symlink_into_repo(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'repo').mkdir();(root/'alias').symlink_to(root/'repo')
            with self.assertRaisesRegex(ValueError,'GitHub'):
                p.check_private(root/'alias'/'probe.iso','.iso',repo=root/'repo')
    def test_allow_private(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);target=root/'private'/'probe.iso'
            self.assertEqual(p.check_private(target,'.iso',repo=root/'repo'),target)
    def test_64_character_source_sha(self):
        self.assertEqual(len(p.ORIGINAL_SHA),64)
        self.assertEqual(p.ORIGINAL_SHA,'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f')
    def test_digest(self):
        self.assertEqual(p.sha(b'xyz'),hashlib.sha256(b'xyz').hexdigest())
