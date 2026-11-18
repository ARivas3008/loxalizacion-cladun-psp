"""Pruebas de corpus versionado (no necesitan la ISO comercial)."""
from __future__ import annotations
import importlib.util
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('qa_corpus',ROOT/'tools/verificar_integridad.py')
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class TestCorpus(unittest.TestCase):
    def test_integridad_y_bytes(self):
        r=module.verificar(ROOT)
        self.assertEqual(r['resultado'],'OK',r['errores'])
        self.assertEqual(r['errores'],[])
    def test_hay_campos_pendientes_sin_afirmar_100(self):
        r=module.verificar(ROOT)
        self.assertGreater(r['pendientes_uso_o_decodificacion'],0)
        self.assertEqual(r['bloques_originales'],r['fuente_formato_confirmado']+r['pendientes_uso_o_decodificacion'])

if __name__=='__main__':unittest.main()
