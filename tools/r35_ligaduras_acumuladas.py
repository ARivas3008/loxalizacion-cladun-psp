#!/usr/bin/env python3
"""R35: additive fixed-offset ligature candidate, NEVER a runtime certification."""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
sys.path.insert(0,str(Path(__file__).resolve().parent))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.r31_bulk_padding import make_plan as previous_plan, serialized, fnv
from tools.f4_r21_ligature_overlay import make_plan as ligature_plan
from tools.f4_r21_ligature_capacity import read_canonical, decode_encoded
from tools.f4_r21_ligature_collision_safe import analyze_collision_free, verify_own_iso_raster
from tools.f4_r21_ligature_font_prototype import build_in_memory
from tools.r29_integrar_longitud_fija import DRAFT, require
from tools.f3_referencias_riesgo import original_script_children, file_sha256, USA_SHA
from tools.f4_r23_font_compact_candidate import candidate_path
from tools.f4_r24_piloto_1650_ligaduras import (
    replace_original_script, replace_member_payload, update_font_in_existing_candidate, validate_final)
from tools.integrar_parche_seguro import (
    build, plan_rows, source_rows, plan_event_safe, TARGET_SCRIPT,
    patch_canonical_menu_layout, patch_canonical_menu_values,
    read_resources, parent_content, append_text_containers)
from tools.extract_cladun import dsarc_entries, decompress
from tools.r32_auditar_packs import selective_repack

PAIRS="es en de er ar ra os te qu nt do ta as el or to st on an al co na ca ad me da pa pe ci nd mo po ed ma ti mi tr cu no ha ce ec nc pu".split()
BATCHES=((1000,955,899150391,1457194777,3798519867,3296589160),
         (1000,964,4216726710,2238206101,1448831672,2992930422),
         (2,2,3342457943,2084927790,3342457943,2084927790))
BASE=5172
TOTAL=7093

def make_plan():
    rows=read_canonical(DRAFT)
    by={r["grupo_id"]:r for r in rows}
    pairs=analyze_collision_free(rows)["pairs"]
    require(pairs==PAIRS,"Codebook drift")
    raw,_=ligature_plan(rows,ligature_count=44)
    prev=previous_plan(pack="all")
    prior_ids={x["gid"] for x in prev}
    prior_offsets={x["offset"] for x in prev}
    require(len(raw)==2002 and len(prior_ids)==1448,"Pool drift")
    require(fnv(serialized(raw,False))==98947122
            and fnv(serialized(raw))==3928797122,"Original pool digest drift")
    selected=[];report=[]
    for i,(n,m,pre,post,apre,apost) in enumerate(BATCHES):
        batch=raw[i*1000:(i+1)*1000]
        admitted=[]
        require(len(batch)==n and fnv(serialized(batch,False))==pre
                and fnv(serialized(batch))==post,"Batch digest drift")
        for x in batch:
            gid=x["group_id"];r=by[gid]
            require(decode_encoded(x["new"],pairs)==r["espanol"]
                    and len(x["new"])==len(x["old"])
                    and x["new"]!=x["old"] and 0 not in x["new"],
                    "Ligature text/width mismatch")
            require((gid in prior_ids)==(x["offset"] in prior_offsets),"ID/offset collision")
            if gid not in prior_ids:admitted.append({**x,"gid":gid})
        require(len(admitted)==m and fnv(serialized(admitted,False))==apre
                and fnv(serialized(admitted))==apost,"Dedup batch digest drift")
        selected.extend(admitted)
        report.append({"batch":i+1,"checked":n,"admitted":m,"duplicate":n-m,
                       "source_bytes":sum(len(x["old"]) for x in batch)})
    require(len(selected)==1921 and fnv(serialized(selected,False))==2736158664
            and fnv(serialized(selected))==3301375592,"Final plan digest drift")
    require(hashlib.sha256(serialized(selected,False)).hexdigest()==
            "0b04add301947864eff2062f375c836cdb5b4a51ce409ab076dc8e2cb872a35b","Authentic preimage anchor drift")
    combined=sorted(prev+selected,key=lambda x:x["offset"])
    require(len({x["gid"] for x in combined})==3369
            and all(a["offset"]+len(a["old"])<=b["offset"] for a,b in zip(combined,combined[1:])),
            "R34/R35 combined overlap")
    pairs_rows,_=patch_canonical_menu_layout(source_rows())
    pairs_rows,_=patch_canonical_menu_values(pairs_rows)
    changes,blocked,_=plan_rows(pairs_rows)
    merged,_,pending,_=plan_event_safe(changes,blocked,verified_packs=True)
    pending=set(pending)
    require({x["gid"] for x in selected}<=pending,"Selected ID not deferred by R34")
    full=[{"group_id":r["grupo_id"],"gid":r["grupo_id"],
           "offset":int(r["offset_hex"],16),"old":old,"new":new}
          for r,old,new in merged[TARGET_SCRIPT]]+selected
    full.sort(key=lambda x:x["offset"])
    require(len(full)==3745 and len({x["gid"] for x in full})==3745
            and all(a["offset"]+len(a["old"])<=b["offset"] for a,b in zip(full,full[1:])),
            "Full baseline+ligature script overlaps")
    require(len(pending-{x["gid"] for x in selected})==1155,"Deferred count drift")
    return selected,full,{"batches":report,"r34":BASE,"new":1921,"total_if_built":TOTAL,
                         "pending":1155,"official":3724,"runtime_verified":False,
                         "release_authorized":False,"candidate_written":False}

