import unittest,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from f4_r18_propuestas_globales import audit,OVERLAY,DRAFT_REL,draft_geometry

class GlobalOverlayTests(unittest.TestCase):
    def test_real_canonical_overlay(self):
        root=Path(__file__).resolve().parents[1]
        r=audit(root/DRAFT_REL,root/OVERLAY)
        self.assertEqual(r['overlay_count'],64)
        self.assertEqual(r['payload_bytes'],2007)
        self.assertEqual(r['scope'],'B_CANONICAL_GIT_PLAN_ONLY')
        self.assertFalse(r['deployment_authorized'])
    def test_geometry_ignores_unrelated_resources(self):
        self.assertEqual(draft_geometry([{'origen':'OTHER'}]),{'text_spans':[]})

if __name__=='__main__':unittest.main()
