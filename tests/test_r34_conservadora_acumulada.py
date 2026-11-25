import unittest
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from tools.integrar_parche_seguro import (
    TARGET_SCRIPT, source_rows, plan_rows, plan_event_safe,
    combine_verified_script_packs, patch_canonical_menu_layout,
    patch_canonical_menu_values)
from tools.r31_bulk_padding import make_plan


class AccumulatedConservativeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows, _ = patch_canonical_menu_layout(source_rows())
        rows, _ = patch_canonical_menu_values(rows)
        cls.changes, cls.blocked, cls.unchanged = plan_rows(rows)
        cls.plan = make_plan(pack="all")
        script = cls.changes[TARGET_SCRIPT]
        cls.allowed = [r for r in script if len(r[1]) == len(r[2])]
        cls.deferred = [r for r in script if len(r[1]) != len(r[2])]

    def test_canonical_cumulative_plan(self):
        base, _, base_pending, _ = plan_event_safe(self.changes, self.blocked)
        new, blocked, pending, report = plan_event_safe(
            self.changes, self.blocked, verified_packs=True)
        self.assertEqual(sum(map(len, base.values())), 3724)
        self.assertEqual(sum(map(len, new.values())), 5172)
        self.assertEqual((len(base_pending), len(pending)), (4524, 3076))
        self.assertEqual(len(new[TARGET_SCRIPT]), 1824)
        self.assertEqual(len(self.plan), 1448)
        self.assertEqual(set(base_pending)-set(pending),
                         {x["gid"] for x in self.plan})
        self.assertFalse(set(pending)&{x["gid"] for x in self.plan})
        self.assertFalse({x["grupo_id"] for x in blocked}&{x["gid"] for x in self.plan})
        for k in base:
            if k != TARGET_SCRIPT:
                self.assertEqual(new[k], base[k])
        before = {r[0]["grupo_id"]: r for r in base[TARGET_SCRIPT]}
        after = {r[0]["grupo_id"]: r for r in new[TARGET_SCRIPT]}
        self.assertEqual({gid:after[gid] for gid in before}, before)
        for x in self.plan:
            self.assertEqual(after[x["gid"]][1:], (x["old"],x["new"]))
        self.assertTrue(all(len(old)==len(new) for _,old,new in new[TARGET_SCRIPT]))
        self.assertEqual(report["total_planned"],5172)
        self.assertFalse(report["runtime_verified"])
        self.assertFalse(report["release_authorized"])
        self.assertEqual(len(self.changes[TARGET_SCRIPT]),4900)

    def test_reject_duplicate_and_unknown(self):
        for bad in ([self.plan[0]]+self.plan[:-1],
                    [{**self.plan[0],"gid":"999999","group_id":"999999"}]+self.plan[1:]):
            with self.assertRaises(ValueError):
                combine_verified_script_packs(self.allowed,self.deferred,bad)

    def test_reject_width_preimage_and_offset_drift(self):
        x=self.plan[0]
        for changed in ({"new":x["new"]+b" "},
                        {"new":b"\x00"+x["new"][1:]},
                        {"old":bytes([x["old"][0]^1])+x["old"][1:]},
                        {"offset":x["offset"]+1}):
            with self.assertRaises(ValueError):
                combine_verified_script_packs(self.allowed,self.deferred,
                                               [{**x,**changed}]+self.plan[1:])

    def test_historical_profile_unchanged(self):
        base, blocked, pending, info = plan_event_safe(self.changes,self.blocked)
        self.assertEqual(len(base[TARGET_SCRIPT]),376)
        self.assertEqual(len(pending),4524)
        self.assertIsNone(info)
        self.assertEqual(len(blocked),len(self.blocked)+4524)


if __name__=="__main__":
    unittest.main()
