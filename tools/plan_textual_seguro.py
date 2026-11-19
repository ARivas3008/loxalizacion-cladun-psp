#!/usr/bin/env python3
"""Genera un plan de edición textual de Cladun enlazado a bytes reales.

No modifica la ISO. Los planes no implican aprobación visual ni runtime.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from auditar_preinsercion_es import SOURCE, DRAFT, IMMUTABLE, read_csv, check_row
from charset_es import encode_spanish
from extract_cladun import iso9660_entries, read_iso_file, pspfs_entries, dsarc_entries, decompress

PATH = "SCRIPT.SDT/SCRIPT.DAT"
SOURCE_SHA256 = "b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f"


def require(ok, why):
    if not ok:
        raise ValueError(why)


def sha256_file(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_script_bytes(iso):
    _, file_table = iso9660_entries(Path(iso))
    dat = next((e for e in file_table if e["path"] == "PSP_GAME/USRDIR/DATA.DAT"), None)
    require(dat is not None, "DATA.DAT ausente")
    package = read_iso_file(Path(iso), dat)
    files = pspfs_entries(package)
    require(len(files) == 349, "PSPFS distinto del juego auditado")
    parent = next((e for e in files if e["name"] == "SCRIPT.SDT"), None)
    require(parent is not None, "SCRIPT.SDT ausente")
    start, end = parent["offset"], parent["offset"] + parent["size_stored"]
    decoded, _ = decompress(package[start:end], parent["size_expanded"])
    child = next((e for e in dsarc_entries(decoded) if e["name"] == "SCRIPT.DAT"), None)
    require(child is not None, "SCRIPT.DAT ausente")
    lo, hi = child["offset"], child["offset"] + child["size"]
    require(0 <= lo < hi <= len(decoded), "Miembro fuera de límites")
    return decoded[lo:hi]


def build_entries(originals, translated, group_ids, script):
    require(len(originals) == len(translated), "Distinto número de grupos")
    require(group_ids and len(set(group_ids)) == len(group_ids), "Grupos vacíos o repetidos")
    by_id = {}
    for source, draft in zip(originals, translated):
        gid = source["grupo_id"]
        require(gid == draft["grupo_id"] and gid not in by_id, "IDs alterados o duplicados")
        require(all(source.get(k, "") == draft.get(k, "") for k in IMMUTABLE),
                f"Fuente o metadatos alterados: {gid}")
        by_id[gid] = source, draft
    edits = []
    for gid in group_ids:
        require(gid in by_id, f"Grupo desconocido: {gid}")
        source, draft = by_id[gid]
        require(source["origen"] == PATH, f"Origen no autorizado: {gid}")
        state = check_row(source, draft)["estado"]
        require(state == "CANDIDATO_A_ENSAYO_NO_VALIDADO", f"{gid} bloqueado: {state}")
        offset = int(source["offset_hex"], 16)
        original = bytes.fromhex(source["bytes_hex"])
        replacement = encode_spanish(draft["espanol"])
        require(original != replacement and len(original) == len(replacement) > 0,
                f"{gid}: la longitud debe ser idéntica y la edición no vacía")
        require(0 <= offset and offset + len(original) <= len(script),
                f"{gid}: offset fuera de SCRIPT.DAT")
        require(script[offset:offset + len(original)] == original,
                f"{gid}: bytes fuente distintos de los de SCRIPT.DAT")
        edits.append({
            "grupo_id": gid, "path": PATH, "offset": offset, "length": len(original),
            "original_hex": original.hex().upper(),
            "replacement_hex": replacement.hex().upper()
        })
    edits.sort(key=lambda e: e["offset"])
    for left, right in zip(edits, edits[1:]):
        require(left["offset"] + left["length"] <= right["offset"],
                "Hay spans solapados")
    return edits


def make_plan(iso, ids, source_csv=SOURCE, draft_csv=DRAFT,
              sha256_expected=SOURCE_SHA256):
    actual = sha256_file(iso)
    require(actual == sha256_expected, "SHA-256 de la ISO no coincide")
    script = source_script_bytes(iso)
    edits = build_entries(read_csv(Path(source_csv)), read_csv(Path(draft_csv)), ids, script)
    return {
        "status": "PLAN_ORIGEN_VERIFICADO_NO_RUNTIME",
        "source_iso_sha256": actual,
        "script_sha256": hashlib.sha256(script).hexdigest(),
        "edits": edits,
        "approved_for_final_insertion": False,
        "ppsspp_verified": False
    }


def verify_manifest(manifest_path, iso, source_csv=SOURCE, draft_csv=DRAFT):
    """Recalcula todo: un manifiesto editable no se trata como autoridad."""
    with Path(manifest_path).open("r", encoding="utf-8") as stream:
        supplied = json.load(stream)
    require(isinstance(supplied, dict) and isinstance(supplied.get("edits"), list),
            "Manifiesto malformado")
    require(all(isinstance(e, dict) for e in supplied["edits"]),
            "Lista de cambios inválida")
    ids = [e.get("grupo_id") for e in supplied["edits"]]
    require(supplied.get("source_iso_sha256") == sha256_file(iso),
            "Manifiesto construido para otra ISO")
    regenerated = make_plan(iso, ids, source_csv, draft_csv,
                            sha256_expected=supplied["source_iso_sha256"])
    require(supplied == regenerated, "Manifiesto distinto del corpus, traducción o ISO actual")
    spans = {PATH: [(e["offset"], e["offset"] + e["length"]) for e in regenerated["edits"]]}
    return spans, regenerated["edits"], regenerated["source_iso_sha256"]


def assert_exact_member_replacements(original, candidate, edits):
    """Comprueba todos los bytes de un miembro, incluidos los no autorizados."""
    require(len(original) == len(candidate), "El miembro cambió de tamaño")
    expected = bytearray(original)
    for e in edits:
        pos = e["offset"]
        old = bytes.fromhex(e["original_hex"])
        new = bytes.fromhex(e["replacement_hex"])
        require(len(old) == len(new) == e["length"], "Bytes fuera del tamaño declarado")
        require(expected[pos:pos + len(old)] == old, "Bytes fuente no coinciden")
        expected[pos:pos + len(old)] = new
    require(bytes(expected) == candidate, "Cambios no declarados dentro o fuera de los spans")
    return True


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--iso", type=Path, required=True, help="ISO privada; solo lectura")
    p.add_argument("--grupo", action="append", required=True, help="Identificador 000001, etc.")
    p.add_argument("--sha256-iso", default=SOURCE_SHA256)
    p.add_argument("--original", type=Path, default=SOURCE)
    p.add_argument("--borrador", type=Path, default=DRAFT)
    p.add_argument("--salida", type=Path, required=True, help="Salida JSON no comercial")
    args = p.parse_args()
    result = make_plan(args.iso, args.grupo, args.original, args.borrador, args.sha256_iso)
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
    print(f"PLAN: {len(result['edits'])} campos iguales en bytes; 0 aprobados para juego")


if __name__ == "__main__":
    main()
