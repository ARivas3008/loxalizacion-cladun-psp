#!/usr/bin/env python3
"""R25: private authentic-ISO experiment for 7,024 / 8,248 substitutions.

This is *not* a release. Preserve all SCRIPT.DAT opcode and SCRIPT.TBL offsets:
- 3,724 already-available historical baseline substitutions
- 2,002 strict 44-ligature growing text replacements
- 1,298 conservative shorter texts padded with 1..7 ASCII spaces at the end
  (padding is visually unproven, not editorially approved).
The last 3,300 are experimental; do not increase official progress metrics.
FONT.ARC 44 compact 16+16 DSARC alignment is not PSP runtime-proven.
The private candidate is written only to a new absolute off-repository path.
No commercial game assets, source text, or payload are printed/published.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

try:
 from tools.charset_es import encode_spanish,decode_spanish
 from tools.f4_r21_ligature_capacity import read_canonical
 from tools.f4_r21_ligature_overlay import make_plan
 from tools.f4_r21_ligature_font_prototype import build_in_memory
 from tools.f4_r23_font_compact_candidate import candidate_path
 from tools.f4_r24_piloto_1650_ligaduras import (
    BASE_INTEGRATED,BASE_DEFERRED,TOTAL_PLANNED,USA_SHA,file_sha256,
    original_script_children,replace_original_script,
    update_font_in_existing_candidate,replace_member_payload,
    validate_final,require)
 from tools.integrar_parche_seguro import build,read_resources,parent_content,append_text_containers
 from tools.extract_cladun import dsarc_entries,decompress
 from tools.imy_repack_safe import recompress
except ModuleNotFoundError:
 from charset_es import encode_spanish,decode_spanish
 from f4_r21_ligature_capacity import read_canonical
 from f4_r21_ligature_overlay import make_plan
 from f4_r21_ligature_font_prototype import build_in_memory
 from f4_r23_font_compact_candidate import candidate_path
 from f4_r24_piloto_1650_ligaduras import (
    BASE_INTEGRATED,BASE_DEFERRED,TOTAL_PLANNED,USA_SHA,file_sha256,
    original_script_children,replace_original_script,
    update_font_in_existing_candidate,replace_member_payload,
    validate_final,require)
 from integrar_parche_seguro import build,read_resources,parent_content,append_text_containers
 from extract_cladun import dsarc_entries,decompress
 from imy_repack_safe import recompress

TARGET_NEW=3300
GROWING_44=2002
SHORTENED_PADDED=1298
MAX_PAD=7
TARGET_COMBINED=BASE_INTEGRATED+TARGET_NEW
EXPECTED_SHORT_SAFE=1622
SCRIPT_PATH="SCRIPT.SDT/SCRIPT.DAT"

def pad_shorter(row:dict,max_pad:int=MAX_PAD)->dict|None:
 """Byte-exact-width proposal, NOT a claim of identical rendered layout."""
 if row.get("origen")!=SCRIPT_PATH or not row.get("espanol"):
  return None
 try:
  old=bytes.fromhex(row["bytes_hex"])
  text=row["espanol"]
  raw=encode_spanish(text)
  if decode_spanish(raw)!=text:return None
 except (ValueError,UnicodeError,KeyError):
  return None
 if (not old or len(raw)>=len(old) or not text.isprintable()
     or text.endswith(" ") or "%" in text or "\\" in text
     or any(b<32 or b>126 or b in (37,92) for b in old)):
  return None
 gap=len(old)-len(raw)
 if not 1<=gap<=max_pad:return None
 new=raw+b" "*gap
 if (len(new)!=len(old) or
     not decode_spanish(new).endswith(" "*gap) or
     decode_spanish(new)[:-gap]!=text or
     new==old):
  return None
 return {"offset":int(row["offset_hex"],16),"group_id":row["grupo_id"],
         "old":old,"new":new,"bytes":len(old),"padding":gap,
         "method":"TRAILING_ASCII_SPACES_VISUALLY_UNVERIFIED"}

def choose_3300(rows:list[dict])->tuple[list[dict],dict]:
 grow,info=make_plan(rows,ligature_count=44)
 require(len(grow)==GROWING_44 and info["selected_ligatures"]==44,
         "Canonical growing ligature pool unexpectedly changed")
 short=[]
 for r in rows:
  proposal=pad_shorter(r)
  if proposal is not None:short.append(proposal)
 # Minimize trailing layout risk: first smallest pad, then source offset.
 short.sort(key=lambda r:(r["padding"],r["offset"],r["group_id"]))
 require(len(short)>=SHORTENED_PADDED and len(short)<=EXPECTED_SHORT_SAFE,
         "Safe shortening pool below target or unexpected drift")
 cut=short[:SHORTENED_PADDED]
 require(max(x["padding"] for x in cut)<=MAX_PAD,
         "More than seven trailing spaces would be needed")
 combined=[{**x,"method":"44_LIGATURES_RUNTIME_UNVERIFIED","padding":0}
           for x in grow]+cut
 combined.sort(key=lambda x:(x["offset"],x["group_id"]))
 ids=[x["group_id"] for x in combined]
 offsets=[x["offset"] for x in combined]
 require(len(ids)==TARGET_NEW and len(set(ids))==TARGET_NEW
         and len(set(offsets))==TARGET_NEW,"Candidate IDs/offsets collide")
 for a,b in zip(combined,combined[1:]):
  require(a["offset"]+a["bytes"]<=b["offset"],
          "Script text spans overlap")
 for item in combined:
  require(len(item["new"])==len(item["old"])==item["bytes"],
          "SCRIPT.DAT event offsets would move")
 stat={
  "schema":"cladun.r25.85pct_experimental_plan.v1",
  "evidence":"B_CANONICAL_AND_CODEC_ONLY_NO_GAMEPLAY",
  "current_official_integrated":BASE_INTEGRATED,
  "current_official_deferred":BASE_DEFERRED,
  "total_integrable_substitutions":TOTAL_PLANNED,
  "strict_ligatures_44_pool":len(grow),
  "shorter_safe_pool_with_gap_le_7":len(short),
  "selected_growing_new":GROWING_44,
  "selected_shorter_new":len(cut),
  "selected_new_total":len(combined),
  "maximum_trailing_ascii_spaces":max(x["padding"] for x in cut),
  "total_trailing_ascii_space_bytes":sum(x["padding"] for x in cut),
  "target_cumulative_binary_candidates":TARGET_COMBINED,
  "target_cumulative_percent":round(100*TARGET_COMBINED/TOTAL_PLANNED,4),
  "target_gain_over_R24_pilot_points":round(100*(TARGET_COMBINED-5374)/TOTAL_PLANNED,4),
  "target_gain_over_current_official_points":round(100*TARGET_NEW/TOTAL_PLANNED,4),
  "remaining_after_only_if_all_proven":TOTAL_PLANNED-TARGET_COMBINED,
  "new_official_integrations":0,
  "release_authorized":False,
  "font_runtime_approved":False,
  "trailing_whitespace_visual_approved":False,
  "gameplay_C_approved":False,
  "selected_group_manifest_sha256":hashlib.sha256(
      ",".join(ids).encode("ascii")).hexdigest(),
  "selected_source_text_bytes":sum(x["bytes"] for x in combined),
  "trailing_pad_only_in_experimental_pilot":True,
 }
 return combined,stat

def run(iso:Path|None,draft:Path,candidate:Path|None=None)->dict:
 proposals,report=choose_3300(read_canonical(draft))
 if candidate is None:
  require(iso is None,"Source ISO requires explicit private candidate path")
  report["ISO_written"]=False
  return report
 require(iso is not None,"Authentic private source ISO required")
 iso=Path(iso)
 if iso.is_symlink() or not iso.is_file() or file_sha256(iso)!=USA_SHA:
  raise ValueError("Authentic USA ISO hash is mandatory")
 candidate=candidate_path(Path(candidate),iso)
 original_script,original_table=original_script_children(iso)
 # Authenticate original preimages and full 51,705-opcode geometry before
 # constructing the baseline. No assumptions about any dynamic MIPS pointer.
 _,source_audit=replace_original_script(original_script,original_table,proposals)
 report["original_source_replay"]={
  "commands":source_audit["total_commands"],
  "nontext_exact":source_audit["nontext_commands_byte_exact"],
  "edited_text_commands":source_audit["text_commands_replaced"],
  "moved_offsets":source_audit["moved_command_offsets"],
  "moved_script_starts":source_audit["moved_script_starts"],
  "runtime_proven":False,
 }
 font_arc,font_m=build_in_memory(
    iso,draft,ligature_count=44,member_alignment=16,include_binary=True)
 require(len(font_arc)==144000 and font_m["ligature_count"]==44,
         "R23 compact font geometry drift")
 with tempfile.TemporaryDirectory(prefix="cladun_r25_private_",dir=candidate.parent) as tmp:
  root=Path(tmp)
  baseline=root/"baseline_3724.iso"
  baseline_result=build(iso,baseline,root/"baseline.json",
                        experimental_partial=True,event_safe_only=True)
  require(baseline_result.get("texto_aplicado")==BASE_INTEGRATED
          and baseline_result.get("dialogos_pospuestos_por_desplazamiento")==BASE_DEFERRED
          and baseline_result["auditoria_eventos"]["all_command_offsets_preserved"],
          "Canonical 3,724 baseline cannot be proven; abort pilot")
  intermediate=root/"font_19plus44.iso"
  report["font_stage"]=update_font_in_existing_candidate(
      iso,baseline,intermediate,font_arc)
  _,package,records=read_resources(intermediate)
  entry=next(x for x in records if x["name"]=="SCRIPT.SDT")
  stored,decoded,codec=parent_content(package,entry)
  require(codec.startswith("IMY"),"Unsupported script codec")
  members=dsarc_entries(decoded)
  require({x["name"] for x in members}==
          {"AISCRIPT.DAT","AISCRIPT.TBL","SCRIPT.DAT","SCRIPT.TBL"},
          "SCRIPT children changed")
  script=next(x for x in members if x["name"]=="SCRIPT.DAT")
  tbl=next(x for x in members if x["name"]=="SCRIPT.TBL")
  script_base=decoded[script["offset"]:script["offset"]+script["size"]]
  table_base=decoded[tbl["offset"]:tbl["offset"]+tbl["size"]]
  require(table_base==original_table,"Baseline SCRIPT.TBL changed")
  mod,audit=replace_original_script(script_base,table_base,proposals)
  require(audit["text_commands_replaced"]==TARGET_NEW
          and audit["all_command_offsets_preserved"],
          "Event layout or selected count drift")
  report["baseline_event_audit"]=audit
  combined_dsarc=replace_member_payload(decoded,members,"SCRIPT.DAT",mod)
  recompressed=recompress(stored,combined_dsarc)
  require(decompress(recompressed,len(combined_dsarc))[0]==combined_dsarc,
          "SCRIPT IMY roundtrip failed")
  report["script_stored_bytes"]=len(recompressed)
  staged=root/"candidate_7024.iso"
  append_info=append_text_containers(
      intermediate,package,records,
      {"SCRIPT.SDT":(recompressed,len(combined_dsarc))},staged)
  require(append_info["SCRIPT.SDT"]["offset_nuevo"]>=len(package),
          "Script not safely appended")
  report["authentic_private_binary_guard"]=validate_final(
      iso,baseline,staged,font_arc,mod,original_table)
  require(not candidate.exists(),"Private target already exists")
  os.link(staged,candidate)  # no-clobber, before tempdir removal
 report["ISO_written"]=True
 report["candidate_sha256_private"]=file_sha256(candidate)
 report["new_official_integrations"]=0
 report["gameplay_C_approved"]=False
 return report

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--borrador",type=Path,
                default=Path("traduccion/CLADUN_BORRADOR_ES.csv"))
 p.add_argument("--iso-original",type=Path)
 p.add_argument("--candidate",type=Path)
 args=p.parse_args()
 if (args.iso_original is None)!=(args.candidate is None):
  p.error("Private --iso-original and --candidate must be supplied together")
 result=run(args.iso_original,args.borrador,args.candidate)
 print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":
 main()
