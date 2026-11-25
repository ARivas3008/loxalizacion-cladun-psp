#!/usr/bin/env python3
"""R12: clasificar operandos 0A/0B/0C en IDs-100 y valores sin ID.

Metadatos únicamente. No interpreta ejecución MIPS, no modifica ISO.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import struct

OPS = {0x0A: 4, 0x0B: 5, 0x0C: 4}
EXPECTED = {0x0A: (862, 860, {0: 1, 1: 1}),
            0x0B: (166, 158, {3: 8}),
            0x0C: (102, 66, {100: 36})}
ISO_SHA = 'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'


def categorize(commands, ids, names):
    if len(ids) != len(names) or len(set(ids)) != len(ids) or not ids:
        raise ValueError('SCRIPT.TBL invalido')
    look = {value: i for i, value in enumerate(ids)}
    grouped = {op: {'total': 0, 'matched_id_minus100': 0,
                    'unmatched': Counter(), 'unmatched_sources': [],
                    'target_ids': set(), 'flags': Counter(),
                    'flag_by_match': Counter()} for op in OPS}
    seen_offsets = set()
    anchor = []
    for c in commands:
        if not 0 <= c.block < len(ids) or c.offset in seen_offsets:
            raise ValueError('Comando fuera de tabla o duplicado')
        seen_offsets.add(c.offset)
        if c.content is not None or c.code not in OPS:
            continue
        expected_size = OPS[c.code]
        if len(c.raw) != 5 + expected_size or struct.unpack_from('<H', c.raw, 3)[0] != expected_size:
            raise ValueError('Cabecera o longitud incorrecta de argumento')
        val = struct.unpack_from('<I', c.raw, 5)[0]
        category = grouped[c.code]
        category['total'] += 1
        match = val >= 100 and val - 100 in look
        if match:
            category['matched_id_minus100'] += 1
            category['target_ids'].add(val - 100)
        else:
            category['unmatched'][val] += 1
            category['unmatched_sources'].append({'value': val,
                'source_block': c.block, 'source_script_name': names[c.block],
                'source_order': c.order, 'command_offset': c.offset})
        if c.code == 0x0B:
            flag = c.raw[9]
            category['flags'][flag] += 1
            category['flag_by_match'][(flag, 'matches_id' if match else 'unmatched')] += 1
        if (c.block, c.order, c.offset, c.code, c.instruction_id, val) == (20,20,7420,0x0A,818,100100):
            anchor.append({'source_block':20,'source_order':20,'offset':7420,
              'value':val, 'target_id_if_minus100':100000,
              'target_block_if_minus100':look.get(100000),
              'target_block_if_literal':look.get(100100)})
    result = {}
    for op, d in grouped.items():
        result[f'0x{op:02X}'] = {
            'commands':d['total'],
            'matches_id_after_minus100':d['matched_id_minus100'],
            'distinct_matched_ids':len(d['target_ids']),
            'nonmatches_by_operand':{str(k):v for k,v in sorted(d['unmatched'].items())},
            'nonmatch_command_metadata':d['unmatched_sources'],
            'trailing_byte_counts':{str(k):v for k,v in sorted(d['flags'].items())},
            'trailing_byte_by_match':{f'{flag}:{kind}':cnt for (flag,kind),cnt in sorted(d['flag_by_match'].items())},
            'unclassified_values_count':len(d['unmatched_sources']),
            'candidate_special_meaning_proven':False}
    return {'opcode_profiles':result,'anchor':anchor,
        'classification':'MATCHED_ID_MINUS100_OR_UNMATCHED_VALUE; special semantics unknown',
        'mips_semantics_proven':False,'relocalization_authorized':False}


def audit(iso):
    try:
        from tools.f3_referencias_riesgo import original_script_children
        from tools.script_event_guard import read_commands
    except ModuleNotFoundError:
        from f3_referencias_riesgo import original_script_children
        from script_event_guard import read_commands
    dat, tbl = original_script_children(iso)
    cmds, starts = read_commands(dat, tbl)
    if len(cmds) != 51705 or len(starts) != 1626 or sum(c.content is None for c in cmds) != 46308:
        raise ValueError('Recuento original distinto')
    ids = [struct.unpack_from('<I', tbl, 16 + i*32)[0] for i in range(1625)]
    names = [tbl[16+i*32+8:16+(i+1)*32].split(b'\0',1)[0].decode('ascii','strict') for i in range(1625)]
    result = categorize(cmds, ids, names)
    for op,(count,matches,unmatched) in EXPECTED.items():
        x=result['opcode_profiles'][f'0x{op:02X}']
        obs={int(k):v for k,v in x['nonmatches_by_operand'].items()}
        if (x['commands'],x['matches_id_after_minus100'],obs)!=(count,matches,unmatched):
            raise ValueError('Ancla F4-R12 inesperada')
    if len(result['anchor']) != 1 or (result['anchor'][0]['target_block_if_minus100'],result['anchor'][0]['target_block_if_literal']) != (757,758):
        raise ValueError('Ancla R11 757/758 inesperada')
    if result['opcode_profiles']['0x0B']['trailing_byte_by_match'] != {'100:matches_id':104,'100:unmatched':8,'101:matches_id':54}:
        raise ValueError('Flags 0B inesperados')
    return {'schema':'cladun.f4.r12_operand_exceptions.v1','evidence':'A_ORIGINAL_ISO_STATIC_NOT_PPSSPP',
        'iso_sha256':ISO_SHA,'script_dat_sha256':'c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358',
        'script_tbl_sha256':'f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37',
        'script_blocks':1625,'commands':51705,'nontext_commands':46308,
        **result,'ppsspp_executed':False,'original_modified':False,'commercial_data_emitted':False}

def main():
    try:from tools.f3_referencias_riesgo import report_path
    except ModuleNotFoundError:from f3_referencias_riesgo import report_path
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iso-original',type=Path,required=True)
    ap.add_argument('--reporte-privado',type=Path,required=True)
    args=ap.parse_args()
    dest=report_path(args.reporte_privado)
    report=audit(args.iso_original)
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('x',encoding='utf-8') as f:
        json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'counts':{k:(v['commands'],v['matches_id_after_minus100'],v['nonmatches_by_operand']) for k,v in report['opcode_profiles'].items()},'C':False,'relocation':False}))
if __name__=='__main__':main()
