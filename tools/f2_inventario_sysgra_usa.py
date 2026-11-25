#!/usr/bin/env python3
"""F2: inventario de METADATOS SYSGRA.ARC verificado contra ISO USA.

Solo lectura. No exporta píxeles, paletas, RAM, texturas ni archivos IMY.
Los nombres sugieren posibles contextos, NO demuestran uso en PPSSPP.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from pathlib import Path

try:
    from tools.f2_auditar_origen_iconos import (
        ISO_SHA256, IMY_SHA256, locate_data, pspfs_entries, dsarc_entries,
    )
except ModuleNotFoundError:
    from f2_auditar_origen_iconos import (
        ISO_SHA256, IMY_SHA256, locate_data, pspfs_entries, dsarc_entries,
    )

EXPECTED_ISO_SIZE = 305496064
EXPECTED_PSPFS = 349
EXPECTED_SYS_INDEX = 225
EXPECTED_SYS_OFFSET = 895488
EXPECTED_SYS_SIZE = 93696
EXPECTED_MEMBERS = 27
EXPECTED_ICON_INDEX = 17
EXPECTED_ICON_OFFSET = 57856
EXPECTED_ICON_LENGTH = 2480
EXPECTED_ICON_ABSOLUTE = 114723840

def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def source_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()

def inspect_dsarc(archive: bytes, *, expected_count: int=EXPECTED_MEMBERS) -> list[dict]:
    """Parse structural metadata from an already isolated DSARC. No image decoding."""
    records = dsarc_entries(archive)
    if len(records) != expected_count:
        raise ValueError('Número DSARC inesperado')
    if len({r['name'] for r in records}) != len(records):
        raise ValueError('Nombres DSARC duplicados')
    table_end = 16 + expected_count * 48 if archive[:8] == b'DSARC FL' else (
        ((16 + expected_count * 2 + 3) // 4) * 4 + expected_count * 48)
    if any(r['offset'] < table_end for r in records):
        raise ValueError('DSARC member overlaps directory')
    spans = sorted((r['offset'], r['offset'] + r['size']) for r in records)
    if any(b > c for (_, b), (c, _) in zip(spans, spans[1:])):
        raise ValueError('DSARC members overlap')
    output = []
    for member in records:
        raw = archive[member['offset']:member['offset'] + member['size']]
        if len(raw) != member['size'] or len(raw) < 16 or raw[:4] != b'IMY\0':
            raise ValueError('Miembro no es IMY o truncado')
        stride = struct.unpack_from('<H', raw, 8)[0]
        rows = struct.unpack_from('<H', raw, 12)[0]
        if not 0 < stride <= 4096 or not 0 < rows <= 4096:
            raise ValueError('Dimensiones IMY fuera de rango')
        name = member['name']
        if name.startswith(('HP_', 'EXP_', 'MAHO_', 'LVSP')) or name in ('DAMAGE.IMY', 'SYS1.IMY', 'ZOKUSEI.IMY'):
            hint = 'nombre_sugiere_HUD_o_combate_NO_PROBADO'
        else:
            hint = 'contexto_visual_DESCONOCIDO'
        output.append({
            'dsarc_index': member['index'],
            'name': name,
            'offset_within_sysgra': member['offset'],
            'stored_length': member['size'],
            'sha256': sha256_bytes(raw),
            'imy_header_stride_bytes': stride,
            'imy_header_rows': rows,
            'context_hint_only': hint,
            'rendered_in_ppsspp_proven': False,
        })
    return output

def inventory(iso: Path) -> dict:
    """Authenticates full source before collecting 27 member metadata rows."""
    iso = Path(iso)
    if iso.stat().st_size != EXPECTED_ISO_SIZE:
        raise ValueError('Tamaño de ISO USA no coincide')
    digest = source_hash(iso)
    if digest != ISO_SHA256:
        raise ValueError('SHA-256 ISO USA no coincide')
    data_record = locate_data(iso)
    with iso.open('rb') as stream:
        stream.seek(data_record['offset'])
        dat = stream.read(data_record['size'])
    if len(dat) != data_record['size']:
        raise ValueError('DATA.DAT truncado')
    items = pspfs_entries(dat)
    if len(items) != EXPECTED_PSPFS:
        raise ValueError('PSPFS no tiene 349 miembros')
    sys = items[EXPECTED_SYS_INDEX]
    if (sys['name'], sys['offset'], sys['size_stored']) != (
        'SYSGRA.ARC', EXPECTED_SYS_OFFSET, EXPECTED_SYS_SIZE
    ):
        raise ValueError('SYSGRA.ARC no coincide con los bytes USA autenticados')
    arc = dat[sys['offset']:sys['offset'] + sys['size_stored']]
    rows = inspect_dsarc(arc)
    icon = rows[EXPECTED_ICON_INDEX]
    if (icon['name'], icon['offset_within_sysgra'], icon['stored_length'], icon['sha256']) != (
        'KITAJIMA_KARI.IMY', EXPECTED_ICON_OFFSET, EXPECTED_ICON_LENGTH, IMY_SHA256
    ):
        raise ValueError('KITAJIMA no coincide con firma original')
    absolute = data_record['offset'] + sys['offset'] + icon['offset_within_sysgra']
    if absolute != EXPECTED_ICON_ABSOLUTE:
        raise ValueError('Desplazamiento ISO KITAJIMA no coincide')
    return {
        'schema': 'cladun.f2.sysgra_members_readonly.2026-11-22.v1',
        'scope': 'REAL_USA_ISO_STATIC_MEMBER_INDEX_NOT_RUNTIME_PROVENANCE',
        'original_iso_sha256': digest,
        'original_iso_size': iso.stat().st_size,
        'data_iso_offset': data_record['offset'],
        'pspfs_members_count': len(items),
        'sysgra_index_pspfs': EXPECTED_SYS_INDEX,
        'sysgra_offset_in_data': EXPECTED_SYS_OFFSET,
        'sysgra_length': len(arc),
        'sysgra_sha256': sha256_bytes(arc),
        'dsarc_members_count': len(rows),
        'all_members_are_individually_hashed': True,
        'unique_member_sha256_count': len({x['sha256'] for x in rows}),
        'kitajima_index': EXPECTED_ICON_INDEX,
        'kitajima_absolute_iso_offset': absolute,
        'kitajima_sha256': icon['sha256'],
        'context_assignments_runtime_proven': False,
        'mips_ram_ge_vram_proven': False,
        'members': rows,
    }

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iso-usa', type=Path, required=True)
    ap.add_argument('--reporte', type=Path, required=True)
    args = ap.parse_args()
    result = inventory(args.iso_usa)
    args.reporte.parent.mkdir(parents=True, exist_ok=True)
    with args.reporte.open('x', encoding='utf-8') as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write('\n')
    print(json.dumps({
        'schema': result['schema'],
        'member_count': result['dsarc_members_count'],
        'sysgra_sha256': result['sysgra_sha256'],
        'kitajima_sha256': result['kitajima_sha256'],
        'runtime_proven': False,
    }, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
