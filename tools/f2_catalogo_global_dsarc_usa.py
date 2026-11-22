#!/usr/bin/env python3
"""F2 metadata-only independent audit of ALL four original DSARC containers.

An exact USA ISO SHA256 is required. Does not decode textures, export
commercial payloads or establish runtime resource usage/VRAM provenance.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

try:
    from tools.f2_auditar_origen_iconos import (
        ISO_SHA256, locate_data, pspfs_entries, dsarc_entries,
    )
    from tools.f2_inventario_sysgra_usa import source_hash
except ModuleNotFoundError:
    from f2_auditar_origen_iconos import (
        ISO_SHA256, locate_data, pspfs_entries, dsarc_entries,
    )
    from f2_inventario_sysgra_usa import source_hash

EXPECTED_ISO_SIZE = 305496064
EXPECTED_ARCHIVES = {
    0: ("SYS.DAT2", 6),
    188: ("SE.ARC", 68),
    225: ("SYSGRA.ARC", 27),
    308: ("FONT.ARC", 7),
}
FONT_IN_SYSGRA_SHA = "50143c165f10aa71ac77d4a2b09fd69012b1eceac4a102bf8e2b8157bf8b5915"
FONT_ATLAS_00_SHA = "698bc5b398a16c3f2a4615527dac6a36dbae73666a7c45c3787bb00a728a8478"

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def classify_header(name: str, payload: bytes) -> str:
    """Checks only a signature, not the full codec or decoded image."""
    if name.endswith(".PNG"):
        if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
            raise ValueError("PNG member with invalid signature")
        return "PNG_SIGNATURE"
    if name.endswith(".IMY"):
        if not payload.startswith(b"IMY\x00"):
            raise ValueError("IMY member with invalid signature")
        return "IMY_SIGNATURE"
    if name.endswith(".SPS"):
        if not payload.startswith(b"\x01\x00\x00\x00"):
            raise ValueError("SPS member with unexpected signature")
        return "SPS_SIGNATURE_ONLY"
    if name.endswith(".BIN"):
        return "BINARY_UNCLASSIFIED"
    raise ValueError("Unexpected member extension: " + name)

def inspect_container(archive: bytes) -> dict:
    """Validate structural overlap, names, bounds and member magic."""
    items = dsarc_entries(archive)
    count = len(items)
    if archive[:8] == b"DSARC FL":
        table_start = 16
    else:
        table_start = (16 + count * 2 + 3) // 4 * 4
    table_end = table_start + 48 * count
    if len({r["name"] for r in items}) != count:
        raise ValueError("Duplicate DSARC member name")
    spans = []
    rows = []
    for r in items:
        start, size = r["offset"], r["size"]
        end = start + size
        if size <= 0 or start < table_end or end > len(archive):
            raise ValueError("Invalid DSARC member offset/size")
        member = archive[start:end]
        fmt = classify_header(r["name"], member)
        rows.append({
            "index": r["index"], "name": r["name"],
            "offset": start, "length": size,
            "signature_kind": fmt, "sha256": sha256(member),
            "ppsspp_runtime_use_proven": False,
        })
        spans.append((start, end))
    spans.sort()
    if any(prev_end > cur_start for (_, prev_end), (cur_start, _) in zip(spans, spans[1:])):
        raise ValueError("DSARC members overlap")
    return {"container_magic": archive[:8].decode("ascii"),
            "members_count": count, "members": rows}

def audit(iso: Path) -> dict:
    iso = Path(iso)
    if iso.stat().st_size != EXPECTED_ISO_SIZE:
        raise ValueError("Wrong ISO size")
    digest = source_hash(iso)
    if digest != ISO_SHA256:
        raise ValueError("Original USA ISO SHA256 mismatch")
    rec = locate_data(iso)
    with iso.open("rb") as f:
        f.seek(rec["offset"])
        data = f.read(rec["size"])
    if len(data) != rec["size"]:
        raise ValueError("DATA.DAT truncated")
    entries = pspfs_entries(data)
    if len(entries) != 349:
        raise ValueError("Unexpected PSPFS member count")
    found = {}
    all_hashes = []
    font_provenance = {}
    for i, ent in enumerate(entries):
        at, size = ent["offset"], ent["size_stored"]
        if at + size > len(data):
            raise ValueError("PSPFS range exceeds DATA.DAT")
        if data[at:at + 8] not in (b"DSARC FL", b"DSARCIDX"):
            continue
        if i not in EXPECTED_ARCHIVES:
            raise ValueError("Unexpected extra DSARC at PSPFS index %d" % i)
        expected_name, expected_count = EXPECTED_ARCHIVES[i]
        if ent["name"] != expected_name:
            raise ValueError("DSARC PSPFS name mismatch")
        raw = data[at:at + size]
        parsed = inspect_container(raw)
        if parsed["members_count"] != expected_count:
            raise ValueError("DSARC count mismatch for " + expected_name)
        found[i] = {
            "pspfs_index": i, "name": expected_name, "stored_size": size,
            "sha256": sha256(raw), "container_magic": parsed["container_magic"],
            "members_count": parsed["members_count"],
            "members": parsed["members"],
        }
        for member in parsed["members"]:
            all_hashes.append(member["sha256"])
            if (expected_name, member["name"]) in (
                ("SYSGRA.ARC", "FONT.IMY"), ("FONT.ARC", "FONT_00.IMY")
            ):
                font_provenance[expected_name + "/" + member["name"]] = member["sha256"]
    if set(found) != set(EXPECTED_ARCHIVES):
        raise ValueError("Expected exactly four DSARC containers")
    if font_provenance.get("SYSGRA.ARC/FONT.IMY") != FONT_IN_SYSGRA_SHA:
        raise ValueError("SYSGRA.ARC/FONT.IMY signature mismatch")
    if font_provenance.get("FONT.ARC/FONT_00.IMY") != FONT_ATLAS_00_SHA:
        raise ValueError("FONT.ARC/FONT_00.IMY signature mismatch")
    if len(all_hashes) != 108 or len(set(all_hashes)) != 108:
        raise ValueError("Unexpected duplicate or missing DSARC members")
    return {
        "schema": "cladun.f2.dsarc_all_metadata_readonly.v1",
        "source_kind": "REAL_ORIGINAL_ISO_STATIC_ONLY",
        "original_iso_sha256": digest,
        "original_iso_bytes": iso.stat().st_size,
        "pspfs_members_total": len(entries),
        "dsarc_containers_count": len(found),
        "dsarc_members_total": len(all_hashes),
        "unique_compressed_member_hashes": len(set(all_hashes)),
        "font_assets_are_distinct_stored_bytes": True,
        "font_assets_provenance": font_provenance,
        "font_assets_rendered_at_runtime": "NOT_PROVEN",
        "hud_combat_icon_runtime_origin": "NOT_PROVEN",
        "ram_ge_vram_proven": False,
        "containers": [found[i] for i in sorted(found)],
    }

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--iso-usa", type=Path, required=True)
    ap.add_argument("--reporte", type=Path, required=True)
    args = ap.parse_args()
    result = audit(args.iso_usa)
    args.reporte.parent.mkdir(parents=True, exist_ok=True)
    with args.reporte.open("x", encoding="utf-8") as fp:
        json.dump(result, fp, indent=2, ensure_ascii=False)
        fp.write("\n")
    print(json.dumps({
        "schema": result["schema"],
        "container_count": result["dsarc_containers_count"],
        "member_count": result["dsarc_members_total"],
        "font_resources_distinct": True, "runtime_proven": False,
    }, ensure_ascii=False))

if __name__ == "__main__":
    main()
