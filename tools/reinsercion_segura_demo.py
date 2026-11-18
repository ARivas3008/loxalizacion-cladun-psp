#!/usr/bin/env python3
"""Ensayo aislado de reinserción para Cladun PSP USA.

NO crea un parche español ni publica una ISO. Solo cambia 2 campos conocidos
en una ISO TEMPORAL, prueba aislamiento binario y elimina esa copia.
Solo garantiza esta prueba, no un arranque correcto en PSP/PPSSPP.
"""
from __future__ import annotations
import argparse
import csv
import gzip
import hashlib
import json
import shutil
import struct
import tempfile
from pathlib import Path
from extract_cladun import (
    iso9660_entries, read_iso_file, pspfs_entries, decompress, dsarc_entries
)

ISO_SHA = "b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f"
def sha(x):
    return hashlib.sha256(x).hexdigest()

def edit_member(parent, member_name, relative_offset, old, new, capacity, exact):
    child = next(x for x in dsarc_entries(parent) if x["name"] == member_name)
    old_bytes = old.encode("cp932", "strict")
    new_bytes = new.encode("cp932", "strict")
    if "\0" in new:
        raise ValueError("NUL incrustado")
    if exact and len(old_bytes) != len(new_bytes):
        raise ValueError("Se rechaza cambiar el tamaño de un comando de script")
    if not exact and len(new_bytes) + 1 > capacity:
        raise ValueError("Se rechaza desbordar el campo de base de datos")
    pos = child["offset"] + relative_offset
    if parent[pos:pos+len(old_bytes)] != old_bytes:
        raise ValueError("Offset o cadena original incompatible")
    modified = bytearray(parent)
    if exact:
        if parent[pos+len(old_bytes)] != 0:
            raise ValueError("Sin terminador de script esperado")
        modified[pos:pos+len(new_bytes)] = new_bytes
    else:
        modified[pos:pos+capacity] = new_bytes + b"\0" * (capacity-len(new_bytes))
    siblings = 0
    for entry in dsarc_entries(parent):
        if entry["name"] == member_name:
            continue
        a, b = entry["offset"], entry["offset"] + entry["size"]
        if parent[a:b] != modified[a:b]:
            raise ValueError("Se alteró un miembro DSARC no autorizado")
        siblings += 1
    return bytes(modified), siblings

def compact(raw, limit):
    # Otros recursos PSPFS de la misma ISO utilizan cabecera GZIP de 12 bytes.
    # El cargador EN EL JUEGO aun no se ha probado para estas dos entradas.
    compressed = struct.pack("<III", 1, 131072, 12) + gzip.compress(raw, compresslevel=9, mtime=0)
    if len(compressed) > limit:
        raise ValueError("Recomprimido no cabe; desplazamiento no autorizado")
    assert gzip.decompress(compressed[12:]) == raw
    return compressed

