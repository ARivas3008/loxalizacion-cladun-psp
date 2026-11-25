import unittest
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from tools.integrar_parche_seguro import (
    source_rows,plan_rows,plan_event_safe,combine_unified_profile,combine_extended_padding,
    combine_verified_symbols,combine_reviewed_concise,combine_r39_concise,combine_r40_concise,
    patch_canonical_menu_layout,patch_canonical_menu_values)
from tools.integrar_parche_seguro import combine_r42_concise,combine_r43_concise,TARGET_SCRIPT
from tools.r43_concision import audit,OVERLAY

class R43Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows,_=patch_canonical_menu_layout(source_rows())
        rows,_=patch_canonical_menu_values(rows)
        changes,blocked,_=plan_rows(rows)
        r36=combine_unified_profile(*plan_event_safe(changes,blocked,verified_packs=True))
        r37=combine_verified_symbols(*combine_extended_padding(*r36))
        r38=combine_reviewed_concise(*r37)
        r39=combine_r39_concise(*r38)
        cls.prior=combine_r42_concise(*combine_r40_concise(*r39))
        cls.current=combine_r43_concise(*cls.prior)

    def test_accumulated_profile(self):
        c,b,d,i=self.current
        self.assertEqual(sum(map(len,c.values())),8214)
        self.assertEqual(len(c[TARGET_SCRIPT]),4866)
        self.assertEqual(len(d),33)
        self.assertFalse(i["runtime_verified"])
        self.assertFalse(i["release_authorized"])
        self.assertEqual(i["resolved_original_target"],8215)
        self.assertEqual(i["resolved_without_new_bytes"],1)
        self.assertNotIn("003765",d)
        self.assertIn("reviewed_concise_r43",i)
        self.assertIn("reviewed_concise_r42",i)
        previous=self.prior[0]
        by={r["grupo_id"]:(r,a,z) for r,a,z in c[TARGET_SCRIPT]}
        for r,a,z in previous[TARGET_SCRIPT]:
            if r["grupo_id"]=="003766":
                self.assertNotEqual(by[r["grupo_id"]][2],z)
                self.assertEqual(by[r["grupo_id"]][:2],(r,a))
                self.assertEqual(len(by[r["grupo_id"]][2]),len(z))
            else:self.assertEqual(by[r["grupo_id"]],(r,a,z))
        for k,v in previous.items():
            if k!=TARGET_SCRIPT:self.assertEqual(v,c[k])
        self.assertFalse(set(by)&set(d))

    def test_overlay_tampering(self):
        full=[{"gid":r["grupo_id"],"offset":int(r["offset_hex"],16),"old":a,"new":z}
              for r,a,z in self.prior[0][TARGET_SCRIPT]]
        with TemporaryDirectory() as tmp:
            bad=Path(tmp)/"bad.tsv"
            bad.write_bytes(OVERLAY.read_bytes().replace(b"Asagi",b"Asagx"))
            with self.assertRaises(ValueError):audit(full,bad)

if __name__=="__main__":unittest.main()
