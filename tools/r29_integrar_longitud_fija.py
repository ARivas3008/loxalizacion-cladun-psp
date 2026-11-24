#!/usr/bin/env python3
"""R29: integrate reviewed exact-width alternatives into a private event-safe baseline.

No new glyphs, ligatures, trailing padding, or shifted event commands. The
baseline already includes the existing 19-sign Spanish font. Static approval
is NOT a claim that rendering or game traversal is certified.
"""
from __future__ import annotations
import argparse
import csv
import json
import os
from pathlib import Path
import tempfile
try:
    from tools.f4_r21_ligature_capacity import read_canonical
    from tools.f4_r18_propuestas_globales import draft_geometry
    from tools.f3_propuestas_longitud_fija import proposal_plan, STATUS
    from tools.f3_referencias_riesgo import original_script_children, file_sha256, USA_SHA
    from tools.f4_r23_font_compact_candidate import candidate_path
    from tools.f4_r24_piloto_1650_ligaduras import replace_original_script, replace_member_payload
    from tools.integrar_parche_seguro import build, read_resources, parent_content, append_text_containers
    from tools.extract_cladun import dsarc_entries, decompress
    from tools.imy_repack_safe import recompress
except ModuleNotFoundError:
    from f4_r21_ligature_capacity import read_canonical
    from f4_r18_propuestas_globales import draft_geometry
    from f3_propuestas_longitud_fija import proposal_plan, STATUS
    from f3_referencias_riesgo import original_script_children, file_sha256, USA_SHA
    from f4_r23_font_compact_candidate import candidate_path
    from f4_r24_piloto_1650_ligaduras import replace_original_script, replace_member_payload
    from integrar_parche_seguro import build, read_resources, parent_content, append_text_containers
    from extract_cladun import dsarc_entries, decompress
    from imy_repack_safe import recompress

ROOT=Path(__file__).resolve().parents[1]
DRAFT=ROOT/"traduccion/CLADUN_BORRADOR_ES.csv"
PROPOSALS=ROOT/"traduccion/propuestas"
SELECTED_R19=frozenset("000003 000010 000016 000035 000036 000777 000784 000786 000787 000791 000800 000801 000806 000807 000808 000812 000813 000816 000818 000820 000821 000826 000831 000832 000833 000852 000858 000863 000864 000866 000871".split())
SELECTED_R20=frozenset("000913 000937 000977".split())
SELECTED_R21=frozenset("001020 001037 001045 001080 001100 001113 001125 001126 001143 001153 001203 001209 001257 001270 001275 001286 001309 001342 002841".split())
REPEAT={"002119":"001275","002887":"000816","004656":"001113"}
TOTAL=56

def require(ok,message):
    if not ok:
        raise ValueError(message)

def csv_rows(path):
    with path.open(encoding="utf-8-sig",newline="") as f:
        return list(csv.DictReader(f))

def select(rows):
    by={r["grupo_id"]:r for r in rows}
    require(len(by)==9237,"Canonical corpus IDs changed")
    selected={}
    specs=(("DICTAMEN_64_R19.csv",SELECTED_R19),
           ("SCRIPT_SCR02_LONGITUD_FIJA_R20.csv",SELECTED_R20),
           ("SCRIPT_POSTPROLOGO_LONGITUD_FIJA_R21.csv",SELECTED_R21))
    for name,ids in specs:
        matches=[r for r in csv_rows(PROPOSALS/name) if r["grupo_id"] in ids]
        require(len(matches)==len(ids),"Review source incomplete")
        for r in matches:
            gid=r["grupo_id"]
            require(gid not in selected,"Duplicate proposal")
            if name.startswith("DICTAMEN"):
                require(r["dictamen_r19"]=="APTA_REVISION_ESTATICA_NO_CANONICA","Rejected or ambiguous R19 proposal")
                require(r["original_en"]==by[gid]["original"] and r["canonico_es"]==by[gid]["espanol"],"Reviewed text drift")
            else:
                require(int(r["offset_hex"],16)==int(by[gid]["offset_hex"],16),"Reviewed offset drift")
            selected[gid]=r["propuesta_es"]
    for gid,anchor in REPEAT.items():
        require(gid not in selected and anchor in selected,"Repeat anchor missing")
        require(by[gid]["original"]==by[anchor]["original"] and by[gid]["espanol"]==by[anchor]["espanol"],"Repeated line differs")
        selected[gid]=selected[anchor]
    require(len(selected)==TOTAL,"Selected count drift")
    return [{"grupo_id":gid,"offset_hex":by[gid]["offset_hex"],
             "longitud_original_bytes":by[gid]["longitud_original_bytes"],
             "propuesta_es":text,"estado":STATUS} for gid,text in selected.items()]

