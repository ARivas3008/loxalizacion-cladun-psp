#!/usr/bin/env python3
"""F3: auditor SOLO LECTURA de sonda privada ANIME000 usada en PPSSPP REAL.

Una diferencia en el nombre PSPFS prueba que se cambió una referencia en el
índice, no que el archivo contenga las letras del prólogo. No parchear juego.
Nunca versionar ISO, capturas, dumps o materiales comerciales.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path

SOURCE_SHA = 'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
PROBE_SHA = '576e9699395dd142b666ed3b9d121db5037c63302dc0c4eee862a04ccfcdbb36'
ISO_SIZE = 305496064
DATA_OFFSET = 113770496
PSPFS_INDEX = 234
PSPFS_NAME_OFF = DATA_OFFSET + 16 + 32 * PSPFS_INDEX
SINGLE_CHANGED_BYTE_OFF = PSPFS_NAME_OFF + 9
OLD_NAME, NEW_NAME = b'ANIME000.IDT', b'ANIME000.XDT'


def hash_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def differences_stream(a, b, *, limit: int = 2) -> tuple[list[int], int]:
    """Streaming; only retains up to limit offsets but counts all changed bytes."""
    found = []
    total = offset = 0
    while True:
        left, right = a.read(1024 * 1024), b.read(1024 * 1024)
        if len(left) != len(right):
            raise ValueError('Binary lengths differ')
        if not left:
            break
        if left != right:
            for j, (x, y) in enumerate(zip(left, right)):
                if x != y:
                    total += 1
                    if len(found) < limit:
                        found.append(offset + j)
        offset += len(left)
    return found, total


def inspect_named_entry(stream, offset: int) -> bytes:
    stream.seek(offset)
    name = stream.read(20).split(b'\x00',1)[0]
    if len(name) != 12:
        raise ValueError('Unexpected PSPFS filename length')
    return name


def audit(source: Path, probe: Path) -> dict:
    source, probe = Path(source), Path(probe)
    if source.is_symlink() or probe.is_symlink() or source.resolve() == probe.resolve():
        raise ValueError('Inputs must be separate regular files without symlink')
    if not source.is_file() or not probe.is_file() or source.stat().st_size != ISO_SIZE or probe.stat().st_size != ISO_SIZE:
        raise ValueError('Wrong input ISO size')
    if hash_file(source) != SOURCE_SHA or hash_file(probe) != PROBE_SHA:
        raise ValueError('Hash mismatch, unauthenticated ISO pair')
    with source.open('rb') as a, probe.open('rb') as b:
        a.seek(DATA_OFFSET)
        if a.read(8) != b'PSPFS_V1':
            raise ValueError('Source PSPFS magic missing')
        b.seek(DATA_OFFSET)
        if b.read(8) != b'PSPFS_V1':
            raise ValueError('Probe PSPFS magic missing')
        if inspect_named_entry(a, PSPFS_NAME_OFF) != OLD_NAME:
            raise ValueError('Original PSPFS entry does not match')
        if inspect_named_entry(b, PSPFS_NAME_OFF) != NEW_NAME:
            raise ValueError('Diagnostic PSPFS entry does not match')
        a.seek(SINGLE_CHANGED_BYTE_OFF)
        b.seek(SINGLE_CHANGED_BYTE_OFF)
        if a.read(1) != b'I' or b.read(1) != b'X':
            raise ValueError('Unexpected changed byte')
        a.seek(0)
        b.seek(0)
        offsets,count=differences_stream(a,b)
    if offsets != [SINGLE_CHANGED_BYTE_OFF] or count != 1:
        raise ValueError('Unexpected changes beyond the single PSPFS filename byte')
    return {
        'schema':'cladun.f3.anime000_name_safety_audit.v1',
        'scope':'REAL_ORIGINAL_ISO_PLUS_PRIVATE_PROBE_STATIC_NOT_CAUSAL_TEXT_PROVENANCE',
        'source_iso_sha256':SOURCE_SHA, 'diagnostic_iso_sha256':PROBE_SHA,
        'iso_bytes_each':ISO_SIZE,'pspfs_index':PSPFS_INDEX,
        'filename_change':{'from':'ANIME000.IDT','to':'ANIME000.XDT',
                            'absolute_byte_offset':SINGLE_CHANGED_BYTE_OFF,
                            'old_hex':'49','new_hex':'58'},
        'total_binary_byte_differences':count,
        'source_asset_payload_altered':False,
        'original_iso_altered':False,
        'diagnostic_modification_safe_for_gameplay':False,
        'diagnostic_modification_permitted_in_final_patch':False,
        'actual_prologue_text_source_identified':False,
        'note':'Observed separately in authentic PPSSPP: diagnostic crashes before title; original recovers. It does not prove ANIME000 stores intro lettering.',
    }


def validate_report_path(path: Path, repo_root: Path | None = None) -> Path:
    path=Path(path).expanduser()
    if not path.is_absolute() or path.suffix.lower()!='.json' or path.is_symlink():
        raise ValueError('Absolute new private JSON file required')
    path=path.resolve(strict=False)
    root=(repo_root or Path(__file__).resolve().parents[1]).resolve()
    if path == root or root in path.parents or path.exists() or any((p/'.git').exists() for p in path.parents):
        raise ValueError('Unsafe report output path')
    return path


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iso-original',required=True,type=Path)
    ap.add_argument('--iso-sonda-privada',required=True,type=Path)
    ap.add_argument('--reporte-privado',required=True,type=Path)
    args=ap.parse_args()
    target=validate_report_path(args.reporte_privado)
    meta=audit(args.iso_original,args.iso_sonda_privada)
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('x',encoding='utf-8') as out:
        json.dump(meta,out,ensure_ascii=False,indent=2)
        out.write('\n')
    print(json.dumps({'source_iso_verified':True,'different_bytes':1,
                      'safe_for_release':False,'intro_text_provenance':False}))


if __name__=='__main__':main()