def residual_inventory(selected, full):
    """Metadata-only residual triage in blocks of 1,000; no new insertion."""
    from collections import Counter
    from tools.charset_es import encode_spanish
    from tools.f4_r21_ligature_capacity import matching
    rows=read_canonical(DRAFT)
    done={x["gid"] for x in full}
    pending=[]
    for r in rows:
        if r["origen"]!=TARGET_SCRIPT or r["grupo_id"] in done:
            continue
        old=bytes.fromhex(r["bytes_hex"])
        text=r["espanol"]
        delta=len(encode_spanish(text))-len(old)
        if delta==0:continue
        controls=(any(c<32 or c>126 or c in (37,92) for c in old)
                  or "%" in text or "\\" in text or not text.isprintable())
        if controls:kind="CONTROL_OR_MULTIBYTE_REVIEW"
        elif delta<0:kind="SHORTER_NEEDS_EDITORIAL_OR_PADDING"
        elif len(matching(text,PAIRS))<delta:kind="GROWING_INSUFFICIENT_44_LIGATURES"
        else:kind="OTHER_REVIEW"
        pending.append({"id":r["grupo_id"],"offset":int(r["offset_hex"],16),
                        "delta":delta,"kind":kind})
    pending.sort(key=lambda r:r["offset"])
    require(len(pending)==1155,"Residual script count drift")
    batches=[]
    for start in range(0,len(pending),1000):
        part=pending[start:start+1000]
        batches.append({"count":len(part),"types":dict(Counter(x["kind"] for x in part)),
                        "positive":sum(x["delta"]>0 for x in part),
                        "negative":sum(x["delta"]<0 for x in part),
                        "ids_sha256":hashlib.sha256(",".join(x["id"] for x in part).encode("ascii")).hexdigest()})
    return {"count":len(pending),"types":dict(Counter(x["kind"] for x in pending)),
            "batches":batches,"newly_approved":0}


def source_audit(iso, selected, full):
    require(file_sha256(iso)==USA_SHA,"Authentic USA required")
    original,table=original_script_children(iso)
    # Each batch and then the complete accumulated SCRIPT against authentic source.
    batches=[]
    for a,b in ((0,955),(955,1919),(1919,1921)):
        _,guard=replace_original_script(original,table,selected[a:b])
        batches.append(guard)
    expected,guard=replace_original_script(original,table,full)
    require(guard["text_commands_replaced"]==3745,"Full script count")
    return expected,table,{"batches":batches,"full":guard}

def run(iso=None, candidate=None, *, experimental=False):
    selected,full,report=make_plan()
    report["residual_inventory"]=residual_inventory(selected,full)
    if iso is None:
        require(candidate is None,"ISO required")
        return report
    expected,tbl,report["source_guard"]=source_audit(iso,selected,full)
    report["original_font_raster_guard"]=verify_own_iso_raster(iso)
    if candidate is None:return report
    require(experimental,"Explicit compact-font risk acceptance required")
    target=candidate_path(candidate,iso)
    font,metric=build_in_memory(iso,DRAFT,ligature_count=44,member_alignment=16,include_binary=True)
    require(len(font)==144000 and metric["preserved_original_base_glyphs"]==2721
            and metric["preserved_existing_spanish_glyphs"]==19
            and metric["ligature_count"]==44,"Font geometry drift")
    report["font"]=metric
    with tempfile.TemporaryDirectory(prefix="r35_private_",dir=target.parent) as tmp:
        root=Path(tmp);base=root/"r34.iso"
        result=build(iso,base,root/"r34.json",experimental_partial=True,event_safe_only=True,verified_packs=True)
        require(result["texto_aplicado"]==BASE and result["dialogos_pospuestos_por_desplazamiento"]==3076,
                "R34 baseline not physically built")
        with_font=root/"font.iso"
        report["font_stage"]=update_font_in_existing_candidate(iso,base,with_font,font)
        _,pack,entries=read_resources(with_font)
        entry=next(x for x in entries if x["name"]=="SCRIPT.SDT")
        stored,archive,codec=parent_content(pack,entry)
        require(codec.startswith("IMY"),"Unexpected SCRIPT codec")
        members=dsarc_entries(archive)
        def child(name):
            m=next(x for x in members if x["name"]==name)
            return archive[m["offset"]:m["offset"]+m["size"]]
        require(child("SCRIPT.TBL")==tbl,"R34 table changed")
        modified,audit=replace_original_script(child("SCRIPT.DAT"),tbl,selected)
        require(modified==expected,"R34+R35 differs from original full replay")
        report["incremental_guard"]=audit
        updated=replace_member_payload(archive,members,"SCRIPT.DAT",modified)
        repacked,blocks=selective_repack(stored,updated)
        require(decompress(repacked,len(updated))[0]==updated,"IMY mismatch")
        staged=root/"r35.iso"
        append_text_containers(with_font,pack,entries,{"SCRIPT.SDT":(repacked,len(updated))},staged)
        report["final_guard"]=validate_final(iso,base,staged,font,expected,tbl)
        report["repacked_blocks"]=blocks
        os.link(staged,target)
    report["candidate_written"]=True
    return report

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--iso-original",type=Path)
    p.add_argument("--candidate",type=Path)
    p.add_argument("--allow-experimental-compact-font",action="store_true")
    a=p.parse_args()
    print(json.dumps(run(a.iso_original,a.candidate,experimental=a.allow_experimental_compact_font),indent=2))

if __name__=="__main__":main()
