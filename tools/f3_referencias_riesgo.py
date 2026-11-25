#!/usr/bin/env python3
"""F3: coincidencias numéricas de SCRIPT.DAT original, NO saltos probados.

SOLO LECTURA. No mueve ni modifica eventos. No emite bytes o textos comerciales.
Los campos u32 se inspeccionan con ventanas deslizantes, sin inferir semántica.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct

try:
    from tools.extract_cladun import iso9660_entries, read_iso_file, pspfs_entries, decompress, dsarc_entries
    from tools.script_event_guard import read_commands
except ModuleNotFoundError:
    from extract_cladun import iso9660_entries, read_iso_file, pspfs_entries, decompress, dsarc_entries
    from script_event_guard import read_commands

USA_SIZE = 305496064
USA_SHA = "b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f"
SCRIPT_SHA = "c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358"
TABLE_SHA = "f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37"
N_SCRIPT_BLOCKS = 1625
N_COMMANDS = 51705
N_NONTEXT = 46308


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(4 * 1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def numeric_candidates(commands, starts, ids, intro_blocks=frozenset()):
    """Los 'candidatos' son coincidencias de enteros, nunca referencias validadas."""
    offset_to_block = {c.offset: c.block for c in commands}
    offsets = set(offset_to_block)
    starts_set = set(starts[:-1]) - {0}
    ids_set = set(ids) - {0}
    counts = Counter()
    intro_counts = Counter()
    signatures = Counter()
    for cmd in commands:
        if cmd.content is not None:
            continue
        payload = cmd.raw[5:]
        base, end = starts[cmd.block:cmd.block + 2]
        for pos in range(max(0, len(payload) - 3)):
            value = struct.unpack_from("<I", payload, pos)[0]
            if value == 0:
                continue
            categories = []
            if value in offsets:
                categories.append("coincide_offset_absoluto_comando")
                if offset_to_block[value] != cmd.block:
                    categories.append("coincide_offset_absoluto_otro_bloque")
            if value in starts_set:
                categories.append("coincide_inicio_script")
            if value in ids_set:
                categories.append("coincide_id_script")
            if value < end - base and base + value in offsets:
                categories.append("coincide_offset_relativo_bloque")
            for category in categories:
                counts[category] += 1
                signatures[(category, f"0x{cmd.code:02x}", pos)] += 1
                if cmd.block in intro_blocks:
                    intro_counts[category] += 1
    return {
        "candidate_counts_zero_excluded": dict(sorted(counts.items())),
        "intro_candidate_counts_zero_excluded": dict(sorted(intro_counts.items())),
        "top_20_candidate_opcode_and_payload_offset": [
            {"candidate": category, "opcode": opcode, "payload_byte_offset": pos, "occurrences": count}
            for (category, opcode, pos), count in signatures.most_common(20)
        ],
        "interpretation": "COINCIDENCIAS NUMERICAS NO PRUEBAN SALTOS NI SEGURIDAD DE REUBICACION",
        "relocation_authorized": False,
        "mips_control_flow_proven": False,
    }


def original_script_children(iso: Path):
    if iso.is_symlink() or not iso.is_file() or iso.stat().st_size != USA_SIZE or file_sha256(iso) != USA_SHA:
        raise ValueError("La ISO no es la USA ORIGINAL autenticada")
    _, entries = iso9660_entries(iso)
    dat = next((r for r in entries if r["path"] == "PSP_GAME/USRDIR/DATA.DAT" and not r["directory"]), None)
    if dat is None:
        raise ValueError("DATA.DAT ausente")
    container = read_iso_file(iso, dat)
    members = pspfs_entries(container)
    if len(members) != 349 or members[231]["name"] != "SCRIPT.SDT":
        raise ValueError("PSPFS original inesperado")
    record = members[231]
    payload = container[record["offset"]:record["offset"] + record["size_stored"]]
    archive, _kind = decompress(payload, record["size_expanded"])
    children = {r["name"]: archive[r["offset"]:r["offset"] + r["size"]] for r in dsarc_entries(archive)}
    if set(children) != {"AISCRIPT.DAT", "AISCRIPT.TBL", "SCRIPT.DAT", "SCRIPT.TBL"}:
        raise ValueError("DSARC original inesperado")
    if hashlib.sha256(children["SCRIPT.DAT"]).hexdigest() != SCRIPT_SHA:
        raise ValueError("SCRIPT.DAT SHA inesperado")
    if hashlib.sha256(children["SCRIPT.TBL"]).hexdigest() != TABLE_SHA:
        raise ValueError("SCRIPT.TBL SHA inesperado")
    return children["SCRIPT.DAT"], children["SCRIPT.TBL"]


def audit(iso: Path):
    data, table = original_script_children(Path(iso))
    commands, starts = read_commands(data, table)
    if len(commands) != N_COMMANDS or sum(c.content is None for c in commands) != N_NONTEXT:
        raise ValueError("Recuento de comandos distinto de fuente original")
    if len(starts) != N_SCRIPT_BLOCKS + 1 or len(table) != 16 + 32 * N_SCRIPT_BLOCKS:
        raise ValueError("Metadatos SCRIPT.TBL inesperados")
    ids = [struct.unpack_from("<I", table, 16 + i * 32)[0] for i in range(N_SCRIPT_BLOCKS)]
    names = [
        table[16 + i * 32 + 8:16 + i * 32 + 32].split(b"\x00", 1)[0].decode("ascii", "strict")
        for i in range(N_SCRIPT_BLOCKS)
    ]
    intro = {i for i, name in enumerate(names) if name in ("demo1001_00.dsf", "demo1001_01.dsf")}
    if len(intro) != 7 or sum(c.block in intro for c in commands) != 878:
        raise ValueError("Bloques demo1001 inesperados")
    return {
        "schema": "cladun.f3.script_numeric_candidates.v1",
        "evidence": "A_ORIGINAL_ISO_NOT_SEMANTIC_MIPS_NOT_PPSSPP",
        "iso_sha256": USA_SHA,
        "script_dat_sha256": SCRIPT_SHA,
        "script_tbl_sha256": TABLE_SHA,
        "script_blocks": N_SCRIPT_BLOCKS,
        "commands": N_COMMANDS,
        "nontext_commands": N_NONTEXT,
        "intro_demo1001_blocks": 7,
        "intro_demo1001_commands": 878,
        **numeric_candidates(commands, starts, ids, intro),
        "original_iso_modified": False,
        "ppsspp_run": False,
        "preserve_event_safe_only": True,
    }


def report_path(raw: Path):
    if not raw.is_absolute() or raw.is_symlink() or raw.suffix.lower() != ".json":
        raise ValueError("Se requiere JSON privado NUEVO con ruta absoluta")
    target = raw.resolve(strict=False)
    repo = Path(__file__).resolve().parents[1]
    if (target.exists() or repo == target or repo in target.parents
            or any((p / ".git").exists() for p in target.parents)):
        raise ValueError("No escribir en un repositorio Git o sobre archivo existente")
    return target


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--iso-original", required=True, type=Path)
    ap.add_argument("--reporte-privado", required=True, type=Path)
    args = ap.parse_args()
    target = report_path(args.reporte_privado)
    result = audit(args.iso_original)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(json.dumps({"original_iso_verified": True, "commands": N_COMMANDS, "relocation_authorized": False}))


if __name__ == "__main__":
    main()
