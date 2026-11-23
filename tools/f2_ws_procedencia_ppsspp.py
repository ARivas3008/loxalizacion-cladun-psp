#!/usr/bin/env python3
"""Correlate a REAL PPSSPP 1.20.4 debugger WS listener to the ISO-holding PID.

Read-only procfs + authenticated private ISO, localhost WebSocket protocol.
PID->ISO fd and PID->TCP LISTEN socket are distinct from gameplay texture proof.
Never emit ISO paths, RAM, screenshots or commercial bytes into public reports.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import re
from pathlib import Path
try:
    from tools.f2_iso_proceso_ppsspp import canonical_private_input, sha_file, proc_snapshot, paired_observations
except ModuleNotFoundError:
    from f2_iso_proceso_ppsspp import canonical_private_input, sha_file, proc_snapshot, paired_observations

SHA_ISO = {
    'usa': 'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f',
    'sonda': 'b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa',
    'f1': '496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986',
}
ISO_BYTES = {'usa': 305496064, 'sonda': 305496064, 'f1': 306456576}
SOCKET = re.compile(r'^socket:\[(\d+)\]$')

def parse_listeners(table: str, port: int) -> set[int]:
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError('Puerto inválido')
    result = set()
    for line in table.splitlines()[1:]:
        parts = line.split()
        if len(parts) < 10:
            continue
        try:
            local_port = int(parts[1].rsplit(':', 1)[1], 16)
            inode = int(parts[9])
        except (ValueError, IndexError):
            continue
        if local_port == port and parts[3].upper() == '0A' and inode > 0:
            result.add(inode)
    return result

def listener_inodes(port: int, proc_root: Path = Path('/proc')) -> set[int]:
    net = Path(proc_root) / 'net'
    return (parse_listeners((net / 'tcp').read_text(encoding='ascii'), port)
            | parse_listeners((net / 'tcp6').read_text(encoding='ascii'), port))

def owned_socket_inodes(pid: int, proc_root: Path = Path('/proc')) -> set[int]:
    if type(pid) is not int or pid <= 0:
        raise ValueError('PID inválido')
    found = set()
    for fd in (Path(proc_root) / str(pid) / 'fd').iterdir():
        if not fd.name.isdecimal():
            continue
        try:
            target = os.readlink(fd)
        except OSError:
            continue
        match = SOCKET.fullmatch(target)
        if match:
            found.add(int(match.group(1)))
    return found

def ownership(pid: int, port: int, proc_root: Path = Path('/proc')) -> set[int]:
    return listener_inodes(port, proc_root) & owned_socket_inodes(pid, proc_root)

def real_websocket_handshake(port: int) -> dict:
    import websocket
    if type(port) is not int or not 1 <= port <= 65535:
        raise ValueError('Puerto inválido')
    conn = websocket.create_connection(
        f'ws://127.0.0.1:{port}/debugger',
        subprotocols=['debugger.ppsspp.org'],
        timeout=12, http_proxy_host=None)
    try:
        if conn.getsubprotocol() != 'debugger.ppsspp.org':
            raise RuntimeError('Subprotocolo no negociado')
        def ask(event: str, ticket: int, **params):
            conn.send(json.dumps({'event': event, 'ticket': ticket, **params}))
            for _ in range(50):
                data = json.loads(conn.recv())
                if data.get('ticket') == ticket:
                    if data.get('event') != event:
                        raise RuntimeError('Error o evento WebSocket inesperado')
                    return data
            raise TimeoutError('Sin respuesta solicitada del depurador')
        version = ask('version', 1, name='cladun-f2-ws-provenance', version='1')
        game = ask('game.status', 2)
        cpu = ask('cpu.status', 3)
        if version.get('name') != 'PPSSPP' or version.get('version') != 'v1.20.4':
            raise RuntimeError('Version de PPSSPP inesperada')
        if (game.get('game') or {}).get('id') != 'NPUH10072':
            raise RuntimeError('No es Cladun USA')
        if 'ticks' not in cpu or 'pc' not in cpu:
            raise RuntimeError('No existe estado CPU completo')
        return {'authentic': True, 'version': version['version'],
                'game_id': 'NPUH10072', 'cpu_running': not bool(cpu.get('stepping')),
                'cpu_ticks': cpu['ticks'], 'cpu_pc_hex': f"0x{cpu['pc']:08X}"}
    finally:
        conn.close()

def correlate(pid: int, port: int, iso: Path, role: str, proc_root: Path = Path('/proc')) -> dict:
    if role not in SHA_ISO:
        raise ValueError('Tipo de ISO no permitido')
    iso = canonical_private_input(iso)
    old_stat = iso.stat()
    if old_stat.st_size != ISO_BYTES[role] or sha_file(iso) != SHA_ISO[role]:
        raise ValueError('ISO no autenticada')
    before = proc_snapshot(pid, iso, proc_root)
    socket_before = ownership(pid, port, proc_root)
    if not socket_before:
        raise RuntimeError('Este PID no posee el socket LISTEN')
    ws = real_websocket_handshake(port)
    socket_after = ownership(pid, port, proc_root)
    after = proc_snapshot(pid, iso, proc_root)
    paired = paired_observations(before, after)
    new_stat = iso.stat()
    if (new_stat.st_ino != old_stat.st_ino or new_stat.st_dev != old_stat.st_dev
            or sha_file(iso) != SHA_ISO[role]):
        raise ValueError('ISO modificada durante la captura')
    if not (socket_before & socket_after):
        raise RuntimeError('Socket LISTEN inestable')
    if not paired['pid_starttime_stable']:
        raise RuntimeError('PID reciclado')
    if not before['ppsspp_executable_name_hint'] or not after['ppsspp_executable_name_hint']:
        raise RuntimeError('PID no identificado como PPSSPP')
    same_fd = paired['same_inode_open_before_and_after']
    return {
        'schema': 'cladun.f2.real_ppsspp_ws_pid_iso.v1',
        'iso_role': role, 'iso_sha256': SHA_ISO[role],
        'iso_bytes': ISO_BYTES[role],
        'pid_starttime_stable': True,
        'argv_exact_iso_match': before['argv_exact_iso_path_present'] and after['argv_exact_iso_path_present'],
        'iso_fd_same_inode_open_before_after': same_fd,
        'websocket_listener_owned_by_same_ppsspp_pid': True,
        'listener_inode_fingerprint_sha256': hashlib.sha256(
            str(sorted(socket_before & socket_after)).encode()).hexdigest(),
        'ws': ws,
        'rendered_game_iso_identity_proven': False,
        'mips_ram_ge_vram_chain_proven': False,
        'note': 'WS y descriptor ISO comparten PID; no demuestra uso de una textura.'
    }

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pid', type=int, required=True)
    parser.add_argument('--port', type=int, default=24192)
    parser.add_argument('--iso-privada', type=Path, required=True)
    parser.add_argument('--tipo', choices=tuple(SHA_ISO), required=True)
    parser.add_argument('--informe-privado', type=Path, required=True)
    args = parser.parse_args()
    result = correlate(args.pid, args.port, args.iso_privada, args.tipo)
    output = args.informe_privado
    repo = Path(__file__).resolve().parents[1]
    out = output.expanduser().resolve(strict=False)
    if (not output.is_absolute() or output.suffix != '.json' or out.exists()
            or repo in out.parents or any((parent / '.git').exists() for parent in out.parents)):
        raise ValueError('Informe debe ser nuevo y privado, fuera del checkout Git')
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open('x', encoding='utf-8') as file:
        json.dump(result, file, ensure_ascii=False, indent=2)
    print(json.dumps({'schema': result['schema'], 'iso_role': result['iso_role'],
        'ws_listener_owned_by_same_ppsspp_pid': True,
        'iso_fd_same_inode_open_before_after': result['iso_fd_same_inode_open_before_after'],
        'rendered_game_iso_identity_proven': False}, ensure_ascii=False))

if __name__ == '__main__':
    main()
