"""R57 auxiliary dialogue storage only. No callers linked; never export BPS."""
from __future__ import annotations
import argparse
from collections import OrderedDict
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from tools.script_event_guard import Command,read_commands,require,u16,u32,TEXT_OPS
from tools.extract_cladun import dsarc_entries,decompress,imy_decode
from tools.imy_repack_safe import compress_block
from tools.r57_imy_refresh import prepare,encode_refresh
from tools.r55_private_accumulated import canonical_plan,build_private as build_r56
from tools.r56_native_ellipsis import extend_donors
from tools.r54_dialogue_envelopes import choose
from tools.r35_ligaduras_acumuladas import PAIRS
from tools.f4_r21_ligature_capacity import decode_encoded
from tools.f3_referencias_riesgo import original_script_children
from tools.f4_r23_font_compact_candidate import candidate_path
from tools.integrar_parche_seguro import read_resources,parent_content,append_text_containers,sha256_file,SOURCE_SHA256

REMAINING=frozenset("001278 001662 002372 002733 002919 003097 003489 003566 004544 004546 004623".split())

def dynamic_parse(data,table):
    # Deliberately separate from release guard, which still requires 1625 blocks.
    n=u32(table,0)
    require(0<n<10000 and len(table)==16+32*n,"R57 table length")
    starts=[u32(table,20+32*i) for i in range(n)]+[len(data)]
    require(starts[0]==0 and starts==sorted(starts) and all(p%16==0 for p in starts),"R57 start geometry")
    out=[]
    for b,(p,end) in enumerate(zip(starts,starts[1:])):
        order=0
        while p+5<=end and any(data[p:end]):
            op=data[p];iid=u16(data,p+1);size=u16(data,p+3);q=p+5+size
            require(q<=end,"R57 command crosses block")
            raw=data[p:q];content=None
            if op in TEXT_OPS:
                require(size>=3 and u16(raw,5)+3==size and raw[-1]==0,"R57 invalid text")
                content=raw[7:-1]
            out.append(Command(b,order,p,op,iid,raw,content));p=q;order+=1
        require(not any(data[p:end]),"R57 nonzero tail")
    return out,starts

def native_call_pattern(commands,table):
    ids={u32(table,16+32*i) for i in range(u32(table,0))}
    pairs=matched=total=0
    for i,c in enumerate(commands):
        if c.code!=0x0A:continue
        total+=1
        if len(c.raw)!=9 or i+1==len(commands):continue
        nxt=commands[i+1]
        if (nxt.block,nxt.code,nxt.instruction_id,len(nxt.raw))==(c.block,0x05,c.instruction_id,5):
            pairs+=1;matched+=u32(c.raw,5) in ids
    return {"opcode_0a":total,"exact_following_05":pairs,"arg_matches_script_id":matched,
            "semantics_proven":False}

def encode_helper(lines,ids):
    def command(op,payload=b""):
        return bytes((op,))+struct.pack("<HH",next(ids),len(payload))+payload
    raw=bytearray(command(0x64))
    for line in lines:
        require(line and 0 not in line and len(line)+3<=65535,"R57 invalid helper text")
        raw.extend(command(0x66,struct.pack("<H",len(line))+line+b"\0"))
    raw.extend(command(0x65));raw.extend(command(0x08))
    raw.extend(bytes(-len(raw)%16));return bytes(raw)

