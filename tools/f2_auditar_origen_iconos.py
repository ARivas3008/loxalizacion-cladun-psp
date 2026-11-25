#!/usr/bin/env python3
"""F2 auditor independiente de solo lectura, origen de iconos en ISO USA.

No exporta texturas, EBOOT, RAM ni bytes del juego. No demuestra GE/VRAM.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import struct
from pathlib import Path

SECTOR=2048
ISO_SHA256="b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f"
IMY_SHA256="0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190"

def sha256(blob:bytes)->str:
    return hashlib.sha256(blob).hexdigest()

def u32(blob:bytes,i:int)->int:
    if i<0 or i+4>len(blob):
        raise ValueError("Lectura fuera de límites")
    return struct.unpack_from("<I",blob,i)[0]

def name(raw:bytes)->str:
    return raw.split(b"\0",1)[0].decode("ascii",errors="strict")

def iso_entry(record:bytes)->dict:
    if len(record)<34 or record[0]<34 or record[0]>len(record):
        raise ValueError("Entrada ISO9660 truncada")
    n=record[32]
    if 33+n>record[0]:
        raise ValueError("Nombre ISO9660 fuera de registro")
    return {"name":record[33:33+n].decode("ascii").split(";")[0],
            "offset":u32(record,2)*SECTOR,"size":u32(record,10),
            "directory":bool(record[25]&2)}

def locate_data(iso:Path)->dict:
    with iso.open("rb") as f:
        f.seek(16*SECTOR)
        pvd=f.read(SECTOR)
        if pvd[:7]!=b"\x01CD001\x01":
            raise ValueError("No ISO9660 PVD")
        root=iso_entry(pvd[156:156+pvd[156]])
        visited=set()
        def walk(d,prefix):
            if d["offset"] in visited:
                raise ValueError("Directorio cíclico")
            visited.add(d["offset"])
            f.seek(d["offset"]);raw=f.read(d["size"])
            if len(raw)!=d["size"]:
                raise ValueError("Directorio truncado")
            pos=0
            while pos<len(raw):
                k=raw[pos]
                if not k:
                    pos=(pos//SECTOR+1)*SECTOR
                    continue
                obj=iso_entry(raw[pos:pos+k]);pos+=k
                if obj["name"] in ("\0","\1"):
                    continue
                path=prefix+"/"+obj["name"] if prefix else obj["name"]
                if path=="PSP_GAME/USRDIR/DATA.DAT":
                    if obj["directory"]:
                        raise ValueError("DATA.DAT no es archivo")
                    return obj
                if obj["directory"]:
                    found=walk(obj,path)
                    if found:
                        return found
            return None
        found=walk(root,"")
        if found is None:
            raise ValueError("DATA.DAT no localizado")
        if found["offset"]+found["size"]>iso.stat().st_size:
            raise ValueError("DATA.DAT excede ISO")
        return found

def pspfs_entries(blob:bytes)->list[dict]:
    if blob[:8]!=b"PSPFS_V1":
        raise ValueError("PSPFS_V1 ausente")
    count=u32(blob,8)
    if not 0<count<=4096 or 16+32*count>len(blob):
        raise ValueError("Tabla PSPFS fuera de límites")
    output=[]
    for i in range(count):
        q=16+32*i
        expanded,stored,offset=struct.unpack_from("<III",blob,q+20)
        if offset+stored>len(blob):
            raise ValueError("PSPFS fuera de DATA.DAT")
        output.append({"index":i,"name":name(blob[q:q+20]),
                       "offset":offset,"size_stored":stored,"size_expanded":expanded})
    return output

def dsarc_entries(blob:bytes)->list[dict]:
    if blob[:8] not in (b"DSARC FL",b"DSARCIDX"):
        raise ValueError("DSARC desconocido")
    n=u32(blob,8)
    if not 0<n<=4096:
        raise ValueError("DSARC cantidad incorrecta")
    start=16 if blob[:8]==b"DSARC FL" else ((16+n*2+3)//4)*4
    if start+48*n>len(blob):
        raise ValueError("DSARC tabla fuera de archivo")
    out=[]
    for i in range(n):
        q=start+i*48
        size,off=struct.unpack_from("<II",blob,q+40)
        if off+size>len(blob):
            raise ValueError("DSARC miembro fuera de límites")
        out.append({"index":i,"name":name(blob[q:q+40]),"offset":off,"size":size})
    return out

def audit(iso:Path)->dict:
    h=hashlib.sha256()
    with iso.open("rb") as f:
        for part in iter(lambda:f.read(1<<20),b""):
            h.update(part)
    if h.hexdigest()!=ISO_SHA256:
        raise ValueError("SHA256 de ISO original incompatible: "+h.hexdigest())
    rec=locate_data(iso)
    with iso.open("rb") as f:
        f.seek(rec["offset"]);dat=f.read(rec["size"])
    if len(dat)!=rec["size"]:
        raise ValueError("DATA.DAT truncado")
    entries=pspfs_entries(dat)
    if len(entries)!=349:
        raise ValueError("PSPFS no tiene 349 registros")
    sy=entries[225]
    if (sy["name"],sy["offset"])!=("SYSGRA.ARC",895488):
        raise ValueError("SYSGRA no coincide")
    arc=dat[sy["offset"]:sy["offset"]+sy["size_stored"]]
    members=dsarc_entries(arc)
    if len(members)!=27:
        raise ValueError("DSARC no tiene 27 miembros")
    icon=members[17]
    if (icon["name"],icon["offset"],icon["size"])!=("KITAJIMA_KARI.IMY",57856,2480):
        raise ValueError("Miembro iconos no coincide")
    imy=arc[icon["offset"]:icon["offset"]+icon["size"]]
    if sha256(imy)!=IMY_SHA256:
        raise ValueError("SHA del IMY no coincide")
    if imy[:4]!=b"IMY\0" or u32(imy,4)!=0x2060:
        raise ValueError("Cabecera IMY desconocida")
    probe=bytearray(imy)
    for i in range(5,16):
        probe[32+i*4:35+i*4]=b"\xff\x00\xff"
    changes=[i for i,(a,b) in enumerate(zip(imy,probe)) if a!=b]
    if len(changes)!=27 or any(i<32 or i>=96 or i%4==3 for i in changes):
        raise ValueError("Sonda RGB afecta a bytes inesperados")
    if probe[:32]!=imy[:32] or probe[96:]!=imy[96:]:
        raise ValueError("Sonda altera encabezado/raster")
    return {"schema":"cladun.f2.iso_usa_icon_origin_readonly.v1",
            "scope":"STATIC_BINARY_ONLY_NOT_GE_OR_VRAM",
            "iso_sha256":h.hexdigest(),"iso_size":iso.stat().st_size,
            "data_iso_offset":rec["offset"],"data_size":rec["size"],
            "pspfs_count":len(entries),"sysgra_index":sy["index"],
            "sysgra_offset_in_data":sy["offset"],
            "dsarc_count":len(members),"icon_member_index":icon["index"],
            "icon_member_offset_in_arc":icon["offset"],"icon_member_size":icon["size"],
            "icon_member_sha256":sha256(imy),
            "icon_absolute_iso_offset":rec["offset"]+sy["offset"]+icon["offset"],
            "in_memory_rgb_change_only":27,"alpha_and_raster_unchanged":True,
            "ge_vram_mips_drawing_proven":False}

def main()->None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--iso-usa",required=True,type=Path)
    ap.add_argument("--reporte",type=Path)
    opts=ap.parse_args()
    result=audit(opts.iso_usa)
    payload=json.dumps(result,indent=2,ensure_ascii=False)+"\n"
    if opts.reporte:
        with opts.reporte.open("x",encoding="utf-8") as f:
            f.write(payload)
    print(payload)

if __name__=="__main__":
    main()
