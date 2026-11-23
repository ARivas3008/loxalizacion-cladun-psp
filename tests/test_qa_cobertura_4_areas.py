"""Ensayos sintéticos del cierre T/G/R/Q; NO ejecutan PPSSPP."""
import unittest
from tools.qa_cobertura_4_areas import REQUIRED, inspect

H = 'a' * 64

def fixture():
    base = {'schema':'cladun.cobertura_cuatro_areas.v1',
      'traduccion':{'cierre_100':False,'borrador':{'hechos':9235,'total':9237},
       'aprobados_contextualmente':{'hechos':None,'total':None},'en_juego':{'hechos':None,'total':None},'inventario_visible_completo':False},
      'graficos':{'cierre_100':False,'inventario_completo':False,'aprobados_ppsspp':{'hechos':None,'total':None}},
      'romhacking':{'cierre_100':False,'sustituciones':{'hechos':3724,'total':8248},'diferidas':4524,
        'relocalizaciones_seguras_demostradas':False,'release_bps_exe_e2e':False},
      'betatesting':{'cierre_100':False,'matriz_completa':False,'aprobados':{'hechos':None,'total':None},'p0_p1_abiertos':None}}
    row = dict.fromkeys(REQUIRED, '')
    row.update({'caso_id':'Q001', 'modo/escena':'Título', 'pasos_reproducibles':'Iniciar juego',
       'expectativa_es':'Título en español','estado':'NOT_RUN'})
    return base, [row]

class TestQAGate(unittest.TestCase):
    def test_accepts_open_truthful_data(self):
        d, rows=fixture();self.assertEqual(inspect(d,rows)['estados']['NOT_RUN'],1)
    def test_reject_duplicate_id(self):
        d,rows=fixture()
        with self.assertRaises(ValueError):inspect(d,rows+rows)
    def test_reject_empty_matrix(self):
        d,_=fixture()
        with self.assertRaises(ValueError):inspect(d,[])
    def test_reject_fake_runtime_pass(self):
        d,rows=fixture();rows[0]['estado']='PASS'
        with self.assertRaises(ValueError):inspect(d,rows)
    def test_accept_runtime_pass_with_hashes_not_closure(self):
        d,rows=fixture();rows[0].update({'estado':'PASS','tipo_evidencia':'C',
            'ISO_SHA256':H,'evidencia_sha256_privada':H,'PPSSPP_version_hash_backend':'1.20.4 | sha | GPU'})
        self.assertEqual(inspect(d,rows)['estados']['PASS'],1)
    def test_reject_close_translation_without_coverage(self):
        d,rows=fixture();d['traduccion']['cierre_100']=True
        with self.assertRaises(ValueError):inspect(d,rows)
    def test_reject_close_graphics_without_inventory(self):
        d,rows=fixture();d['graficos']['cierre_100']=True
        with self.assertRaises(ValueError):inspect(d,rows)
    def test_reject_close_romhacking_with_deferred(self):
        d,rows=fixture();d['romhacking']['cierre_100']=True
        with self.assertRaises(ValueError):inspect(d,rows)
    def test_reject_close_qa_with_not_run(self):
        d,rows=fixture();d['betatesting']['cierre_100']=True
        with self.assertRaises(ValueError):inspect(d,rows)
    def test_reject_negative_denominator(self):
        d,rows=fixture();d['romhacking']['sustituciones']['total']=-1
        with self.assertRaises(ValueError):inspect(d,rows)
    def test_reject_invalid_state(self):
        d,rows=fixture();rows[0]['estado']='OK'
        with self.assertRaises(ValueError):inspect(d,rows)

if __name__ == '__main__':unittest.main()
