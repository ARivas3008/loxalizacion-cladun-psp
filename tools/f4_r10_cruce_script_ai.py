#!/usr/bin/env python3
"""F4-R10: cruce seguro de 0A/0B/0C contra SCRIPT.TBL y AISCRIPT.TBL.
Las coincidencias numéricas NO demuestran saltos ni semántica PSP MIPS.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

ISO_SHA='b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
SCRIPT_DAT_SHA='c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358'
SCRIPT_TBL_SHA='f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37'
SCRIPT_SDT_SHA='1811742d7d3e88da530c1fd2b98885e8426f7af761f7c89aecc80f34ffdbe2d4'
SOURCE_INSTRUCTION=(20,20,7420,0x0a,818,100100)
LENGTHS={0x0a:4,0x0b:5,0x0c:4}

def parse_script_table_ids(table:bytes,count:int,data_size:int)->list[int]:
    if len(table)!=16+32*count or struct.unpack_from('<I',table,0)[0]!=count:
        raise ValueError('Tabla de indices inconsistente')
    ids=[];starts=[]
    for i in range(count):
        sid,start=struct.unpack_from('<II',table,16+i*32)
        if start%16 or start>=data_size:
            raise ValueError('Offset de script fuera de rango/alineacion')
        ids.append(sid);starts.append(start)
    if len(set(ids))!=count or starts[0]!=0 or starts!=sorted(starts):
        raise ValueError('IDs duplicados u offsets no monotonos')
    return ids

def profile_opcode_namespaces(commands,script_ids,ai_ids,script_names):
    if len(script_ids)!=len(script_names) or not script_ids or not ai_ids:
        raise ValueError('Tablas incompletas')
    if len(set(script_ids))!=len(script_ids) or len(set(ai_ids))!=len(ai_ids):
        raise ValueError('IDs duplicados')
    S=set(script_ids);A=set(ai_ids)
    counts={op:Counter() for op in LENGTHS};targets={op:set() for op in LENGTHS}
    flags=Counter();candidate=[]
    for cmd in commands:
        if cmd.content is not None or cmd.code not in LENGTHS:continue
        op=cmd.code;raw=cmd.raw;size=LENGTHS[op]
        if len(raw)!=5+size or struct.unpack_from('<H',raw,3)[0]!=size:
            raise ValueError(f'Longitud no valida para opcode {op:#x}')
        payload=raw[5:];value=struct.unpack_from('<I',payload,0)[0]
        C=counts[op];C['total']+=1
        if value in S:C['SCRIPT']+=1;targets[op].add(value)
        if value in A:C['AISCRIPT']+=1
        if value in S and value in A:C['both']+=1
        if value not in S and value not in A:C['neither']+=1
        if op==0x0b:flags[payload[4]]+=1
        if (cmd.block,cmd.order,cmd.offset,op,cmd.instruction_id,value)==SOURCE_INSTRUCTION:
            candidate.append({'source_block':cmd.block,'source_order':cmd.order,
              'source_command_offset':cmd.offset,'opcode':'0x0a',
              'instruction_id':cmd.instruction_id,'operand_u32':value,
              'source_script_name':script_names[cmd.block],
              'target_script_block':script_ids.index(value) if value in S else None})
    return {
        'script_tbl_ids':len(script_ids),'aiscript_tbl_ids':len(ai_ids),
        'namespace_id_overlap_count':len(S&A),
        'opcodes':{f'0x{op:02x}':{
          'payload_bytes':LENGTHS[op],'commands':counts[op]['total'],
          'matches_SCRIPT_TBL':counts[op]['SCRIPT'],
          'distinct_SCRIPT_TBL_ids':len(targets[op]),
          'matches_AISCRIPT_TBL':counts[op]['AISCRIPT'],
          'matches_both_tables':counts[op]['both'],
          'matches_neither_table':counts[op]['neither']}
          for op in LENGTHS},
        'opcode_0b_trailing_byte_counts':{str(k):v for k,v in sorted(flags.items())},
        'source_100100_candidates':candidate,
        'meaning':'Solo coincidencias numericas estaticas; NO se demuestran calls/saltos MIPS',
        'mips_semantics_proven':False,'relocalization_authorized':False}

def audit_original(iso:Path):
    try:
        from tools.extract_cladun import iso9660_entries,read_iso_file,pspfs_entries,decompress,dsarc_entries
        from tools.script_event_guard import read_commands
    except ModuleNotFoundError:
        from extract_cladun import iso9660_entries,read_iso_file,pspfs_entries,decompress,dsarc_entries
        from script_event_guard import read_commands
    iso=Path(iso)
    if iso.is_symlink() or not iso.is_file() or iso.stat().st_size!=305496064:
        raise ValueError('ISO USA original ausente o no regular')
    h=hashlib.sha256()
    with iso.open('rb') as f:
        for c in iter(lambda:f.read(4*1024*1024),b''):h.update(c)
    if h.hexdigest()!=ISO_SHA:raise ValueError('ISO USA SHA inesperado')
    _,entries=iso9660_entries(iso)
    dat=next((r for r in entries if r['path']=='PSP_GAME/USRDIR/DATA.DAT' and not r['directory']),None)
    if dat is None:raise ValueError('DATA.DAT ausente')
    container=read_iso_file(iso,dat)
    members=pspfs_entries(container)
    if len(members)!=349 or members[231]['name']!='SCRIPT.SDT':
        raise ValueError('PSPFS #231 inesperado')
    rec=members[231];packed=container[rec['offset']:rec['offset']+rec['size_stored']]
    if hashlib.sha256(packed).hexdigest()!=SCRIPT_SDT_SHA:raise ValueError('SCRIPT.SDT modificado')
    archive,_=decompress(packed,rec['size_expanded'])
    children={r['name']:archive[r['offset']:r['offset']+r['size']] for r in dsarc_entries(archive)}
    if set(children)!={'SCRIPT.DAT','SCRIPT.TBL','AISCRIPT.DAT','AISCRIPT.TBL'}:
        raise ValueError('DSARC original no reconocido')
    sd,st,ad,at=[children[x] for x in ('SCRIPT.DAT','SCRIPT.TBL','AISCRIPT.DAT','AISCRIPT.TBL')]
    if hashlib.sha256(sd).hexdigest()!=SCRIPT_DAT_SHA or hashlib.sha256(st).hexdigest()!=SCRIPT_TBL_SHA:
        raise ValueError('SCRIPT.DAT/TBL modificados')
    ids=parse_script_table_ids(st,1625,len(sd))
    ai=parse_script_table_ids(at,552,len(ad))
    commands,_=read_commands(sd,st)
    if len(commands)!=51705 or sum(c.content is None for c in commands)!=46308:
        raise ValueError('Recuento comandos no coincide con fuente original')
    names=[st[16+32*i+8:16+32*i+32].split(b'\0',1)[0].decode('ascii','strict') for i in range(1625)]
    data=profile_opcode_namespaces(commands,ids,ai,names)
    expected={'0x0a':(862,320,183,0),'0x0b':(166,75,67,0),'0x0c':(102,86,49,0)}
    for op,(total,matches,unique,ai_count) in expected.items():
        x=data['opcodes'][op]
        if (x['commands'],x['matches_SCRIPT_TBL'],x['distinct_SCRIPT_TBL_ids'],x['matches_AISCRIPT_TBL'])!=(total,matches,unique,ai_count):
            raise ValueError('Ancla F4-R10 inesperada '+op)
    if data['namespace_id_overlap_count']!=6 or data['opcode_0b_trailing_byte_counts']!={'100':112,'101':54}:
        raise ValueError('Ancla original AISCRIPT / 0x0B inesperada')
    if len(data['source_100100_candidates'])!=1 or data['source_100100_candidates'][0]['target_script_block']!=758:
        raise ValueError('Candidato scr01.dsf fuera del original')
    return {'schema':'cladun.f4.r10.script_ai_namespace_readonly.v1',
      'evidence':'A_AUTHENTIC_ISO_STATIC_NOT_PPSSPP',
      'iso_sha256':ISO_SHA,'script_dat_sha256':SCRIPT_DAT_SHA,
      'script_tbl_sha256':SCRIPT_TBL_SHA,'script_sdt_sha256':SCRIPT_SDT_SHA,
      'scripts':1625,'ai_scripts':552,'commands':51705,'nontext_commands':46308,
      **data,'ppsspp_executed':False,'original_commercial_bytes_written':False}

def main():
    try:from tools.f3_referencias_riesgo import report_path
    except ModuleNotFoundError:from f3_referencias_riesgo import report_path
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iso-original',required=True,type=Path)
    ap.add_argument('--reporte-privado',required=True,type=Path)
    args=ap.parse_args();target=report_path(args.reporte_privado)
    result=audit_original(args.iso_original)
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
    print(json.dumps({'script_ids':1625,'ai_ids':552,'opcodes':result['opcodes'],
      'ppsspp_C':False,'relocalization_authorized':False},ensure_ascii=False))
if __name__=='__main__':main()
