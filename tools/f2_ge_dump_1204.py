#!/usr/bin/env python3
"""Read-only PPSSPP v1.20.4 GE dump v6 parser. No proprietary payload in report.

Format based on PPSSPP v1.20.4 GPU/Debugger/RecordFormat.h and Record.cpp.
An authentic dump can show GE opcodes but cannot prove their MIPS origin.
"""
from __future__ import annotations
import argparse
import collections
import ctypes
import hashlib
import json
import struct
from pathlib import Path

MAGIC=b'PPSSPPGE'
VERSION=6
HEADER_SIZE=32
COMMAND_STRIDE=9
MAX_CMDS=500_000
MAX_PAYLOAD=128*1024*1024
MAX_COMPRESSED=160*1024*1024
KINDS={0:'INIT',1:'REGISTERS',2:'VERTICES',3:'INDICES',4:'CLUT',5:'TRANSFERSRC',
       6:'MEMSET',7:'MEMCPYDEST',8:'MEMCPYDATA',9:'DISPLAY',10:'CLUTADDR',11:'EDRAMTRANS'}
KINDS.update({0x10+i:f'TEXTURE{i}' for i in range(8)})
KINDS.update({0x18+i:f'FRAMEBUF{i}' for i in range(8)})
GE_NAMES={0x01:'VADDR',0x02:'IADDR',0x04:'PRIM',0x08:'JUMP',0x0A:'CALL',
          0x0C:'END',0x0E:'SIGNAL',0x0F:'FINISH',0x10:'BASE',
          0xB0:'CLUTADDR',0xB1:'CLUTADDRUPPER',0xB2:'TRANSFERSRC',
          0xB3:'TRANSFERSRCW',0xB4:'TRANSFERDST',0xB5:'TRANSFERDSTW',
          0xC2:'TEXMODE',0xC3:'TEXFORMAT',0xC5:'CLUTFORMAT',
          0xEA:'TRANSFERSTART',0xEB:'TRANSFERSRCPOS',
          0xEC:'TRANSFERDSTPOS',0xEE:'TRANSFERSIZE'}
GE_NAMES.update({0xA0+i:f'TEXADDR{i}' for i in range(8)})
GE_NAMES.update({0xA8+i:f'TEXBUFWIDTH{i}' for i in range(8)})
GE_NAMES.update({0xB8+i:f'TEXSIZE{i}' for i in range(8)})


MAX_GE_ADDRESS_OBSERVATIONS=150

def _hexaddr(v:int)->str:
    return '0x%08X' % v

def _known_vram_window(v:int)->bool:
    """Classify candidate numeric region only; not proof of a VRAM upload."""
    return 0x04000000<=v<0x04200000

