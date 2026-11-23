"""Synthetic procfs fixtures only. NO PPSSPP execution or gameplay."""
from pathlib import Path
import hashlib
import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import f2_iso_proceso_ppsspp as m

def sha(s): return hashlib.sha256(s).hexdigest()

def mkstat(ticks=123456,comm='ppsspp test) (bad'):
    fields=[b'S']+[b'0']*49
    fields[19]=str(ticks).encode()
    return b'502 ('+comm.encode()+b') '+b' '.join(fields)+b'\n'

class TestProcfileAudit(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.repo=self.root/'repo';self.repo.mkdir()
        self.iso=self.root/'original.iso';self.iso.write_bytes(b'MOCK ORIGINAL PSP')
        self.procs=self.root/'proc';self.pid=502
        self.directory=self.procs/str(self.pid)
        self.directory.mkdir(parents=True)
        (self.directory/'fd').mkdir()
        (self.directory/'exe').symlink_to('/opt/ppsspp/PPSSPPSDL')
        (self.directory/'stat').write_bytes(mkstat())
        (self.directory/'cmdline').write_bytes(b'PPSSPPSDL\0'+os.fsencode(str(self.iso))+b'\0')
        (self.directory/'fd'/'5').symlink_to(self.iso)
    def snapshot(self):return m.proc_snapshot(self.pid,self.iso,self.procs)
    def test_stat_parentheses(self):self.assertEqual(m.read_start_ticks(mkstat(123456)),123456)
    def test_stat_invalid(self):
        with self.assertRaises(ValueError):m.read_start_ticks(b'bad')
    def test_stat_truncated(self):
        with self.assertRaises(ValueError):m.read_start_ticks(b'502 (ppsspp) S 1 2')
    def test_stat_zero(self):
        with self.assertRaises(ValueError):m.read_start_ticks(mkstat(0))
    def test_exact_fd(self):
        r=self.snapshot()
        self.assertEqual(r['open_descriptor_count_to_exact_iso_inode'],1)
        self.assertTrue(r['argv_exact_iso_path_present'])
        self.assertFalse(r['loaded_game_iso_identity_proven'])
    def test_executable_hint_only(self):
        self.assertTrue(self.snapshot()['ppsspp_executable_name_hint'])
        self.assertFalse(self.snapshot()['websocket_server_pid_correlated'])
    def test_different_fd_content_same_size(self):
        other=self.root/'other.iso';other.write_bytes(b'X'*len(self.iso.read_bytes()))
        (self.directory/'fd'/'5').unlink();(self.directory/'fd'/'5').symlink_to(other)
        self.assertFalse(self.snapshot()['exact_iso_inode_open_at_snapshot'])
    def test_fd_symlink_alias_same_inode(self):
        alias=self.root/'alias.iso';os.link(self.iso,alias)
        (self.directory/'fd'/'5').unlink();(self.directory/'fd'/'5').symlink_to(alias)
        self.assertTrue(self.snapshot()['exact_iso_inode_open_at_snapshot'])
    def test_no_fd_unknown_not_negative_proof(self):
        (self.directory/'fd'/'5').unlink()
        self.assertFalse(self.snapshot()['exact_iso_inode_open_at_snapshot'])
        self.assertFalse(self.snapshot()['loaded_game_iso_identity_proven'])
    def test_not_substring_of_cmdline(self):
        (self.directory/'cmdline').write_bytes(b'PPSSPP\0'+os.fsencode(str(self.iso))+b'.other\0')
        self.assertFalse(self.snapshot()['argv_exact_iso_path_present'])
    def test_cmdline_too_big(self):
        (self.directory/'cmdline').write_bytes(b'A'*300000)
        with self.assertRaises(ValueError):self.snapshot()
    def test_missing_cmdline(self):
        (self.directory/'cmdline').write_bytes(b'')
        with self.assertRaises(ValueError):self.snapshot()
    def test_pid_reused_midway(self):
        counts=iter((123456,123457))
        with patch.object(m,'read_start_ticks',side_effect=lambda _:next(counts)):
            with self.assertRaises(RuntimeError):self.snapshot()
    def test_wrong_pid(self):
        for value in (0,-1,True):
            with self.assertRaises(ValueError):m.proc_snapshot(value,self.iso,self.procs)
    def test_pair_matching_positive_evidence_limited(self):
        a=self.snapshot();b=self.snapshot()
        r=m.paired_observations(a,b)
        self.assertTrue(r['same_inode_open_before_and_after'])
        self.assertFalse(r['is_conclusive_proof_of_loaded_iso'])
    def test_pair_no_open_fd(self):
        a=self.snapshot();(self.directory/'fd'/'5').unlink();b=self.snapshot()
        self.assertFalse(m.paired_observations(a,b)['same_inode_open_before_and_after'])
    def test_pair_different_pid_rejected(self):
        a=self.snapshot();b={**a,'pid':505}
        with self.assertRaises(ValueError):m.paired_observations(a,b)
    def test_pair_different_start_ticks_rejected(self):
        a=self.snapshot();b={**a,'linux_start_ticks':606}
        with self.assertRaises(ValueError):m.paired_observations(a,b)
    def test_pair_changed_iso_inode_rejected(self):
        a=self.snapshot();b={**a,'iso_device_inode_fingerprint':'another'}
        with self.assertRaises(ValueError):m.paired_observations(a,b)
    def test_pair_invalid_schema_rejected(self):
        a=self.snapshot();b={**a,'schema':'wrong'}
        with self.assertRaises(ValueError):m.paired_observations(a,b)
    def test_private_file_absolute(self):
        self.assertEqual(m.canonical_private_input(self.iso,self.repo),self.iso)
    def test_private_relative_denied(self):
        with self.assertRaises(ValueError):m.canonical_private_input(Path('original.iso'),self.repo)
    def test_private_symlink_denied(self):
        link=self.root/'link.iso';link.symlink_to(self.iso)
        with self.assertRaises(ValueError):m.canonical_private_input(link,self.repo)
    def test_inside_repo_denied(self):
        file=self.repo/'test.iso';file.write_bytes(b'DATA')
        with self.assertRaises(ValueError):m.canonical_private_input(file,self.repo)
    def test_inside_other_git_denied(self):
        (self.root/'.git').mkdir()
        with self.assertRaises(ValueError):m.canonical_private_input(self.iso,self.repo)
    def test_iso_reject_wrong_sha(self):
        with self.assertRaises(ValueError):m.validate_iso(self.iso,'0'*64,self.repo)
    def test_iso_reject_wrong_file_content(self):
        with self.assertRaises(ValueError):m.validate_iso(self.iso,m.SOURCE_SHA,self.repo)
    def test_iso_synthetic_validated_only_under_patching(self):
        with patch.object(m,'ISO_SIZE',self.iso.stat().st_size),patch.object(m,'SOURCE_SHA',sha(self.iso.read_bytes())):
            r=m.validate_iso(self.iso,sha(self.iso.read_bytes()),self.repo)
            self.assertEqual(r['source_iso_bytes'],len(self.iso.read_bytes()))
    def test_no_paths_in_snapshot(self):
        r=self.snapshot();s=str(r)
        self.assertNotIn(str(self.iso),s)
        self.assertNotIn(str(self.root),s)
    def test_no_real_runtime_claims(self):
        r=self.snapshot()
        self.assertFalse(r['gameplay_or_mips_ge_vram_proven'])
        self.assertFalse(r['iso_binary_hash_verified_by_snapshot'])

if __name__=='__main__':unittest.main()
