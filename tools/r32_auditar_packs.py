#!/usr/bin/env python3
"""R32: exhaustive bulk pack audit, private source only; never writes ISO.
Run at repo root: python -m tools.r32_auditar_packs /private/USA.iso
"""
import argparse
import hashlib
import json
import struct
from pathlib import Path

from tools.r31_bulk_padding import pool, serialized, fnv, GAPS
from tools.r29_integrar_longitud_fija import require
from tools.f3_referencias_riesgo import file_sha256, USA_SHA
from tools.f4_r24_piloto_1650_ligaduras import replace_original_script, replace_member_payload
from tools.integrar_parche_seguro import read_resources, parent_content
from tools.extract_cladun import dsarc_entries, decompress, imy_decode
from tools.imy_repack_safe import compress_block

EXPECTED = {1:(737420481,1627750828),2:(1449893416,3479435758),
            3:(150812015,3641101921),4:(3513338450,1822911979),
            5:(1381431979,3266062521),6:(931119746,202707510),
            7:(4010312363,1941161653)}
SHA=lambda data:hashlib.sha256(data).hexdigest()

def selective_repack(original, decoded):
    n, capacity=struct.unpack_from("<II",original)
    require(1<=n<=512 and 8+4*n<=len(original),"IMY count")
    offsets=struct.unpack_from("<"+"I"*n,original,8)
    require(offsets[0]>=8+4*n and list(offsets)==sorted(set(offsets))
            and offsets[-1]<len(original),"IMY directory")
    out=bytearray(original[:8]+bytes(n*4))
    cursor=changed=0
    for i,at in enumerate(offsets):
        end=offsets[i+1] if i+1<n else len(original)
        h=original[at:at+32]
        require(len(h)==32 and h[:4]==b"IMY\0","IMY header")
        z=struct.unpack_from("<H",h,8)[0]*struct.unpack_from("<H",h,12)[0]
        piece=decoded[cursor:cursor+z]
        require(len(piece)==z,"IMY geometry")
        old=imy_decode(original,at)
        if piece==old:
            chunk=original[at:end]
        else:
            chunk=compress_block(piece,h)
            changed+=1
        out.extend(bytes(-len(out)%4))
        struct.pack_into("<I",out,8+i*4,len(out))
        out.extend(chunk)
        cursor+=z
    require(cursor==len(decoded),"expanded size drift")
    require(decompress(bytes(out),len(decoded))[0]==decoded,"IMY roundtrip")
    return bytes(out),changed

def audit(iso, selected="all"):
    require(file_sha256(iso)==USA_SHA,"Authentic USA required")
    _,pack,records=read_resources(iso)
    require(len(records)==349,"PSPFS count")
    entry=next(x for x in records if x["name"]=="SCRIPT.SDT")
    stored,archive,codec=parent_content(pack,entry)
    require(codec.startswith("IMY"),"SCRIPT codec")
    members=dsarc_entries(archive)
    def member(blob,name):
        x=next(r for r in members if r["name"]==name)
        return blob[x["offset"]:x["offset"]+x["size"]]
    src=member(archive,"SCRIPT.DAT")
    tbl=member(archive,"SCRIPT.TBL")
    _,rows=pool()
    families={g:[x for x in rows if x["padding"]==g] for g in GAPS}
    require(len({x["offset"] for x in rows})==1302,"Duplicate offsets")
    for g,p in families.items():
        require(len(p)==GAPS[g] and (fnv(serialized(p,False)),fnv(serialized(p)))==EXPECTED[g],
                "Canonical pack digest drift")
    plans={str(g):p for g,p in families.items()}
    plans["short"]=[x for x in rows if x["padding"]<=2]
    plans["long"]=[x for x in rows if x["padding"]>=3]
    plans["all"]=rows
    output={}
    for label,plan in plans.items():
        if selected!="all" and label!=selected:continue
        changed,guard=replace_original_script(src,tbl,plan)
        dest=replace_member_payload(archive,members,"SCRIPT.DAT",changed)
        require(dsarc_entries(dest)==members,"DSARC directory drift")
        require(all(member(dest,x["name"])==member(archive,x["name"])
                    for x in members if x["name"]!="SCRIPT.DAT"),"Sibling altered")
        packed,n=selective_repack(stored,dest)
        output[label]={"records":len(plan),"preimage_sha256":SHA(serialized(plan,False)),
                       "plan_sha256":SHA(serialized(plan)),
                       "script_sha256":SHA(changed),"compressed_sha256":SHA(packed),
                       "repacked_blocks":n,"stored_size":len(packed),"event_guard":guard}
    require(file_sha256(iso)==USA_SHA,"Original modified")
    return {"packs":output,"scope":"authentic source DSARC, no cumulative F1 ISO",
            "iso_candidate_written":False,"ppsspp_run":False,"official_new":0,
            "release_authorized":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("iso",type=Path)
    p.add_argument("--pack",choices=[str(x) for x in range(1,8)]+["short","long","all"],default="all")
    a=p.parse_args()
    print(json.dumps(audit(a.iso,a.pack),indent=2))

if __name__=="__main__":
    main()
