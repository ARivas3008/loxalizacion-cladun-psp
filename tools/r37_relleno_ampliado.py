#!/usr/bin/env python3
"""R37: authenticated residual triage and extended-padding overlay."""
from __future__ import annotations
import hashlib
import sys
from pathlib import Path
from collections import Counter
sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.r35_ligaduras_acumuladas import make_plan, PAIRS
from tools.r31_bulk_padding import serialized, fnv
from tools.r29_integrar_longitud_fija import DRAFT, require
from tools.f4_r21_ligature_capacity import read_canonical, matching
from tools.f4_r25_piloto_85pct import pad_shorter
from tools.charset_es import encode_spanish, ES_GLYPHS

GROUPS=((8,12,200,1330499443,202296382),(13,16,42,2266923989,3831548989),
        (17,31,33,268700573,2699294979))
def audit(full=None):
    if full is None:
        _,full,_=make_plan()
    done={x["gid"] for x in full}
    require(len(done)==3745,"R36 source profile drift")
    pending=[];selected=[]
    for r in read_canonical(DRAFT):
        if r["origen"]!="SCRIPT.SDT/SCRIPT.DAT" or r["grupo_id"] in done:
            continue
        old=bytes.fromhex(r["bytes_hex"]);text=r["espanol"]
        delta=len(encode_spanish(text))-len(old)
        if not delta:continue
        controls=(any(c<32 or c>126 or c in (37,92) for c in old)
                  or "%" in text or "\\" in text or not text.isprintable()
                  or any(not (32<=ord(c)<=126 or c in ES_GLYPHS) for c in text))
        kind=("controls_or_multibyte" if controls else
              "long_padding" if delta<0 else "overflow")
        pending.append({"gid":r["grupo_id"],"offset":int(r["offset_hex"],16),
                        "old":old,"delta":delta,"kind":kind})
        if kind=="long_padding":
            p=pad_shorter(r,max_pad=31)
            require(p is not None and 8<=p["padding"]<=31,"Extended padding changed")
            selected.append({**p,"gid":r["grupo_id"]})
        elif kind=="overflow":
            require(len(matching(text,PAIRS))<delta,"Missed ligature candidate")
    pending.sort(key=lambda x:x["offset"]);selected.sort(key=lambda x:x["offset"])
    counts=Counter(x["kind"] for x in pending)
    require(len(pending)==1155 and counts=={"overflow":787,"long_padding":275,"controls_or_multibyte":93}
            and fnv(serialized(pending,False))==2044779673
            and hashlib.sha256(serialized(pending,False)).hexdigest()=="838b7879d90439f6c21f2e876023332d4e12e20a23e23768b77bafaa617dbb08",
            "Residual preimage inventory drift")
    for lo,hi,n,pre,post in GROUPS:
        part=[x for x in selected if lo<=x["padding"]<=hi]
        require(len(part)==n and fnv(serialized(part,False))==pre
                and fnv(serialized(part))==post,"R37 padding group drift")
    require(len(selected)==275 and fnv(serialized(selected))==1455508832
            and hashlib.sha256(serialized(selected)).hexdigest()=="86c7a635521a50aa493086c4c0f3b34e0a3b4790c1fd040d2aa24c54c47c59aa",
            "R37 combined overlay drift")
    combined=sorted(full+selected,key=lambda x:x["offset"])
    require(len({x["gid"] for x in combined})==4020
            and all(a["offset"]+len(a["old"])<=b["offset"] for a,b in zip(combined,combined[1:])),
            "R37 overlapping script plan")
    return selected,{"pending_before":1155,"categories":dict(counts),
                     "admitted_extended_padding":275,"remaining":880,"total_if_built":7368,
                     "runtime_verified":False,"release_authorized":False,
                     "max_padding":31,"batches":[1000,155]}

if __name__=="__main__":
    import json
    print(json.dumps(audit()[1],indent=2))
