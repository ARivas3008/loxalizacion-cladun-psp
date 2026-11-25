import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"tools"))
from tools.integrar_parche_seguro import (source_rows,plan_rows,plan_event_safe,
    combine_unified_profile,combine_extended_padding,combine_verified_symbols,
    patch_canonical_menu_layout,patch_canonical_menu_values,TARGET_SCRIPT)

class R37Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rows,_=patch_canonical_menu_layout(source_rows())
        rows,_=patch_canonical_menu_values(rows)
        changes,blocked,_=plan_rows(rows)
        cls.base=combine_unified_profile(*plan_event_safe(changes,blocked,verified_packs=True))
        cls.padded=combine_extended_padding(*cls.base)
        cls.final=combine_verified_symbols(*cls.padded)

    def test_counts_and_exact_preservation(self):
        for plan,count,script,pending in ((self.base,7093,3745,1155),
             (self.padded,7368,4020,880),(self.final,7421,4073,827)):
            c,b,d,i=plan
            self.assertEqual(sum(map(len,c.values())),count)
            self.assertEqual(len(c[TARGET_SCRIPT]),script)
            self.assertEqual(len(d),pending)
            self.assertEqual(len({r["grupo_id"] for v in c.values() for r,_,_ in v}),count)
            self.assertTrue(all(len(a)==len(z) for _,a,z in c[TARGET_SCRIPT]))
            self.assertFalse(i["runtime_verified"])
        for k,v in self.base[0].items():
            if k!=TARGET_SCRIPT:self.assertEqual(v,self.final[0][k])
        by={r["grupo_id"]:(r,a,b) for r,a,b in self.final[0][TARGET_SCRIPT]}
        for r,a,b in self.base[0][TARGET_SCRIPT]:
            self.assertEqual(by[r["grupo_id"]],(r,a,b))

    def test_symbols_and_pending(self):
        self.assertEqual(self.final[3]["verified_symbols"]["preserved_tokens"],65)
        self.assertEqual(self.final[3]["verified_symbols"]["categories"],
            {"icon_static_fit":53,"icon_text_overflow":19,
             "non_icon_multibyte_review":11,"format_control_review":10})
        self.assertEqual(self.final[3]["extended_padding"]["admitted_extended_padding"],275)

if __name__=="__main__":unittest.main()
