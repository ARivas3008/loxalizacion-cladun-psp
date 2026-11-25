import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from tools.integrar_parche_seguro import (
    source_rows,plan_rows,plan_event_safe,combine_unified_profile,
    combine_extended_padding,combine_verified_symbols,combine_reviewed_concise,
    patch_canonical_menu_layout,patch_canonical_menu_values,TARGET_SCRIPT)
from tools.r38_concision import audit, OVERLAY
from tools.r31_bulk_padding import fnv,serialized

class R38Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows,_=patch_canonical_menu_layout(source_rows())
        rows,_=patch_canonical_menu_values(rows)
        changes,blocked,_=plan_rows(rows)
        cls.r36=combine_unified_profile(*plan_event_safe(changes,blocked,verified_packs=True))
        cls.r37=combine_verified_symbols(*combine_extended_padding(*cls.r36))
        cls.r38=combine_reviewed_concise(*cls.r37)

    def test_all_verified_parts_preserved(self):
        c,b,d,i=self.r38
        self.assertEqual(sum(map(len,c.values())),7520)
        self.assertEqual(len(c[TARGET_SCRIPT]),4172)
        self.assertEqual(len(d),728)
        ids={r["grupo_id"] for v in c.values() for r,_,_ in v}
        self.assertEqual(len(ids),7520)
        self.assertFalse(ids&set(d))
        self.assertFalse(ids&{r["grupo_id"] for r in b})
        previous=self.r37[0]
        for k,v in previous.items():
            if k!=TARGET_SCRIPT:self.assertEqual(v,c[k])
        by={r["grupo_id"]:(r,a,z) for r,a,z in c[TARGET_SCRIPT]}
        for r,a,z in previous[TARGET_SCRIPT]:
            self.assertEqual(by[r["grupo_id"]],(r,a,z))
        self.assertTrue(all(len(a)==len(z) for _,a,z in c[TARGET_SCRIPT]))
        self.assertFalse(i["runtime_verified"])
        self.assertFalse(i["release_authorized"])

    def test_combined_427_authentic_fingerprint(self):
        old={r["grupo_id"] for r,_,_ in self.r36[0][TARGET_SCRIPT]}
        recent=[{"gid":r["grupo_id"],"offset":int(r["offset_hex"],16),"old":a,"new":z}
                for r,a,z in self.r38[0][TARGET_SCRIPT] if r["grupo_id"] not in old]
        self.assertEqual(len(recent),427)
        self.assertEqual(fnv(serialized(recent)),3970964725)

    def test_overlay_modified_rejected(self):
        full=[{"gid":r["grupo_id"],"offset":int(r["offset_hex"],16),"old":a,"new":z}
              for r,a,z in self.r37[0][TARGET_SCRIPT]]
        with TemporaryDirectory() as tmp:
            bad=Path(tmp)/"bad.tsv"
            bad.write_bytes(OVERLAY.read_bytes()+b"\n")
            with self.assertRaises(ValueError):audit(full,bad)

if __name__=="__main__":unittest.main()
