#!/usr/bin/env python3
"""F2 diagnostic-only full-19-glyph text screen in Options help.

Writes a complete PRIVATE CSV overlay; never changes canonical sources.
Only 005694 is a new diagnostic; 005709/005713 carry previously certified
F1 layout spacing when --borrador explicitly disables the automatic override.
The build must use --experimental-parcial --event-safe-only on verified USA ISO.
No generated screenshot proves anything until viewed in real PPSSPP.
"""
from __future__ import annotations
import argparse,csv,json,hashlib
from pathlib import Path
from auditar_preinsercion_es import DRAFT, SOURCE
from integrar_parche_seguro import source_rows
from menu_layout_es import patch_canonical_menu_layout, patch_canonical_menu_values
from charset_es import ES_GLYPHS, encode_spanish, decode_spanish
from font_es_patch import SOURCE_SHA256

DIAGNOSTIC_ID='005694'
DIAGNOSTIC_TEXT='F2 áéíóú ÁÉÍÓÚ ñÑüÜ ¿¡ «» ō'
EXPECTED_RESOURCE='DATABASE.DAT/STRTBL.DAT'

def digest(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for data in iter(lambda:f.read(1<<20),b''):h.update(data)
 return h.hexdigest()

def prepare(rows):
 if len(rows)!=9237:raise ValueError('Se requieren 9237 registros')
 corrected,layout=patch_canonical_menu_layout(rows)
 corrected,_=patch_canonical_menu_values(corrected)
 found=0;result=[]
 for src,dst in corrected:
  if src['grupo_id']==DIAGNOSTIC_ID:
   if (found or src['origen']!=EXPECTED_RESOURCE or
       src['original']!='Changes button configuration. (Switches screen)' or
       dst['espanol']!='Configura los botones.' or
       src['bytes_hex'].upper()!=src['original'].encode('cp932').hex().upper()):
    raise ValueError('Preimagen 005694 inesperada')
   found+=1
   if ''.join(c for c in DIAGNOSTIC_TEXT if c in ES_GLYPHS)!=ES_GLYPHS:
    raise ValueError('19 glyph order unexpectedly changed')
   binary=encode_spanish(DIAGNOSTIC_TEXT)
   if decode_spanish(binary)!=DIAGNOSTIC_TEXT:
    raise ValueError('Codec F2 is not reversible')
   dst={**dst,'espanol':DIAGNOSTIC_TEXT}
  result.append((src,dst))
 if found!=1:raise ValueError('005694 debe existir solo una vez')
 changes=[(s['grupo_id'],[k for k in d if d[k]!=o[k]])
          for (s,o),(_s,d) in zip(rows,result) if o!=d]
 if changes!=[(DIAGNOSTIC_ID,['espanol']),('005709',['espanol']),('005713',['espanol'])]:
  raise ValueError('Ediciones fuera de 005694 y rellenos F1: '+repr(changes))
 return result,{'layout':layout,'changes':changes,
               'one_diagnostic_id':DIAGNOSTIC_ID,'full_glyphs':ES_GLYPHS,
               'diagnostic_text':DIAGNOSTIC_TEXT,'F1_layout_preserved':True,
               'F1_values_preserved':True,'F1_event_safe_only_mandatory':True}

def build(csvout,report,iso):
 csvout,report,iso=map(Path,(csvout,report,iso))
 if len({csvout.resolve(),report.resolve(),iso.resolve()})!=3 or \
    csvout.resolve() in (DRAFT.resolve(),SOURCE.resolve()) or report.resolve() in (DRAFT.resolve(),SOURCE.resolve()):
  raise ValueError('Protected input / output collision')
 if csvout.exists() or report.exists():raise FileExistsError('Use unused output destinations')
 if digest(iso)!=SOURCE_SHA256:raise ValueError('Incorrect USA ISO source')
 pairs,info=prepare(source_rows())
 with DRAFT.open(encoding='utf-8-sig',newline='') as f:
  fields=csv.DictReader(f).fieldnames
 csvout.parent.mkdir(parents=True,exist_ok=True); report.parent.mkdir(parents=True,exist_ok=True)
 with csvout.open('x',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=fields)
  writer.writeheader();writer.writerows(dst for _src,dst in pairs)
 record={'schema':'cladun.f2.glifos_diagnostico.v1','estado':'SOLO_CSV_NO_QA_VISUAL',
         'total_registros':len(pairs),'source_iso_sha256':digest(iso),
         'csv_sha256':digest(csvout),'codigo':'CP932_A1_B3',
         'exclusivamente_privado':True,**info}
 with report.open('x',encoding='utf-8') as f:json.dump(record,f,indent=2,ensure_ascii=False);f.write('\n')
 return record

if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--iso',type=Path,required=True)
 p.add_argument('--salida-csv',type=Path,required=True)
 p.add_argument('--reporte',type=Path,required=True)
 a=p.parse_args()
 print(json.dumps(build(a.salida_csv,a.reporte,a.iso),indent=2,ensure_ascii=False))
