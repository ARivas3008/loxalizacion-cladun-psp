#!/usr/bin/env python3
"""R15 Cladun: only-read PSP memory locator for *authenticated* SCRIPT.DAT.

Static A: derives hashed, unique anchors from user's verified ISO.
Potential C provenance: probes real PPSSPP 1.20.4 through read-only WebSocket,
checking AppImage/ISO/process/socket before+after. A located byte image is
NOT proof that the MIPS interpreter executed commands, calls or returns.
"""
from __future__ import annotations
import argparse
import base64
import hashlib
import json
from pathlib import Path
from collections import defaultdict

ISO_SHA='b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
SCRIPT_SHA='c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358'
SCRIPT_SIZE=633344
OFFSETS=(7420,218095,218133,223351,223360,223602,223637,227968,228194)
ANCHOR_SIZE=32
MIN_ANCHORS=3
MAX_RANGE=32*1024*1024
MIN_CHUNK=4096
MAX_CHUNK=65536
MAX_CANDIDATES=16


def script_anchors(data:bytes, offsets=OFFSETS):
    if len(data)!=SCRIPT_SIZE or hashlib.sha256(data).hexdigest()!=SCRIPT_SHA:
        raise ValueError('SCRIPT.DAT has incorrect size or SHA-256')
    if len(offsets)<MIN_ANCHORS or len(set(offsets))!=len(offsets):
        raise ValueError('Need at least three independent command offsets')
    output=[]
    for off in offsets:
        if off<0 or off+ANCHOR_SIZE>len(data):raise ValueError('Anchor offset outside original SCRIPT.DAT')
        fragment=data[off:off+ANCHOR_SIZE]
        if data.count(fragment)!=1:raise ValueError('Anchor not unique inside original SCRIPT.DAT')
        output.append((off,fragment))
    if len({frag for _,frag in output}) != len(output):
        raise ValueError('Non-distinct anchor fingerprints')
    return output


def valid_scan_range(start,end,chunk_size):
    if type(start) is not int or type(end) is not int or not 0x08000000<=start<end<=0x0C000000:
        raise ValueError('Explicit PSP RAM scanning range must be inside 08000000..0C000000')
    if end-start>MAX_RANGE:raise ValueError('Read-only scan exceeds 32 MiB cap')
    if type(chunk_size) is not int or not MIN_CHUNK<=chunk_size<=MAX_CHUNK:
        raise ValueError('Chunk size outside safe range 4096..65536')
    if end-start < ANCHOR_SIZE:raise ValueError('Range too small for fingerprints')


def candidate_bases(read,start,end,anchors,chunk_size=16384):
    """Search each 32-byte anchor with overlap; derive tentative SCRIPT.DAT RAM bases.

    Returns a dict of base=>matched distinct anchor offsets; never a truth claim.
    """
    valid_scan_range(start,end,chunk_size)
    if len(anchors)<MIN_ANCHORS:raise ValueError('Insufficient anchors')
    if len({off for off,_ in anchors})!=len(anchors):raise ValueError('Duplicate anchors')
    if any(len(f)!=ANCHOR_SIZE for _,f in anchors):raise ValueError('Bad fingerprint length')
    found=defaultdict(set)
    tail=b''
    for addr in range(start,end,chunk_size):
        size=min(chunk_size,end-addr)
        buf=read(addr,size)
        if not isinstance(buf,bytes) or len(buf)!=size:raise ValueError('Memory reader returned wrong byte count')
        data=tail+buf
        begin=addr-len(tail)
        for offset,fingerprint in anchors:
            p=data.find(fingerprint)
            while p>=0:
                image_base=begin+p-offset
                if start<=image_base and image_base+SCRIPT_SIZE<=end:
                    found[image_base].add(offset)
                p=data.find(fingerprint,p+1)
        if len(found)>MAX_CANDIDATES:raise ValueError('Too many ambiguous candidate bases')
        tail=data[-(ANCHOR_SIZE-1):]
    return dict(found)


