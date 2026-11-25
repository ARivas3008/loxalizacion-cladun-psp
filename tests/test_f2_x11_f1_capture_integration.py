"""Synthetic-only F1 X11 capture integration; no ISO, PPSSPP or commercial pixels."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from PIL import Image
from tools import f2_x11_ppsspp_procfs_capture as m

class TestX11F1CaptureIntegration(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / 'fake_git_repo'
        self.repo.mkdir()
        self.iso = self.root / 'fake.iso'
        self.path = self.root / 'evidence.png'
        self.meta = {'x':160,'y':88,'width':960,'height':544,
                     'window_pid':200,'window_title_is_cladun':True,
                     'window_size_960x544':True}
        self.validate_calls = []

    def synthetic_capture(self, role='f1', filename=None):
        def validate(iso, expected):
            self.validate_calls.append(expected)
            return {'inode':123, 'device':1, 'source_iso_sha256':expected}
        with (patch.object(m, 'validate_iso', side_effect=validate),
              patch.object(m, 'proc_snapshot', return_value={'pid':200}),
              patch.object(m, 'find_window', return_value=self.meta),
              patch.object(m, 'paired_observations', return_value={'pid_starttime_stable':True}),
              patch('PIL.ImageGrab.grab', return_value=Image.new('RGB',(960,544),'black'))):
            return m.capture(':99',200,self.iso,role,filename or self.path,self.repo)

    def test_f1_calls_approved_sha_twice(self):
        r = self.synthetic_capture()
        self.assertEqual(self.validate_calls,[m.F1_SHA,m.F1_SHA])
        self.assertTrue(self.path.exists())
        self.assertEqual(r['source_iso_role'],'f1')
        self.assertFalse(r['this_is_psp_framebuffer'])
        self.assertFalse(r['mips_ram_ge_vram_proven'])

    def test_usa_sha_unchanged(self):
        self.synthetic_capture('usa')
        self.assertEqual(self.validate_calls,[m.SOURCE_SHA,m.SOURCE_SHA])

    def test_probe_sha_unchanged(self):
        self.synthetic_capture('sonda')
        self.assertEqual(self.validate_calls,[m.PROBE_SHA,m.PROBE_SHA])

    def test_unknown_role_rejected(self):
        with self.assertRaises(ValueError):
            self.synthetic_capture('experimental')
        self.assertEqual(self.validate_calls,[])

    def test_existing_file_preserved(self):
        self.path.write_bytes(b'NO OVERWRITE')
        with self.assertRaises(FileExistsError):
            self.synthetic_capture()
        self.assertEqual(self.path.read_bytes(),b'NO OVERWRITE')

if __name__=='__main__':
    unittest.main()
