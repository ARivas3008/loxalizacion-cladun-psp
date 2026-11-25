"""R54: isolate balanced text relocation within native dialogue envelopes.
Static evidence only; no new page insertion, no runtime or release claim.
"""
import argparse
import json
import struct
from collections import Counter
from pathlib import Path
from tools.script_event_guard import read_commands, audit_script_rebuild, require

def choose(commands,residuals,donors,*,include_speakers=False):
    slots={c.offset+7:i for i,c in enumerate(commands) if c.content is not None}
    accepted={};envelopes=[]
    for p,(old,new,gid) in residuals.items():
        i=slots[p];c=commands[i]
        require(c.content==old and len(new)>len(old),"R54 source mismatch")
        if c.code==0x66:
            l=r=i
            while l>0 and commands[l-1].block==c.block and commands[l-1].code in (0x66,0x67):l-=1
            while r+1<len(commands) and commands[r+1].block==c.block and commands[r+1].code in (0x66,0x67):r+=1
            if l==0 or r+1==len(commands):continue
            a,b=commands[l-1],commands[r+1]
            if (a.block,a.code,b.block,b.code)!=(c.block,0x64,c.block,0x65):continue
            group=commands[l:r+1]
        elif include_speakers and c.code==0x6e:
            r=i+1
            if r>=len(commands) or (commands[r].block,commands[r].code)!=(c.block,0x64):continue
            r+=1
            while r<len(commands) and commands[r].block==c.block and commands[r].code in (0x66,0x67):r+=1
            if r>=len(commands) or (commands[r].block,commands[r].code)!=(c.block,0x65):continue
            a,b=c,commands[r]
            group=commands[i:r]
        else:continue
        if sum(x.offset+7 in residuals for x in group)!=1:continue
        local={x.offset+7:donors[x.offset+7] for x in group if x.offset+7 in donors}
        for q,(old_d,new_d,_) in local.items():
            require(commands[slots[q]].content==old_d and len(new_d)<len(old_d),"R54 donor mismatch")
        if len(new)-len(old)!=sum(len(x[0])-len(x[1]) for x in local.values()):continue
        require(not (set(local)|{p})&set(accepted),"R54 duplicate")
        accepted.update(local);accepted[p]=(old,new,gid)
        envelopes.append((c.block,a.offset,b.offset,gid))
    return accepted,envelopes

def rebuild(data,table,residuals,donors,baseline=None,*,include_speakers=False):
    commands,starts=read_commands(data,table)
    selected,envelopes=choose(commands,residuals,donors,include_speakers=include_speakers)
    expected=dict(baseline or {})
    require(all(len(old)==len(new) for old,new,_ in expected.values()),"R54 baseline not fixed")
    expected.update(selected)
    out=bytearray();last=0
    for c in commands:
        out.extend(data[last:c.offset]);last=c.offset+len(c.raw)
        slot=c.offset+7
        if slot not in expected:out.extend(c.raw);continue
        old,new,gid=expected[slot]
        require(c.content==old and old!=new and 0 not in new and len(new)+3<=65535,"R54 invalid replacement "+gid)
        out.extend(c.raw[:3]+struct.pack("<HH",len(new)+3,len(new))+new+b"\0")
    out.extend(data[last:])
    require(len(out)==len(data),"R54 size drift")
    after,_=read_commands(bytes(out),table)
    event=audit_script_rebuild(data,table,bytes(out),table,expected,require_fixed_offsets=False)
    for a,b in zip(commands,after):
        if a.offset==b.offset:continue
        require(any(block==a.block and l<a.offset<r for block,l,r,_ in envelopes)
                and a.code in ((0x64,0x66,0x67) if include_speakers else (0x66,0x67)),"R54 movement escaped dialogue")
    require(event["moved_script_starts"]==0,"R54 moved block")
    return bytes(out),event,envelopes

def audit(iso):
    from tools.f3_referencias_riesgo import original_script_children
    from tools.r44_local_experimental import RESIDUAL,width
    from tools.r52_local_optimized import DONORS
    from tools.r35_ligaduras_acumuladas import PAIRS
    from tools.f4_r21_ligature_capacity import matching
    from tools.charset_es import encode_spanish
    import hashlib
    data,table=original_script_children(iso)
    commands,_=read_commands(data,table)
    slots={c.offset+7:c.content for c in commands if c.content is not None}
    residuals={};donors={}
    for line in RESIDUAL.read_text(encoding="utf-8").splitlines():
        gid,p,text=line.split("\t",2);p=int(p,16)
        n=len(encode_spanish(text))-len(matching(text,PAIRS))
        residuals[p]=(slots[p],width(text,n),gid)
    for line in DONORS.read_text(encoding="utf-8").splitlines():
        gid,p,save,text=line.split("\t",3);p=int(p,16)
        donors[p]=(slots[p],width(text,len(slots[p])-int(save)),gid)
    out,event,envelopes=rebuild(data,table,residuals,donors)
    require((len(envelopes),event["text_commands_replaced"],event["moved_command_offsets"],
             event["moved_nontext_command_offsets"])==(18,36,21,2),"R54 geometry drift")
    require(hashlib.sha256(out).hexdigest()=="0a595767efb16d27b9915706cf5b6aca9f81af7a828b7b2c40ac5ad249bac8d7","R54 isolated digest drift")
    return {"evidence":"A_STATIC_ONLY","envelopes":envelopes,"event_audit":event,
            "isolated_sha256":hashlib.sha256(out).hexdigest(),"runtime_verified":False,
            "release_authorized":False,"accumulated_iso_built":False}

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--iso-original",type=Path,required=True)
    print(json.dumps(audit(p.parse_args().iso_original),indent=2))
