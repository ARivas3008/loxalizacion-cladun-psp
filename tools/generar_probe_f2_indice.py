#!/usr/bin/env python3
"""F2 differential font-only ISO probes. PRIVATE; never a localization release.

Requires F1 canonical source SHA. Touches FONT.ARC atlas only; no corpus or scripts.
The C glyph is a mandatory positive control; □○×△ use old vs new slots.
A real PPSSPP test must decide what the button symbols actually use.
"""
from __future__ import annotations
import argparse, json, struct, shutil, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from extract_cladun import iso9660_entries, pspfs_entries, dsarc_entries
from font_es_patch import decode_imy_texture, u32, u16, sha256_file
from font_es_narrow import atlas_slots, encode_atlas, unswizzle

F1_SHA = "496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986"
ORIGINAL_COUNT, NEW_COUNT = 2721, 2740
SYMBOLS, POSITIVE, ASCII_SYMBOLS = "□○×△", "C", "LR"

def code_of(character):
    return int.from_bytes(character.encode("cp932"), "big")

def get_probe_indices(old_codes, new_codes, mode):
    if mode not in ("old", "new"):
        raise ValueError("Only old or new positions allowed")
    assert len(old_codes) == ORIGINAL_COUNT and len(new_codes) == NEW_COUNT
    assert new_codes == old_codes[:95] + list(range(0xA1, 0xB4)) + old_codes[95:]
    def location(code, codes):
        if code not in codes:
            raise ValueError("Unknown glyph code")
        return codes.index(code)
    selected = {
        ch: location(code_of(ch), old_codes if mode == "old" else new_codes)
        for ch in SYMBOLS
    }
    selected.update({ch:location(code_of(ch), new_codes) for ch in POSITIVE+ASCII_SYMBOLS})
    assert len(set(selected.values())) == len(selected)
    return selected

