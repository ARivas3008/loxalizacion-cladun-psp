"""R36 unified profile: verify independent full plan and one-stage source replay."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from tools.integrar_parche_seguro import (
    TARGET_SCRIPT, source_rows, plan_rows, plan_event_safe, combine_unified_profile,
    patch_canonical_menu_layout, patch_canonical_menu_values)
from tools.r35_ligaduras_acumuladas import make_plan

class R36Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows,_=patch_canonical_menu_layout(source_rows())
        rows,_=patch_canonical_menu_values(rows)
        changes,blocked,_=plan_rows(rows)
        cls.r34=plan_event_safe(changes,blocked,verified_packs=True)
        cls.selected,cls.full,_=make_plan()
        cls.unified=combine_unified_profile(*cls.r34)

    def test_all_verified_parts_together(self):
        changes,blocked,deferred,info=self.unified
        self.assertEqual(sum(map(len,changes.values())),7093)
        self.assertEqual(len(changes[TARGET_SCRIPT]),3745)
        self.assertEqual(len(deferred),1155)
        self.assertEqual(len(self.r34[2])-len(deferred),1921)
        ids={src["grupo_id"] for v in changes.values() for src,_,_ in v}
        self.assertEqual(len(ids),7093)
        self.assertFalse(ids&set(deferred))
        self.assertFalse(ids&{x["grupo_id"] for x in blocked})
        self.assertEqual(info["total_planned"],7093)
        self.assertFalse(info["runtime_verified"])
        self.assertFalse(info["release_authorized"])

    def test_base_unchanged(self):
        old=self.r34[0];new=self.unified[0]
        for k,v in old.items():
            if k!=TARGET_SCRIPT:
                self.assertEqual(v,new[k])
        n={src["grupo_id"]:(src,a,b) for src,a,b in new[TARGET_SCRIPT]}
        for src,a,b in old[TARGET_SCRIPT]:
            self.assertEqual(n[src["grupo_id"]],(src,a,b))
        self.assertEqual([(r["grupo_id"],int(r["offset_hex"],16),a,b)
                          for r,a,b in new[TARGET_SCRIPT]],
                         [(x["gid"],x["offset"],x["old"],x["new"]) for x in self.full])

    def test_reject_non_deferred_or_missing_ligature(self):
        changes,blocked,deferred,info=self.r34
        with self.assertRaises(ValueError):
            combine_unified_profile(changes,blocked,[x for x in deferred if x!=self.selected[0]["gid"]],info)
        with patch("tools.r35_ligaduras_acumuladas.make_plan",
                   return_value=(self.selected[:-1],self.full,{})):
            with self.assertRaises(ValueError):
                combine_unified_profile(*self.r34)

if __name__=="__main__":
    unittest.main()