def ge_addresses_from_state(registers:dict[int,int], trigger:int)->dict:
    """Pure address metadata derived exactly from PPSSPP v1.20.4 GPUState.h.

    Only register arguments seen in this *recording* are used. Missing INIT or
    previous-frame GPU state means the candidate list may be incomplete.
    Neither a candidate address nor a PRIM proves a texture was ever uploaded.
    """
    result={}
    if trigger==0x04:
        if 0x1E in registers:
            result['texture_mapping_enabled_seen']=bool(registers[0x1E]&1)
        if 0xC3 in registers:
            result['texture_format_seen']=registers[0xC3]&0xF
        slots=[]
        for level in range(8):
            a,b=0xA0+level,0xA8+level
            if a in registers and b in registers:
                addr=(registers[a]&0xFFFFF0)|((registers[b]<<8)&0x0F000000)
                slots.append({'mip_level':level,'address_candidate':_hexaddr(addr),
                              'in_primary_2mib_vram_window':_known_vram_window(addr)})
        if slots:result['texture_address_candidates']=slots
        if 0xB0 in registers and 0xB1 in registers:
            addr=(registers[0xB0]&0x00FFFFF0)|((registers[0xB1]<<8)&0x0F000000)
            result['clut_address_candidate']=_hexaddr(addr)
            result['clut_in_primary_2mib_vram_window']=_known_vram_window(addr)
        if 0xC5 in registers:
            result['clut_format_seen']=registers[0xC5]&3
    if trigger==0xEA:
        if 0xB2 in registers and 0xB3 in registers:
            addr=(registers[0xB2]&0xFFFFF0)|((registers[0xB3]&0xFF0000)<<8)
            result['transfer_source_address_candidate']=_hexaddr(addr)
            result['source_in_primary_2mib_vram_window']=_known_vram_window(addr)
        if 0xB4 in registers and 0xB5 in registers:
            addr=(registers[0xB4]&0xFFFFF0)|((registers[0xB5]&0xFF0000)<<8)
            result['transfer_destination_address_candidate']=_hexaddr(addr)
            result['destination_in_primary_2mib_vram_window']=_known_vram_window(addr)
        if 0xEE in registers:
            result['transfer_width_pixels_seen']=(registers[0xEE]&0x3FF)+1
            result['transfer_height_pixels_seen']=((registers[0xEE]>>10)&0x3FF)+1
        result['transfer_bpp_bytes_seen']=4 if (registers[0xEA]&1) else 2
    return result


def _zstd_decompress(compressed:bytes,expected:int)->bytes:
    """Decompress into an exactly sized, bounded output buffer."""
    if not 0<=expected<=MAX_PAYLOAD:
        raise ValueError('Uncompressed length outside safe limit')
    if not compressed or len(compressed)>MAX_COMPRESSED:
        raise ValueError('Compressed data outside safe limit')
    try:
        zstd=ctypes.CDLL('libzstd.so.1')
    except OSError as exc:
        raise RuntimeError('libzstd.so.1 is required') from exc
    zstd.ZSTD_decompress.argtypes=[ctypes.c_void_p,ctypes.c_size_t,ctypes.c_void_p,ctypes.c_size_t]
    zstd.ZSTD_decompress.restype=ctypes.c_size_t
    zstd.ZSTD_isError.argtypes=[ctypes.c_size_t]
    zstd.ZSTD_isError.restype=ctypes.c_uint
    src=ctypes.create_string_buffer(compressed)
    dst=ctypes.create_string_buffer(max(expected,1))
    n=zstd.ZSTD_decompress(dst,expected,src,len(compressed))
    if zstd.ZSTD_isError(n) or n!=expected:
        raise ValueError('Invalid zstd frame or decompressed length')
    return dst.raw[:n]


def _compressed_block(blob:bytes,pos:int,expected:int)->tuple[bytes,int]:
    if pos+4>len(blob):
        raise ValueError('Missing zstd size')
    n=struct.unpack_from('<I',blob,pos)[0]
    pos+=4
    if not 0<n<=MAX_COMPRESSED or pos+n>len(blob):
        raise ValueError('Zstd block truncated or too large')
    return _zstd_decompress(blob[pos:pos+n],expected),pos+n


