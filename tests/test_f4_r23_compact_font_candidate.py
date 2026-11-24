"""R23 synthetic security regressions. A synthetic fixture is NOT game evidence C."""
import copy
import struct
import tempfile
import unittest
from pathlib import Path
from tools.f4_r21_ligature_font_prototype import compact_member_offset, slot_safety
from tools.f4_r23_font_compact_candidate import audit_pspfs_isolation, candidate_path

RECORDS=349
FONT_IDX=308
FONT_OFFSET=11776
FONT_OLD=143888
FONT_NEW=144000
NEXT=156160
SIZE=180000
META=16+FONT_IDX*32+24

def fixture():
 orig=bytearray(SIZE)
 orig[:8]=b"PSPFS_V1"
 struct.pack_into("<I",orig,8,RECORDS)
 records=[]
 for i in range(RECORDS):
  if i==FONT_IDX:
   name,off,stored="FONT.ARC",FONT_OFFSET,FONT_OLD
  elif i==0:
   name,off,stored="SE.ARC",NEXT,16
  else:
   name,off,stored=f"FILE{i:03d}",156192+i*32,16
  table=16+32*i
  orig[table:table+20]=name.encode().ljust(20,b"\0")
  struct.pack_into("<III",orig,table+20,0,stored,off)
  if i!=FONT_IDX:orig[off:off+stored]=bytes([1+i%250])*stored
  records.append((name,off,stored))
 orig[FONT_OFFSET:FONT_OFFSET+FONT_OLD]=b"x"*FONT_OLD
 new=bytearray(orig)
 arc=bytearray(FONT_NEW)
 arc[:8]=b"DSARCIDX";struct.pack_into("<I",arc,8,7)
 base=32
 font_codes=list(range(32,127))+list(range(0xA1,0xE0))+list(range(0x8140,0x8140+2626))
 assert len(font_codes)==2784
 fontbin=struct.pack("<I",len(font_codes))+b"".join(struct.pack("<HBB",c,0,7) for c in font_codes)
 for i in range(7):
  row=base+i*48
  name="FONT.BIN" if i==0 else f"FONT_{i-1:02d}.IMY"
  arc[row:row+40]=name.encode().ljust(40,b"\0")
  offset=528 if i==0 else 12000+(i-1)*32
  contents=fontbin if i==0 else b"IMY\0"+bytes(12)
  struct.pack_into("<II",arc,row+40,len(contents),offset)
  arc[offset:offset+len(contents)]=contents
 struct.pack_into("<I",new,META,FONT_NEW)
 new[FONT_OFFSET:FONT_OFFSET+FONT_NEW]=arc
 return bytes(orig),bytes(new),bytes(arc),records

class CompactFontPilotSecurityTests(unittest.TestCase):
 def test_historial_512_layout(self):
  self.assertEqual(compact_member_offset(11700,512),11792)
 def test_packing_16_is_aligned(self):
  for end in range(11700,11770,7):
   p=compact_member_offset(end,16)
   self.assertGreaterEqual(p,end+16)
   self.assertEqual((p-16)%16,0)
 def test_bad_alignment_rejected(self):
  for a in (0,1,15,17,255,1024,-16):
   with self.subTest(a=a),self.assertRaises(ValueError):
    compact_member_offset(12000,a)
 def test_source_real_geometry_fits_compact_44_only(self):
  old=slot_safety(143888,145696,496)
  new=slot_safety(143888,144000,496)
  self.assertFalse(old["can_write_in_place"])
  self.assertTrue(new["can_write_in_place"])
  self.assertEqual(new["maximum_in_place_arc_bytes"]-144000,384)
 def test_isolation_fixture_accepted(self):
  old,new,arc,records=fixture()
  m=audit_pspfs_isolation(old,new,arc)
  self.assertEqual(m["other_resources_byte_exact"],348)
  self.assertEqual(m["spanish_codes"],19)
  self.assertEqual(m["ligature_codes"],44)
 def test_neighbor_payload_mutation_rejected(self):
  old,new,arc,records=fixture()
  b=bytearray(new);b[NEXT]^=1
  with self.assertRaises(ValueError):
   audit_pspfs_isolation(old,bytes(b),arc)
 def test_other_resource_offset_mutation_rejected(self):
  old,new,arc,records=fixture()
  b=bytearray(new);struct.pack_into("<I",b,16+0*32+28,NEXT+32)
  with self.assertRaises(ValueError):
   audit_pspfs_isolation(old,bytes(b),arc)
 def test_font_table_size_mutation_rejected(self):
  old,new,arc,records=fixture()
  b=bytearray(new);struct.pack_into("<I",b,META,FONT_NEW+16)
  with self.assertRaises(ValueError):
   audit_pspfs_isolation(old,bytes(b),arc)
 def test_nonzero_margin_rejected(self):
  old,new,arc,records=fixture()
  b=bytearray(new);b[FONT_OFFSET+FONT_NEW]=255
  with self.assertRaises(ValueError):
   audit_pspfs_isolation(old,bytes(b),arc)
 def test_reject_colliding_codebook_records(self):
  old,new,arc,records=fixture()
  broken=bytearray(arc)
  # Two codepoints A1 instead of A1,A2.
  struct.pack_into("<H",broken,528+4+4*96,0xA1)
  b=bytearray(new);b[FONT_OFFSET:FONT_OFFSET+FONT_NEW]=broken
  with self.assertRaises(ValueError):
   audit_pspfs_isolation(old,bytes(b),bytes(broken))
 def test_private_destination_must_be_new_absolute_path(self):
  with tempfile.TemporaryDirectory() as d:
   origin=Path(d)/"original.iso";origin.write_bytes(b"test")
   with self.assertRaises(ValueError):
    candidate_path(Path("relative.iso"),origin)
   with self.assertRaises(ValueError):
    candidate_path(origin,origin)
   with self.assertRaises(ValueError):
    candidate_path(Path(d),origin)
 def test_tampered_dsarc_child_offset_rejected(self):
  old,new,arc,records=fixture()
  broken=bytearray(arc)
  struct.pack_into("<I",broken,32+1*48+44,12001)
  b=bytearray(new);b[FONT_OFFSET:FONT_OFFSET+FONT_NEW]=broken
  with self.assertRaises(ValueError):
   audit_pspfs_isolation(old,bytes(b),bytes(broken))

if __name__=="__main__":
 unittest.main()
