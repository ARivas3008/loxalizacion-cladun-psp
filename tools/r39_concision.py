#!/usr/bin/env python3
"""R39 reviewed concise alternatives; fixed-width and authentic preimage anchors.

These are insertion-only editorial proposals, not modifications to the literary
draft, and remain experimental until contextual PPSSPP QA.
"""
from pathlib import Path
import hashlib
from tools.r29_integrar_longitud_fija import DRAFT,require
from tools.f4_r21_ligature_capacity import read_canonical, matching, encode_fixed, decode_encoded
from tools.r35_ligaduras_acumuladas import PAIRS
from tools.r31_bulk_padding import fnv,serialized
from tools.charset_es import encode_spanish,ES_GLYPHS

OVERLAY=Path(__file__).resolve().parents[1]/"traduccion/propuestas/R39_CONCISION.tsv"
OVERLAY_SHA="5fac6e55e1f0fb4631deb79934dfaa9a1d5b73c5cfa436f8331cf4341c2c0aa7"
COUNT=176

def audit(full,overlay=OVERLAY):
    done={x["gid"] for x in full}
    require(len(full)==len(done)==4172,"R38 profile drift")
    raw=Path(overlay).read_bytes()
    require(hashlib.sha256(raw).hexdigest()==OVERLAY_SHA,"R39 editorial overlay hash differs")
    rows={r["grupo_id"]:r for r in read_canonical(DRAFT)}
    plan=[]
    for line in raw.decode("utf-8").splitlines():
        gid,offset,text=line.split("\t",2)
        r=rows[gid];old=bytes.fromhex(r["bytes_hex"]);at=int(offset,16)
        require(gid not in done and r["origen"]=="SCRIPT.SDT/SCRIPT.DAT"
                and at==int(r["offset_hex"],16)
                and len(old)==int(r["longitud_original_bytes"])
                and all(32<=b<=126 and b not in (37,92) for b in old),
                "R39 slot mismatch")
        canonical=r["espanol"]
        require(canonical and canonical!=text and all(32<=ord(c)<=126 or c in ES_GLYPHS for c in canonical+text)
                and "%" not in canonical+text and "\\" not in canonical+text
                and text==text.strip()
                and len(encode_spanish(canonical))-len(matching(canonical,PAIRS))>len(old),
                "R39 proposal must be a previously deferred ASCII/ES overflow")
        ordinary=encode_spanish(text)
        if len(ordinary)>len(old):
            new=encode_fixed(text,len(old),PAIRS);padding=0
        else:
            padding=len(old)-len(ordinary)
            require(padding<=7,"R39 excessive whitespace")
            new=ordinary+b" "*padding
        require(len(new)==len(old) and 0 not in new and new!=old
                and decode_encoded(new,PAIRS)==text+" "*padding,"R39 codec mismatch")
        plan.append({"gid":gid,"group_id":gid,"offset":at,"old":old,"new":new,
                     "padding":padding})
    plan.sort(key=lambda x:x["offset"])
    require(len(plan)==len({x["gid"] for x in plan})==COUNT
            and fnv(serialized(plan,False))==1098652814
            and fnv(serialized(plan))==3013028385
            and hashlib.sha256(serialized(plan,False)).hexdigest()=="f963e505414e29b3935bba106ece154b2f10727112b309f6b3e96207848d9229"
            and hashlib.sha256(serialized(plan)).hexdigest()=="03696a3f7fa8feb51b5dd015ec5f00dc63992b06f9ec3dff847891e951330b56",
            "R39 authenticated plan drift")
    combined=sorted(full+plan,key=lambda x:x["offset"])
    require(len(combined)==len({x["gid"] for x in combined})==4348
            and all(a["offset"]+len(a["old"])<=b["offset"] for a,b in zip(combined,combined[1:])),
            "R39 combined overlap")
    return plan,{"new":COUNT,"prior":7520,"total_if_built":7696,"remaining":552,
                 "canonical_modified":False,"runtime_verified":False,"release_authorized":False}
