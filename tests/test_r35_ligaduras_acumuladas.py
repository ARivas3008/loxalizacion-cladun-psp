import unittest
from tools.r35_ligaduras_acumuladas import make_plan, run, TOTAL, BASE

class R35Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.selected,cls.full,cls.report=make_plan()

    def test_batches(self):
        self.assertEqual([(b["checked"],b["admitted"],b["duplicate"]) for b in self.report["batches"]],
                         [(1000,955,45),(1000,964,36),(2,2,0)])
        self.assertEqual(len(self.selected),1921)
        self.assertEqual(len(self.full),3745)
        self.assertEqual((BASE,TOTAL,self.report["pending"]),(5172,7093,1155))

    def test_width_and_overlap(self):
        self.assertTrue(all(len(x["old"])==len(x["new"]) for x in self.full))
        self.assertEqual(len({x["gid"] for x in self.full}),3745)
        self.assertTrue(all(a["offset"]+len(a["old"])<=b["offset"] for a,b in zip(self.full,self.full[1:])))

    def test_no_false_promotion(self):
        self.assertEqual(self.report["official"],3724)
        for key in ("runtime_verified","release_authorized","candidate_written"):
            self.assertFalse(self.report[key])

if __name__=="__main__":
    unittest.main()
