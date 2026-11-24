#!/usr/bin/env python3
"""Classify SCRIPT Spanish byte-width deltas without modifying the corpus or ISO."""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import Counter
from pathlib import Path
try:
 from tools.charset_es import encode_spanish,decode_spanish
 from tools.f3_referencias_riesgo import original_script_children
except ModuleNotFoundError:
 from charset_es import encode_spanish,decode_spanish
 from f3_referencias_riesgo import original_script_children

def classify(rows,script=None):
 result=Counter()
 deltas=Counter()
 seen=set()
 examples=[]
 for row in rows:
  if row['origen']!='SCRIPT.SDT/SCRIPT.DAT':
   continue
  gid=row['grupo_id']
  if gid in seen:raise ValueError('duplicate SCRIPT group '+gid)
  seen.add(gid)
  text=row['espanol']
  if not text:
   result['without_spanish']+=1
   continue
  try:
   old=bytes.fromhex(row['bytes_hex'])
   new=encode_spanish(text)
   if decode_spanish(new)!=text:raise ValueError('codec non-roundtrip')
   offset=int(row['offset_hex'],16)
   if script is not None and script[offset:offset+len(old)]!=old:
    raise ValueError('source mismatch at '+gid)
  except (ValueError,UnicodeError) as exc:
   result['invalid_or_unencodable']+=1
   if len(examples)<10:examples.append({'group_id':gid,'reason':type(exc).__name__})
   continue
  delta=len(new)-len(old)
  result['translated_script_rows']+=1
  deltas[delta]+=1
  if delta==0:result['same_byte_width']+=1
  else:
   result['variable_byte_width']+=1
   if abs(delta)<=3:result['variable_within_3_bytes']+=1
   if delta>0:result['growing']+=1
   else:result['shrinking']+=1
 return {
  'schema':'cladun.r20.script_width_delta.v1',
  'evidence':'A_AUTHENTIC_SCRIPT_PREIMAGE' if script is not None else 'B_GIT_CORPUS_STATIC',
  **dict(result),
  'delta_histogram':{str(k):v for k,v in sorted(deltas.items())},
  'invalid_examples_without_text':examples,
  'all_changes_canonical_approved':False,
  'variable_length_insertion_authorized':False,
  'ppsspp_verified':False,
 }

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--borrador',type=Path,default=Path('traduccion/CLADUN_BORRADOR_ES.csv'))
 p.add_argument('--iso-original',type=Path)
 a=p.parse_args()
 script=None
 if a.iso_original is not None:
  script,_=original_script_children(a.iso_original)
 with a.borrador.open(encoding='utf-8-sig',newline='') as f:
  result=classify(csv.DictReader(f),script)
 print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
