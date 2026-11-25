#!/usr/bin/env python3
"""Reproducible STATIC comparison of the original and 3-byte magenta TUIKA ISO.

Measures how many original indexed pixels would change solely because of the
stored CLUT. Neither private PNG nor exact asset bytes are sent to GitHub.
NO gameplay, PPSSPP, RAM, MIPS, GE, VRAM, or runtime context is proven.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

try:
    from tools.f2_auditar_27_imy_sysgra import decode_imy
    from tools.f2_previsualizar_sysgra_privado import unswizzle_psp
except ModuleNotFoundError:
    from f2_auditar_27_imy_sysgra import decode_imy
    from f2_previsualizar_sysgra_privado import unswizzle_psp

ISO_BYTES=305496064
SOURCE_SHA='b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
PROBE_SHA='b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa'
SOURCE_MEMBER_SHA='c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127'
PROBE_MEMBER_SHA='efcf4f41f57c300476e8ce54a32dea01f242dda3fbf3fb9c4e0b582bad8f5252'
SOURCE_DECODED_SHA='3c181786f72008c144a2187d362d289d453b4f00d93fe5f8cb2facc0f23d14d5'
DATA_OFFSET=113770496
SYSGRA_OFFSET=895488
TUIKA_OFFSET=78848
TUIKA_BYTES=7912
MEMBER_ABSOLUTE=DATA_OFFSET+SYSGRA_OFFSET+TUIKA_OFFSET
PALETTE_RGB_OFFSET=32+2*4
CLUT_INDEX=2
ORIGINAL_RGBA=(249,251,249,255)
PROBE_RGBA=(255,0,255,255)

def sha256(data:bytes)->str:
    return hashlib.sha256(data).hexdigest()

def sha256_file(path:Path)->str:
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for piece in iter(lambda:stream.read(4*1024*1024),b''):
            h.update(piece)
    return h.hexdigest()

def validate_private_output(path:Path,*,repository_root:Path|None=None,extension:str='.json')->Path:
    path=Path(path).expanduser()
    if not path.is_absolute() or path.suffix.lower()!=extension:
        raise ValueError('Private output requires an absolute '+extension+' path')
    root=(repository_root or Path(__file__).resolve().parents[1]).resolve()
    resolved=path.resolve(strict=False)
    if resolved==root or root in resolved.parents:
        raise ValueError('Commercial evidence output inside GitHub checkout forbidden')
    if resolved.exists() or path.exists():
        raise FileExistsError('Private evidence already exists: refuse overwrite')
    return path

def verify_palette_only_change(original:bytes,probe:bytes)->None:
    if len(original)!=len(probe) or len(original)<98:
        raise ValueError('IMY length mismatch')
    if original[4]!=0x60 or probe[4]!=0x60 or original[10]!=0xA4 or probe[10]!=0xA4:
        raise ValueError('Unsupported IMY format')
    at=PALETTE_RGB_OFFSET
    if tuple(original[at:at+4])!=ORIGINAL_RGBA or tuple(probe[at:at+4])!=PROBE_RGBA:
        raise ValueError('Unexpected palette color')
    if original[:at]!=probe[:at] or original[at+3:]!=probe[at+3:]:
        raise ValueError('IMY data outside three RGB bytes modified')

def group_active_rows(per_row:list[int],per_row_x:list[tuple[int,int]|None])->list[dict]:
    if len(per_row)!=len(per_row_x):
        raise ValueError('Row extent geometry mismatch')
    bands=[];current=None
    for y,(count,xspan) in enumerate(zip(per_row,per_row_x)):
        if count<0 or (count>0)!=(xspan is not None):
            raise ValueError('Row counts and bounding boxes inconsistent')
        if not count:
            if current is not None:bands.append(current);current=None
            continue
        if current is None:
            current={'y_start':y,'y_end_inclusive':y,'pixel_count':0,
                     'x_min':xspan[0],'x_max_inclusive':xspan[1]}
        current['y_end_inclusive']=y
        current['pixel_count']+=count
        current['x_min']=min(current['x_min'],xspan[0])
        current['x_max_inclusive']=max(current['x_max_inclusive'],xspan[1])
    if current is not None:bands.append(current)
    return bands

def compare_members(original:bytes,probe:bytes,*,enforce_real_sha:bool=True)->tuple[dict,bytes,bytes,bytes]:
    if enforce_real_sha and (sha256(original)!=SOURCE_MEMBER_SHA or sha256(probe)!=PROBE_MEMBER_SHA):
        raise ValueError('TUIKA member SHA mismatch')
    verify_palette_only_change(original,probe)
    first,meta=decode_imy(original)
    second,_=decode_imy(probe)
    if first!=second:
        raise ValueError('Decompressed pixel indices changed')
    if enforce_real_sha and sha256(first)!=SOURCE_DECODED_SHA:
        raise ValueError('Original decoded texture SHA mismatch')
    stride=meta['width_pixels_if_4bpp']//2
    width,height=meta['width_pixels_if_4bpp'],meta['rows']
    linear=unswizzle_psp(first,stride,height)
    mask=bytearray(width*height)
    counts=[0]*16
    rows=[0]*height
    spans=[None]*height
    for y in range(height):
        xs=[]
        for off in range(stride):
            octet=linear[y*stride+off]
            x=off*2
            for dx,index in ((0,octet&15),(1,octet>>4)):
                counts[index]+=1
                if index==CLUT_INDEX:
                    px=x+dx
                    mask[y*width+px]=255
                    rows[y]+=1
                    xs.append(px)
        if xs:spans[y]=(min(xs),max(xs))
    bounds=(min((s[0] for s in spans if s),default=None),
            min((i for i,v in enumerate(rows) if v),default=None),
            max((s[1] for s in spans if s),default=None),
            max((i for i,v in enumerate(rows) if v),default=None))
    changed=counts[CLUT_INDEX]
    if changed!=sum(rows) or changed!=sum(x==255 for x in mask):
        raise ValueError('Mask/count mismatch')
    if enforce_real_sha and (width,height,changed)!=(256,256,9144):
        raise ValueError('Unexpected authentic original TUIKA pixel geometry')
    report={
      'schema':'cladun.f2.original_tuika_clut2_static_pixel_delta.v1',
      'kind':'AUTHENTIC_ISO_RESOURCE_DECODE_STATIC_NOT_PPSSPP',
      'original_member_sha256':sha256(original),'probe_member_sha256':sha256(probe),
      'decoded_pixel_index_sha256':sha256(first),'indices_unchanged_between_isos':True,
      'texture_dimensions_px':[width,height],
      'source_palette_rgba':list(ORIGINAL_RGBA),'probe_palette_rgba':list(PROBE_RGBA),
      'palette_index_changed':CLUT_INDEX,'other_palette_entries_unchanged':True,
      'swizzled_raster_bytes_identical':True,'counterfactual_changed_pixel_count':changed,
      'counterfactual_changed_pixel_fraction':round(changed/(width*height),8),
      'all_unchanged_pixel_count':width*height-changed,
      'source_index_histogram':counts,'mask_sha256':sha256(mask),
      'mask_bounds_xy_inclusive':bounds,
      'rows_with_affected_pixels':sum(x>0 for x in rows),
      'vertical_bands':group_active_rows(rows,spans),
      'row_count_sha256':sha256(struct.pack('<%dI'%len(rows),*rows)),
      'gameplay_ppsspp_executed':False,'runtime_resource_binding_proven':False,
      'can_certify_translation_complete':False,'raw_pixel_bytes_exported_in_report':False
    }
    return report,bytes(mask),linear,original

def inspect_source_and_probe(original_iso:Path,probe_iso:Path)->tuple[dict,bytes,bytes,bytes]:
    original_iso=Path(original_iso);probe_iso=Path(probe_iso)
    if original_iso.resolve()==probe_iso.resolve():
        raise ValueError('Original/probe ISO must be different files')
    for file,expected in ((original_iso,SOURCE_SHA),(probe_iso,PROBE_SHA)):
        if file.stat().st_size!=ISO_BYTES or sha256_file(file)!=expected:
            raise ValueError('ISO SHA256/size mismatch: '+file.name)
    with original_iso.open('rb') as f:
        f.seek(MEMBER_ABSOLUTE);a=f.read(TUIKA_BYTES)
    with probe_iso.open('rb') as f:
        f.seek(MEMBER_ABSOLUTE);b=f.read(TUIKA_BYTES)
    report,mask,linear,member=compare_members(a,b)
    report.update({'original_iso_sha256':SOURCE_SHA,'probe_iso_sha256':PROBE_SHA,
                   'member_absolute_iso_offset':MEMBER_ABSOLUTE,
                   'isolation_previously_verified_in_separate_report':True})
    return report,mask,linear,member

def render_private_png(path:Path,report:dict,mask:bytes,linear:bytes,original:bytes)->dict:
    try:
        from PIL import Image,ImageDraw
    except ImportError as e:
        raise RuntimeError('Pillow is needed only for private PNG creation') from e
    path=validate_private_output(path,extension='.png')
    w,h=report['texture_dimensions_px']
    colors=[tuple(original[32+4*i:36+4*i]) for i in range(16)]
    after=colors.copy();after[CLUT_INDEX]=PROBE_RGBA
    orig=Image.new('RGBA',(w,h));candidate=Image.new('RGBA',(w,h))
    colors0=[];colors1=[]
    for octet in linear:
        for idx in (octet&15,octet>>4):
            colors0.append(colors[idx]);colors1.append(after[idx])
    orig.putdata(colors0);candidate.putdata(colors1)
    surface=Image.new('RGB',(3*w,h+42),(55,55,55))
    draw=ImageDraw.Draw(surface)
    for col,picture,title in ((0,orig,'Original IMY (no PPSSPP)'),
                              (1,candidate,'CLUT2 magenta (no PPSSPP)')):
        bg=Image.new('RGB',(w,h),(79,79,79))
        bg.paste(picture,(0,0),picture)
        surface.paste(bg,(col*w,42))
        draw.text((col*w+4,12),title,fill=(255,255,255))
    diff=Image.new('RGB',(w,h),(28,28,28))
    diff.putdata([(255,0,255) if mark else (28,28,28) for mark in mask])
    surface.paste(diff,(2*w,42))
    draw.text((2*w+4,12),f'Mask of {report["counterfactual_changed_pixel_count"]} pixels',
              fill=(255,255,255))
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f:surface.save(f,format='PNG',optimize=True)
    return {'private_image_basename':path.name,'private_image_sha256':sha256_file(path),
            'private_image_bytes':path.stat().st_size,
            'private_image_dimensions':[surface.width,surface.height],
            'image_type':'STATIC_SOURCE_ASSET_PROBE_COUNTERFACTUAL_NOT_EMULATOR'}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso-usa',type=Path,required=True)
    p.add_argument('--iso-sonda',type=Path,required=True)
    p.add_argument('--reporte-privado',type=Path,required=True)
    p.add_argument('--png-privado',type=Path)
    args=p.parse_args()
    report_file=validate_private_output(args.reporte_privado)
    png=validate_private_output(args.png_privado,extension='.png') if args.png_privado else None
    if png and png.resolve()==report_file.resolve():
        raise ValueError('Private output file collision')
    report,mask,linear,member=inspect_source_and_probe(args.iso_usa,args.iso_sonda)
    if png:report.update(render_private_png(png,report,mask,linear,member))
    report_file.parent.mkdir(parents=True,exist_ok=True)
    with report_file.open('x',encoding='utf-8') as f:
        json.dump(report,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({k:report[k] for k in ('counterfactual_changed_pixel_count',
      'texture_dimensions_px','rows_with_affected_pixels','gameplay_ppsspp_executed')},
      ensure_ascii=False))

if __name__=='__main__':
    main()
