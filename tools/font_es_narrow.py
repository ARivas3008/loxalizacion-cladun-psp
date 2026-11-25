#!/usr/bin/env python3
"""Experimental narrow-width Spanish font using single-byte CP932 halfwidth codes.

The original 2721 font glyphs are *preserved exactly* at new atlas indices, with
19 Spanish glyphs inserted between ASCII and double-byte Shift-JIS entries.
Early runtime screens were checked in PPSSPP 1.20.4; full adventure remains unverified.
"""
from __future__ import annotations
import struct
from pathlib import Path
from font_es_patch import (archive,CHARACTERS,BASE_GLYPHS,make_glyph,
                           decode_imy_texture,encode_imy_texture,swizzle,unswizzle,
                           nibble,put,ensure,u16,u32,sha256_file)
from extract_cladun import dsarc_entries

CODE_BASE = 0xA1
SLOTS_PER_PAGE = 512
TOTAL_PAGES=6
PIXELS=16


def atlas_slots(page_bytes: list[bytes]) -> list[bytes]:
    """Return 3072 independent 16x16 4-bit grayscale raster cells."""
    result=[]
    for raw in page_bytes:
        for cell in range(SLOTS_PER_PAGE):
            x=(cell % 32)*16
            y=(cell // 32)*16
            result.append(bytes(nibble(raw,x+xx,y+yy) for yy in range(16) for xx in range(16)))
    return result


def encode_atlas(slots: list[bytes], original_imys: list[bytes]) -> list[bytes]:
    ensure(len(slots)==3072 and len(original_imys)==6,'Incorrect font atlas input')
    result=[]
    for p in range(6):
        raw=bytearray(65536)
        for slot in range(512):
            pixels=slots[p*512+slot]
            ensure(len(pixels)==256,'Cell pixel count invalid')
            x0=(slot%32)*16;y0=(slot//32)*16
            for yy in range(16):
                for xx in range(16):
                    put(raw,x0+xx,y0+yy,pixels[yy*16+xx])
        data=encode_imy_texture(swizzle(bytes(raw)),original_imys[p])
        ensure(decode_imy_texture(data)==swizzle(bytes(raw)),
               f'Failed verified IMY recompression for atlas page {p}')
        result.append(data)
    return result


def whiten_new_glyph_pixels(generated):
    """F2 experimental: palette index 15 is yellow in FONT_00.IMY, 1 white.

    Apply ONLY to a newly generated Spanish glyph, never an original raster.
    """
    return [[1 if v == 15 else v for v in row] for row in generated]


def patched_archive_narrow(font_arc: bytes, members:list[dict], *, white_new_ink:bool=False)->tuple[bytes,dict]:
    ensure(font_arc[:8]==b'DSARCIDX' and len(members)==7,
           'Unsupported FONT.ARC container')
    ensure([m['name'] for m in members]==['FONT.BIN']+[f'FONT_{i:02d}.IMY' for i in range(6)],
           'Unexpected FONT.ARC member list')
    m=members[0];fontbin=font_arc[m['offset']:m['offset']+m['size']]
    count=u32(fontbin)
    ensure(count==2721,'Font base glyph count changed')
    recs=[fontbin[4+i*4:4+(i+1)*4] for i in range(count)]
    codes=[u16(r) for r in recs]
    ensure(codes==sorted(codes) and len(codes)==len(set(codes)),
           'Original font codes are not uniquely sorted')
    newcodes=[CODE_BASE+i for i in range(len(CHARACTERS))]
    ensure(all(0x7E<c<0x8140 and c not in codes for c in newcodes),
           'Single-byte font codes conflict with existing codes')
    insert=sum(c<CODE_BASE for c in codes)
    ensure(insert==95 and all(c<0x8140 for c in codes[:insert]),
           'Unexpected font index insertion point')
    old_index={c:i for i,c in enumerate(codes)}
    newrecs=[]
    for i,char in enumerate(CHARACTERS):
        base_code=ord(BASE_GLYPHS[i])
        base=fontbin[4+old_index[base_code]*4:4+(old_index[base_code]+1)*4]
        newrecs.append(struct.pack('<H',newcodes[i])+base[2:4])
    allrecs=recs[:insert]+newrecs+recs[insert:]
    codeoutput=[u16(x) for x in allrecs]
    ensure(codeoutput==sorted(codeoutput) and len(set(codeoutput))==len(codeoutput),
           'New font index would break binary-search order')
    newbin=struct.pack('<I',len(allrecs))+b''.join(allrecs)
    first_img=members[1]['offset']
    ensure(m['offset']+len(newbin)<first_img and
           not any(font_arc[m['offset']+m['size']:m['offset']+len(newbin)]),
           'Insufficient safe font index padding')
    orig_imys=[font_arc[entry['offset']:entry['offset']+entry['size']]
               for entry in members[1:]]
    pages=[unswizzle(decode_imy_texture(raw)) for raw in orig_imys]
    old_slots=atlas_slots(pages)
    new_slots=old_slots[:insert]
    for character,base in zip(CHARACTERS,BASE_GLYPHS):
        raster=old_slots[old_index[ord(base)]]
        matrix=[list(raster[y*16:y*16+16]) for y in range(16)]
        generated=make_glyph(matrix,character)
        if white_new_ink:
            generated=whiten_new_glyph_pixels(generated)
        new_slots.append(bytes(v for row in generated for v in row))
    new_slots.extend(old_slots[insert:count])
    new_slots.extend([bytes(256)]*(3072-len(new_slots)))
    ensure(len(new_slots)==3072,'Insufficient font atlas slots')
    for i in range(count):
        shifted_index=i+(len(CHARACTERS) if i>=insert else 0)
        ensure(new_slots[shifted_index]==old_slots[i],f'Glyph {i} changed')
    textures=encode_atlas(new_slots,orig_imys)
    # Keep DSARCIDX header and 48-byte member records; repack ONLY the font resource.
    header=bytearray(font_arc[:m['offset']])
    table_start=(16+len(members)*2+3)//4*4
    ensure(all(u16(header,16+i*2)==u16(font_arc,16+i*2) for i in range(7)),
           'Unexpected member header ordering')
    output=bytearray(header)
    all_members=[newbin]+textures
    offsets=[]
    for i,content in enumerate(all_members):
        if i==0:
            offset=m['offset']
        else:
            offset=(len(output)+511)//512*512+16
        if len(output)<offset:output.extend(bytes(offset-len(output)))
        output.extend(content)
        offsets.append(offset)
        meta=table_start+i*48
        struct.pack_into('<II',output,meta+40,len(content),offset)
    if len(output)%16:output.extend(bytes(16-len(output)%16))
    after=dsarc_entries(bytes(output))
    ensure(len(after)==7 and [x['name'] for x in after]==[x['name'] for x in members],
           'Repacked font member index invalid')
    for i,x in enumerate(after):
        ensure(x['offset']==offsets[i] and x['size']==len(all_members[i]),
               'Repacked font record mismatched its content')
    # Independent structural and pixel check after serialization.
    decoded=[unswizzle(decode_imy_texture(output[x['offset']:x['offset']+x['size']]))
             for x in after[1:]]
    actual=atlas_slots(decoded)
    for i in range(count):
        j=i+(len(CHARACTERS) if i>=insert else 0)
        ensure(actual[j]==old_slots[i],f'Original rendered glyph changed at {i}')
    for i in range(len(CHARACTERS)):
        ensure(any(actual[insert+i]),'New Spanish glyph unexpectedly blank')
    return bytes(output),{
        'mode':'single_byte_shiftjis_halfwidth',
        'original_glyphs_byte_exact_at_pixel_level':count,
        'new_glyphs':len(CHARACTERS),
        'white_new_ink_opt_in':white_new_ink,
        'old_font_arc_size':len(font_arc),
        'new_font_arc_size':len(output),
        'code_range':[hex(newcodes[0]),hex(newcodes[-1])],
        'insertion_at_index':insert,
        'atlas_pages_verified':len(decoded),
        'original_non_font_resources_modified':0,
    }


def build_narrow_font_arc_from_iso(source_iso:Path)->tuple[bytes,dict]:
    _,_,_,_,arc,members=archive(Path(source_iso))
    return patched_archive_narrow(arc,members)

if __name__=='__main__':
    import json,sys
    font,summary=build_narrow_font_arc_from_iso(Path(sys.argv[1]));
    print(json.dumps(summary,indent=2))

# The helper functions below are used when the full integration pipeline
# creates its temporary Spanish-font ISO.

def build(source_iso:Path,candidate:Path)->dict:
    import shutil
    source_iso=Path(source_iso).resolve()
    candidate=Path(candidate).resolve()
    ensure(source_iso!=candidate,'Cannot overwrite original')
    dat,pack,entries,font,arc,members=archive(source_iso)
    patched,summary=patched_archive_narrow(arc,members)
    old_len=font['size_stored'];start=font['offset']
    next_offset=min(e['offset'] for e in entries if e['offset']>start)
    ensure(start+len(patched)<=next_offset,'FONT.ARC expansion overlaps another PSPFS entry')
    ensure(not any(pack[start+old_len:start+len(patched)]),
           'FONT.ARC expansion overwrites existing nonzero padding')
    ensure(not candidate.exists(),'The font candidate already exists')
    shutil.copyfile(source_iso,candidate)
    with candidate.open('r+b') as file:
        file.seek(dat['offset']+start)
        file.write(patched)
        file.seek(dat['offset']+16+font['index']*32+24)
        file.write(struct.pack('<I',len(patched)))
    summary['font_end_margin']=next_offset-start-len(patched)
    summary['candidate_sha256']=sha256_file(candidate)
    return summary


def verify(source_iso:Path,candidate:Path)->dict:
    from extract_cladun import iso9660_entries, read_iso_file,pspfs_entries,dsarc_entries
    from font_es_guard import same_file_except,outside_equal
    source_iso,candidate=Path(source_iso),Path(candidate)
    ensure(sha256_file(source_iso)=='b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f',
           'Incorrect source ISO')
    ensure(source_iso.stat().st_size==candidate.stat().st_size,'Font-only ISO changed size')
    aiso,afiles=iso9660_entries(source_iso)
    biso,bfiles=iso9660_entries(candidate)
    ensure(afiles==bfiles,'ISO9660 inventory or offsets changed')
    adat=next(f for f in afiles if f['path']=='PSP_GAME/USRDIR/DATA.DAT')
    bdat=next(f for f in bfiles if f['path']=='PSP_GAME/USRDIR/DATA.DAT')
    ensure(adat==bdat,'DATA.DAT extent changed')
    same_file_except(source_iso,candidate,adat['offset'],adat['offset']+adat['size'])
    aa=read_iso_file(source_iso,adat)
    bb=read_iso_file(candidate,bdat)
    ae=pspfs_entries(aa)
    be=pspfs_entries(bb)
    ensure(len(ae)==len(be)==349,'Incorrect PSPFS member count')
    afont=next(e for e in ae if e['name']=='FONT.ARC')
    bfont=next(e for e in be if e['name']=='FONT.ARC')
    ensure(afont['index']==bfont['index'] and afont['offset']==bfont['offset'],
           'FONT.ARC moved')
    for old,new in zip(ae,be):
        if old['name']=='FONT.ARC':continue
        ensure(old==new,'PSPFS neighbor metadata changed: '+old['name'])
        ensure(aa[old['offset']:old['offset']+old['size_stored']]==
               bb[old['offset']:old['offset']+old['size_stored']],
               'PSPFS neighbor content changed: '+old['name'])
    offset=afont['offset'];size=afont['size_stored'];newsize=bfont['size_stored']
    ensure(not any(aa[offset+size:offset+newsize]),'Nonzero slot padding changed')
    meta=16+afont['index']*32+24
    outside_equal(aa,bb,[(meta,meta+4),(offset,offset+newsize)],'DATA.DAT')
    original=aa[offset:offset+size]
    generated=bb[offset:offset+newsize]
    members_old=dsarc_entries(original);members_new=dsarc_entries(generated)
    ensure([x['name'] for x in members_old]==[x['name'] for x in members_new],
           'FONT archive members rearranged')
    oldbin=original[members_old[0]['offset']:members_old[0]['offset']+members_old[0]['size']]
    newbin=generated[members_new[0]['offset']:members_new[0]['offset']+members_new[0]['size']]
    oldcodes=[u16(oldbin,4+4*i) for i in range(u32(oldbin))]
    newcodes=[u16(newbin,4+4*i) for i in range(u32(newbin))]
    ensure(u32(newbin)==u32(oldbin)+len(CHARACTERS),'Spanish index size mismatch')
    ensure(newcodes==oldcodes[:95]+list(range(CODE_BASE,CODE_BASE+len(CHARACTERS)))+oldcodes[95:],
           'Narrow font codes have wrong order')
    original_idx=[oldbin[4+i*4+2:4+i*4+4] for i in range(u32(oldbin))]
    new_idx=[newbin[4+i*4+2:4+i*4+4] for i in range(u32(newbin))]
    ensure(new_idx[:95]+new_idx[95+len(CHARACTERS):]==original_idx,
           'Original FONT.BIN glyph metrics changed')
    old_pages=[unswizzle(decode_imy_texture(original[m['offset']:m['offset']+m['size']]))
               for m in members_old[1:]]
    new_pages=[unswizzle(decode_imy_texture(generated[m['offset']:m['offset']+m['size']]))
               for m in members_new[1:]]
    old_slots=atlas_slots(old_pages)
    new_slots=atlas_slots(new_pages)
    ensure(old_slots[:95]==new_slots[:95] and
           old_slots[95:u32(oldbin)]==new_slots[95+len(CHARACTERS):u32(newbin)],
           'An existing original glyph was changed')
    ensure(all(any(s) for s in new_slots[95:95+len(CHARACTERS)]),
           'Empty new glyph')
    return {'status':'FONT_SINGLE_BYTE_BINARY_ISOLATION_PASS',
            'original_glyphs_identical':len(oldcodes),
            'new_glyphs':len(CHARACTERS),
            'non_font_pspfs_members_identical':348,
            'font_size_original':size,
            'font_size_result':newsize,
            'iso_size_identical':True,
            'ppsspp_visual_test':False}
