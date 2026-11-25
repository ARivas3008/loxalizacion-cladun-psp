#!/usr/bin/env python3
"""F2 read-only audit: all glyphs/margins/atlas pixel preservation. ISO stays private.

Prints glyph codes, indices and SHA-256 of individual rasters, never textures.
This does not prove code-vs-index lookup at runtime.
"""
from __future__ import annotations
import sys, json, hashlib, struct, argparse
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from font_es_patch import archive, decode_imy_texture, sha256_file
from font_es_narrow import atlas_slots, unswizzle
from extract_cladun import iso9660_entries, read_iso_file, pspfs_entries, dsarc_entries
from charset_es import ES_GLYPHS, ES_BYTES

def font(iso, original=False):
    if original:
        _, _, _, _, arc, members = archive(iso)
    else:
        _, entries = iso9660_entries(iso)
        record = next(e for e in entries if e["path"] == "PSP_GAME/USRDIR/DATA.DAT")
        with iso.open("rb") as handle:
            handle.seek(record["offset"])
            pack = handle.read(record["size"])
        files = pspfs_entries(pack)
        member = next(f for f in files if f["name"] == "FONT.ARC")
        arc = pack[member["offset"]:member["offset"] + member["size_stored"]]
        members = dsarc_entries(arc)
    header = members[0]
    index = arc[header["offset"]:header["offset"] + header["size"]]
    count = struct.unpack_from("<I", index)[0]
    records = [index[4 + i*4:8 + i*4] for i in range(count)]
    codes = [struct.unpack_from("<H", record)[0] for record in records]
    slots = atlas_slots([
        unswizzle(decode_imy_texture(arc[m["offset"]:m["offset"] + m["size"]]))
        for m in members[1:]
    ])
    return codes, records, slots, index, members

def audit(original, candidate):
    oc, old_records, old_slots, ob, om = font(original, True)
    nc, new_records, new_slots, nb, nm = font(candidate)
    assert len(oc) == 2721 and len(nc) == 2740
    assert len(old_slots) == len(new_slots) == 3072
    assert nc == oc[:95] + list(range(0xA1, 0xB4)) + oc[95:]
    assert new_records[:95] + new_records[114:] == old_records
    assert all(old_slots[i] == new_slots[i + (19 if i >= 95 else 0)] for i in range(2721))
    assert len(set(nc)) == len(nc)
    symbols = []
    for char in "□○×△■●▲◆▼→←↑↓LR":
        encoded = char.encode("cp932")
        code = int.from_bytes(encoded, "big")
        if code not in oc:
            raise AssertionError("Unknown original symbol " + char)
        before, after = oc.index(code), nc.index(code)
        symbols.append({
            "unicode": f"U+{ord(char):04X}", "cp932_hex": encoded.hex().upper(),
            "original_index": before, "spanish_index": after,
            "original_page": before // 512, "new_page": after // 512,
            "original_cell": [before % 32, before % 512 // 32],
            "new_cell": [after % 32, after % 512 // 32],
            "raster_unchanged": old_slots[before] == new_slots[after],
            "raster_sha256": hashlib.sha256(old_slots[before]).hexdigest(),
        })
    spanish = []
    for char in ES_GLYPHS:
        code = ES_BYTES[char][0]
        i = nc.index(code)
        spanish.append({
            "character": char, "unicode": f"U+{ord(char):04X}",
            "cp932_byte": f"{code:02X}", "new_index": i,
            "page": i // 512, "cell": [i % 32, i % 512 // 32],
            "nonempty": bool(any(new_slots[i])),
            "raster_sha256": hashlib.sha256(new_slots[i]).hexdigest(),
            "advance_record_hex": new_records[i][2:].hex(),
        })
    files = iso9660_entries(original)[1]
    boot = next(x for x in files if x["path"] == "PSP_GAME/SYSDIR/BOOT.BIN")
    eboot = next(x for x in files if x["path"] == "PSP_GAME/SYSDIR/EBOOT.BIN")
    raw_boot = read_iso_file(original, boot)
    raw_eboot = read_iso_file(original, eboot)
    return {
        "schema": "cladun.f2.atlas_provenance.v1",
        "original_iso_sha256": sha256_file(original),
        "f1_iso_sha256": sha256_file(candidate),
        "original_font_bin_sha256": hashlib.sha256(ob).hexdigest(),
        "f1_font_bin_sha256": hashlib.sha256(nb).hexdigest(),
        "original_glyphs": len(oc), "new_glyphs": len(nc),
        "spanish_glyphs": len(spanish), "insert_position": 95,
        "inserted_single_byte_codes": "A1-B3",
        "original_code_records_unchanged": sum(
            oc[i] == nc[i+(19 if i >= 95 else 0)] for i in range(len(oc))),
        "original_metric_records_unchanged": sum(
            old_records[i][2:] == new_records[i+(19 if i >= 95 else 0)][2:]
            for i in range(len(oc))),
        "original_rasters_unchanged": sum(
            old_slots[i] == new_slots[i+(19 if i >= 95 else 0)]
            for i in range(len(oc))),
        "font_arc_members_original": [m["name"] for m in om],
        "font_arc_members_spanish": [m["name"] for m in nm],
        "symbols": symbols, "spanish": spanish,
        "executable_provenance": {
            "boot_size": len(raw_boot), "boot_all_zero": not any(raw_boot),
            "eboot_size": len(raw_eboot), "eboot_magic_hex": raw_eboot[:4].hex(),
            "warning": "On-disc ~PSP encrypted EBOOT is not disassembled in this static audit.",
        },
        "limitations": "Static pixel-index equality does not determine runtime sprite lookup.",
    }

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--original", required=True, type=Path)
    p.add_argument("--f1", required=True, type=Path)
    p.add_argument("--salida", required=True, type=Path)
    a = p.parse_args()
    if a.salida.exists() or a.salida.resolve() in (a.original.resolve(), a.f1.resolve()):
        p.error("Destination must be a new independent report")
    report = audit(a.original, a.f1)
    a.salida.parent.mkdir(parents=True, exist_ok=True)
    with a.salida.open("x", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({k:v for k,v in report.items() if k not in ("symbols","spanish")},
                     ensure_ascii=False,indent=2))
