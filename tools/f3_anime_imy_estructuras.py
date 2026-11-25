#!/usr/bin/env python3
"""Auditor F3 SOLO LECTURA de cabeceras IMY ANIME en ISO USA autenticada.

Aporta metadatos y un ensayo de compatibilidad de las banderas con el algoritmo
IMY convencional. Un PASS no confirma geometría, paleta ni procedencia visual;
un FAIL impide reutilizar el decodificador sin estudiar el formato. No crea PNG.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
from collections import Counter
from pathlib import Path

SHA_USA = 'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
SIZE_USA = 305496064
DATA_ISO_OFF = 113770496
DATA_SIZE = 191697408
EXPECTED = {234: ('ANIME000.IDT', 3537936, 231),
            235: ('ANIME001.LDT', 287472, 24),
            236: ('ANIME002.LDT', 2067856, 0)}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for piece in iter(lambda: handle.read(4 * 1024 * 1024), b''):
            digest.update(piece)
    return digest.hexdigest()


def parse_pspfs_entry(table: bytes, index: int, data_size: int) -> dict:
    if len(table) < 16 or table[:8] != b'PSPFS_V1' or struct.unpack_from('<I', table, 8)[0] != 349:
        raise ValueError('PSPFS original inesperado')
    off = 16 + index * 32
    if len(table) < off + 32:
        raise ValueError('PSPFS truncado')
    row = table[off:off + 32]
    name_bytes = row[:20].split(b'\x00', 1)[0]
    try:
        name = name_bytes.decode('ascii', 'strict')
    except UnicodeDecodeError as exc:
        raise ValueError('Nombre PSPFS no ASCII') from exc
    expanded, stored, payload_off = struct.unpack_from('<III', row, 20)
    if expanded != 0 or stored == 0 or payload_off < len(table) or payload_off + stored > data_size:
        raise ValueError('Offset/tamaño PSPFS inválido')
    return {'name': name, 'size_stored': stored, 'offset': payload_off}


def scan_imy_headers(blob: bytes) -> list[dict]:
    """Métricas; no decodifica imágenes ni presume que IMY sea un cuadro."""
    out = []
    pos = 0
    while True:
        pos = blob.find(b'IMY\x00', pos)
        if pos < 0:
            break
        if pos + 34 > len(blob):
            raise ValueError('Firma IMY incompleta')
        target_plus_32 = struct.unpack_from('<I', blob, pos + 4)[0]
        stride = struct.unpack_from('<H', blob, pos + 8)[0]
        typ = blob[pos + 10]
        rows = struct.unpack_from('<H', blob, pos + 12)[0]
        flags_count = struct.unpack_from('<H', blob, pos + 32)[0]
        if (not stride or not rows or target_plus_32 != stride * rows + 32
                or flags_count == 0 or pos + 34 + flags_count > len(blob)):
            raise ValueError('IMY malformado: geometría/flags inconsistente')
        out.append({'offset': pos, 'stride': stride, 'rows': rows,
                    'typ': typ, 'flags_count': flags_count})
        pos += 4
    return out


def legacy_flag_probe(blob: bytes, header: dict) -> str:
    """Prueba SOLO del flujo IMY legado, no equivalencia de formato ni de imagen."""
    off, stride, rows = header['offset'], header['stride'], header['rows']
    flag_end = off + 34 + header['flags_count']
    flags = blob[off + 34:flag_end]
    read_pos = flag_end
    target = stride * rows
    decoded = bytearray()
    lookbacks = (2, stride, stride + 2, stride - 2)
    for flag in flags:
        if len(decoded) >= target:
            break
        if flag & 0xC0 == 0xC0:
            distance = lookbacks[(flag >> 4) & 3]
            if distance < 1 or len(decoded) < distance:
                return 'LOOKBACK_INVALIDO'
            for _ in range((flag & 15) + 1):
                ix = len(decoded) - distance
                decoded.extend(decoded[ix:ix + 2])
        elif flag & 0xF0:
            distance = (flag - 16) * 2 + 2
            if read_pos - distance < flag_end:
                return 'REFERENCIA_LITERAL_INVALIDA'
            decoded.extend(blob[read_pos - distance:read_pos - distance + 2])
        else:
            count = (flag + 1) * 2
            if read_pos + count > len(blob):
                return 'LITERAL_TRUNCADO'
            decoded.extend(blob[read_pos:read_pos + count])
            read_pos += count
        if len(decoded) > target:
            return 'LONGITUD_DISTINTA'
    return 'ALGORITMO_LEGADO_CONSUME_FLAGS' if len(decoded) == target else 'LONGITUD_DISTINTA'


def inventory_member(blob: bytes, expected_count: int) -> dict:
    headers = scan_imy_headers(blob)
    if len(headers) != expected_count:
        raise ValueError('Número de cabeceras IMY distinto del original autenticado')
    types = Counter(f"0x{item['typ']:02x}" for item in headers)
    statuses = Counter((f"0x{item['typ']:02x}", legacy_flag_probe(blob, item)) for item in headers)
    return {
        'stored_bytes': len(blob),
        'sha256': hashlib.sha256(blob).hexdigest(),
        'first_u32_unsigned': struct.unpack_from('<I', blob, 0)[0],
        'imy_header_occurrences': len(headers),
        'header_types': dict(sorted(types.items())),
        'legacy_flags_probe_by_type': {
            typ: dict(sorted((status, n) for (t, status), n in statuses.items() if t == typ))
            for typ in sorted(types)
        },
        'frame_count_or_intro_resource_proven': False,
    }


def audit(iso: Path) -> dict:
    iso = Path(iso)
    if iso.is_symlink() or not iso.is_file() or iso.stat().st_size != SIZE_USA or sha256_file(iso) != SHA_USA:
        raise ValueError('Se requiere ISO USA ORIGINAL exacta')
    result = {}
    with iso.open('rb') as handle:
        handle.seek(DATA_ISO_OFF)
        top = handle.read(16 + 349 * 32)
        for index, (expected_name, expected_size, expected_imy) in EXPECTED.items():
            entry = parse_pspfs_entry(top, index, DATA_SIZE)
            if entry['name'] != expected_name or entry['size_stored'] != expected_size:
                raise ValueError(f'Recurso PSPFS {index} no coincide con original')
            handle.seek(DATA_ISO_OFF + entry['offset'])
            blob = handle.read(entry['size_stored'])
            if len(blob) != expected_size:
                raise ValueError('Recurso truncado')
            result[str(index)] = {'name': expected_name,
                                  **inventory_member(blob, expected_imy)}
            if index == 234:
                try:
                    from tools.f3_anime_imy_r17 import analyze
                except ModuleNotFoundError:
                    from f3_anime_imy_r17 import analyze
                if hashlib.sha256(blob).hexdigest() != '0e57353eb1d5f9688164b3453e57b0fd91ff77dee8e422844ba3fb0fef32eb37':
                    raise ValueError('ANIME000 source hash differs')
                result[str(index)]['r17_bounded_candidate'] = analyze(blob)
    if result['234']['header_types'] != {'0x00': 136, '0x02': 95}:
        raise ValueError('Tipos originales ANIME000 no coinciden')
    if result['235']['header_types'] != {'0x00': 24} or result['236']['header_types']:
        raise ValueError('Tipos de ANIME001/002 no coinciden')
    return {'schema': 'cladun.f3.anime_imy_static_readonly.v1',
            'evidence': 'A_ORIGINAL_ISO_STATIC; NOT_C_PPSSPP',
            'usa_iso_sha256': SHA_USA, 'usa_iso_size': SIZE_USA,
            'pspfs_entries': 349, 'resources': result,
            'game_assets_modified': False, 'textures_exported': False,
            'visual_prologue_text_source_proven': False,
            'runtime_ppsspp_executed_by_this_tool': False,
            'conclusion': 'IMY type 0x00 is compatible with the legacy flags algorithm in this read-only experiment; 0x02 is not. Neither result identifies intro lettering.'}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iso-original', type=Path, required=True)
    parser.add_argument('--reporte', type=Path, required=True)
    args = parser.parse_args()
    report = args.reporte.expanduser().resolve(strict=False)
    if (args.reporte.is_symlink() or not args.reporte.is_absolute()
            or report.exists() or report.suffix.lower() != '.json'):
        raise ValueError('El JSON de informe debe ser una ruta nueva y absoluta')
    result = audit(args.iso_original)
    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps({'original_sha_verified': True,
                      'imy_header_counts': {k: v['imy_header_occurrences']
                                            for k, v in result['resources'].items()},
                      'render_proven': False}))


if __name__ == '__main__':
    main()
