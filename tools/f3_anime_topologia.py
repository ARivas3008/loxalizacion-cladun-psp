#!/usr/bin/env python3
"""F3: topology of IMY headers and adjacent byte intervals; metadata only.

This is not an IMY decoder, texture identifier, or PPSSPP runtime witness.
Reads an authenticated privately owned original USA ISO, never writes assets.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import itertools
import json
from pathlib import Path
import struct

USA_SIZE = 305496064
USA_SHA256 = 'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
DATA_OFF = 113770496
DATA_SIZE = 191697408
MEMBERS = {
    234: ('ANIME000.IDT', 3537936, '0e57353eb1d5f9688164b3453e57b0fd91ff77dee8e422844ba3fb0fef32eb37'),
    235: ('ANIME001.LDT', 287472, 'cb7f1354e38ced1a5b19f36c2b45d939e59094e33de901d4b43dc8d65faaa174'),
    236: ('ANIME002.LDT', 2067856, 'e1617dd4aea349f60953db9471e53c1524e9c3184b2566a4a732c3ecc756eec6'),
}

def file_sha256(path: Path) -> str:
    sha = hashlib.sha256()
    with path.open('rb') as handle:
        for part in iter(lambda: handle.read(4 * 1024 * 1024), b''):
            sha.update(part)
    return sha.hexdigest()

def topology(blob: bytes) -> dict:
    """Inspect literal headers; do not infer frame references or compressed payload."""
    pos = 0
    offsets = []
    while True:
        pos = blob.find(b'IMY\x00', pos)
        if pos < 0:
            break
        offsets.append(pos)
        pos += 4
    kinds = []
    hashes = []
    intervals = []
    for i, start in enumerate(offsets):
        end = offsets[i + 1] if i + 1 < len(offsets) else len(blob)
        if start % 4 or start + 34 > end:
            raise ValueError('Misaligned or truncated IMY header')
        target_plus32, stride, typ, subtype, rows = struct.unpack_from('<IHBBH', blob, start + 4)
        flag_count = struct.unpack_from('<H', blob, start + 32)[0]
        if (target_plus32 != stride * rows + 32 or not stride or not rows
                or typ not in (0, 2) or flag_count == 0
                or start + 34 + flag_count > end):
            raise ValueError('IMY header/flag range inconsistent with next header')
        kinds.append(typ)
        intervals.append(end - start)
        hashes.append((typ, hashlib.sha256(blob[start:end]).digest()))
    runs = [(kind, len(list(g))) for kind, g in itertools.groupby(kinds)]
    pairs = Counter(f'{a:02x}->{b:02x}' for a, b in zip(kinds, kinds[1:]))
    duplicates = {}
    for typ in sorted(set(kinds)):
        counts = Counter(d for t, d in hashes if t == typ)
        duplicates[f'0x{typ:02x}'] = sum(c - 1 for c in counts.values())
    return {
        'literal_headers': len(kinds),
        'header_type_counts': {f'0x{t:02x}': c for t, c in sorted(Counter(kinds).items())},
        'adjacent_type_transitions': dict(sorted(pairs.items())),
        'type_run_count': len(runs),
        'longest_consecutive_run_by_type': {
            f'0x{t:02x}': max(n for kind, n in runs if kind == t) for t in sorted(set(kinds))
        },
        'exact_duplicate_adjacent_intervals_by_type': duplicates,
        'first_header_offset_bytes': offsets[0] if offsets else None,
        'max_adjacent_interval_bytes': max(intervals, default=None),
        'all_headers_4byte_aligned_and_flags_within_next_header': True,
        'decoded_frames_or_palette_proven': False,
    }

def audit(iso: Path) -> dict:
    iso = Path(iso)
    if iso.is_symlink() or not iso.is_file() or iso.stat().st_size != USA_SIZE or file_sha256(iso) != USA_SHA256:
        raise ValueError('Not the exact original USA ISO')
    out = {}
    with iso.open('rb') as handle:
        handle.seek(DATA_OFF)
        table = handle.read(16 + 349 * 32)
        if table[:8] != b'PSPFS_V1' or struct.unpack_from('<I', table, 8)[0] != 349:
            raise ValueError('PSPFS_V1/349 not found')
        for index, (name, size, digest) in MEMBERS.items():
            record = table[16 + index * 32:16 + (index + 1) * 32]
            actual_name = record[:20].split(b'\x00')[0].decode('ascii', 'strict')
            expanded, stored, offset = struct.unpack_from('<III', record, 20)
            if actual_name != name or expanded != 0 or stored != size or offset < len(table) or offset + size > DATA_SIZE:
                raise ValueError(f'PSPFS member {index} differs from original')
            handle.seek(DATA_OFF + offset)
            blob = handle.read(size)
            if len(blob) != size or hashlib.sha256(blob).hexdigest() != digest:
                raise ValueError(f'PSPFS member {index} digest mismatch')
            out[str(index)] = {'name': name, 'size': size, 'sha256': digest, **topology(blob)}
    if (out['234']['literal_headers'], out['235']['literal_headers'], out['236']['literal_headers']) != (231, 24, 0):
        raise ValueError('Unexpected original IMY counts')
    return {'schema': 'cladun.f3.imy_adjacent_topology_readonly.v1',
            'evidence_class': 'A_ORIGINAL_ISO_STATIC_ONLY',
            'usa_sha256': USA_SHA256, 'members': out, 'original_assets_modified': False,
            'public_output_has_game_bytes': False, 'ppsspp_runtime_in_this_analysis': False,
            'prologue_letters_source_identified': False}

def safe_report(path: Path) -> Path:
    path = Path(path).expanduser()
    if not path.is_absolute() or path.is_symlink() or path.suffix.lower() != '.json':
        raise ValueError('A new absolute private JSON path is required')
    path = path.resolve(strict=False)
    if path.exists() or any((parent / '.git').exists() for parent in path.parents):
        raise ValueError('Will not overwrite or write inside Git')
    return path

def main() -> None:
    cli = argparse.ArgumentParser(description=__doc__)
    cli.add_argument('--iso-original', type=Path, required=True)
    cli.add_argument('--reporte-privado', type=Path, required=True)
    args = cli.parse_args()
    path = safe_report(args.reporte_privado)
    result = audit(args.iso_original)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('x', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(json.dumps({'iso_verified': True, 'headers': [v['literal_headers'] for v in result['members'].values()],
                      'visual_source_proven': False}))

if __name__ == '__main__':
    main()
