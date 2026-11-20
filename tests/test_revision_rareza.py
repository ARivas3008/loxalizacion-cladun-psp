import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from aplicar_revision_rareza import validar_plan


def mock_rows():
    return ([{'text_id':f'CLD-{i:06d}','original':'Test message',
              'espanol':'Mensaje de prueba'} for i in range(1,9238)])


def row(key='CLD-000001', old='Mensaje de prueba', new='Mensaje claro'):
    return {'text_id':key,'es_anterior':old,'es_corregido':new,
            'motivo':'Comparación manual', 'segmento':'G00001'}


class RarezaContractTests(unittest.TestCase):
    def test_one_permitted_change(self):
        result,pending=validar_plan(mock_rows(),[row()], [{'ids':'CLD-000001','alerta':'PUNTUACION'}])
        self.assertEqual((result,len(pending)),('pendiente',1))

    def test_reject_non_alerted(self):
        with self.assertRaisesRegex(ValueError,'ajeno'):
            validar_plan(mock_rows(),[row()], [{'ids':'CLD-000002','alerta':'PUNTUACION'}])

    def test_reject_unintended_edit(self):
        with self.assertRaisesRegex(ValueError,'no coincide'):
            validar_plan(mock_rows(),[row(old='Cualquier cosa')], [{'ids':'CLD-000001','alerta':'PUNTUACION'}])

    def test_reject_duplicate(self):
        with self.assertRaisesRegex(ValueError,'duplicada'):
            validar_plan(mock_rows(),[row(),row()], [{'ids':'CLD-000001','alerta':'PUNTUACION'}])

    def test_reject_marker(self):
        rows=mock_rows();rows[0]['original']='Press ⑨ to continue'
        with self.assertRaisesRegex(ValueError,'Marcador'):
            validar_plan(rows,[row()], [{'ids':'CLD-000001','alerta':'PUNTUACION'}])

    def test_accept_idempotent_complete(self):
        rows=mock_rows();rows[0]['espanol']='Mensaje claro'
        s,p=validar_plan(rows,[row()], [{'ids':'CLD-000001','alerta':'PUNTUACION'}])
        self.assertEqual((s,len(p)),('ya_aplicado',0))


if __name__=='__main__':unittest.main()
