#!/usr/bin/env python3
"""R30: reviewed exact-pair repeated SCRIPT alternatives, cumulative R29 + R30.

The 90 additional slots match original English AND existing canonical Spanish
exactly. No fuzzy matching, no whitespace padding, no ligatures, no changed
event offsets. This is static experimental integration, not release approval.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
try:
    from tools.r29_integrar_longitud_fija import DRAFT, make_plan as r29_plan, run as build, require
    from tools.f4_r21_ligature_capacity import read_canonical
    from tools.f4_r18_propuestas_globales import draft_geometry
    from tools.f3_propuestas_longitud_fija import proposal_plan, STATUS
except ModuleNotFoundError:
    from r29_integrar_longitud_fija import DRAFT, make_plan as r29_plan, run as build, require
    from f4_r21_ligature_capacity import read_canonical
    from f4_r18_propuestas_globales import draft_geometry
    from f3_propuestas_longitud_fija import proposal_plan, STATUS

# (original, unchanged canonical draft, candidate, exact number of slots).
RULES=(
 ("You can now go to a new dungeon!","¡Ahora puedes ir a una nueva mazmorra!","¡Puedes ir a una nueva mazmorra!",52),
 ("What do you want to know?","¿Qué quieres saber?","¿Qué te interesa conocer?",6),
 ("What?!","¡¿Qué?!","¿Qué?!",5),
 ("Argh!","¡Argh!","¡Agh!",5),
 ("Ahhh!","¡Ahhh!","¡Ahh!",4),
 ("You now have access to the Tavern.","Ahora tienes acceso a la taberna.","Ahora puedes acceder a la taberna.",4),
 ("Don't run away!","¡No huyas!","¡No te escapes!",3),
 ("Who goes there?!","¿Quién va ahí?","¿Quién anda ahí?",3),
 ("Allows you to use ranged attacks.","Te permite usar ataques a distancia.","Permite usar ataques a distancia.",2),
 ("Elements are decided by the type of staff.","Los elementos se determinan en función del tipo de bastón.","Los elementos dependen del tipo de bastón.",2),
 ("Brown treasure chests keep reappearing.","Los cofres del tesoro marrones siguen reapareciendo.","Los cofres marrones vuelven a aparecer.",2),
 ("This is your playable character.","Este es tu personaje jugable.","Es el personaje que puedes usar.",2),
)
TOTAL=90
COMBINED=146

def select(rows):
    selected=[]
    for original,draft,candidate,count in RULES:
        matches=[r for r in rows if r["origen"]=="SCRIPT.SDT/SCRIPT.DAT"
                 and r["original"]==original and r["espanol"]==draft]
        require(len(matches)==count,"Exact-pair rule count changed")
        for r in matches:
            require(bytes.fromhex(r["bytes_hex"])==original.encode("ascii"),
                    "Source bytes not equal to reviewed original")
            selected.append({"grupo_id":r["grupo_id"],"offset_hex":r["offset_hex"],
                "longitud_original_bytes":r["longitud_original_bytes"],
                "propuesta_es":candidate,"estado":STATUS})
    require(len(selected)==TOTAL and len({x["grupo_id"] for x in selected})==TOTAL,
            "New selection count/identity changed")
    return selected

def make_plan(draft=DRAFT):
    rows=read_canonical(draft)
    new=proposal_plan(rows,draft_geometry(rows),select(rows))
    require(len(new)==TOTAL and sum(x["new"].isascii() for x in new)==10,
            "R30 byte-width or font dependency drift")
    combined=r29_plan(draft)+[{**x,"group_id":x["gid"]} for x in new]
    combined.sort(key=lambda x:x["offset"])
    require(len(combined)==COMBINED and len({x["gid"] for x in combined})==COMBINED
            and len({x["offset"] for x in combined})==COMBINED,
            "R29/R30 overlap")
    require(all(a["offset"]+len(a["old"])<=b["offset"] for a,b in zip(combined,combined[1:])),
            "Overlapping spans")
    require(sum(x["new"].isascii() for x in combined)==26,"ASCII inventory changed")
    return combined

def run(iso=None,candidate=None):
    return build(iso,candidate,plan_builder=make_plan)

def run_isolated(iso,candidate, *, plan_builder=make_plan):
    """Build 146 on authentic USA + existing 19-glyph font, not F1 baseline."""
    import os
    import tempfile
    try:
        from tools.f3_referencias_riesgo import original_script_children, file_sha256, USA_SHA
        from tools.f4_r23_font_compact_candidate import candidate_path
        from tools.f4_r24_piloto_1650_ligaduras import replace_original_script, replace_member_payload
        from tools.integrar_parche_seguro import read_resources, parent_content, append_text_containers
        from tools.font_es_narrow import build as build_font, verify as verify_font
        from tools.extract_cladun import dsarc_entries, decompress
        from tools.imy_repack_safe import recompress
        from tools.r29_integrar_longitud_fija import verify_resources
    except ModuleNotFoundError:
        from f3_referencias_riesgo import original_script_children, file_sha256, USA_SHA
        from f4_r23_font_compact_candidate import candidate_path
        from f4_r24_piloto_1650_ligaduras import replace_original_script, replace_member_payload
        from integrar_parche_seguro import read_resources, parent_content, append_text_containers
        from font_es_narrow import build as build_font, verify as verify_font
        from extract_cladun import dsarc_entries, decompress
        from imy_repack_safe import recompress
        from r29_integrar_longitud_fija import verify_resources
    require(iso is not None and candidate is not None,"Private ISO and output required")
    require(file_sha256(iso)==USA_SHA,"Authentic original required")
    target=candidate_path(candidate,iso)
    original,table=original_script_children(iso)
    plan=plan_builder()
    count=len(plan)
    require(count>0 and len({x["offset"] for x in plan})==count,"Invalid isolated plan")
    modified,guard=replace_original_script(original,table,plan)
    require(guard["text_commands_replaced"]==count and guard["all_command_offsets_preserved"],
            "Event guard failed")
    with tempfile.TemporaryDirectory(prefix="r30_isolated_",dir=target.parent) as tmp:
        root=Path(tmp)
        fontbase=root/"font.iso"
        build_font(iso,fontbase)
        fontguard=verify_font(iso,fontbase)
        require(fontguard["original_glyphs_identical"]==2721 and fontguard["new_glyphs"]==19,
                "Font guard failed")
        _,pack,records=read_resources(fontbase)
        entry=next(x for x in records if x["name"]=="SCRIPT.SDT")
        stored,decoded,codec=parent_content(pack,entry)
        require(codec.startswith("IMY"),"Unexpected codec")
        members=dsarc_entries(decoded)
        archive=replace_member_payload(decoded,members,"SCRIPT.DAT",modified)
        repacked=recompress(stored,archive)
        require(decompress(repacked,len(archive))[0]==archive,"Roundtrip failed")
        staged=root/"candidate.iso"
        append_text_containers(fontbase,pack,records,{"SCRIPT.SDT":(repacked,len(archive))},staged)
        _,final_pack,final_records=read_resources(staged)
        unchanged=verify_resources(records,pack,final_records,final_pack)
        new_entry=next(x for x in final_records if x["name"]=="SCRIPT.SDT")
        _,final_archive,_=parent_content(final_pack,new_entry)
        require(final_archive==archive and dsarc_entries(final_archive)==members,"Final script mismatch")
        require(file_sha256(iso)==USA_SHA,"Source changed")
        result={"isolated_original_not_F1":True,"script_texts_applied":count,
            "font_guard":fontguard,"event_guard":guard,"non_script_resources_exact_vs_fontbase":unchanged,
            "candidate_sha256":file_sha256(staged),"candidate_size":staged.stat().st_size,
            "ppsspp_run":False,"release_authorized":False,"new_official_integrations":0}
        os.link(staged,target)
    return result

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--iso-original",type=Path)
    p.add_argument("--candidate",type=Path)
    p.add_argument("--isolated-original",action="store_true",help="146 texts + 19 glyphs on USA, not F1")
    a=p.parse_args()
    result=run_isolated(a.iso_original,a.candidate) if a.isolated_original else run(a.iso_original,a.candidate)
    print(json.dumps(result,indent=2))

if __name__=="__main__":
    main()