def make_plan(draft=DRAFT):
    rows=read_canonical(draft)
    plan=proposal_plan(rows,draft_geometry(rows),select(rows))
    require(len(plan)==TOTAL and sum(x["new"].isascii() for x in plan)==16,
            "Exact-width selection drift")
    return [{**x,"group_id":x["gid"]} for x in plan]

def verify_resources(before,oldpack,after,newpack):
    require(len(before)==len(after)==349,"PSPFS count changed")
    intact=0
    for a,b in zip(before,after):
        require(a["name"]==b["name"] and a["index"]==b["index"],"PSPFS order changed")
        if a["name"]=="SCRIPT.SDT":
            continue
        require(a==b,"Non-SCRIPT resource metadata changed")
        at,z=a["offset"],a["size_stored"]
        require(oldpack[at:at+z]==newpack[at:at+z],"Non-SCRIPT resource modified")
        intact+=1
    require(intact==348,"Unexpected resource count")
    return intact

def run(iso=None,candidate=None, *, plan_builder=make_plan):
    plan=plan_builder()
    count=len(plan)
    ascii_count=sum(x["new"].isascii() for x in plan)
    require(count>0 and len({x["offset"] for x in plan})==count,"Empty or duplicate plan")
    result={"selected":count,"ascii":ascii_count,"existing_spanish_font_required":count-ascii_count,
            "candidate_total_if_built":3724+count,"official_integrated_unchanged":3724,
            "new_official_integrations":0,"private_candidate_written":False,
            "ppsspp_run":False,"release_authorized":False}
    if iso is None:
        require(candidate is None,"ISO required")
        return result
    require(candidate is not None and file_sha256(iso)==USA_SHA,"Authentic original and private candidate required")
    target=candidate_path(candidate,iso)
    original,tbl=original_script_children(iso)
    _,source_guard=replace_original_script(original,tbl,plan)
    result["source_event_guard"]=source_guard
    with tempfile.TemporaryDirectory(prefix="r29_private_",dir=target.parent) as tmp:
        root=Path(tmp)
        baseline=root/"baseline.iso"
        base_result=build(iso,baseline,root/"baseline.json",experimental_partial=True,event_safe_only=True)
        require(base_result["texto_aplicado"]==3724 and base_result["dialogos_pospuestos_por_desplazamiento"]==4524,
                "Baseline count drift")
        _,pack,records=read_resources(baseline)
        entry=next(r for r in records if r["name"]=="SCRIPT.SDT")
        stored,decoded,codec=parent_content(pack,entry)
        require(codec.startswith("IMY"),"Unexpected SCRIPT codec")
        members=dsarc_entries(decoded)
        def child(blob,name):
            r=next(x for x in members if x["name"]==name)
            return blob[r["offset"]:r["offset"]+r["size"]]
        require(child(decoded,"SCRIPT.TBL")==tbl,"Baseline table changed")
        modified,event_guard=replace_original_script(child(decoded,"SCRIPT.DAT"),tbl,plan)
        archive=replace_member_payload(decoded,members,"SCRIPT.DAT",modified)
        repacked=recompress(stored,archive)
        require(decompress(repacked,len(archive))[0]==archive,"IMY roundtrip failed")
        staged=root/"combined.iso"
        append_text_containers(baseline,pack,records,{"SCRIPT.SDT":(repacked,len(archive))},staged)
        _,final_pack,final_records=read_resources(staged)
        result["unchanged_resources_vs_baseline"]=verify_resources(records,pack,final_records,final_pack)
        final_entry=next(r for r in final_records if r["name"]=="SCRIPT.SDT")
        _,final_archive,_=parent_content(final_pack,final_entry)
        require(final_archive==archive and dsarc_entries(final_archive)==members,"Final SCRIPT archive differs")
        require(file_sha256(iso)==USA_SHA,"Original altered")
        result["additional_event_guard"]=event_guard
        result["candidate_sha256"]=file_sha256(staged)
        os.link(staged,target)
    result["private_candidate_written"]=True
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--iso-original",type=Path)
    p.add_argument("--candidate",type=Path)
    a=p.parse_args()
    print(json.dumps(run(a.iso_original,a.candidate),indent=2))

if __name__=="__main__":
    main()
