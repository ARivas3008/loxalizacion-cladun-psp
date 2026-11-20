#!/usr/bin/env python3
"""QA de guion reconstruido: todas las unidades y atribuciones conservadoras."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / 'tools'))
from reconstruir_guion_completo import build, join_exact, read_csv, render, write_report


class GuionCompletoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.src = BASE/'corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv'
        cls.dst = BASE/'traduccion/CLADUN_BORRADOR_ES.csv'
        cls.a = read_csv(cls.src)
        cls.b = read_csv(cls.dst)
        cls.groups, cls.items, cls.other, cls.alerts, cls.counts = build(cls.a,cls.b)

    def test_9237_ids_permanecen_una_vez(self):
        ids=[v for i in self.items for v in i['ids']]+[x['text_id'] for x in self.other]
        self.assertEqual(len(ids),9237)
        self.assertEqual(len(set(ids)),9237)
        self.assertEqual(set(ids),{x['text_id'] for x in self.a})

    def test_escenas_cuadros_y_opciones(self):
        self.assertEqual(len(self.groups),586)
        self.assertEqual(self.counts['nombre'],400)
        self.assertEqual(self.counts['opcion'],113)
        self.assertEqual(self.counts['dialogo'],2216)
        self.assertEqual(len(self.other),4030)

    def test_joven_frenetico_dialogo_completo(self):
        grp=next(i for i in self.items if i['tipo']=='dialogo' and i['ids']==
                 ['CLD-000804','CLD-000805','CLD-000806'])
        self.assertEqual(grp['hablante'],'Joven frenético')
        self.assertIn('¿Te duele algo?',grp['ES'])
        self.assertTrue(grp['ES'].endswith('¡Estás cubierto de barro!'))
        self.assertEqual(grp['atribucion'],'marcador_0x6E_inmediato')

    def test_otra_voz_no_se_atribuye_por_inercia(self):
        grp=next(i for i in self.items if i['tipo']=='dialogo' and
                 i['ids'][0]=='CLD-000807')
        self.assertEqual(grp['hablante'],'HABLANTE NO VERIFICADO')

    def test_oracion_entre_cajas_se_senaliza_como_probable(self):
        grp=next(i for i in self.items if i['tipo']=='dialogo' and
                 'CLD-002565' in i['ids'])
        self.assertIn('CLD-002566',grp['ids'])
        self.assertTrue(any('UNION_ENTRE_CAJAS' in v for v in grp['flags']))

    def test_traduccion_mtl_partida_sigue_visible(self):
        grp=next(i for i in self.items if i['tipo']=='dialogo' and
                 'CLD-001023' in i['ids'])
        self.assertIn('vengo. de linaje',grp['ES'])
        self.assertIn('I come from a noble bloodline',grp['EN'])
        self.assertTrue(any('FRASE_CORTADA_POR_PUNTO' in x for x in grp['flags']))

    def test_concatenacion_no_corrige_arbitrariamente(self):
        self.assertEqual(join_exact(['Una palabra.', 'siguiente frase']),
                         'Una palabra. siguiente frase')
        self.assertEqual(join_exact(['Hello,','world!']), 'Hello, world!')

    def test_csv_master_no_cambia_y_appendix_completo(self):
        bef=(hashlib.sha256(self.src.read_bytes()).hexdigest(),
             hashlib.sha256(self.dst.read_bytes()).hexdigest())
        with tempfile.TemporaryDirectory() as tmp:
            info=write_report(Path(tmp),self.src,self.dst,self.groups,self.items,
                              self.other,self.alerts,self.counts)
            self.assertEqual(info['integridad']['ids_conservados'],9237)
            self.assertTrue((Path(tmp)/'CLADUN_TODO_TEXTO_RECONSTRUIDO_ES_EN.txt').exists())
            self.assertIn('RECURSO: DATABASE.DAT/',
                          (Path(tmp)/'CLADUN_TODO_TEXTO_RECONSTRUIDO_ES_EN.txt').read_text(encoding='utf-8-sig'))
        aft=(hashlib.sha256(self.src.read_bytes()).hexdigest(),
             hashlib.sha256(self.dst.read_bytes()).hexdigest())
        self.assertEqual(bef,aft)

    def test_no_mezclar_registros_de_distinta_escena(self):
        for x in self.items:
            self.assertEqual(len({(r['indice_registro'],r['script_id'],r['script'])
                                 for r in x['rows']}),1)


if __name__=='__main__':unittest.main()
