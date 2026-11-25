#!/usr/bin/env python3
"""R40: 492 authenticated fixed-width overlays, preserving tokens and all prior IDs.

The physical A audit used the genuine USA ISO. This module independently
recreates the exact accepted plan from the pinned canonical corpus and TSV.
It never certifies gameplay, font rendering or distribution.
"""
from pathlib import Path
from collections import Counter
import hashlib
import re
from tools.r29_integrar_longitud_fija import DRAFT, require
from tools.f4_r21_ligature_capacity import read_canonical, matching, encode_fixed, decode_encoded
from tools.r35_ligaduras_acumuladas import PAIRS
from tools.r31_bulk_padding import fnv, serialized
from tools.charset_es import encode_spanish, ES_GLYPHS
from tools.r37_simbolos_preservados import multibyte_tokens, ICONS

OVERLAY=Path(__file__).resolve().parents[1]/"traduccion/propuestas/R40_CANDIDATOS.tsv"
OVERLAY_BLOB="a22fa6e2c7f72a41125340d33b8b26d062deb356"
COUNT=492
FORMAT=re.compile(rb"(?:-?[0-9]+|[A-Z])%|[@#$%^&]+")

def audit(full,overlay=OVERLAY):
    done={x["gid"] for x in full}
    require(len(full)==len(done)==4348,"R39 profile drift")
    raw=Path(overlay).read_bytes()
    require(hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()==OVERLAY_BLOB,
            "R40 overlay blob changed")
    rows={r["grupo_id"]:r for r in read_canonical(DRAFT)}
    plan=[]; kinds=Counter()
    for line in raw.decode("utf-8").splitlines():
        gid,offset,kind,text=line.split("\t",3)
        r=rows[gid];old=bytes.fromhex(r["bytes_hex"]);at=int(offset,16)
        canonical=r["espanol"]
        require(gid not in done and r["origen"]=="SCRIPT.SDT/SCRIPT.DAT"
                and at==int(r["offset_hex"],16)
                and len(old)==int(r["longitud_original_bytes"])
                and text and text==text.strip() and text!=canonical
                and "\\" not in r["original"]+text+canonical,
                "R40 slot / proposal mismatch")
        require(all(32<=ord(c)<=126 or c in ES_GLYPHS or c in ICONS for c in text),
                "R40 unknown symbol")
        ordinary=encode_spanish(text)
        special=bool(multibyte_tokens(old) or FORMAT.findall(old))
        require(special==(kind=="special"),"R40 special category mismatch")
        if special:
            require(len(encode_spanish(canonical))!=len(old)
                    and all(t.decode("cp932") in ICONS for t in multibyte_tokens(old)),
                    "R40 controls must be verified original icons/format tokens")
        else:
            require(kind in ("ascii","mask")
                    and all(32<=c<=126 and c not in (37,92) for c in old)
                    and len(encode_spanish(canonical))-len(matching(canonical,PAIRS))>len(old),
                    "R40 not a deferred ordinary overflow")
        if kind=="mask":
            require(r["tipo"]=="personaje_interlocutor" and r["original"]=="Mask"
                    and canonical=="Máscara" and text=="Careta",
                    "R40 speaker label mismatch")
        if len(ordinary)>len(old):
            new=encode_fixed(text,len(old),PAIRS);pad=0
        else:
            pad=len(old)-len(ordinary)
            require(pad<=7,"R40 padding exceeds policy")
            new=ordinary+b" "*pad
        require(len(new)==len(old) and new!=old and 0 not in new
                and decode_encoded(new,PAIRS)==text+" "*pad
                and multibyte_tokens(new)==multibyte_tokens(old)
                and FORMAT.findall(new)==FORMAT.findall(old),
                "R40 width / codec / tokens changed")
        kinds[kind]+=1
        plan.append({"gid":gid,"group_id":gid,"offset":at,"old":old,"new":new,
                     "kind":kind,"padding":pad})
    plan.sort(key=lambda x:x["offset"])
    require(len(plan)==len({x["gid"] for x in plan})==COUNT
            and kinds=={"ascii":417,"special":29,"mask":46}
            and sum(len(multibyte_tokens(x["old"])) for x in plan)==19
            and sum(len(FORMAT.findall(x["old"])) for x in plan)==10
            and fnv(serialized(plan,False))==266516364
            and fnv(serialized(plan))==2890877613
            and hashlib.sha256(serialized(plan,False)).hexdigest()=="7263945a7f90ebc3a149e1ba25e3b5468adf226fea7d62f9f042c2fcce46a95a"
            and hashlib.sha256(serialized(plan)).hexdigest()=="e1b9dc90dd6839139cf2c4b910d872f79ce3c00afc284e6f185f4931cdab26f1",
            "R40 physical plan fingerprint mismatch")
    for i,(pre,post) in enumerate(((1032504791,805522759),(1888082895,2816133643),
                                 (2017697080,2751146973))):
        batch=plan[i*164:(i+1)*164]
        require(len(batch)==164 and fnv(serialized(batch,False))==pre
                and fnv(serialized(batch))==post,"R40 batch mismatch")
    merged=sorted(full+plan,key=lambda x:x["offset"])
    require(len(merged)==len({x["gid"] for x in merged})==4840
            and all(a["offset"]+len(a["old"])<=b["offset"] for a,b in zip(merged,merged[1:])),
            "R40 overlapping records")
    return plan,{"new":COUNT,"prior":7696,"total_if_built":8188,"remaining":60,
                 "batches":[164,164,164],"categories":dict(kinds),
                 "special_tokens":19,"format_tokens":10,
                 "canonical_modified":False,"runtime_verified":False,
                 "release_authorized":False}
