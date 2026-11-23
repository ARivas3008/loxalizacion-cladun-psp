#!/usr/bin/env python3
"""F4-R11: detectar desplazamiento de IDs en argumentos; SOLO evidencia A estatica.

No prueba llamadas PSP MIPS y nunca autoriza relocalizar ni exportar assets.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import struct

OP_LENGTHS={0x0A:4,0x0B:5,0x0C:4}
DELTA_RANGE=tuple(range(-256,257))
ISO_SHA='b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'

def infer_static_deltas(commands,ids,names,starts,deltas=DELTA_RANGE):
    """Cuenta coincidencias value-delta con SCRIPT IDs sin inferir semantica."""
    if len(ids)!=len(names) or len(starts)!=len(ids)+1 or len(set(ids))!=len(ids):
        raise ValueError('SCRIPT.TBL inconsistente')
    if not deltas or len(set(deltas))!=len(deltas) or 0 not in deltas or 100 not in deltas:
        raise ValueError('Rango de control debe incluir 0 y 100, sin duplicados')
    sid=set(ids)
    seen=set()
    grouped={op:[] for op in OP_LENGTHS}
    anchor=[]
    for cmd in commands:
        if cmd.offset in seen or not 0<=cmd.block<len(ids):
            raise ValueError('Offset de comando duplicado o bloque invalido')
        seen.add(cmd.offset)
        if cmd.content is not None or cmd.code not in OP_LENGTHS:
            continue
        n=OP_LENGTHS[cmd.code]
        if len(cmd.raw)!=5+n or struct.unpack_from('<H',cmd.raw,3)[0]!=n:
            raise ValueError('Payload de opcode corrupto')
        value=struct.unpack_from('<I',cmd.raw,5)[0]
        grouped[cmd.code].append(value)
        if (cmd.block,cmd.order,cmd.offset,cmd.code,cmd.instruction_id,value)==(20,20,7420,0x0a,818,100100):
            anchor.append({'source_block':20,'source_script_name':names[20],
              'order':20,'command_offset':7420,'operand_u32':100100,
              'literal_target_block':ids.index(value) if value in sid else None,
              'minus_100_target_id':value-100,
              'minus_100_target_block':ids.index(value-100) if value-100 in sid else None})
    summaries={}
    for opcode,values in grouped.items():
        ranked=[(sum(v-d in sid for v in values),d) for d in deltas]
        ranked.sort(key=lambda t:(-t[0],abs(t[1]),t[1]))
        exceptions=Counter(str(v) for v in values if v-100 not in sid)
        summaries[f'0x{opcode:02x}']={
          'commands':len(values),
          'literal_matches':sum(v in sid for v in values),
          'minus_100_matches':sum(v-100 in sid for v in values),
          'minus_100_distinct_script_ids':len({v-100 for v in values if v-100 in sid}),
          'minus_100_exceptions':dict(sorted(exceptions.items(),key=lambda x:int(x[0]))),
          'best_deltas':[{'delta':d,'matches':n} for n,d in ranked[:10]]}
    return {'script_tbl_ids':len(ids),'delta_range':[min(deltas),max(deltas)],
            'opcode_profiles':summaries,'source_anchor':anchor,
            'interpretation':'Asociacion numerica; no identifica semantica del interprete',
            'mips_control_flow_proven':False,'relocalization_authorized':False}

def audit_original(iso):
    try:
        from tools.f3_referencias_riesgo import original_script_children
        from tools.script_event_guard import read_commands
    except ModuleNotFoundError:
        from f3_referencias_riesgo import original_script_children
        from script_event_guard import read_commands
    data,table=original_script_children(Path(iso))
    commands,starts=read_commands(data,table)
    if len(commands)!=51705 or len(starts)!=1626:
        raise ValueError('Recuento original inesperado')
    ids=[struct.unpack_from('<I',table,16+32*i)[0] for i in range(1625)]
    names=[table[16+32*i+8:16+32*i+32].split(b'\0',1)[0].decode('ascii','strict') for i in range(1625)]
    result=infer_static_deltas(commands,ids,names,starts)
    expected={
       '0x0a':(862,320,860,278,{'0':1,'1':1}),
       '0x0b':(166,75,158,139,{'3':8}),
       '0x0c':(102,86,66,None,None)}
    for opcode,(n,literal,shift,unique,exceptions) in expected.items():
        row=result['opcode_profiles'][opcode]
        if (row['commands'],row['literal_matches'],row['minus_100_matches'])!=(n,literal,shift):
            raise ValueError('La ISO no coincide con el baseline R11: '+opcode)
        if unique is not None and row['minus_100_distinct_script_ids']!=unique:
            raise ValueError('Cantidad destinos desplazados inesperada: '+opcode)
        if exceptions is not None and row['minus_100_exceptions']!=exceptions:
            raise ValueError('Excepciones inesperadas: '+opcode)
    if len(result['source_anchor'])!=1 or result['source_anchor'][0]['literal_target_block']!=758 or result['source_anchor'][0]['minus_100_target_block']!=757:
        raise ValueError('El ancla 100100 no concuerda con original')
    return {'schema':'cladun.f4.r11_script_id_delta_readonly.v1',
      'source':'A_AUTHENTIC_ISO_NOT_PPSSPP',
      'usa_iso_sha256':ISO_SHA,
      'script_dat_sha256':'c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358',
      'script_tbl_sha256':'f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37',
      **result,'original_assets_modified':False,'commercial_bytes_in_report':False,
      'ppsspp_executed':False}

def main():
    try:from tools.f3_referencias_riesgo import report_path
    except ModuleNotFoundError:from f3_referencias_riesgo import report_path
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iso-original',required=True,type=Path)
    ap.add_argument('--reporte-privado',required=True,type=Path)
    a=ap.parse_args()
    dest=report_path(a.reporte_privado)
    result=audit_original(a.iso_original)
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
    print(json.dumps({'original_iso_verified':True,
      '0x0a_value_minus100':result['opcode_profiles']['0x0a']['minus_100_matches'],
      '0x0b_value_minus100':result['opcode_profiles']['0x0b']['minus_100_matches'],
      'relocalization_authorized':False}))
if __name__=='__main__':main()
