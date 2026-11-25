import unittest
from tools.r30_integrar_repeticiones import make_plan,run,select,RULES
from tools.r29_integrar_longitud_fija import make_plan as r29_plan,DRAFT
from tools.f4_r21_ligature_capacity import read_canonical

class R30Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan=make_plan()
    def test_inventory(self):
        self.assertEqual(len(self.plan),146)
        self.assertEqual(len(RULES),12)
        self.assertEqual(sum(x[3] for x in RULES),90)
    def test_r29_unchanged(self):
        old={x["gid"]:x for x in r29_plan()}
        now={x["gid"]:x for x in self.plan}
        self.assertEqual({k:now[k] for k in old},old)
    def test_width_and_no_controls(self):
        for x in self.plan:
            self.assertEqual(len(x["new"]),len(x["old"]))
            self.assertNotEqual(x["new"],x["old"])
            self.assertNotIn(b"%",x["new"])
            self.assertNotIn(b"\\",x["new"])
            self.assertFalse(x["new"].endswith(b" "))
    def test_font_count(self):
        self.assertEqual(sum(x["new"].isascii() for x in self.plan),26)
    def test_distinct(self):
        self.assertEqual(len({x["gid"] for x in self.plan}),146)
        self.assertEqual(len({x["offset"] for x in self.plan}),146)
    def test_rule_drift_rejected(self):
        rows=read_canonical(DRAFT)
        row=next(x for x in rows if x["original"]==RULES[0][0] and x["espanol"]==RULES[0][1] and x["origen"]=="SCRIPT.SDT/SCRIPT.DAT")
        row["espanol"]="alteración"
        with self.assertRaises(ValueError):
            select(rows)
    def test_no_release_claim(self):
        r=run()
        self.assertEqual(r["candidate_total_if_built"],3870)
        self.assertEqual(r["new_official_integrations"],0)
        self.assertFalse(r["private_candidate_written"])
        self.assertFalse(r["release_authorized"])
