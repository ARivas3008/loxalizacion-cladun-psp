import unittest
from tools.r29_integrar_longitud_fija import make_plan, run, SELECTED_R19, SELECTED_R20, SELECTED_R21, REPEAT

class R29FixedWidthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=make_plan()
    def test_exact_count(self):
        self.assertEqual(len(self.plan),56)
        self.assertEqual(len({x["offset"] for x in self.plan}),56)
    def test_byte_width_and_controls(self):
        for x in self.plan:
            self.assertEqual(len(x["old"]),len(x["new"]))
            self.assertNotEqual(x["old"],x["new"])
            self.assertNotIn(b"%",x["new"])
            self.assertNotIn(b"\\",x["new"])
            self.assertFalse(x["new"].endswith(b" "))
    def test_font_dependencies(self):
        self.assertEqual(sum(x["new"].isascii() for x in self.plan),16)
    def test_no_overlap(self):
        for a,b in zip(self.plan,self.plan[1:]):
            self.assertLessEqual(a["offset"]+len(a["old"]),b["offset"])
    def test_review_ids(self):
        self.assertEqual({x["gid"] for x in self.plan},SELECTED_R19|SELECTED_R20|SELECTED_R21|set(REPEAT))
        self.assertNotIn("000023",{x["gid"] for x in self.plan})
        self.assertNotIn("000031",{x["gid"] for x in self.plan})
    def test_no_runtime_claim(self):
        r=run()
        self.assertEqual(r["candidate_total_if_built"],3780)
        self.assertEqual(r["new_official_integrations"],0)
        self.assertFalse(r["release_authorized"])
        self.assertFalse(r["private_candidate_written"])
