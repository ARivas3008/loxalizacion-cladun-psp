#!/usr/bin/env python3
"""F2: map the 14 TUIKA CLUT2 stripes from an authenticated private ISO pair.

ONLY metadata is emitted. The mask is from static PSP IMY decoding, not PPSSPP.
No game pixels, CLUT data, PNG, or modified ISO are written to GitHub.
These stripes are not automatically verified as strings or safe editing ROIs.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

try:
    from tools.f2_cotejar_impacto_clut_tuika import inspect_source_and_probe
except ModuleNotFoundError:
    from f2_cotejar_impacto_clut_tuika import inspect_source_and_probe

EXPECTED_MASK_SHA = '382ae8d2ffa8908979050b5e83f38ec9967b461bbf9b614dd92775da90e409ba'
EXPECTED_STRIP_COUNT = 14
EXPECTED_PIXELS = 9144
HEX_SHA = re.compile(r'^[0-9a-f]{64}$')


def safe_private_json(path: Path, checkout: Path | None = None) -> Path:
    """Fail closed on symlinks, local git checkouts and overwrites."""
    path = Path(path).expanduser()
    if not path.is_absolute() or path.suffix.lower() != '.json' or path.is_symlink():
        raise ValueError('An absolute new private .json (not symlink) is required')
    resolved = path.resolve(strict=False)
    repo = (checkout or Path(__file__).resolve().parents[1]).resolve()
    if resolved == repo or repo in resolved.parents:
        raise ValueError('Output must be outside the checkout')
    if resolved.exists() or path.exists():
        raise FileExistsError('Never overwrite evidence')
    if any((p / '.git').exists() for p in resolved.parents):
        raise ValueError('Output is within another Git repository')
    return path


def analyze_strips(mask: bytes, width: int, height: int, *, strict_real: bool = True) -> dict:
    """Derive band envelopes only, never conclude a band is translatable text.

    The byte-mask format is exactly one 0 or 255 per pixel, row-major.
    The band hash covers only the masked pixel footprint in that band.
    """
    if not isinstance(mask, bytes) or not (1 <= width <= 4096 and 1 <= height <= 4096):
        raise ValueError('Invalid mask type or dimensions')
    if width * height != len(mask):
        raise ValueError('Mask length does not match dimensions')
    if any(v not in (0, 255) for v in mask):
        raise ValueError('Mask must contain binary 0/255 values')
    mask_sha = hashlib.sha256(mask).hexdigest()
    rows = [mask[y * width:(y + 1) * width] for y in range(height)]
    active = [y for y, row in enumerate(rows) if 255 in row]
    if not active:
        raise ValueError('Mask contains no CLUT2 pixels')
    spans = []
    first = last = active[0]
    for y in active[1:]:
        if y != last + 1:
            spans.append((first, last))
            first = y
        last = y
    spans.append((first, last))
    result = []
    for number, (y0, y1) in enumerate(spans):
        xs = set()
        changed = 0
        for y in range(y0, y1 + 1):
            row = rows[y]
            changed += row.count(255)
            xs.update(x for x, val in enumerate(row) if val == 255)
        x0, x1 = min(xs), max(xs)
        x_runs = 0
        previous_active = False
        for x in range(width):
            now = x in xs
            if now and not previous_active:
                x_runs += 1
            previous_active = now
        content = b''.join(rows[y0:y1 + 1])
        result.append({
            'stripe_index': number,
            'y_first': y0,
            'y_last_inclusive': y1,
            'height': y1 - y0 + 1,
            'x_first_clut2': x0,
            'x_last_clut2_inclusive': x1,
            'observed_clut2_bbox_width': x1 - x0 + 1,
            'pixels_clut2': changed,
            'distinct_columns_clut2': len(xs),
            'horizontal_occupied_runs': x_runs,
            'blank_rows_before': y0 if number == 0 else y0 - spans[number - 1][1] - 1,
            'blank_rows_after': height - y1 - 1 if number == len(spans) - 1 else spans[number + 1][0] - y1 - 1,
            'stripe_mask_sha256': hashlib.sha256(content).hexdigest(),
            'automatically_approved_for_translation': False,
        })
    if sum(s['pixels_clut2'] for s in result) != mask.count(255):
        raise ValueError('Lost pixels during row band segmentation')
    if strict_real and ((width, height) != (256, 256) or
            len(result) != EXPECTED_STRIP_COUNT or mask.count(255) != EXPECTED_PIXELS or
            mask_sha != EXPECTED_MASK_SHA):
        raise ValueError('Authenticated real TUIKA mask properties differ')
    return {
        'schema': 'cladun.f2.tuika_clut2_band_geometry_metadata.v1',
        'scope': 'STATIC_IMY_INDICES_NOT_PPSSPP',
        'dimensions_px': [width, height],
        'mask_sha256': mask_sha,
        'total_clut2_pixels': mask.count(255),
        'stripe_count': len(result),
        'stripe_pixel_sum_verified': True,
        'stripes': result,
        'text_identity_per_band_proven': False,
        'runtime_visibility_proven': False,
        'ge_vram_proven': False,
        'translation_safe_rois_proven': False,
        'original_art_or_pixels_in_report': False,
        'caveat': ('Bounding rectangles contain other CLUT indices and possibly shared art. '
                   'A horizontal band is not proof of a separate text string or safe edit area.'),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso-usa', type=Path, required=True)
    p.add_argument('--iso-sonda', type=Path, required=True)
    p.add_argument('--reporte-privado', type=Path, required=True)
    args = p.parse_args()
    output = safe_private_json(args.reporte_privado)
    parent, mask, _, _ = inspect_source_and_probe(args.iso_usa, args.iso_sonda)
    report = analyze_strips(mask, *parent['texture_dimensions_px'])
    report.update({'original_iso_sha256': parent['original_iso_sha256'],
                   'probe_iso_sha256': parent['probe_iso_sha256'],
                   'parent_raster_sha256': parent['decoded_pixel_index_sha256']})
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open('x', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write('\n')
    print(json.dumps({'stripe_count': report['stripe_count'],
                      'total_clut2_pixels': report['total_clut2_pixels'],
                      'runtime_visibility_proven': False}))


if __name__ == '__main__':
    main()
