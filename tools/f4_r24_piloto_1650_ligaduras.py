#!/usr/bin/env python3
"""R24 private, fail-closed joint 3,724+1,650 *EXPERIMENTAL* pilot.

Never a production patch. The base 3,724 historical in-place-safe strings are
built using the existing integrator; an additional 1,650 selected longer
Spanish strings are compressed with the 44-glyph dictionary without moving
SCRIPT.DAT instructions. SCRIPT.SDT is appended using the existing PSPFS
append-only writer, not overwritten into its too-small original slot.
44-glyph compact IMY/DSARC alignment is NOT PPSSPP-proven; hence none of the
1,650 counts may increase official integration/completion metrics until real
PPSSPP A/B/A and editorial acceptance.
No commercial bytes/texts/ISO are printed or written to Git.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
import shutil
import struct
import tempfile
from pathlib import Path

try:
 from tools.f4_r21_ligature_capacity import read_canonical
 from tools.f4_r21_ligature_overlay import make_plan,simulate_authenticated
 from tools.f4_r21_ligature_font_prototype import build_in_memory
 from tools.f4_r23_font_compact_candidate import candidate_path,audit_pspfs_isolation
 from tools.f3_referencias_riesgo import original_script_children,USA_SHA,file_sha256
 from tools.integrar_parche_seguro import (build,read_resources,parent_content,
                                           append_text_containers)
 from tools.extract_cladun import dsarc_entries,decompress,iso9660_entries,read_iso_file,pspfs_entries
 from tools.imy_repack_safe import recompress
 from tools.script_event_guard import read_commands,audit_script_rebuild
 from tools.font_es_guard import outside_equal,same_file_except
except ModuleNotFoundError:
 from f4_r21_ligature_capacity import read_canonical
 from f4_r21_ligature_overlay import make_plan,simulate_authenticated
 from f4_r21_ligature_font_prototype import build_in_memory
 from f4_r23_font_compact_candidate import candidate_path,audit_pspfs_isolation
 from f3_referencias_riesgo import original_script_children,USA_SHA,file_sha256
 from integrar_parche_seguro import build,read_resources,parent_content,append_text_containers
 from extract_cladun import dsarc_entries,decompress,iso9660_entries,read_iso_file,pspfs_entries
 from imy_repack_safe import recompress
 from script_event_guard import read_commands,audit_script_rebuild
 from font_es_guard import outside_equal,same_file_except

BASE_INTEGRATED=3724
BASE_DEFERRED=4524
TOTAL_PLANNED=8248
TARGET_EXTRA=1650
FONT_SLOT_BYTES=144384

def require(ok,reason):
 if not ok:raise ValueError(reason)

def selection(plan, limit=TARGET_EXTRA):
 """Only previously growing strict candidates, deterministically by offset."""
 require(type(limit) is int and 1<=limit<=len(plan),
         "Requested extra replacement count unavailable")
 subset=plan[:limit]
 for prev,nxt in zip(subset,subset[1:]):
  require(prev["offset"]+prev["bytes"]<=nxt["offset"],
          "Overlapping candidate text spans")
 return subset

def metrics(plan,selected):
 require(len(selected)==TARGET_EXTRA,"R24 plus-20 target must be exactly 1,650")
 require(len(plan)>=len(selected),"Insufficient fixed-width candidates")
 final=BASE_INTEGRATED+len(selected)
 require(final<=TOTAL_PLANNED,"Experimental candidate overcounts records")
 return {
  "schema":"cladun.r24.plus20_experimental.v1",
  "historical_accepted_count":BASE_INTEGRATED,
  "planned_total":TOTAL_PLANNED,
  "historical_deferred":BASE_DEFERRED,
  "selected_experimental_additions":len(selected),
  "fittable_44_strict_pool":len(plan),
  "candidate_baseline_plus_experiment_count":final,
  "candidate_binary_coverage_percent":round(100*final/TOTAL_PLANNED,4),
  "baseline_historical_percent":round(100*BASE_INTEGRATED/TOTAL_PLANNED,4),
  "pilot_gain_percentage_points":round(100*len(selected)/TOTAL_PLANNED,4),
  "new_official_integrations":0,
  "new_gameplay_verified":0,
  "not_canonical":True,
  "not_release_authorized":True,
  "not_PPSSPP_proven":True
 }

def replace_original_script(src:bytes,tbl:bytes,selected)->tuple[bytes,dict]:
 """Fixed-width edits only; source may be an existing event-safe candidate."""
 before,starts=read_commands(src,tbl)
 require(len(before)==51705 and sum(c.content is None for c in before)==46308,
         "SCRIPT baseline geometry drift")
 lookup={x.offset+7:x for x in before if x.content is not None}
 dest=bytearray(src);expected={}
 for item in selected:
  at=item["offset"];old=item["old"];new=item["new"]
  cmd=lookup.get(at)
  require(cmd is not None and cmd.content==old and len(old)==len(new),
          "Baseline/source preimage or length mismatch: "+item["group_id"])
  require(src[at:at+len(old)]==old,"Mismatch in original text span")
  require(at not in expected,"Duplicate replacement offset")
  dest[at:at+len(old)]=new
  expected[at]=(old,new,item["group_id"])
 audit=audit_script_rebuild(src,tbl,bytes(dest),tbl,expected,
                            require_fixed_offsets=True)
 require(audit["text_commands_replaced"]==len(selected)
         and audit["nontext_commands_byte_exact"]==46308
         and audit["moved_command_offsets"]==0
         and audit["moved_script_starts"]==0,
         "SCRIPT event guard violation")
 return bytes(dest),audit

def font_allowed_span(offset:int,old_size:int,new_size:int,next_offset:int)->tuple[int,int]:
 """Only font's old/new byte union, bounded strictly before the next PSPFS."""
 if not all(type(n) is int for n in (offset,old_size,new_size,next_offset)):
  raise ValueError("FONT slot parameters must be integers")
 if offset<0 or old_size<=0 or new_size<=0 or next_offset<=offset:
  raise ValueError("Unsafe FONT slot parameters")
 end=offset+max(old_size,new_size)
 require(end<=next_offset,"FONT allowed span overlaps an unrelated resource")
 return offset,end

