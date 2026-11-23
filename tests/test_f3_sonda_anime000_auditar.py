"""Synthetic tests; do NOT make game ISO edits in CI."""
from pathlib import Path
from io import BytesIO
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import f3_sonda_anime000_auditar as f3

class TestF3Anime000Guard(unittest.TestCase):
    def test_one_diff(self):
        a=BytesIO(b'ABCD');b=BytesIO(b'ABXD')
        self.assertEqual(f3.differences_stream(a,b),([2],1))
    def test_no_diff(self):
        self.assertEqual(f3.differences_stream(BytesIO(b'123'),BytesIO(b'123')),([],0))
    def test_multiple_diffs(self):
        self.assertEqual(f3.differences_stream(BytesIO(b'ABC'),BytesIO(b'XXX')),([0,1],3))
    def test_diff_length_rejected(self):
        with self.assertRaises(ValueError):f3.differences_stream(BytesIO(b'12'),BytesIO(b'123'))
    def test_name_parser(self):
        self.assertEqual(f3.inspect_named_entry(BytesIO(b'ANIME000.IDT'+b'\0'*8),0),f3.OLD_NAME)
    def test_name_length_rejected(self):
        with self.assertRaises(ValueError):f3.inspect_named_entry(BytesIO(b'BAD'+b'\0'*17),0)
    def test_index_geometry(self):
        self.assertEqual(f3.PSPFS_NAME_OFF,113778000)
        self.assertEqual(f3.SINGLE_CHANGED_BYTE_OFF,113778009)
    def test_synthetic_verified_report(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'a.iso';b=Path(d)/'b.iso'
            offset=f3.SINGLE_CHANGED_BYTE_OFF
            size=offset+100
            # Sparse files: no game artwork and no actual game ISO source.
            with a.open('wb') as out:
                out.seek(size-1);out.write(b'\0')
            with a.open('r+b') as out:
                out.seek(f3.DATA_OFFSET);out.write(b'PSPFS_V1')
                out.seek(f3.PSPFS_NAME_OFF);out.write(f3.OLD_NAME+b'\0'*8)
            b.write_bytes(a.read_bytes())
            with b.open('r+b') as out:
                out.seek(f3.SINGLE_CHANGED_BYTE_OFF);out.write(b'X')
            with patch.object(f3,'ISO_SIZE',size),patch.object(f3,'SOURCE_SHA',f3.hash_file(a)),patch.object(f3,'PROBE_SHA',f3.hash_file(b)):
                result=f3.audit(a,b)
            self.assertEqual(result['total_binary_byte_differences'],1)
            self.assertFalse(result['actual_prologue_text_source_identified'])
    def test_file_same_object_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            a=Path(d)/'same.iso';a.write_bytes(b'test')
            with self.assertRaises(ValueError):f3.audit(a,a)
    def test_path_relative(self):
        with self.assertRaises(ValueError):f3.validate_report_path(Path('diag.json'))
    def test_path_inside_repo(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            with self.assertRaises(ValueError):f3.validate_report_path(root/'diag.json',root)
    def test_path_existing(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);target=root/'x.json';target.write_text('keep')
            with self.assertRaises(ValueError):f3.validate_report_path(target,root/'repo')
    def test_path_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);link=root/'link.json';link.symlink_to(root/'missing')
            with self.assertRaises(ValueError):f3.validate_report_path(link,root/'repo')
    def test_path_git_elsewhere(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);(root/'.git').mkdir()
            with self.assertRaises(ValueError):f3.validate_report_path(root/'x.json',root/'repo')

if __name__=='__main__':unittest.main()
