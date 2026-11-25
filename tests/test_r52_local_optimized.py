import unittest
from test_r44_local_experimental import R44Tests
from tools.integrar_parche_seguro import combine_r44_local_experimental,TARGET_SCRIPT
from tools.r52_local_optimized import DONOR_IDS, audit
from tools.r44_local_experimental import IDS
from tools.f4_r21_ligature_capacity import decode_encoded
from tools.r35_ligaduras_acumuladas import PAIRS

class R52Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        R44Tests.setUpClass()
        cls.prior=R44Tests.r43
        cls.current=combine_r44_local_experimental(*cls.prior,optimized=True)
    def test_optimized_total_plan(self):
        c,b,d,i=self.current
        self.assertEqual(sum(map(len,c.values())),8247)
        self.assertEqual(len(c[TARGET_SCRIPT]),4899)
        self.assertEqual(d,[])
        self.assertEqual(i["resolved_original_target"],8248)
        self.assertFalse(i["local_relocation_experimental"]["fixed_offsets"])
        self.assertFalse(i["local_relocation_experimental"]["release_authorized"])
        old={r["grupo_id"]:(a,z) for r,a,z in self.prior[0][TARGET_SCRIPT]}
        new={r["grupo_id"]:(a,z) for r,a,z in c[TARGET_SCRIPT]}
        self.assertEqual(set(new)-set(old),IDS)
        self.assertEqual({gid for gid in old if old[gid]!=new[gid]},DONOR_IDS)
        for gid in DONOR_IDS:
            self.assertEqual(decode_encoded(old[gid][1],PAIRS).rstrip(" "),decode_encoded(new[gid][1],PAIRS).rstrip(" "))
        self.assertEqual(sum(len(z)-len(a) for a,z in new.values()),0)
    def test_reject_wrong_deferred(self):
        full=[{"gid":r["grupo_id"],"offset":int(r["offset_hex"],16),"old":a,"new":z} for r,a,z in self.prior[0][TARGET_SCRIPT]]
        with self.assertRaises(ValueError):audit(full,[])
if __name__=="__main__":unittest.main()
