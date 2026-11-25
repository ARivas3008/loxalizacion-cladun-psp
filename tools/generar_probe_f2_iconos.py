#!/usr/bin/env python3
"""F2 SONDA PRIVADA: cambiar solo CLUT de SYSGRA.ARC/KITAJIMA_KARI.IMY.

No es un parche público ni una corrección visual: requiere ISO F1 privada exacta.
El cambio se usa como control causal con capturas PPSSPP auténticas.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from extract_cladun import iso9660_entries, pspfs_entries, dsarc_entries, read_iso_file
from font_es_patch import sha256_file

F1_SHA = '496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986'
IMY_SHA = '0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190'
IMY_NAME = 'KITAJIMA_KARI.IMY'
PSPFS_NAME = 'SYSGRA.ARC'
MAGENTA = b'\xff\x00\xff'

def recolor_palette_only(imy: bytes) -> tuple[bytes, list[int]]:
    if len(imy) != 2480 or imy[:4] != b'IMY\0' or int.from_bytes(imy[4:8], 'little') != 0x2060:
        raise ValueError('F2: cabecera/longitud IMY desconocida')
    if not all(imy[32 + 4*i + 3] > 0 for i in range(5, 16)):
        raise ValueError('F2: paleta de botones sin alpha esperado')
    result = bytearray(imy)
    for i in range(5, 16):
        result[32 + i*4:35 + i*4] = MAGENTA
    changed = [i for i, (a, b) in enumerate(zip(imy, result)) if a != b]
    if not (25 <= len(changed) <= 33 and all(32 <= i < 96 and i % 4 != 3 for i in changed)):
        raise ValueError('F2: cambio fuera del RGB de la paleta')
    return bytes(result), changed

def build(source: Path, target: Path, report: Path) -> dict:
    source, target, report = map(Path, (source, target, report))
    if len({source.resolve(),target.resolve(),report.resolve()}) != 3 or target.exists() or report.exists():
        raise ValueError('F2: las salidas deben ser nuevas y no sobrescribir fuentes')
    if sha256_file(source) != F1_SHA:
        raise ValueError('F2: requiere ISO canónica F1 SHA exacto')
    _, iso_files = iso9660_entries(source)
    data = next(x for x in iso_files if x['path'] == 'PSP_GAME/USRDIR/DATA.DAT')
    pack = read_iso_file(source,data)
    resources = pspfs_entries(pack)
    if len(resources) != 349: raise ValueError('F2: 349 PSPFS esperados')
    group = next(x for x in resources if x['name'] == PSPFS_NAME)
    archive = pack[group['offset']:group['offset'] + group['size_stored']]
    members = dsarc_entries(archive)
    if len(members) != 27: raise ValueError('F2: DSARC diferente')
    member = next(x for x in members if x['name'] == IMY_NAME)
    old = archive[member['offset']:member['offset'] + member['size']]
    if hashlib.sha256(old).hexdigest() != IMY_SHA:
        raise ValueError('F2: SHA del miembro desconocido')
    updated, changed = recolor_palette_only(old)
    abs_off = data['offset'] + group['offset'] + member['offset']
    target.parent.mkdir(parents=True,exist_ok=True)
    report.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(source,target)
    with target.open('r+b') as f:
        f.seek(abs_off); f.write(updated)
    _,new_iso=iso9660_entries(target)
    if new_iso != iso_files: raise ValueError('F2: ISO9660 modificado')
    new_pack=read_iso_file(target,data)
    if pspfs_entries(new_pack)!=resources: raise ValueError('F2: indice PSPFS modificado')
    for obj in resources:
        if obj['name'] != PSPFS_NAME:
            i,n=obj['offset'],obj['size_stored']
            if pack[i:i+n] != new_pack[i:i+n]: raise ValueError('F2: recurso ajeno modificado')
    new_arc = new_pack[group['offset']:group['offset']+group['size_stored']]
    if dsarc_entries(new_arc)!=members:raise ValueError('F2: indice DSARC modificado')
    for other in members:
        if other['name'] != IMY_NAME:
            a,z=other['offset'],other['size']
            if archive[a:a+z] != new_arc[a:a+z]:raise ValueError('F2: miembro vecino modificado')
    changed_all = [i for i,(a,b) in enumerate(zip(archive,new_arc)) if a!=b]
    if changed_all != [member['offset']+i for i in changed]:
        raise ValueError('F2: delta distinto de paleta')
    result = {'schema':'cladun.f2.private_kitajima_palette_probe.v1',
        'estado':'SONDA_PRIVADA_REQUIERE_PPSSPP_PARA_DEMOSTRAR_USO',
        'origen_f1_sha256':F1_SHA,'candidato_iso_sha256':sha256_file(target),
        'recurso':'SYSGRA.ARC/KITAJIMA_KARI.IMY','miembro_original_sha256':IMY_SHA,
        'pspfs_total':349,'pspfs_ajenos_identicos':348,'dsarc_total':27,
        'miembros_ajenos_identicos':26,'bytes_rgb_modificados':len(changed),
        'datos_imy_fuera_paleta_identicos':True,'eventos_y_fuentes_identicos':True,
        'capturas_ppsspp':'NO_GENERADAS_POR_ESTA_HERRAMIENTA'}
    with report.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
    return result

if __name__ == '__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso-f1',required=True,type=Path)
    p.add_argument('--salida-iso',required=True,type=Path)
    p.add_argument('--reporte',required=True,type=Path)
    a=p.parse_args()
    print(json.dumps(build(a.iso_f1,a.salida_iso,a.reporte),ensure_ascii=False,indent=2))