def verify_candidates(read,bases,anchors,min_anchors=MIN_ANCHORS,full_hash=True):
    if min_anchors<3 or min_anchors>len(anchors):raise ValueError('Insufficient independent anchors required')
    results=[]
    for base,offsets in sorted(bases.items()):
        if len(offsets)<min_anchors:continue
        agreement=sum(read(base+off,len(fragment))==fragment for off,fragment in anchors)
        if agreement<min_anchors:continue
        confirmed=False
        if full_hash:
            sha=hashlib.sha256()
            for start in range(0,SCRIPT_SIZE,65536):
                size=min(65536,SCRIPT_SIZE-start)
                part=read(base+start,size)
                if not isinstance(part,bytes) or len(part)!=size:raise ValueError('Truncated full-memory digest')
                sha.update(part)
            confirmed=sha.hexdigest()==SCRIPT_SHA
        results.append({'candidate_base':base,'candidate_base_hex':f'0x{base:08X}',
            'anchors_matched':agreement,'total_anchors':len(anchors),
            'complete_original_script_sha256_matched':confirmed,
            'mips_control_flow_observed':False,'event_calls_proven':False})
    return results


class ReadonlyWS:
    """Official v1.20.4 WS: memory.read returns base64, includes request ticket."""
    def __init__(self,ws):self.ws=ws;self.ticket=150000
    def __call__(self,addr,size):
        if not 0x08000000<=addr or not 1<=size<=MAX_CHUNK or addr+size>0x0C000000:
            raise ValueError('Unsafe memory.read range')
        self.ticket+=1
        ticket=self.ticket
        self.ws.send(json.dumps({'event':'memory.read','ticket':ticket,
            'address':addr,'size':size,'replacements':True}))
        for _ in range(64):
            resp=json.loads(self.ws.recv())
            if resp.get('ticket')!=ticket:continue  # Async events or unrelated responses.
            if resp.get('event')=='error':raise RuntimeError('PPSSPP memory.read rejected requested range')
            if resp.get('event')!='memory.read':raise ValueError('Unexpected WS event with matching ticket')
            if type(resp.get('base64')) is not str:raise ValueError('Missing memory.read base64 data')
            try:part=base64.b64decode(resp['base64'],validate=True)
            except Exception as e:raise ValueError('Invalid memory.read base64 data') from e
            if len(part)!=size:raise ValueError('memory.read response length does not match request')
            return part
        raise TimeoutError('No memory.read response for ticket')


def prepare_report(data):
    anchors=script_anchors(data)
    return {'schema':'cladun.f4.r15_ram_anchor_recipe.v1',
        'scope':'A_ISO_STATIC; NOT_GAMEPLAY; NO_RAM_ADDRESSES',
        'original_iso_sha256':ISO_SHA,'script_dat_sha256':SCRIPT_SHA,
        'original_script_bytes':SCRIPT_SIZE,
        'fingerprint_size':ANCHOR_SIZE,
        'unique_in_original_count':len(anchors),
        'fingerprints':[{'script_dat_offset':off,'sha256':hashlib.sha256(f).hexdigest(),
            'occurrences_in_original':1} for off,f in anchors],
        'mips_trace_performed':False,'ppsspp_memory_checked':False,
        'relocation_allowed':False,'commercial_original_bytes_in_report':False}


