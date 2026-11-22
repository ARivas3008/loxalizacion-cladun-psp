"""Unit tests: synthetic DSARC containers only; no game textures."""
import struct
import unittest

from tools.f2_catalogo_global_dsarc_usa import (
    classify_header, inspect_container, sha256,
)

def synthetic_container(magic=b"DSARC FL", names=None, payloads=None):
    names = names or ("A.IMY", "B.PNG")
    payloads = payloads or (b"IMY\x00" + b"\x00" * 16,
                            b"\x89PNG\r\n\x1a\n" + b"\x00" * 12)
    count = len(names)
    if magic == b"DSARC FL":
        start = 16
    else:
        start = (16 + 2 * count + 3) // 4 * 4
    raw = bytearray(start + count * 48)
    raw[:8] = magic
    struct.pack_into("<I", raw, 8, count)
    for i, (name, payload) in enumerate(zip(names, payloads)):
        pos = start + i * 48
        raw[pos:pos + len(name)] = name.encode("ascii")
        struct.pack_into("<II", raw, pos + 40, len(payload), len(raw))
        raw.extend(payload)
    return bytes(raw)

class TestAllDsarcMetadata(unittest.TestCase):
    def test_fl_container(self):
        value = inspect_container(synthetic_container())
        self.assertEqual(value["container_magic"], "DSARC FL")
        self.assertEqual(value["members_count"], 2)
        self.assertEqual(value["members"][0]["signature_kind"], "IMY_SIGNATURE")
        self.assertFalse(value["members"][0]["ppsspp_runtime_use_proven"])

    def test_idx_container(self):
        value = inspect_container(synthetic_container(magic=b"DSARCIDX"))
        self.assertEqual(value["container_magic"], "DSARCIDX")
        self.assertEqual(value["members"][1]["signature_kind"], "PNG_SIGNATURE")

    def test_sps_signature(self):
        self.assertEqual(classify_header("SE_001.SPS", b"\x01\0\0\0" + b"DATA"),
                         "SPS_SIGNATURE_ONLY")

    def test_font_bin_has_no_graphic_claim(self):
        self.assertEqual(classify_header("FONT.BIN", b"\x00\x01"),
                         "BINARY_UNCLASSIFIED")

    def test_reject_bad_imy(self):
        with self.assertRaisesRegex(ValueError, "IMY member"):
            classify_header("FONT.IMY", b"\x00" * 20)

    def test_reject_bad_png(self):
        with self.assertRaisesRegex(ValueError, "PNG member"):
            classify_header("FONT.PNG", b"\x00" * 20)

    def test_reject_bad_sps(self):
        with self.assertRaisesRegex(ValueError, "SPS member"):
            classify_header("S.SPS", b"\x00" * 20)

    def test_reject_unknown_extension(self):
        with self.assertRaisesRegex(ValueError, "Unexpected member"):
            classify_header("X.EXE", b"\x00" * 20)

    def test_reject_duplicate_names(self):
        data = synthetic_container(names=("A.IMY", "A.IMY"),
                                   payloads=(b"IMY\0" * 3, b"IMY\0" * 3))
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            inspect_container(data)

    def test_reject_bad_member_offset_in_table(self):
        data = bytearray(synthetic_container())
        struct.pack_into("<I", data, 16 + 44, 16)
        with self.assertRaisesRegex(ValueError, "offset/size"):
            inspect_container(bytes(data))

    def test_reject_overlap(self):
        data = bytearray(synthetic_container())
        first_offset = struct.unpack_from("<I", data, 16 + 44)[0]
        struct.pack_into("<I", data, 16 + 48 + 44, first_offset + 8)
        with self.assertRaisesRegex(ValueError, "overlap"):
            inspect_container(bytes(data))

    def test_sha_deterministic(self):
        self.assertEqual(sha256(b"ABC"), sha256(b"ABC"))
        self.assertNotEqual(sha256(b"ABC"), sha256(b"ABD"))
