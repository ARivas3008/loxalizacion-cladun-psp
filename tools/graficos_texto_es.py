#!/usr/bin/env python3
"""Precisely bounded graphical-text localization for Cladun SYS.DAT2 PNGs.

Never commits any original or edited proprietary texture. Only works on the
exact six PNGs from the audited USA ISO; other pixels outside each declared
text ROI must be bit-identical in RGB, even if the PNG compression differs.

This is *graphical text*, not a change to unrelated graphics or tiles. The
visual results still require on-device/PPSSPP review. Requires Pillow >= 12.
"""
from __future__ import annotations

import hashlib
import io
from pathlib import Path
import json

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:
    raise RuntimeError("Pillow >= 12 is required to localize the graphic text") from exc

# name: (source PNG SHA-256, x0,y0,x1,y1, font_size, text, foreground)
GRAPHICS = {
    "PIC1.PNG": ("42d4d60ac2f44e9bf7d908bd081a126ca59a95a0765941133b284d8a260e24e7",
                 (310, 248, 418, 265), 9, "¡Esto es un RPG!", (238, 235, 231)),
    "DOT_PIC1.PNG": ("2464018e3fe528c8b83daf0512409a00b6a755408cb14fcadf12bb01c2afa704",
                     (310, 248, 418, 265), 9, "¡Esto es un RPG!", (238, 235, 231)),
    "SAVE.PNG": ("3aba8f82a50736ed89f6b783589a6bc21b9f99970b8ca134ac9c6c52893960da",
                 (60, 37, 111, 51), 6, "¡Esto es un RPG!", (248, 248, 240)),
    "DOT_SAVE.PNG": ("8a29151722f8fc61bcd16e3ce9480f8f7d06c8265411e77352fe746f77082159",
                     (43, 36, 110, 51), 6, "¡Esto es un RPG!", (248, 248, 240)),
    "NODATA.PNG": ("eb3b9536b7c0046ce5d2e1d2e794088566cc2344976363fb7169d7d8c33c9b7c",
                   (20, 29, 126, 56), 17, "SIN DATOS", (255, 255, 255)),
    "DOT_NODATA.PNG": ("516c621ee8257d43aa6ed544439e748214755723eaf1b6a17a61958f9f7bb2d8",
                       (20, 29, 126, 56), 17, "SIN DATOS", (255, 255, 255)),
}

DIMENSIONS = {
    "PIC1.PNG": (480, 272), "DOT_PIC1.PNG": (480, 272),
    "SAVE.PNG": (144, 80), "DOT_SAVE.PNG": (144, 80),
    "NODATA.PNG": (144, 80), "DOT_NODATA.PNG": (144, 80),
}


def require(ok, why):
    if not ok:
        raise ValueError(why)


def mask_pixels(name, image, roi):
    x0, y0, x1, y1 = roi
    selected = set()
    for y in range(y0, y1):
        for x in range(x0, x1):
            r, g, b = image.getpixel((x, y))
            if name.endswith("NODATA.PNG"):
                is_letter = (r, g, b) in {(255, 255, 255), (186, 105, 19)}
            elif name.endswith("PIC1.PNG"):
                is_letter = ((r > 105 and abs(r - g) < 16 and abs(g - b) < 16) or
                             (r < 45 and g < 35 and b < 30 and y >= 250))
            else:
                is_letter = ((r > 95 and abs(r - g) < 17 and abs(g - b) < 17) or
                             (r < 65 and g < 55 and b < 50 and y >= 40))
            if is_letter:
                selected.add((x, y))
    # Remove one-pixel antialias/shadow fringe, clipped strictly to the text ROI.
    padded = set(selected)
    for x, y in selected:
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if x0 <= x + dx < x1 and y0 <= y + dy < y1:
                    padded.add((x + dx, y + dy))
    return padded


def reconstruct_background(image, mask):
    """Bounded, local inverse-distance fill; no changes outside the mask."""
    source = image
    output = image.copy()
    for x, y in mask:
        samples = []
        for dx, dy in ((0, 1), (0, -1), (1, 0), (-1, 0),
                       (1, 1), (1, -1), (-1, 1), (-1, -1)):
            for distance in range(1, 14):
                xx, yy = x + dx * distance, y + dy * distance
                if not (0 <= xx < image.width and 0 <= yy < image.height):
                    break
                if (xx, yy) in mask:
                    continue
                samples.append((1 / (distance * distance), source.getpixel((xx, yy))))
                break
        if samples:
            divisor = sum(weight for weight, rgb in samples)
            rgb = tuple(round(sum(weight * c[component] for weight, c in samples) / divisor)
                        for component in range(3))
            output.putpixel((x, y), rgb)
    return output


