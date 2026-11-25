#!/usr/bin/env python3
"""F4: localizar coincidencias u32 en comandos contra demo1001 ORIGINAL.

Solo metadatos. Una coincidencia numérica NO es referencia MIPS ni salto.
Nunca escribe ISO, SCRIPT.DAT, texto, recursos ni volcado de RAM.
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


def scan_numeric_matches(commands, starts, ids, names):
    """Censo exacto de igualdades u32: no deduce semántica de opcodes."""
    if len(starts) != len(ids)+1 or len(ids) != len(names):
        raise ValueError('Tabla inconsistente')
    intro = {i for i, n in enumerate(names) if n in INTRO_NAMES}
    if not intro:
        raise ValueError('No hay bloques demo1001')
    pos_to_block = {c.offset: c.block for c in commands}
    if len(pos_to_block) != len(commands):
        raise ValueError('Offsets de comando duplicados')
    intro_starts = {starts[i] for i in intro if starts[i] != 0}
    intro_cmd = {p for p, block in pos_to_block.items() if block in intro}
    intro_ids = {ids[i] for i in intro if ids[i] != 0}
    by_class, by_origin, signatures, alignments = Counter(), Counter(), Counter(), Counter()
    windows = 0
    for cmd in commands:
        if cmd.content is not None:
            continue
        if cmd.block < 0 or cmd.block >= len(ids):
            raise ValueError('Bloque fuera de tabla')
        payload = cmd.raw[5:]
        for j in range(max(0, len(payload)-3)):
            value = struct.unpack_from('<I', payload, j)[0]
            windows += 1
            if value == 0:
                continue
            matched=[]
            if value in intro_cmd:
                matched.append('u32_igual_inicio_comando_demo1001')
            if value in intro_starts:
                matched.append('u32_igual_inicio_bloque_demo1001')
            if value in intro_ids:
                matched.append('u32_igual_ID_script_demo1001')
            if cmd.block in intro:
                candidate = starts[cmd.block]+value
                if candidate in pos_to_block and pos_to_block[candidate] == cmd.block:
                    matched.append('u32_igual_offset_relativo_comando_mismo_bloque')
            for kind in matched:
                by_class[kind] += 1
                by_origin[(kind, 'desde_demo1001' if cmd.block in intro else 'desde_otros_scripts')] += 1
                signatures[(kind, f'0x{cmd.code:02x}', j)] += 1
                alignments[(kind, j % 4)] += 1
    return {
        'u32_windows_nontext_inspected': windows,
        'intro_blocks':len(intro),
        'intro_commands':sum(c.block in intro for c in commands),
        'candidate_counts':dict(sorted(by_class.items())),
        'candidate_source_scope':[
            {'class':a, 'origin':b, 'hits':n}
            for (a,b),n in sorted(by_origin.items())],
        'candidate_opcode_payload_offset':[
            {'class':a, 'opcode':b, 'payload_byte_offset':c, 'hits':n}
            for (a,b,c),n in sorted(signatures.items())],
        'candidate_payload_alignment_mod4':[
            {'class':a, 'payload_offset_mod4':b, 'hits':n}
            for (a,b),n in sorted(alignments.items())],
        'note':'Igualdad numérica u32 (todas alineaciones); NO demuestra referencias, PCs MIPS ni opcodes de control de flujo.',
        'semantic_MIPS_verified': False, 'relocation_authorized':False,
    }


def audit_original(iso):
    try:
        from tools.f3_referencias_riesgo import original_script_children
        from tools.script_event_guard import read_commands
    except ModuleNotFoundError:
        from f3_referencias_riesgo import original_script_children
        from script_event_guard import read_commands
    script, table = original_script_children(Path(iso))
    commands, starts = read_commands(script, table)
    if hashlib.sha256(script).hexdigest() != SCRIPT_SHA or hashlib.sha256(table).hexdigest() != TABLE_SHA:
        raise ValueError('SCRIPT.DAT/TBL distintos de la ISO original')
    if len(commands) != 51705 or sum(c.content is None for c in commands) != 46308:
        raise ValueError('Número de comandos inesperado')
    if len(starts) != 1626:
        raise ValueError('Número de bloques inesperado')
    ids = [struct.unpack_from('<I',table,16+32*i)[0] for i in range(1625)]
    names = [table[16+32*i+8:16+32*i+32].split(b'\x00')[0].decode('ascii','strict') for i in range(1625)]
    result=scan_numeric_matches(commands,starts,ids,names)
    if result['intro_blocks'] != 7 or result['intro_commands'] != 878:
        raise ValueError('demo1001 no coincide con el original')
    return {
        'schema':'cladun.f4.demo1001_numeric_matches.v1',
        'evidence':'A_AUTHENTIC_ORIGINAL_ISO_STATIC_NOT_PPSSPP',
        'usa_original_sha256':ISO_SHA,
        'script_dat_sha256':SCRIPT_SHA,
        'script_tbl_sha256':TABLE_SHA,
        'commands':51705,'nontext_commands':46308,'script_blocks':1625,
        **result, 'ppsspp_executed':False,
        'source_iso_modified':False,'game_assets_in_report':False,
        'global_deferred_text_changes':4524,
    }


def main():
    try:
        from tools.f3_referencias_riesgo import report_path
    except ModuleNotFoundError:
        from f3_referencias_riesgo import report_path
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iso-original',type=Path,required=True)
    ap.add_argument('--reporte-privado',type=Path,required=True)
    args=ap.parse_args()
    dest=report_path(args.reporte_privado)
    result=audit_original(args.iso_original)
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('x',encoding='utf-8') as out:
        json.dump(result,out,indent=2,ensure_ascii=False)
        out.write('\n')
    print(json.dumps({'iso_sha256':ISO_SHA,'candidates':result['candidate_counts'],
                      'mips_verified':False,'reallocation_authorized':False},ensure_ascii=False))


if __name__=='__main__':main()
