#!/usr/bin/env python3
"""F2: authenticated original TUIKA indexed texture + human-reviewed label inventory.

Static offline source only; never equate horizontal stripes to independent strings,
editing regions or runtime use. No image pixels, palette or ISO bytes in JSON.
Visual source transcription is a *separate*, explicitly provisional observation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from tools.f2_auditar_27_imy_sysgra import decode_imy
    from tools.f2_previsualizar_sysgra_privado import unswizzle_psp
    from tools.f2_mapa_franjas_tuika import analyze_strips
except ModuleNotFoundError:
    from f2_auditar_27_imy_sysgra import decode_imy
    from f2_previsualizar_sysgra_privado import unswizzle_psp
    from f2_mapa_franjas_tuika import analyze_strips

SOURCE_SHA = 'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
SOURCE_SIZE = 305496064
ORIGINAL_MEMBER_SHA = 'c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127'
INDEX_SHA = '3c181786f72008c144a2187d362d289d453b4f00d93fe5f8cb2facc0f23d14d5'
MASK_SHA = '382ae8d2ffa8908979050b5e83f38ec9967b461bbf9b614dd92775da90e409ba'
DATA_OFFSET = 113770496
SYSGRA_OFFSET = 895488
TUIKA_OFFSET = 78848
MEMBER_SIZE = 7912
ALLOWED_MEMBER_POS = DATA_OFFSET + SYSGRA_OFFSET + TUIKA_OFFSET
# Text was READ from a private original-source preview; not OCR, not program evidence.
# These labels are *not* approved translations or proof of context in gameplay.
LABELS = (
    ('mixed_level_japanese', 'Normal & Warrior LV. [Japanese glyphs at right]', None),
    ('level', 'Gamble Merchant LV.', None),
    ('level', 'Angel Guard LV.', None),
    ('level', 'Demon Magic LV.', None),
    ('level', 'Hell Dragon LV.', None),
    ('message', 'Nullified traps!', '¡Trampas anuladas!'),
    ('message', 'Scattered G!', '¡G dispersos!'),
    ('message', 'Replenished HP for all!', '¡HP recuperados para todos!'),
    ('message', 'Recovered SP!', '¡SP recuperados!'),
    ('message', 'Attack all enemies on screen!', '¡Ataca a todos los enemigos en pantalla!'),
    ('mixed_label_control', 'G Star On! [control glyphs to right]', None),
    ('control_symbols', '[control symbols, F and punctuation]', None),
    ('digits', '[digit glyphs 0-9]', None),
    ('mixed_digits_message', '[digit glyphs 0-9] No special attack', 'Sin ataque especial'),
)


def sha_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def full_file_sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def verify_output(output: Path, repo: Path | None = None) -> Path:
    output = Path(output).expanduser()
    if not output.is_absolute() or output.suffix.lower() != '.json' or output.is_symlink():
        raise ValueError('Private output must be a new absolute .json without symlinks')
    resolved = output.resolve(strict=False)
    root = (repo or Path(__file__).resolve().parents[1]).resolve()
    if resolved == root or root in resolved.parents:
        raise ValueError('Refusing output inside checkout')
    if resolved.exists() or output.exists():
        raise FileExistsError('Refusing overwrite')
    if any((p / '.git').exists() for p in resolved.parents):
        raise ValueError('Refusing output inside any git repository')
    return output


def inspect_indices(index_pixels: list[int], width: int, height: int,
                    labels: tuple = LABELS, *, strict: bool = True) -> dict:
    if width <= 0 or height <= 0 or len(index_pixels) != width * height:
        raise ValueError('Invalid indexed surface dimensions')
    if any(not isinstance(x, int) or isinstance(x, bool) or x < 0 or x > 15 for x in index_pixels):
        raise ValueError('Invalid indexed pixel value')
    mask = bytes(255 if value == 2 else 0 for value in index_pixels)
    geometry = analyze_strips(mask, width, height, strict_real=strict)
    bands = geometry['stripes']
    if len(labels) != len(bands):
        raise ValueError('Label count cannot be silently inferred or resized')
    items=[]
    for g,(kind,english,spanish) in zip(bands, labels):
        y0,y1=g['y_first'],g['y_last_inclusive']
        x0,x1=g['x_first_clut2'],g['x_last_clut2_inclusive']
        # Counts in the bounding rectangle NOT ONLY CLUT2: a whole-rectangle
        # overwrite risks opaque black outlines and other palette indices.
        region=[index_pixels[y*width+x] for y in range(y0,y1+1) for x in range(x0,x1+1)]
        byindex={str(n): region.count(n) for n in range(16) if region.count(n)}
        # The 14-row atlas is opaque rasterized material, not a text encoding.
        items.append({
            'stripe_index':g['stripe_index'],
            'y_first':y0,'y_last_inclusive':y1,
            'x_first_clut2':x0,'x_last_clut2_inclusive':x1,
            'clut2_pixel_count':g['pixels_clut2'],
            'bbox_pixel_count':len(region),
            'non_clut2_pixels_inside_bbox':len(region)-g['pixels_clut2'],
            'clut1_opaque_black_pixels_inside_bbox':byindex.get('1',0),
            'bbox_palette_index_counts':byindex,
            'source_text_manual_visual_read':english,
            'source_type_manual_visual_read':kind,
            'draft_es_candidate_UNAPPROVED':spanish,
            'requires_in_game_scene_confirmation':True,
            'requires_manual_glyph_glossary_and_layout_review':True,
            'safe_to_replace_whole_band':False,
            'safe_to_replace_bbox':False,
            'safe_to_replace_clut2_only':False,
        })
    counts={kind:sum(t['source_type_manual_visual_read']==kind for t in items)
            for kind in sorted(set(t[0] for t in labels))}
    return {
        'schema':'cladun.f2.tuika_original_manual_raster_label_catalog.v1',
        'source_type':'AUTHENTIC_ORIGINAL_ISO_STATIC_RASTER_PLUS_MANUAL_VISUAL_INTERPRETATION',
        'source_member':'SYSGRA.ARC/TUIKA_MES.IMY',
        'raster_dimensions_px':[width,height],
        'clut2_mask_sha256':sha_bytes(mask),
        'clut2_pixels':mask.count(255),
        'stripes':items,
        'stripe_count':len(items),
        'visual_category_counts':counts,
        'multiple_types_of_non_text_graphic_present':True,
        'band_equals_translatable_string_proven':False,
        'visual_transcriptions_verified_by_gameplay':False,
        'translations_applied_to_iso':False,
        'ppsspp_1204_ran':False,
        'mips_ram_ge_vram_origin_proven':False,
        'bitmap_indices_or_pixels_exported':False,
        'note':'Visual labels are readings of private original atlas preview, not automatically recognized bytes. Japanese glyphs and control symbols need a separate verified transcription. Do not treat any bbox as writable ROI.',
    }


def audit_original_iso(iso: Path) -> dict:
    iso=Path(iso)
    if iso.stat().st_size!=SOURCE_SIZE or full_file_sha(iso)!=SOURCE_SHA:
        raise ValueError('Original user ISO size/SHA256 mismatch')
    with iso.open('rb') as f:
        f.seek(ALLOWED_MEMBER_POS)
        member=f.read(MEMBER_SIZE)
    if sha_bytes(member)!=ORIGINAL_MEMBER_SHA:
        raise ValueError('TUIKA original member hash mismatch')
    indexed, meta=decode_imy(member)
    if sha_bytes(indexed)!=INDEX_SHA or meta['width_pixels_if_4bpp']!=256 or meta['rows']!=256:
        raise ValueError('Expected native original TUIKA raster mismatch')
    linear=unswizzle_psp(indexed,128,256)
    indices=[]
    for byte in linear:
        indices.extend((byte&15,byte>>4))
    report=inspect_indices(indices,256,256,strict=True)
    if report['clut2_mask_sha256']!=MASK_SHA or len(report['stripes'])!=14:
        raise ValueError('Expected original TUIKA CLUT2 mask mismatch')
    report.update({'iso_sha256':SOURCE_SHA,
                   'imy_member_sha256':ORIGINAL_MEMBER_SHA,
                   'decoded_swizzled_index_sha256':INDEX_SHA,
                   'region_opaque_index1_pixels_total':sum(x['clut1_opaque_black_pixels_inside_bbox'] for x in report['stripes'])})
    return report


def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso-usa', type=Path, required=True)
    p.add_argument('--reporte-privado', type=Path, required=True)
    args=p.parse_args()
    output=verify_output(args.reporte_privado)
    res=audit_original_iso(args.iso_usa)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as stream:
        json.dump(res,stream,ensure_ascii=False,indent=2)
        stream.write('\n')
    print(json.dumps({'authentic_iso':True,'bands':res['stripe_count'],
                      'clut2_pixels':res['clut2_pixels'],
                      'non_text_present':res['multiple_types_of_non_text_graphic_present'],
                      'in_game_proof':res['ppsspp_1204_ran']}))


if __name__ == '__main__':
    main()