def run_attested_scan(data,iso,appimage,pid,port,ram_start,ram_end,chunk_size):
    """Do not scan without exact game/AppImage hashes and OS+WS provenance."""
    import websocket
    try:from tools.f4_r14_ppsspp_preflight import attest_local_pid,check_ws_readonly,digest,USA_SHA,APPIMAGE_SHA,SUBPROTOCOL
    except ModuleNotFoundError:from f4_r14_ppsspp_preflight import attest_local_pid,check_ws_readonly,digest,USA_SHA,APPIMAGE_SHA,SUBPROTOCOL
    valid_scan_range(ram_start,ram_end,chunk_size)
    if iso.is_symlink() or iso.stat().st_size!=305496064 or digest(iso)!=USA_SHA:
        raise ValueError('Original ISO cannot be authenticated')
    if appimage.is_symlink() or not appimage.is_file() or digest(appimage)!=APPIMAGE_SHA:
        raise ValueError('Official PPSSPP v1.20.4 AppImage missing or wrong SHA')
    proc=attest_local_pid(Path('/proc'),pid,iso,appimage,port)
    status=check_ws_readonly(port)
    ws=websocket.create_connection(f'ws://127.0.0.1:{port}/debugger',timeout=8,
        subprotocols=[SUBPROTOCOL],enable_multithread=True)
    try:
        if ws.getsubprotocol()!=SUBPROTOCOL:raise ValueError('Wrong debugger WebSocket subprotocol')
        reader=ReadonlyWS(ws)
        anchors=script_anchors(data)
        candidates=candidate_bases(reader,ram_start,ram_end,anchors,chunk_size)
        verified=verify_candidates(reader,candidates,anchors)
    finally:ws.close()
    proc_end=attest_local_pid(Path('/proc'),pid,iso,appimage,port)
    if proc['starttime_ticks']!=proc_end['starttime_ticks']:
        raise ValueError('PPSSPP process replaced during scan')
    return {'schema':'cladun.f4.r15_ram_locator_status.v1',
        'scope':'C_PROVENANCE_AND_READONLY_RAM_INSPECTION_NOT_MIPS_EXECUTION',
        'official_appimage_sha256':APPIMAGE_SHA,'iso_sha256':USA_SHA,
        'ppsspp_version':status['ws_event_version'],'game_id':status['ws_game_id'],
        'pid':proc['pid'],'process_starttime_ticks':proc['starttime_ticks'],
        'scan_start':f'0x{ram_start:08X}','scan_end':f'0x{ram_end:08X}',
        'candidate_count':len(candidates),'verified_candidates':verified,
        'full_script_image_found':any(x['complete_original_script_sha256_matched'] for x in verified),
        'control_flow_or_retour_observed':False,'event_Q050_Q051_Q053_pass':False,
        'memory_write_calls':0,'commercial_bytes_in_report':False}


def load_script_private(args):
    if args.script_dat_private:
        if args.script_dat_private.is_symlink():raise ValueError('SCRIPT.DAT private path cannot be symlink')
        return args.script_dat_private.read_bytes()
    if not args.iso_original:raise ValueError('Need original ISO or private verified SCRIPT.DAT')
    try:from tools.f3_referencias_riesgo import original_script_children
    except ModuleNotFoundError:from f3_referencias_riesgo import original_script_children
    return original_script_children(args.iso_original)[0]


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--script-dat-private',type=Path)
    ap.add_argument('--iso-original',type=Path)
    ap.add_argument('--modo',choices=['preparar','escanear'],required=True)
    ap.add_argument('--appimage',type=Path)
    ap.add_argument('--pid',type=int)
    ap.add_argument('--port',type=int,default=24192)
    ap.add_argument('--ram-start',type=lambda x:int(x,0))
    ap.add_argument('--ram-end',type=lambda x:int(x,0))
    ap.add_argument('--chunk-size',type=int,default=16384)
    ap.add_argument('--reporte-privado',type=Path,required=True)
    args=ap.parse_args()
    data=load_script_private(args)
    static=prepare_report(data)
    if args.modo=='preparar':result=static
    else:
        if not all([args.iso_original,args.appimage,args.pid,args.ram_start,args.ram_end]):
            raise ValueError('Scan requires real ISO, AppImage, PID and explicit RAM range')
        result=run_attested_scan(data,args.iso_original,args.appimage,args.pid,args.port,args.ram_start,args.ram_end,args.chunk_size)
    try:from tools.f3_referencias_riesgo import report_path
    except ModuleNotFoundError:from f3_referencias_riesgo import report_path
    dst=report_path(args.reporte_privado)
    dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open('x',encoding='utf-8') as f:json.dump(result,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'mode':args.modo,'scope':result['scope'],
        'found_full_script_image':result.get('full_script_image_found',False),
        'mips_event_trace_verified':False}))
if __name__=='__main__':main()
