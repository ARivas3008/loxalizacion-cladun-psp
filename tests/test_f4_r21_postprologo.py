"""R21: 20 additional post-prologue exact-width proposals, never approved."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from f4_r18_propuestas_globales import audit
from f3_propuestas_longitud_fija import read_proposals
from charset_es import encode_spanish,decode_spanish
P=ROOT/"traduccion"/"propuestas"/"SCRIPT_POSTPROLOGO_LONGITUD_FIJA_R21.csv"
class PostPrologueR21(unittest.TestCase):
 def test_canonical_git_geometry_and_widths(self):
  result=audit(ROOT/"traduccion"/"CLADUN_BORRADOR_ES.csv",P)
  self.assertEqual(result["overlay_count"],20)
  self.assertFalse(result["deployment_authorized"])
  self.assertFalse(result["canonical_modified"])
 def test_all_glyph_roundtrips(self):
  proposals=read_proposals(P)
  self.assertEqual(len({x["grupo_id"] for x in proposals}),20)
  for p in proposals:
   with self.subTest(gid=p["grupo_id"]):
    self.assertEqual(len(encode_spanish(p["propuesta_es"])),int(p["longitud_original_bytes"]))
    self.assertEqual(decode_spanish(encode_spanish(p["propuesta_es"])),p["propuesta_es"])
 def test_no_change_to_canonical(self):
  self.assertTrue(all(p["estado"]=="PROPUESTA_REVISION_NO_CANONICA" for p in read_proposals(P)))
if __name__=="__main__": unittest.main()
