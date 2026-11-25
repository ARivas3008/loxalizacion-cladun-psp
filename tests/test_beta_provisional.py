import unittest
from unittest.mock import patch
from types import SimpleNamespace
from tools.beta_provisional import movement, PROFILES

def command(i, moved=False, changed=False, text=False):
    return SimpleNamespace(block=0,order=i,code=0x66 if text else 0x01,instruction_id=i,
        offset=i*12+int(moved),raw=b'unchanged',content=(b'new' if changed else b'old') if text else None)

class BetaMovementTests(unittest.TestCase):
    def test_profile_counts(self):
        self.assertEqual(PROFILES["r52"],(8247,146,104,4899))
        self.assertEqual(PROFILES["r43"],(8214,0,0,4866))
    def test_reopen_r52_and_refuse_nontext_mutation(self):
        old=[command(i,text=i>=46308) for i in range(51705)]
        new=[command(i,moved=(i<104 or 46308<=i<46350),changed=46308<=i<51207,text=i>=46308) for i in range(51705)]
        a={"SCRIPT.DAT":b'a',"SCRIPT.TBL":b't',"AISCRIPT.DAT":b'i',"AISCRIPT.TBL":b'j'}
        b={**a,"SCRIPT.DAT":b'b'}
        with patch("tools.beta_provisional.read_commands",side_effect=[(old,[0,10]),(new,[0,10])]):
            rows=movement(a,b,"r52")
        self.assertEqual(len(rows),146)
        self.assertEqual(sum(r["nontext"] for r in rows),104)
        self.assertTrue(all(r["status"]=="NOT_RUN" for r in rows))
        new[0].raw=b'wrong'
        with patch("tools.beta_provisional.read_commands",side_effect=[(old,[0,10]),(new,[0,10])]):
            with self.assertRaises(ValueError): movement(a,b,"r52")
    def test_reject_table_drift(self):
        a={"SCRIPT.DAT":b'a',"SCRIPT.TBL":b't',"AISCRIPT.DAT":b'i',"AISCRIPT.TBL":b'j'}
        with self.assertRaises(ValueError): movement(a,{**a,"SCRIPT.TBL":b'x"},"r43")

if __name__=="__main__":
    unittest.main()
