"""R52 optimized local relocation, experimental only.
All old text retained for donors; each block's net size change must be zero.
No fixed-offset claim, no runtime claim, no release.
"""
from collections import defaultdict
from pathlib import Path
import struct
from tools.r44_local_experimental import audit as historical_audit, width, IDS
from tools.r29_integrar_longitud_fija import require
from tools.r35_ligaduras_acumuladas import PAIRS
from tools.f4_r21_ligature_capacity import decode_encoded
from tools.script_event_guard import read_commands, audit_script_rebuild
from tools.r45_referencias_locales import scan

DONORS=Path(__file__).resolve().parents[1]/"traduccion/propuestas/R52_DONANTES.tsv"
DONOR_IDS=frozenset("000096 000805 000966 001265 001277 001606 001653 001661 001886 002030 002076 002099 002371 002734 002907 002922 002923 003099 003175 003488 003547 003568 003951 004158 004321 004394 004510 004513 004522 004526 004545 004547 004548 004622 004774".split())

def audit(full,deferred):
    # R44 source authentication and residual encodings remain immutable.
    selected,_,_=historical_audit(full,deferred)
    done={x["gid"]:x for x in full}
    donors={}
    for line in DONORS.read_text(encoding="utf-8").splitlines():
        gid,offset,save,text=line.split("\t",3)
        require(gid in DONOR_IDS and gid not in donors and gid in done,"R52 donor ID")
        p=done[gid];save=int(save)
        require(p["offset"]==int(offset,16) and 1<=save<=4 and len(p["old"])==len(p["new"])
                and decode_encoded(p["new"],PAIRS).rstrip(" ")==text,"R52 donor text drift: "+gid)
        new=width(text,len(p["old"])-save)
        require(new!=p["old"] and decode_encoded(new,PAIRS).rstrip(" ")==text,"R52 donor roundtrip")
        donors[gid]={**p,"new":new}
    require(set(donors)==DONOR_IDS and len(donors)==35 and
            sum(len(x["old"])-len(x["new"]) for x in donors.values())==40,"R52 donor geometry")
    merged=sorted([donors.get(x["gid"],x) for x in full]+selected,key=lambda x:x["offset"])
    require(len(merged)==len({x["gid"] for x in merged})==4899 and
            all(a["offset"]+len(a["old"])<=b["offset"] for a,b in zip(merged,merged[1:])),"R52 overlap")
    return selected,donors,{"new":33,"donors":35,"total_if_built":8247,"resolved_without_new_bytes":1,
                            "resolved_original_target":8248,"remaining":0,"fixed_offsets":False,
                            "profile":"R52_OPTIMIZED_LOCAL","runtime_verified":False,"release_authorized":False}

def rebuild(data,table,expected):
    commands,starts=read_commands(data,table)
    groups=defaultdict(list)
    for c in commands:groups[c.block].append(c)
    out=bytearray();used=set()
    for block,(start,end) in enumerate(zip(starts,starts[1:])):
        require(len(out)==start,"R52 block start drift")
        for c in groups[block]:
            slot=c.offset+7
            if slot not in expected:
                out.extend(c.raw);continue
            old,new,gid=expected[slot]
            require(c.content==old and old!=new and 0 not in new and len(new)+3<=65535,"R52 source slot: "+gid)
            out.extend(c.raw[:3]+struct.pack("<HH",len(new)+3,len(new))+new+b"\0");used.add(slot)
        last=groups[block][-1] if groups[block] else None
        original_end=last.offset+len(last.raw) if last else start
        require(len(out)==original_end,"R52 block net length or padding drift: "+str(block))
        out.extend(b"\0"*(end-len(out)))
    require(used==set(expected) and len(out)==len(data),"R52 incomplete replay")
    result=bytes(out)
    event=audit_script_rebuild(data,table,result,table,expected,require_fixed_offsets=False)
    require(event["total_commands"]==51705 and event["nontext_commands_byte_exact"]==46308
            and event["moved_script_starts"]==0 and event["moved_command_offsets"]==146
            and event["moved_nontext_command_offsets"]==104 and event["script_blocks_with_moved_commands"]==24
            and not event["all_command_offsets_preserved"],"R52 authenticated geometry drift")
    deltas={slot:len(new)-len(old) for slot,(old,new,_) in expected.items() if len(old)!=len(new)}
    require(len(deltas)==68 and sum(deltas.values())==0,"R52 relocation count")
    references=scan(commands,starts,deltas)
    require(not any(references["counts"].values()),"R52 numeric reference candidate found")
    event["numeric_reference_candidates"]=references["counts"]
    event["all_block_padding_preserved"]=True
    event["release_authorized"]=False
    return result,table,event
