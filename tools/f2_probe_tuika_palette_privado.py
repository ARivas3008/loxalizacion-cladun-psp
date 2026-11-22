#!/usr/bin/env python3
"""Private in-place TUIKA_MES.IMY magenta CLUT probe; NOT PPSSPP gameplay.

The genuine original USA ISO is required by exact SHA. Writes an independent
PRIVATE ISO, changing 3 RGB bytes only, and validates all 348 PSPFS neighbors,
26 SYSGRA DSARC neighbors, table bytes and every other ISO byte.
Never publish the binary experiment. A successful probe does not establish
actual runtime usage of the image: that needs PPSSPP.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import struct
from pathlib import Path

ORIGINAL_SHA = 'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
ORIGINAL_SIZE = 305496064
DATA_OFFSET = 113770496
PSPFS_ENTRIES = 349
SYSGRA_INDEX = 225
SYSGRA_DATA_OFFSET = 895488
SYSGRA_SIZE = 93696
ORIGINAL_ARCHIVE_SHA = '63d9443084a2aeab8c2a3f79aebdb130eaf6c5d2e86f8be51346d7458ab81854'
TUIKA_INDEX, TUIKA_OFFSET, TUIKA_SIZE = 24, 78848, 7912
ORIGINAL_MEMBER_SHA = 'c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127'
PALETTE_INDEX = 2
BEFORE = bytes((249,251,249,255))
AFTER = bytes((255,0,255,255))

def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def hash_file(path: Path) -> str:
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(4*1024*1024),b''):
            h.update(chunk)
    return h.hexdigest()

def check_private(path: Path, suffix: str, repo: Path | None=None) -> Path:
    path=Path(path).expanduser()
    if not path.is_absolute() or path.suffix.lower()!=suffix:
        raise ValueError('Output must be absolute private path ending '+suffix)
    root=(repo or Path(__file__).resolve().parents[1]).resolve()
    target=path.resolve(strict=False)
    if target==root or root in target.parents:
        raise ValueError('Proprietary data must not be written in GitHub checkout')
    if path.exists() or target.exists():
        raise FileExistsError('Private evidence exists: will not overwrite')
    return path

def parse_dsarc(arc: bytes) -> list[dict]:
    if arc[:8]!=b'DSARC FL' or len(arc)<16 or struct.unpack_from('<I',arc,8)[0]!=27:
        raise ValueError('Invalid 27-member DSARC FL header')
    rows=[];ranges=[]
    for i in range(27):
        cell=arc[16+48*i:16+48*(i+1)]
        if len(cell)!=48:raise ValueError('Truncated DSARC table')
        name=cell[:40].split(b'\0',1)[0].decode('ascii')
        length,off=struct.unpack_from('<II',cell,40)
        if not name or length<=0 or off<16+27*48 or off+length>len(arc):
            raise ValueError('DSARC member bounds invalid')
        ranges.append((off,off+length))
        rows.append({'index':i,'name':name,'offset':off,'size':length})
    if len({r['name'] for r in rows})!=27:
        raise ValueError('Duplicate DSARC names')
    ranges.sort()
    if any(a[1]>b[0] for a,b in zip(ranges,ranges[1:])):
        raise ValueError('DSARC members overlap')
    return rows

def patch_member(member: bytes) -> tuple[bytes,list[int]]:
    if len(member)!=TUIKA_SIZE or sha(member)!=ORIGINAL_MEMBER_SHA:
        raise ValueError('Original TUIKA_MES.IMY SHA or length mismatch')
    if member[:4]!=b'IMY\0' or member[4]!=0x60 or member[10]!=0xA4:
        raise ValueError('Original IMY type unexpected')
    at=32+PALETTE_INDEX*4
    if member[at:at+4]!=BEFORE:
        raise ValueError('Original index 2 RGBA unexpected')
    changed=bytearray(member);changed[at:at+3]=AFTER[:3]
    assert changed[at+3]==BEFORE[3]
    return bytes(changed),list(range(at,at+3))

def parse_pspfs_records(header: bytes) -> list[tuple[str,int,int]]:
    if len(header)!=16+32*PSPFS_ENTRIES or header[:8]!=b'PSPFS_V1' or struct.unpack_from('<I',header,8)[0]!=349:
        raise ValueError('PSPFS header/count unexpected')
    rows=[]
    for i in range(PSPFS_ENTRIES):
        rec=header[16+i*32:16+(i+1)*32]
        name=rec[:20].split(b'\0',1)[0].decode('ascii')
        _expanded,stored,offset=struct.unpack_from('<III',rec,20)
        if not name or not stored:raise ValueError('PSPFS empty member')
        rows.append((name,offset,stored))
    if rows[SYSGRA_INDEX]!=('SYSGRA.ARC',SYSGRA_DATA_OFFSET,SYSGRA_SIZE):
        raise ValueError('SYSGRA PSPFS descriptor unexpected')
    return rows

def exact_deltas(original: Path,modified: Path,expected: dict[int,tuple[int,int]]) -> list[int]:
    changed=[]
    with Path(original).open('rb') as a,Path(modified).open('rb') as b:
        offset=0
        while True:
            before=a.read(4*1024*1024);after=b.read(4*1024*1024)
            if len(before)!=len(after):raise ValueError('ISO byte length changed')
            if before!=after:
                for i,(x,y) in enumerate(zip(before,after)):
                    if x!=y:
                        address=offset+i
                        if expected.get(address)!=(x,y):
                            raise ValueError('Unauthorized ISO byte change '+hex(address))
                        changed.append(address)
            if not before:break
            offset+=len(before)
    if set(changed)!=set(expected):raise ValueError('Missing/duplicate expected byte deltas')
    return changed

def audit_isos(usa: Path,probe: Path) -> dict:
    if usa.stat().st_size!=ORIGINAL_SIZE or probe.stat().st_size!=ORIGINAL_SIZE:
        raise ValueError('ISO size mismatch')
    with usa.open('rb') as a,probe.open('rb') as b:
        a.seek(DATA_OFFSET);b.seek(DATA_OFFSET)
        header_a=a.read(16+32*PSPFS_ENTRIES)
        header_b=b.read(16+32*PSPFS_ENTRIES)
        if header_a!=header_b:raise ValueError('PSPFS table mutated')
        entries=parse_pspfs_records(header_a)
        neighbors=0
        for i,(name,off,length) in enumerate(entries):
            a.seek(DATA_OFFSET+off);b.seek(DATA_OFFSET+off)
            x=a.read(length);y=b.read(length)
            if len(x)!=length or len(y)!=length:
                raise ValueError('PSPFS member truncated')
            if i==SYSGRA_INDEX:
                original_arc,probe_arc=x,y
                if sha(x)!=ORIGINAL_ARCHIVE_SHA:
                    raise ValueError('Original SYSGRA SHA mismatch')
            else:
                if x!=y:raise ValueError('Unrelated PSPFS member modified '+name)
                neighbors+=1
    original_members=parse_dsarc(original_arc)
    probe_members=parse_dsarc(probe_arc)
    if original_members!=probe_members or original_arc[:1312]!=probe_arc[:1312]:
        raise ValueError('DSARC table modified')
    other=0
    for i,r in enumerate(original_members):
        start=r['offset'];end=start+r['size']
        if i==TUIKA_INDEX:
            if (r['name'],start,r['size'])!=('TUIKA_MES.IMY',TUIKA_OFFSET,TUIKA_SIZE):
                raise ValueError('Unexpected TUIKA DSARC row')
            expected_member,inner_offsets=patch_member(original_arc[start:end])
            if probe_arc[start:end]!=expected_member:
                raise ValueError('Probe member violates 3-byte invariant')
        else:
            if original_arc[start:end]!=probe_arc[start:end]:
                raise ValueError('Unrelated DSARC member modified')
            other+=1
    location=DATA_OFFSET+SYSGRA_DATA_OFFSET+TUIKA_OFFSET
    changes=exact_deltas(usa,probe,{location+i:(BEFORE[k],AFTER[k]) for k,i in enumerate(inner_offsets)})
    usa_sha=hash_file(usa)
    if usa_sha!=ORIGINAL_SHA:
        raise ValueError('Source USA SHA changed')
    return {
        'schema':'cladun.f2.private_tuika_rgba2_probe.v1',
        'scope':'STATIC_ISO_EXPERIMENT_NOT_PPSSPP',
        'original_iso_sha256':usa_sha,'probe_iso_sha256':hash_file(probe),
        'original_archive_sha256':sha(original_arc),
        'probe_archive_sha256':sha(probe_arc),
        'original_member_sha256':sha(original_arc[TUIKA_OFFSET:TUIKA_OFFSET+TUIKA_SIZE]),
        'probe_member_sha256':sha(probe_arc[TUIKA_OFFSET:TUIKA_OFFSET+TUIKA_SIZE]),
        'changed_byte_count':len(changes),'changed_absolute_iso_offsets':changes,
        'original_palette_rgba':list(BEFORE),'probe_palette_rgba':list(AFTER),
        'alpha_unchanged':True,'pspfs_count':349,'pspfs_neighbors_unchanged':neighbors,
        'dsarc_count':27,'dsarc_neighbors_unchanged':other,
        'pspfs_table_unchanged':True,'dsarc_table_unchanged':True,
        'no_other_iso_bytes_modified':True,
        'ppsspp_executed':False,'gameplay_usage_proven':False,
        'public_game_assets_included':False
    }

def build_probe(original: Path,output: Path,report: Path) -> dict:
    original=Path(original)
    output=check_private(output,'.iso')
    report=check_private(report,'.json')
    if original.resolve()==output.resolve() or output.resolve()==report.resolve():
        raise ValueError('Input/output paths collide')
    if original.stat().st_size!=ORIGINAL_SIZE or hash_file(original)!=ORIGINAL_SHA:
        raise ValueError('Original USA SHA/size invalid')
    with original.open('rb') as f:
        f.seek(DATA_OFFSET)
        records=parse_pspfs_records(f.read(16+32*PSPFS_ENTRIES))
        _,off,length=records[SYSGRA_INDEX]
        f.seek(DATA_OFFSET+off)
        arc=f.read(length)
    if sha(arc)!=ORIGINAL_ARCHIVE_SHA:
        raise ValueError('Original archive SHA invalid')
    member=parse_dsarc(arc)[TUIKA_INDEX]
    if (member['name'],member['offset'],member['size'])!=('TUIKA_MES.IMY',TUIKA_OFFSET,TUIKA_SIZE):
        raise ValueError('Unexpected TUIKA member')
    _,relative=patch_member(arc[TUIKA_OFFSET:TUIKA_OFFSET+TUIKA_SIZE])
    absolute=DATA_OFFSET+off+TUIKA_OFFSET+relative[0]
    output.parent.mkdir(parents=True,exist_ok=True)
    report.parent.mkdir(parents=True,exist_ok=True)
    try:
        with original.open('rb') as a, output.open('xb') as b:
            shutil.copyfileobj(a,b,4*1024*1024)
        with output.open('r+b') as f:
            f.seek(absolute);f.write(AFTER[:3])
        result=audit_isos(original,output)
        result['private_iso_basename']=output.name
        with report.open('x',encoding='utf-8') as f:
            json.dump(result,f,ensure_ascii=False,indent=2)
            f.write('\n')
        return result
    except Exception:
        if output.exists():output.unlink()
        raise

def main() -> None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso-usa',type=Path,required=True)
    p.add_argument('--salida-iso-privada',type=Path,required=True)
    p.add_argument('--reporte-privado',type=Path,required=True)
    args=p.parse_args()
    report=build_probe(args.iso_usa,args.salida_iso_privada,args.reporte_privado)
    print(json.dumps({k:report[k] for k in ('changed_byte_count','changed_absolute_iso_offsets','pspfs_neighbors_unchanged','dsarc_neighbors_unchanged','ppsspp_executed')},ensure_ascii=False))

if __name__=='__main__':
    main()
