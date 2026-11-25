"""R53 metadata-only bidirectional relative candidate scan on authenticated R52 geometry."""
from collections import Counter, defaultdict
from pathlib import Path
import argparse
import json

def movement(commands, deltas):
    shift=defaultdict(int)
    moved={}
    used=set()
    for c in commands:
        if shift[c.block]:
            moved[c.offset]={"block":c.block,"order":c.order,"instruction_id":c.instruction_id,
                "opcode":c.code,"old_offset":c.offset,"new_offset":c.offset+shift[c.block],
                "delta":shift[c.block],"textual":c.content is not None}
        if c.offset+7 in deltas:
            if c.content is None: raise ValueError("Nontext slot")
            shift[c.block]+=deltas[c.offset+7]
            used.add(c.offset+7)
    if used!=set(deltas) or any(shift.values()): raise ValueError("Slot or block geometry drift")
    return moved

def relative_scan(commands,moved):
    positions={c.offset:c for c in commands}
    counts=Counter()
    values=Counter()
    hits=[]
    for c in commands:
        if c.content is not None: continue
        payload=c.raw[5:]
        for width in (2,4):
            for j in range(len(payload)-width+1):
                v=int.from_bytes(payload[j:j+width],"little",signed=True)
                field=(c.code,len(payload),j,width)
                counts[field]+=1
                values[(*field,v)]+=1
                if not v: continue
                for label,base in (("start",c.offset),("end",c.offset+len(c.raw))):
                    target=positions.get(base+v)
                    if target is None or target.block!=c.block: continue
                    ds=moved.get(c.offset,{}).get("delta",0)
                    dt=moved.get(target.offset,{}).get("delta",0)
                    if ds==dt: continue
                    hits.append({"block":c.block,"source_order":c.order,"source_offset":c.offset,
                        "source_opcode":c.code,"payload_size":len(payload),"payload_offset":j,
                        "width":width,"base":label,"signed_value":v,"source_delta":ds,
                        "target_order":target.order,"target_offset":target.offset,"target_delta":dt,
                        "difference":dt-ds,"classification":"NUMERIC_MATCH_ONLY"})
    for h in hits:
        field=(h["source_opcode"],h["payload_size"],h["payload_offset"],h["width"])
        h["same_value_global"]=values[(*field,h["signed_value"])]
        h["same_field_global"]=counts[field]
    return hits

def audit(iso):
    from tools.f3_referencias_riesgo import original_script_children
    from tools.script_event_guard import read_commands
    from tools.r44_local_experimental import RESIDUAL
    from tools.r52_local_optimized import DONORS
    from tools.r35_ligaduras_acumuladas import PAIRS
    from tools.f4_r21_ligature_capacity import matching
    from tools.charset_es import encode_spanish
    from tools.r45_referencias_locales import scan
    data,table=original_script_children(iso)
    commands,starts=read_commands(data,table)
    slots={c.offset+7:c for c in commands if c.content is not None}
    deltas={}
    for line in RESIDUAL.read_text(encoding="utf-8").splitlines():
        gid,offset,text=line.split("\t",2)
        p=int(offset,16)
        d=len(encode_spanish(text))-len(matching(text,PAIRS))-len(slots[p].content)
        if p in deltas or d<=0: raise ValueError("Residual drift "+gid)
        deltas[p]=d
    if len(deltas)!=33 or sum(deltas.values())!=40: raise ValueError("Residual geometry")
    for line in DONORS.read_text(encoding="utf-8").splitlines():
        gid,offset,saved,_=line.split("\t",3)
        p=int(offset,16)
        if p in deltas or p not in slots or not 1<=int(saved)<=4: raise ValueError("Donor drift "+gid)
        deltas[p]=-int(saved)
    if len(deltas)!=68 or sum(deltas.values()): raise ValueError("Net geometry")
    moved=movement(commands,deltas)
    hits=relative_scan(commands,moved)
    direct=scan(commands,starts,deltas)
    observed=(len(commands),len(moved),sum(not x["textual"] for x in moved.values()),
        len({x["block"] for x in moved.values()}),len(hits),
        sum(bool(h["target_delta"]) for h in hits),sum(not h["target_delta"] for h in hits))
    if observed!=(51705,146,104,24,31,22,9) or any(direct["counts"].values()):
        raise ValueError("Authenticated R52/R53 geometry drift: "+str(observed))
    return {"schema":"cladun.r53.relative_bidir.v1","evidence":"A_SOURCE_STATIC",
        "commands":51705,"moved":list(moved.values()),"relative_candidates":hits,
        "absolute_and_local":direct["counts"],"runtime_verified":False,
        "reference_semantics_proven":False,"release_authorized":False}

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--iso-original",type=Path,required=True)
    print(json.dumps(audit(p.parse_args().iso_original),indent=2))