def stage_auxiliary(data,table,archive,baseline,residuals,remaining):
    before,starts=read_commands(data,table)
    require(len(before)==51705 and len(starts)==1626,"R57 baseline")
    require(tuple(c.code for c in before if c.block==52)==(0x64,0x66,0x65,0x08),
            "R57 native minimal box template drift")
    pattern=native_call_pattern(before,table)
    require((pattern["opcode_0a"],pattern["exact_following_05"],pattern["arg_matches_script_id"])==(862,862,320),
            "R57 native candidate call pattern drift")
    slots={c.offset+7:i for i,c in enumerate(before) if c.content is not None}
    variants=OrderedDict();sites=[]
    for offset,(old,new,gid) in sorted(residuals.items()):
        if gid not in remaining:continue
        require(offset in slots,"R57 residual slot missing")
        i=slots[offset];c=before[i]
        require(c.code==0x66 and c.content==old,"R57 unresolved source mismatch "+gid)
        l=r=i
        while l>0 and before[l-1].block==c.block and before[l-1].code==0x66:l-=1
        while r+1<len(before) and before[r+1].block==c.block and before[r+1].code==0x66:r+=1
        require(l>0 and r+1<len(before) and before[l-1].block==before[r+1].block==c.block
                and before[l-1].code==0x64 and before[r+1].code==0x65,"R57 envelope boundary")
        lines=[]
        for j in range(l,r+1):
            x=before[j]
            if j==i:lines.append(new)
            else:
                require(gid=="003566" and x.offset+7 in baseline,"R57 unexpected companion")
                a,b,companion=baseline[x.offset+7]
                require(companion=="003567" and x.content==b and decode_encoded(b,PAIRS)=="¿Eh?",
                        "R57 exact companion mismatch")
                lines.append(b)
        variants.setdefault(tuple(lines),[]).append(gid)
        left,right=before[l-1],before[r+1];n=right.offset+len(right.raw)-left.offset
        sites.append({"gid":gid,"block":c.block,"source_script_id":u32(table,16+32*c.block),
                      "first_offset":left.offset,"last_offset_exclusive":right.offset+len(right.raw),
                      "source_instruction_id":c.instruction_id,"box_bytes":n,
                      "hypothetical_call_bytes":14,"unresolved_filler_bytes":n-14,"linked":False})
    require(set(x["gid"] for x in sites)==remaining==REMAINING and len(variants)==7,"R57 residual geometry")
    original_ids={u32(table,16+32*i) for i in range(1625)}
    original_iids={c.instruction_id for c in before}
    require(max(original_iids)==3224,"R57 instruction ID maximum drift")
    ids=iter(i for i in range(3225,32768) if i not in original_iids)
    sids=(i for i in range(962160,963000) if i not in original_ids and struct.pack("<I",i) not in archive)
    d=bytearray(data);t=bytearray(table);helpers=[]
    for lines,gids in variants.items():
        sid=next(sids);start=len(d);encoded=encode_helper(lines,ids)
        d.extend(encoded);t.extend(struct.pack("<II24s",sid,start,b"r57_dialogue.dsf"))
        helpers.append({"script_id":sid,"block":1625+len(helpers),"offset":start,"bytes":len(encoded),
                        "lines":len(lines),"source_gids":gids,"command_count":len(lines)+3})
        for site in sites:
            if site["gid"] in gids:site["candidate_script_id"]=sid
    struct.pack_into("<I",t,0,1632)
    out,after_starts=dynamic_parse(bytes(d),bytes(t))
    require(bytes(d[:len(data)])==data and bytes(t[4:len(table)])==table[4:]
            and out[:len(before)]==before and after_starts[:1626]==starts
            and len(out)==51734 and len(d)-len(data)==272 and len(t)-len(table)==224,
            "R57 existing prefix or helper geometry changed")
    return bytes(d),bytes(t),{"helpers":helpers,"sites":sites,"native_call_pattern":pattern,
                             "new_commands":29,"existing_commands_preserved":51705,
                             "existing_block_starts_preserved":1625,"call_sites_linked":0}

