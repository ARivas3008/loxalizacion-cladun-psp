#!/usr/bin/env python3
"""R26 experimental FULL 8,248/8,248 byte-level insertion into user's own ISO.

WARNING: This pilot necessarily moves SCRIPT.DAT instruction offsets and
SCRIPT.TBL block starts. The independent event guard proves unchanged opcode
IDs/order and nontext payload bytes, NOT hidden PSP MIPS code references.
No evidence of PPSSPP runtime, maps, saves, graphics or release safety.
Do not publish/redistribute the private ISO, BPS, or proprietary game assets.
This tool never reports romhacking 100% *official*.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile

try:
 from tools.integrar_parche_seguro import (
     build,plan_rows,source_rows,TARGET_SCRIPT)
 from tools.f4_r23_font_compact_candidate import candidate_path
 from tools.f3_referencias_riesgo import USA_SHA,file_sha256
except ModuleNotFoundError:
 from integrar_parche_seguro import build,plan_rows,source_rows,TARGET_SCRIPT
 from f4_r23_font_compact_candidate import candidate_path
 from f3_referencias_riesgo import USA_SHA,file_sha256

FULL_TARGET=8248
SCRIPT_TARGET=4900
NON_SCRIPT_TARGET=3348
VARIABLE_SCRIPT_TARGET=4524
EQUAL_SCRIPT_TARGET=376
SCRIPT_ALL_TRANSLATED=5207
SCRIPT_IDENTICAL_OLD_NEW=307
SCRIPT_ALL_EQUAL_WIDTH=683

def require(ok,reason):
 if not ok:raise ValueError(reason)

def preview(original_csv:Path|None=None,draft_csv:Path|None=None)->dict:
 """B only: count the actual insertion planner's admissible replacements.

 This is NOT a plan that writes to original DATA.DAT or moves assets in CI.
 """
 kwargs={}
 if original_csv is not None:kwargs["source_csv"]=Path(original_csv)
 if draft_csv is not None:kwargs["draft_csv"]=Path(draft_csv)
 rows=source_rows(**kwargs)
 changes,blocked,unchanged=plan_rows(rows)
 n=sum(map(len,changes.values()))
 script=changes.get(TARGET_SCRIPT,[])
 variable=sum(len(old)!=len(new) for _,old,new in script)
 equal=len(script)-variable
 observed=(len(rows),n,len(script),n-len(script),variable,equal)
 expected=(9237,FULL_TARGET,SCRIPT_TARGET,NON_SCRIPT_TARGET,
           VARIABLE_SCRIPT_TARGET,EQUAL_SCRIPT_TARGET)
 require(observed==expected,
         f"8,248 fixed campaign baseline drift; observed={observed}, "
         f"expected={expected}; ABORT 100% pilot")
 # Every record is uniquely planned or retained; actual source validation
 # is in source_rows + plan_rows and eventual private build.
 ids=[row["grupo_id"] for changed in changes.values()
      for row,old,new in changed]
 require(len(set(ids))==FULL_TARGET,"Duplicate planned canonical IDs")
 require(EQUAL_SCRIPT_TARGET+SCRIPT_IDENTICAL_OLD_NEW==SCRIPT_ALL_EQUAL_WIDTH,
         "683 equal-width records must account for 307 byte-identical rows")
 require(SCRIPT_ALL_TRANSLATED-SCRIPT_IDENTICAL_OLD_NEW==SCRIPT_TARGET,
         "Original 5,207 visible texts include 307 already identical records")
 return {
  "schema":"cladun.r26.experimental_all_8248_text_insertions.v1",
  "evidence":"B_CORPUS_PLANNER_ONLY_NOT_ISO",
  "source_rows":len(rows),
  "planned_all_changed_canonical_records":n,
  "planned_SCRIPT_dat_changed_texts":len(script),
  "all_SCRIPT_dat_translated_rows":SCRIPT_ALL_TRANSLATED,
  "SCRIPT_dat_already_byte_identical_unmodified":SCRIPT_IDENTICAL_OLD_NEW,
  "planned_other_textual_records":n-len(script),
  "planned_SCRIPT_same_length_changed":equal,
  "all_SCRIPT_same_width_including_unchanged":SCRIPT_ALL_EQUAL_WIDTH,
  "planned_SCRIPT_changed_length":variable,
  "non_applied_or_nonchanged_source_rows":len(blocked)+unchanged,
  "deferred_untranslated_or_unsafe_records":len(blocked),
  "source_unchanged_bytes_records":unchanged,
  "all_script_event_offsets_would_be_preserved":False,
  "requires_MIPS_control_flow_reference_audit":True,
  "source_legal_iso_required_for_private_candidate":True,
  "official_integrated_records_unchanged":3724,
  "official_coverage_percent_unchanged":round(100*3724/FULL_TARGET,4),
  "private_candidate_created":False,
  "PPSSPP_1_20_4_C_verified":False,
  "commercial_payload_published":False,
  "release_authorized":False,
  "100_percent_ROMhacking_official":False
 }

def full_8248_metadata_manifest(
    original_csv:Path|None=None,draft_csv:Path|None=None)->list[dict]:
 """Enumerate ALL 8,248 byte-change IDs for QA, never copies source text.

 All rows remain editorially and visually UNVERIFIED. The 307 SCRIPT rows
 that already match English are omitted because they do not change bytes.
 """
 kwargs={}
 if original_csv is not None:kwargs["source_csv"]=Path(original_csv)
 if draft_csv is not None:kwargs["draft_csv"]=Path(draft_csv)
 changes,blocked,unchanged=plan_rows(source_rows(**kwargs))
 result=[]
 for location,items in changes.items():
  for source,old,new in items:
   affected_script=location==TARGET_SCRIPT
   category=("SCRIPT_VARIABLE" if affected_script and len(old)!=len(new)
             else "SCRIPT_FIXED" if affected_script else "OTHER_RESOURCE")
   result.append({
     "grupo_id":source["grupo_id"],
     "origen":location,
     "offset_hex":source["offset_hex"],
     "original_bytes":len(old),
     "new_bytes":len(new),
     "category":category,
     "binary_admission":"B_STATIC_PLANNER_ONLY",
     "editorial_review":"PENDIENTE_CONTEXTUAL",
     "PPSSPP_C":"NOT_RUN",
     "MIPS_references":"UNVERIFIED" if category=="SCRIPT_VARIABLE" else "NOT_APPLICABLE",
     "canonical_gameplay_integrated":"NO"
   })
 result.sort(key=lambda x:x["grupo_id"])
 counts={}
 for row in result:counts[row["category"]]=counts.get(row["category"],0)+1
 require(len(result)==8248 and len({x["grupo_id"] for x in result})==8248
         and (counts.get("SCRIPT_VARIABLE",0),
              counts.get("SCRIPT_FIXED",0),
              counts.get("OTHER_RESOURCE",0))==(4524,376,3348),
         "The full 8,248 manifest lost or duplicated records")
 return result

def write_private_review_manifest(path:Path,rows:list[dict])->dict:
 """Write metadata-only private JSON, never overwrite files."""
 path=Path(path)
 require(path.is_absolute() and not path.exists()
         and not path.is_symlink() and path.parent.is_dir(),
         "Manifest must be a NEW absolute file in an existing private directory")
 with path.open("x",encoding="utf-8") as f:
  json.dump({"schema":"cladun.r26.8248_metadata_review_only.v1",
             "commercial_dialogues_included":False,
             "runtime_certified":False,"rows":rows},
            f,ensure_ascii=False,indent=2)
  f.write("\n")
 return {"metadata_manifest_private_path":str(path),
         "metadata_manifest_count":len(rows),
         "gameplay_approved_count":0}

def private_candidate(
  original_iso:Path, candidate_iso:Path, *, explicit_risk_acceptance:bool,
  original_csv:Path|None=None,draft_csv:Path|None=None)->dict:
 """Full pilot, fail-closed, opt-in, new private pathname only.

 The preflight and source binary check precede any ISO copy. All later
 validation fails invalidate/remove the newly written private candidate.
 """
 require(explicit_risk_acceptance,
         "Changed instruction offsets demand explicit experimental risk flag")
 data=preview(original_csv,draft_csv)
 source=Path(original_iso)
 candidate=candidate_path(Path(candidate_iso),source)
 require(not source.is_symlink() and source.is_file()
         and file_sha256(source)==USA_SHA,
         "Only the user's authenticated original USA ISO is accepted")
 with tempfile.TemporaryDirectory(prefix="cladun_r26_full_private_",
                                  dir=candidate.parent) as tmp:
  report=Path(tmp)/"audit.json"
  kwargs={}
  if original_csv is not None:kwargs["source_csv"]=Path(original_csv)
  if draft_csv is not None:kwargs["draft_csv"]=Path(draft_csv)
  try:
   result=build(
      source,candidate,report,
      experimental_partial=True,add_spanish_font=True,
      event_safe_only=False,**kwargs)
   require(result["texto_aplicado"]==FULL_TARGET
           and result["cambios_admisibles_para_ensayo"]==FULL_TARGET,
           "Not all 8,248 canonical planned replacements applied")
   event=result["auditoria_eventos"]
   require(event is not None
           and event["total_commands"]==51705
           and event["nontext_commands_byte_exact"]==46308
           and event["text_commands_replaced"]==SCRIPT_TARGET
           and event["nontext_payload_changes"]==0
           and event["opcode_instruction_id_order_changes"]==0,
           "Nontext event logic or number of textual opcodes changed")
   require(event["moved_command_offsets"]>0
           and event["moved_script_starts"]>0,
           "Expected full resize to have MOVED offsets (do not misreport!)")
   require(not event["all_command_offsets_preserved"],
           "Full resize falsely declared fixed-offset")
   require(file_sha256(source)==USA_SHA,
           "Original ISO tampered during candidate construction")
   require(result["estado"]=="EXPERIMENTAL_AISLAMIENTO_BINARIO_SOLAMENTE"
           and not result["ppsspp_validado"]
           and not result["aprobado_para_distribucion"],
           "Incorrect runtime/approval flags in the integrator")
   data.update({
    "evidence":"A_AUTHENTIC_PRIVATE_ISO_STATIC_NOT_C",
    "private_candidate_created":True,
    "private_iso_sha256":result["iso_resultante_sha256"],
    "private_iso_bytes":candidate.stat().st_size,
    "records_applied_statically":result["texto_aplicado"],
    "event_commands":event["total_commands"],
    "nontext_commands_byte_exact":event["nontext_commands_byte_exact"],
    "text_commands_replaced":event["text_commands_replaced"],
    "MOVED_command_offsets":event["moved_command_offsets"],
    "MOVED_script_starts":event["moved_script_starts"],
    "all_command_offsets_were_preserved":False,
    "original_iso_unchanged":True,
    "risk_full_reference_fixups_not_proven":True,
    "runtime_PPSSPP_approved":False,
    "official_integrated_records_unchanged":3724,
    "100_percent_ROMhacking_official":False
   })
  except BaseException:
   candidate.unlink(missing_ok=True)
   raise
 return data

def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument("--original-csv",type=Path)
 ap.add_argument("--borrador",type=Path)
 ap.add_argument("--iso-original",type=Path)
 ap.add_argument("--candidate",type=Path)
 ap.add_argument("--manifest",type=Path,
                 help="new private JSON of exactly 8248 IDs and risk status, NO game texts")
 ap.add_argument("--i-accept-experimental-moving-event-offsets",
                 action="store_true")
 args=ap.parse_args()
 if (args.iso_original is None)!=(args.candidate is None):
  ap.error("--iso-original and --candidate must BOTH be supplied")
 if args.iso_original is None:
  data=preview(args.original_csv,args.borrador)
 else:
  data=private_candidate(
    args.iso_original,args.candidate,
    explicit_risk_acceptance=args.i_accept_experimental_moving_event_offsets,
    original_csv=args.original_csv,draft_csv=args.borrador)
 if args.manifest:
  meta=full_8248_metadata_manifest(args.original_csv,args.borrador)
  data.update(write_private_review_manifest(args.manifest,meta))
 print(json.dumps(data,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
