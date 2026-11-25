import hashlib
import unittest
from collections import Counter
from tools.r31_bulk_padding import pool, make_plan, audit, fnv, serialized, GAPS, SHA_608
from tools.charset_es import decode_spanish

class R31Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.prior,cls.new=pool()
    def test_full_pool(self):
        self.assertEqual(len(self.new),1302)
        self.assertEqual(Counter(x["padding"] for x in self.new),GAPS)
        self.assertEqual(fnv(serialized(self.new,False)),1592949294)
        self.assertEqual(fnv(serialized(self.new)),1412021638)
    def test_real_608_digest(self):
        short=[x for x in self.new if x["padding"]<=2]
        self.assertEqual(len(short),608)
        self.assertEqual(hashlib.sha256(serialized(short)).hexdigest(),SHA_608)
        self.assertEqual(sum(x["padding"] for x in short),886)
    def test_pack_sizes(self):
        for pack,n in (("one",476),("two",424),("short",754),("long",840),("all",1448)):
            self.assertEqual(len(make_plan(pack=pack)),n)
    def test_nonoverlap_prior(self):
        self.assertFalse({x["gid"] for x in self.prior}&{x["gid"] for x in self.new})
        self.assertFalse({x["offset"] for x in self.prior}&{x["offset"] for x in self.new})
    def test_width_controls_and_padding(self):
        for x in self.new:
            self.assertEqual(len(x["old"]),len(x["new"]))
            self.assertNotEqual(x["old"],x["new"])
            self.assertNotIn(b"%",x["new"])
            self.assertNotIn(b"\\",x["new"])
            self.assertTrue(x["new"].endswith(b" "*x["padding"]))
            self.assertFalse(decode_spanish(x["new"][:-x["padding"]]).endswith(" "))
    def test_no_release_claim(self):
        self.assertEqual(audit()["cumulative_if_built"],4478)
        self.assertEqual(audit("all")["cumulative_if_built"],5172)
        self.assertEqual(audit()["official_new"],0)
        self.assertFalse(audit()["release_authorized"])
