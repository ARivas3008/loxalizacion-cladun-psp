import json
from pathlib import Path
import unittest
from tools.g_r50_prologo_reinsercion import verify_text
ROOT=Path(__file__).resolve().parents[1]
class R50Prologue(unittest.TestCase):
    def test_current_user_text(self):
        r=json.loads((ROOT/"reports/G_R50_PROLOGO_CANONICO.json").read_text(encoding="utf-8"))
        text=verify_text(r).decode("utf-8")
        self.assertIn("puede hallarse",text)
        self.assertNotIn("puede ser hallarse",text)
        self.assertNotIn("Unos dicen",text)
        self.assertIn("«Arcanus cella».",text)
        self.assertEqual(len(text.splitlines()),8)
        self.assertEqual(r["unchanged_r49_encoded_hashes"],51)
        self.assertEqual(r["exact_encoded_hashes_replayed"],53)
        self.assertEqual(r["prologue"]["bytes_before"],r["prologue"]["bytes_after"])
        self.assertFalse(r["runtime_verified"])
        self.assertFalse(r["release_authorized"])
