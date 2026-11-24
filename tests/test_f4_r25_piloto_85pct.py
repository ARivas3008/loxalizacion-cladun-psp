"""R25: 7,024 prototype guards (without ISO) and explicit visual non-approval."""
import csv
from pathlib import Path
import unittest
from tools.f4_r25_piloto_85pct import (
 BASE_INTEGRATED,BASE_DEFERRED,TOTAL_PLANNED,
 TARGET_NEW,GROWING_44,SHORTENED_PADDED,MAX_PAD,TARGET_COMBINED,
 pad_shorter,choose_3300
)
from tools.f4_r21_ligature_capacity import read_canonical
from tools.charset_es import decode_spanish

ROOT=Path(__file__).resolve().parents[1]
CORPUS=ROOT/"traduccion/CLADUN_BORRADOR_ES.csv"
SHORT_MANIFEST=ROOT/"traduccion/propuestas/R25_COLA_EDITORIAL_1298.csv"

def entry(text="Hola",old=b"HELLO!"):
 return {
  "origen":"SCRIPT.SDT/SCRIPT.DAT","espanol":text,"grupo_id":"demo",
  "offset_hex":"0x100","bytes_hex":old.hex()
 }

class TestR25Pilot(unittest.TestCase):
 def test_absolute_target(self):
  self.assertEqual(BASE_INTEGRATED+TARGET_NEW,TARGET_COMBINED)
  self.assertEqual((BASE_INTEGRATED,BASE_DEFERRED,TOTAL_PLANNED),
                   (3724,4524,8248))
  self.assertEqual(GROWING_44+SHORTENED_PADDED,TARGET_NEW)
  self.assertGreater(100*TARGET_COMBINED/TOTAL_PLANNED,85)
 def test_shorter_ascii_pad_is_fixed_width(self):
  p=pad_shorter(entry())
  self.assertIsNotNone(p)
  self.assertEqual(p["old"],b"HELLO!")
  self.assertEqual(p["new"],b"Hola  ")
  self.assertEqual(p["padding"],2)
  self.assertEqual(decode_spanish(p["new"]).rstrip(" "), "Hola")
 def test_shorter_spanish_accents_are_reversible(self):
  p=pad_shorter(entry("¿Sí?",b"HELLO!"))
  self.assertIsNotNone(p)
  self.assertEqual(len(p["new"]),len(p["old"]))
  self.assertEqual(decode_spanish(p["new"]), "¿Sí?  ")
 def test_not_larger_or_same_width(self):
  self.assertIsNone(pad_shorter(entry("Long Text",b"SHORT")))
  self.assertIsNone(pad_shorter(entry("Hola",b"ABCD")))
 def test_no_nonascii_source_byte(self):
  self.assertIsNone(pad_shorter(entry("Sí",b"\x81\x40\x81\x40")))
 def test_no_original_percent_control(self):
  self.assertIsNone(pad_shorter(entry("Hola",b"HELLO%")))
 def test_no_original_backslash_control(self):
  self.assertIsNone(pad_shorter(entry("Hola",b"HELLO\\")))
 def test_no_new_percent_or_backslash(self):
  self.assertIsNone(pad_shorter(entry("Hola%",b"HELLO WORLD")))
  self.assertIsNone(pad_shorter(entry("Hola\\",b"HELLO WORLD")))
 def test_no_original_outside_script(self):
  a=entry();a["origen"]="DATABASE.DAT/STRTBL.DAT"
  self.assertIsNone(pad_shorter(a))
 def test_no_trailing_space_before_padding(self):
  self.assertIsNone(pad_shorter(entry("Hola ",b"HELLO!")))
 def test_no_multiline_or_nonprintable(self):
  self.assertIsNone(pad_shorter(entry("Ho\nla",b"HELLO!")))
 def test_no_more_than_seven_space_padding(self):
  self.assertIsNone(pad_shorter(entry("Hola",b"abcdefghijklm")))
 def test_exactly_seven_spaces_possible(self):
  p=pad_shorter(entry("Hola",b"ABCDEFGHIJK"))
  self.assertEqual(p["padding"],MAX_PAD)
  self.assertEqual(p["new"],b"Hola       ")
 def test_source_text_not_approvable_without_visual(self):
  rows=read_canonical(CORPUS)
  selected,r=choose_3300(rows)
  self.assertEqual(len(selected),3300)
  self.assertEqual(r["strict_ligatures_44_pool"],2002)
  self.assertGreaterEqual(r["shorter_safe_pool_with_gap_le_7"],1298)
  self.assertEqual(r["selected_shorter_new"],1298)
  self.assertEqual(r["selected_growing_new"],2002)
  self.assertEqual(r["target_cumulative_binary_candidates"],7024)
  self.assertEqual(r["new_official_integrations"],0)
  self.assertFalse(r["trailing_whitespace_visual_approved"])
  self.assertFalse(r["font_runtime_approved"])
  self.assertFalse(r["gameplay_C_approved"])
  self.assertEqual(len({r["group_id"] for r in selected}),3300)
  self.assertEqual(len({r["offset"] for r in selected}),3300)
  self.assertTrue(all(len(r["old"])==len(r["new"]) for r in selected))
 def test_shorter_selected_have_bounded_visual_risk(self):
  selected,r=choose_3300(read_canonical(CORPUS))
  pads=[x for x in selected if x["padding"]>0]
  self.assertEqual(len(pads),1298)
  self.assertEqual(max(x["padding"] for x in pads),7)
  self.assertTrue(all(x["new"].endswith(b" "*x["padding"]) for x in pads))
  self.assertTrue(all(x["method"]==
    "TRAILING_ASCII_SPACES_VISUALLY_UNVERIFIED" for x in pads))
 def test_fail_if_canonical_manifest_not_identical(self):
  chosen,_=choose_3300(read_canonical(CORPUS))
  shorten=sorted((x for x in chosen if x["padding"]>0),
                 key=lambda z:(z["padding"],z["offset"],z["group_id"]))
  with SHORT_MANIFEST.open(encoding="utf-8",newline="") as f:
   records=list(csv.DictReader(f))
  self.assertEqual(len(records),1298)
  self.assertEqual(len(shorten),1298)
  for text,selected in zip(records,shorten):
   self.assertEqual(text["grupo_id"],selected["group_id"])
   self.assertEqual(int(text["offset_hex"],16),selected["offset"])
   self.assertEqual(int(text["bytes_origen"]),selected["bytes"])
   self.assertEqual(int(text["espacios_experimentales"]),selected["padding"])
   self.assertEqual(text["dictamen_editorial"],"PENDIENTE_CONTEXTUAL")
   self.assertEqual(text["verificacion_ppsspp"],"NOT_RUN")
   self.assertEqual(text["integracion_canonica"],"NO")
if __name__=="__main__": unittest.main()
