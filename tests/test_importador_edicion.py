import csv
import sys
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from aplicar_correcciones_editor import actualizar_txt, validar
from generar_guion_hablantes import cargar, construir

class ImportadorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        source_path=ROOT/'corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv'
        draft_path=ROOT/'traduccion/CLADUN_BORRADOR_ES.csv'
        cls.source=cargar(source_path)
        with draft_path.open(encoding='utf-8-sig',newline='') as f:
            read=csv.DictReader(f);cls.cols=list(read.fieldnames or []);cls.draft=list(read)

    def test_csv_preflight_changes_only_spanish(self):
        alt=[r.copy() for r in self.draft]
        alt[783]['espanol']='Joven nervioso'
        changes=validar(self.draft,alt,self.cols,self.cols,self.source)
        self.assertEqual(len(changes),1)
        self.assertEqual(changes[0][0]['grupo_id'],'000784')
        alt[783]['bytes_hex']='000000000000'
        with self.assertRaises(ValueError):validar(self.draft,alt,self.cols,self.cols,self.source)

    def test_historical_txt_roundtrip_only_targeted_group(self):
        old=self.draft[783]
        new={**old,'espanol':'Joven nervioso'}
        for name,bilingual in [('CLADUN_BORRADOR_ES.txt',False),
                               ('CLADUN_BORRADOR_BILINGUE_FAQ.txt',True)]:
            before=(ROOT/'traduccion'/name).read_text(encoding='utf-8-sig')
            after=actualizar_txt(before,[(old,new)],bilingual)
            self.assertNotEqual(before,after)
            self.assertIn('Joven nervioso',after)
            self.assertEqual(len(before)-len(after),len(old['espanol'])-len(new['espanol']))

    def test_five_thousand_two_hundred_seven_script_rows(self):
        indexed,counts=construir(self.draft)
        self.assertEqual(len(indexed),5207)
        self.assertEqual(sum(r['tipo']=='personaje_interlocutor' for r in indexed),400)
        self.assertEqual(sum(v for v in counts.values()),4807)

if __name__=='__main__':unittest.main()
