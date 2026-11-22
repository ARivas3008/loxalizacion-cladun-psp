#!/usr/bin/env python3
"""F2: auditoría de geometría de 19 glifos sin exportar píxeles comerciales.

Usa las funciones de reconstrucción vigentes, sin escribir ISO ni FONT.ARC.
La geometría estática no sustituye la comprobación visual en PPSSPP.
"""
from __future__ import annotations
import argparse,hashlib,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from font_es_patch import archive,CHARACTERS,BASE_GLYPHS,make_glyph,decode_imy_texture
from font_es_narrow import atlas_slots,unswizzle
from charset_es import ES_BYTES
from font_es_patch import u16,u32

def geometry(grid):
    pixels=[(x,y) for y,row in enumerate(grid) for x,v in enumerate(row) if v]
    if not pixels:return {'bbox_xyxy':None,'pixels':0}
    return {'bbox_xyxy':[min(p[0] for p in pixels),min(p[1] for p in pixels),
                         max(p[0] for p in pixels),max(p[1] for p in pixels)],
            'pixels':len(pixels)}

def audit(iso:Path)->dict:
    _,_,_,_,arc,members=archive(iso)  # SHA-256 USA comprobado
    m=members[0];fontbin=arc[m['offset']:m['offset']+m['size']]
    count=u32(fontbin)
    if count!=2721:raise ValueError('FONT original inesperada')
    recs=[fontbin[4+i*4:8+i*4] for i in range(count)]
    codes=[u16(r) for r in recs]
    if codes!=sorted(codes) or len(codes)!=len(set(codes)):raise ValueError('Código de fuente desordenado')
    index={code:i for i,code in enumerate(codes)}
    pages=[unswizzle(decode_imy_texture(arc[z['offset']:z['offset']+z['size']])) for z in members[1:]]
    slots=atlas_slots(pages)
    if len(slots)!=3072:raise ValueError('Atlas fuente incompleto')
    result=[];total_ink=0
    for i,(ch,base) in enumerate(zip(CHARACTERS,BASE_GLYPHS)):
        old=slots[index[ord(base)]]
        src=[list(old[k*16:(k+1)*16]) for k in range(16)]
        new=make_glyph(src,ch)
        changed=sum(v==15 for row in new for v in row)
        total_ink+=changed
        oldg,newg=geometry(src),geometry(new)
        code=ES_BYTES[ch][0]
        if code!=0xA1+i:raise ValueError('Codec A1-B3 no coincide')
        result.append({'char':ch,'cp932_hex':f'{code:02X}','slot':95+i,
                       'base':base,'base_index':index[ord(base)],
                       'advance_raw_hex':recs[index[ord(base)]][2:].hex(),
                       'base_geom':oldg,'spanish_geom':newg,
                       'pixels_tinta_15':changed,
                       'raster_sha256':hashlib.sha256(bytes(v for row in new for v in row)).hexdigest()})
    if len(result)!=19 or total_ink!=100:
        raise ValueError(f'Cuenta de 19/100 inesperada: {len(result)}/{total_ink}')
    return {'schema':'cladun.f2.raster_geometry_19.v1',
            'nivel':'ESTATICO_ORIGINAL_NO_PPSSPP',
            'originales':count,'nuevos':len(result),
            'suma_texels_tinta_15':total_ink,
            'atencion_acentos':['í: el trazo nuevo extiende bbox de x3 hasta x4',
                                  'Mayúsculas acentuadas/Ñ/Ü: algunos originales se desplazan hasta y15'],
            'avance_no_interpretado':'Los dos bytes de métricas se conservan del glifo base',
            'white_new_ink_activado_por_defecto':False,
            'ppsspp_multicontexto_verificado':False,
            'glifos':result}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso-usa',type=Path,required=True)
    p.add_argument('--reporte',type=Path,required=True)
    x=p.parse_args()
    if x.reporte.exists() or x.reporte.resolve()==x.iso_usa.resolve():
        raise ValueError('Usar informe nuevo y no sobrescribir ISO')
    out=audit(x.iso_usa)
    x.reporte.parent.mkdir(parents=True,exist_ok=True)
    with x.reporte.open('x',encoding='utf-8') as f:json.dump(out,f,indent=2,ensure_ascii=False);f.write('\n')
    print(json.dumps({k:v for k,v in out.items() if k!='glifos'},ensure_ascii=False,indent=2))
if __name__=='__main__':main()
