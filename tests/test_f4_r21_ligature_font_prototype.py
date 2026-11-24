import struct,sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from f4_r21_ligature_font_prototype import (create_records,insert_raster_slots,INSERT,TOTAL)
from f4_r21_ligature_capacity import ASCII_LOWER_WIDTHS
PAIRS="es en de er ue ar ra os te qu nt do ta as el or la to st on lo re an al co un na ie ca ro ad me da in pa so pe ci se nd mo sa po ed".split()
def dummy_font():
 recs=[struct.pack("<HBB",code,0,7) for code in range(32,127)]
 recs += [struct.pack("<HBB",code,0,7) for code in range(0xA1,0xB4)]
 recs += [struct.pack("<HBB",0x8140+i,0,14) for i in range(2721-95)]
 return struct.pack("<I",2740)+b"".join(recs)
class Font63PrototypeTest(unittest.TestCase):
 def test_sorted_44_new_font_records(self):
  raw=create_records(dummy_font(),PAIRS)
  self.assertEqual(struct.unpack_from("<I",raw)[0],TOTAL)
  self.assertEqual(struct.unpack_from("<H",raw,4+INSERT*4)[0],0xB4)
  self.assertEqual(struct.unpack_from("<H",raw,4+(INSERT+43)*4)[0],0xDF)
 def test_base_records_unchanged(self):
  old=dummy_font();new=create_records(old,PAIRS)
  self.assertEqual(new[4:4+INSERT*4],old[4:4+INSERT*4])
  self.assertEqual(new[4+(INSERT+44)*4:],old[4+INSERT*4:])
 def test_reject_malformed_font_count(self):
  with self.assertRaises(ValueError):create_records(b"\x00"*64,PAIRS)
 def test_reject_inconsistent_dictionary(self):
  with self.assertRaises(ValueError):create_records(dummy_font(),["de"]*44)
 def test_atlas_44_new_pixels_and_preservation(self):
  # Make existing lowercase ASCII cells carry distinct ink away from clipping.
  old=[bytes(256) for _ in range(3072)]
  for c in "abcdefghijklmnopqrstuvwxyz":
   a=bytearray(256);a[1]=1;old[ord(c)-32]=bytes(a)
  new,stats=insert_raster_slots(old,PAIRS)
  self.assertEqual(stats["ligature_rasters"],44)
  self.assertEqual(len(new),3072)
  self.assertEqual(new[INSERT+44],old[INSERT])
  self.assertEqual(new[94],old[94])
 def test_reject_invalid_atlas_shape(self):
  with self.assertRaises(ValueError):insert_raster_slots([bytes(256)]*10,PAIRS)
if __name__=="__main__":unittest.main()
