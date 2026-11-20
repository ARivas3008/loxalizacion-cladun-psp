#!/usr/bin/env python3
"""Generate a PRIVATE experimental BPS delta against a legally owned Cladun ISO.

BPS1 spec: source-read / target-read actions only. The patch contains only
differences and copy instructions; the commercial ISO is NEVER distributed.

The CLI intentionally requires the complete fail-closed integrator's audit
report, matching hashes and --experimental. It verifies the produced patch by
applying it to the original and comparing the result against the candidate
SHA-256, before atomically making the BPS file visible.

This is NOT a declaration of PPSSPP runtime compatibility or patch readiness.
"""
from __future__ import annotations

import argparse
import binascii
import hashlib
import json
import os
from pathlib import Path
import struct
import tempfile

from font_es_patch import SOURCE_SHA256
from integrar_parche_seguro import read_resources, iso9660_entries, read_iso_file, locate_iso_dir_record

MAGIC = b"BPS1"
SOURCE_READ = 0
TARGET_READ = 1
BLOCK = 65536
TEXT_CONTAINERS = {"SCRIPT.SDT", "DATABASE.DAT", "STAFFROLL.TXT", "SYS.DAT2", "FONT.ARC"}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def encode_number(value: int) -> bytes:
    require(isinstance(value, int) and value >= 0, "BPS number must be nonnegative")
    output = bytearray()
    while True:
        out = value & 0x7F
        value >>= 7
        if value == 0:
            output.append(out | 0x80)
            return bytes(output)
        output.append(out)
        value -= 1


