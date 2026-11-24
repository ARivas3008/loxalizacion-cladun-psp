"""Synthetic metadata tests; they do not prove graphics visually translated."""
import unittest
from tools.r23_pspfs_graphics_inventory import extension,candidate,inventory_records

def fixture():
 return [
  {"index":i,"name":f"MAP{i:03d}.DMD","size_stored":200+i}
  for i in range(349)
 ]

class TestR23GraphicsInventory(unittest.TestCase):
 def test_extensions(self):
  self.assertEqual(extension("FOO.MPB"),"MPB")
  self.assertEqual(extension("FOO.mpb"),"MPB")
 def test_invalid_name(self):
  for v in ("FOO","",3):
   with self.subTest(v=v),self.assertRaises(ValueError):
    extension(v)
 def test_selects_graphics_primary_families(self):
  for name in ("TITLE.MPB","ANIME000.IDT","ANIME001.LDT",
               "FONT.ARC","SYSGRA.ARC"):
   self.assertTrue(candidate(name),name)
 def test_does_not_assume_every_archive_is_graphics(self):
  for name in ("SE.ARC","SCRIPT.SDT","SOUND.SPS","MAP001.DMD"):
   self.assertFalse(candidate(name),name)
 def test_valid_synthetic_metadata_not_runtime(self):
  result=inventory_records(fixture(),verify_original=False)
  self.assertEqual(result["first_pass_graphic_family_candidates"],0)
  self.assertFalse(result["graphics_full_inventory_complete"])
  self.assertIsNone(result["graphics_edit_completion_percent"])
 def test_graphics_potential_not_total(self):
  rows=fixture();rows[0]["name"]="TITLE.MPB"
  result=inventory_records(rows,verify_original=False)
  self.assertEqual(result["first_pass_graphic_family_candidates"],1)
  self.assertEqual(result["candidate_members"][0]["index"],0)
  self.assertTrue(result["graphic_candidates_are_not_total_graphics"])
 def test_reject_wrong_record_count(self):
  with self.assertRaises(ValueError):
   inventory_records(fixture()[:-1],verify_original=False)
 def test_reject_index_shift(self):
  rows=fixture();rows[10]["index"]=999
  with self.assertRaises(ValueError):
   inventory_records(rows,verify_original=False)
 def test_reject_duplicated_name(self):
  rows=fixture();rows[10]["name"]=rows[9]["name"]
  with self.assertRaises(ValueError):
   inventory_records(rows,verify_original=False)
 def test_reject_fabricated_original(self):
  with self.assertRaises(ValueError):
   inventory_records(fixture(),verify_original=True)

if __name__=="__main__":
 unittest.main()