def rebuild_archive(arc, members, slots):
    expected = ["FONT.BIN"] + [f"FONT_{i:02d}.IMY" for i in range(6)]
    if not arc.startswith(b"DSARCIDX") or len(members) != 7 or [
        m["name"] for m in members] != expected:
        raise ValueError("Unknown FONT.ARC layout")
    font_member = members[0]
    fontbin = arc[font_member["offset"]:font_member["offset"]+font_member["size"]]
    if u32(fontbin) != NEW_COUNT:
        raise ValueError("Unexpected FONT.BIN count")
    source_imy = [arc[m["offset"]:m["offset"]+m["size"]] for m in members[1:]]
    old_slots = atlas_slots([unswizzle(decode_imy_texture(v)) for v in source_imy])
    new_slots = old_slots.copy()
    for index in slots.values():
        if not any(old_slots[index]):
            raise ValueError(f"Blank positive/negative control at {index}")
        new_slots[index] = bytes([1] * 256)
    images = encode_atlas(new_slots, source_imy)
    buf = bytearray(arc[:font_member["offset"]])
    table_start = (16 + len(members)*2 + 3) // 4 * 4
    for i, binary in enumerate([fontbin] + images):
        offset = font_member["offset"] if i == 0 else ((len(buf)+511)//512)*512+16
        if len(buf) < offset:
            buf.extend(bytes(offset-len(buf)))
        buf.extend(binary)
        struct.pack_into("<II",buf,table_start+i*48+40,len(binary),offset)
    if len(buf) % 16:
        buf.extend(bytes(16-len(buf)%16))
    parsed = dsarc_entries(bytes(buf))
    if [m["name"] for m in parsed] != expected:
        raise ValueError("DSARC member list unexpectedly changed")
    actual_font = buf[parsed[0]["offset"]:parsed[0]["offset"]+parsed[0]["size"]]
    if actual_font != fontbin:
        raise ValueError("FONT.BIN code table changed")
    actual_slots = atlas_slots([
        unswizzle(decode_imy_texture(buf[m["offset"]:m["offset"]+m["size"]]))
        for m in parsed[1:]])
    different = [i for i in range(len(old_slots)) if old_slots[i] != actual_slots[i]]
    if sorted(different) != sorted(slots.values()):
        raise ValueError("Unexpected raster edits")
    return bytes(buf),different

def build(f1:Path,target:Path,report:Path,*,mode):
    f1,target,report = map(Path,(f1,target,report))
    if len({f1.resolve(),target.resolve(),report.resolve()}) != 3:
        raise ValueError("Protected source/output/report collision")
    if target.exists() or report.exists():
        raise FileExistsError("Only unused output paths accepted")
    if sha256_file(f1) != F1_SHA:
        raise ValueError("Original F1 ISO hash differs")
    _, iso_files = iso9660_entries(f1)
    dat = next(f for f in iso_files if f["path"] == "PSP_GAME/USRDIR/DATA.DAT")
    with f1.open("rb") as handle:
        handle.seek(dat["offset"]); pack = handle.read(dat["size"])
    ps = pspfs_entries(pack)
    if len(ps) != 349:
        raise ValueError("PSPFS count differs")
    font = next(x for x in ps if x["name"] == "FONT.ARC")
    arc = pack[font["offset"]:font["offset"]+font["size_stored"]]
    members = dsarc_entries(arc)
    index_member = members[0]
    fontindex = arc[index_member["offset"]:index_member["offset"]+index_member["size"]]
    codes_new = [u16(fontindex,4+i*4) for i in range(u32(fontindex))]
    codes_old = codes_new[:95]+codes_new[114:]
    selected = get_probe_indices(codes_old,codes_new,mode)
    replacement,changed = rebuild_archive(arc,members,selected)
    previous_size,new_size = font["size_stored"],len(replacement)
    next_offset = min(x["offset"] for x in ps if x["offset"]>font["offset"])
    if font["offset"]+new_size>next_offset:
        raise ValueError("FONT.ARC would overlap next resource")
    if new_size>previous_size and any(pack[font["offset"]+previous_size:font["offset"]+new_size]):
        raise ValueError("Nonzero padding would be overwritten")
    target.parent.mkdir(parents=True,exist_ok=True)
    report.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(f1,target)
    with target.open("r+b") as handle:
        handle.seek(dat["offset"]+font["offset"]);handle.write(replacement)
        if previous_size>new_size:
            handle.write(bytes(previous_size-new_size))
        handle.seek(dat["offset"]+16+font["index"]*32+24)
        handle.write(struct.pack("<I",new_size))
    with target.open("rb") as handle:
        handle.seek(dat["offset"]); altered_pack = handle.read(dat["size"])
    altered = pspfs_entries(altered_pack)
    if len(altered) != 349:
        raise ValueError("Altered PSPFS count differs")
    unchanged = 0
    for old,new in zip(ps,altered):
        if old["name"] == "FONT.ARC":
            continue
        if old != new or (pack[old["offset"]:old["offset"]+old["size_stored"]] !=
                          altered_pack[new["offset"]:new["offset"]+new["size_stored"]]):
            raise ValueError("Unrelated PSPFS asset changed: " + old["name"])
        unchanged+=1
    if iso9660_entries(f1)[1]!=iso9660_entries(target)[1]:
        raise ValueError("ISO9660 changed")
    result={
        "schema":"cladun.f2.private_font_probe.v1",
        "state":"EXPERIMENTAL_PRIVATE_NOT_APPROVED_FOR_RELEASE",
        "mode":mode,"f1_source_sha256":F1_SHA,
        "iso_sha256":sha256_file(target),
        "changed_glyph_slots":selected,"actual_changed_slots":len(changed),
        "font_bin_table_byte_exact":True,
        "unrelated_pspfs_byte_exact":unchanged,
        "pspfs_total":349,"iso9660_inventory_equal":True,
        "iso_length_equal":f1.stat().st_size==target.stat().st_size,
        "font_archive_previous_bytes":previous_size,
        "font_archive_new_bytes":new_size,
        "post_generation_realtime_PPSPP_check":"NOT_PERFORMED_BY_THIS_SCRIPT",
        "warning":"Do not upload experimental ISO or report with commercial bytes.",
    }
    with report.open("x",encoding="utf-8") as f:
        json.dump(result,f,ensure_ascii=False,indent=2);f.write("\n")
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--f1",type=Path,required=True)
    parser.add_argument("--salida",type=Path,required=True)
    parser.add_argument("--informe",type=Path,required=True)
    parser.add_argument("--modo",choices=["old","new"],required=True)
    args=parser.parse_args()
    print(json.dumps(build(args.f1,args.salida,args.informe,mode=args.modo),
                     ensure_ascii=False,indent=2))
