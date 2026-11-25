"""Solo mocks del protocolo y /proc: NO emulador PPSSPP ni ISO del juego."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools import f2_ppsspp_ws_1204 as ws
from tools import f2_iso_proceso_ppsspp as proc

EXPECTED=proc.SOURCE_SHA

def status(*,fd=True,exe=True,pid=42,start=123,iso='fingerprint'):
    return {'schema':'cladun.f2.procfs_open_iso_witness.v1',
            'pid':pid,'linux_start_ticks':start,
            'iso_device_inode_fingerprint':iso,
            'ppsspp_executable_name_hint':exe,
            'exact_iso_inode_open_at_snapshot':fd}

def verified(inode=5):
    return {'source_iso_sha256':EXPECTED,'expected_label':'USA_original',
            'inode':inode,'device':1}

class TestIntegratedCaptureEvidenceSynthetic(unittest.TestCase):
    def run_harness(self,before=None,after=None,validated=None):
        before=before or status();after=after or status()
        with patch.object(proc,'validate_iso',side_effect=validated or [verified(),verified()]) as auth,\
             patch.object(proc,'proc_snapshot',side_effect=[before,after]) as snap,\
             patch.object(ws,'capture',return_value={'screenshots':[{'name':'FAKE_SYNTHETIC.png'}]}) as cap:
            shots,proof=ws.capture_with_iso_witness(object(),'TEST',Path('/tmp/FAKE'),False,
                                                    42,Path('/tmp/FAKE.iso'),EXPECTED)
            return shots,proof,auth.call_count,snap.call_count,cap.call_count
    def test_normal_synthetic_run_distinguishes_loaded_iso(self):
        shots,proof,a,s,c=self.run_harness()
        self.assertEqual((a,s,c),(2,2,1))
        self.assertTrue(proof['paired']['same_inode_open_before_and_after'])
        self.assertFalse(proof['runtime_loaded_iso_identity_proven'])
        self.assertFalse(proof['websocket_server_pid_correlated'])
    def test_no_fd_never_disproves_iso(self):
        _,proof,_,_,_=self.run_harness(status(fd=False),status(fd=False))
        self.assertFalse(proof['paired']['same_inode_open_before_and_after'])
        self.assertTrue(proof['paired']['no_open_fd_does_not_disprove_loaded_iso'])
    def test_mixed_fd_observation(self):
        _,proof,_,_,_=self.run_harness(status(fd=True),status(fd=False))
        self.assertFalse(proof['paired']['same_inode_open_before_and_after'])
    def test_pid_switch_rejected(self):
        with self.assertRaises(ValueError):self.run_harness(status(),status(pid=43))
    def test_pid_reuse_rejected(self):
        with self.assertRaises(ValueError):self.run_harness(status(),status(start=999))
    def test_iso_inodenode_change_rejected(self):
        with self.assertRaises(ValueError):self.run_harness(status(),status(iso='new'))
    def test_wrong_executable_name_fails_before_capture(self):
        with patch.object(proc,'validate_iso',return_value=verified()),\
             patch.object(proc,'proc_snapshot',return_value=status(exe=False)),\
             patch.object(ws,'capture') as cap:
            with self.assertRaises(ValueError):
                ws.capture_with_iso_witness(object(),'TEST',Path('/tmp/FAKE'),False,
                                            42,Path('/tmp/FAKE.iso'),EXPECTED)
            cap.assert_not_called()
    def test_iso_changed_on_disk_rejected(self):
        with self.assertRaises(ValueError):
            self.run_harness(validated=[verified(5),verified(999)])
    def test_capture_failure_prevents_positive_manifest(self):
        with patch.object(proc,'validate_iso',return_value=verified()),\
             patch.object(proc,'proc_snapshot',return_value=status()) as snap,\
             patch.object(ws,'capture',side_effect=RuntimeError('synthetic capture failure')):
            with self.assertRaises(RuntimeError):
                ws.capture_with_iso_witness(object(),'TEST',Path('/tmp/FAKE'),False,
                                            42,Path('/tmp/FAKE.iso'),EXPECTED)
            self.assertEqual(snap.call_count,1)
    def test_false_gpu_or_mips_provenance(self):
        _,proof,_,_,_=self.run_harness()
        self.assertFalse(proof['mips_ram_ge_vram_proven'])

if __name__=='__main__':unittest.main()
