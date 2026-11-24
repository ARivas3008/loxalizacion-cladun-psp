#!/usr/bin/env python3
"""F4 R14: manifest of exact ORIGINAL SCRIPT.DAT observation points.

A static, read-only instrument-placement aid. Never asserts MIPS control flow.
No original payloads or text are exported.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import struct

ISO_SHA = 'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
# (block, order, opcode, expected_u32, target_script_block_if_minus_100)
PROBES = (
    (20, 20, 0x0A, 100100, 757),
    (757, 2, 0x0A, 100200, 758),
    (758, 1, 0x0C, 100290, 759),
    (758, 415, 0x0C, 100, None),
    (758, 416, 0x0A, 100201, 760),
    (759, 23, 0x0C, 100, None),
    (760, 1, 0x0C, 100291, 761),
    (760, 336, 0x0C, 100, None),
    (761, 23, 0x0C, 100, None),
)

def build_manifest(commands, ids, names, starts, probes=PROBES):
    if not ids or len(ids) != len(names) or len(starts) != len(ids) + 1:
        raise ValueError('Invalid SCRIPT.TBL dimensions')
    if len(set(ids)) != len(ids) or starts != sorted(starts):
        raise ValueError('Duplicate script IDs / invalid block order')
    keyset = set(); lookup = {}
    for c in commands:
        if (c.block, c.order) in keyset or not 0 <= c.block < len(ids):
            raise ValueError('Duplicate command or invalid block')
        keyset.add((c.block, c.order))
        if not starts[c.block] <= c.offset < starts[c.block + 1]:
            raise ValueError('Command offset outside block')
        lookup[(c.block, c.order)] = c
    result = []
    if len(set((b,o) for b,o,*_ in probes)) != len(probes):
        raise ValueError('Duplicate probe')
    id_to_block = {v:i for i,v in enumerate(ids)}
    for block,order,opcode,value,target in probes:
        c = lookup.get((block,order))
        if c is None or c.content is not None or c.code != opcode:
            raise ValueError(f'Missing or altered nontext command {block}/{order}')
        arg_size = 4 if opcode in (0x0A,0x0C) else 5
        if len(c.raw) != 5 + arg_size or struct.unpack_from('<H',c.raw,3)[0] != arg_size:
            raise ValueError(f'Invalid original command argument size {block}/{order}')
        actual = struct.unpack_from('<I',c.raw,5)[0]
        if value != actual:
            raise ValueError(f'Wrong u32 at {block}/{order}')
        actual_target = id_to_block.get(value - 100) if value >= 100 else None
        if actual_target != target:
            raise ValueError(f'Candidate ID+100 target has changed {block}/{order}')
        result.append({
            'block':block,'script_id':ids[block], 'script_name':names[block],
            'order':order,'script_dat_offset_decimal':c.offset,
            'script_dat_offset_hex':f'0x{c.offset:06X}',
            'opcode':f'0x{opcode:02X}', 'instruction_id':c.instruction_id,
            'operand_u32':value,'candidate_id_minus100':value-100 if target is not None else None,
            'candidate_target_block':target,
            'literal_target_block':id_to_block.get(value),
            'event_semantics_verified':False,
            'ram_address':None,'mips_pc':None,
        })
    return {'schema':'cladun.f4.r14_probe_manifest.v1',
        'evidence':'A_STATIC_AUTHENTIC_ISO_NOT_PPSSPP',
        'iso_original_sha256':ISO_SHA,'probe_count':len(result),'probes':result,
        'mips_execution_verified':False,'patching_allowed':False,
        'note':'Offsets are within decompressed SCRIPT.DAT, NOT PSP memory addresses.'}

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
        raise ValueError('Original command counts incorrect')
    ids=[struct.unpack_from('<I',table,16+32*i)[0] for i in range(1625)]
    names=[table[16+32*i+8:16+32*(i+1)].split(b'\x00',1)[0].decode('ascii','strict') for i in range(1625)]
    result=build_manifest(commands,ids,names,starts)
    expected_offsets=(7420,218095,218133,223351,223360,223602,223637,227968,228194)
    if tuple(p['script_dat_offset_decimal'] for p in result['probes'])!=expected_offsets:
        raise ValueError('R14 original offset anchors do not match')
    return result

def main():
    try:from tools.f3_referencias_riesgo import report_path
    except ModuleNotFoundError:from f3_referencias_riesgo import report_path
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iso-original',required=True,type=Path)
    ap.add_argument('--reporte-privado',required=True,type=Path)
    args=ap.parse_args()
    target=report_path(args.reporte_privado)
    result=audit_original(args.iso_original)
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
    print(json.dumps({'authenticated_original_probes':len(result['probes']),
        'mips_execution_verified':False,'patching_allowed':False}))
if __name__=='__main__':main()
