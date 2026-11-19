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
from pathlib import Path
import shutil
import struct
import tempfile

from auditar_preinsercion_es import SOURCE, DRAFT, IMMUTABLE, check_row, read_csv
from charset_es import encode_spanish, decode_spanish
from extract_cladun import iso9660_entries, read_iso_file, pspfs_entries, dsarc_entries, decompress
from font_es_patch import SOURCE_SHA256, sha256_file, build as build_font
from font_es_guard import verify as verify_font
from imy_repack_safe import recompress
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


def rebuild_script_arc(archive, replacements):
    children = dsarc_entries(archive)
    by_name = {x["name"]: x for x in children}
    require(set(by_name) == {"AISCRIPT.DAT", "AISCRIPT.TBL", "SCRIPT.DAT", "SCRIPT.TBL"},
            "Unexpected SCRIPT.SDT members")
    script = by_name["SCRIPT.DAT"]
    tbl = by_name["SCRIPT.TBL"]
    script_old = archive[script["offset"]:script["offset"] + script["size"]]
    tbl_old = archive[tbl["offset"]:tbl["offset"] + tbl["size"]]
    new_script, new_tbl = text_command_rebuild(script_old, tbl_old, replacements)
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
            require(cap >= len(new) + 1, f"DB overflow: {src['grupo_id']}")
            require(before[offset:offset + len(old)] == old, f"DB byte mismatch: {src['grupo_id']}")
            require(not any(before[offset + len(old):offset + cap]),
                    f"DB field is not NUL-padded: {src['grupo_id']}")
            updated[offset:offset + cap] = new + b"\0" * (cap - len(new))
            prior_end = offset + cap
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
        target.extend(b"\\0" * (position - len(target)))
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
        require(target[record["offset"]:record["offset"] + record["size"]][:8] == b"\\x89PNG\\r\\n\\x1a\\n",
                "Rebuilt PNG resource not recognized")
    return bytes(target), accounted_for, audits


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


def append_text_containers(source_iso, source_pack, entries, replacements, result_iso):
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
        new_size = align(append_offset, 2048)
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
        # Unchanged exact bytes: source and target still share same original file offsets.
        require(read_iso_file(source_iso, a) == read_iso_file(result_iso, b),
                f"Unrelated ISO file content changed: {a['path']}")
    return actual_files


def build(source_iso, candidate, report, *, source_csv=SOURCE, draft_csv=DRAFT,
          experimental_partial=False, add_spanish_font=True):
    source_iso, candidate, report = map(Path, (source_iso, candidate, report))
    require(source_iso.resolve() != candidate.resolve(), "Cannot overwrite source ISO")
    require(sha256_file(source_iso) == SOURCE_SHA256, "Wrong Cladun USA source ISO")
    rows = source_rows(source_csv, draft_csv)
    changes, blocked, unchanged = plan_rows(rows)
    all_changed = sum(len(x) for x in changes.values())
    counted = Counter(x["motivo"] for x in blocked)
    result = {"estado": "BLOQUEADO_SIN_CANDIDATO", "original_sha256": SOURCE_SHA256,
              "total": len(rows), "cambios_admisibles_para_ensayo": all_changed,
              "sin_cambio_de_bytes": unchanged,
              "bloqueos": dict(counted),
              "bloqueos_por_grupo": blocked,
              "modo_completo": not experimental_partial,
              "ppsspp_validado": False, "aprobado_para_distribucion": False}
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
        else:
            base = source_iso
        _, package, entries = read_resources(base)
        table = {e["name"]: e for e in entries}
        replacements = {}
        applied = set()
        if TARGET_SCRIPT in changes:
            stored, raw, method = parent_content(package, table["SCRIPT.SDT"])
            require(method.startswith("IMY"), "SCRIPT.SDT compression format changed")
            script_changes = {}
            for src, old, new in changes[TARGET_SCRIPT]:
                at = int(src["offset_hex"], 16)
                require(at not in script_changes, "Duplicate SCRIPT.DAT text offset")
                script_changes[at] = (old, new, src["grupo_id"])
            rewritten = rebuild_script_arc(raw, script_changes)
            replacements["SCRIPT.SDT"] = (recompress(stored, rewritten), len(rewritten))
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
            new_graphics, IDs, graphic_audits = rebuild_sys_arc(raw, graphic_changes)
            replacements[TARGET_SYS] = (new_graphics, 0)
            applied.update(IDs)

        require(len(applied) == all_changed, "Some admissible entries were not applied")
        require(not candidate.exists(), "Candidate path already exists: never overwrite")
        metadata = append_text_containers(base, package, entries, replacements, candidate)
        result.update({"estado": "EXPERIMENTAL_AISLAMIENTO_BINARIO_SOLAMENTE",
                       "iso_resultante_sha256": sha256_file(candidate),
                       "texto_aplicado": len(applied),
                       "recurso_textual_reubicado_append_only": metadata,
                       "recursos_no_textuales_mismo_offset_y_mismos_bytes": 349 - len(replacements),
                       "fuente_es_prototipo": add_spanish_font,
                       "graficos_textuales_verificados": graphic_audits,
                       "todos_los_textos_insertados": len(blocked) == 0})
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
    args = p.parse_args()
    try:
        summary = build(args.iso, args.candidate, args.report,
                        source_csv=args.original, draft_csv=args.borrador,
                        experimental_partial=args.experimental_parcial,
                        add_spanish_font=not args.sin_fuente)
        print(json.dumps({k: v for k, v in summary.items() if k != "bloqueos_por_grupo"},
                         indent=2, ensure_ascii=False))
    except Exception as exc:
        print(f"RECHAZADO: {exc}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
