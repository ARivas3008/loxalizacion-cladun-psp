"""R44: LOCAL RELOCATION EXPERIMENT ONLY. Not fixed-offset and not releasable.
Reuse 18 existing translations at shorter widths, preserve every script start,
every nontext payload and the entire SCRIPT.TBL. The engine's hidden offset
references are NOT proven. No new font codes. Never export a patch from this mode.
"""
from pathlib import Path
import hashlib
import struct
from collections import defaultdict
from tools.r29_integrar_longitud_fija import DRAFT, require
from tools.f4_r21_ligature_capacity import read_canonical, matching, encode_fixed, decode_encoded
from tools.r35_ligaduras_acumuladas import PAIRS
from tools.r31_bulk_padding import serialized
from tools.charset_es import encode_spanish, ES_GLYPHS
from tools.script_event_guard import read_commands, audit_script_rebuild

ROOT=Path(__file__).resolve().parents[1]/"traduccion/propuestas"
RESIDUAL=ROOT/"R44_RESIDUALES.tsv"
DONORS=ROOT/"R44_DONANTES.tsv"
IDS=frozenset("000095 000804 000965 001264 001278 001604 001652 001662 001885 002029 002075 002100 002372 002733 002908 002919 003097 003174 003489 003546 003566 003950 004159 004320 004393 004507 004512 004521 004525 004544 004546 004623 004773".split())
DONOR_IDS=frozenset("000096 000805 000966 001265 001606 001653 001886 002030 002099 003175 003547 003951 004157 004321 004394 004774 002929 004554".split())
PREIMAGE="9ef2f30359bed85564ad00870e081a0581f997771f321f8f58750652c4efc506"

def width(text,n):
    require(text and text==text.strip() and all(32<=ord(c)<=126 or c in ES_GLYPHS for c in text)
            and chr(92) not in text and "%" not in text,"R44 unknown symbol")
    raw=encode_spanish(text)
    if len(raw)>n:
        raw=encode_fixed(text,n,PAIRS)
    else:
        raw+=b" "*(n-len(raw))
    require(len(raw)==n and 0 not in raw and decode_encoded(raw,PAIRS).rstrip(" ")==text,
            "R44 width or roundtrip drift")
    return raw

def audit(full,deferred):
    done={x["gid"]:x for x in full}
    require(len(done)==len(full)==4866 and set(deferred)==IDS and not set(done)&IDS,
            "R43 input profile or residual IDs drift")
    rows={r["grupo_id"]:r for r in read_canonical(DRAFT)}
    new=[]
    for line in RESIDUAL.read_text(encoding="utf-8").splitlines():
        gid,offset,text=line.split("\t",2)
        r=rows[gid];old=bytes.fromhex(r["bytes_hex"]);at=int(offset,16)
        require(gid in IDS and r["origen"]=="SCRIPT.SDT/SCRIPT.DAT"
                and at==int(r["offset_hex"],16) and len(old)==int(r["longitud_original_bytes"])
                and all(32<=b<=126 and b not in (37,92) for b in old),"R44 residual source mismatch")
        n=len(encode_spanish(text))-len(matching(text,PAIRS))
        require(n>len(old),"R44 residual no longer needs relocation")
        raw=width(text,n)
        new.append({"gid":gid,"offset":at,"old":old,"new":raw})
    new.sort(key=lambda x:x["offset"])
    require(len(new)==len({x["gid"] for x in new})==33 and {x["gid"] for x in new}==IDS
            and sum(len(x["new"])-len(x["old"]) for x in new)==40
            and hashlib.sha256(serialized(new,False)).hexdigest()==PREIMAGE,
            "R44 residual preimage or capacity drift")
    donors={}
    for line in DONORS.read_text(encoding="utf-8").splitlines():
        gid,offset,save,text=line.split("\t",3)
        p=done[gid];save=int(save);at=int(offset,16)
        require(gid in DONOR_IDS and gid not in donors and at==p["offset"]
                and 1<=save<=2 and len(p["new"])==len(p["old"])
                and decode_encoded(p["new"],PAIRS).rstrip(" ")==text,
                "R44 donor must retain exact previous text")
        raw=width(text,len(p["old"])-save)
        require(raw!=p["old"],"R44 donor became unchanged")
        donors[gid]={**p,"new":raw}
    require(set(donors)==DONOR_IDS and len(donors)==18
            and sum(len(x["old"])-len(x["new"]) for x in donors.values())==22,
            "R44 donor allocation drift")
    combined=sorted([donors.get(x["gid"],x) for x in full]+new,key=lambda x:x["offset"])
    require(len(combined)==len({x["gid"] for x in combined})==4899
            and all(a["offset"]+len(a["old"])<=b["offset"] for a,b in zip(combined,combined[1:])),
            "R44 original spans overlap")
    return new,donors,{"new":33,"donors":18,"total_if_built":8247,"resolved_without_new_bytes":1,
            "resolved_original_target":8248,"remaining":0,"fixed_offsets":False,
            "runtime_verified":False,"release_authorized":False}

def rebuild(data,table,expected):
    before,starts=read_commands(data,table)
    grouped=defaultdict(list)
    for cmd in before:grouped[cmd.block].append(cmd)
    out=bytearray();used=set()
    for block,(start,end) in enumerate(zip(starts,starts[1:])):
        require(len(out)==start,"R44 block start drift")
        for c in grouped[block]:
            slot=c.offset+7
            if slot not in expected:
                out.extend(c.raw);continue
            old,new,gid=expected[slot]
            require(c.content is not None and c.content==old and old!=new
                    and 0 not in new and len(new)+3<=65535,"R44 source slot mismatch: "+gid)
            out.extend(c.raw[:3]+struct.pack("<HH",len(new)+3,len(new))+new+b"\0")
            used.add(slot)
        require(len(out)<=end,"R44 local block overflow: "+str(block))
        out.extend(b"\0"*(end-len(out)))
    require(used==set(expected) and len(out)==len(data),"R44 incomplete replay")
    result=bytes(out)
    event=audit_script_rebuild(data,table,result,table,expected,require_fixed_offsets=False)
    require(event["total_commands"]==51705 and event["nontext_commands_byte_exact"]==46308
            and event["moved_script_starts"]==0 and event["moved_command_offsets"]==2712
            and event["moved_nontext_command_offsets"]==2221
            and event["script_blocks_with_moved_commands"]==24
            and not event["all_command_offsets_preserved"],
            "R44 authenticated relocation geometry drift")
    return result,table,event
