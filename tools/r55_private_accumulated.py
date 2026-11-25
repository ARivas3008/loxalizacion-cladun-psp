"""R55 private accumulated candidate. Never exports BPS or certifies runtime."""
from pathlib import Path
import argparse
import hashlib
import json
import os
import struct
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
from tools.script_event_guard import require,read_commands,audit_script_rebuild
from tools.r54_dialogue_envelopes import rebuild
from tools.imy_repack_safe import compress_block
from tools.extract_cladun import imy_decode,decompress,dsarc_entries
from tools.r52_local_optimized import audit as plan_r52
from tools.f3_referencias_riesgo import original_script_children
from tools.f4_r23_font_compact_candidate import candidate_path
from tools.f4_r24_piloto_1650_ligaduras import replace_member_payload
from tools.integrar_parche_seguro import (
    build,source_rows,plan_rows,plan_event_safe,combine_unified_profile,
    combine_extended_padding,combine_verified_symbols,combine_reviewed_concise,
    combine_r39_concise,combine_r40_concise,combine_r42_concise,combine_r43_concise,
    patch_canonical_menu_layout,patch_canonical_menu_values,TARGET_SCRIPT,
    read_resources,parent_content,append_text_containers,sha256_file,SOURCE_SHA256)

def repack_min(original,decoded):
    n,capacity=struct.unpack_from("<II",original)
    require(1<=n<=512 and 8+4*n<=len(original),"R55 IMY count")
    offsets=struct.unpack_from("<"+"I"*n,original,8)
    require(offsets[0]>=8+4*n and list(offsets)==sorted(set(offsets)) and offsets[-1]<len(original),"R55 IMY directory")
    out=bytearray(original[:8]+bytes(n*4));cursor=0;changed=[]
    for i,at in enumerate(offsets):
        end=offsets[i+1] if i+1<n else len(original)
        old=imy_decode(original,at);piece=decoded[cursor:cursor+len(old)]
        require(len(piece)==len(old),"R55 IMY geometry")
        if old==piece:chunk=original[at:end]
        else:
            h=original[at:at+32]
            chunk=min((compress_block(piece,h),compress_block(piece,h,pending_refs=True)),key=len)
            changed.append(i)
        out.extend(bytes(-len(out)%4));struct.pack_into("<I",out,8+i*4,len(out));out.extend(chunk);cursor+=len(old)
    require(cursor==len(decoded) and decompress(bytes(out),len(decoded))[0]==decoded,"R55 IMY roundtrip")
    return bytes(out),changed

def canonical_plan():
    rows,_=patch_canonical_menu_layout(source_rows())
    rows,_=patch_canonical_menu_values(rows)
    c,b,_=plan_rows(rows)
    r36=combine_unified_profile(*plan_event_safe(c,b,verified_packs=True))
    r37=combine_verified_symbols(*combine_extended_padding(*r36))
    r38=combine_reviewed_concise(*r37)
    r39=combine_r39_concise(*r38)
    changes,blocked,deferred,info=combine_r43_concise(*combine_r42_concise(*combine_r40_concise(*r39)))
    full=[{"gid":r["grupo_id"],"offset":int(r["offset_hex"],16),"old":a,"new":z} for r,a,z in changes[TARGET_SCRIPT]]
    sel,donors,_=plan_r52(full,deferred)
    slots=lambda seq:{x["offset"]:(x["old"],x["new"],x["gid"]) for x in seq}
    require(len(full)==4866 and sum(map(len,changes.values()))==8214,"R55 baseline count")
    return slots(full),slots(sel),slots(donors.values())

