#!/usr/bin/env python3
"""Readonly comparison of two original IMY font-like textures.

Writes only hashes/numeric metadata. No asset bytes, PNGs or decoded pixels.
An image found in ISO is NOT automatically used by PPSSPP at runtime.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import mmap
import struct
from pathlib import Path

SOURCE_SHA = 'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
SIZE = 305496064
DATA_OFFSET = 113770496  # known from independently parsed, exact SHA source ISO
EXPECTED = (
    (225, 'SYSGRA.ARC', 'FONT.IMY', 14, 4148,
     '50143c165f10aa71ac77d4a2b09fd69012b1eceac4a102bf8e2b8157bf8b5915', 128, 256),
    (308, 'FONT.ARC', 'FONT_00.IMY', 1, 17468,
     '698bc5b398a16c3f2a4615527dac6a36dbae73666a7c45c3787bb00a728a8478', 256, 256),
)

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def sha_file(path: Path) -> str:
    d = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b''):
            d.update(chunk)
    return d.hexdigest()

def unpack_image(imy: bytes) -> tuple[bytes, dict]:
    """Decode known IMY 0xA4/4bpp flavor; low byte of header field locates flags.

    No generic claim about other IMY variants. Decoded pixels stay in memory.
    """
    if len(imy) < 98 or imy[:4] != b'IMY\0':
        raise ValueError('Invalid IMY signature or truncated header')
    pointer = struct.unpack_from('<H', imy, 4)[0]
    if (pointer & 255) != 0x60 or imy[10] != 0xA4:
        raise ValueError('Unsupported IMY 0xA4 format or flags offset')
    stride, rows = struct.unpack_from('<H', imy, 8)[0], struct.unpack_from('<H', imy, 12)[0]
    if not 0 < stride <= 4096 or not 0 < rows <= 4096 or stride % 2:
        raise ValueError('Invalid image stride/rows')
    target = stride * rows
    flags_len = struct.unpack_from('<H', imy, 0x60)[0]
    flags_start = 0x62
    reader = flags_start + flags_len
    if flags_len == 0 or reader > len(imy):
        raise ValueError('Truncated IMY flag stream')
    literals_start = reader
    out = bytearray()
    for flag in imy[flags_start:reader]:
        if len(out) >= target:
            break
        if (flag & 0xC0) == 0xC0:
            gap = (2, stride, stride + 2, stride - 2)[(flag >> 4) & 3]
            if len(out) < gap:
                raise ValueError('IMY pixel lookback before start')
            repeat = (flag & 15) + 1
            if len(out) + repeat * 2 > target:
                raise ValueError('IMY repeat exceeds image geometry')
            for _ in range(repeat):
                off = len(out) - gap
                out.extend(out[off:off + 2])
        elif flag & 0xF0:
            gap = (flag - 16) * 2 + 2
            if reader - gap < literals_start:
                raise ValueError('IMY literal lookback before start')
            if len(out) + 2 > target:
                raise ValueError('IMY literal repeat overflows image')
            out.extend(imy[reader - gap:reader - gap + 2])
        else:
            n = (flag + 1) * 2
            if len(out) + n > target or reader + n > len(imy):
                raise ValueError('IMY literal block exceeds image/source')
            out.extend(imy[reader:reader + n])
            reader += n
    if len(out) != target or reader != len(imy):
        raise ValueError('Incomplete IMY decoding or unconsumed trailing data')
    usage = [0] * 16
    for value in out:
        usage[value & 15] += 1
        usage[value >> 4] += 1
    return bytes(out), {
        'header_flags_field_hex': f'0x{pointer:04X}',
        'header_flags_low_byte': pointer & 255,
        'format_byte_hex': '0xA4',
        'stride_bytes': stride,
        'rows': rows,
        'width_pixels_for_4bpp': stride * 2,
        'raw_4bpp_bytes': target,
        'pixel_index_counts': usage,
        'used_clut_indices': [i for i, v in enumerate(usage) if v],
        'flags_count': flags_len,
        'stream_fully_consumed': True,
        'decoded_sha256': sha(out),
    }

def audit(iso: Path) -> dict:
    iso = Path(iso)
    if iso.stat().st_size != SIZE or sha_file(iso) != SOURCE_SHA:
        raise ValueError('Source ISO USA size/SHA256 mismatch')
    report = []
    with iso.open('rb') as f:
        mem = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        try:
            if mem[16 * 2048:16 * 2048 + 7] != b'\x01CD001\x01':
                raise ValueError('ISO9660 PVD missing')
            for pi, parent_name, member_name, mi, member_size, member_hash, stride, rows in EXPECTED:
                entry = mem[DATA_OFFSET + 16 + 32 * pi:DATA_OFFSET + 16 + 32 * (pi + 1)]
                label = entry[:20].split(b'\0', 1)[0].decode('ascii')
                if label != parent_name:
                    raise ValueError('Wrong PSPFS parent')
                expanded, stored, offset = struct.unpack_from('<III', entry, 20)
                if expanded != 0 or stored < member_size:
                    raise ValueError('Unexpected PSPFS archive size')
                p = DATA_OFFSET + offset
                magic = mem[p:p + 8]
                members = struct.unpack_from('<I', mem, p + 8)[0]
                if magic not in (b'DSARC FL', b'DSARCIDX'):
                    raise ValueError('Not DSARC')
                start = 16 if magic == b'DSARC FL' else (16 + members * 2 + 3) // 4 * 4
                e = mem[p + start + 48 * mi:p + start + 48 * (mi + 1)]
                name = e[:40].split(b'\0', 1)[0].decode('ascii')
                size, off = struct.unpack_from('<II', e, 40)
                if name != member_name or size != member_size or off + size > stored:
                    raise ValueError('Wrong DSARC member or bounds')
                imy = mem[p + off:p + off + size]
                if sha(imy) != member_hash:
                    raise ValueError('Original member checksum changed')
                raw, metadata = unpack_image(imy)
                if (metadata['stride_bytes'], metadata['rows']) != (stride, rows):
                    raise ValueError('Wrong original texture dimensions')
                metadata.update({
                    'pspfs_index': pi,
                    'parent': parent_name,
                    'member_index': mi,
                    'member': member_name,
                    'stored_length': len(imy),
                    'stored_sha256': sha(imy),
                    'member_graphic_in_ppsspp_proven': False,
                })
                report.append(metadata)
        finally:
            mem.close()
    return {
        'schema': 'cladun.f2.independent_font_images_decoded_static.v1',
        'source_iso_sha256': SOURCE_SHA,
        'source_iso_bytes': SIZE,
        'scope': 'ORIGINAL_DATA_STATIC_ONLY_NOT_PPSSPP_RENDERING',
        'different_decoded_sizes': report[0]['raw_4bpp_bytes'] != report[1]['raw_4bpp_bytes'],
        'different_decoded_sha256': report[0]['decoded_sha256'] != report[1]['decoded_sha256'],
        'not_same_original_image_geometry': True,
        'which_font_is_used_by_runtime': 'NOT_PROVEN',
        'proof_of_RAM_GE_VRAM': False,
        'decoded_textures_exported': False,
        'textures': report,
    }

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso-usa', type=Path, required=True)
    p.add_argument('--reporte', type=Path, required=True)
    args = p.parse_args()
    r = audit(args.iso_usa)
    args.reporte.parent.mkdir(exist_ok=True, parents=True)
    with args.reporte.open('x', encoding='utf8') as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps({
        'schema': r['schema'],
        'widths': [x['width_pixels_for_4bpp'] for x in r['textures']],
        'decoded_hashes': [x['decoded_sha256'] for x in r['textures']],
        'functional_use': 'NOT_PROVEN',
    }, ensure_ascii=False))

if __name__ == '__main__':
    main()
