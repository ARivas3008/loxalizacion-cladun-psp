#!/usr/bin/env python3
"""Read-only origin-to-RAM probe for Cladun icons and PPSSPP 1.20.4.

Never dumps assets to Git. A RAM match does NOT establish GE/VRAM provenance;
a paused MIPS PC must be independently correlated with GE and textures.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
from pathlib import Path

from f2_ppsspp_ws_1204 import Client, output_dir, exclusive

USA_SHA = 'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
KITAJIMA_SHA = '0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190'
KITAJIMA_ISO_OFFSET = 114723840
KITAJIMA_SIZE = 2480
MIN_ADDR = 0x08000000
MAX_ADDR = 0x0C000000
DEFAULT_START = 0x08800000
DEFAULT_END = 0x0A000000
DEFAULT_CHUNK = 65536


def verified_signature(iso: Path, *, expected_sha=USA_SHA, offset=KITAJIMA_ISO_OFFSET,
                       size=KITAJIMA_SIZE, expected_member_sha=KITAJIMA_SHA) -> bytes:
    iso=Path(iso)
    digest=hashlib.sha256()
    with iso.open('rb') as handle:
        for part in iter(lambda: handle.read(1<<20),b''):
            digest.update(part)
    if digest.hexdigest()!=expected_sha:
        raise ValueError('ISO fuente con SHA256 no autorizado')
    if offset<0 or size<256 or size>65536 or offset+size>iso.stat().st_size:
        raise ValueError('Firma fuera de la ISO')
    with iso.open('rb') as handle:
        handle.seek(offset)
        signature=handle.read(size)
    if hashlib.sha256(signature).hexdigest()!=expected_member_sha:
        raise ValueError('KITAJIMA_KARI.IMY tiene SHA incorrecto')
    return signature


def scan_ram(client: Client, signature: bytes, start=DEFAULT_START,
             end=DEFAULT_END, chunk=DEFAULT_CHUNK) -> dict:
    if not (MIN_ADDR<=start<end<=MAX_ADDR and 4096<=chunk<=DEFAULT_CHUNK):
        raise ValueError('Rango PSP RAM o bloque fuera de límite')
    if not 256<=len(signature)<=chunk:
        raise ValueError('Firma no válida')
    hits=[]
    skipped=[]
    tail=b''
    for address in range(start,end,chunk):
        size=min(chunk,end-address)
        try:
            reply=client.request('memory.read',address=address,size=size)
            encoded=reply['base64']
            if not isinstance(encoded,str) or len(encoded)>((size+2)//3)*4+4:
                raise ValueError('Lectura RAM excesiva')
            contents=base64.b64decode(encoded,validate=True)
            if len(contents)!=size:
                raise ValueError('Tamaño de lectura RAM distinto')
        except (RuntimeError,ValueError,KeyError):
            skipped.append(address)
            tail=b''  # Nunca unir páginas desconocidas
            continue
        joined=tail+contents
        hit=joined.find(signature)
        while hit!=-1:
            found=address-len(tail)+hit
            if found not in hits and len(hits)<32:
                hits.append(found)
            hit=joined.find(signature,hit+1)
        tail=contents[-(len(signature)-1):]
    return {'scan_start':start,'scan_end':end,'chunk_size':chunk,
            'signature_sha256':hashlib.sha256(signature).hexdigest(),
            'exact_ram_hits_max_32':hits,'unreadable_chunks_count':len(skipped),
            'is_continuous_complete_scan':not bool(skipped),
            'findings_limitations':'An exact compressed signature is an observation in RAM, not evidence of an upload to GE/VRAM.'}


def scan_ram_snapshot(client: Client, signature: bytes, start=DEFAULT_START,
                      end=DEFAULT_END, chunk=DEFAULT_CHUNK) -> dict:
    """Scan a consistent STOPPED PSP CPU; do not stitch asynchronous snapshots.

    A verified compressed copy in RAM still does not prove any GE upload.
    Preserve externally established debugger pauses, including failures.
    """
    original = client.request('cpu.status')
    was_paused = original.get('stepping') is True
    paused_here = False
    try:
        if not was_paused:
            client.notify('cpu.stepping')
            client.wait_broadcast('cpu.stepping')
            paused_here = True
        start_status = client.request('cpu.status')
        if start_status.get('stepping') is not True:
            raise RuntimeError('No se confirmó CPU detenida antes de leer RAM')
        before = start_status.get('ticks')
        if not isinstance(before, (int,float)):
            raise RuntimeError('PPSSPP no informó ticks de emulación')
        result = scan_ram(client, signature, start, end, chunk)
        end_status = client.request('cpu.status')
        after = end_status.get('ticks')
        if end_status.get('stepping') is not True or after != before:
            raise RuntimeError('CPU avanzó mientras se escaneaba RAM; invalidar resultados')
        result.update({'snapshot_cpu_stepping_confirmed':True,
                       'snapshot_emulated_ticks':before,
                       'pause_preexisted':was_paused,
                       'mips_pc_proven':False, 'ge_vram_upload_proven':False})
        return result
    finally:
        if paused_here:
            # Never resume if another debugger already resumed the CPU.
            current=client.request('cpu.status')
            if current.get('stepping') is True:
                client.notify('cpu.resume')
                client.wait_broadcast('cpu.resume')


def watch_address_once(client: Client,address:int,size:int=4) -> dict:
    """One breakpoint and a CPU stop; never modify PSP memory or game code.

    External CPU pause is refused. The PC is an observation at CPU stop; only
    verified reason/relatedAddress plus more GE evidence can establish causality.
    """
    if not MIN_ADDR<=address<MAX_ADDR or not 1<=size<=16 or address+size>MAX_ADDR:
        raise ValueError('Watchpoint inválido')
    status=client.request('cpu.status')
    if status.get('stepping') is True:
        raise RuntimeError('CPU ya detenida: preservar pausa del operador')
    client.request('memory.breakpoint.add',address=address,size=size,
                   enabled=True,log=False,read=True,write=True,change=False)
    halted=False
    matching_break=False
    try:
        event=client.wait_broadcast('cpu.stepping')
        halted=client.request('cpu.status').get('stepping') is True
        if not halted:
            raise RuntimeError('No se confirmó pausa de CPU tras evento')
        related=event.get('relatedAddress')
        matching_break=isinstance(related,int) and address<=related<address+size
        pc=event.get('pc')
        if not isinstance(pc,int) or pc%4 or not MIN_ADDR<=pc<MAX_ADDR:
            raise ValueError('PC MIPS no válido en el evento de pausa')
        disasm=client.request('memory.disasm',address=pc-16,count=12).get('lines',[])
        regs=client.request('cpu.getAllRegs').get('categories',[])
        return {'watched_address':address,'watched_size':size,'cpu_pc_at_pause':pc,
                'broadcast_reason':event.get('reason'),'related_address':related,
                'possible_matching_memory_break':matching_break,
                'disassembly':disasm,'registers':regs,'ge_upload_proven':False,
                'vram_address_proven':False}
    finally:
        try:
            client.request('memory.breakpoint.remove',address=address,size=size)
        finally:
            if halted and matching_break:
                client.notify('cpu.resume')
                client.wait_broadcast('cpu.resume')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--iso-usa',type=Path,required=True)
    parser.add_argument('--salida-privada',type=Path,required=True,
                        help='Directorio nuevo, nunca bajo el repositorio')
    parser.add_argument('--solo-origen',action='store_true')
    parser.add_argument('--scan-ram',action='store_true')
    parser.add_argument('--watch-address',type=lambda a:int(a,0))
    parser.add_argument('--port',type=int,default=24192)
    args=parser.parse_args()
    folder=output_dir(args.salida_privada,Path(__file__).resolve().parents[1])
    signature=verified_signature(args.iso_usa)
    report={'schema':'cladun.f2.compressed_imy_ram_provenance.v1',
            'origin_verified':'USA ISO SHA256 and exact KITAJIMA_KARI.IMY SHA256',
            'icon_absolute_iso_offset':KITAJIMA_ISO_OFFSET,
            'compressed_imy_length':len(signature),
            'compressed_imy_sha256':hashlib.sha256(signature).hexdigest(),
            'actual_ram_trace':'NOT_EXECUTED','mips_ge_vram_chain_proven':False}
    if args.scan_ram or args.watch_address is not None:
        if args.solo_origen:
            parser.error('--solo-origen incompatible con --scan-ram o --watch-address')
        if not 1<=args.port<=65535:
            parser.error('Puerto local inválido')
        try:
            import websocket
        except ImportError as exc:
            raise RuntimeError('Requiere websocket-client para conectar a PPSSPP real') from exc
        conn=websocket.create_connection('ws://127.0.0.1:%d/debugger'%args.port,
                                         timeout=60,subprotocols=['debugger.ppsspp.org'])
        try:
            if conn.getsubprotocol()!='debugger.ppsspp.org':
                raise RuntimeError('Subprotocolo WebSocket incorrecto')
            client=Client(conn)
            v=client.request('version',name='cladun-f2-ram',version='1')
            if v.get('name')!='PPSSPP' or not str(v.get('version','')).startswith('v1.20.4'):
                raise RuntimeError('Se requiere PPSSPP 1.20.4')
            game=client.request('game.status').get('game')
            if not isinstance(game,dict) or 'cladun' not in str(game.get('title','')).lower():
                raise RuntimeError('Juego distinto de Cladun')
            report['actual_ram_trace']='PPSSPP debugger WebSocket connected'
            report['game_id']=game.get('id')
            if args.scan_ram:
                report['ram_scan']=scan_ram_snapshot(client,signature)
            if args.watch_address is not None:
                report['watchpoint']=watch_address_once(client,args.watch_address)
        finally:
            conn.close()
    data=(json.dumps(report,ensure_ascii=False,indent=2)+'\n').encode('utf-8')
    result=exclusive(folder/'f2_ram_origen_manifest_PRIVADO.json',data)
    print(json.dumps({'manifest_sha256':result['sha256'],
                      'compressed_imy_sha256':report['compressed_imy_sha256'],
                      'ram_trace':report['actual_ram_trace'],
                      'mips_ge_vram_chain_proven':False},ensure_ascii=False,indent=2))

if __name__=='__main__':main()
