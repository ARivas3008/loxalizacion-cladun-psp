#!/usr/bin/env python3
"""F2 SONDA PRIVADA: tinta blanca para los 19 glifos nuevos CP932 A1-B3.

Requiere dos ISO privadas verificadas: USA original y el diagnóstico 19 glifos
creado por generar_probe_f2_glifos.py + --experimental-parcial --event-safe-only.
Cambia SOLO FONT.ARC, conserva todos los demás PSPFS y las 2721 celdas base.
No modifica corpus canónico ni es una versión de distribución.
"""
from __future__ import annotations
import argparse,hashlib,json,shutil,struct
from pathlib import Path
from extract_cladun import iso9660_entries,pspfs_entries,dsarc_entries,read_iso_file
from font_es_patch import archive,sha256_file,decode_imy_texture
from font_es_narrow import patched_archive_narrow,atlas_slots,unswizzle

DIAGNOSTIC_SHA='58f98b65185f39f172de0b5da97b9ce6fecb009e61b9462632f602485c99e4ca'

def rasters(arc,members):
    return atlas_slots([unswizzle(decode_imy_texture(arc[m['offset']:m['offset']+m['size']])) for m in members[1:]])

def build(original:Path,diagnostic:Path,out:Path,report:Path):
    original,diagnostic,out,report=map(Path,(original,diagnostic,out,report))
    if len({x.resolve() for x in (original,diagnostic,out,report)})!=4 or out.exists() or report.exists():
        raise ValueError('F2: usar entradas diferentes y dos salidas nuevas')
    if sha256_file(diagnostic)!=DIAGNOSTIC_SHA:raise ValueError('F2: diagnóstico no es la ISO de referencia')
    _dat, _pack,_entries,_font,base_arc,base_members=archive(original)
    historical,_=patched_archive_narrow(base_arc,base_members)
    corrected,summary=patched_archive_narrow(base_arc,base_members,white_new_ink=True)
    _,original_filelist=iso9660_entries(diagnostic)
    data=next(x for x in original_filelist if x['path']=='PSP_GAME/USRDIR/DATA.DAT')
    pack=read_iso_file(diagnostic,data);entries=pspfs_entries(pack)
    if len(entries)!=349:raise ValueError('F2: total PSPFS inesperado')
    font=next(x for x in entries if x['name']=='FONT.ARC')
    old_arc=pack[font['offset']:font['offset']+font['size_stored']]
    if old_arc!=historical:raise ValueError('F2: preimagen FONT.ARC no coincide byte a byte')
    oldmembers=dsarc_entries(old_arc);newmembers=dsarc_entries(corrected)
    if [x['name'] for x in oldmembers]!=[x['name'] for x in newmembers]:raise ValueError('F2: miembros FONT cambiaron')
    oldslots,newslots=rasters(old_arc,oldmembers),rasters(corrected,newmembers)
    if oldslots[:95]!=newslots[:95] or oldslots[114:]!=newslots[114:]:
        raise ValueError('F2: cambian celdas ajenas a A1-B3')
    corrections=[]
    for i in range(95,114):
        orig,new=oldslots[i],newslots[i]
        if not all(a==b or (a==15 and b==1) for a,b in zip(orig,new)):
            raise ValueError('F2: delta de paleta distinto 15->1')
        corrections.append(sum(a!=b for a,b in zip(orig,new)))
    if sum(corrections)!=100:raise ValueError('F2: conteo de 100 texels esperado')
    if old_arc[oldmembers[0]['offset']:oldmembers[0]['offset']+oldmembers[0]['size']]!=corrected[newmembers[0]['offset']:newmembers[0]['offset']+newmembers[0]['size']]:
        raise ValueError('F2: FONT.BIN no puede alterarse')
    next_offset=min(x['offset'] for x in entries if x['offset']>font['offset'])
    if len(corrected)>font['size_stored'] and (font['offset']+len(corrected)>next_offset or any(pack[font['offset']+font['size_stored']:font['offset']+len(corrected)])):
        raise ValueError('F2: no hay espacio no invasivo')
    out.parent.mkdir(parents=True,exist_ok=True);report.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(diagnostic,out)
    with out.open('r+b') as f:
        f.seek(data['offset']+font['offset']);f.write(corrected)
        if len(corrected)<font['size_stored']:f.write(bytes(font['size_stored']-len(corrected)))
        f.seek(data['offset']+16+font['index']*32+24);f.write(struct.pack('<I',len(corrected)))
    _,new_iso=iso9660_entries(out)
    if new_iso!=original_filelist:raise ValueError('F2: ISO9660 cambia')
    newpack=read_iso_file(out,data);newresources=pspfs_entries(newpack)
    if len(newresources)!=349:raise ValueError('F2: PSPFS cambia')
    for old,new in zip(entries,newresources):
        if old['name']!='FONT.ARC':
            a,n=old['offset'],old['size_stored']
            if old!=new or pack[a:a+n]!=newpack[new['offset']:new['offset']+new['size_stored']]:
                raise ValueError('F2: otro recurso modificado')
    result={'schema':'cladun.f2.white_ink_opt_in_private_iso.v1',
        'estado':'SONDA_PRIVADA_REQUIERE_COMPARACION_PPSSPP',
        'diagnostico_sha256':DIAGNOSTIC_SHA,'candidata_sha256':sha256_file(out),
        'raster_originales_identicos':2721,'glifos_nuevos':19,
        'tinta_index15_amarillo_to_index1_blanco':100,
        'conteos_por_glifo':corrections,'font_bin_byte_exact':True,
        'pspfs_total':349,'pspfs_ajenos_intactos':348,
        'iso9660_sin_cambios':True,'codigo_canónico_f1_no_modificado':True}
    with report.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso-original',required=True,type=Path)
    p.add_argument('--iso-diagnostico',required=True,type=Path)
    p.add_argument('--salida-iso',required=True,type=Path)
    p.add_argument('--reporte',required=True,type=Path)
    a=p.parse_args()
    print(json.dumps(build(a.iso_original,a.iso_diagnostico,a.salida_iso,a.reporte),ensure_ascii=False,indent=2))
