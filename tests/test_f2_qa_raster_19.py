"""Pruebas sintéticas de medidas F2: no son capturas PPSSPP."""
import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from f2_qa_raster_19 import geometry

class TestF2Raster19(unittest.TestCase):
    def test_empty_raster(self):
        self.assertEqual(geometry([[0]*16 for _ in range(16)])['pixels'],0)
    def test_bbox(self):
        g=[[0]*16 for _ in range(16)]
        g[0][2]=15;g[15][8]=1
        self.assertEqual(geometry(g)['bbox_xyxy'],[2,0,8,15])
        self.assertEqual(geometry(g)['pixels'],2)
    def test_no_fake_runtime_claims(self):
        import inspect
        from f2_qa_raster_19 import audit
        self.assertIn('total_ink!=100',inspect.getsource(audit))
if __name__=='__main__':unittest.main()
