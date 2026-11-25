"""R24 slot risk gate (synthetic). Authentic no-op IMY test needs private ISO."""
import unittest
from tools.f4_r24_script_slot_audit import slot_safety

class TestR24ScriptSlot(unittest.TestCase):
 def test_real_record_geometry_baseline_recompression_does_not_fit(self):
  s=slot_safety(699624,10352128,9652224,700483)
  self.assertEqual(s["slot_bytes"],699904)
  self.assertEqual(s["excess_bytes"],579)
  self.assertFalse(s["can_write_inplace"])
  self.assertTrue(s["must_use_append_only"])
 def test_historical_stored_size_fits(self):
  s=slot_safety(699624,10352128,9652224,699624)
  self.assertTrue(s["can_write_inplace"])
 def test_equal_boundary_is_fitting(self):
  s=slot_safety(699624,10352128,9652224,699904)
  self.assertEqual(s["excess_bytes"],0)
  self.assertFalse(s["must_use_append_only"])
 def test_next_byte_overflow_rejected(self):
  s=slot_safety(699624,10352128,9652224,699905)
  self.assertEqual(s["excess_bytes"],1)
 def test_stored_larger_than_slot_rejected(self):
  with self.assertRaises(ValueError):
   slot_safety(699905,10352128,9652224,700000)
 def test_negative_offset_rejected(self):
  with self.assertRaises(ValueError):
   slot_safety(100,200,-1,100)
 def test_zero_storage_rejected(self):
  with self.assertRaises(ValueError):
   slot_safety(0,200,0,100)
 def test_zero_repack_rejected(self):
  with self.assertRaises(ValueError):
   slot_safety(100,200,0,0)
 def test_boolean_offset_rejected(self):
  with self.assertRaises(ValueError):
   slot_safety(100,200,True,100)
 def test_noninteger_size_rejected(self):
  with self.assertRaises(ValueError):
   slot_safety(100.0,200,0,100)
if __name__=="__main__":
 unittest.main()
