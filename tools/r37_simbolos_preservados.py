#!/usr/bin/env python3
"""R37 controlled CP932-symbol overlay: exact token bytes and fixed width."""
from __future__ import annotations
from collections import Counter
import hashlib
from tools.r31_bulk_padding import fnv,serialized
from tools.r29_integrar_longitud_fija import DRAFT,require
from tools.f4_r21_ligature_capacity import read_canonical,encode_fixed,decode_encoded
from tools.r35_ligaduras_acumuladas import PAIRS
from tools.charset_es import encode_spanish

ICONS=frozenset("①②③④⑤⑥⑧⑨⑬⑯⑰⑳㈱㈲㊧㊨㊤㊦↑↓←→♪")
IDS=frozenset("000046 000102 000106 000112 000169 000239 000242 000248 000260 000298 000299 000301 000372 000374 000375 000382 000406 000409 000414 000427 000465 000466 000468 000539 000541 000542 000549 000573 000703 000849 000854 001149 001171 001173 001185 001186 001206 001215 001216 001223 001373 001374 001387 001410 001413 002790 002791 003277 003378 003837 004920 005110 005112".split())

def multibyte_tokens(raw):
    tokens=[];i=0
    while i<len(raw):
        b=raw[i]
        if 0x81<=b<=0x9f or 0xe0<=b<=0xfc:
            require(i+1<len(raw),"Truncated CP932 symbol")
            token=raw[i:i+2]
            token.decode("cp932","strict")
            tokens.append(token);i+=2
        else:i+=1
    return tokens

def propose(row):
    old=bytes.fromhex(row["bytes_hex"]);text=row["espanol"]
    original=old.decode("cp932","strict")
    if "%" in original+text or "\\" in original+text or not text.isprintable():
        return None,"format_control_review"
    tokens=multibyte_tokens(old)
    if not tokens or any(x.decode("cp932") not in ICONS for x in tokens):
        return None,"non_icon_multibyte_review"
    raw=encode_spanish(text)
    if multibyte_tokens(raw)!=tokens:
        return None,"symbol_sequence_mismatch"
    delta=len(raw)-len(old)
    if delta==0:return None,"already_fixed"
    if delta<0:
        new=raw+b" "*(-delta)
        require(decode_encoded(new,PAIRS)==text+" "*(-delta),"Symbol padding roundtrip")
    else:
        try:new=encode_fixed(text,len(old),PAIRS)
        except ValueError:return None,"icon_text_overflow"
        require(decode_encoded(new,PAIRS)==text,"Symbol ligature roundtrip")
    require(len(new)==len(old) and new!=old and 0 not in new
            and multibyte_tokens(new)==tokens,"Special symbol bytes drift")
    return {"gid":row["grupo_id"],"group_id":row["grupo_id"],
            "offset":int(row["offset_hex"],16),"old":old,"new":new,
            "tokens":len(tokens)},"icon_static_fit"

def audit(full):
    done={x["gid"] for x in full}
    require(len(done)==4020,"R37 extended profile drift")
    out=[];all_controls=[];counts=Counter()
    from tools.charset_es import ES_GLYPHS
    for r in read_canonical(DRAFT):
        if r["origen"]!="SCRIPT.SDT/SCRIPT.DAT" or r["grupo_id"] in done:continue
        old=bytes.fromhex(r["bytes_hex"]);t=r["espanol"]
        if len(encode_spanish(t))==len(old):continue
        control=(any(c<32 or c>126 or c in (37,92) for c in old)
                 or "%" in t or "\\" in t or not t.isprintable()
                 or any(not (32<=ord(c)<=126 or c in ES_GLYPHS) for c in t))
        if not control:continue
        all_controls.append({"offset":int(r["offset_hex"],16),"old":old})
        p,kind=propose(r);counts[kind]+=1
        if p is not None:out.append(p)
    out.sort(key=lambda x:x["offset"]);all_controls.sort(key=lambda x:x["offset"])
    require(len(all_controls)==93 and fnv(serialized(all_controls,False))==1021132515
            and counts=={"icon_static_fit":53,"icon_text_overflow":19,
                         "non_icon_multibyte_review":11,"format_control_review":10},
            "R37 residual control classification drift")
    require({x["gid"] for x in out}==IDS and fnv(serialized(out,False))==1899166132
            and fnv(serialized(out))==2586129159
            and hashlib.sha256(serialized(out)).hexdigest()=="10fe45321109a8a94f0083def28860b90a3f2d63acfce5e3cd5ad79afccc960d"
            and sum(x["tokens"] for x in out)==65,"R37 authentic CP932 overlay drift")
    combined=sorted(full+out,key=lambda x:x["offset"])
    require(len({x["gid"] for x in combined})==4073
            and all(a["offset"]+len(a["old"])<=b["offset"] for a,b in zip(combined,combined[1:])),
            "CP932 overlay overlaps existing profile")
    return out,{"checked":93,"categories":dict(counts),"new":53,"preserved_tokens":65,
                "remaining":827,"total_if_built":7421,"runtime_verified":False,
                "release_authorized":False}