def verify_outside_roi(original, translated, roi):
    """Pixel equality on four disjoint regions covering everything outside ROI."""
    x0, y0, x1, y1 = roi
    require(original.size == translated.size and original.mode == translated.mode,
            "Image geometry/color mode changed")
    regions = [
        (0, 0, original.width, y0),
        (0, y1, original.width, original.height),
        (0, y0, x0, y1),
        (x1, y0, original.width, y1),
    ]
    for region in regions:
        if original.crop(region).tobytes() != translated.crop(region).tobytes():
            raise ValueError("Nontext pixel changed outside authorized ROI: " + str(region))
    return True


def patch_png(name: str, original: bytes, spanish: str) -> tuple[bytes, dict]:
    require(name in GRAPHICS, "Unapproved graphical asset")
    digest, roi, font_size, expected, color = GRAPHICS[name]
    require(spanish == expected, "Graphics text does not match the approved translation")
    require(hashlib.sha256(original).hexdigest() == digest,
            "Original PNG differs from the audited Cladun USA disc")
    with Image.open(io.BytesIO(original)) as picture:
        picture.load()
        require(picture.mode == "RGB" and picture.size == DIMENSIONS[name],
                "Unexpected PNG color mode or dimensions")
        source = picture.copy()
    mask = mask_pixels(name, source, roi)
    require(len(mask) > 90, "Original glyph mask not found")
    candidate = reconstruct_background(source, mask)
    font = ImageFont.load_default(size=font_size)
    pencil = ImageDraw.Draw(candidate)
    bounds = pencil.textbbox((0, 0), spanish, font=font)
    width, height = bounds[2] - bounds[0], bounds[3] - bounds[1]
    x0, y0, x1, y1 = roi
    require(width <= x1 - x0 - 2 and height <= y1 - y0 - 2,
            "Spanish label would overflow its rectangle")
    x = x0 + (x1 - x0 - width) // 2
    y = y0 + (y1 - y0 - height) // 2 - bounds[1]
    pencil.text((x + 1, y + 1), spanish, font=font, fill=(23, 20, 18))
    pencil.text((x, y), spanish, font=font, fill=color)
    verify_outside_roi(source, candidate, roi)
    altered = sum(source.getpixel((x, y)) != candidate.getpixel((x, y))
                  for y in range(y0, y1) for x in range(x0, x1))
    require(altered > 0, "Graphics label had no effect")
    buffer = io.BytesIO()
    candidate.save(buffer, format="PNG", optimize=True)
    with Image.open(io.BytesIO(buffer.getvalue())) as reread:
        reread.load()
        require(reread.tobytes() == candidate.tobytes(),
                "PNG re-encoding did not preserve RGB pixels")
    report = {
        "asset": name, "roi": list(roi),
        "pixels_changed_inside_text_roi": altered,
        "source_sha256": digest,
        "pixel_exact_outside_text_roi": True,
        "ppsspp_visual_verified": False,
    }
    return buffer.getvalue(), report


def patch_private_directory(source_dir: Path, out_dir: Path, report: Path):
    source_dir, out_dir, report = map(Path, (source_dir, out_dir, report))
    require(source_dir.resolve() != out_dir.resolve(), "Never modify sources in place")
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, cfg in GRAPHICS.items():
        output, audit = patch_png(name, (source_dir / name).read_bytes(), cfg[3])
        target = out_dir / name
        require(not target.exists(), "Refusing to overwrite patched image")
        target.write_bytes(output)
        rows.append(audit)
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps({"status": "PIXEL_GUARD_PASS_NOT_RUNTIME",
                                 "six_graphics": rows}, indent=2, ensure_ascii=False) + "\n",
                      encoding="utf-8")
    return rows


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--origen", type=Path, required=True, help="Private extracted original PNG dir")
    ap.add_argument("--salida", type=Path, required=True, help="Private output PNG dir")
    ap.add_argument("--informe", type=Path, required=True, help="Noncommercial JSON report")
    args = ap.parse_args()
    print(json.dumps(patch_private_directory(args.origen, args.salida, args.informe),
                     ensure_ascii=False, indent=2))
