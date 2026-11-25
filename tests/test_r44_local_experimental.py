import unittest
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from tools.integrar_parche_seguro import (
    source_rows,plan_rows,plan_event_safe,combine_unified_profile,combine_extended_padding,
    combine_verified_symbols,combine_reviewed_concise,combine_r39_concise,combine_r40_concise,
    patch_canonical_menu_layout,patch_canonical_menu_values)
from tools.integrar_parche_seguro import combine_r42_concise,combine_r43_concise,combine_r44_local_experimental,TARGET_SCRIPT
from tools.r44_local_experimental import audit,IDS,DONOR_IDS
from tools.f4_r21_ligature_capacity import decode_encoded
from tools.r35_ligaduras_acumuladas import PAIRS

class R44Tests(unittest.TestCase):
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
        cls.r43=combine_r43_concise(*cls.prior)
        cls.current=combine_r44_local_experimental(*cls.r43)

    def test_experimental_all_resolved(self):
        c,b,d,i=self.current
        self.assertEqual(sum(map(len,c.values())),8247)
        self.assertEqual(len(c[TARGET_SCRIPT]),4899)
        self.assertEqual(d,[])
        self.assertEqual(i["resolved_original_target"],8248)
        self.assertEqual(i["resolved_without_new_bytes"],1)
        self.assertFalse(i["local_relocation_experimental"]["fixed_offsets"])
        self.assertFalse(i["release_authorized"])
        old={r["grupo_id"]:(a,z) for r,a,z in self.r43[0][TARGET_SCRIPT]}
        new={r["grupo_id"]:(a,z) for r,a,z in c[TARGET_SCRIPT]}
        self.assertEqual(set(new)-set(old),IDS)
        self.assertEqual({gid for gid in old if old[gid]!=new[gid]},DONOR_IDS)
        for gid in DONOR_IDS:
            self.assertEqual(decode_encoded(old[gid][1],PAIRS).rstrip(" "),
                             decode_encoded(new[gid][1],PAIRS).rstrip(" "))
        self.assertEqual(sum(len(new[g][1])-len(new[g][0]) for g in IDS),40)

    def test_wrong_deferred_set_rejected(self):
        full=[{"gid":r["grupo_id"],"offset":int(r["offset_hex"],16),"old":a,"new":z}
              for r,a,z in self.r43[0][TARGET_SCRIPT]]
        with self.assertRaises(ValueError):audit(full,[])

if __name__=="__main__":unittest.main()
