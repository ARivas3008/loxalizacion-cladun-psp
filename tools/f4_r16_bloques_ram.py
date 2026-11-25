"""R16: locate independent original script bodies; read-only, never MIPS proof."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import argparse
from collections import defaultdict
import struct
try:
    from tools.f4_r15_localizador_ram import valid_scan_range, ReadonlyWS, SCRIPT_SHA, SCRIPT_SIZE
except ModuleNotFoundError:
    from f4_r15_localizador_ram import valid_scan_range, ReadonlyWS, SCRIPT_SHA, SCRIPT_SIZE

BLOCKS=(20,757,758,759,760,761,762,763)
TABLE_SHA='f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37'
EXPECTED_LENGTHS=(340,34,5269,221,4355,238,332,415)
WIDTH=16


def digest(data):
    return hashlib.sha256(data).hexdigest()


def unique(data, signature):
    p=data.find(signature)
    return p>=0 and data.find(signature,p+1)<0


def recipes(data,commands,starts,blocks=BLOCKS):
    """Return private byte recipes. Do not serialize them or commit them."""
    if len(starts)<2 or starts[0]!=0 or starts[-1]!=len(data) or any(a>=b for a,b in zip(starts,starts[1:])):
        raise ValueError('Invalid block boundaries')
    if not blocks or len(set(blocks))!=len(blocks):raise ValueError('Duplicate or missing block selection')
    grouped=defaultdict(list)
    for c in commands:
        if c.block in blocks:grouped[c.block].append(c)
    result=[]
    for b in blocks:
        if not 0<=b<len(starts)-1:raise ValueError('Invalid block')
        begin,limit=starts[b:b+2];end=begin
        for c in sorted(grouped[b],key=lambda x:x.offset):
            if c.offset!=end or len(c.raw)<5 or end+len(c.raw)>limit or data[end:end+len(c.raw)]!=c.raw:
                raise ValueError('Command coverage inconsistent')
            end+=len(c.raw)
        body=data[begin:end]
        if any(data[end:limit]):raise ValueError('Nonzero padding')
        if len(body)<2*WIDTH:raise ValueError('Body too short for disjoint anchors')
        first,last=body[:WIDTH],body[-WIDTH:]
        if not unique(data,first) or not unique(data,last) or first==last:raise ValueError('Ambiguous anchor')
        result.append((b,begin,body,((0,first),(len(body)-WIDTH,last))))
    return result


def metadata(items):
    return [{'block':b,'script_offset':off,'command_bytes':len(body),'body_sha256':digest(body),
             'anchors':[{'relative_offset':rel,'sha256':digest(sig)} for rel,sig in anchors]}
            for b,off,body,anchors in items]


def scan(read,start,end,items,chunk_size=16384):
    """Two independent hits plus full body equality, twice; no execution inference."""
    valid_scan_range(start,end,chunk_size)
    if not items or len({x[0] for x in items})!=len(items):raise ValueError('Invalid recipes')
    found=defaultdict(set);tail=b''
    for addr in range(start,end,chunk_size):
        n=min(chunk_size,end-addr);part=read(addr,n)
        if type(part) is not bytes or len(part)!=n:raise ValueError('Incomplete read')
        buf=tail+part;origin=addr-len(tail)
        for block,_,body,anchors in items:
            for rel,sig in anchors:
                pos=buf.find(sig)
                while pos>=0:
                    base=origin+pos-rel
                    if start<=base and base+len(body)<=end:found[(block,base)].add(rel)
                    pos=buf.find(sig,pos+1)
        if len(found)>128:raise ValueError('Too many candidate block locations')
        tail=buf[-(WIDTH-1):]
    results=[]
    byblock={x[0]:x for x in items}
    for (b,base),hits in sorted(found.items()):
        _,_,body,anchors=byblock[b]
        if hits!={r for r,_ in anchors}:continue
        if len(body)>65536:raise ValueError('Block exceeds safe read cap')
        if read(base,len(body))!=body or read(base,len(body))!=body:continue
        results.append({'block':b,'candidate_base':base,'command_bytes':len(body),
                        'body_sha256':digest(body),'two_full_reads_match':True,'mips_execution_proven':False})
    return results


def authenticated_recipes(iso):
    try:
        from tools.f3_referencias_riesgo import original_script_children
        from tools.script_event_guard import read_commands
    except ModuleNotFoundError:
        from f3_referencias_riesgo import original_script_children
        from script_event_guard import read_commands
    data,tbl=original_script_children(iso)
    if len(data)!=SCRIPT_SIZE or digest(data)!=SCRIPT_SHA or digest(tbl)!=TABLE_SHA:raise ValueError('Original hashes mismatch')
    commands,starts=read_commands(data,tbl)
    if len(commands)!=51705 or len(starts)!=1626 or sum(c.content is None for c in commands)!=46308:raise ValueError('Original counts mismatch')
    items=recipes(data,commands,starts)
    if tuple(len(x[2]) for x in items)!=EXPECTED_LENGTHS:raise ValueError('Original block lengths mismatch')
    return items


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso-original',type=Path,required=True)
    p.add_argument('--reporte-privado',type=Path,required=True)
    p.add_argument('--modo',choices=('preparar','escanear'),default='preparar')
    p.add_argument('--appimage',type=Path);p.add_argument('--pid',type=int);p.add_argument('--port',type=int,default=24192)
    p.add_argument('--ram-start',type=lambda x:int(x,0));p.add_argument('--ram-end',type=lambda x:int(x,0))
    a=p.parse_args();items=authenticated_recipes(a.iso_original)
    report={'scope':'A_STATIC_ONLY','blocks':metadata(items),'mips_execution_proven':False,'relocation_allowed':False}
    if a.modo=='escanear':
        import websocket
        try:from tools.f4_r14_ppsspp_preflight import attest_local_pid,check_ws_readonly,digest as file_digest,USA_SHA,APPIMAGE_SHA,SUBPROTOCOL
        except ModuleNotFoundError:from f4_r14_ppsspp_preflight import attest_local_pid,check_ws_readonly,digest as file_digest,USA_SHA,APPIMAGE_SHA,SUBPROTOCOL
        if not all((a.appimage,a.pid,a.ram_start,a.ram_end)):raise ValueError('Explicit authenticated session and range required')
        if a.appimage.is_symlink() or not a.appimage.is_file() or file_digest(a.appimage)!=APPIMAGE_SHA:raise ValueError('AppImage not authenticated')
        if a.iso_original.is_symlink() or file_digest(a.iso_original)!=USA_SHA:raise ValueError('ISO not authenticated')
        valid_scan_range(a.ram_start,a.ram_end,16384)
        before=attest_local_pid(Path('/proc'),a.pid,a.iso_original,a.appimage,a.port);status=check_ws_readonly(a.port)
        ws=websocket.create_connection(f'ws://127.0.0.1:{a.port}/debugger',timeout=8,subprotocols=[SUBPROTOCOL])
        try:
            if ws.getsubprotocol()!=SUBPROTOCOL:raise ValueError('Wrong debugger protocol')
            matches=scan(ReadonlyWS(ws),a.ram_start,a.ram_end,items)
        finally:ws.close()
        after=attest_local_pid(Path('/proc'),a.pid,a.iso_original,a.appimage,a.port)
        if before['starttime_ticks']!=after['starttime_ticks'] or check_ws_readonly(a.port)!=status:raise ValueError('Session changed')
        report.update(scope='C_READONLY_BLOCK_BYTES_NOT_EXECUTION',matches=matches,pid=a.pid,starttime=before['starttime_ticks'],iso_sha256=USA_SHA,appimage_sha256=APPIMAGE_SHA,version=status['ws_event_version'],game_id=status['ws_game_id'])
    try:from tools.f3_referencias_riesgo import report_path
    except ModuleNotFoundError:from f3_referencias_riesgo import report_path
    out=report_path(a.reporte_privado);out.parent.mkdir(parents=True,exist_ok=True)
    with out.open('x',encoding='utf-8') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'scope':report['scope'],'blocks':len(items),'mips_execution_proven':False}))
if __name__=='__main__':main()
