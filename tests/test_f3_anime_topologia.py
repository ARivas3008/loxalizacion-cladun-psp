"""Synthetic-only topology tests, independent of commercial ISO or emulation."""
import importlib.util
import struct
import tempfile
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'tools' / 'f3_anime_topologia.py'
spec = importlib.util.spec_from_file_location('f3_anime_topologia', SOURCE)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def fake_imy(typ=0, flag_count=1, stride=2, rows=1):
    raw = bytearray(34)
    raw[:4] = b'IMY\x00'
    struct.pack_into('<IHBBH', raw, 4, stride * rows + 32, stride, typ, 4, rows)
    struct.pack_into('<H', raw, 32, flag_count)
    return bytes(raw) + b'\x00' * flag_count + b'\x11' * ((-34 - flag_count) % 4)

class Tests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(mod.topology(b'xx')['literal_headers'], 0)
    def test_synthetic_types_and_transition(self):
        result = mod.topology(fake_imy(0) + fake_imy(2))
        self.assertEqual(result['header_type_counts'], {'0x00': 1, '0x02': 1})
        self.assertEqual(result['adjacent_type_transitions'], {'00->02': 1})
    def test_run_length(self):
        result = mod.topology(fake_imy(2) * 3 + fake_imy(0))
        self.assertEqual(result['longest_consecutive_run_by_type'], {'0x00': 1, '0x02': 3})
    def test_identical_interval_detection(self):
        result = mod.topology(fake_imy(2) * 3)
        self.assertEqual(result['exact_duplicate_adjacent_intervals_by_type']['0x02'], 2)
    def test_different_members_not_mixed(self):
        self.assertEqual(mod.topology(fake_imy(0))['exact_duplicate_adjacent_intervals_by_type'], {'0x00': 0})
    def test_unaligned_magic_rejected(self):
        with self.assertRaises(ValueError):mod.topology(b'x' + fake_imy(0))
    def test_bad_geometry_rejected(self):
        b = bytearray(fake_imy()); struct.pack_into('<I', b, 4, 999)
        with self.assertRaises(ValueError):mod.topology(bytes(b))
    def test_unknown_type_rejected(self):
        with self.assertRaises(ValueError):mod.topology(fake_imy(7))
    def test_flags_cross_next_header_rejected(self):
        b = bytearray(fake_imy() + fake_imy());struct.pack_into('<H', b, 32, 100)
        with self.assertRaises(ValueError):mod.topology(bytes(b))
    def test_zero_flags_rejected(self):
        b = bytearray(fake_imy());struct.pack_into('<H', b, 32, 0)
        with self.assertRaises(ValueError):mod.topology(bytes(b))
    def test_truncated_header_rejected(self):
        with self.assertRaises(ValueError):mod.topology(b'IMY\x00bad')
    def test_private_report_only(self):
        with self.assertRaises(ValueError):mod.safe_report(Path('test.json'))
    def test_no_overwrite(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d)/'r.json';p.write_text('keep')
            with self.assertRaises(ValueError):mod.safe_report(p)
            self.assertEqual(p.read_text(),'keep')
    def test_no_git_inside(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d);(root/'.git').mkdir()
            with self.assertRaises(ValueError):mod.safe_report(root/'r.json')

if __name__ == '__main__':unittest.main()
