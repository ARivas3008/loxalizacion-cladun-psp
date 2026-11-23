"""Synthetic X11 metadata checks; never need ISO, X11 or game images."""
import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from f2_x11_ppsspp_procfs_capture import verify_window_metadata,checked_output

class TestX11Metadata(unittest.TestCase):
 def test_valid(self):
  data=verify_window_metadata(99,99,'NPUH10072 : CLADUN: This is an RPG!',960,544,160,88)
  self.assertEqual(data['window_pid'],99)
  self.assertTrue(data['window_size_960x544'])
 def test_invalid_pid(self):
  with self.assertRaises(ValueError):verify_window_metadata(99,98,'NPUH10072 : CLADUN',960,544,160,88)
 def test_invalid_game(self):
  with self.assertRaises(ValueError):verify_window_metadata(99,99,'Other game',960,544,160,88)
 def test_invalid_size(self):
  with self.assertRaises(ValueError):verify_window_metadata(99,99,'NPUH10072 : CLADUN',480,272,160,88)
 def test_negative_location(self):
  with self.assertRaises(ValueError):verify_window_metadata(99,99,'NPUH10072 : CLADUN',960,544,-1,88)
 def test_reject_checkout_output(self):
  repo=Path(__file__).resolve().parents[1]
  with self.assertRaises(ValueError):checked_output(repo/'bad.png',repo)
 def test_reject_other_suffix(self):
  repo=Path(__file__).resolve().parents[1]
  with self.assertRaises(ValueError):checked_output(Path('/tmp/evidence.txt'),repo)

if __name__=='__main__':unittest.main()
