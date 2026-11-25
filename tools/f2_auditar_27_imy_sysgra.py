#!/usr/bin/env python3
"""Decode 27 ORIGINAL SYSGRA IMY indexed surfaces without exporting game assets.

Supports audited native header variants 0x20 (256 RGBA palette entries at +32)
and 0x60 (16 RGBA entries at +32); flag streams start at 0x420 / 0x60.
Distinct bytes or decoded surfaces do not prove PPSSPP runtime provenance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

ISO_SHA = 'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
ISO_SIZE = 305496064
DATA_OFFSET = 113770496
SYSGRA_INDEX = 225
SYSGRA_OFFSET = 895488
SYSGRA_SIZE = 93696
SYSGRA_SHA = '63d9443084a2aeab8c2a3f79aebdb130eaf6c5d2e86f8be51346d7458ab81854'
KITAJIMA_SHA = '0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190'
FONT_SHA = '5d4ff855af1132ea0abf204b5a4c44ddce28b55758772feba21ce6163cc6c4fc'
PALETTE_NAMES = tuple('PALETE_%d.IMY' % n for n in range(4))

def sha(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest()

def file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for piece in iter(lambda: f.read(1024 * 1024), b''):
            h.update(piece)
    return h.hexdigest()

def decode_imy(imy: bytes) -> tuple[bytes, dict]:
    """Fail-closed indexed 4bpp reconstruction; palette and raw pixels stay private."""
    if len(imy) < 98 or imy[:4] != b'IMY\x00':
        raise ValueError('IMY header missing or truncated')
    mode = imy[4]
    if mode not in (0x20, 0x60) or imy[6:8] != b'\x00\x00':
        raise ValueError('Unsupported IMY header mode')
    if imy[10] not in (0x84, 0xA4):
        raise ValueError('Unsupported IMY pixel format')
    stride, rows = struct.unpack_from('<H', imy, 8)[0], struct.unpack_from('<H', imy, 12)[0]
    if stride < 2 or stride > 4096 or stride % 2 or rows < 1 or rows > 4096:
        raise ValueError('IMY geometry invalid')
    flags_at = 0x420 if mode == 0x20 else 0x60
    palette = imy[0x20:flags_at]
    if len(palette) != (1024 if mode == 0x20 else 64):
        raise ValueError('IMY palette truncated')
    if flags_at + 2 > len(imy):
        raise ValueError('IMY flag length missing')
    nf = struct.unpack_from('<H', imy, flags_at)[0]
    flags_start = flags_at + 2
    literals_start = flags_start + nf
    if nf == 0 or literals_start > len(imy):
        raise ValueError('IMY flags truncated')
    cursor = literals_start
    target = stride * rows
    out = bytearray()
    flags = imy[flags_start:literals_start]
    used_flags = 0
    for flag in flags:
        if len(out) >= target:
            break
        used_flags += 1
        if flag & 0xC0 == 0xC0:
            back = (2, stride, stride + 2, stride - 2)[(flag >> 4) & 3]
            repeat = (flag & 0xF) + 1
            if back <= 0 or len(out) < back:
                raise ValueError('IMY invalid pixel lookback')
            if len(out) + 2 * repeat > target:
                raise ValueError('IMY pixel lookback exceeds target')
            for _ in range(repeat):
                pos = len(out) - back
                out.extend(out[pos:pos + 2])
        elif flag & 0xF0:
            back = (flag - 0x10) * 2 + 2
            if cursor - back < literals_start:
                raise ValueError('IMY invalid literal lookback')
            if len(out) + 2 > target:
                raise ValueError('IMY literal lookback exceeds target')
            out.extend(imy[cursor - back:cursor - back + 2])
        else:
            count = (flag + 1) * 2
            if len(out) + count > target or cursor + count > len(imy):
                raise ValueError('IMY literal exceeds source or target')
            out.extend(imy[cursor:cursor + count])
            cursor += count
    unused_flags = flags[used_flags:]
    # Original IMY streams may append up to three zero command bytes for alignment.
    if len(unused_flags) > 3 or any(unused_flags):
        raise ValueError('IMY unused flag commands not zero alignment padding')
    if len(out) != target:
        raise ValueError('IMY reconstructed texture length mismatch')
    tail = imy[cursor:]
    if len(tail) > 3 or any(tail):
        raise ValueError('IMY trailing bytes are not zero alignment padding')
    indices = [0] * 16
    for octet in out:
        indices[octet & 0xF] += 1
        indices[octet >> 4] += 1
    return bytes(out), {
        'imagedata_format_byte': f'0x{imy[10]:02X}',
        'palette_entries': len(palette) // 4,
        'palette_sha256': sha(palette),
        'flag_offset_hex': f'0x{flags_at:04X}',
        'flag_command_count': nf,
        'width_pixels_if_4bpp': stride * 2,
        'rows': rows,
        'decoded_bytes': len(out),
        'decoded_sha256': sha(out),
        'nonzero_pixel_indices': [i for i, count in enumerate(indices) if count],
        'pixel_index_counts': indices,
        'zero_tail_padding_bytes': len(tail),
        'unused_flag_command_count': len(unused_flags),
        'unused_flags_are_zero': not any(unused_flags),
        'compressed_stream_complete': True,
        'runtime_resource_use_proven': False,
    }

def inspect_sysgra(archive: bytes) -> dict:
    """Authenticate DSARC topology and known icon/texture signatures."""
    if len(archive) != SYSGRA_SIZE or sha(archive) != SYSGRA_SHA:
        raise ValueError('SYSGRA.ARC size/checksum mismatch')
    if archive[:8] != b'DSARC FL' or struct.unpack_from('<I', archive, 8)[0] != 27:
        raise ValueError('Unexpected SYSGRA DSARC header/count')
    table_end = 16 + 48 * 27
    records, offsets, names = [], [], set()
    for i in range(27):
        cell = archive[16 + 48 * i:16 + 48 * (i + 1)]
        name = cell[:40].split(b'\0', 1)[0].decode('ascii')
        size, off = struct.unpack_from('<II', cell, 40)
        if not name or not name.endswith('.IMY') or name in names:
            raise ValueError('Invalid or duplicate DSARC member name')
        if size < 100 or off < table_end or off + size > len(archive):
            raise ValueError('DSARC member out of bounds')
        names.add(name)
        records.append((i, name, off, size))
        offsets.append((off, off + size))
    offsets.sort()
    if any(end > start for (_, end), (start, _) in zip(offsets, offsets[1:])):
        raise ValueError('Overlapping DSARC members')
    outputs = []
    for index, name, offset, length in records:
        stored = archive[offset:offset + length]
        _, info = decode_imy(stored)
        info.update({'dsarc_index': index, 'name': name,
                     'stored_bytes': length, 'stored_sha256': sha(stored)})
        outputs.append(info)
    if outputs[17]['name'] != 'KITAJIMA_KARI.IMY' or outputs[17]['stored_sha256'] != KITAJIMA_SHA:
        raise ValueError('Known controls icon member changed')
    if outputs[14]['name'] != 'FONT.IMY' or outputs[14]['decoded_sha256'] != FONT_SHA:
        raise ValueError('Known font metadata changed')
    palettes = [next(x for x in outputs if x['name'] == name) for name in PALETTE_NAMES]
    if len({x['decoded_sha256'] for x in palettes}) != 1:
        raise ValueError('Expected four equal index surfaces for PALETE variants')
    if len({x['palette_sha256'] for x in palettes}) != 4:
        raise ValueError('Expected four distinct color palettes for PALETE variants')
    return {
        'schema': 'cladun.f2.original_sysgra_27_index_palettes.v1',
        'scope': 'ORIGINAL_ISO_STATIC_NOT_PPSSPP_RAM_GE_VRAM',
        'sysgra_sha256': sha(archive),
        'decoded_members_count': len(outputs),
        'unique_decoded_index_surfaces': len({x['decoded_sha256'] for x in outputs}),
        'palette_variants_share_index_surface': True,
        'palette_variants_have_distinct_rgba_tables': True,
        'palette_variant_names': list(PALETTE_NAMES),
        'runtime_causal_rendering_proven': False,
        'members': outputs,
    }

def audit(iso: Path) -> dict:
    iso = Path(iso)
    if iso.stat().st_size != ISO_SIZE or file_sha(iso) != ISO_SHA:
        raise ValueError('Original ISO USA size/SHA256 mismatch')
    with iso.open('rb') as f:
        f.seek(16 * 2048)
        if f.read(7) != b'\x01CD001\x01':
            raise ValueError('ISO9660 PVD missing')
        f.seek(DATA_OFFSET)
        if f.read(8) != b'PSPFS_V1':
            raise ValueError('PSPFS header missing')
        if struct.unpack('<I', f.read(4))[0] != 349:
            raise ValueError('Unexpected PSPFS count')
        f.seek(DATA_OFFSET + 16 + 32 * SYSGRA_INDEX)
        rec = f.read(32)
        name = rec[:20].split(b'\0', 1)[0].decode('ascii')
        expanded, stored, offset = struct.unpack_from('<III', rec, 20)
        if name != 'SYSGRA.ARC' or expanded != 0 or stored != SYSGRA_SIZE or offset != SYSGRA_OFFSET:
            raise ValueError('SYSGRA parent PSPFS descriptor mismatch')
        f.seek(DATA_OFFSET + offset)
        archive = f.read(stored)
    result = inspect_sysgra(archive)
    result.update({'source_iso_sha256': ISO_SHA, 'source_iso_bytes': ISO_SIZE,
                   'pspfs_index': SYSGRA_INDEX, 'image_or_palette_bytes_exported': False})
    return result

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iso-usa', required=True, type=Path)
    ap.add_argument('--reporte', required=True, type=Path)
    arg = ap.parse_args()
    result = audit(arg.iso_usa)
    arg.reporte.parent.mkdir(parents=True, exist_ok=True)
    with arg.reporte.open('x', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps({k: result[k] for k in ('decoded_members_count',
        'unique_decoded_index_surfaces', 'palette_variants_share_index_surface',
        'palette_variants_have_distinct_rgba_tables')}, ensure_ascii=False))

if __name__ == '__main__':
    main()
