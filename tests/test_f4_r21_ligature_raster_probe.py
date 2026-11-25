import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from f4_r21_ligature_raster_probe import combine_two_cells

def cell(points):
 result=bytearray(256)
 for x,y,value in points:result[y*16+x]=value
 return bytes(result)
class LigatureRasterTest(unittest.TestCase):
 def test_nonoverlapping_letters(self):
  first=cell([(0,2,9),(3,2,9)])
  second=cell([(1,2,4),(4,2,4)])
  raw,stats=combine_two_cells(first,second,7,7)
  self.assertEqual(raw[2*16+8],4)
  self.assertEqual(stats["overlap_pixels"],0)
  self.assertEqual(stats["composed_advance"],14)
 def test_source_not_modified(self):
  first=cell([(0,0,1)]);second=cell([(0,0,2)])
  before=first+second
  combine_two_cells(first,second,7,7)
  self.assertEqual(first+second,before)
 def test_fails_on_overlap(self):
  first=cell([(8,3,4)]);second=cell([(1,3,9)])
  with self.assertRaisesRegex(ValueError,"overlap"):combine_two_cells(first,second,7,7)
 def test_fails_on_clipping(self):
  first=cell([(0,3,4)]);second=cell([(15,3,9)])
  with self.assertRaisesRegex(ValueError,"clipped"):combine_two_cells(first,second,7,7)
 def test_fails_on_unfittable_metrics(self):
  with self.assertRaises(ValueError):combine_two_cells(bytes(256),bytes(256),8,8)
 def test_fails_on_bad_nibble(self):
  with self.assertRaises(ValueError):combine_two_cells(bytes([16])+bytes(255),bytes(256),7,7)
 def test_fails_on_bad_cell_size(self):
  with self.assertRaises(ValueError):combine_two_cells(bytes(255),bytes(256),7,7)
if __name__=="__main__":unittest.main()