def extend_archive(archive,members,data,table,stored):
    by={m["name"]:m for m in members}
    require(set(by)=={"AISCRIPT.DAT","AISCRIPT.TBL","SCRIPT.DAT","SCRIPT.TBL"},"R57 DSARC shape")
    a,b=by["SCRIPT.DAT"],by["SCRIPT.TBL"]
    require(a["offset"]+len(data)<=b["offset"] and
            not any(archive[a["offset"]+a["size"]:b["offset"]]) and
            not any(archive[b["offset"]+b["size"]:]),"R57 source padding")
    n=u32(stored,0);last=u32(stored,8+4*(n-1));quantum=2*u16(stored,last+8)
    extension=((max(0,b["offset"]+len(table)-len(archive))+quantum-1)//quantum)*quantum
    require(extension==256,"R57 expanded geometry drift")
    out=bytearray(archive+bytes(extension))
    out[a["offset"]:a["offset"]+len(data)]=data
    out[b["offset"]:b["offset"]+len(table)]=table
    for member,blob in ((a,data),(b,table)):
        struct.pack_into("<I",out,int(member["table_offset_hex"],16)+40,len(blob))
    rebuilt=dsarc_entries(out)
    require([(m["name"],m["offset"]) for m in rebuilt]==[(m["name"],m["offset"]) for m in members],
            "R57 DSARC offset drift")
    for m in members:
        if m["name"] not in ("SCRIPT.DAT","SCRIPT.TBL"):
            p,n=m["offset"],m["size"]
            require(out[p:p+n]==archive[p:p+n],"R57 unrelated member changed")
    return bytes(out)

def repack_extended(stored,decoded):
    n=u32(stored,0);offsets=[u32(stored,8+4*i) for i in range(n)]+[len(stored)]
    require(1<=n<=512 and offsets==sorted(set(offsets)) and offsets[0]>=8+4*n,
            "R57 IMY directory")
    out=bytearray(stored[:8]+bytes(n*4));cursor=0;changed=[]
    for i,(at,end) in enumerate(zip(offsets,offsets[1:])):
        old=imy_decode(stored,at);h=bytearray(stored[at:at+32])
        piece=decoded[cursor:cursor+len(old)] if i<n-1 else decoded[cursor:]
        if len(piece)!=len(old):
            stride=u16(h,8);rows=len(piece)//stride
            require(i==n-1 and len(piece)>len(old) and len(piece)%(2*stride)==0 and rows<=1024,
                    "R57 final block geometry")
            struct.pack_into("<H",h,12,rows);struct.pack_into("<I",h,4,0x20|((rows//2)<<8))
        if old==piece:chunk=stored[at:end]
        else:
            pre=prepare(piece,h)
            variants=[compress_block(piece,h),compress_block(piece,h,pending_refs=True)]
            for limit,fc in ((32,True),(128,True),(16,False)):
                try:variants.append(encode_refresh(piece,h,pre,distance=320,next_limit=limit,flush_cost=fc))
                except ValueError:pass
            chunk=min(variants,key=len);require(imy_decode(chunk,0)==piece,"R57 IMY chunk roundtrip")
            changed.append(i)
        out.extend(bytes(-len(out)%4));struct.pack_into("<I",out,8+4*i,len(out));out.extend(chunk);cursor+=len(piece)
    require(cursor==len(decoded) and decompress(bytes(out),len(decoded))[0]==decoded,"R57 full IMY roundtrip")
    return bytes(out),changed

def build_storage(iso,candidate,report):
    iso=Path(iso).resolve(strict=True);candidate=candidate_path(Path(candidate),iso);report=candidate_path(Path(report),iso)
    require(candidate!=report and sha256_file(iso)==SOURCE_SHA256,"R57 source inputs")
    original,original_table=original_script_children(iso)
    baseline,residuals,donors=canonical_plan()
    donors=extend_donors(baseline,residuals,donors)
    _,envelopes=choose(read_commands(original,original_table)[0],residuals,donors,include_speakers=True)
    remaining={gid for _,_,gid in residuals.values()}-{e[3] for e in envelopes}
    require(len(envelopes)==22 and remaining==REMAINING,"R57 R56 selection drift")
    with tempfile.TemporaryDirectory(prefix="cladun_r57_",dir=candidate.parent) as td:
        tmp=Path(td);base=tmp/"R56.iso";base_report=tmp/"R56.json";staged=tmp/"R57.iso"
        summary=build_r56(iso,base,base_report,native_ellipsis=True)
        require(summary["resolved_original_target"]==8237,"R57 R56 accumulated count")
        _,pkg,entries=read_resources(base);e=next(x for x in entries if x["name"]=="SCRIPT.SDT")
        stored,archive,_=parent_content(pkg,e);members=dsarc_entries(archive);by={m["name"]:m for m in members}
        child=lambda name:archive[by[name]["offset"]:by[name]["offset"]+by[name]["size"]]
        d,t=child("SCRIPT.DAT"),child("SCRIPT.TBL")
        require(t==original_table,"R57 R56 table drift")
        d2,t2,audit=stage_auxiliary(d,t,archive,baseline,residuals,remaining)
        expanded=extend_archive(archive,members,d2,t2,stored);packed,ch=repack_extended(stored,expanded)
        # Accumulated path uses the existing append-only isolation guard.
        # The authentic isolated diagnostic used an in-place slot; these are distinct.
        metadata=append_text_containers(base,pkg,entries,{"SCRIPT.SDT":(packed,len(expanded))},staged)
        _,fp,fe=read_resources(staged);_,actual,_=parent_content(fp,next(x for x in fe if x["name"]=="SCRIPT.SDT"))
        require(actual==expanded and sha256_file(iso)==SOURCE_SHA256,"R57 staged archive or source drift")
        result={"schema":"cladun.r57.private_accumulated_storage.v1","estado":"EXPERIMENTAL_NO_EXPORTAR",
                "iso_resultante_sha256":sha256_file(staged),"texto_aplicado":8236,
                "resolved_original_target":8237,"remaining":11,"auxiliary_texts_stored":11,
                "all_target_text_storage_planned":8248,"audit":audit,"script_repacked_chunks":ch,
                "metadata":metadata,"offsets_de_comandos_preservados":False,
                "event_logic_runtime_certified":False,"runtime_verified":False,"release_authorized":False}
        rp=tmp/"report.json";rp.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
        os.link(staged,candidate)
        try:os.link(rp,report)
        except Exception:candidate.unlink();raise
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__)
    for k in ("iso","candidate","report"):p.add_argument("--"+k,required=True,type=Path)
    p.add_argument("--acepto-auxiliares-sin-enlazar",action="store_true")
    a=p.parse_args()
    if not a.acepto_auxiliares_sin_enlazar:p.error("Auxiliaries are unlinked and runtime-unverified")
    print(json.dumps(build_storage(a.iso,a.candidate,a.report),indent=2))
