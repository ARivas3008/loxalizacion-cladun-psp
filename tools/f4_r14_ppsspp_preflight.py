#!/usr/bin/env python3
"""Fail-closed, READ-ONLY PPSSPP 1.20.4 provenance preflight (Linux).

Authenticates ISO, AppImage bytes, OS process starttime/FD/socket and WS
version/game status before accepting a future MIPS observation. It does NOT
trace control flow; never writes emulated memory, breakpoints or commercial data.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path

USA_SHA='b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
APPIMAGE_SHA='661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21'
GAME_ID='NPUH10072'
SUBPROTOCOL='debugger.ppsspp.org'

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda:f.read(4*1024*1024),b''):
            h.update(part)
    return h.hexdigest()

def starttime_from_proc_stat(stat):
    # /proc/PID/stat's process name may contain spaces or ')' chars.
    end=stat.rfind(')')
    if end<0 or not stat[:stat.find(' (')].isdigit():raise ValueError('Invalid /proc/PID/stat')
    rest=stat[end+2:].split()  # field 3 is index 0; field 22 is index 19.
    if len(rest)<=19 or not rest[19].isdigit():raise ValueError('Missing process starttime')
    return int(rest[19])

def socket_inodes_for_port(proc_root,port):
    found=set()
    for f in ('tcp','tcp6'):
        path=Path(proc_root)/'net'/f
        if not path.is_file():continue
        with path.open('r',encoding='ascii') as inp:
            next(inp,None)
            for line in inp:
                parts=line.split()
                if len(parts)<10:continue
                address=parts[1]
                if ':' not in address:continue
                try:actual_port=int(address.rsplit(':',1)[1],16)
                except ValueError:continue
                if parts[3]=='0A' and actual_port==port:
                    found.add(parts[9])
    return found

def attest_local_pid(proc_root,pid,iso,appimage,port=24192):
    """Process ownership checks; when tested with fixtures this remains B only."""
    if not isinstance(pid,int) or pid<2 or not 1<=port<=65535:
        raise ValueError('PID or debugger port invalid')
    root=Path(proc_root);proc=root/str(pid)
    stat=(proc/'stat').read_text(encoding='utf-8')
    start=starttime_from_proc_stat(stat)
    if int(stat.split(' ',1)[0])!=pid:raise ValueError('PID /proc/stat mismatch')
    comm=(proc/'comm').read_text(encoding='utf-8').strip()
    exe=os.readlink(proc/'exe')
    if 'ppsspp' not in (comm+' '+Path(exe).name).lower():
        raise ValueError('Target process is not identifiable as PPSSPP')
    appimage=Path(appimage).resolve(strict=True);iso=Path(iso).resolve(strict=True)
    environ=(proc/'environ').read_bytes().split(b'\0')
    appenv=[x.split(b'=',1)[1].decode('utf-8','surrogateescape')
            for x in environ if x.startswith(b'APPIMAGE=')]
    cmdline=[x.decode('utf-8','surrogateescape') for x in (proc/'cmdline').read_bytes().split(b'\0') if x]
    paths=appenv+cmdline
    if not any(Path(item).is_absolute() and Path(item).resolve(strict=False)==appimage for item in paths):
        raise ValueError('The running PPSSPP process does not identify the pinned AppImage')
    fds=proc/'fd';iso_ident=(iso.stat().st_dev,iso.stat().st_ino)
    iso_matches=[];socket_ids=set()
    for fd in fds.iterdir():
        try:
            link=os.readlink(fd)
            if link.startswith('socket:[') and link.endswith(']'):
                socket_ids.add(link[8:-1])
            else:
                st=fd.stat()
                if (st.st_dev,st.st_ino)==iso_ident:iso_matches.append(int(fd.name))
        except (FileNotFoundError,PermissionError,OSError):continue
    if not iso_matches:raise ValueError('Original ISO file inode not open by the same PID')
    bound=socket_ids & socket_inodes_for_port(root,port)
    if not bound:raise ValueError('WebSocket listening TCP port not owned by target PID')
    newer=starttime_from_proc_stat((proc/'stat').read_text(encoding='utf-8'))
    if newer!=start:raise ValueError('Process starttime changed during inspection')
    return {'pid':pid,'starttime_ticks':start,'iso_fd_count':len(iso_matches),
        'tcp_listen_socket_count':len(bound),'tcp_port':port,
        'proc_identity_checked':True,'network_process_provenance_checked':True,
        'ppsspp_MIPS_flow_proven':False}

def check_ws_readonly(port):
    # websocket-client is used only for an actual, optional, locally installed PPSSPP.
    try:import websocket
    except ImportError as e:raise RuntimeError('pip install websocket-client for real PPSSPP probing') from e
    ws=websocket.create_connection(f'ws://127.0.0.1:{port}/debugger',timeout=5,
        subprotocols=[SUBPROTOCOL],enable_multithread=True)
    try:
        if ws.getsubprotocol()!=SUBPROTOCOL:raise ValueError('Incorrect WebSocket debugger subprotocol')
        def request(event,ticket,extra):
            ws.send(json.dumps({'event':event,'ticket':ticket,**extra}))
            for _ in range(40):
                z=json.loads(ws.recv())
                if z.get('ticket')!=ticket:continue
                if z.get('event')=='error':raise ValueError('Debugger rejected '+event+': '+str(z.get('message')))
                if z.get('event')!=event:raise ValueError('Unexpected WS event returned for ticket')
                return z
            raise TimeoutError('No debugger response with matching ticket')
        version=request('version',7101,{'name':'cladun-r14-attestor','version':'1.0'})
        ver=version.get('version')
        # Tagged v1.20.4 source: version response lacks PID and game path.
        if version.get('name')!='PPSSPP' or not isinstance(ver,str) or not ver.startswith('v1.20.4'):
            raise ValueError('Unexpected PPSSPP version/name')
        game=request('game.status',7102,{})
        game_id=game.get('game',{}).get('id') if isinstance(game.get('game'),dict) else None
        if game_id!=GAME_ID:raise ValueError('PPSSPP has not loaded matching Cladun edition')
        return {'ws_event_version':ver,'ws_game_id':game_id,
            'ws_subprotocol_confirmed':True,'ws_read_only_commands':['version','game.status']}
    finally:ws.close()

def run_real(iso,appimage,pid,port,report_out):
    if iso.is_symlink() or not iso.is_file() or iso.stat().st_size!=305496064 or digest(iso)!=USA_SHA:
        raise ValueError('Original USA ISO missing or SHA/size wrong')
    if appimage.is_symlink() or not appimage.is_file() or digest(appimage)!=APPIMAGE_SHA:
        raise ValueError('Official PPSSPP AppImage absent or hash differs')
    proc=attest_local_pid(Path('/proc'),pid,iso,appimage,port)
    ws=check_ws_readonly(port)
    proc2=attest_local_pid(Path('/proc'),pid,iso,appimage,port)
    if proc2['starttime_ticks']!=proc['starttime_ticks']:
        raise ValueError('Process reused between provenance and WS probes')
    # This is only identity/preflight, not proof of an executed instruction.
    result={'schema':'cladun.f4.r14_ppsspp_provenance.v1','iso_sha256':USA_SHA,
        'ppsspp_appimage_sha256':APPIMAGE_SHA,**proc,**ws,
        'identity_checks_passed':True,'gameplay_case_Q050_Q051_executed':False,
        'mips_dispatch_or_control_flow_proven':False,
        'trace_C_of_event':False,'commercial_bytes_in_report':False}
    try:from tools.f3_referencias_riesgo import report_path
    except ModuleNotFoundError:from f3_referencias_riesgo import report_path
    target=report_path(report_out)
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2);f.write('\n')
    return result

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iso-original',type=Path,required=True)
    ap.add_argument('--appimage',type=Path,required=True)
    ap.add_argument('--pid',type=int,required=True)
    ap.add_argument('--port',type=int,default=24192)
    ap.add_argument('--reporte-privado',type=Path,required=True)
    a=ap.parse_args()
    result=run_real(a.iso_original,a.appimage,a.pid,a.port,a.reporte_privado)
    print(json.dumps({'pid':result['pid'],'version':result['ws_event_version'],
        'identity_checks_passed':True,'trace_C_of_event':False}))
if __name__=='__main__':main()
