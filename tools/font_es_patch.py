#!/usr/bin/env python3
"""Experimental, fail-closed Spanish FONT.ARC prototype for Cladun USA PSP.

Requires an independently owned, exact-match ISO. Creates a separate private ISO
only when --candidate is supplied. Never distribute the ISO or the font atlas.
Does not prove PPSSPP rendering, string-parser semantics or full localization.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import struct
from pathlib import Path

from extract_cladun import iso9660_entries, read_iso_file, pspfs_entries, dsarc_entries

SOURCE_SHA256 = 'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
CHARACTERS = 'áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō'
BASE_GLYPHS = 'aeiouAEIOUnNuU?!<>o'
CODE_BASE = 0xF5A0
FONT_05_BYTES_PER_ROW = 256
ATLAS_WIDTH, ATLAS_HEIGHT = 512, 256
SLOT_PIXELS = 16

def ensure(ok: bool, why: str) -> None:
    if not ok:
        raise ValueError(why)

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def u16(buf: bytes, at: int = 0) -> int:
    return struct.unpack_from('<H', buf, at)[0]

def u32(buf: bytes, at: int = 0) -> int:
    return struct.unpack_from('<I', buf, at)[0]

def archive(iso: Path):
    ensure(sha256_file(iso) == SOURCE_SHA256, 'No corresponde a la ISO USA analizada')
    _, items = iso9660_entries(iso)
    data = next((x for x in items if x['path'] == 'PSP_GAME/USRDIR/DATA.DAT'), None)
    ensure(data is not None, 'Falta DATA.DAT')
    pack = read_iso_file(iso, data)
    files = pspfs_entries(pack)
    ensure(len(files) == 349, 'Recuento PSPFS inesperado')
    font = next(x for x in files if x['name'] == 'FONT.ARC')
    ensure(font['size_expanded'] == 0, 'FONT.ARC no es un recurso RAW')
    start, size = font['offset'], font['size_stored']
    value = pack[start:start+size]
    members = dsarc_entries(value)
    ensure([m['name'] for m in members] == ['FONT.BIN'] + [f'FONT_{i:02d}.IMY' for i in range(6)], 'Estructura FONT.ARC inesperada')
    return data, pack, files, font, value, members

def unswizzle(raw: bytes, width_bytes: int = FONT_05_BYTES_PER_ROW, rows: int = ATLAS_HEIGHT) -> bytes:
    ensure(len(raw) == width_bytes * rows and width_bytes % 16 == 0 and rows % 8 == 0, 'Swizzle dimensiones no válidas')
    dst = bytearray(len(raw))
    for by in range(rows // 8):
        for bx in range(width_bytes // 16):
            src = (by * (width_bytes // 16) + bx) * 128
            for yy in range(8):
                to = (by*8+yy)*width_bytes + bx*16
                dst[to:to+16] = raw[src+yy*16:src+yy*16+16]
    return bytes(dst)

def swizzle(raw: bytes, width_bytes: int = FONT_05_BYTES_PER_ROW, rows: int = ATLAS_HEIGHT) -> bytes:
    ensure(len(raw) == width_bytes * rows, 'Longitud de imagen no válida')
    dst = bytearray(len(raw))
    for by in range(rows // 8):
        for bx in range(width_bytes // 16):
            dest = (by * (width_bytes // 16) + bx) * 128
            for yy in range(8):
                src = (by*8+yy)*width_bytes + bx*16
                dst[dest+yy*16:dest+yy*16+16] = raw[src:src+16]
    return bytes(dst)

def decode_imy_texture(data: bytes) -> bytes:
    ensure(data[:4] == b'IMY\x00' and data[10] == 0xA4, 'No es imagen IMY PSP 0xA4')
    stride, rows = u16(data, 8), u16(data, 12)
    ensure((stride, rows) == (256, 256), 'Dimensiones del atlas diferentes')
    flags_at = u16(data, 4)
    flags_count = u16(data, flags_at)
    flags = data[flags_at+2:flags_at+2+flags_count]
    reader, minimum = flags_at+2+flags_count, flags_at+2+flags_count
    out = bytearray()
    for fl in flags:
        if len(out) >= stride*rows: break
        if fl & 0xC0 == 0xC0:
            gap = (2, stride, stride+2, stride-2)[(fl >> 4) & 3]
            ensure(len(out) >= gap, 'Referencia IMY fuera de límites')
            for _ in range((fl & 15) + 1):
                off = len(out)-gap
                out.extend(out[off:off+2])
        elif fl & 0xF0:
            gap = (fl-16)*2+2
            ensure(reader-gap >= minimum, 'Literal IMY fuera de límites')
            out.extend(data[reader-gap:reader-gap+2])
        else:
            amount = (fl+1)*2
            ensure(reader+amount <= len(data), 'IMY truncado')
            out.extend(data[reader:reader+amount]); reader += amount
    ensure(len(out) == stride*rows, 'Imagen IMY no se descomprimió completamente')
    return bytes(out)

def encode_imy_texture(raw: bytes, original_header: bytes) -> bytes:
    ensure(len(raw) == 65536 and len(raw)%2 == 0, 'Texture input not 4bpp')
    stride = u16(original_header, 8)
    words = [raw[i:i+2] for i in range(0, len(raw), 2)]
    n = len(words)
    dist = (2, stride, stride+2, stride-2)
    matches = {d: [0]*n for d in dist}
    for d, arr in matches.items():
        word_distance = d//2
        for i in range(n-1,word_distance-1,-1):
            if words[i] == words[i-word_distance]:
                arr[i] = min(16, 1+(arr[i+1] if i+1<n else 0))
    flags, literals, recent, run = bytearray(),bytearray(),{},bytearray()
    def flush():
        nonlocal run
        for at in range(0,len(run),32):
            part = run[at:at+32]; flags.append(len(part)//2 -1)
            source = len(literals); literals.extend(part)
            for k in range(0,len(part),2): recent[bytes(part[k:k+2])] = source+k
        run = bytearray()
    i=0
    while i<n:
        length,kind=0,-1
        for index,gap in enumerate(dist):
            if matches[gap][i]>length:
                length,kind=matches[gap][i],index
        if length:
            if run:flush()
            flags.append(0xC0+(kind<<4)+length-1); i+=length;continue
        old=recent.get(words[i])
        if old is not None:
            delta=len(literals)+len(run)-old
            if 2<=delta<=352 and delta%2==0:
                if run:flush()
                flags.append(0x10+(delta-2)//2);i+=1;continue
        run.extend(words[i]);i+=1
        if len(run)==32:flush()
    if run:flush()
    header_size = u16(original_header, 4)
    ensure(header_size >= 16, 'Cabecera IMY inválida')
    return original_header[:header_size]+struct.pack('<H',len(flags))+bytes(flags)+bytes(literals)

def nibble(raw: bytes|bytearray, x: int, y: int) -> int:
    index = y*FONT_05_BYTES_PER_ROW+x//2
    return (raw[index] >> (4 if x%2 else 0)) & 15

def put(raw: bytearray, x: int, y: int, value: int) -> None:
    index=y*FONT_05_BYTES_PER_ROW+x//2
    old=raw[index]
    raw[index] = (old & (0x0F if x%2 else 0xF0)) | ((value & 15) << (4 if x%2 else 0))

def make_glyph(existing: list[list[int]], letter: str) -> list[list[int]]:
    if letter in 'ÁÉÍÓÚÑÜ':
        img=[[0]*16 for _ in range(16)]
        for y in range(14):img[y+2] = existing[y][:]
    else:img=[row[:] for row in existing]
    def pixel(x,y,val=15): img[y][x]=val
    if letter in 'áéíóúÁÉÍÓÚ':
        if letter=='í':
            for x in (2,3):
                for y in (3,4):pixel(x,y,0)
        for x,y in [(3,0),(4,0),(2,1),(3,1)]:pixel(x,y)
    elif letter in 'ñÑ':
        for x,y in [(1,0),(2,0),(3,1),(4,1),(5,0),(6,0)]:pixel(x,y)
    elif letter in 'üÜ':
        for x,y in [(1,0),(2,0),(1,1),(2,1),(5,0),(6,0),(5,1),(6,1)]:pixel(x,y)
    elif letter in '¿¡':
        # A 180-degree turn displaces the raster to the RIGHT of the 16x16
        # cell. Restore the original left bearing after the rotation; otherwise
        # the inverted punctuation bleeds into the following character.
        original_x = min((x for row in existing for x, val in enumerate(row)
                          if val), default=0)
        turned = [list(reversed(row)) for row in reversed(img)]
        rotated_x = min((x for row in turned for x, val in enumerate(row)
                         if val), default=original_x)
        delta = rotated_x - original_x
        if delta > 0:
            img = [row[delta:] + [0] * delta for row in turned]
        elif delta < 0:
            img = [[0] * (-delta) + row[:delta] for row in turned]
        else:
            img = turned
    elif letter in '«»':
        img=[[0]*16 for _ in range(16)]
        left=[(3,4),(2,5),(1,6),(0,7),(1,9),(2,10),(3,11),
              (7,4),(6,5),(5,6),(4,7),(5,9),(6,10),(7,11)]
        for x,y in left:pixel(x if letter=='«' else 7-x,y)
    elif letter=='ō':
        for x,y in [(2,0),(3,0),(4,0),(5,0)]:pixel(x,y)
    return img

def patched_archive(font_arc: bytes, members: list[dict]) -> tuple[bytes, dict]:
    font = bytearray(font_arc)
    tab = members[0]
    count = u32(font_arc, tab['offset'])
    ensure(count == 2721, 'Cambió el número de glifos base')
    old_table = font_arc[tab['offset']:tab['offset']+tab['size']]
    codes = [u16(old_table,4+i*4) for i in range(count)]
    ensure(codes == sorted(codes) and len(set(codes))==count, 'Tabla original no ordenada')
    ensure(max(codes) < CODE_BASE and CODE_BASE+len(CHARACTERS)-1 <= 0xF5FC, 'Códigos nuevos sin orden')
    old_indices={code:i for i,code in enumerate(codes)}
    extension=bytearray()
    for i,base in enumerate(BASE_GLYPHS):
        cp=ord(base)
        ensure(cp in old_indices, f'Glifo original ausente: {base}')
        base_idx=old_indices[cp]
        rec=old_table[4+base_idx*4:4+(base_idx+1)*4]
        extension.extend(struct.pack('<H',CODE_BASE+i)+rec[2:4])
    ensure(len(extension)==len(CHARACTERS)*4, 'Mapping length mismatch')
    ensure(not any(font_arc[tab['offset']+tab['size']:tab['offset']+tab['size']+len(extension)]), 'FONT.BIN no dispone de padding vacío')
    ensure(tab['offset']+tab['size']+len(extension)<members[1]['offset'], 'FONT.BIN sobreescribe otra página')
    struct.pack_into('<I',font,tab['offset'],count+len(CHARACTERS))
    font[tab['offset']+tab['size']:tab['offset']+tab['size']+len(extension)] = extension
    ensure(font_arc[:8]==b'DSARCIDX','Esperado DSARCIDX')
    table_start=(16+len(members)*2+3)//4*4
    struct.pack_into('<I',font,table_start+40,tab['size']+len(extension))
    image=members[-1]
    old_image=font_arc[image['offset']:image['offset']+image['size']]
    linear=bytearray(unswizzle(decode_imy_texture(old_image)))
    original_pixels=bytes(linear)
    font_pages=[]
    for m in members[1:]:
        raw = font_arc[m['offset']:m['offset']+m['size']]
        font_pages.append(unswizzle(decode_imy_texture(raw)))
    for i,(character,base) in enumerate(zip(CHARACTERS,BASE_GLYPHS)):
        src_idx=old_indices[ord(base)]
        src_page, src_slot=divmod(src_idx,512)
        src_bytes=font_pages[src_page]
        src_x=(src_slot%32)*16;src_y=(src_slot//32)*16
        base_glyph=[[nibble(src_bytes,src_x+x,src_y+y) for x in range(16)] for y in range(16)]
        glyph=make_glyph(base_glyph,character)
        slot=count+i-5*512
        ensure(0<=slot<512, 'No hay espacio para 19 glifos en FONT_05')
        target_x=(slot%32)*16;target_y=(slot//32)*16
        for yy in range(16):
            for xx in range(16):
                ensure(nibble(linear,target_x+xx,target_y+yy)==0, f'Atlas no está vacío: posición {slot}')
        for yy in range(16):
            for xx in range(16):put(linear,target_x+xx,target_y+yy,glyph[yy][xx])
    encoded=encode_imy_texture(swizzle(bytes(linear)),old_image)
    ensure(decode_imy_texture(encoded)==swizzle(bytes(linear)), 'Roundtrip IMY falló')
    new_imy_len=(len(encoded)+3)//4*4
    new_archive_len=max(len(font_arc),image['offset']+new_imy_len)
    new_archive_len=(new_archive_len+15)//16*16
    result=bytearray(new_archive_len)
    result[:len(font)] = font
    result[image['offset']:image['offset']+len(encoded)] = encoded
    struct.pack_into('<I',result,table_start+(len(members)-1)*48+40,new_imy_len)
    ensure(len(result)>=len(font_arc), 'Disminución no permitida')
    ensure([(e['name'],e['offset']) for e in dsarc_entries(result)]==[(e['name'],e['offset']) for e in members], 'Índice fuente desplazado')
    return bytes(result), {'old_codes':len(codes),'new_codes':len(codes)+len(CHARACTERS),'first_new':f'{CODE_BASE:04X}',
                           'last_new':f'{CODE_BASE+len(CHARACTERS)-1:04X}',
                           'old_font_bytes':len(font_arc),'new_font_bytes':len(result),'image_05_original_size':image['size'],
                           'image_05_new_size':new_imy_len,'new_glyph_pixels':sum(a!=b for a,b in zip(linear,original_pixels))}

def build(source_iso: Path, candidate: Path) -> dict:
    source_iso=source_iso.resolve();candidate=candidate.resolve()
    ensure(source_iso!=candidate,'Salida igual que entrada')
    dat, pack, entries, font, arc, children=archive(source_iso)
    replacement,summary=patched_archive(arc,children)
    start=font['offset'];size=font['size_stored'];new_size=len(replacement)
    next_entry=min(e['offset'] for e in entries if e['offset']>start)
    ensure(start+new_size<=next_entry, 'El archivo FONT.ARC invade otro recurso')
    ensure(not any(pack[start+size:start+new_size]),'La extensión sobrescribe bytes no nulos')
    ensure(pack[start:start+size]==arc,'Archivo fuente alterado durante análisis')
    candidate.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source_iso,candidate)
    with candidate.open('r+b') as f:
        f.seek(dat['offset']+start);f.write(replacement)
        f.seek(dat['offset']+16+font['index']*32+24);f.write(struct.pack('<I',new_size))
    summary.update({'status':'EXPERIMENTAL_FONT_CANDIDATE','iso_sha256_original':SOURCE_SHA256,
                    'iso_sha256_modified':sha256_file(candidate),'iso_size_unchanged':source_iso.stat().st_size==candidate.stat().st_size,
                    'pspfs_entries':len(entries),'other_resources_untouched_by_builder':len(entries)-1,
                    'font_end_margin':next_entry-start-new_size,
                    'emulator_render_verified':False,'full_translation_reinsertion_verified':False})
    return summary

def main() -> int:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True,help='Only local private ISO; NEVER publish')
    p.add_argument('--report',type=Path)
    args=p.parse_args()
    result=build(args.iso,args.candidate)
    raw=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    print(raw)
    if args.report:args.report.write_text(raw,encoding='utf-8')
    return 0

if __name__=='__main__':raise SystemExit(main())