def update_font_in_existing_candidate(original:Path,baseline:Path,
                                       output:Path,font_arc:bytes)->dict:
 """Replace only FONT.ARC + 4-byte PSPFS length, preserving all prior text edits."""
 data,pack,entries=read_resources(baseline)
 font=next(x for x in entries if x["name"]=="FONT.ARC")
 require(font["index"]==308 and font["offset"]==11776
         and font["size_expanded"]==0 and len(font_arc)<=FONT_SLOT_BYTES,
         "FONT PSPFS identity/slot drift")
 end=min(x["offset"] for x in entries if x["offset"]>font["offset"])
 require(end-font["offset"]==FONT_SLOT_BYTES,"Unexpected FONT slot")
 require(not any(pack[font["offset"]+font["size_stored"]:end]),
         "Baseline FONT slack is nonzero")
 require(output!=baseline and not output.exists(),"Unsafe font candidate path")
 shutil.copyfile(baseline,output)
 foff=data["offset"]+font["offset"]
 with output.open("r+b") as f:
  f.seek(foff)
  f.write(font_arc)
  if len(font_arc)<font["size_stored"]:
   f.write(bytes(font["size_stored"]-len(font_arc)))
  f.seek(data["offset"]+16+font["index"]*32+24)
  f.write(struct.pack("<I",len(font_arc)))
 _,modified,members=read_resources(output)
 for old,new in zip(entries,members):
  if old["name"]=="FONT.ARC":continue
  require(old==new,"Unauthorized PSPFS metadata change at font stage")
  st=old["offset"];n=old["size_stored"]
  require(pack[st:st+n]==modified[st:st+n],
          "Nonfont PSPFS content mutation")
 meta=16+font["index"]*32+24
 # The canonical 19-glyph baseline FONT.ARC occupies 144352 bytes,
 # while compact 19+44 occupies 144000. Clearing the retired 352-byte tail
 # changes bytes belonging to the OLD FONT.ARC, not an unrelated asset.
 # Authorize the full union of old/new FONT spans, never SE.ARC.
 allowed_lo,allowed_hi=font_allowed_span(
     font["offset"],font["size_stored"],len(font_arc),end)
 outside_equal(pack,modified,[(meta,meta+4),(allowed_lo,allowed_hi)],
               "FONT replacement in baseline DATA.DAT")
 require(not any(modified[font["offset"]+len(font_arc):end]),
         "Retired font tail or remaining PSPFS padding not zero")
 # Base already includes other approved text edits; strict comparison is
 # intentionally to BASE, not original.
 require(output.stat().st_size==baseline.stat().st_size,"Font stage shifted ISO")
 return {"slot_capacity":end-font["offset"],
         "new_font_bytes":len(font_arc),"unused_slot":end-font["offset"]-len(font_arc),
         "nonfont_pspfs_exact":348}