def build_private(iso,candidate,report,*,native_ellipsis=False):
    iso=Path(iso).resolve(strict=True);candidate=candidate_path(Path(candidate),iso)
    report=candidate_path(Path(report),iso)
    require(candidate!=report and sha256_file(iso)==SOURCE_SHA256,"R55 inputs")
    source,table=original_script_children(iso)
    baseline,residuals,donors=canonical_plan()
    if native_ellipsis:
        from tools.r56_native_ellipsis import extend_donors,verify_native_glyph
        verify_native_glyph(iso)
        donors=extend_donors(baseline,residuals,donors)
    new,event,envelopes=rebuild(source,table,residuals,donors,baseline,include_speakers=True)
    require((len(envelopes),event["text_commands_replaced"],event["moved_command_offsets"],
        event["moved_nontext_command_offsets"],event["nontext_commands_byte_exact"])==((22,4888,28,5,46308) if native_ellipsis else (21,4887,27,5,46308)),"R55/R56 geometry")
    with tempfile.TemporaryDirectory(prefix="cladun_r55_",dir=candidate.parent) as td:
        tmp=Path(td);fixed=tmp/"fixed.iso";fixed_report=tmp/"fixed.json";staged=tmp/"final.iso"
        build(iso,fixed,fixed_report,experimental_partial=True,event_safe_only=True,verified_packs=True,
              unified_profile=True,extended_padding=True,verified_symbols=True,concise_verified=True,
              r39_verified=True,r40_verified=True,r42_verified=True,r43_verified=True)
        _,pkg,entries=read_resources(fixed);e=next(x for x in entries if x["name"]=="SCRIPT.SDT")
        stored,arc,_=parent_content(pkg,e);members=dsarc_entries(arc);by={m["name"]:m for m in members}
        child=lambda name:arc[by[name]["offset"]:by[name]["offset"]+by[name]["size"]]
        require(child("SCRIPT.TBL")==table,"R55 baseline table drift")
        audit_script_rebuild(source,table,child("SCRIPT.DAT"),table,baseline,require_fixed_offsets=True)
        rewritten=replace_member_payload(arc,members,"SCRIPT.DAT",new)
        packed,ch=repack_min(stored,rewritten)
        meta=append_text_containers(fixed,pkg,entries,{"SCRIPT.SDT":(packed,len(rewritten))},staged)
        require(sha256_file(iso)==SOURCE_SHA256,"R55 source drift")
        _,fp,fe=read_resources(staged);_,fr,_=parent_content(fp,next(x for x in fe if x["name"]=="SCRIPT.SDT"))
        require(fr==rewritten,"R55 staged script drift")
        result={"schema":("cladun.r56.private_accumulated.v1" if native_ellipsis else "cladun.r55.private_accumulated.v1"),"estado":"EXPERIMENTAL_NO_EXPORTAR",
                "iso_resultante_sha256":sha256_file(staged),"texto_aplicado":8235+int(native_ellipsis),
                "resolved_original_target":8236+int(native_ellipsis),"remaining":12-int(native_ellipsis),"native_ellipsis":native_ellipsis,"auditoria_eventos":event,
                "offsets_de_comandos_preservados":False,"control_logico_no_textual_intacto":True,
                "event_logic_runtime_certified":False,"runtime_verified":False,"release_authorized":False,
                "script_repacked_chunks":ch,"metadata":meta,"envelopes":envelopes}
        rp=tmp/"result.json";rp.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
        os.link(staged,candidate)
        try:os.link(rp,report)
        except Exception:
            candidate.unlink();raise
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--iso",required=True,type=Path)
    p.add_argument("--candidate",required=True,type=Path);p.add_argument("--report",required=True,type=Path)
    p.add_argument("--acepto-reubicacion-local",action="store_true")
    p.add_argument("--puntos-suspensivos-nativos",action="store_true",help="R56 opt-in: one additional dialogue, visual QA pending")
    a=p.parse_args()
    if not a.acepto_reubicacion_local:p.error("R55 remains experimental; explicit acceptance required")
    print(json.dumps(build_private(a.iso,a.candidate,a.report,native_ellipsis=a.puntos_suspensivos_nativos),indent=2))
