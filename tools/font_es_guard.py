#!/usr/bin/env python3
"""Independent fail-closed verifier for experimental Cladun Spanish font ISO.

Checks every original ISO and PSPFS byte outside whitelisted FONT.ARC spans;
preserves the 2,721 original font records and pixels. Cannot prove game
rendering or that the engine interprets added codes correctly.
"""
from __future__ import annotations
import argparse
import json
import struct
from pathlib import Path
from extract_cladun import iso9660_entries, read_iso_file, pspfs_entries, dsarc_entries
from font_es_patch import (SOURCE_SHA256, CHARACTERS, CODE_BASE, decode_imy_texture,
                           unswizzle, nibble, ensure, sha256_file)

def outside_equal(a: bytes, b: bytes, allowed: list[tuple[int,int]], where: str):
    ensure(len(a)==len(b),f'{where}: size mismatch')
    pos=0
    for left,right in sorted(allowed):
        ensure(pos<=left<right<=len(a),f'{where}: invalid or overlapping allowed span')
        ensure(a[pos:left]==b[pos:left],f'{where}: unauthorized bytes preceding position {left}')
        pos=right
    ensure(a[pos:]==b[pos:],f'{where}: unauthorized trailing bytes')

def same_file_except(a: Path,b: Path,start: int,end: int):
    ensure(a.stat().st_size==b.stat().st_size,'ISO size changed')
    with a.open('rb') as fa,b.open('rb') as fb:
        for s,t in [(0,start),(end,a.stat().st_size)]:
            fa.seek(s); fb.seek(s)
            while s<t:
                n=min(1024*1024,t-s)
                ensure(fa.read(n)==fb.read(n),'ISO bytes outside DATA.DAT changed')
                s+=n

def inspect(iso: Path):
    _,entries=iso9660_entries(iso)
    data=next((e for e in entries if e['path']=='PSP_GAME/USRDIR/DATA.DAT'),None)
    ensure(data is not None,'No DATA.DAT found')
    pack=read_iso_file(iso,data)
    table=pspfs_entries(pack)
    return entries,data,pack,table

