#!/usr/bin/env python3
"""Pruebas independientes del plan de cierre: no tocan binarios ni traducciones."""
import csv
from pathlib import Path
import sys
import unittest
from tempfile import TemporaryDirectory

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from cerrar_qa_linguistico import audit,csv_read,decisions

class CierreLinguisticoTest(unittest.TestCase):
    def test_inventory_and_preimage(self):
        h,rows,plan,pending,guarded,source=audit(ROOT,ROOT/'qa/plan_cierre_linguistico.txt')
        self.assertEqual(len(rows),9237)
        self.assertEqual(len(plan),227)
        self.assertEqual(len(guarded),2)
        self.assertIn(len(pending),(0,227))
        self.assertEqual(sum(x['espanol']=='' for x in rows),2)
        self.assertEqual({x['grupo_id'] for x in source if x['original'].endswith('�')},{'008723','008724'})

    def test_guarded_japanese_fields_not_invented(self):
        _,rows,plan,pending,guarded,_=audit(ROOT,ROOT/'qa/plan_cierre_linguistico.txt')
        self.assertEqual(guarded['CLD-F-TIPATTR-0214-nombre_atributo']['etiqueta_de_insercion'],'Aceite animado')
        self.assertEqual(guarded['CLD-F-TIPATTR-0215-nombre_atributo']['etiqueta_de_insercion'],'Agua animada')

    def test_only_spanish_changed_in_plan(self):
        h,rows,plan,pending,guarded,_=audit(ROOT,ROOT/'qa/plan_cierre_linguistico.txt')
        refs={r['text_id']:r for r in rows}
        for p in plan:
            r=refs[p['text_id']]
            self.assertEqual(p['original'],r['original'])
            self.assertIn(r['espanol'],(p['es_anterior'],p['es_corregido']))

    def test_decisions_cover_all_110_before_and_after(self):
        _,rows,plan,_,guarded,_=audit(ROOT,ROOT/'qa/plan_cierre_linguistico.txt')
        result=decisions(ROOT,plan,rows,guarded)
        self.assertEqual(len(result),110)
        from collections import Counter
        counts=Counter(x['dictamen_editorial'] for x in result)
        self.assertEqual(counts['corregido_nombre_propio'],82)
        self.assertEqual(counts['excepcion_fuente_truncada_con_etiqueta_de_insercion'],2)
        self.assertEqual(counts['corregido_texto_unido'],1)

    def test_canonical_names_cannot_be_mistranslated(self):
        _,rows,plan,_,_,_=audit(ROOT,ROOT/'qa/plan_cierre_linguistico.txt')
        patches={x['text_id']:x['es_corregido'] for x in plan}
        def current(r):return patches.get(r['text_id'],r['espanol'])
        for r in rows:
            if r['tipo']=='nombres_jefes' and r['origen']=='DATABASE.DAT/BOSSNAME.DAT':
                self.assertEqual(current(r),r['original'])
            if r['tipo']=='nombres_personajes' and ('CHARNAMEMAN.DAT' in r['origen'] or 'CHARNAMEWOMAN.DAT' in r['origen']):
                self.assertEqual(current(r),r['original'])
        for id,expected in [('CLD-006657','Sherbet'),('CLD-006663','Coco'),('CLD-006682','Bob'),('CLD-006688','Sunday')]:
            self.assertEqual(current(next(x for x in rows if x['text_id']==id)),expected)

if __name__=='__main__':unittest.main()
