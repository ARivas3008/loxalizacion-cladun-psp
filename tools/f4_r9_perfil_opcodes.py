#!/usr/bin/env python3
"""F4-R9: perfil de argumentos de opcodes 0x0A/0x01/0x02 en ISO original.

Un match de u32 con ID de script u offset de comando no prueba salto MIPS.
Informe SOLO metadatos; nunca exporta bytes, textos, ROM ni captura comercial.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

INTRO_NAMES = frozenset(('demo1001_00.dsf', 'demo1001_01.dsf'))
ISO_SHA = 'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
SCRIPT_SHA = 'c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358'
TABLE_SHA = 'f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37'

def profile(commands, starts, script_ids, names):
    if len(starts) != len(script_ids)+1 or len(names) != len(script_ids):
        raise ValueError('Tabla inconsistente')
    if len(set(script_ids)) != len(script_ids):
        raise ValueError('IDs de script duplicados')
    intro = {i for i, name in enumerate(names) if name in INTRO_NAMES}
    if not intro:
        raise ValueError('demo1001 no existe')
    idset = set(script_ids)
    pos_to_cmd = {}
    for cmd in commands:
        if cmd.block < 0 or cmd.block >= len(script_ids) or cmd.offset in pos_to_cmd:
            raise ValueError('Offset/comando fuera de tabla o duplicado')
        pos_to_cmd[cmd.offset] = cmd
    op0a = 0
    id_matches = 0
    matched_ids = set()
    external_intro = []
    relative_motifs = Counter()
    op02_field_values = {2:Counter(), 6:Counter()}
    opcode_counts = Counter()
    for cmd in commands:
        if cmd.content is not None:
            continue
        opcode = cmd.code
        opcode_counts[opcode] += 1
        p = cmd.raw[5:]
        if opcode in (0x01, 0x0A) and len(p) != 4:
            raise ValueError('Longitud de argumento no esperada para 0x01/0x0A')
        if opcode == 0x02 and len(p) != 18:
            raise ValueError('Longitud de argumento no esperada para 0x02')
        if opcode == 0x0A:
            op0a += 1
            v = struct.unpack_from('<I',p,0)[0]
            if v in idset:
                id_matches += 1
                matched_ids.add(v)
                if v in (script_ids[i] for i in intro) and cmd.block not in intro:
                    target = script_ids.index(v)
                    external_intro.append({
                        'source_block':cmd.block,'source_script_id':script_ids[cmd.block],
                        'source_script_name':names[cmd.block], 'source_order':cmd.order,
                        'source_command_offset':cmd.offset,'instruction_id':cmd.instruction_id,
                        'operand_u32':v, 'target_block':target,'target_script_name':names[target],
                        'target_block_offset':starts[target]})
        if opcode == 0x02:
            for j in (2,6):op02_field_values[j][struct.unpack_from('<I',p,j)[0]]+=1
        if cmd.block in intro and opcode in (0x01,0x02):
            for j in ((0,) if opcode == 0x01 else (2,6)):
                v = struct.unpack_from('<I',p,j)[0]
                if v == 0:continue
                target = pos_to_cmd.get(starts[cmd.block]+v)
                if target is not None and target.block == cmd.block:
                    relative_motifs[(cmd.block,opcode,j,v,target.order,target.code)] += 1
    return {
        'nontext_opcode_counts_selected':{f'0x{k:02x}':opcode_counts[k] for k in (1,2,10)},
        'opcode_0a_u32_script_id_matches':id_matches,
        'opcode_0a_total_commands':op0a,
        'opcode_0a_unique_existing_script_ids':len(matched_ids),
        'opcode_0a_external_demo1001_candidates':sorted(external_intro,key=lambda x:(x['source_block'],x['source_order'])),
        'intro_relative_numeric_matches_total':sum(relative_motifs.values()),
        'intro_relative_numeric_motifs':[{
            'source_block':b,'opcode':f'0x{op:02x}','argument_byte_offset':j,
            'operand_u32':v,'coincident_target_order':t,'coincident_target_opcode':f'0x{tc:02x}',
            'occurrences':n}
            for (b,op,j,v,t,tc),n in sorted(relative_motifs.items())],
        'opcode_02_field_2_common_values':[{'value':v,'count':n} for v,n in op02_field_values[2].most_common(5)],
        'opcode_02_field_6_common_values':[{'value':v,'count':n} for v,n in op02_field_values[6].most_common(5)],
        'MIPS_semantics_proven':False,'relocation_authorized':False,
        'meaning':'Solo coincidencias estáticas. Cualquier referencia debe confirmarse observando el intérprete PSP MIPS en ejecución.'
    }

def audit(iso):
    try:
        from tools.f3_referencias_riesgo import original_script_children
        from tools.script_event_guard import read_commands
    except ModuleNotFoundError:
        from f3_referencias_riesgo import original_script_children
        from script_event_guard import read_commands
    script, table = original_script_children(Path(iso))
    if hashlib.sha256(script).hexdigest() != SCRIPT_SHA or hashlib.sha256(table).hexdigest() != TABLE_SHA:
        raise ValueError('SCRIPT.DAT/TBL no original')
    cmds, starts = read_commands(script, table)
    if len(cmds) != 51705 or len(starts) != 1626:
        raise ValueError('Cantidad de comandos/bloques no original')
    ids = [struct.unpack_from('<I',table,16+32*i)[0] for i in range(1625)]
    names = [table[16+32*i+8:16+32*i+32].split(b'\0',1)[0].decode('ascii','strict') for i in range(1625)]
    result = profile(cmds,starts,ids,names)
    expected = (862,320,183,21,6,4061,2039)
    actual = (result['opcode_0a_total_commands'],result['opcode_0a_u32_script_id_matches'],
              result['opcode_0a_unique_existing_script_ids'],result['intro_relative_numeric_matches_total'],
              len(result['intro_relative_numeric_motifs']),result['nontext_opcode_counts_selected']['0x01'],
              result['nontext_opcode_counts_selected']['0x02'])
    if actual != expected or len(result['opcode_0a_external_demo1001_candidates']) != 1:
        raise ValueError(f'Ancla de auditoría F4-R9 no coincide: {actual}')
    return {'schema':'cladun.f4.r9_opcode_operands_readonly.v1',
            'source':'A_AUTHENTIC_USA_ORIGINAL_STATIC_NOT_PPSSPP',
            'iso_sha256':ISO_SHA,'script_dat_sha256':SCRIPT_SHA,
            'script_tbl_sha256':TABLE_SHA,'script_blocks':1625,
            'commands':51705,'nontext_commands':46308,
            'intro_blocks':7,'intro_commands':878,
            **result,'original_iso_modified':False,
            'commercial_resource_bytes_written':False,'ppsspp_executed':False}

def main():
    try:
        from tools.f3_referencias_riesgo import report_path
    except ModuleNotFoundError:
        from f3_referencias_riesgo import report_path
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iso-original',required=True,type=Path)
    ap.add_argument('--reporte-privado',required=True,type=Path)
    a=ap.parse_args()
    target=report_path(a.reporte_privado)
    result=audit(a.iso_original)
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('x',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'original_iso_verified':True,
      '0x0a_id_matches':result['opcode_0a_u32_script_id_matches'],
      'intro_relative_motifs':len(result['intro_relative_numeric_motifs']),
      'MIPS_semantics_proven':False,'relocation_authorized':False}))

if __name__=='__main__':main()
