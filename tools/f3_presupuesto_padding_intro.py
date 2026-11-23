#!/usr/bin/env python3
"""F3-R6: presupuesto de padding de 7 bloques demo1001, NO reubicador.

Combina una lectura previa autenticada de ISO (solo metadatos) con la huella
criptográfica ISO↔CSV F3-R5. Puede revalidar la ISO PRIVADA, pero CI no la
requiere. No escribe SCRIPT.DAT, no interpreta MIPS, no autoriza insertar.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

try:
    from tools import f3_anclar_intro as anchor
    from tools.f3_referencias_riesgo import original_script_children
    from tools.script_event_guard import read_commands
except ModuleNotFoundError:
    import f3_anclar_intro as anchor
    from f3_referencias_riesgo import original_script_children
    from script_event_guard import read_commands

PADDING_REL = Path('reports/F3_DEMO1001_PADDING_ORIGINAL_2026-11-23.json')
# Metadatos derivados de la ISO original por lectura independiente, no bytes.
EXPECTED_ROWS = (
    (757,100000,218080,218128,218114,14),
    (758,100100,218128,223408,223397,11),
    (759,100190,223408,223632,223629,3),
    (760,100101,223632,228000,227987,13),
    (761,100191,228000,228240,228238,2),
    (762,100110,228240,228576,228572,4),
    (763,100120,228576,228992,228991,1),
)
EXPECTED_SCRIPT_SHA = 'c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358'
EXPECTED_TABLE_SHA = 'f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37'


def validate_padding(padding: dict, geometry: dict, *, canonical: bool = True) -> list[tuple]:
    if padding.get('schema') != 'cladun.f3.intro_original_padding_compact.v1':
        raise ValueError('Esquema padding no reconocido')
    if (padding.get('original_iso_sha256') != anchor.ISO_SHA256 or
        padding.get('script_dat_sha256') != EXPECTED_SCRIPT_SHA or
        padding.get('script_tbl_sha256') != EXPECTED_TABLE_SHA):
        raise ValueError('Padding no ligado a ISO/SCRIPT original autenticados')
    blocks = anchor.check_geometry(geometry, require_canonical=canonical)
    rows = [tuple(item) for item in padding['padding_rows']]
    if len(rows) != len(blocks) or len({x[0] for x in rows}) != len(rows):
        raise ValueError('Duplicados o faltan bloques')
    if canonical and tuple(rows) != EXPECTED_ROWS:
        raise ValueError('Geometría de padding distinta de ISO original')
    for item in rows:
        if len(item) != 6 or not all(type(n) is int for n in item):
            raise ValueError('Fila de padding malformada')
        block_idx,sid,start,limit,last_end,tail = item
        b = blocks.get(block_idx)
        if (not b or sid != b['script_id'] or start != b['source_start'] or
            limit != b['source_end'] or not 0 < limit - start or
            not start < last_end <= limit or tail != limit-last_end or
            (limit-start) % 16):
            raise ValueError('Padding/end de bloque no coincide con metadatos canónicos')
    return rows


def project_capacity(padding: dict, geometry: dict, projected: list[dict], *, canonical: bool = True) -> dict:
    rows = validate_padding(padding, geometry, canonical=canonical)
    plans = {p['script_id']:p for p in projected}
    if len(plans) != len(rows):
        raise ValueError('Faltan/duplican scripts de la proyección')
    result=[]
    for idx,sid,start,limit,last_end,tail in rows:
        plan=plans.get(sid)
        if not plan or plan['source_commands'] != {b['block_index']:b['command_count'] for b in geometry['blocks']}[idx]:
            raise ValueError('Cantidad de comandos por script no coincide')
        delta=plan['net_text_byte_delta']
        if type(delta) is not int:
            raise ValueError('Delta no entero')
        original_used = last_end-start
        original_capacity = limit-start
        hypothetical_used = original_used+delta
        if hypothetical_used <= 0:
            raise ValueError('La proyección borraría todas las instrucciones')
        hypothetical_aligned = (hypothetical_used+15)//16*16
        extra = max(0,hypothetical_aligned-original_capacity)
        fit = hypothetical_used <= original_capacity
        result.append({
            'block_index':idx,'script_id':sid,'source_commands':plan['source_commands'],
            'original_allocation_bytes':original_capacity,'original_zero_tail_bytes':tail,
            'net_spanish_text_delta_bytes':delta,
            'hypothetical_used_bytes':hypothetical_used,
            'hypothetical_aligned_required_bytes':hypothetical_aligned,
            'would_fit_existing_block_allocation':fit,
            'minimum_additional_capacity_bytes_if_individually_aligned':extra,
            'hypothetical_internal_command_start_changes':plan['hypothetical_commands_with_changed_start'],
            'model_internal_offsets_not_shifted': plan['hypothetical_commands_with_changed_start'] == 0 and extra == 0,
        })
    totals={
        'original_trailing_padding_bytes':sum(r['original_zero_tail_bytes'] for r in result),
        'original_allocated_bytes':sum(r['original_allocation_bytes'] for r in result),
        'net_spanish_text_delta_bytes':sum(r['net_spanish_text_delta_bytes'] for r in result),
        'blocks_that_cannot_fit_existing_allocation':sum(not r['would_fit_existing_block_allocation'] for r in result),
        'min_additional_capacity_if_each_block_individually_16_aligned':sum(r['minimum_additional_capacity_bytes_if_individually_aligned'] for r in result),
        'hypothetical_internal_command_start_changes':sum(r['hypothetical_internal_command_start_changes'] for r in result),
    }
    if canonical and (totals['original_trailing_padding_bytes'] != 48 or
        totals['net_spanish_text_delta_bytes'] != 131 or
        totals['blocks_that_cannot_fit_existing_allocation'] != 3 or
        totals['min_additional_capacity_if_each_block_individually_16_aligned'] != 144 or
        totals['hypothetical_internal_command_start_changes'] != 588):
        raise ValueError('La geometría o la traducción cambió respecto a ISO autenticada')
    return {
        'schema':'cladun.f3.intro_padding_budget.v1',
        'rows':result,'totals':totals,
        'interpretation':'Modelo de concatenación lineal por bloque, con alineación de 16 bytes; NO es un modelo de control de flujo MIPS.',
        'new_iso_size_established':False,'external_references_repaired':False,
        'all_85_intro_variable_length_entries_blocked':True,
        'relocation_authorized':False,'ppsspp_runtime_proven':False,
    }


def verify_iso_padding(iso:Path, padding:dict, geometry:dict)->dict:
    rows = validate_padding(padding,geometry)
    script,table=original_script_children(iso)
    commands,starts=read_commands(script,table)
    byblock={}
    target_blocks={r[0] for r in rows}
    for cmd in commands:
        if cmd.block in target_blocks:
            byblock.setdefault(cmd.block, []).append(cmd)
    for idx, sid, start, limit, end, tail in rows:
        seq=byblock.get(idx)
        if not seq or starts[idx:idx+2] != [start,limit]:
            raise ValueError('Script original no coincide con geometría de padding')
        last=seq[-1]
        if last.offset+len(last.raw)!=end or any(script[end:limit]):
            raise ValueError('El padding privado no consiste íntegramente en ceros')
    return {'original_iso_static_authenticated':True,'script_blocks_checked':len(rows),
            'last_command_offsets_confirmed':True,'trailing_padding_all_zero':True,
            'ppsspp_gameplay_executed':False}


def audit(draft:Path, geometry_path:Path, padding_path:Path, iso:Path|None=None) -> dict:
    geometry=anchor.load_geometry(geometry_path)
    padding=json.loads(padding_path.read_text(encoding='utf-8'))
    csv_rows, csv_blob_sha=anchor.read_draft(draft)
    if csv_blob_sha!=anchor.DRAFT_BLOB_SHA1:
        raise ValueError('Borrador canónico editado sin revisión')
    projection=anchor.evaluate_rows(csv_rows,geometry)
    capacity=project_capacity(padding,geometry,projection['simple_concat_projection'])
    return {
        'evidence':'A_SOURCE_ISO_GEOMETRY_B_REAL_CSV_AND_SYNTHETIC_C_PPSSPP_NOT_EXECUTED',
        'source_and_order_sha256':projection['source_root_sha256'],
        'draft_git_blob_sha1':csv_blob_sha,
        'original_iso_sha256':anchor.ISO_SHA256,
        'original_iso_reverified_this_run':iso is not None,
        'iso_verification':verify_iso_padding(iso,padding,geometry) if iso else None,
        **capacity,
        'corpus_rows':projection['total_draft_rows'],
        'intro_spanish_entries':projection['intro_rows'],
        'blocked_variable_length':projection['change_counts']['unequal'],
        'commercial_content_published':False,
    }


def main()->None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--borrador-es',type=Path,default=anchor.DRAFT_REL)
    ap.add_argument('--geometria',type=Path,default=anchor.GEOMETRY_REL)
    ap.add_argument('--padding',type=Path,default=PADDING_REL)
    ap.add_argument('--iso-original',type=Path)
    ap.add_argument('--reporte-privado',type=Path)
    args=ap.parse_args()
    result=audit(args.borrador_es,args.geometria,args.padding,args.iso_original)
    if args.reporte_privado:
        try:
            from tools.f3_referencias_riesgo import report_path
        except ModuleNotFoundError:
            from f3_referencias_riesgo import report_path
        output=report_path(args.reporte_privado)
        output.parent.mkdir(parents=True,exist_ok=True)
        with output.open('x',encoding='utf-8') as f:
            json.dump(result,f,ensure_ascii=False,indent=2)
            f.write('\n')
    print(json.dumps({'total_blocks':len(result['rows']), 'verified_iso':result['original_iso_reverified_this_run'],
        'does_not_fit':result['totals']['blocks_that_cannot_fit_existing_allocation'],
        'minimum_block_capacity_addition':result['totals']['min_additional_capacity_if_each_block_individually_16_aligned'],
        'relocation_authorized':False}))


if __name__=='__main__':main()
