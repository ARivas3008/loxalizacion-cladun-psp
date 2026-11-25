#!/usr/bin/env python3
"""F2: alcance REAL de una sonda global CLUT2 sobre TUIKA 4bpp de ISO USA.

Solo lectura: nunca exporta atlas/IMY/ISO. Datos RGB se usan solo para
autenticación; las cuentas de texeles NO equivalen a render de PPSSPP.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

try:
    from tools.f2_tuika_proteger_subregiones import (
        REGIONS,GAPS,ISO_SIZE,ISO_SHA,MEMBER_OFFSET,MEMBER_BYTES,MEMBER_SHA,
        WIDTH,HEIGHT,INDEX_DECODED_SHA,LINEAR_PIXEL_INDEX_SHA,MASK_SHA)
    from tools.f2_auditar_27_imy_sysgra import decode_imy
    from tools.f2_previsualizar_sysgra_privado import unswizzle_psp
    from tools.f2_probe_tuika_palette_privado import exact_deltas, BEFORE, AFTER
except ModuleNotFoundError:
    from f2_tuika_proteger_subregiones import (
        REGIONS,GAPS,ISO_SIZE,ISO_SHA,MEMBER_OFFSET,MEMBER_BYTES,MEMBER_SHA,
        WIDTH,HEIGHT,INDEX_DECODED_SHA,LINEAR_PIXEL_INDEX_SHA,MASK_SHA)
    from f2_auditar_27_imy_sysgra import decode_imy
    from f2_previsualizar_sysgra_privado import unswizzle_psp
    from f2_probe_tuika_palette_privado import exact_deltas, BEFORE, AFTER

PROBE_SHA='b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa'
PROBE_MEMBER_SHA='efcf4f41f57c300476e8ce54a32dea01f242dda3fbf3fb9c4e0b582bad8f5252'
PALETTE_INDEX=2
SHA=lambda b:hashlib.sha256(b).hexdigest()


def file_sha(path:Path)->str:
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for part in iter(lambda:f.read(4*1024*1024),b''):h.update(part)
    return h.hexdigest()


def summarize_indices(indices:bytes)->dict:
    """Counts/ranges only. Every coordinate is a native 256x256 atlas coordinate."""
    if not isinstance(indices,bytes) or len(indices)!=WIDTH*HEIGHT or any(x>15 for x in indices):
        raise ValueError('Only exact 256x256 indexed 4bpp raster accepted')
    hist=Counter(indices)
    by_row=[indices[y*WIDTH:(y+1)*WIDTH].count(PALETTE_INDEX) for y in range(HEIGHT)]
    regions=[]
    all_protected=set()
    strictly_locked=set()
    for name,x0,y0,x1,y1,status,region_sha in REGIONS:
        if not (0<=x0<=x1<WIDTH and 0<=y0<=y1<HEIGHT):
            raise ValueError('Invalid subregion')
        positions={y*WIDTH+x for y in range(y0,y1+1) for x in range(x0,x1+1)}
        crop=bytes(indices[y*WIDTH+x] for y in range(y0,y1+1) for x in range(x0,x1+1))
        if status.startswith('LOCKED'):strictly_locked.update(positions)
        all_protected.update(positions)
        regions.append({'region':name,'status':status,
                        'index2_pixels_affected':crop.count(PALETTE_INDEX),
                        'region_area_pixels':len(crop),
                        'region_edit_authorized':False})
    for name,x0,y0,x1,y1 in GAPS:
        gap={y*WIDTH+x for y in range(y0,y1+1) for x in range(x0,x1+1)}
        if any(indices[z] for z in gap):
            raise ValueError('Separator is not transparent')
        all_protected.update(gap)
        strictly_locked.update(gap)
    affected={i for i,v in enumerate(indices) if v==PALETTE_INDEX}
    protected=affected&all_protected
    locked=affected&strictly_locked
    if sum(by_row)!=len(affected) or len(protected)>len(affected):
        raise AssertionError('Corrupt coverage accounting')
    affected_bbox=([min(i%WIDTH for i in affected),min(i//WIDTH for i in affected),
                    max(i%WIDTH for i in affected),max(i//WIDTH for i in affected)]
                   if affected else None)
    return {'atlas_dimensions':[WIDTH,HEIGHT],
            'index_histogram':{str(i):hist.get(i,0) for i in range(16)},
            'index2_pixels_affected':len(affected),
            'index2_affected_fraction_of_atlas':round(len(affected)/len(indices),8),
            'index2_affected_bbox_xyxy_inclusive':affected_bbox,
            'index2_affected_in_all_seven_protected_regions':len(protected),
            'index2_affected_in_strictly_locked_regions_and_gaps':len(locked),
            'index2_affected_outside_seven_regions_and_gaps':len(affected)-len(protected),
            'by_16_atlas_rows':[sum(by_row[y:y+16]) for y in range(0,HEIGHT,16)],
            'affected_counts_per_protected_region':regions,
            'clut_global_change_is_safe_translation_edit':False,
            'protected_icons_and_digits_can_change_color_if_rendered':bool(protected),
            'atlas_pixels_proven_to_be_rendered_in_game':False,
            'source_pixels_or_images_embedded':False}


def audit(usa:Path,probe:Path)->dict:
    usa,probe=Path(usa),Path(probe)
    if usa.resolve()==probe.resolve():
        raise ValueError('Source and probe must be independent files')
    if (usa.is_symlink() or probe.is_symlink() or not usa.is_file() or
        not probe.is_file() or usa.stat().st_size!=ISO_SIZE or
        probe.stat().st_size!=ISO_SIZE or file_sha(usa)!=ISO_SHA or
        file_sha(probe)!=PROBE_SHA):
        raise ValueError('Require exact original and three-byte probe ISO')
    with usa.open('rb') as f:
        f.seek(MEMBER_OFFSET);member=f.read(MEMBER_BYTES)
    with probe.open('rb') as f:
        f.seek(MEMBER_OFFSET);probe_member=f.read(MEMBER_BYTES)
    if (SHA(member)!=MEMBER_SHA or SHA(probe_member)!=PROBE_MEMBER_SHA or
        member[:3]!=b'IMY' or member[3]!=0 or member[4]!=0x60 or member[10]!=0xA4):
        raise ValueError('TUIKA content/IMY header invalid')
    changed_at=32+4*PALETTE_INDEX
    if (member[changed_at:changed_at+4]!=BEFORE or
        probe_member[changed_at:changed_at+4]!=AFTER or
        member[:changed_at]!=probe_member[:changed_at] or
        member[changed_at+4:]!=probe_member[changed_at+4:]):
        raise ValueError('Probe must alter only CLUT2 RGB')
    changed={MEMBER_OFFSET+changed_at+i:(BEFORE[i],AFTER[i]) for i in range(3)}
    exact_deltas(usa,probe,changed)
    tiled,metadata=decode_imy(member)
    probe_tiled,probe_metadata=decode_imy(probe_member)
    if (SHA(tiled)!=INDEX_DECODED_SHA or tiled!=probe_tiled or
        metadata['width_pixels_if_4bpp']!=WIDTH or metadata['rows']!=HEIGHT or
        probe_metadata['width_pixels_if_4bpp']!=WIDTH):
        raise ValueError('Decoded data changed or has invalid size')
    linear=unswizzle_psp(tiled,WIDTH//2,HEIGHT)
    indices=bytes(nib for b in linear for nib in (b&15,b>>4))
    mask=bytes(255 if i==PALETTE_INDEX else 0 for i in indices)
    if SHA(indices)!=LINEAR_PIXEL_INDEX_SHA or SHA(mask)!=MASK_SHA:
        raise ValueError('Original raster does not match certified hashes')
    summary=summarize_indices(indices)
    return {'schema':'cladun.f2.tuika_clut2_static_impact.v1',
            'category':'A_AUTHENTIC_ISO_STATIC_NOT_PPSSPP',
            'iso_usa_sha256':ISO_SHA,'probe_iso_sha256':PROBE_SHA,
            'original_tuika_member_sha256':MEMBER_SHA,
            'probe_tuika_member_sha256':PROBE_MEMBER_SHA,
            'decoded_tiled_sha256':INDEX_DECODED_SHA,
            'linear_index_sha256':LINEAR_PIXEL_INDEX_SHA,
            'index2_mask_sha256':MASK_SHA,
            'changed_absolute_rgb_bytes':list(changed),
            **summary,
            'ppsspp_executed':False,'clut_gpu_upload_seen':False,
            'mips_ram_ge_vram_proven':False,
            'interpretation':'Changing a shared palette entry can recolor locked digits/icons; this is a diagnostic probe, not a safe translated asset.'}


def private_target(path:Path,repo:Path)->Path:
    path=Path(path)
    if not path.is_absolute() or path.is_symlink() or path.suffix.lower()!='.json':
        raise ValueError('Private output must be new absolute JSON, no symlink')
    out=path.resolve(strict=False);root=repo.resolve()
    if out.exists() or out==root or root in out.parents or any((p/'.git').exists() for p in out.parents):
        raise ValueError('No overwrite or Git workspace permitted')
    return out


def main()->None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iso-usa',type=Path,required=True)
    ap.add_argument('--iso-sonda',type=Path,required=True)
    ap.add_argument('--reporte-privado',type=Path,required=True)
    args=ap.parse_args()
    output=private_target(args.reporte_privado,Path(__file__).resolve().parents[1])
    data=audit(args.iso_usa,args.iso_sonda)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as f:
        json.dump(data,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'index2_pixels_affected':data['index2_pixels_affected'],
                      'index2_affected_in_all_seven_protected_regions':
                      data['index2_affected_in_all_seven_protected_regions'],
                      'ppsspp_executed':False},ensure_ascii=False))


if __name__=='__main__':main()
