#!/usr/bin/env python3
"""Reinserción PSP append-only estricta: NO desplaza sprites, retratos ni tiles.

Solo ISO propia. El modo completo falla si algún texto no tiene una ruta de
integración demostrable. --experimental-parcial permite pruebas privadas
con los textos estructurados admitidos y genera informe de pendientes.
NO demuestra que el motor acepte las ampliaciones ni el render de los glifos.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
import os
from pathlib import Path
import shutil
import struct
import tempfile

from auditar_preinsercion_es import SOURCE, DRAFT, IMMUTABLE, check_row, read_csv
from menu_layout_es import patch_canonical_menu_layout, patch_canonical_menu_values
from charset_es import encode_spanish, decode_spanish
from extract_cladun import iso9660_entries, read_iso_file, pspfs_entries, dsarc_entries, decompress
from font_es_patch import SOURCE_SHA256, sha256_file
from font_es_narrow import build as build_font, verify as verify_font
from imy_repack_safe import recompress
from script_event_guard import audit_script_rebuild
from ajustes_campos_es import effective
from graficos_texto_es import GRAPHICS, patch_png

ROOT = Path(__file__).resolve().parents[1]
TEXT_OPS = {0x66, 0x69, 0x6E}
TARGET_SCRIPT = "SCRIPT.SDT/SCRIPT.DAT"
TARGET_DB = "DATABASE.DAT"
TARGET_CREDITS = "STAFFROLL.TXT"
TARGET_SYS = "SYS.DAT2"


def require(ok, why):
    if not ok:
        raise ValueError(why)


def u16(raw, off=0):
    return struct.unpack_from("<H", raw, off)[0]


def u32(raw, off=0):
    return struct.unpack_from("<I", raw, off)[0]


def align(value, size):
    return (value + size - 1) // size * size


def strict_next(value, size):
    """Original SCRIPT.DAT has one complete padding block at aligned boundaries."""
    return value + size - value % size


def source_rows(source_csv=SOURCE, draft_csv=DRAFT):
    source = read_csv(source_csv)
    draft = read_csv(draft_csv)
    require(len(source) == len(draft) == 9237, "Corpus incompleto o reordenado")
    seen = set()
    for a, b in zip(source, draft):
        key = a["grupo_id"]
        require(key == b["grupo_id"] and key not in seen, "Orden o identidad cambiados")
        seen.add(key)
        require(all(a.get(k, "") == b.get(k, "") for k in IMMUTABLE),
                f"Fuente alterada: {key}")
    return list(zip(source, draft))


def plan_rows(rows):
    """Clasifica en vez de truncar. No hace sustituciones automáticas para 'hacer caber'."""
    changes, blocked, unchanged = defaultdict(list), [], 0
    for src, dest in rows:
        gid = src["grupo_id"]
        original = src["original"]
        spanish, adaptation = effective(src, dest)
        source_is_incomplete = adaptation == "original_truncado_verificado_por_bytes"
        if not spanish:
            blocked.append({"grupo_id": gid, "motivo": "SIN_TRADUCCION"})
            continue
        if not source_is_incomplete and (src["estado"] == "requiere_reconstruccion" or "\ufffd" in original):
            blocked.append({"grupo_id": gid, "motivo": "FUENTE_INCOMPLETA"})
            continue
        state = ({"estado": "CANDIDATO_A_ENSAYO_NO_VALIDADO"}
                 if source_is_incomplete
                 else check_row(src, {**dest, "espanol": spanish}))
        where = src["origen"]
        if state["estado"] in ("BLOQUEADO_MARCADOR", "BLOQUEADO_CODIFICACION",
                                "BLOQUEADO_BYTES_ORIGINALES", "BLOQUEADO_FUENTE_MODIFICADA"):
            blocked.append({"grupo_id": gid, "motivo": state["estado"]})
            continue
        try:
            old = bytes.fromhex(src["bytes_hex"])
            new = encode_spanish(spanish)
            require(decode_spanish(new) == spanish, "Codificación no reversible")
        except (ValueError, UnicodeError) as exc:
            blocked.append({"grupo_id": gid, "motivo": "CODIFICACION", "detalle": str(exc)})
            continue
        if old == new:
            unchanged += 1
            continue
        if where == TARGET_SCRIPT:
            if state["estado"] not in ("CANDIDATO_A_ENSAYO_NO_VALIDADO",
                                       "BLOQUEADO_CAMBIO_LONGITUD_SCRIPT"):
                blocked.append({"grupo_id": gid, "motivo": state["estado"]})
                continue
        elif where == "DATABASE.DAT/STRTBL.DAT":
            if state["estado"] != "BLOQUEADO_SIN_MODELO_DE_CAPACIDAD":
                blocked.append({"grupo_id": gid, "motivo": state["estado"]})
                continue
        elif where.startswith("DATABASE.DAT/"):
            if state["estado"] != "CANDIDATO_A_ENSAYO_NO_VALIDADO":
                blocked.append({"grupo_id": gid, "motivo": state["estado"]})
                continue
        elif where.startswith("SYS.DAT2/"):
            image = where.split("/", 1)[1]
            if image not in GRAPHICS or spanish != GRAPHICS[image][3]:
                blocked.append({"grupo_id": gid, "motivo": "IMAGEN_NO_AUTORIZADA"})
                continue
        elif where == TARGET_CREDITS:
            # Counts, offsets and source bytes will be checked against every original line.
            if state["estado"] not in ("BLOQUEADO_SIN_MODELO_DE_CAPACIDAD",
                                       "CANDIDATO_A_ENSAYO_NO_VALIDADO"):
                blocked.append({"grupo_id": gid, "motivo": state["estado"]})
                continue
        else:
            blocked.append({"grupo_id": gid, "motivo": "FORMATO_AUN_NO_INTEGRADO",
                            "origen": where})
            continue
        changes[where].append((src, old, new))
    return changes, blocked, unchanged


def combine_verified_script_packs(allowed, deferred, plan):
    """Join R29-R33 to the fixed-offset planner, without changing the corpus.

    All entries must be previously deferred SCRIPT records, not new arbitrary
    writes.  Return new lists; never mutate caller inputs on failure.
    """
    require(len(plan) == 1448, "Verified pack count drift")
    require(len(allowed) == 376 and len(deferred) == 4524,
            "Conservative baseline script counts drift")
    base = {src["grupo_id"] for src, _, _ in allowed}
    waiting = {src["grupo_id"]: (src, old, new) for src, old, new in deferred}
    require(len(base) == len(allowed) and len(waiting) == len(deferred)
            and not base.intersection(waiting), "Baseline IDs collide")
    merged = list(allowed)
    selected = set()
    spans = [(int(src["offset_hex"], 16), len(old)) for src, old, _ in allowed]
    for item in plan:
        gid = item["gid"]
        require(gid in waiting and gid not in selected, "Pack ID is not a unique deferred slot")
        src, old, ordinary = waiting[gid]
        new = item["new"]
        require(src["origen"] == TARGET_SCRIPT and int(src["offset_hex"], 16) == item["offset"]
                and src["grupo_id"] == item["group_id"]
                and bytes.fromhex(src["bytes_hex"]) == old == item["old"]
                and len(ordinary) != len(old) == len(new) and new != old
                and 0 not in new, "Pack preimage/width/control mismatch")
        text = decode_spanish(new)
        require(encode_spanish(text) == new, "Pack encoding roundtrip failed")
        selected.add(gid)
        spans.append((item["offset"], len(old)))
        merged.append((src, old, new))
    spans.sort()
    require(all(a + z <= b for (a, z), (b, _) in zip(spans, spans[1:])),
            "Merged script spans overlap")
    remaining = [r for r in deferred if r[0]["grupo_id"] not in selected]
    require(len(merged) == 1824 and len(remaining) == 3076, "Merged count drift")
    merged.sort(key=lambda r: int(r[0]["offset_hex"], 16))
    return merged, remaining, selected


def plan_event_safe(changes, blocked, *, verified_packs=False):
    """Fixed offsets for both historical and accumulated conservative profiles."""
    allowed, deferred = [], []
    for src, old, new in changes.get(TARGET_SCRIPT, []):
        (allowed if len(old) == len(new) else deferred).append((src, old, new))
    info = None
    if verified_packs:
        # Lazy import avoids the r31 -> r29 -> this module import cycle.
        try:
            from tools.r31_bulk_padding import make_plan, serialized, fnv
        except ModuleNotFoundError:
            from r31_bulk_padding import make_plan, serialized, fnv
        require(sum(map(len, changes.values())) == 8248, "Canonical admissible count drift")
        plan = make_plan(pack="all")
        require(fnv(serialized(plan, False)) == 1345572782
                and fnv(serialized(plan)) == 4017724493,
                "R34 independently verified combined pack fingerprints differ")
        allowed, deferred, selected = combine_verified_script_packs(allowed, deferred, plan)
        info = {"baseline": 3724, "additional_exact": 146, "additional_padded": 1302,
                "selected": len(selected), "total_planned": 5172, "remaining": 3076,
                "runtime_verified": False, "release_authorized": False,
                "selected_ids_sha256": hashlib.sha256(",".join(sorted(selected)).encode("ascii")).hexdigest()}
    result = changes.copy()
    if allowed:
        result[TARGET_SCRIPT] = allowed
    else:
        result.pop(TARGET_SCRIPT, None)
    event_deferred = [src["grupo_id"] for src, _, _ in deferred]
    blocked = list(blocked) + [{"grupo_id": gid,
                               "motivo": "CAMBIO_LONGITUD_SCRIPT_EVENTO_PENDIENTE"}
                              for gid in event_deferred]
    if verified_packs:
        require(sum(map(len, result.values())) == 5172 and len(event_deferred) == 3076,
                "Accumulated profile count drift")
    return result, blocked, event_deferred, info


def combine_unified_profile(changes, blocked, deferred, accumulated, *, draft_csv=DRAFT):
    """R36 single-pass 7093 profile; preserve R34 and add only vetted ligatures."""
    try:
        from tools.r35_ligaduras_acumuladas import make_plan, PAIRS
        from tools.f4_r21_ligature_capacity import decode_encoded
    except ModuleNotFoundError:
        from r35_ligaduras_acumuladas import make_plan, PAIRS
        from f4_r21_ligature_capacity import decode_encoded
    selected, full, verification = make_plan()
    base = {src["grupo_id"]: (src, old, new) for src, old, new in changes[TARGET_SCRIPT]}
    by_id = {src["grupo_id"]: src for src, dst in source_rows(SOURCE, draft_csv)}
    extra = {x["gid"]: x for x in selected}
    require(len(base) == 1824 and len(extra) == 1921
            and set(extra) <= set(deferred) and not set(base) & set(extra),
            "R36 duplicate or non-deferred text")
    merged = list(base.values())
    for gid, x in extra.items():
        src = by_id[gid]
        require(src["origen"] == TARGET_SCRIPT
                and int(src["offset_hex"],16) == x["offset"]
                and bytes.fromhex(src["bytes_hex"]) == x["old"]
                and len(x["old"]) == len(x["new"]) and 0 not in x["new"],
                "R36 source slot mismatch")
        merged.append((src,x["old"],x["new"]))
    merged.sort(key=lambda x:int(x[0]["offset_hex"],16))
    require([(src["grupo_id"],int(src["offset_hex"],16),old,new) for src,old,new in merged]
            == [(x["gid"],x["offset"],x["old"],x["new"]) for x in full],
            "R36 independent full plan differs")
    result = changes.copy()
    result[TARGET_SCRIPT] = merged
    remaining = [gid for gid in deferred if gid not in extra]
    filtered = [b for b in blocked if b["grupo_id"] not in extra]
    require(len(blocked)-len(filtered)==1921 and len(remaining)==1155
            and sum(map(len,result.values()))==7093, "R36 totals differ")
    info = {**accumulated,"selected":3369,"additional_ligatures":1921,
            "r34_selected_ids_sha256":accumulated["selected_ids_sha256"],
            "full_script_ids_sha256":hashlib.sha256(",".join(sorted(set(base)|set(extra))).encode("ascii")).hexdigest(),
            "total_planned":7093,"remaining":1155,"script_changes":3745,
            "compact_font_experimental":True,"runtime_verified":False,
            "release_authorized":False,"r35_batch_verification":verification["batches"]}
    info.pop("selected_ids_sha256",None)
    return result,filtered,remaining,info


def combine_extended_padding(changes,blocked,deferred,accumulated,*,draft_csv=DRAFT):
    """R37 opt-in: longer whitespace is still visually unverified."""
    try:
        from tools.r37_relleno_ampliado import audit
    except ModuleNotFoundError:
        from r37_relleno_ampliado import audit
    baseline=changes[TARGET_SCRIPT]
    full=[{"gid":r["grupo_id"],"offset":int(r["offset_hex"],16),"old":a,"new":b}
          for r,a,b in baseline]
    selected,verification=audit(full)
    extra={x["gid"]:x for x in selected}
    require(len(extra)==275 and set(extra)<=set(deferred),"R37 non-deferred IDs")
    by_id={r["grupo_id"]:r for r,_ in source_rows(SOURCE,draft_csv)}
    merged=list(baseline)
    for gid,x in extra.items():
        r=by_id[gid]
        require(r["origen"]==TARGET_SCRIPT and int(r["offset_hex"],16)==x["offset"]
                and bytes.fromhex(r["bytes_hex"])==x["old"]
                and len(x["old"])==len(x["new"]) and 0 not in x["new"],
                "R37 slot mismatch")
        merged.append((r,x["old"],x["new"]))
    merged.sort(key=lambda x:int(x[0]["offset_hex"],16))
    require(len({r["grupo_id"] for r,_,_ in merged})==4020
            and all(int(a[0]["offset_hex"],16)+len(a[1])<=int(b[0]["offset_hex"],16)
                    for a,b in zip(merged,merged[1:])), "R37 overlapping slots")
    result=changes.copy()
    result[TARGET_SCRIPT]=merged
    remaining=[g for g in deferred if g not in extra]
    filtered=[b for b in blocked if b["grupo_id"] not in extra]
    require(len(remaining)==880 and len(blocked)-len(filtered)==275
            and sum(map(len,result.values()))==7368,"R37 profile drift")
    info={**accumulated,"selected":3644,"total_planned":7368,"remaining":880,
          "script_changes":4020,"extended_padding":verification,
          "full_script_ids_sha256":hashlib.sha256(",".join(sorted(r["grupo_id"] for r,_,_ in merged)).encode("ascii")).hexdigest()}
    return result,filtered,remaining,info


def combine_verified_symbols(changes,blocked,deferred,accumulated,*,draft_csv=DRAFT):
    """R37: retain all original CP932 symbol bytes; do not promote runtime."""
    try:
        from tools.r37_simbolos_preservados import audit
    except ModuleNotFoundError:
        from r37_simbolos_preservados import audit
    baseline=changes[TARGET_SCRIPT]
    full=[{"gid":r["grupo_id"],"offset":int(r["offset_hex"],16),"old":a,"new":b}
          for r,a,b in baseline]
    selected,verification=audit(full)
    extra={x["gid"]:x for x in selected}
    require(len(extra)==53 and set(extra)<=set(deferred),"R37 symbol IDs not deferred")
    by_id={r["grupo_id"]:r for r,_ in source_rows(SOURCE,draft_csv)}
    merged=list(baseline)
    for gid,x in extra.items():
        r=by_id[gid]
        require(r["origen"]==TARGET_SCRIPT and int(r["offset_hex"],16)==x["offset"]
                and bytes.fromhex(r["bytes_hex"])==x["old"]
                and len(x["old"])==len(x["new"]) and 0 not in x["new"],
                "R37 symbol slot mismatch")
        merged.append((r,x["old"],x["new"]))
    merged.sort(key=lambda x:int(x[0]["offset_hex"],16))
    require(len({r["grupo_id"] for r,_,_ in merged})==4073
            and all(int(a[0]["offset_hex"],16)+len(a[1])<=int(b[0]["offset_hex"],16)
                    for a,b in zip(merged,merged[1:])), "R37 symbol overlaps")
    result=changes.copy()
    result[TARGET_SCRIPT]=merged
    remaining=[g for g in deferred if g not in extra]
    filtered=[b for b in blocked if b["grupo_id"] not in extra]
    require(len(remaining)==827 and len(blocked)-len(filtered)==53
            and sum(map(len,result.values()))==7421,"R37 complete residual profile drift")
    info={**accumulated,"selected":3697,"total_planned":7421,"remaining":827,
          "script_changes":4073,"verified_symbols":verification,
          "full_script_ids_sha256":hashlib.sha256(",".join(sorted(r["grupo_id"] for r,_,_ in merged)).encode("ascii")).hexdigest()}
    return result,filtered,remaining,info


def combine_reviewed_concise(changes,blocked,deferred,accumulated,*,draft_csv=DRAFT):
    """R38: add the 99 authenticated concise alternatives to the entire R37 plan."""
    try:
        from tools.r38_concision import audit
    except ModuleNotFoundError:
        from r38_concision import audit
    baseline=changes[TARGET_SCRIPT]
    full=[{"gid":r["grupo_id"],"offset":int(r["offset_hex"],16),"old":a,"new":b}
          for r,a,b in baseline]
    selected,verification=audit(full)
    extra={x["gid"]:x for x in selected}
    require(len(extra)==99 and set(extra)<=set(deferred),"R38 non-deferred IDs")
    by_id={r["grupo_id"]:r for r,_ in source_rows(SOURCE,draft_csv)}
    merged=list(baseline)
    for gid,x in extra.items():
        r=by_id[gid]
        require(r["origen"]==TARGET_SCRIPT and int(r["offset_hex"],16)==x["offset"]
                and bytes.fromhex(r["bytes_hex"])==x["old"]
                and len(x["old"])==len(x["new"]) and 0 not in x["new"],
                "R38 slot mismatch")
        merged.append((r,x["old"],x["new"]))
    merged.sort(key=lambda x:int(x[0]["offset_hex"],16))
    require(len({r["grupo_id"] for r,_,_ in merged})==4172
            and all(int(a[0]["offset_hex"],16)+len(a[1])<=int(b[0]["offset_hex"],16)
                    for a,b in zip(merged,merged[1:])), "R38 overlapping slots")
    result=changes.copy()
    result[TARGET_SCRIPT]=merged
    remaining=[g for g in deferred if g not in extra]
    filtered=[b for b in blocked if b["grupo_id"] not in extra]
    require(len(remaining)==728 and len(blocked)-len(filtered)==99
            and sum(map(len,result.values()))==7520,"R38 accumulated profile drift")
    info={**accumulated,"selected":3796,"total_planned":7520,"remaining":728,
          "script_changes":4172,"reviewed_concise":verification,
          "full_script_ids_sha256":hashlib.sha256(",".join(sorted(r["grupo_id"] for r,_,_ in merged)).encode("ascii")).hexdigest()}
    return result,filtered,remaining,info


def combine_r39_concise(changes,blocked,deferred,accumulated,*,draft_csv=DRAFT):
    """R39: add the 176 authenticated concise alternatives to the entire R37 plan."""
    try:
        from tools.r39_concision import audit
    except ModuleNotFoundError:
        from r39_concision import audit
    baseline=changes[TARGET_SCRIPT]
    full=[{"gid":r["grupo_id"],"offset":int(r["offset_hex"],16),"old":a,"new":b}
          for r,a,b in baseline]
    selected,verification=audit(full)
    extra={x["gid"]:x for x in selected}
    require(len(extra)==176 and set(extra)<=set(deferred),"R39 non-deferred IDs")
    by_id={r["grupo_id"]:r for r,_ in source_rows(SOURCE,draft_csv)}
    merged=list(baseline)
    for gid,x in extra.items():
        r=by_id[gid]
        require(r["origen"]==TARGET_SCRIPT and int(r["offset_hex"],16)==x["offset"]
                and bytes.fromhex(r["bytes_hex"])==x["old"]
                and len(x["old"])==len(x["new"]) and 0 not in x["new"],
                "R39 slot mismatch")
        merged.append((r,x["old"],x["new"]))
    merged.sort(key=lambda x:int(x[0]["offset_hex"],16))
    require(len({r["grupo_id"] for r,_,_ in merged})==4348
            and all(int(a[0]["offset_hex"],16)+len(a[1])<=int(b[0]["offset_hex"],16)
                    for a,b in zip(merged,merged[1:])), "R39 overlapping slots")
    result=changes.copy()
    result[TARGET_SCRIPT]=merged
    remaining=[g for g in deferred if g not in extra]
    filtered=[b for b in blocked if b["grupo_id"] not in extra]
    require(len(remaining)==552 and len(blocked)-len(filtered)==176
            and sum(map(len,result.values()))==7696,"R39 accumulated profile drift")
    info={**accumulated,"selected":3972,"total_planned":7696,"remaining":552,
          "script_changes":4348,"reviewed_concise_r39":verification,
          "full_script_ids_sha256":hashlib.sha256(",".join(sorted(r["grupo_id"] for r,_,_ in merged)).encode("ascii")).hexdigest()}
    return result,filtered,remaining,info


def combine_r40_concise(changes,blocked,deferred,accumulated,*,draft_csv=DRAFT):
    """R40: add the 492 authenticated concise alternatives to the entire R39 plan."""
    try:
        from tools.r40_concision import audit
    except ModuleNotFoundError:
        from r40_concision import audit
    baseline=changes[TARGET_SCRIPT]
    full=[{"gid":r["grupo_id"],"offset":int(r["offset_hex"],16),"old":a,"new":b}
          for r,a,b in baseline]
    selected,verification=audit(full)
    extra={x["gid"]:x for x in selected}
    require(len(extra)==492 and set(extra)<=set(deferred),"R40 non-deferred IDs")
    by_id={r["grupo_id"]:r for r,_ in source_rows(SOURCE,draft_csv)}
    merged=list(baseline)
    for gid,x in extra.items():
        r=by_id[gid]
        require(r["origen"]==TARGET_SCRIPT and int(r["offset_hex"],16)==x["offset"]
                and bytes.fromhex(r["bytes_hex"])==x["old"]
                and len(x["old"])==len(x["new"]) and 0 not in x["new"],
                "R40 slot mismatch")
        merged.append((r,x["old"],x["new"]))
    merged.sort(key=lambda x:int(x[0]["offset_hex"],16))
    require(len({r["grupo_id"] for r,_,_ in merged})==4840
            and all(int(a[0]["offset_hex"],16)+len(a[1])<=int(b[0]["offset_hex"],16)
                    for a,b in zip(merged,merged[1:])), "R40 overlapping slots")
    result=changes.copy()
    result[TARGET_SCRIPT]=merged
    remaining=[g for g in deferred if g not in extra]
    filtered=[b for b in blocked if b["grupo_id"] not in extra]
    require(len(remaining)==60 and len(blocked)-len(filtered)==492
            and sum(map(len,result.values()))==8188,"R40 accumulated profile drift")
    info={**accumulated,"selected":4464,"total_planned":8188,"remaining":60,
          "script_changes":4840,"reviewed_concise_r40":verification,
          "full_script_ids_sha256":hashlib.sha256(",".join(sorted(r["grupo_id"] for r,_,_ in merged)).encode("ascii")).hexdigest()}
    return result,filtered,remaining,info



def combine_r42_concise(changes,blocked,deferred,accumulated,*,draft_csv=DRAFT):
    """R42: add the 21 authenticated R42 alternatives to the complete R40 plan."""
    try:
        from tools.r42_concision import audit
    except ModuleNotFoundError:
        from r42_concision import audit
    baseline=changes[TARGET_SCRIPT]
    full=[{"gid":r["grupo_id"],"offset":int(r["offset_hex"],16),"old":a,"new":b}
          for r,a,b in baseline]
    selected,verification=audit(full)
    extra={x["gid"]:x for x in selected}
    require(len(extra)==21 and set(extra)<=set(deferred),"R42 non-deferred IDs")
    by_id={r["grupo_id"]:r for r,_ in source_rows(SOURCE,draft_csv)}
    merged=list(baseline)
    for gid,x in extra.items():
        r=by_id[gid]
        require(r["origen"]==TARGET_SCRIPT and int(r["offset_hex"],16)==x["offset"]
                and bytes.fromhex(r["bytes_hex"])==x["old"]
                and len(x["old"])==len(x["new"]) and 0 not in x["new"],
                "R42 slot mismatch")
        merged.append((r,x["old"],x["new"]))
    merged.sort(key=lambda x:int(x[0]["offset_hex"],16))
    require(len({r["grupo_id"] for r,_,_ in merged})==4861
            and all(int(a[0]["offset_hex"],16)+len(a[1])<=int(b[0]["offset_hex"],16)
                    for a,b in zip(merged,merged[1:])), "R42 overlapping slots")
    result=changes.copy()
    result[TARGET_SCRIPT]=merged
    remaining=[g for g in deferred if g not in extra]
    filtered=[b for b in blocked if b["grupo_id"] not in extra]
    require(len(remaining)==39 and len(blocked)-len(filtered)==21
            and sum(map(len,result.values()))==8209,"R42 accumulated profile drift")
    info={**accumulated,"selected":4485,"total_planned":8209,"remaining":39,
          "script_changes":4861,"reviewed_concise_r42":verification,
          "full_script_ids_sha256":hashlib.sha256(",".join(sorted(r["grupo_id"] for r,_,_ in merged)).encode("ascii")).hexdigest()}
    return result,filtered,remaining,info



def combine_r43_concise(changes,blocked,deferred,accumulated,*,draft_csv=DRAFT):
    """Five new R43 slots; repair one previous slot and close one unchanged name."""
    try:
        from tools.r43_concision import audit, UNCHANGED_ID, REPAIR_ID
    except ModuleNotFoundError:
        from r43_concision import audit, UNCHANGED_ID, REPAIR_ID
    baseline=changes[TARGET_SCRIPT]
    full=[{"gid":r["grupo_id"],"offset":int(r["offset_hex"],16),"old":a,"new":b}
          for r,a,b in baseline]
    selected,repair,verification=audit(full)
    extra={x["gid"]:x for x in selected}
    resolved=set(extra)|{UNCHANGED_ID}
    require(len(extra)==5 and resolved<=set(deferred),"R43 non-deferred ID")
    by_id={r["grupo_id"]:r for r,_ in source_rows(SOURCE,draft_csv)}
    merged=[(r,a,repair["new"] if r["grupo_id"]==REPAIR_ID else b) for r,a,b in baseline]
    for gid,x in extra.items():
        r=by_id[gid]
        require(r["origen"]==TARGET_SCRIPT and int(r["offset_hex"],16)==x["offset"]
                and bytes.fromhex(r["bytes_hex"])==x["old"] and len(x["old"])==len(x["new"])
                and 0 not in x["new"],"R43 slot mismatch")
        merged.append((r,x["old"],x["new"]))
    merged.sort(key=lambda x:int(x[0]["offset_hex"],16))
    require(len(merged)==len({r["grupo_id"] for r,_,_ in merged})==4866
            and all(int(a[0]["offset_hex"],16)+len(a[1])<=int(b[0]["offset_hex"],16)
                    for a,b in zip(merged,merged[1:])),"R43 overlapping slots")
    result=changes.copy(); result[TARGET_SCRIPT]=merged
    remaining=[g for g in deferred if g not in resolved]
    filtered=[b for b in blocked if b["grupo_id"] not in resolved]
    require(len(remaining)==33 and len(blocked)-len(filtered)==6
            and sum(map(len,result.values()))==8214,"R43 profile drift")
    info={**accumulated,"selected":4490,"total_planned":8214,"remaining":33,
          "script_changes":4866,"resolved_without_new_bytes":1,"resolved_original_target":8215,
          "reviewed_concise_r43":verification,
          "full_script_ids_sha256":hashlib.sha256(",".join(sorted(r["grupo_id"] for r,_,_ in merged)).encode("ascii")).hexdigest()}
    return result,filtered,remaining,info


def combine_r44_local_experimental(changes,blocked,deferred,accumulated,*,draft_csv=DRAFT,optimized=False):
    """RISK: 33 new residual translations, 18 donors, moving command offsets."""
    try:
        from tools.r44_local_experimental import audit
    except ModuleNotFoundError:
        from r44_local_experimental import audit
    if optimized:
        from tools.r52_local_optimized import audit
    baseline=changes[TARGET_SCRIPT]
    full=[{"gid":r["grupo_id"],"offset":int(r["offset_hex"],16),"old":a,"new":b}
          for r,a,b in baseline]
    selected,donors,verification=audit(full,deferred)
    extra={x["gid"]:x for x in selected}
    require(set(extra)==set(deferred),"R44 deferred set drift")
    by_id={r["grupo_id"]:r for r,_ in source_rows(SOURCE,draft_csv)}
    merged=[(r,a,donors[r["grupo_id"]]["new"] if r["grupo_id"] in donors else b)
            for r,a,b in baseline]
    for gid,x in extra.items():
        r=by_id[gid]
        require(r["origen"]==TARGET_SCRIPT and int(r["offset_hex"],16)==x["offset"]
                and bytes.fromhex(r["bytes_hex"])==x["old"] and 0 not in x["new"],"R44 slot mismatch")
        merged.append((r,x["old"],x["new"]))
    merged.sort(key=lambda x:int(x[0]["offset_hex"],16))
    require(len(merged)==len({r["grupo_id"] for r,_,_ in merged})==4899,"R44 merged count")
    result=changes.copy(); result[TARGET_SCRIPT]=merged
    filtered=[b for b in blocked if b["grupo_id"] not in extra]
    require(len(blocked)-len(filtered)==33 and sum(map(len,result.values()))==8247,"R44 profile drift")
    info={**accumulated,"selected":4523,"total_planned":8247,"remaining":0,
          "script_changes":4899,"resolved_original_target":8248,
          "local_relocation_experimental":verification,
          "full_script_ids_sha256":hashlib.sha256(",".join(sorted(r["grupo_id"] for r,_,_ in merged)).encode("ascii")).hexdigest()}
    return result,filtered,[],info

def read_resources(iso):
    _, iso_files = iso9660_entries(iso)
    target = next((x for x in iso_files if x["path"] == "PSP_GAME/USRDIR/DATA.DAT"), None)
    require(target is not None, "Falta DATA.DAT")
    pack = read_iso_file(iso, target)
    entries = pspfs_entries(pack)
    require(len(entries) == 349 and len({x["name"] for x in entries}) == 349,
            "PSPFS inesperado")
    return target, pack, entries


def parent_content(pack, entry):
    start = entry["offset"]
    stored = pack[start:start + entry["size_stored"]]
    decoded, method = decompress(stored, entry["size_expanded"])
    return stored, decoded, method


def text_command_rebuild(data, table, allowed):
    """Replace textual opcodes, recompute parameter lengths and 1625 script starts.

    No non-text instruction is interpreted or changed. Its original byte sequence
    is carried over bit-for-bit; original script padding and 16-byte alignment remain.
    """
    count = u32(table)
    require(len(table) == 16 + 32 * count and count == 1625,
            "Unexpected SCRIPT.TBL")
    result, table_copy, used = bytearray(), bytearray(table), set()
    for i in range(count):
        old_start = u32(table, 16 + i * 32 + 4)
        old_end = u32(table, 16 + (i + 1) * 32 + 4) if i + 1 < count else len(data)
        require(0 <= old_start <= old_end <= len(data), "Script boundary invalid")
        struct.pack_into("<I", table_copy, 16 + i * 32 + 4, len(result))
        pos = old_start
        while pos + 5 <= old_end:
            if not any(data[pos:old_end]):
                break
            old_param_len = u16(data, pos + 3)
            end = pos + 5 + old_param_len
            require(end <= old_end, "Opcode runs past script boundary")
            original_cmd = data[pos:end]
            code = data[pos]
            if code in TEXT_OPS and old_param_len >= 3:
                payload = data[pos + 5:end]
                require(u16(payload) + 3 == old_param_len and payload[-1] == 0,
                        f"Text opcode format unexpected at {pos:#x}")
                slot = pos + 7
                if slot in allowed:
                    old, new, gid = allowed[slot]
                    require(payload[2:-1] == old, f"Original string mismatch: {gid}")
                    require(slot not in used, f"Duplicate script string offset: {gid}")
                    require(len(new) + 3 <= 65535, f"Text opcode too long: {gid}")
                    new_param_len = len(new) + 3
                    result.extend(original_cmd[:3])
                    result.extend(struct.pack("<H", new_param_len))
                    result.extend(struct.pack("<H", len(new)))
                    result.extend(new)
                    result.append(0)
                    used.add(slot)
                else:
                    result.extend(original_cmd)
            else:
                require(slot_not_in_command(pos, end, allowed),
                        "A planned text offset points inside a non-text instruction")
                result.extend(original_cmd)
            pos = end
        require(not any(data[pos:old_end]), "Nonzero script trailer")
        result.extend(b"\0" * (16 - len(result) % 16))
    require(used == set(allowed), "Unmatched script translation offsets")
    if not allowed:
        require(bytes(result) == data and bytes(table_copy) == table,
                "No-op script reconstruction changed original data")
    return bytes(result), bytes(table_copy)


def slot_not_in_command(start, end, allowed):
    return not any(start <= off < end for off in allowed)


def rebuild_script_arc(archive, replacements, *, event_report=None, strict_event_offsets=False):
    children = dsarc_entries(archive)
    by_name = {x["name"]: x for x in children}
    require(set(by_name) == {"AISCRIPT.DAT", "AISCRIPT.TBL", "SCRIPT.DAT", "SCRIPT.TBL"},
            "Unexpected SCRIPT.SDT members")
    script = by_name["SCRIPT.DAT"]
    tbl = by_name["SCRIPT.TBL"]
    script_old = archive[script["offset"]:script["offset"] + script["size"]]
    tbl_old = archive[tbl["offset"]:tbl["offset"] + tbl["size"]]
    new_script, new_tbl = text_command_rebuild(script_old, tbl_old, replacements)
    # Independent command-by-command comparison before any DSARC or IMY packing.
    event_audit = audit_script_rebuild(
        script_old, tbl_old, new_script, new_tbl, replacements,
        require_fixed_offsets=strict_event_offsets)
    if event_report is not None:
        event_report.update(event_audit)
    new_tbl_start = strict_next(script["offset"] + len(new_script), 512)
    archive_len = align(new_tbl_start + len(new_tbl), 256)
    result = bytearray(archive_len)
    result[:script["offset"]] = archive[:script["offset"]]
    result[script["offset"]:script["offset"] + len(new_script)] = new_script
    result[new_tbl_start:new_tbl_start + len(new_tbl)] = new_tbl
    for x in children:
        if x["name"] in ("SCRIPT.DAT", "SCRIPT.TBL"):
            continue
        start, end = x["offset"], x["offset"] + x["size"]
        require(archive[start:end] == result[start:end],
                f"Unrelated DSARC member changed: {x['name']}")
    # DSARC FL metadata: count, size/offset pairs. NO changes to unrelated entries.
    struct.pack_into("<I", result, int(script["table_offset_hex"], 16) + 40, len(new_script))
    struct.pack_into("<I", result, int(tbl["table_offset_hex"], 16) + 44, new_tbl_start)
    new_children = dsarc_entries(result)
    require([x["name"] for x in new_children] == [x["name"] for x in children],
            "SCRIPT.SDT member order changed")
    return bytes(result)


def rebuild_strtbl_member(original, rows):
    """Rebuild 654 pointer slots and 651 NUL-terminated strings, preserving 3 zeros."""
    first = u32(original)
    require(first % 4 == 0 and first <= len(original), "STRTBL header invalid")
    count = first // 4
    offsets = struct.unpack_from("<" + "I" * count, original)
    valid = [(index, value) for index, value in enumerate(offsets)
             if first <= value < len(original)]
    require(len(valid) == 651 and len({value for index, value in valid}) == 651,
            "STRTBL count or alias model differs from verified source")
    require([value for index, value in valid] == sorted(value for index, value in valid),
            "STRTBL pointers not monotonic")
    changed = {}
    for source, old, new in rows:
        index = int(source["indice_registro"])
        require(index not in changed, f"Duplicated STRTBL ID at index {index}")
        changed[index] = source, old, new

    new_table = bytearray(original[:first])
    body = bytearray()
    used = set()
    for pos, (index, offset) in enumerate(valid):
        end = valid[pos + 1][1] if pos + 1 < len(valid) else len(original)
        require(end > offset and original[end - 1] == 0 and b"\0" not in original[offset:end - 1],
                f"Unexpected terminator in STRTBL index {index}")
        original_value = original[offset:end - 1]
        replacement = original_value
        if index in changed:
            source, old, new = changed[index]
            require(int(source["offset_hex"], 16) == offset and old == original_value,
                    f"String table source byte mismatch: {source['grupo_id']}")
            replacement = new
            used.add(source["grupo_id"])
        struct.pack_into("<I", new_table, index * 4, first + len(body))
        body.extend(replacement + b"\0")
    require(used == {source["grupo_id"] for source, old, new in rows},
            "STRTBL change unaccounted for")
    return bytes(new_table + body), used


def rebuild_database_arc(archive, per_child):
    result = bytearray(archive)
    children = {x["name"]: x for x in dsarc_entries(archive)}
    seen = set()
    strtbl_changes = per_child.get("STRTBL.DAT", [])
    for child_name, records in per_child.items():
        if child_name == "STRTBL.DAT":
            continue
        require(child_name in children, "Unknown DB member")
        member = children[child_name]
        before = archive[member["offset"]:member["offset"] + member["size"]]
        updated = bytearray(before)
        prior_end = 0
        for src, old, new in sorted(records, key=lambda x: int(x[0]["offset_hex"], 16)):
            offset = int(src["offset_hex"], 16)
            cap = int(src["capacidad_campo"])
            require(offset >= prior_end and offset + cap <= len(before),
                    f"Overlapping or out-of-range DB record: {src['grupo_id']}")
            require(before[offset:offset + len(old)] == old, f"DB byte mismatch: {src['grupo_id']}")
            # The corpus's capacity is only an upper bound. Some original fields
            # terminate immediately before non-text record metadata; never zero
            # those metadata bytes even when a modelled field size includes them.
            if cap == len(old):
                # A few fixed-width names occupy the entire field, with no NUL.
                # Only alter that exact span; never write into the next record.
                require(len(new) <= cap, f"DB fixed-width overflow: {src['grupo_id']}")
                updated[offset:offset + cap] = new + b" " * (cap - len(new))
                prior_end = offset + cap
            else:
                trailer = before[offset + len(old):offset + cap]
                first_nonzero = next((i for i, value in enumerate(trailer) if value), len(trailer))
                verified_cap = len(old) + first_nonzero
                require(verified_cap >= len(new) + 1,
                        f"DB field overflows verified NUL padding: {src['grupo_id']}")
                require(first_nonzero > 0, f"DB field missing terminator: {src['grupo_id']}")
                updated[offset:offset + verified_cap] = new + b"\0" * (verified_cap - len(new))
                prior_end = offset + verified_cap
            seen.add(src["grupo_id"])
        result[member["offset"]:member["offset"] + member["size"]] = updated
    for child_name, member in children.items():
        if child_name in per_child:
            continue
        start, end = member["offset"], member["offset"] + member["size"]
        require(result[start:end] == archive[start:end],
                f"DB nontext member changed: {child_name}")
    if strtbl_changes:
        member = children.get("STRTBL.DAT")
        require(member is not None, "Missing STRTBL.DAT member")
        old = archive[member["offset"]:member["offset"] + member["size"]]
        changed_table, used = rebuild_strtbl_member(old, strtbl_changes)
        append_at = strict_next(len(result), 512)
        target = bytearray(align(append_at + len(changed_table), 256))
        target[:len(result)] = result
        target[append_at:append_at + len(changed_table)] = changed_table
        meta = int(member["table_offset_hex"], 16)
        struct.pack_into("<I", target, meta + 40, len(changed_table))
        struct.pack_into("<I", target, meta + 44, append_at)
        updated_members = {x["name"]: x for x in dsarc_entries(target)}
        for name, original_member in children.items():
            if name == "STRTBL.DAT":
                continue
            require(original_member["offset"] == updated_members[name]["offset"] and
                    original_member["size"] == updated_members[name]["size"],
                    f"Relocation of unrelated DATABASE.DAT member: {name}")
        seen |= used
        result = target
    return bytes(result), seen

def rebuild_sys_arc(archive, per_child):
    """Append localized PNGs; only the six text images may be changed.

    The six original PNG data regions remain in the DSARC copy; the new
    members are appended and linked from their six table entries. This avoids
    relocating any unrelated graphic or binary within SYS.DAT2.
    """
    children = {x["name"]: x for x in dsarc_entries(archive)}
    require(set(children) == set(GRAPHICS) and set(per_child) == set(GRAPHICS),
            "Expected all six and only the six audited graphical text members")
    target = bytearray(archive)
    accounted_for = set()
    audits = []
    for name in sorted(GRAPHICS):
        records = per_child[name]
        require(len(records) == 1, "Expected one translation per graphical text PNG")
        src, old, encoded = records[0]
        require(src["origen"] == "SYS.DAT2/" + name and
                src["original"] in ("NO DATA", "This is an RPG!") and
                src["tipo"] in ("mensaje_grafico", "titulo_grafico"),
                "Graphic text source metadata unexpected")
        member = children[name]
        original = archive[member["offset"]:member["offset"] + member["size"]]
        updated, audit = patch_png(name, original, GRAPHICS[name][3])
        position = strict_next(len(target), 512)
        target.extend(b"\0" * (position - len(target)))
        target.extend(updated)
        meta = int(member["table_offset_hex"], 16)
        struct.pack_into("<II", target, meta + 40, len(updated), position)
        require(target[member["offset"]:member["offset"] + member["size"]] == original,
                "Original PNG bytes moved or altered")
        accounted_for.add(src["grupo_id"])
        audits.append(audit)
    after = {x["name"]: x for x in dsarc_entries(target)}
    require(set(after) == set(children), "SYS.DAT2 member inventory changed")
    for name in children:
        record = after[name]
        require(target[record["offset"]:record["offset"] + record["size"]][:8] == b"\x89PNG\r\n\x1a\n",
                "Rebuilt PNG resource not recognized")
    return bytes(target), accounted_for, audits



def rebuild_sys_arc_compact(archive, per_child, capacity):
    """Rebuild only the six approved PNGs inside the original PSPFS physical slot.

    Unlike the former append-to-parent approach, this does not duplicate every
    bitmap and nearly double SYS.DAT2 RAM allocation. Offsets remain 512 aligned
    and neighboring PSPFS assets are never moved or overwritten.
    """
    children = dsarc_entries(archive)
    require(archive[:8] == b"DSARC FL" and len(children) == 6 and
            {x["name"] for x in children} == set(GRAPHICS) == set(per_child),
            "Unexpected graphical text archive")
    header_end = min(x["offset"] for x in children)
    require(header_end % 512 == 0 and header_end >= 16 + 48 * len(children),
            "Unexpected graphical text header")
    require(capacity >= len(archive), "Original graphic PSPFS slot shrank")
    result = bytearray(archive[:header_end])
    cursor = header_end
    used, audits = set(), []
    for member in sorted(children, key=lambda x: x["offset"]):
        name = member["name"]
        rows = per_child[name]
        require(len(rows) == 1, "Expected one translated graphic per PNG")
        source, old, encoded = rows[0]
        require(source["origen"] == "SYS.DAT2/" + name and
                source["original"] in ("NO DATA", "This is an RPG!") and
                source["tipo"] in ("mensaje_grafico", "titulo_grafico"),
                "Unapproved graphical text metadata")
        original_png = archive[member["offset"]:member["offset"] + member["size"]]
        revised, audit = patch_png(name, original_png, GRAPHICS[name][3])
        cursor = align(cursor, 512)
        require(cursor + len(revised) <= capacity,
                "Translated PNGs do not fit original SYS.DAT2 PSPFS slot")
        if len(result) < cursor:
            result.extend(b"\0" * (cursor - len(result)))
        result.extend(revised)
        table_at = int(member["table_offset_hex"], 16)
        struct.pack_into("<II", result, table_at + 40, len(revised), cursor)
        cursor += len(revised)
        used.add(source["grupo_id"])
        audits.append(audit)
    total = align(cursor, 512)
    require(total <= capacity, "SYS.DAT2 physical slot overflow")
    result.extend(b"\0" * (total - len(result)))
    after = dsarc_entries(result)
    require([e["name"] for e in after] == [e["name"] for e in children],
            "DSARC member inventory/order changed")
    require(all(result[e["offset"]:e["offset"] + e["size"]].startswith(b"\x89PNG\r\n\x1a\n")
                for e in after), "Invalid PNG signature after compact repack")
    return bytes(result), used, audits


def rebuild_credits(raw, records):
    """Preserve CRLF/LF separators and rows from original STAFFROLL.TXT."""
    lines = raw.splitlines(keepends=True)
    by_index = {int(a["indice_registro"]): (a, old, new) for a, old, new in records}
    require(len(by_index) == len(records), "Duplicate credit lines")
    out = bytearray()
    positions = 0
    for index, line in enumerate(lines):
        plain = line.rstrip(b"\r\n")
        eol = line[len(plain):]
        if index in by_index:
            src, old, new = by_index[index]
            require(int(src["offset_hex"], 16) == positions and plain == old,
                    f"Credits source mismatch at line {index}")
            plain = new
        out.extend(plain + eol)
        positions += len(line)
    require(set(by_index) <= set(range(len(lines))), "Credit line out of range")
    return bytes(out)


def locate_iso_dir_record(path):
    """Find actual ISO9660 file directory entry; never scan/replace guessed bytes."""
    with path.open("rb") as stream:
        stream.seek(2048 * 16)
        pvd = stream.read(2048)
        require(pvd[:7] == b"\x01CD001\x01", "ISO9660 PVD missing")

        def fields(rec):
            return u32(rec, 2) * 2048, u32(rec, 10)

        rec = pvd[156:156 + pvd[156]]
        extent, size = fields(rec)
        for segment in ("PSP_GAME", "USRDIR", "DATA.DAT"):
            stream.seek(extent)
            folder = stream.read(size)
            offset = 0
            found = False
            while offset < len(folder):
                length = folder[offset]
                if length == 0:
                    offset = align(offset + 1, 2048)
                    continue
                row = folder[offset:offset + length]
                name_raw = row[33:33 + row[32]]
                if name_raw in (b"\x00", b"\x01"):
                    offset += length
                    continue
                name = name_raw.decode("ascii", "strict").split(";")[0]
                if name == segment:
                    directory_offset = extent + offset
                    extent, size = fields(row)
                    found = True
                    break
                offset += length
            require(found, f"ISO9660 entry missing: {segment}")
        return directory_offset, extent, size


def append_text_containers(source_iso, source_pack, entries, replacements, result_iso,
                           *, inplace_resources=frozenset()):
    """Only append modified PSPFS parents; no original asset offsets change."""
    record_at, extent, old_size = locate_iso_dir_record(source_iso)
    original_total = source_iso.stat().st_size
    require(extent + old_size <= original_total, "DATA.DAT extent outside ISO")
    by_name = {e["name"]: e for e in entries}
    actual_files = {}
    append_offset = original_total - extent
    require(append_offset % 512 == 0, "Append position not PSPFS aligned")
    shutil.copyfile(source_iso, result_iso)

    with result_iso.open("r+b") as target:
        target.seek(original_total)
        for name, (stored, expanded) in sorted(replacements.items()):
            require(name in ("SCRIPT.SDT", "DATABASE.DAT", "STAFFROLL.TXT", "SYS.DAT2"),
                    "Only text and six audited graphic-text members may be updated")
            original = by_name[name]
            if name in inplace_resources:
                require(name == "SYS.DAT2" and expanded == 0,
                        "Only the six verified graphical labels may be changed in place")
                next_start = min(x["offset"] for x in entries
                                 if x["offset"] > original["offset"])
                require(len(stored) <= next_start - original["offset"],
                        "SYS.DAT2 replacement would overwrite an adjacent resource")
                require(not any(source_pack[original["offset"] + original["size_stored"]:
                                            original["offset"] + len(stored)]),
                        "SYS.DAT2 in-place extension is not zero-padding")
                offset = original["offset"]
                pos = target.tell()
                target.seek(extent + offset)
                target.write(stored)
                target.seek(pos)
            else:
                offset = append_offset
                target.write(stored)
                pad = -len(stored) % 512
                target.write(b"\0" * pad)
                append_offset += len(stored) + pad
            table_at = extent + 16 + original["index"] * 32 + 20
            actual_files[name] = {"offset_original": original["offset"],
                                  "offset_nuevo": offset,
                                  "size_original": original["size_stored"],
                                  "size_nuevo": len(stored)}
            pos = target.tell()
            target.seek(table_at)
            target.write(struct.pack("<III", expanded, len(stored), offset))
            target.seek(pos)

        # ISO9660 volume space is sector-addressed: the image must also end
        # at an actual 2048-byte boundary, not merely PSPFS's 512-byte boundary.
        new_size = align(append_offset, 2048) if append_offset > original_total - extent else old_size
        require(new_size < 2**32, "DATA.DAT length exceeds ISO9660 32-bit field")
        target.seek(record_at + 10)
        target.write(struct.pack("<I", new_size))
        target.write(struct.pack(">I", new_size))
        target.seek(2048 * 16 + 80)
        sectors = align(extent + new_size, 2048) // 2048
        target.write(struct.pack("<I", sectors))
        target.write(struct.pack(">I", sectors))
        target.truncate(extent + new_size)

    # Independently check index and immutable neighboring assets.
    _, final_pack, final_entries = read_resources(result_iso)
    require(len(final_entries) == len(entries), "PSPFS entry count changed")
    changed_count = 0
    for old, new in zip(entries, final_entries):
        require(old["name"] == new["name"] and old["index"] == new["index"],
                "PSPFS file order changed")
        if old["name"] in replacements:
            changed_count += 1
            stored_expected, expanded_expected = replacements[old["name"]]
            info = actual_files[old["name"]]
            require(new["offset"] == info["offset_nuevo"] and
                    new["size_stored"] == len(stored_expected) and
                    new["size_expanded"] == expanded_expected,
                    "Textual PSPFS record does not identify the appended payload")
            require(final_pack[new["offset"]:new["offset"] + new["size_stored"]] ==
                    stored_expected,
                    "Textual PSPFS stored bytes changed after insertion")
            decoded, codec = decompress(stored_expected, expanded_expected)
            if expanded_expected:
                require(codec.startswith("IMY") and len(decoded) == expanded_expected,
                        "Text archive lost original IMY encoding")
            else:
                require(codec == "sin_comprimir",
                        "Unexpected text/PNG archive codec")
            continue
        require(old == new, f"Unrelated PSPFS index/position changed: {old['name']}")
        offset = old["offset"]
        length = old["size_stored"]
        require(source_pack[offset:offset + length] == final_pack[offset:offset + length],
                f"Unrelated asset changed (portrait, tile, etc.): {old['name']}")
    require(changed_count == len(replacements), "A requested archive was not inserted")

    source_iso_files = iso9660_entries(source_iso)[1]
    final_iso_files = iso9660_entries(result_iso)[1]
    require(len(source_iso_files) == len(final_iso_files), "ISO9660 file count changed")
    for a, b in zip(source_iso_files, final_iso_files):
        require(a["path"] == b["path"] and a["offset"] == b["offset"],
                "Unrelated ISO file offset changed")
        if a["path"] == "PSP_GAME/USRDIR/DATA.DAT":
            continue
        require(a["size"] == b["size"], f"ISO asset length changed: {a['path']}")
        before = read_iso_file(source_iso, a)
        after = read_iso_file(result_iso, b)
        if a["path"] == "PSP_GAME/USRDIR":
            # The only permitted directory modification is the DATA.DAT
            # child record's two 32-bit size fields (LE+BE).
            relative = record_at - a["offset"]
            require(0 <= relative and relative + 18 <= len(before) and
                    before[:relative + 10] == after[:relative + 10] and
                    before[relative + 18:] == after[relative + 18:],
                    "USRDIR modified outside DATA.DAT size fields")
        else:
            require(before == after,
                    f"Unrelated ISO file content changed: {a['path']}")
    return actual_files


def build(source_iso, candidate, report, *, source_csv=SOURCE, draft_csv=DRAFT,
          experimental_partial=False, add_spanish_font=True, event_safe_only=False,
          verified_packs=False, unified_profile=False, extended_padding=False, verified_symbols=False, concise_verified=False, r39_verified=False, r40_verified=False, r42_verified=False, r43_verified=False, r44_local_experimental=False, r52_local_optimized=False, corrective_ui=False):
    source_iso, candidate, report = map(Path, (source_iso, candidate, report))
    require(source_iso.resolve() != candidate.resolve(), "Cannot overwrite source ISO")
    require(sha256_file(source_iso) == SOURCE_SHA256, "Wrong Cladun USA source ISO")
    require(not (r44_local_experimental and r52_local_optimized),"Choose exactly one local relocation profile")
    require(not corrective_ui or (r52_local_optimized and unified_profile and Path(source_csv).resolve()==Path(SOURCE).resolve() and Path(draft_csv).resolve()==Path(DRAFT).resolve()), "Corrective UI requires canonical R52")
    r44_local_experimental = r44_local_experimental or r52_local_optimized
    require(not r44_local_experimental or (r43_verified and experimental_partial and event_safe_only),
            "R44 requires explicit local relocation experiment and R43 base")
    require(not r43_verified or r42_verified,"R43 requires R42 profile")
    require(not r42_verified or r40_verified,"R42 requires R40 profile")
    require(not r40_verified or r39_verified,"R40 requires R39 profile")
    require(not r39_verified or concise_verified,"R39 requires prior concise profile")
    require(not concise_verified or verified_symbols,"Concise profile requires verified symbols")
    require(not verified_symbols or extended_padding,"Verified symbols require extended profile")
    require(not extended_padding or unified_profile,"Extended padding requires unified profile")
    if unified_profile:
        require(verified_packs and event_safe_only and experimental_partial and add_spanish_font,
                "Unified profile requires verified packs, fixed offsets, font and explicit partial mode")
        try:
            from tools.f4_r23_font_compact_candidate import candidate_path
        except ModuleNotFoundError:
            from f4_r23_font_compact_candidate import candidate_path
        candidate = candidate_path(candidate, source_iso)
        require(report.resolve() not in (source_iso.resolve(),candidate.resolve(),
                                        Path(source_csv).resolve(),Path(draft_csv).resolve())
                and not report.exists() and not report.is_symlink(),
                "Unified report must be a new file, never overwrite inputs or candidate")
    rows = source_rows(source_csv, draft_csv)
    layout_f1 = None
    # El borrador completo es literario. Ajustar solo la presentación
    # verificada al compilar su versión canónica, no ensayos --borrador.
    if Path(source_csv).resolve() == Path(SOURCE).resolve() and Path(draft_csv).resolve() == Path(DRAFT).resolve():
        rows, layout_f1 = patch_canonical_menu_layout(rows)
        rows, values_f1 = patch_canonical_menu_values(rows)
        layout_f1["onoff_presentacion"] = values_f1
    corrective_log = None
    if corrective_ui:
        from tools.qa_corrective_r52 import save_overlay
        rows, corrective_log = save_overlay(rows)
    changes, blocked, unchanged = plan_rows(rows)
    event_deferred = []
    accumulated = None
    if verified_packs:
        require(event_safe_only and experimental_partial and add_spanish_font
                and Path(source_csv).resolve() == Path(SOURCE).resolve()
                and Path(draft_csv).resolve() == Path(DRAFT).resolve(),
                "Verified packs require canonical corpus, font, fixed offsets and experimental partial mode")
    if event_safe_only:
        changes, blocked, event_deferred, accumulated = plan_event_safe(
            changes, blocked, verified_packs=verified_packs)
    if unified_profile:
        changes, blocked, event_deferred, accumulated = combine_unified_profile(
            changes, blocked, event_deferred, accumulated, draft_csv=draft_csv)
    if extended_padding:
        changes,blocked,event_deferred,accumulated=combine_extended_padding(
            changes,blocked,event_deferred,accumulated,draft_csv=draft_csv)
    if verified_symbols:
        changes,blocked,event_deferred,accumulated=combine_verified_symbols(
            changes,blocked,event_deferred,accumulated,draft_csv=draft_csv)
    if concise_verified:
        changes,blocked,event_deferred,accumulated=combine_reviewed_concise(
            changes,blocked,event_deferred,accumulated,draft_csv=draft_csv)
    if r39_verified:
        changes,blocked,event_deferred,accumulated=combine_r39_concise(
            changes,blocked,event_deferred,accumulated,draft_csv=draft_csv)
    if r40_verified:
        changes,blocked,event_deferred,accumulated=combine_r40_concise(
            changes,blocked,event_deferred,accumulated,draft_csv=draft_csv)
    if r42_verified:
        changes,blocked,event_deferred,accumulated=combine_r42_concise(
            changes,blocked,event_deferred,accumulated,draft_csv=draft_csv)
    if r43_verified:
        changes,blocked,event_deferred,accumulated=combine_r43_concise(
            changes,blocked,event_deferred,accumulated,draft_csv=draft_csv)
        unchanged += 1
    if r44_local_experimental:
        changes,blocked,event_deferred,accumulated=combine_r44_local_experimental(
            changes,blocked,event_deferred,accumulated,draft_csv=draft_csv,optimized=r52_local_optimized)
    all_changed = sum(len(x) for x in changes.values())
    counted = Counter(x["motivo"] for x in blocked)
    result = {"estado": "BLOQUEADO_SIN_CANDIDATO", "original_sha256": SOURCE_SHA256,
              "total": len(rows), "cambios_admisibles_para_ensayo": all_changed,
              "sin_cambio_de_bytes": unchanged,
              "bloqueos": dict(counted),
              "bloqueos_por_grupo": blocked,
              "modo_completo": not experimental_partial,
              "modo_eventos_offsets_fijos": event_safe_only and not r44_local_experimental,
              "reubicacion_local_experimental": r44_local_experimental,
              "perfil_reubicacion_local": "R52" if r52_local_optimized else "R44" if r44_local_experimental else None,
              "dialogos_pospuestos_por_desplazamiento": len(event_deferred),
              "ppsspp_validado": False, "aprobado_para_distribucion": False,
              "f1_presentacion_menu": layout_f1,
              "corrective_ui_experimental": corrective_log,
              "perfil_conservador_acumulado": accumulated}
    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if blocked and not experimental_partial:
        raise ValueError("Se bloquea inserción TOTAL: hay entradas sin capacidad o sin texto. "
                         "Reporte escrito. Use --experimental-parcial solo si acepta no traducirlas.")
    require(all_changed > 0, "No changes to apply")
    with tempfile.TemporaryDirectory(prefix="cladun_protegido_") as tmp:
        interim = Path(tmp) / "fuente-privada.iso"
        if add_spanish_font:
            build_font(source_iso, interim)
            verify_font(source_iso, interim)
            base = interim
            if unified_profile:
                try:
                    from tools.f4_r21_ligature_collision_safe import verify_own_iso_raster
                    from tools.f4_r21_ligature_font_prototype import build_in_memory
                    from tools.f4_r24_piloto_1650_ligaduras import update_font_in_existing_candidate
                except ModuleNotFoundError:
                    from f4_r21_ligature_collision_safe import verify_own_iso_raster
                    from f4_r21_ligature_font_prototype import build_in_memory
                    from f4_r24_piloto_1650_ligaduras import update_font_in_existing_candidate
                result["auditoria_raster_original"] = verify_own_iso_raster(source_iso)
                compact, metric = build_in_memory(source_iso, Path(draft_csv),
                    ligature_count=44, member_alignment=16, include_binary=True, white_new_ink=corrective_ui)
                require((len(compact)==144000 or corrective_ui) and metric["preserved_original_base_glyphs"]==2721
                        and metric["preserved_existing_spanish_glyphs"]==19
                        and metric["ligature_count"]==44
                        and metric["can_write_in_original_slot_without_relocation"],
                        "R36 compact font geometry drift")
                base = Path(tmp) / "fuente-unificada.iso"
                result["auditoria_fuente_unificada"] = update_font_in_existing_candidate(
                    source_iso, interim, base, compact)
                result["fuente_unificada"] = metric
        else:
            base = source_iso
        _, package, entries = read_resources(base)
        table = {e["name"]: e for e in entries}
        replacements = {}
        applied = set()
        event_audit = None
        if TARGET_SCRIPT in changes:
            stored, raw, method = parent_content(package, table["SCRIPT.SDT"])
            require(method.startswith("IMY"), "SCRIPT.SDT compression format changed")
            script_changes = {}
            for src, old, new in changes[TARGET_SCRIPT]:
                at = int(src["offset_hex"], 16)
                require(at not in script_changes, "Duplicate SCRIPT.DAT text offset")
                script_changes[at] = (old, new, src["grupo_id"])
            event_audit = {}
            if unified_profile:
                # Single replay against the original archive; preserve DSARC geometry.
                try:
                    from tools.f4_r24_piloto_1650_ligaduras import replace_member_payload
                    from tools.r32_auditar_packs import selective_repack
                except ModuleNotFoundError:
                    from f4_r24_piloto_1650_ligaduras import replace_member_payload
                    from r32_auditar_packs import selective_repack
                members = dsarc_entries(raw)
                by_name = {m["name"]:m for m in members}
                def child(name):
                    m=by_name[name]
                    return raw[m["offset"]:m["offset"]+m["size"]]
                original_script, original_table = child("SCRIPT.DAT"), child("SCRIPT.TBL")
                if r44_local_experimental:
                    try:
                        from tools.r44_local_experimental import rebuild
                    except ModuleNotFoundError:
                        from r44_local_experimental import rebuild
                    if r52_local_optimized:
                        from tools.r52_local_optimized import rebuild
                    new_script,new_table,event_audit=rebuild(original_script,original_table,script_changes)
                else:
                    new_script,new_table = text_command_rebuild(original_script,original_table,script_changes)
                    event_audit = audit_script_rebuild(original_script,original_table,
                        new_script,new_table,script_changes,require_fixed_offsets=True)
                require(new_table==original_table,"R36 SCRIPT.TBL differs")
                rewritten = replace_member_payload(raw,members,"SCRIPT.DAT",new_script)
                packed, count = selective_repack(stored,rewritten)
                result["script_imy_repacked_blocks"] = count
            else:
                rewritten = rebuild_script_arc(
                    raw, script_changes, event_report=event_audit,
                    strict_event_offsets=event_safe_only)
                packed = recompress(stored, rewritten)
            if verified_packs:
                require((event_audit["all_command_offsets_preserved"] if not r44_local_experimental
                         else event_audit["moved_script_starts"]==0 and event_audit["moved_command_offsets"]==(146 if r52_local_optimized else 2712))
                        and event_audit["nontext_commands_byte_exact"] == 46308
                        and event_audit["text_commands_replaced"] == (4899 if r44_local_experimental else 4866 if r43_verified else 4861 if r42_verified else 4840 if r40_verified else 4348 if r39_verified else 4172 if concise_verified else 4073 if verified_symbols else 4020 if extended_padding else 3745 if unified_profile else 1824),
                        "Accumulated SCRIPT failed physical event audit")
            replacements["SCRIPT.SDT"] = (packed, len(rewritten))
            applied.update(a["grupo_id"] for a, old, new in changes[TARGET_SCRIPT])

        db_changes = {k.split("/", 1)[1]: records for k, records in changes.items()
                      if k.startswith("DATABASE.DAT/")}
        if db_changes:
            stored, raw, method = parent_content(package, table[TARGET_DB])
            require(method.startswith("IMY"), "DATABASE.DAT compression format changed")
            rewritten, seen = rebuild_database_arc(raw, db_changes)
            replacements[TARGET_DB] = (recompress(stored, rewritten), len(rewritten))
            applied.update(seen)
        if TARGET_CREDITS in changes:
            stored, raw, method = parent_content(package, table[TARGET_CREDITS])
            require(method == "sin_comprimir", "Credit compression unexpectedly changed")
            rewritten = rebuild_credits(raw, changes[TARGET_CREDITS])
            replacements[TARGET_CREDITS] = (rewritten, 0)
            applied.update(a["grupo_id"] for a, old, new in changes[TARGET_CREDITS])
        graphic_changes = {
            k.split("/", 1)[1]: records for k, records in changes.items()
            if k.startswith("SYS.DAT2/")
        }
        graphic_audits = []
        if graphic_changes:
            stored, raw, method = parent_content(package, table[TARGET_SYS])
            require(method == "sin_comprimir", "SYS.DAT2 has unexpected compression")
            entry = table[TARGET_SYS]
            next_start = min(x["offset"] for x in entries if x["offset"] > entry["offset"])
            capacity = next_start - entry["offset"]
            new_graphics, IDs, graphic_audits = rebuild_sys_arc_compact(
                raw, graphic_changes, capacity)
            replacements[TARGET_SYS] = (new_graphics, 0)
            applied.update(IDs)

        require(len(applied) == all_changed, "Some admissible entries were not applied")
        require(not candidate.exists(), "Candidate path already exists: never overwrite")
        candidate.parent.mkdir(parents=True, exist_ok=True)
        fd, staged_path = tempfile.mkstemp(
            prefix=".cladun_verificando_", suffix=".iso.tmp", dir=candidate.parent)
        os.close(fd)
        staged = Path(staged_path)
        try:
            metadata = append_text_containers(
                base, package, entries, replacements, staged,
                inplace_resources=frozenset({TARGET_SYS} & replacements.keys()))
            candidate_hash = sha256_file(staged)
            require(sha256_file(source_iso) == SOURCE_SHA256,
                    "Original ISO changed while generating the patch")
            # Atomic publish: hard link fails rather than overwriting an existing ISO.
            os.link(staged, candidate)
        finally:
            staged.unlink(missing_ok=True)
        result.update({"estado": "EXPERIMENTAL_AISLAMIENTO_BINARIO_SOLAMENTE",
                       "iso_resultante_sha256": candidate_hash,
                       "texto_aplicado": len(applied),
                       "recurso_textual_reubicado_append_only": metadata,
                       "recursos_no_textuales_mismo_offset_y_mismos_bytes": 349 - len(replacements),
                       "fuente_es_prototipo": add_spanish_font,
                       "graficos_textuales_verificados": graphic_audits,
                       "todos_los_textos_insertados": len(blocked) == 0,
                       "auditoria_eventos": event_audit,
                       "control_logico_no_textual_intacto": bool(event_audit and
                           event_audit["nontext_payload_changes"] == 0 and
                           event_audit["opcode_instruction_id_order_changes"] == 0),
                       "offsets_de_comandos_preservados": bool(event_audit and
                           event_audit["all_command_offsets_preserved"])})
        report.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n",
                          encoding="utf-8")
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--iso", type=Path, required=True, help="ISO USA original privada")
    p.add_argument("--candidate", type=Path, required=True,
                   help="ISO candidate PRIVATE, never commit or distribute")
    p.add_argument("--report", type=Path, required=True, help="JSON without assets")
    p.add_argument("--original", type=Path, default=SOURCE)
    p.add_argument("--borrador", type=Path, default=DRAFT)
    p.add_argument("--experimental-parcial", action="store_true",
                   help="Allow candidate with unhandled text (never claim full translation)")
    p.add_argument("--sin-fuente", action="store_true", help="Developer-only, no Spanish glyphs")
    p.add_argument("--event-safe-only", action="store_true",
                   help="Conservar absolutamente todos los offsets de comandos; pospone textos de longitud diferente")
    p.add_argument("--packs-verificados", action="store_true",
                   help="Integrar 146 exactos + 1302 acolchados en la base conservadora; experimental, sin QA PPSSPP")
    p.add_argument("--perfil-unificado", action="store_true",
                   help="7093 textos, fuente compacta experimental 44 ligaduras; implica los modos parciales y offsets fijos. NO es release.")
    p.add_argument("--relleno-ampliado", action="store_true",
                   help="Con --perfil-unificado añade 275 textos con 8–31 espacios; riesgo visual sin PPSSPP.")
    p.add_argument("--residuales-verificados", action="store_true",
                   help="Con --perfil-unificado añade 275 rellenos y 53 textos CP932 verificados estáticamente; experimental.")
    p.add_argument("--perfil-acumulado", action="store_true",
                   help="Lotes R43: 8214 sustituciones, 1 registro resuelto sin cambios, 33 pendientes; experimental. No release.")
    p.add_argument("--perfil-total-local-experimental",action="store_true",
                   help="8247 substitutions + 1 unchanged; MOVES 2712 commands; private diagnostic only.")
    p.add_argument("--perfil-total-local-optimizado",action="store_true",
                   help="R52: 8247 substitutions + 1 unchanged, 146 moved commands; private diagnostic only.")
    p.add_argument("--acepto-reubicacion-local",action="store_true",
                   help="Acknowledge unverified event references; no BPS export.")
    args = p.parse_args()
    if args.perfil_total_local_experimental and args.perfil_total_local_optimizado:
        p.error("Choose only one local relocation profile")
    if args.perfil_total_local_experimental or args.perfil_total_local_optimizado:
        if not args.acepto_reubicacion_local or args.event_safe_only:
            p.error("R44 requires explicit local-relocation acceptance and cannot be event-safe-only")
        args.perfil_acumulado=True
    elif args.acepto_reubicacion_local:
        p.error("Risk flag requires the R44 experimental profile")
    try:
        summary = build(args.iso, args.candidate, args.report,
                        source_csv=args.original, draft_csv=args.borrador,
                        experimental_partial=args.experimental_parcial or args.perfil_unificado or args.perfil_acumulado,
                        add_spanish_font=not args.sin_fuente,
                        event_safe_only=args.event_safe_only or args.perfil_unificado or args.perfil_acumulado,
                        verified_packs=args.packs_verificados or args.perfil_unificado or args.perfil_acumulado,
                        unified_profile=args.perfil_unificado or args.perfil_acumulado,
                        extended_padding=args.relleno_ampliado or args.residuales_verificados or args.perfil_acumulado,
                        verified_symbols=args.residuales_verificados or args.perfil_acumulado,
                        concise_verified=args.perfil_acumulado,
                        r39_verified=args.perfil_acumulado,
                        r40_verified=args.perfil_acumulado,
                        r42_verified=args.perfil_acumulado,
                        r43_verified=args.perfil_acumulado,
                        r44_local_experimental=args.perfil_total_local_experimental,
                        r52_local_optimized=args.perfil_total_local_optimizado)
        print(json.dumps({k: v for k, v in summary.items() if k != "bloqueos_por_grupo"},
                         indent=2, ensure_ascii=False))
    except Exception as exc:
        print(f"RECHAZADO: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