def inspect(blob:bytes)->dict:
    if len(blob)<HEADER_SIZE or blob[:8]!=MAGIC:
        raise ValueError('Invalid PPSSPP GE dump magic')
    version=struct.unpack_from('<I',blob,8)[0]
    if version!=VERSION:
        raise ValueError('Only PPSSPP v1.20.4 GE dump v6 supported')
    game_id=blob[12:21].split(b'\0',1)[0]
    if not game_id or any(not (ord('A')<=ch<=ord('Z') or ord('0')<=ch<=ord('9')) for ch in game_id):
        raise ValueError('Invalid game ID in GE header')
    num,bufsz=struct.unpack_from('<II',blob,24)
    if not 0<num<=MAX_CMDS or not 0<bufsz<=MAX_PAYLOAD:
        raise ValueError('Command count or pushbuffer size invalid')
    commands,pos=_compressed_block(blob,HEADER_SIZE,num*COMMAND_STRIDE)
    pushbuf,pos=_compressed_block(blob,pos,bufsz)
    if pos!=len(blob):
        raise ValueError('Unexpected trailing dump payload')
    kinds=collections.Counter()
    ge=collections.Counter()
    findings=[]
    address_observations=[]
    gpu_registers_seen={}
    total_ge_address_triggers=0
    for i in range(num):
        kind,sz,ptr=struct.unpack_from('<BII',commands,i*COMMAND_STRIDE)
        if kind not in KINDS:
            raise ValueError(f'Unknown recorder command type {kind} at {i}')
        if ptr>bufsz or sz>bufsz-ptr:
            raise ValueError(f'Out-of-bounds pushbuffer span at {i}')
        kinds[KINDS[kind]]+=1
        if kind==1:
            if sz%4:
                raise ValueError('REGISTERS length is not aligned to 4 bytes')
            for j in range(0,sz,4):
                word=struct.unpack_from('<I',pushbuf,ptr+j)[0]
                op=word>>24
                gpu_registers_seen[op]=word&0x00FFFFFF
                if op in (0x04,0xEA):
                    total_ge_address_triggers+=1
                    if len(address_observations)<MAX_GE_ADDRESS_OBSERVATIONS:
                        event={'recorder_index':i,'word_index':j//4,
                               'trigger':'PRIM' if op==0x04 else 'TRANSFERSTART',
                               'state_completeness':'PARTIAL_ONLY_REGISTERS_OBSERVED_IN_DUMP'}
                        if op==0x04:event['primitive_vertex_count_seen']=word&0xFFFF
                        event.update(ge_addresses_from_state(gpu_registers_seen,op))
                        address_observations.append(event)
                if op in GE_NAMES:
                    ge[GE_NAMES[op]]+=1
                    if len(findings)<150 and op in (0x04,0xB0,0xB1,0xB2,0xB3,0xB4,0xB5,0xC2,0xC3,0xC5,0xEA):
                        findings.append({'recorder_index':i,'word_index':j//4,'opcode':GE_NAMES[op]})
    return {'schema':'cladun.f2.ppsspp_ge_dump_v6_static.v1',
            'scope':'AUTHENTIC_DUMP_ONLY_IF_GENUINE_INPUT; NO_MIPS_PC_PROOF',
            'dump_sha256':hashlib.sha256(blob).hexdigest(),
            'dump_size':len(blob),'record_version':version,
            'game_id':game_id.decode('ascii'),'recorded_command_count':num,
            'pushbuffer_size':bufsz,'recorded_types':dict(sorted(kinds.items())),
            'ge_register_opcode_counts':dict(sorted(ge.items())),
            'command_positions_limited_to_150':findings,
            'ge_address_candidates_limited_to_150':address_observations,
            'ge_address_trigger_count_total':total_ge_address_triggers,
            'addresses_are_partial_unverified_candidates':True,
            'mips_pc_proven':False,'texture_identity_proven':False,
            'vram_upload_proven':False,'visual_context_proven':False}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--entrada-privada',type=Path,required=True)
    p.add_argument('--reporte-privado',type=Path,required=True)
    args=p.parse_args()
    if args.entrada_privada.resolve()==args.reporte_privado.resolve() or args.reporte_privado.exists():
        raise ValueError('Report must be new; never overwrite input')
    if args.entrada_privada.stat().st_size>MAX_COMPRESSED*2+HEADER_SIZE+8:
        raise ValueError('Dump file too large')
    output=inspect(args.entrada_privada.read_bytes())
    args.reporte_privado.parent.mkdir(parents=True,exist_ok=True)
    with args.reporte_privado.open('x',encoding='utf-8') as f:
        json.dump(output,f,indent=2,ensure_ascii=False)
        f.write('\n')
    print(json.dumps({k:v for k,v in output.items() if k!='command_positions_limited_to_150'},indent=2))

if __name__=='__main__':
    main()