def replace_member_payload(unpacked:bytes,members:list[dict],name:str,
                           modified:bytes)->bytes:
 entry=next(x for x in members if x["name"]==name)
 require(len(modified)==entry["size"],"SCRIPT.DAT original length must stay fixed")
 out=bytearray(unpacked)
 out[entry["offset"]:entry["offset"]+entry["size"]]=modified
 require(len(out)==len(unpacked),"DSARC geometry changed")
 changed={entry["offset"],entry["size"]}
 for x in members:
  if x["name"]==name:continue
  at=x["offset"];size=x["size"]
  require(unpacked[at:at+size]==out[at:at+size],
          "Other SCRIPT.SDT DSARC child modified")
 require(dsarc_entries(out)==members,"SCRIPT.SDT child headers changed")
 return bytes(out)

def validate_final(source:Path,result:Path,font_arc:bytes,expected_script:bytes,
                   original_table:bytes)->dict:
 require(file_sha256(source)==USA_SHA,"Original ISO unexpectedly altered")
 _,a_data,a_entries=read_resources(source)
 _,b_data,b_entries=read_resources(result)
 require(len(a_entries)==len(b_entries)==349,"Final PSPFS inventory changed")
 allow={"FONT.ARC","SCRIPT.SDT"}
 for left,right in zip(a_entries,b_entries):
  require(left["name"]==right["name"] and left["index"]==right["index"],
          "Resource order changed")
  if left["name"] in allow:continue
  require(left==right,"Unrelated PSPFS metadata relocated")
  s=left["offset"];n=left["size_stored"]
  require(a_data[s:s+n]==b_data[s:s+n],
          "Nonfont and nonscript resource changed: "+left["name"])
 font=next(x for x in b_entries if x["name"]=="FONT.ARC")
 require(b_data[font["offset"]:font["offset"]+font["size_stored"]]==font_arc,
         "Final FONT differs from plan")
 script=next(x for x in b_entries if x["name"]=="SCRIPT.SDT")
 require(script["offset"]>=len(a_data) and script["size_expanded"]==930304,
         "SCRIPT.SDT was not appended")
 stored=b_data[script["offset"]:script["offset"]+script["size_stored"]]
 unpacked,method=decompress(stored,930304)
 require(method.startswith("IMY"),"SCRIPT compression format changed")
 members=dsarc_entries(unpacked)
 ch={x["name"]:unpacked[x["offset"]:x["offset"]+x["size"]] for x in members}
 require(ch["SCRIPT.DAT"]==expected_script and ch["SCRIPT.TBL"]==original_table,
         "SCRIPT.DAT/TBL differ from byte-preserving plan")
 before_files=iso9660_entries(source)[1]
 after_files=iso9660_entries(result)[1]
 require(len(before_files)==len(after_files),"ISO9660 inventory changed")
 for a,b in zip(before_files,after_files):
  require(a["path"]==b["path"] and a["offset"]==b["offset"],
          "ISO file offset/name changed")
  if a["path"]=="PSP_GAME/USRDIR/DATA.DAT":
   require(b["size"]>a["size"],"Append-only DATA.DAT did not grow")
  elif not a["directory"] and a["path"]!="PSP_GAME/USRDIR":
   require(a["size"]==b["size"],"Non-DATA ISO file size changed")
 return {
  "evidence":"A_AUTHENTIC_ISO_PRIVATE_STATIC_NO_PPSSPP",
  "pspfs_members":349,
  "nontext_resource_members_byte_exact":347,
  "source_iso_sha256":USA_SHA,
  "private_pilot_iso_sha256":file_sha256(result),
  "final_script_archive_stored_bytes":script["size_stored"],
  "script_archive_relocated_append_only":True,
  "final_font_bytes":len(font_arc),
  "script_uncompressed_bytes":len(expected_script),
  "script_table_byte_exact":True,
  "source_ISO_unmodified":True,
  "PPSSPP_verified":False,
  "release_authorized":False
 }