def decode_number(blob: bytes, at: int) -> tuple[int, int]:
    value, shift = 0, 1
    while True:
        require(at < len(blob), "Truncated BPS number")
        chunk = blob[at]
        at += 1
        value += (chunk & 0x7F) * shift
        if chunk & 0x80:
            return value, at
        shift <<= 7
        value += shift
        require(shift < 2**70, "BPS number exceeds supported size")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as inp:
        for part in iter(lambda: inp.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def file_crc32(path: Path) -> int:
    crc = 0
    with path.open("rb") as inp:
        for part in iter(lambda: inp.read(1024 * 1024), b""):
            crc = binascii.crc32(part, crc)
    return crc & 0xFFFFFFFF


def build_bps(source: Path, target: Path, patch: Path) -> dict:
    """Create interoperable BPS1 without copying the original whole ISO."""
    source, target, patch = Path(source), Path(target), Path(patch)
    require(source.resolve() != target.resolve(), "Source/target paths identical")
    require(patch.resolve() not in (source.resolve(), target.resolve()),
            "Patch path must differ from both game files")
    source_size, target_size = source.stat().st_size, target.stat().st_size
    require(source_size and target_size, "Empty source or target")
    require(not patch.exists(), "Never overwrite a BPS patch")
    copy_count, literal_count = 0, 0
    with source.open("rb") as original, target.open("rb") as candidate, patch.open("xb") as output:
        output.write(MAGIC)
        output.write(encode_number(source_size))
        output.write(encode_number(target_size))
        output.write(encode_number(0))  # no proprietary metadata
        kind, pending = None, 0
        literal = bytearray()

        def flush():
            nonlocal kind, pending, literal, copy_count, literal_count
            if pending == 0:
                return
            output.write(encode_number(((pending - 1) << 2) | kind))
            if kind == TARGET_READ:
                require(len(literal) == pending, "BPS literal group mismatch")
                output.write(literal)
                literal_count += pending
                literal = bytearray()
            else:
                copy_count += pending
            pending = 0
            kind = None

        def consume(action, part):
            nonlocal kind, pending, literal
            if not part:
                return
            if kind is not None and kind != action:
                flush()
            kind = action
            pending += len(part)
            if action == TARGET_READ:
                literal.extend(part)

        while True:
            current = candidate.read(BLOCK)
            if not current:
                break
            before = original.read(len(current))
            if before == current:
                consume(SOURCE_READ, current)
            elif before and len(before) < len(current) and current.startswith(before):
                # An appended text archive may begin after the end of the
                # original ISO in the middle of a block. Copy its unchanged
                # prefix rather than unnecessarily embedding it as literal.
                consume(SOURCE_READ, before)
                consume(TARGET_READ, current[len(before):])
            else:
                consume(TARGET_READ, current)
        flush()
        require(copy_count + literal_count == target_size, "Patch omits target bytes")
        output.write(struct.pack("<II", file_crc32(source), file_crc32(target)))
    # The final checksum must include every patch byte before its own footer.
    with patch.open("r+b") as output:
        output.seek(0)
        crc = 0
        while chunk := output.read(BLOCK):
            crc = binascii.crc32(chunk, crc)
        output.write(struct.pack("<I", crc & 0xFFFFFFFF))
    return {"source_size": source_size, "target_size": target_size,
            "source_read_bytes": copy_count, "target_literal_bytes": literal_count,
            "bps_size": patch.stat().st_size, "bps_sha256": file_sha256(patch)}


def apply_bps(source: Path, patch: Path, destination: Path) -> None:
    """Independent BPS decoder for our source/target actions with CRC guard."""
    source, patch, destination = map(Path, (source, patch, destination))
    require(not destination.exists(), "Refusing to overwrite reconstructed ISO")
    raw = patch.read_bytes()
    require(len(raw) >= 4 + 3 + 12 and raw[:4] == MAGIC, "Not BPS1")
    patch_end = len(raw) - 12
    src_crc, tgt_crc, patch_crc = struct.unpack_from("<III", raw, patch_end)
    require((binascii.crc32(raw[:len(raw) - 4]) & 0xFFFFFFFF) == patch_crc,
            "BPS patch checksum mismatch")
    require(file_crc32(source) == src_crc, "BPS source ISO checksum mismatch")
    at = 4
    source_size, at = decode_number(raw, at)
    target_size, at = decode_number(raw, at)
    meta_length, at = decode_number(raw, at)
    require(at + meta_length <= patch_end, "BPS metadata truncated")
    at += meta_length
    require(source.stat().st_size == source_size, "BPS source ISO size mismatch")
    produced = 0
    with source.open("rb") as original, destination.open("xb") as out:
        while produced < target_size:
            require(at < patch_end, "BPS command stream truncated")
            instruction, at = decode_number(raw, at)
            action, count = instruction & 3, (instruction >> 2) + 1
            require(count <= target_size - produced, "BPS action exceeds target size")
            if action == SOURCE_READ:
                original.seek(produced)
                # Read in chunks so a huge source copy never allocates an ISO-sized buffer.
                left = count
                while left:
                    chunk = original.read(min(left, BLOCK))
                    require(chunk, "BPS source read past EOF")
                    out.write(chunk)
                    left -= len(chunk)
            elif action == TARGET_READ:
                require(at + count <= patch_end, "BPS literal truncated")
                out.write(raw[at:at + count])
                at += count
            else:
                raise ValueError("Unexpected BPS source-copy/target-copy action")
            produced += count
        require(at == patch_end, "Unexpected extra BPS command bytes")
    require(file_crc32(destination) == tgt_crc, "BPS reconstructed ISO checksum mismatch")


def assert_unrelated_assets_exact(source: Path, target: Path) -> None:
    """Independent check before exporting a patch: no PSPFS neighbor may differ."""
    src_iso_record, src_pack, src_entries = read_resources(source)
    dst_iso_record, dst_pack, dst_entries = read_resources(target)
    require(len(src_entries) == len(dst_entries) == 349,
            "PSPFS resource count changed")
    for before, after in zip(src_entries, dst_entries):
        require(before["index"] == after["index"] and
                before["name"] == after["name"], "PSPFS file sequence changed")
        if before["name"] in TEXT_CONTAINERS:
            continue
        require(before == after, "Unrelated PSPFS metadata changed: " + before["name"])
        pos, size = before["offset"], before["size_stored"]
        require(src_pack[pos:pos + size] == dst_pack[pos:pos + size],
                "Unrelated PSPFS resource was changed: " + before["name"])
    orig = iso9660_entries(source)[1]
    dest = iso9660_entries(target)[1]
    require(len(orig) == len(dest), "ISO9660 inventory changed")
    for a, b in zip(orig, dest):
        require(a["path"] == b["path"] and a["offset"] == b["offset"],
                "ISO file position or path changed")
        if a["path"] != "PSP_GAME/USRDIR/DATA.DAT":
            require(a["size"] == b["size"], "ISO asset size changed: " + a["path"])
            before = read_iso_file(source, a)
            after = read_iso_file(target, b)
            if a["path"] == "PSP_GAME/USRDIR":
                record_at, _, _ = locate_iso_dir_record(source)
                relative = record_at - a["offset"]
                require(0 <= relative and relative + 18 <= len(before) and
                        before[:relative + 10] == after[:relative + 10] and
                        before[relative + 18:] == after[relative + 18:],
                        "USRDIR modified outside DATA.DAT size fields")
            else:
                require(before == after, "ISO non-DATA file changed: " + a["path"])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", required=True, type=Path)
    parser.add_argument("--candidato", required=True, type=Path)
    parser.add_argument("--informe-integracion", required=True, type=Path)
    parser.add_argument("--salida", required=True, type=Path)
    parser.add_argument("--informe-bps", required=True, type=Path)
    parser.add_argument("--experimental", action="store_true",
                        help="Mandatory acknowledgment: NOT a tested final release")
    args = parser.parse_args()
    require(args.experimental, "BPS release is blocked without --experimental")
    require(args.salida.resolve() not in (args.original.resolve(), args.candidato.resolve(),
                                          args.informe_bps.resolve()),
            "Unsafe path overlap")
    require(args.informe_bps.resolve() != args.candidato.resolve(),
            "Report cannot overwrite a game file")
    require(not args.salida.exists() and not args.informe_bps.exists(),
            "Refusing to overwrite patch or report")
    require(file_sha256(args.original) == SOURCE_SHA256,
            "Original ISO SHA-256 mismatch")
    report = json.loads(args.informe_integracion.read_text(encoding="utf-8"))
    result_hash = file_sha256(args.candidato)
    require(report.get("original_sha256") == SOURCE_SHA256 and
            report.get("iso_resultante_sha256") == result_hash and
            report.get("todos_los_textos_insertados") is True and
            report.get("ppsspp_validado") is False,
            "Candidate does not match the full experimental integration audit")
    assert_unrelated_assets_exact(args.original, args.candidato)
    args.salida.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="cladun_bps_privado_", dir=args.salida.parent) as tmp:
        staged = Path(tmp) / "candidate.bps"
        reconstructed = Path(tmp) / "roundtrip.iso"
        summary = build_bps(args.original, args.candidato, staged)
        apply_bps(args.original, staged, reconstructed)
        require(file_sha256(reconstructed) == result_hash,
                "BPS reconstructed bytes differ from integrated candidate ISO")
        os.link(staged, args.salida)
    output = {
        "status": "BPS_EXPERIMENTAL_RECONSTRUCTION_PASS_NOT_PPSSPP",
        "source_sha256": SOURCE_SHA256, "candidate_sha256": result_hash,
        "bps_roundtrip_identical": True, "outside_text_assets_verified": True,
        "gameplay_ppsspp_verified": False, "approved_for_distribution": False,
        **summary,
    }
    args.informe_bps.parent.mkdir(parents=True, exist_ok=True)
    args.informe_bps.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n",
                                encoding="utf-8")
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
