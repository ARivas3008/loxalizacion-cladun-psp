import unittest
import copy
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from f3_propuestas_longitud_fija import proposal_plan, STATUS

class ProposalTests(unittest.TestCase):
    def setUp(self):
        self.rows=[{'grupo_id':'000001','origen':'SCRIPT.SDT/SCRIPT.DAT','offset_hex':'0x10','script_id':'100100','orden_script':'1','bytes_hex':'48657921','espanol':'Hola amigo','longitud_original_bytes':'4'}]
        self.geo={'text_spans':[{'offset':16,'script_id':100100,'command_order':1,'source_length':4,'block_index':1}]}
        self.p=[{'grupo_id':'000001','offset_hex':'0x10','longitud_original_bytes':'4','propuesta_es':'¡Ey!','estado':STATUS}]
    def run_plan(self):return proposal_plan(self.rows,self.geo,self.p)
    def test_exact_width(self):self.assertEqual(len(self.run_plan()[0]['new']),4)
    def test_wrong_width(self):
        self.p[0]['propuesta_es']='Hola amigo';self.assertRaises(ValueError,self.run_plan)
    def test_duplicate(self):
        self.p.append(copy.deepcopy(self.p[0]));self.assertRaises(ValueError,self.run_plan)
    def test_wrong_offset(self):
        self.p[0]['offset_hex']='0x11';self.assertRaises(ValueError,self.run_plan)
    def test_wrong_order(self):
        self.rows[0]['orden_script']='2';self.assertRaises(ValueError,self.run_plan)
    def test_already_equal(self):
        self.rows[0]['espanol']='Hola';self.assertRaises(ValueError,self.run_plan)
    def test_no_controls(self):
        self.p[0]['propuesta_es']='A\nBC';self.assertRaises(ValueError,self.run_plan)
    def test_no_format_token(self):
        self.rows[0]['bytes_hex']='48652573';self.assertRaises(ValueError,self.run_plan)
    def test_no_padding(self):
        self.p[0]['propuesta_es']=' Ey ';self.assertRaises(ValueError,self.run_plan)
    def test_wrong_status(self):
        self.p[0]['estado']='PASS';self.assertRaises(ValueError,self.run_plan)
    def test_wrong_length_metadata(self):
        self.p[0]['longitud_original_bytes']='5';self.assertRaises(ValueError,self.run_plan)
    def test_empty(self):
        self.p=[];self.assertRaises(ValueError,self.run_plan)
    def test_repository_proposals(self):
        from f3_simular_intro_mismo_tamano import audit_proposals, anchor
        root=Path(__file__).resolve().parents[1]
        result=audit_proposals(root/anchor.DRAFT_REL,root/anchor.GEOMETRY_REL,root/'traduccion/propuestas/DEMO1001_LONGITUD_FIJA_R17.csv')
        self.assertEqual(result['same_length_candidates'],42)
        self.assertEqual(result['canonical_blocked_different_length'],85)
        self.assertEqual(result['changed_length_blocked'],43)
        self.assertFalse(result['deployment_authorized'])

if __name__=='__main__':unittest.main()