def audit(iso, corpus):
    if sha(iso.read_bytes()) != ISO_SHA:
        raise ValueError("ISO no reconocida: SHA-256 distinto")
    with corpus.open(encoding="utf-8-sig", newline="") as f:
        rows = {r["grupo_id"]: r for r in csv.DictReader(f)}
    _, files = iso9660_entries(iso)
    data_rec = next(x for x in files if x["path"] == "PSP_GAME/USRDIR/DATA.DAT")
    offset_iso = data_rec["offset"]
    pkg = read_iso_file(iso, data_rec)
    index = pspfs_entries(pkg)
    byname = {r["name"]: r for r in index}
    changes, details = {}, []
    for parent_name, member, group, replacement, exact in [
        ("SCRIPT.SDT", "SCRIPT.DAT", "000001", "Es esta la taberna?", True),
        ("DATABASE.DAT", "ARTIFACT.DAT", "005897", "Mini Manzana", False),
    ]:
        entry = byname[parent_name]
        stored = pkg[entry["offset"]:entry["offset"] + entry["size_stored"]]
        unpacked, codec = decompress(stored, entry["size_expanded"])
        row = rows[group]
        altered, sibling_count = edit_member(
            unpacked, member, int(row["offset_hex"],16),
            row["original"], replacement, int(row["capacidad_campo"] or 0), exact
        )
        changes[parent_name] = compact(altered, entry["size_stored"])
        details.append({
            "recurso": parent_name, "miembro": member, "grupo": group,
            "bytes_originales": len(row["original"].encode("cp932")),
            "bytes_nuevos": len(replacement.encode("cp932")),
            "otros_miembros_inalterados": sibling_count,
            "comprimido_antes": entry["size_stored"],
            "comprimido_despues": len(changes[parent_name]),
        })
    candidate = bytearray(pkg)
    permitted = []
    for name, packed in changes.items():
        e = byname[name]
        slot = e["offset"]
        table_length = 16 + e["index"] * 32 + 24
        candidate[slot:slot+len(packed)] = packed
        struct.pack_into("<I", candidate, table_length, len(packed))
        permitted.extend(((slot, slot+len(packed)), (table_length, table_length+4)))
    if len(candidate) != len(pkg):
        raise ValueError("Tamaño de DATA.DAT alterado")
    rebuilt = pspfs_entries(candidate)
    others = 0
    for before, after in zip(index, rebuilt):
        for attr in ("name", "offset", "size_expanded"):
            if before[attr] != after[attr]:
                raise ValueError(f"Se desplazó {attr} de {before['name']}")
        if before["name"] not in changes:
            a, b = before["offset"], before["offset"] + before["size_stored"]
            if before["size_stored"] != after["size_stored"] or pkg[a:b] != candidate[a:b]:
                raise ValueError(f"Recurso no autorizado: {before['name']}")
            others += 1
        else:
            stored = candidate[after["offset"]:after["offset"] + after["size_stored"]]
            decompress(stored, after["size_expanded"])
    if byname["FONT.ARC"]["name"] not in ("FONT.ARC",):
        raise AssertionError("Fuente no encontrada")
    # No basta con conservar offsets: se comparan TODOS los bytes de DATA.DAT.
    touched = 0
    for i, (a,b) in enumerate(zip(pkg, candidate)):
        if a != b:
            touched += 1
            if not any(lo <= i < hi for lo,hi in permitted):
                raise ValueError(f"Se modificó el byte prohibido {i}")
    with tempfile.TemporaryDirectory(prefix="cladun_seguro_") as folder:
        tmp = Path(folder)/"private_test.iso"
        shutil.copyfile(iso, tmp)
        with tmp.open("r+b") as f:
            f.seek(offset_iso)
            f.write(candidate)
        if tmp.stat().st_size != iso.stat().st_size:
            raise ValueError("El tamaño de la ISO cambió")
        checked_other_iso = 0
        with iso.open("rb") as fa, tmp.open("rb") as fb:
            for ent in files:
                if ent["directory"] or ent["path"] == "PSP_GAME/USRDIR/DATA.DAT":
                    continue
                fa.seek(ent["offset"])
                fb.seek(ent["offset"])
                if fa.read(ent["size"]) != fb.read(ent["size"]):
                    raise ValueError("Se modificó otro archivo ISO")
                checked_other_iso += 1
        # La copia temporal desaparece sin incluir material comercial.
    return {
        "resultado": "PASS: solo aislamiento binario para 2 cambios de prueba",
        "iso_size_same": True, "offsets_same": True,
        "pspfs_total":len(index), "pspfs_untouched":others,
        "unrelated_iso_files_identical":checked_other_iso,
        "modified_bytes_in_permitted_ranges":touched,
        "font_archive_identical": True, "tiles_sprites_portraits_untouched": True,
        "details":details, "runtime_ppsspp_verified":False,
        "spanish_font_ready":False, "full_corpus_reinsertion_ready":False
    }

if __name__ == "__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--iso",type=Path,required=True)
    ap.add_argument("--corpus",type=Path,default=Path(__file__).resolve().parent.parent/"corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv")
    ap.add_argument("--salida",type=Path)
    args=ap.parse_args()
    result=audit(args.iso,args.corpus)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if args.salida:
        args.salida.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
