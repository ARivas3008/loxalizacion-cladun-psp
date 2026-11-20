#!/usr/bin/env python3
"""BPS roundtrip and rejection tests on synthetic bytes only."""
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from generar_parche_bps import build_bps, apply_bps, encode_number, decode_number


class TestBPSVerificable(unittest.TestCase):
    def test_canonical_variable_length_numbers_roundtrip(self):
        for n in (0, 1, 2, 127, 128, 129, 256, 16384, 1048576, 1 << 32):
            value = encode_number(n)
            restored, cursor = decode_number(value, 0)
            self.assertEqual(restored, n)
            self.assertEqual(cursor, len(value))

    def test_synthetic_patch_handles_modified_blocks_and_iso_growth(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            old, new = root / "old.bin", root / "new.bin"
            patch, reconstructed = root / "diff.bps", root / "reconstructed.iso"
            old.write_bytes(b"Start" + b"A" * 180000 + b"END")
            new.write_bytes(b"Start" + b"A" * 65536 + b"Spanish text" +
                            b"A" * (180000 - 65536 - len(b"Spanish text")) +
                            b"END" + b"append-only-text" * 170)
            report = build_bps(old, new, patch)
            self.assertEqual(report["target_size"], new.stat().st_size)
            self.assertLess(patch.stat().st_size, new.stat().st_size // 2)
            apply_bps(old, patch, reconstructed)
            self.assertEqual(reconstructed.read_bytes(), new.read_bytes())

    def test_reject_tampered_patch_and_wrong_source(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            old, new = root / "source.iso", root / "target.iso"
            patch, broken, reconstructed = root / "diff.bps", root / "broken.bps", root / "out.iso"
            old.write_bytes(b"A" * 32768 + b"B" * 65536)
            new.write_bytes(b"A" * 32768 + b"C" * 65536)
            build_bps(old, new, patch)
            content = bytearray(patch.read_bytes())
            content[-8] ^= 0x5A
            broken.write_bytes(content)
            with self.assertRaises(ValueError):
                apply_bps(old, broken, reconstructed)
            self.assertFalse(reconstructed.exists())
            old.write_bytes(b"X" + old.read_bytes()[1:])
            with self.assertRaises(ValueError):
                apply_bps(old, patch, reconstructed)
            self.assertFalse(reconstructed.exists())

    def test_refuse_to_overwrite_existing_patch_or_output(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            old, new = root / "orig.iso", root / "new.iso"
            patch, reconstructed = root / "existing.bps", root / "existing_out.iso"
            old.write_bytes(b"ABC")
            new.write_bytes(b"ABCD")
            patch.write_bytes(b"Keep")
            with self.assertRaises(ValueError):
                build_bps(old, new, patch)
            self.assertEqual(patch.read_bytes(), b"Keep")
            patch.unlink()
            build_bps(old, new, patch)
            reconstructed.write_bytes(b"Keep")
            with self.assertRaises(ValueError):
                apply_bps(old, patch, reconstructed)
            self.assertEqual(reconstructed.read_bytes(), b"Keep")


if __name__ == "__main__":
    unittest.main()
