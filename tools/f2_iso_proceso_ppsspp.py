#!/usr/bin/env python3
"""F2: auditor de procedencia de una ISO abierta por un proceso PPSSPP Linux.

Solo lectura de /proc. NO demuestra ISO cargada, juego representado, versión,
ni origen MIPS/GE/VRAM. La ausencia de FD tampoco descarta ISO ya cargada.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import stat
from pathlib import Path

SOURCE_SHA = 'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
PROBE_SHA = 'b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa'
ISO_SIZE = 305496064
APPIMAGE_SHA = '661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21'
APPIMAGE_SIZE = 50689748

def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()

def canonical_private_input(path: Path, checkout: Path | None = None) -> Path:
    path = Path(path).expanduser()
    if not path.is_absolute() or path.is_symlink():
        raise ValueError('Ruta absoluta y sin symlink exigida')
    actual = path.resolve(strict=True)
    root = (checkout or Path(__file__).resolve().parents[1]).resolve()
    if actual == root or root in actual.parents:
        raise ValueError('Imagen comercial dentro del checkout')
    if not actual.is_file():
        raise ValueError('Entrada ISO no es archivo regular')
    if any((p / '.git').exists() for p in (actual.parent, *actual.parents)):
        raise ValueError('Prohibida ISO en otro repositorio Git')
    return actual

def validate_iso(iso: Path, expected_sha: str, checkout: Path | None = None) -> dict:
    iso = canonical_private_input(iso, checkout)
    if expected_sha not in (SOURCE_SHA, PROBE_SHA):
        raise ValueError('Solo hashes aprobados de ISO USA original/sonda')
    st = iso.stat()
    if st.st_size != ISO_SIZE or sha_file(iso) != expected_sha:
        raise ValueError('La ISO no coincide exactamente con SHA/tamaño exigidos')
    return {'source_iso_sha256': expected_sha, 'source_iso_bytes': st.st_size,
            'expected_label':'USA_original' if expected_sha == SOURCE_SHA else 'TUIKA_magenta_probe',
            'inode':st.st_ino,'device':st.st_dev}

def read_start_ticks(stat_bytes: bytes) -> int:
    raw = stat_bytes.strip()
    end, start = raw.rfind(b')'), raw.find(b'(')
    if start < 0 or end <= start:
        raise ValueError('stat /proc inválido')
    after = raw[end+1:].split()
    if len(after) < 20:
        raise ValueError('stat /proc truncado')
    ticks = int(after[19])
    if ticks <= 0:
        raise ValueError('starttime inválido')
    return ticks

def _argv_matches_iso(args: list[bytes], iso: Path) -> bool:
    for arg in args:
        try: candidate = os.fsdecode(arg)
        except (ValueError, UnicodeError): continue
        if candidate == str(iso):
            return True
    return False

def proc_snapshot(pid: int, iso: Path, proc_root: Path = Path('/proc')) -> dict:
    """Evidence: process has fd to exact inode, not that it loaded/used it."""
    if isinstance(pid, bool) or not isinstance(pid,int) or pid <= 0:
        raise ValueError('PID inválido')
    iso = Path(iso).resolve(strict=True)
    st_iso = iso.stat()
    directory = Path(proc_root)/str(pid)
    first = read_start_ticks((directory/'stat').read_bytes())
    raw = (directory/'cmdline').read_bytes()
    if not raw or len(raw) > 256*1024:
        raise ValueError('cmdline vacío/demasiado largo')
    argv = [s for s in raw.split(b'\0') if s]
    exe = os.readlink(directory/'exe')
    hint = any(v in Path(exe).name.lower() for v in ('ppsspp','apprun'))
    found = scanned = unreadable = 0
    for fd in (directory/'fd').iterdir():
        if not fd.name.isdecimal(): continue
        scanned += 1
        try: st = fd.stat()
        except (FileNotFoundError,PermissionError,OSError):
            unreadable += 1
            continue
        if stat.S_ISREG(st.st_mode) and (st.st_dev,st.st_ino,st.st_size) == (st_iso.st_dev,st_iso.st_ino,st_iso.st_size):
            found += 1
    second = read_start_ticks((directory/'stat').read_bytes())
    if first != second:
        raise RuntimeError('PID reutilizado/reiniciado durante lectura /proc')
    fingerprint = hashlib.sha256(f'{st_iso.st_dev}:{st_iso.st_ino}:{st_iso.st_size}'.encode()).hexdigest()
    return {
        'schema':'cladun.f2.procfs_open_iso_witness.v1',
        'pid':pid,'linux_start_ticks':first,
        'iso_device_inode_fingerprint':fingerprint,
        'cmdline_sha256':hashlib.sha256(raw).hexdigest(),
        'argv_exact_iso_path_present':_argv_matches_iso(argv,iso),
        'ppsspp_executable_name_hint':hint,
        'file_descriptors_scanned':scanned,'fd_stat_unreadable':unreadable,
        'open_descriptor_count_to_exact_iso_inode':found,
        'exact_iso_inode_open_at_snapshot':bool(found),
        'file_descriptors_not_published':True,
        'iso_binary_hash_verified_by_snapshot':False,
        'loaded_game_iso_identity_proven':False,
        'websocket_server_pid_correlated':False,
        'gameplay_or_mips_ge_vram_proven':False,
        'warning':'Un fd abierto al mismo inodo no prueba que sea el juego cargado. Su ausencia tampoco lo descarta.'
    }

def paired_observations(before: dict, after: dict) -> dict:
    if before.get('schema') != 'cladun.f2.procfs_open_iso_witness.v1' or after.get('schema') != before['schema']:
        raise ValueError('Observaciones /proc inválidas')
    if before['pid'] != after['pid'] or before['linux_start_ticks'] != after['linux_start_ticks']:
        raise ValueError('Distinto proceso o reinicio entre muestras')
    if before.get('iso_device_inode_fingerprint') != after.get('iso_device_inode_fingerprint'):
        raise ValueError('ISO sustituida entre muestras')
    both = bool(before['exact_iso_inode_open_at_snapshot'] and after['exact_iso_inode_open_at_snapshot'])
    return {'schema':'cladun.f2.procfs_pair_metadata.v1',
            'pid_starttime_stable':True,'same_inode_open_before_and_after':both,
            'is_conclusive_proof_of_loaded_iso':False,
            'is_conclusive_proof_of_websocket_server_pid':False,
            'is_gameplay_evidence':False,
            'no_open_fd_does_not_disprove_loaded_iso':True}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pid',type=int,required=True)
    p.add_argument('--iso-privada',type=Path,required=True)
    p.add_argument('--tipo',choices=('usa','sonda'),required=True)
    args=p.parse_args()
    expected=SOURCE_SHA if args.tipo == 'usa' else PROBE_SHA
    trusted=validate_iso(args.iso_privada,expected)
    witness=proc_snapshot(args.pid,args.iso_privada)
    print(json.dumps({'iso':{k:v for k,v in trusted.items() if k not in ('inode','device')},
                      'snapshot':witness},indent=2,ensure_ascii=False))

if __name__=='__main__':
    main()
