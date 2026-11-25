"""Only fabricated metadata, no emulator screenshots or executable."""
import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from f2_cotejar_capturas_tuika import evidence_summary,USA_SHA,PROBE_SHA

def item(sha=USA_SHA,role='USA_original',fd=True):
    return {'schema':'cladun.f2.ppsspp_procfs_capture_corroboration.v1',
            'source_iso_sha256_verified_twice':sha,
            'source_iso_role':role,
            'runtime_loaded_iso_identity_proven':False,
            'paired':{'same_inode_open_before_and_after':fd,
                      'is_conclusive_proof_of_loaded_iso':False}}
class TestWitnessAB(unittest.TestCase):
    def test_legacy_synthetic_manifest_compatible(self):
        self.assertFalse(evidence_summary(None,USA_SHA,'USA_original')['manifest_has_procfs_witness'])
    def test_strict_roles(self):
        with self.assertRaises(ValueError):
            evidence_summary(item(),PROBE_SHA,'TUIKA_magenta_probe')
    def test_probe_witness_accepted_as_declaration_only(self):
        result=evidence_summary(item(PROBE_SHA,'TUIKA_magenta_probe'),PROBE_SHA,'TUIKA_magenta_probe')
        self.assertTrue(result['reported_fd_open_before_after'])
        self.assertFalse(result['loaded_game_iso_identity_proven'])
    def test_missing_fd_not_loaded_negative(self):
        result=evidence_summary(item(fd=False),USA_SHA,'USA_original')
        self.assertFalse(result['reported_fd_open_before_after'])
        self.assertFalse(result['loaded_game_iso_identity_proven'])
    def test_false_claim_of_loaded_iso_rejected(self):
        q=item();q['runtime_loaded_iso_identity_proven']=True
        with self.assertRaises(ValueError):evidence_summary(q,USA_SHA,'USA_original')
    def test_false_claim_in_pair_rejected(self):
        q=item();q['paired']['is_conclusive_proof_of_loaded_iso']=True
        with self.assertRaises(ValueError):evidence_summary(q,USA_SHA,'USA_original')
    def test_hash_mismatch_rejected(self):
        q=item();q['source_iso_sha256_verified_twice']='0'*64
        with self.assertRaises(ValueError):evidence_summary(q,USA_SHA,'USA_original')
    def test_malformed_manifest_rejected(self):
        for q in ({'schema':'wrong'},['list'],'not an object'):
            with self.assertRaises(ValueError):evidence_summary(q,USA_SHA,'USA_original')
    def test_missing_pair_rejected(self):
        q=item();q.pop('paired')
        with self.assertRaises(ValueError):evidence_summary(q,USA_SHA,'USA_original')

if __name__=='__main__':unittest.main()
