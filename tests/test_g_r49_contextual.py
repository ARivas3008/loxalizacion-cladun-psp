import hashlib
import json
from pathlib import Path
import unittest
from tools.g_r49_prologo_reinsercion import apply_delta

ROOT=Path(__file__).resolve().parents[1]
class R49ContextualGraphics(unittest.TestCase):
    def test_guarded_delta(self):
        a=b"abc";d=bytes([0,1,0]);b=b"acc"
        h=lambda x:hashlib.sha256(x).hexdigest()
        self.assertEqual(apply_delta(a,d,h(a),h(b)),b)
        for bad in (b"x",b"zzz",bytes(3)):
            with self.assertRaises(ValueError):apply_delta(a,bad,h(a),h(b))
    def test_evidence_boundaries(self):
        r=json.loads((ROOT/"reports/G_R49_EDICION_CONTEXTUAL.json").read_text(encoding="utf-8"))
        self.assertEqual(sum(r["groups"].values()),r["edited"])
        self.assertEqual(r["edited"],53)
        self.assertEqual(r["known_edit_targets"],53)
        self.assertEqual(r["independent_replay_exact_encoded_sha256"],53)
        self.assertEqual(r["growth_resources"]+r["same_size"]+r["shrinking_resources"],53)
        self.assertEqual(sum(r["remaining"].values()),322)
        self.assertFalse(r["all_426_surfaces_final_classified"])
        self.assertFalse(r["runtime_verified"])
        self.assertFalse(r["release_authorized"])
        q=r["prologue"]
        self.assertEqual(q["bytes_before"],q["bytes_after"])
        self.assertEqual(q["absolute_iso_offset"],113770496+3386368+3417360)
        self.assertEqual(hashlib.sha256(("\n".join(q["text"])+"\n").encode()).hexdigest(),q["text_sha256"])
        self.assertEqual(q["text"][5:8],["Cualquiera puede llegar a ese lugar,","pero está conectado con muchos otros lugares.","A ese mundo lo llaman «Arcanus Cella»."])
        self.assertEqual(q["unrelated_pspfs_exact"],348)
        self.assertEqual(q["unrelated_idt_surfaces_exact"],230)
        self.assertFalse(q["ppsspp_verified"])
if __name__=="__main__":unittest.main()
