from pathlib import Path
import sys,unittest

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'tools'))
from revisar_corpus import CAMPOS, IMAGENES, original_de_campo, campos_archivo
from verificar_integridad import verificar

class TestCorpus(unittest.TestCase):
    def test_corpus_sin_traduccion_y_con_indice(self):
        result=verificar(BASE)
        self.assertEqual(result['resultado'],'OK')
        self.assertEqual(result['bloques_originales'],9237)

    def test_campo_japones_cp932(self):
        text,raw=original_de_campo('炎上'.encode('cp932')+b'\x00\x00')
        self.assertEqual(text,'炎上')
        self.assertEqual(raw,'炎上'.encode('cp932'))

    def test_campo_con_bytes_incompletos_se_marca(self):
        text,raw=original_de_campo('オイル'.encode('cp932')+b'\x96\x00')
        self.assertIn('\ufffd',text)
        self.assertTrue(raw.endswith(b'\x96'))

    def test_rutas_internas_se_excluyen(self):
        self.assertEqual([f.uso for f in CAMPOS['RMAPSET.DAT']],['texto','recurso_interno'])

    def test_campos_dungeon_no_absorben_prefijos(self):
        self.assertEqual(CAMPOS['DUNGEON.DAT'][0].desplazamiento,32)
        self.assertEqual(CAMPOS['DUNGEON.DAT'][0].capacidad,32)

    def test_graficos_protegidos(self):
        self.assertEqual(sum(x[3]=='texto' for x in IMAGENES),6)
        self.assertEqual(sum(x[3]=='marca' for x in IMAGENES),4)
        self.assertEqual(sum(x[3]=='decoracion' for x in IMAGENES),2)

if __name__=='__main__':unittest.main()
