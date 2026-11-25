#!/usr/bin/env python3
"""F2: prove immutable digit/control subregions of original TUIKA_MES.IMY.

Static authentic ISO only: NO runtime provenance, translations, game images or
new game payload. Labels are provisional. Never treat a candidate text box as
an approved editing ROI. A separate future gameplay review is mandatory.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ISO_SIZE = 305496064
ISO_SHA = 'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
MEMBER_OFFSET = 113770496 + 895488 + 78848
MEMBER_BYTES = 7912
MEMBER_SHA = 'c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127'
INDEX_DECODED_SHA = '3c181786f72008c144a2187d362d289d453b4f00d93fe5f8cb2facc0f23d14d5'
LINEAR_PIXEL_INDEX_SHA = 'a3da2c0d728288c2842b0d9164f4dd220c4713eaa19b3559ef7105f837f8106d'
MASK_SHA = '382ae8d2ffa8908979050b5e83f38ec9967b461bbf9b614dd92775da90e409ba'
WIDTH = HEIGHT = 256
# All boundaries derive from the 4bpp original indexed raster, not a game frame.
# Each SHA is of row-major original 0..15 index BYTES in the rectangle, not RGB.
REGIONS = (
    ('band00_mixed_japanese',       1,  2, 240,  15, 'LOCKED_UNRESOLVED_MIXED', '035e418ba097eeeca464729c5d8a3fc20fd4e0164ba7c22dfa74817cd8caa933'),
    ('band10_g_star_label',        4,181,  79, 196, 'PROVISIONAL_LABEL_LOCKED', '6b6f8d988c81022b5913af4686fa9b6468f3fd3c66ec84e90298d5ac9de7ae42'),
    ('band10_control_icons',      92,181, 115, 196, 'LOCKED_ICON', 'c130f1d94b27467b3cfe603e0dfbfc0e922c6ae777ff52557788537b57314268'),
    ('band11_control_symbols',     1,199, 136, 214, 'LOCKED_ICON', '036958ab369722152f658807d6cb9bfb246374996e582881326fe08a4e055677'),
    ('band12_digits_0_to_9',       1,218, 138, 231, 'LOCKED_DIGITS', 'ada283d0d131636eeac112d2982979fd737fa1cf7ec042b9f034626b1dcbd08c'),
    ('band13_digits_0_to_9',       1,236, 108, 249, 'LOCKED_DIGITS', '315e2178f7391c79d5105cf862050b7d1a44e263a8d05a7d22ca7a8c3caacada'),
    ('band13_no_special_attack', 112,236, 248, 249, 'PROVISIONAL_LABEL_LOCKED', 'a02845ad02253e0333466b1f879d2acea66d59564c15796e06a5f2dc90ceb32e'),
)
# Gaps must be completely transparent index 0, not merely free of white ink.
GAPS = (
    ('band10_label_to_icons', 80,181, 91,196),
    ('band13_digits_to_text',109,236,111,249),
    ('band13_special_to_attack',190,236,199,249),
)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(b)
    return h.hexdigest()


def validate_private_output(path: Path, repo_root: Path | None = None) -> Path:
    path = Path(path).expanduser()
    if not path.is_absolute() or path.suffix.lower() != '.json' or path.is_symlink():
        raise ValueError('Output requires new absolute private .json, no symlink')
    resolved = path.resolve(strict=False)
    repo = (repo_root or Path(__file__).resolve().parents[1]).resolve()
    if resolved == repo or repo in resolved.parents:
        raise ValueError('No commercial-derived evidence in repository')
    if resolved.exists() or path.exists():
        raise FileExistsError('No evidence overwrite')
    if any((p / '.git').exists() for p in resolved.parents):
        raise ValueError('Refuse any git workspace')
    return path


def crop_indices(indices: bytes, x0: int, y0: int, x1: int, y1: int,
                 width: int = WIDTH, height: int = HEIGHT) -> bytes:
    if (not isinstance(indices, bytes) or len(indices) != width * height or
            not (0 <= x0 <= x1 < width and 0 <= y0 <= y1 < height)):
        raise ValueError('Invalid raster or region geometry')
    return b''.join(indices[y * width+x0:y*width+x1+1] for y in range(y0,y1+1))


def analyze_indexed(indices: bytes, *, strict_original: bool = True) -> dict:
    if not isinstance(indices, bytes) or len(indices) != WIDTH*HEIGHT or any(x > 15 for x in indices):
        raise ValueError('Expected native 256x256 4-bit index bytes')
    linear_sha = sha(indices)
    mask_sha = sha(bytes(255 if x == 2 else 0 for x in indices))
    if strict_original and (linear_sha != LINEAR_PIXEL_INDEX_SHA or mask_sha != MASK_SHA):
        raise ValueError('Not the authenticated original indexed raster')
    regions = []
    for name,x0,y0,x1,y1,status,original_sha in REGIONS:
        crop=crop_indices(indices,x0,y0,x1,y1)
        if strict_original and sha(crop)!=original_sha:
            raise ValueError('Authenticated subregion hash mismatch: '+name)
        counts={str(i):crop.count(i) for i in range(16) if i in crop}
        regions.append({'name':name,'bbox_xyxy_inclusive':[x0,y0,x1,y1],
                        'size_px':len(crop),'index_counts':counts,
                        'original_region_index_sha256':sha(crop),
                        'classification':status,
                        'currently_authorized_for_edit':False,
                        'gameplay_proven':False})
    gaps=[]
    for name,x0,y0,x1,y1 in GAPS:
        crop=crop_indices(indices,x0,y0,x1,y1)
        if strict_original and any(crop):
            raise ValueError('Original gap is not fully empty: '+name)
        gaps.append({'name':name,'bbox_xyxy_inclusive':[x0,y0,x1,y1],
                     'pixels':len(crop),'all_index0_transparent':not any(crop),
                     'index_sha256':sha(crop),'must_be_preserved':True})
    return {'schema':'cladun.f2.tuika_original_subregions_readonly.v1',
            'scope':'AUTHENTIC_ISO_STATIC_INDEXED_RASTER_NO_PPSSPP',
            'texture_dimensions':[WIDTH,HEIGHT],
            'original_linear_pixel_index_sha256':linear_sha,
            'original_clut2_mask_sha256':mask_sha,
            'measured_region_count':len(regions),'measured_gap_count':len(gaps),
            'regions':regions,'separating_gaps':gaps,
            'runtime_texture_use_proven':False,'mips_ram_ge_vram_proven':False,
            'translation_inserted':False,'any_editing_roi_approved':False,
            'source_game_art_embedded_in_report':False,
            'warning':'These subregions define pixels to preserve or inspect, NOT a safe translation area. The A/B PPSSPP test must precede any edit.'}


def protected_pixel_positions(width: int = WIDTH) -> frozenset[int]:
    positions=set()
    for _,x0,y0,x1,y1,status,_ in REGIONS:
        if status.startswith('LOCKED'):
            positions.update(y*width+x for y in range(y0,y1+1) for x in range(x0,x1+1))
    for _,x0,y0,x1,y1 in GAPS:
        positions.update(y*width+x for y in range(y0,y1+1) for x in range(x0,x1+1))
    return frozenset(positions)


def guard_candidate(source: bytes, candidate: bytes,
                    approved_pixels: frozenset[int] = frozenset()) -> dict:
    """No file writes. Zero edits permitted by default; locked pixels always denied.

    approved_pixels is a future QA interface, *not* a runtime edit approval;
    callers must separately prove context/permissions and repack safety.
    """
    if (not isinstance(source,bytes) or not isinstance(candidate,bytes) or
            len(source)!=WIDTH*HEIGHT or len(candidate)!=len(source) or
            any(v>15 for v in source) or any(v>15 for v in candidate)):
        raise ValueError('Only equal-size 256x256 4bpp index arrays allowed')
    if not isinstance(approved_pixels, frozenset) or any(type(i)!=int or not 0<=i<len(source) for i in approved_pixels):
        raise ValueError('Approved pixels must be explicit bounded frozenset')
    locked=protected_pixel_positions()
    if locked & approved_pixels:
        raise ValueError('Approved mask overlaps protected digits/icons or gaps')
    differences=[i for i,(a,b) in enumerate(zip(source,candidate)) if a!=b]
    if any(i not in approved_pixels for i in differences):
        raise ValueError('Candidate changes outside explicit allowed mask')
    return {'schema':'cladun.f2.in_memory_candidate_geometry_guard.v1',
            'changed_pixel_count':len(differences),
            'protected_pixel_count':len(locked),
            'no_unauthorized_pixel_change':True,
            'gameplay_or_translation_safety_proven':False,
            'raster_exported':False}


def audit_original(iso: Path) -> dict:
    iso=Path(iso)
    if iso.stat().st_size!=ISO_SIZE or sha_file(iso)!=ISO_SHA:
        raise ValueError('Source USA ISO size/SHA mismatch')
    with iso.open('rb') as f:
        f.seek(MEMBER_OFFSET)
        member=f.read(MEMBER_BYTES)
    if sha(member)!=MEMBER_SHA:
        raise ValueError('TUIKA member SHA mismatch')
    try:
        from tools.f2_auditar_27_imy_sysgra import decode_imy
        from tools.f2_previsualizar_sysgra_privado import unswizzle_psp
    except ModuleNotFoundError:
        from f2_auditar_27_imy_sysgra import decode_imy
        from f2_previsualizar_sysgra_privado import unswizzle_psp
    tiled, meta=decode_imy(member)
    if sha(tiled)!=INDEX_DECODED_SHA or meta['width_pixels_if_4bpp']!=WIDTH or meta['rows']!=HEIGHT:
        raise ValueError('Decoded original raster SHA/dimensions invalid')
    linear=unswizzle_psp(tiled,WIDTH//2,HEIGHT)
    indices=bytes(index for b in linear for index in (b&15,b>>4))
    report=analyze_indexed(indices,strict_original=True)
    report.update({'source_original_iso_sha256':ISO_SHA,
                   'source_member_sha256':MEMBER_SHA,
                   'swizzled_decoded_index_sha256':INDEX_DECODED_SHA})
    return report


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso-usa',type=Path,required=True)
    p.add_argument('--reporte-privado',type=Path,required=True)
    args=p.parse_args()
    out=validate_private_output(args.reporte_privado)
    result=audit_original(args.iso_usa)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2)
        f.write('\n')
    print(json.dumps({'regions':result['measured_region_count'],
                      'gaps':result['measured_gap_count'],
                      'editing_roi_approved':False,
                      'ppsspp_gameplay_proven':False}))


if __name__ == '__main__':
    main()
