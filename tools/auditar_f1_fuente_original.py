#!/usr/bin/env python3
"""Reauditar SOLO la ISO original USA de Cladun, sin publicar assets.

La comparación de una ISO parcheada requiere el integrador y el BPS guard.
Este script NO acredita que los offsets de una CANDIDATA sean iguales.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

from extract_cladun import (
    iso9660_entries, read_iso_file, pspfs_entries, decompress,
    dsarc_entries, script_table, parse_commands,
)

EXPECTED_ISO = "b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f"
EXPECTED_STRTBL = "16d9da36c05380cbb8af7eba53cb26c7b3e21f8ef5c80fdb90fdba20621044bf"
EXPECTED_FONT = "1f1f5692fecb3b4a66c50f4b20191c1f2658a32ca1220902a5888ae9a11afb46"
TEXT_OPS = {"0x66", "0x69", "0x6E"}


def sha_file(p):
    h = hashlib.sha256()
    with p.open("rb") as inp:
        for chunk in iter(lambda: inp.read(1024*1024), b""):
            h.update(chunk)
    return h.hexdigest()


def require(test, desc):
    if not test:
        raise ValueError(desc)


def audit(source):
    source = Path(source)
    require(source.stat().st_size == 305496064 and sha_file(source) == EXPECTED_ISO,
            "ISO original SHA/tamaño distinto")
    _volume, files = iso9660_entries(source)
    require(len(files) == 16, "ISO9660 inventario distinto")
    records = [x for x in files if x["path"] == "PSP_GAME/USRDIR/DATA.DAT"]
    require(len(records) == 1, "DATA.DAT ausente")
    rec = records[0]
    require((rec["offset"], rec["size"]) == (113770496, 191697408),
            "DATA.DAT offset/tamaño inesperado")
    pack = read_iso_file(source, rec)
    entries = pspfs_entries(pack)
    require(len(entries) == 349 and len({x["name"] for x in entries}) == 349,
            "PSPFS no tiene 349 nombres únicos")
    names = {x["name"]: x for x in entries}
    nested = {}
    for name in ("SCRIPT.SDT", "DATABASE.DAT", "FONT.ARC"):
        entry = names[name]
        stored = pack[entry["offset"]:entry["offset"] + entry["size_stored"]]
        raw, method = decompress(stored, entry["size_expanded"])
        nested[name] = {k["name"]: raw[k["offset"]:k["offset"] + k["size"]]
                        for k in dsarc_entries(raw)}
    strtbl = nested["DATABASE.DAT"]["STRTBL.DAT"]
    font = nested["FONT.ARC"]["FONT.BIN"]
    require(hashlib.sha256(strtbl).hexdigest() == EXPECTED_STRTBL, "STRTBL modificado")
    require(hashlib.sha256(font).hexdigest() == EXPECTED_FONT, "FONT.BIN modificado")
    tab = nested["SCRIPT.SDT"]["SCRIPT.TBL"]
    script = nested["SCRIPT.SDT"]["SCRIPT.DAT"]
    blocks = script_table(tab, "SCRIPT.TBL")
    commands, texts = parse_commands(script, blocks, "SCRIPT.SDT/SCRIPT.DAT")
    nontext = sum(cmd["opcode_hex"] not in TEXT_OPS for cmd in commands)
    require(len(blocks) == 1625 and len(commands) == 51705 and nontext == 46308,
            "Script original diverge de la auditoría histórica")
    require(len(texts) == 5397, "Texto de comandos diverge")
    return {
        "schema":"cladun.f1.original_iso_static_audit.v1",
        "status":"PASS_ORIGINAL_ONLY_NOT_CANDIDATE_NOT_PPSSPP",
        "original_sha256":EXPECTED_ISO,
        "original_bytes":source.stat().st_size,
        "iso9660_records":len(files),
        "pspfs_entries":len(entries),
        "pspfs_unique_names":len(names),
        "dsarc_member_counts":{name:len(values) for name,values in nested.items()},
        "strtbl_sha256":EXPECTED_STRTBL,
        "font_bin_sha256":EXPECTED_FONT,
        "script_starts":len(blocks),
        "script_commands":len(commands),
        "script_nontext_commands":nontext,
        "script_text_commands":len(texts),
        "candidate_compared":False,
        "roundtrip_bps_executed":False,
        "ppsspp_verified":False
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--iso", type=Path, required=True)
    ap.add_argument("--reporte", type=Path, required=True)
    args = ap.parse_args()
    if args.reporte.exists():
        raise FileExistsError("No sobrescribir informe")
    result = audit(args.iso)
    args.reporte.parent.mkdir(parents=True, exist_ok=True)
    with args.reporte.open("x",encoding="utf-8") as f:
        json.dump(result,f,ensure_ascii=False,indent=2);f.write("\n")
    print(json.dumps(result,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
