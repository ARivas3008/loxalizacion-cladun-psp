#!/usr/bin/env python3
"""Private ONLY preview of the 27 authentic SYSGRA indexed textures (NOT PPSSPP).

No game data, decoded images, commercial screenshots, or PNGs are committed.
The resulting image is a static ISO resource contact sheet, NOT game footage.
Pillow is needed only to render a private preview (CI tests need no Pillow).
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

try:
    from tools.f2_auditar_27_imy_sysgra import (
        decode_imy, inspect_sysgra, DATA_OFFSET, SYSGRA_OFFSET, SYSGRA_SIZE,
        ISO_SIZE, ISO_SHA, file_sha,
    )
except ModuleNotFoundError:
    from f2_auditar_27_imy_sysgra import (
        decode_imy, inspect_sysgra, DATA_OFFSET, SYSGRA_OFFSET, SYSGRA_SIZE,
        ISO_SIZE, ISO_SHA, file_sha,
    )

ROWS, COLUMNS = 7, 4
CELL_W, CELL_H = 330, 344

def unswizzle_psp(raw: bytes, stride_bytes: int, rows: int) -> bytes:
    """PSP GE tiled 16-byte by 8-row blocks -> linear bytes (does not alter CLUT)."""
    if (stride_bytes < 16 or stride_bytes % 16 or rows < 8 or rows % 8
            or len(raw) != stride_bytes * rows):
        raise ValueError("PSP unswizzle geometry/length invalid")
    linear = bytearray(len(raw))
    cols = stride_bytes // 16
    for block_y in range(rows // 8):
        for block_x in range(cols):
            source = (block_y * cols + block_x) * 128
            for local_y in range(8):
                target = (block_y * 8 + local_y) * stride_bytes + block_x * 16
                linear[target:target + 16] = raw[source + local_y * 16:source + local_y * 16 + 16]
    return bytes(linear)

def rgba_palette(imy: bytes) -> list[tuple[int,int,int,int]]:
    """Return only the palette from the two audited IMY header layouts."""
    if len(imy) < 98 or imy[:4] != b'IMY\x00' or imy[4] not in (0x20, 0x60):
        raise ValueError("IMY palette header invalid")
    count = 256 if imy[4] == 0x20 else 16
    limit = 0x420 if count == 256 else 0x60
    if len(imy) < limit + 2:
        raise ValueError("Truncated IMY palette")
    return [tuple(imy[i:i+4]) for i in range(0x20, limit, 4)]

def indexed_rgba_4bpp(
    tiled: bytes, stride_bytes: int, rows: int,
    palette: list[tuple[int,int,int,int]]
) -> tuple[list[tuple[int,int,int,int]], int, int]:
    """A4 texture only; PSP nibble order = low first, then high."""
    if len(palette) < 16:
        raise ValueError("4bpp requires at least sixteen palette entries")
    raw = unswizzle_psp(tiled, stride_bytes, rows)
    pixels = []
    for byte in raw:
        pixels.append(palette[byte & 15])
        pixels.append(palette[(byte >> 4) & 15])
    return pixels, stride_bytes * 2, rows

def verify_private_path(output: Path, *, source_root: Path | None = None) -> Path:
    """Fail closed even for a symlink resolving into the Git checkout."""
    output = Path(output).expanduser()
    if not output.is_absolute() or output.suffix.lower() != ".png":
        raise ValueError("Private PNG output must be an absolute .png path")
    repo_root = (source_root or Path(__file__).resolve().parents[1]).resolve()
    resolved = output.resolve(strict=False)
    if resolved == repo_root or repo_root in resolved.parents:
        raise ValueError("Refusing to write commercial-resource preview inside repository")
    if resolved.exists() or output.exists():
        raise FileExistsError("Refusing to overwrite private evidence")
    return output

def render(iso: Path, output: Path) -> dict:
    """Exact USA ISO input; private preview only, no original asset byte export."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError as exc:
        raise RuntimeError("Install Pillow only for private preview: pip install pillow") from exc
    output = verify_private_path(output)
    iso = Path(iso)
    if iso.stat().st_size != ISO_SIZE or file_sha(iso) != ISO_SHA:
        raise ValueError("Original ISO USA SHA256/size mismatch")
    with iso.open("rb") as f:
        f.seek(DATA_OFFSET + SYSGRA_OFFSET)
        archive = f.read(SYSGRA_SIZE)
    manifest = inspect_sysgra(archive)
    if manifest["decoded_members_count"] != 27:
        raise ValueError("Unexpected original SYSGRA count")
    canvas = Image.new("RGB", (CELL_W*COLUMNS, CELL_H*ROWS), (32,33,38))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    graphic_labels = []
    palette_panels = []
    for index in range(27):
        cell = archive[16+48*index:16+48*(index+1)]
        name = cell[:40].split(b"\0",1)[0].decode("ascii")
        size, offset = struct.unpack_from("<II", cell, 40)
        member = archive[offset:offset+size]
        raw, meta = decode_imy(member)
        colors = rgba_palette(member)
        x0, y0 = (index%COLUMNS)*CELL_W, (index//COLUMNS)*CELL_H
        draw.text((x0+12,y0+9), f"{index:02d} {name}", font=font, fill=(247,247,247))
        if member[10] == 0x84:
            # PALETE_0..3 are color definitions. Their 0x84 index surface is NOT
            # incorrectly drawn as a sprite: render the stored 256-color swatches.
            if len(colors) != 256:
                raise ValueError("0x84 color definition needs 256 RGBA entries")
            swatches = Image.new("RGBA",(16,16))
            swatches.putdata(colors)
            tile = swatches.resize((280,280),Image.Resampling.NEAREST)
            palette_panels.append(name)
            descr = "256 RGBA stored colors (NOT a game frame)"
        elif member[10] == 0xA4:
            stride = meta["width_pixels_if_4bpp"]//2
            pixels,w,h = indexed_rgba_4bpp(raw,stride,meta["rows"],colors)
            tile = Image.new("RGBA",(w,h))
            tile.putdata(pixels)
            tile.thumbnail((310,280),Image.Resampling.NEAREST)
            graphic_labels.append(name)
            descr = f"Original 4bpp {w}x{h}; static ISO resource"
        else:
            raise ValueError("Unexpected IMY pixel format")
        draw.text((x0+12,y0+25),descr,font=font,fill=(176,186,196))
        bg = Image.new("RGB",(310,285),(62,62,62))
        back = ImageDraw.Draw(bg)
        for cy in range(0,285,18):
            for cx in range(0,310,18):
                if (cx//18+cy//18)%2 == 0:
                    back.rectangle((cx,cy,cx+17,cy+17),fill=(93,93,93))
        bg.paste(tile,((310-tile.width)//2,(285-tile.height)//2),tile)
        canvas.paste(bg,(x0+10,y0+51))
    output.parent.mkdir(parents=True,exist_ok=True)
    # x-binary exclusive: no accidental replacement of private evidence.
    with output.open("xb") as fp:
        canvas.save(fp,format="PNG",optimize=True)
    digest = file_sha(output)
    return {
        "schema":"cladun.f2.private_original_sysgra_atlas_preview.v1",
        "source_iso_sha256":ISO_SHA,
        "source_archive_sha256":manifest["sysgra_sha256"],
        "output_type":"STATIC_UNSWIZZLED_ORIGINAL_ASSET_PREVIEW_NOT_PPSSPP",
        "output_file_private":output.name,
        "output_sha256":digest,
        "output_image_width":canvas.width,
        "output_image_height":canvas.height,
        "images_4bpp_rendered":len(graphic_labels),
        "color_table_swatches_rendered":len(palette_panels),
        "labels":graphic_labels,
        "palette_panels":palette_panels,
        "runtime_usage_proven":False,
        "contains_original_game_art":True,
        "DO_NOT_COMMIT_PNG_TO_GITHUB":True,
    }

def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--iso-usa",type=Path,required=True)
    ap.add_argument("--salida-privada",type=Path,required=True)
    args=ap.parse_args()
    print(json.dumps(render(args.iso_usa,args.salida_privada),ensure_ascii=False,indent=2))

if __name__ == "__main__":
    main()