def run(source:Path,draft:Path,candidate:Path|None=None,
        *,limit:int=TARGET_EXTRA)->dict:
 rows=read_canonical(draft)
 all_plan,static=make_plan(rows,ligature_count=44)
 selected=selection(all_plan,limit)
 report=metrics(all_plan,selected)
 report["selected_text_bytes"]=sum(x["bytes"] for x in selected)
 report["selected_group_manifest_sha256"]=hashlib.sha256(
     ",".join(x["group_id"] for x in selected).encode("ascii")).hexdigest()
 report["experimental_44_codebook_sha256"]=static["candidate_codebook_hash"]
 report["experimental_only"]=True
 if candidate is None:return report
 if source.is_symlink() or not source.is_file() or file_sha256(source)!=USA_SHA:
  raise ValueError("Authentic original USA ISO mandatory")
 target=candidate_path(candidate,source)
 authentic_data,authentic_tbl=original_script_children(source)
 report["original_script_ram_simulation"]=simulate_authenticated(
     authentic_data,authentic_tbl,selected)
 font_arc,font_metrics=build_in_memory(
     source,draft,ligature_count=44,member_alignment=16,include_binary=True)
 require(len(font_arc)==144000 and font_metrics["ligature_count"]==44,
         "Experimental compact FONT slot and glyph count mismatch")
 with tempfile.TemporaryDirectory(prefix="cladun_r24_private_",dir=target.parent) as temporary:
  working=Path(temporary)
  baseline=working/"baseline.iso"
  baseline_report=working/"baseline_report.json"
  original_baseline=build(source,baseline,baseline_report,
                          experimental_partial=True,event_safe_only=True)
  require(original_baseline.get("texto_aplicado")==BASE_INTEGRATED
          and original_baseline.get("dialogos_pospuestos_por_desplazamiento")==BASE_DEFERRED
          and original_baseline["auditoria_eventos"]["all_command_offsets_preserved"],
          "Historical safe baseline has drifted: abort combined candidate")
  fontpilot=working/"with_font.iso"
  report["font_isolation"]=update_font_in_existing_candidate(
      source,baseline,fontpilot,font_arc)
  _,pack,entries=read_resources(fontpilot)
  script_entry=next(x for x in entries if x["name"]=="SCRIPT.SDT")
  stored,expanded,codec=parent_content(pack,script_entry)
  require(codec.startswith("IMY"),"Original script compression changed")
  members=dsarc_entries(expanded)
  names={x["name"] for x in members}
  require(names=={"AISCRIPT.DAT","AISCRIPT.TBL","SCRIPT.DAT","SCRIPT.TBL"},
          "SCRIPT children drift")
  by_name={x["name"]:x for x in members}
  script=by_name["SCRIPT.DAT"];table=by_name["SCRIPT.TBL"]
  old_script=expanded[script["offset"]:script["offset"]+script["size"]]
  old_table=expanded[table["offset"]:table["offset"]+table["size"]]
  require(old_table==authentic_tbl,"Baseline SCRIPT.TBL moved")
  modified,audit=replace_original_script(old_script,old_table,selected)
  report["source_to_pilot_script_guard"]=audit
  rebuilt=replace_member_payload(expanded,members,"SCRIPT.DAT",modified)
  packed=recompress(stored,rebuilt)
  require(decompress(packed,len(rebuilt))[0]==rebuilt,
          "SCRIPT compressor roundtrip failed")
  report["script_stored_old_bytes"]=len(stored)
  report["script_stored_new_bytes"]=len(packed)
  staged=working/"joint_pilot.iso"
  appended=append_text_containers(
      fontpilot,pack,entries,{"SCRIPT.SDT":(packed,len(rebuilt))},staged)
  require(appended["SCRIPT.SDT"]["offset_nuevo"]>=len(pack),
          "Joint PILOT did not append SCRIPT.SDT")
  report["authentic_private_pilot"]=validate_final(
      source,staged,font_arc,modified,authentic_tbl)
  require(not target.exists(),"Output candidate exists")
  os.link(staged,target)  # atomic no-clobber
 report["pilot_created"]=True
 report["runtime_tested"]=False
 report["new_official_integrations"]=0
 return report

def main()->None:
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--borrador",type=Path,
                default=Path("traduccion/CLADUN_BORRADOR_ES.csv"))
 p.add_argument("--iso-original",type=Path)
 p.add_argument("--candidate",type=Path)
 p.add_argument("--limit",type=int,default=TARGET_EXTRA)
 a=p.parse_args()
 if (a.iso_original is None)!=(a.candidate is None):
  p.error("--candidate and --iso-original must both be supplied for private A test")
 report=run(a.iso_original,a.borrador,a.candidate,limit=a.limit)
 print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=="__main__":
 main()
