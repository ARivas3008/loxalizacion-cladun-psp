import unittest
from tools.r55_private_accumulated import canonical_plan
from tools.r56_native_ellipsis import extend_donors,DONOR,RESIDUAL
from tools.r35_ligaduras_acumuladas import PAIRS
from tools.f4_r21_ligature_capacity import decode_encoded

class R56Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.baseline,cls.residuals,cls.donors=canonical_plan()
    def test_exact_donor_and_punctuation(self):
        d=extend_donors(self.baseline,self.residuals,self.donors)
        self.assertEqual(set(d)-set(self.donors),{DONOR})
        self.assertEqual({k:d[k] for k in self.donors},self.donors)
        old,new,gid=d[DONOR]
        self.assertEqual((gid,len(old),len(new)),("004508",8,7))
        self.assertEqual(decode_encoded(new,PAIRS),"¡Pues…!")
        self.assertEqual(decode_encoded(self.residuals[RESIDUAL][1],PAIRS),"¡Oh!")
    def test_reject_donor_drift(self):
        b=dict(self.baseline)
        old,new,gid=b[DONOR];b[DONOR]=(old,b"12345678",gid)
        with self.assertRaises(ValueError):extend_donors(b,self.residuals,self.donors)
    def test_donor_not_already_used(self):
        with self.assertRaises(ValueError):extend_donors(self.baseline,self.residuals,{**self.donors,DONOR:self.baseline[DONOR]})
