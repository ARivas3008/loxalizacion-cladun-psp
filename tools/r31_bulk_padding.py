#!/usr/bin/env python3
"""R31: bulk experimental fixed-width padding on canonical shorter SCRIPT text.

Never promote trailing spaces to official integration without PPSSPP. The
existing 19-character Spanish font is sufficient; no ligatures or relocation.
Only printable ASCII and the existing Spanish single-byte glyphs are accepted.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
try:
    from tools.charset_es import ES_GLYPHS, decode_spanish
    from tools.f4_r21_ligature_capacity import read_canonical
    from tools.f4_r25_piloto_85pct import pad_shorter
    from tools.r29_integrar_longitud_fija import DRAFT, require, run as build
    from tools.r30_integrar_repeticiones import make_plan as r30_plan, run_isolated
except ModuleNotFoundError:
    from charset_es import ES_GLYPHS, decode_spanish
    from f4_r21_ligature_capacity import read_canonical
    from f4_r25_piloto_85pct import pad_shorter
    from r29_integrar_longitud_fija import DRAFT, require, run as build
    from r30_integrar_repeticiones import make_plan as r30_plan, run_isolated

GAPS={1:330,2:278,3:187,4:166,5:137,6:114,7:90}
POOL=1302
FNV_PREIMAGE=1592949294
FNV_FULL=1412021638
FNV_608=480022839
SHA_608="f41ae5b79ae9de53cd988551ddb734529a63c33f77f165dc7379345d6d30c4eb"
PACKS={"one":(1,), "two":(2,), "short":(1,2), "long":(3,4,5,6,7), "all":tuple(range(1,8))}

def serialized(plan, include_new=True):
    return b"".join(struct.pack("<IH",x["offset"],len(x["old"]))+x["old"]+
                    (x["new"] if include_new else b"") for x in plan)

def fnv(data):
    h=2166136261
    for byte in data:
        h=((h^byte)*16777619)&0xffffffff
    return h

def pool(draft=DRAFT):
    rows=read_canonical(draft)
    previous=r30_plan(draft)
    excluded={x["gid"] for x in previous}
    selected=[]
    for r in rows:
        if r["grupo_id"] in excluded or r["origen"]!="SCRIPT.SDT/SCRIPT.DAT":
            continue
        text=r["espanol"]
        if not text or not all(32<=ord(c)<=126 or c in ES_GLYPHS for c in text):
            continue
        proposal=pad_shorter(r,max_pad=7)
        if proposal is None:
            continue
        require(len(proposal["old"])==int(r["longitud_original_bytes"]),"Source width drift")
        require(decode_spanish(proposal["new"])==text+" "*proposal["padding"],
                "Canonical text or padding changed")
        selected.append({**proposal,"gid":r["grupo_id"],"block":int(r["indice_registro"]),
                         "order":int(r["orden_script"]),"script_id":int(r["script_id"])})
    selected.sort(key=lambda x:x["offset"])
    require(len(selected)==POOL and Counter(x["padding"] for x in selected)==GAPS,
            "Bulk pool count or gaps changed")
    require(len({x["gid"] for x in selected})==POOL and len({x["offset"] for x in selected})==POOL,
            "Duplicate slot")
    require(fnv(serialized(selected,False))==FNV_PREIMAGE and fnv(serialized(selected))==FNV_FULL,
            "Bulk pool bytes differ from independently recorded corpus audit")
    short=[x for x in selected if x["padding"]<=2]
    require(fnv(serialized(short))==FNV_608 and hashlib.sha256(serialized(short)).hexdigest()==SHA_608,
            "608-slot source/candidate digest changed")
    return previous,selected

def make_plan(draft=DRAFT, pack="short"):
    require(pack in PACKS,"Unknown experimental pack")
    prior,all_new=pool(draft)
    new=[x for x in all_new if x["padding"] in PACKS[pack]]
    result=sorted(prior+new,key=lambda x:x["offset"])
    require(len(result)==146+sum(GAPS[g] for g in PACKS[pack]),"Pack size changed")
    require(len({x["gid"] for x in result})==len(result),"Repeated ID")
    require(all(a["offset"]+len(a["old"])<=b["offset"] for a,b in zip(result,result[1:])),
            "Overlapping script spans")
    return result

def audit(pack="short"):
    selected=make_plan(pack=pack)
    return {"pack":pack,"new_padding_slots":len(selected)-146,"prior_exact_width":146,
            "total_isolated_if_built":len(selected),"cumulative_if_built":3724+len(selected),
            "pool":POOL,"gap_counts":GAPS,"trailing_spaces_runtime_unverified":True,
            "official_integrated":3724,"official_new":0,"ppsspp_run":False,
            "release_authorized":False,"candidate_written":False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pack",choices=tuple(PACKS),default="short")
    p.add_argument("--iso-original",type=Path)
    p.add_argument("--candidate",type=Path)
    p.add_argument("--isolated-original",action="store_true")
    p.add_argument("--allow-experimental-padding",action="store_true",
                   help="Required for private ISO; spaces not proven in PPSSPP")
    a=p.parse_args()
    if a.iso_original is None and a.candidate is None:
        print(json.dumps(audit(a.pack),indent=2))
        return
    if not (a.iso_original and a.candidate and a.allow_experimental_padding):
        p.error("Private ISO, candidate and explicit experimental padding flag required")
    builder=lambda:make_plan(pack=a.pack)
    run=run_isolated if a.isolated_original else build
    result=run(a.iso_original,a.candidate,plan_builder=builder)
    result.update({"padding_runtime_unverified":True,"pack":a.pack,
                   "official_new_integrations":0,"release_authorized":False})
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
