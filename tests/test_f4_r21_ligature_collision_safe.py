"""A-backed collision blacklist in the 44-pair text compressor."""
import sys,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"tools"))
from f4_r21_ligature_collision_safe import (
  COLLIDING_PAIRS,COLLISION_FREE_PAIRS,VALID_METRIC_PAIRS,
  analyze_collision_free)
from f4_r21_ligature_capacity import read_canonical,encode_fixed,decode_encoded

class NoOverlapCodebookTest(unittest.TestCase):
 def test_151_real_font_raster_conflicts_are_excluded(self):
  self.assertEqual((len(VALID_METRIC_PAIRS),len(COLLIDING_PAIRS),len(COLLISION_FREE_PAIRS)),(672,151,521))
  self.assertIn("ue",COLLIDING_PAIRS)
  self.assertIn("la",COLLIDING_PAIRS)
  self.assertIn("in",COLLIDING_PAIRS)
  self.assertNotIn("de",COLLIDING_PAIRS)
 def test_actual_corpus_strict_coverage(self):
  rows=read_canonical(ROOT/"traduccion/CLADUN_BORRADOR_ES.csv")
  summary=analyze_collision_free(rows,samples=12)
  self.assertEqual(summary["theoretically_fittable"],2042)
  self.assertEqual(summary["strict_candidates"],2002)
  self.assertEqual(summary["strict_candidate_payload_bytes"],61723)
  self.assertEqual(summary["strict_exclusions"],40)
  self.assertEqual(len(summary["pairs"]),44)
  self.assertTrue(set(summary["pairs"])<=COLLISION_FREE_PAIRS)
  self.assertFalse(summary["deployment_authorized"])
 def test_real_text_roundtrip_with_safe_dictionary(self):
  rows=read_canonical(ROOT/"traduccion/CLADUN_BORRADOR_ES.csv")
  report=analyze_collision_free(rows)
  pairs=report["pairs"]
  text="Debes entrar de nuevo"
  from charset_es import encode_spanish
  src_len=len(encode_spanish(text))-1
  encoded=encode_fixed(text,src_len,pairs)
  self.assertEqual(len(encoded),src_len)
  self.assertEqual(decode_encoded(encoded,pairs),text)
 def test_hash_is_stable_and_not_a_game_resource(self):
  rows=read_canonical(ROOT/"traduccion/CLADUN_BORRADOR_ES.csv")
  report=analyze_collision_free(rows)
  self.assertEqual(len(report["codebook_sha256"]),64)
  self.assertEqual(report["candidate_pairs_with_15px_budget"],672)
if __name__=="__main__":unittest.main()