def verify(source: Path, candidate: Path) -> dict:
    source,candidate=source.resolve(),candidate.resolve()
    ensure(source!=candidate,'Cannot compare file to itself')
    ensure(sha256_file(source)==SOURCE_SHA256,'Source ISO checksum invalid')
    aa,a_iso,a,a_entries=inspect(source)
    bb,b_iso,b,b_entries=inspect(candidate)
    ensure(aa==bb,'ISO9660 file table/path/size/offset changed')
    ensure(a_iso==b_iso,'DATA.DAT extent changed')
    same_file_except(source,candidate,a_iso['offset'],a_iso['offset']+a_iso['size'])
    ensure(len(a_entries)==len(b_entries)==349,'Wrong PSPFS entry count')
    for x,y in zip(a_entries,b_entries):
        for field in ('name','index','offset','size_expanded'):
            ensure(x[field]==y[field],f'PSPFS shifted or modified: {x["name"]}.{field}')
        if x['name']!='FONT.ARC':
            ensure(x['size_stored']==y['size_stored'], f'Other resource size changed: {x["name"]}')
            start=x['offset'];n=x['size_stored']
            ensure(a[start:start+n]==b[start:start+n],f'Another PSPFS resource changed: {x["name"]}')
    f0=next(e for e in a_entries if e['name']=='FONT.ARC')
    f1=next(e for e in b_entries if e['name']=='FONT.ARC')
    old_len,new_len=f0['size_stored'],f1['size_stored']
    start=f0['offset']
    ensure(old_len<new_len,'Font was not expanded')
    end=min(x['offset'] for x in a_entries if x['offset']>start)
    ensure(start+new_len<=end,'FONT.ARC overlaps the next resource')
    ensure(not any(a[start+old_len:start+new_len]),'Nonempty padding consumed')
    arc_a=a[start:start+old_len];arc_b=b[start:start+new_len]
    x=dsarc_entries(arc_a);y=dsarc_entries(arc_b)
    ensure(len(x)==len(y)==7,'Unexpected number of font members')
    ensure([(m['name'],m['offset']) for m in x]==[(m['name'],m['offset']) for m in y], 'Font member offset shifted')
    assert x[0]['name']=='FONT.BIN' and x[-1]['name']=='FONT_05.IMY'
    for orig,new in zip(x[1:-1],y[1:-1]):
        ensure(orig['size']==new['size'],f'Unrelated font page size changed: {orig["name"]}')
        u,v=orig['offset'],orig['size']
        ensure(arc_a[u:u+v]==arc_b[u:u+v],f'Older font page changed: {orig["name"]}')
    oldbin=arc_a[x[0]['offset']:x[0]['offset']+x[0]['size']]
    newbin=arc_b[y[0]['offset']:y[0]['offset']+y[0]['size']]
    count=struct.unpack_from('<I',oldbin)[0]
    ensure(count==2721,'Font original count mismatch')
    ensure(struct.unpack_from('<I',newbin)[0]==count+len(CHARACTERS),'New font count mismatch')
    ensure(y[0]['size']==x[0]['size']+4*len(CHARACTERS),'Font table grew wrong size')
    ensure(oldbin[4:]==newbin[4:len(oldbin)],'Existing font records altered')
    codes=[struct.unpack_from('<H',newbin,4+4*i)[0] for i in range(count+len(CHARACTERS))]
    ensure(codes==sorted(codes) and len(set(codes))==len(codes),'Font index unsorted or duplicated')
    ensure(codes[count:]==list(range(CODE_BASE,CODE_BASE+len(CHARACTERS))),'New font codes inconsistent with codec')
    last_a=arc_a[x[-1]['offset']:x[-1]['offset']+x[-1]['size']]
    last_b=arc_b[y[-1]['offset']:y[-1]['offset']+y[-1]['size']]
    old_atlas=unswizzle(decode_imy_texture(last_a))
    new_atlas=unswizzle(decode_imy_texture(last_b))
    ensure(len(old_atlas)==len(new_atlas)==65536,'Decoded font atlas size changed')
    changed=0
    written=set(range(count-5*512,count-5*512+len(CHARACTERS)))
    for offset,(p,q) in enumerate(zip(old_atlas,new_atlas)):
        if p==q:continue
        yy=offset//256;xx=(offset%256)*2
        for n in (0,1):
            old=(p>>(4*n))&15;new=(q>>(4*n))&15
            if old==new:continue
            slot=(yy//16)*32+(xx+n)//16
            ensure(slot in written,f'Older font glyph pixel modified: slot {slot} pixel ({xx+n},{yy})')
            changed+=1
    ensure(changed>0,'No font pixels actually changed')
    for slot in written:
        x0=(slot%32)*16;y0=(slot//32)*16
        ensure(any(nibble(new_atlas,x0+xx,y0+yy) for yy in range(16) for xx in range(16)),f'New glyph is blank: {slot}')
    base=(16+len(x)*2+3)//4*4
    allowed_arc=[(base+40,base+44),
                 (base+(len(x)-1)*48+40,base+(len(x)-1)*48+44),
                 (x[0]['offset'],x[0]['offset']+4),
                 (x[0]['offset']+x[0]['size'],x[0]['offset']+y[0]['size']),
                 (x[-1]['offset'],y[-1]['offset']+y[-1]['size'])]
    oldpadded=arc_a+bytes(new_len-old_len)
    outside_equal(oldpadded,arc_b,allowed_arc,'FONT.ARC')
    font_meta=16+f0['index']*32+24
    outside_equal(a,b,[(font_meta,font_meta+4),(start,start+new_len)],'DATA.DAT')
    return {
        'status':'PASS_BINARY_ISOLATION_FONT_ONLY',
        'sha256_original':sha256_file(source),
        'sha256_candidate':sha256_file(candidate),
        'pspfs_entries_verified':len(a_entries),
        'pspfs_other_resources_byte_identical':len(a_entries)-1,
        'original_font_glyphs_preserved':count,
        'new_spanish_glyphs':len(CHARACTERS),
        'new_font_code_first':f'{CODE_BASE:04X}',
        'new_font_code_last':f'{CODE_BASE+len(CHARACTERS)-1:04X}',
        'changed_pixels_in_new_slots':changed,
        'iso9660_offsets_unchanged':True,
        'pspfs_offsets_unchanged':True,
        'font_internal_member_offsets_unchanged':True,
        'font_expansion_bytes':new_len-old_len,
        'margin_before_next_resource':end-start-new_len,
        'non_font_atlas_portraits_tiles_and_sprites_bytes_unchanged':True,
        'ppsspp_render_verified':False,
        'full_text_reinsertion_verified':False,
    }

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--report',type=Path)
    args=p.parse_args()
    try:
        report=verify(args.original,args.candidate)
    except Exception as e:
        report={'status':'REJECTED','reason':str(e)}
    print(json.dumps(report,ensure_ascii=False,indent=2))
    if args.report:args.report.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return 0 if report['status'].startswith('PASS') else 1

if __name__=='__main__':raise SystemExit(main())
