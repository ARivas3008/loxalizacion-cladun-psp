"""Fixtures PSPFS/DSARC sintéticos: no dependen de una ISO comercial."""
import struct
import unittest
from tools.f2_auditar_origen_iconos import ISO_SHA256, IMY_SHA256, dsarc_entries, iso_entry, pspfs_entries, sha256

class TestF2OrigenIconos(unittest.TestCase):
    def make_pspfs(self):
        b=bytearray(128);b[:8]=b"PSPFS_V1"
        struct.pack_into("<I",b,8,1);b[16:24]=b"TEST.ARC"
        struct.pack_into("<III",b,36,4,4,112)
        return b
    def make_dsarc(self):
        b=bytearray(128);b[:8]=b"DSARC FL"
        struct.pack_into("<I",b,8,1);b[16:24]=b"TEST.IMY"
        struct.pack_into("<II",b,56,8,96)
        return b
    def test_hash_lengths(self):
        self.assertEqual(len(ISO_SHA256),64)
        self.assertEqual(len(IMY_SHA256),64)
        self.assertEqual(len(sha256(b"ab")),64)
    def test_pspfs_valid(self):
        e=pspfs_entries(self.make_pspfs())[0]
        self.assertEqual((e["name"],e["offset"],e["size_stored"]),("TEST.ARC",112,4))
    def test_pspfs_out_of_bounds(self):
        b=self.make_pspfs();struct.pack_into("<I",b,44,65535)
        with self.assertRaises(ValueError):pspfs_entries(b)
    def test_pspfs_wrong_magic(self):
        b=self.make_pspfs();b[:8]=b"INVALID!"
        with self.assertRaises(ValueError):pspfs_entries(b)
    def test_dsarc_valid(self):
        e=dsarc_entries(self.make_dsarc())[0]
        self.assertEqual((e["name"],e["offset"],e["size"]),("TEST.IMY",96,8))
    def test_dsarc_out_of_bounds(self):
        b=self.make_dsarc();struct.pack_into("<I",b,60,65535)
        with self.assertRaises(ValueError):dsarc_entries(b)
    def test_iso_bad_record(self):
        with self.assertRaises(ValueError):iso_entry(b"\0"*34)
