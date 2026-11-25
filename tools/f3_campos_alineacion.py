#!/usr/bin/env python3
"""F3-R4: auditor de campos u32 hipotéticos en SCRIPT.DAT autenticado.

El escáner anterior usaba ventanas de un byte y contaba coincidencias como
candidatos. Aquí se confronta ese efecto con layouts *hipotéticos* por opcode,
SIN afirmar que los campos sean saltos, identificadores o punteros.
No modifica ISO, texturas, comandos ni traducciones. Emite solo metadatos.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import struct

try:
    from tools import f3_referencias_riesgo as base
    from tools.extract_cladun import iso9660_entries, read_iso_file
    from tools.script_event_guard import read_commands
except ModuleNotFoundError:
    import f3_referencias_riesgo as base
    from extract_cladun import iso9660_entries, read_iso_file
    from script_event_guard import read_commands

# Estructuras hipotéticas deducidas de longitudes de argumentos consistentes.
# NO constituyen documentación del motor ni semántica de opcodes confirmada.
LAYOUTS = {
    0x01: (4, (0,)),
    0x02: (18, (2, 6, 10, 14)),
    0x07: (5, (1,)),
    0x0A: (4, (0,)),
    0xFB: (8, (0, 4)),
    0xFC: (8, (0, 4)),
}
EXPECTED_OP02_COUNT = 2039
EXPECTED_OP02_FALSE_WINDOW_5 = 1439
EXPECTED_OP02_ALIAS_VALUE = 8192
EXPECTED_ISO_BOOT = 2158521
EXPECTED_ISO_EBOOT = 2158864
EXPECTED_BOOT_SHA = "d2240653adc6119df174c4a3cb8451381934f6898ef2bff8d6ffe00763aebdf2"
EXPECTED_EBOOT_SHA = "06e39573dfc9ed18122d9b0c6c69546265b1e3f0e5806b8eb9603fcc09f2ab57"


def cmd_payload(cmd):
    if cmd.content is not None:
        return None
    return cmd.raw[5:]


def classify_executables(boot: bytes, eboot: bytes, *, require_original=False) -> dict:
    """No descifra PSP ni afirma inexistencia de código en RAM."""
    if require_original:
        if (len(boot) != EXPECTED_ISO_BOOT or len(eboot) != EXPECTED_ISO_EBOOT or
            hashlib.sha256(boot).hexdigest() != EXPECTED_BOOT_SHA or
            hashlib.sha256(eboot).hexdigest() != EXPECTED_EBOOT_SHA):
            raise ValueError("BOOT/EBOOT no coinciden con la ISO USA autenticada")
    return {
        "boot_size": len(boot),
        "boot_sha256": hashlib.sha256(boot).hexdigest(),
        "boot_all_zero": not any(boot),
        "eboot_size": len(eboot),
        "eboot_sha256": hashlib.sha256(eboot).hexdigest(),
        "eboot_magic": "PSP_ENCRYPTED_HEADER" if eboot.startswith(b"~PSP") else (
            "ELF" if eboot.startswith(b"\x7fELF") else "OTHER"),
        "mips_elf_plaintext_in_these_iso_members": bool(eboot.startswith(b"\x7fELF") or boot.startswith(b"\x7fELF")),
        "mips_interpreter_disassembled": False,
    }


def read_executables(iso: Path) -> dict:
    """Reutiliza tabla ISO9660 del extractor público; no exporta ejecutables."""
    _, entries = iso9660_entries(iso)
    by_path = {r["path"]: r for r in entries if not r["directory"]}
    names = ("PSP_GAME/SYSDIR/BOOT.BIN", "PSP_GAME/SYSDIR/EBOOT.BIN")
    if any(name not in by_path for name in names):
        raise ValueError("Faltan ejecutables PSP originales")
    return classify_executables(*(read_iso_file(iso, by_path[name]) for name in names), require_original=True)


def profile_hypothesized_fields(commands, starts, ids, intro_blocks=frozenset()) -> dict:
    """Cuenta coincidencias en posiciones seleccionadas, nunca saltos reales."""
    offset_to_block = {c.offset: c.block for c in commands}
    if len(offset_to_block) != len(commands):
        raise ValueError("Offsets de comandos duplicados")
    absolute = set(offset_to_block)
    block_starts = set(starts[:-1]) - {0}
    ids_set = set(ids) - {0}
    profiles = {}
    totals = Counter()
    intro_totals = Counter()
    scanned_commands = Counter()
    op02_legacy_false_windows = Counter()
    op02_alias_invariant = True
    for cmd in commands:
        payload = cmd_payload(cmd)
        if payload is None or cmd.code not in LAYOUTS:
            continue
        size, locations = LAYOUTS[cmd.code]
        if len(payload) != size:
            raise ValueError(f"Opcode 0x{cmd.code:02x}: longitud inesperada")
        opcode = f"0x{cmd.code:02x}"
        scanned_commands[opcode] += 1
        start, limit = starts[cmd.block:cmd.block + 2]
        if cmd.code == 2:
            # En este corpus: los primeros dos enteros caben en 8 bits y
            # la lectura desfasada en +5 equivale a leer el segundo << 8.
            val5 = struct.unpack_from("<I", payload, 5)[0]
            field6 = struct.unpack_from("<I", payload, 6)[0]
            op02_alias_invariant &= val5 == (field6 << 8) and field6 <= 255
            if val5 in absolute:
                op02_legacy_false_windows[val5] += 1
        for location in locations:
            value = struct.unpack_from("<I", payload, location)[0]
            key = (opcode, location)
            p = profiles.setdefault(key, {
                "occurrences": 0,
                "nonzero": 0,
                "value_frequency": Counter(),
                "matches": defaultdict(Counter),
                "intro_matches": Counter(),
            })
            p["occurrences"] += 1
            p["value_frequency"][value] += 1
            if not value:
                continue
            p["nonzero"] += 1
            labels = []
            if value in absolute:
                labels.append("absolute_command_offset")
                if offset_to_block[value] != cmd.block:
                    labels.append("absolute_other_block")
            if value in block_starts:
                labels.append("script_start")
            if value in ids_set:
                labels.append("script_id")
            if value < limit - start and value + start in absolute:
                labels.append("relative_command_offset")
            for label in labels:
                totals[label] += 1
                p["matches"][label][value] += 1
                if cmd.block in intro_blocks:
                    intro_totals[label] += 1
                    p["intro_matches"][label] += 1
    field_rows = []
    for (opcode, pos), p in sorted(profiles.items()):
        match_profiles = {
            label: {
                "occurrences": sum(freq.values()),
                "distinct_numeric_values": len(freq),
                "largest_single_value_repetition": max(freq.values(), default=0),
            }
            for label, freq in sorted(p["matches"].items())
        }
        field_rows.append({
            "opcode": opcode, "hypothesized_u32_byte_offset": pos,
            "occurrences": p["occurrences"], "nonzero": p["nonzero"],
            "distinct_numeric_values_including_zero": len(p["value_frequency"]),
            "largest_single_value_repetition": max(p["value_frequency"].values(), default=0),
            "numeric_matches_not_proven_references": match_profiles,
            "intro_numeric_matches": dict(sorted(p["intro_matches"].items())),
        })
    return {
        "layout_hypotheses_not_confirmed_by_mips": {
            f"0x{op:02x}": {"payload_bytes": length, "u32_offsets": list(offsets)}
            for op, (length, offsets) in sorted(LAYOUTS.items())
        },
        "scanned_nontext_commands_by_opcode": dict(sorted(scanned_commands.items())),
        "field_profiles": field_rows,
        "totals_selected_fields_only": dict(sorted(totals.items())),
        "intro_totals_selected_fields_only": dict(sorted(intro_totals.items())),
        "legacy_opcode_02_unaligned_u32_byte5": {
            "occurrences_matching_an_absolute_command_offset": sum(op02_legacy_false_windows.values()),
            "distinct_numeric_values": len(op02_legacy_false_windows),
            "largest_single_value_repetition": max(op02_legacy_false_windows.values(), default=0),
            "all_opcode02_byte5_equals_field6_times_256": op02_alias_invariant,
            "byte5_is_a_hypothesized_field_start": False,
        },
        "untested_opcodes_not_cleared": True,
        "mips_semantics_proven": False,
        "script_relocation_authorized": False,
    }


def audit(iso: Path) -> dict:
    iso = Path(iso)
    # La extracción conserva el requisito fail-closed de SHA de ISO y DSARC.
    script, table = base.original_script_children(iso)
    commands, starts = read_commands(script, table)
    if len(commands) != base.N_COMMANDS or sum(c.content is None for c in commands) != base.N_NONTEXT:
        raise ValueError("Los conteos originales SCRIPT.DAT no coinciden")
    if len(starts) != base.N_SCRIPT_BLOCKS + 1:
        raise ValueError("Bloques SCRIPT.TBL no coinciden")
    ids = [struct.unpack_from("<I", table, 16 + 32 * i)[0] for i in range(base.N_SCRIPT_BLOCKS)]
    names = [table[16 + i * 32 + 8:16 + i * 32 + 32].split(b"\x00", 1)[0].decode("ascii")
             for i in range(base.N_SCRIPT_BLOCKS)]
    intro = {i for i, name in enumerate(names) if name in {"demo1001_00.dsf", "demo1001_01.dsf"}}
    if len(intro) != 7 or sum(c.block in intro for c in commands) != 878:
        raise ValueError("Bloques demo1001 no coinciden")
    profiles = profile_hypothesized_fields(commands, starts, ids, intro)
    fp = profiles["legacy_opcode_02_unaligned_u32_byte5"]
    if (profiles["scanned_nontext_commands_by_opcode"].get("0x02") != EXPECTED_OP02_COUNT or
        fp["occurrences_matching_an_absolute_command_offset"] != EXPECTED_OP02_FALSE_WINDOW_5 or
        fp["distinct_numeric_values"] != 1 or
        fp["largest_single_value_repetition"] != EXPECTED_OP02_FALSE_WINDOW_5 or
        not fp["all_opcode02_byte5_equals_field6_times_256"]):
        raise ValueError("La anomalía original de 0x02 no se reproduce")
    return {
        "schema": "cladun.f3.event_field_hypotheses.v1",
        "evidence": "A_ORIGINAL_AUTHENTIC_STATIC_AND_B_SYNTHETIC_NOT_C_PPSSPP",
        "original_iso_sha256": base.USA_SHA,
        "script_dat_sha256": base.SCRIPT_SHA,
        "script_tbl_sha256": base.TABLE_SHA,
        "command_count": len(commands),
        "nontext_command_count": base.N_NONTEXT,
        "intro_blocks": len(intro),
        "intro_commands": 878,
        "psp_executable_iso_members": read_executables(iso),
        **profiles,
        "translations_changed": False,
        "game_binary_modified": False,
        "new_ppsspp_runtime": False,
        "variable_length_intro_85_blocked": True,
        "variable_length_all_4524_blocked": True,
        "event_safe_only_preserved": True,
        "conclusion": "1439 lecturas u32 0x02 en offset +5 son repetición de un valor desfasado, no 1439 destinos; ninguna semántica MIPS comprobada.",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--iso-original", type=Path, required=True)
    ap.add_argument("--reporte-privado", type=Path, required=True)
    args = ap.parse_args()
    target = base.report_path(args.reporte_privado)
    result = audit(args.iso_original)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("x", encoding="utf-8") as stream:
        json.dump(result, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    print(json.dumps({"original_sha_verified": True, "legacy_false_windows": EXPECTED_OP02_FALSE_WINDOW_5,
                      "mips_semantics_proven": False, "relocation_authorized": False}))


if __name__ == "__main__":
    main()
