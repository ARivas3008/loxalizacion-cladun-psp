#!/usr/bin/env python3
"""R26: rebuild ALL 4,900 changed SCRIPT commands in MEMORY from original ISO.

The original 46,308 nontext commands/IDs/order are verified exactly, but
variable text lengths move instruction offsets, so this DOES NOT demonstrate
that the PSP MIPS control-flow runtime can follow events.
No ISO, DSARC payload, commercial text or bin file is written or printed.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib,json
from pathlib import Path

try:
 from tools.f3_referencias_riesgo import USA_SHA,file_sha256,original_script_children
 from tools.integrar_parche_seguro import (
     source_rows,plan_rows,text_command_rebuild,TARGET_SCRIPT)
 from tools.script_event_guard import read_commands,audit_script_rebuild
except ModuleNotFoundError:
 from f3_referencias_riesgo import USA_SHA,file_sha256,original_script_children
 from integrar_parche_seguro import (
     source_rows,plan_rows,text_command_rebuild,TARGET_SCRIPT)
 from script_event_guard import read_commands,audit_script_rebuild

def require(ok,message):
 if not ok:raise ValueError(message)

def canonical_plan()->tuple[dict,dict]:
 rows=source_rows()
 changes,blocked,unchanged=plan_rows(rows)
 all_changed=sum(len(x) for x in changes.values())
 script=changes.get(TARGET_SCRIPT,[])
 require(all_changed==8248 and len(script)==4900
         and sum(len(old)!=len(new) for _,old,new in script)==4524,
         "Full script integration corpus drift")
 replacement={}
 for row,old,new in script:
  offset=int(row["offset_hex"],16)
  require(offset not in replacement,"Duplicate script source offset")
  replacement[offset]=(old,new,row["grupo_id"])
 return replacement,{
  "all_canonical_candidate_changes":all_changed,
  "SCRIPT_changed_texts":len(script),
  "SCRIPT_changed_length_texts":4524,
  "SCRIPT_changed_bytes_same_length_texts":376,
  "original_unchanged_SCRIPT_texts":307,
  "not_runtime_proven":True,
 }

def analyze_moving_offsets(original:bytes,table:bytes,new:bytes,newtable:bytes,
                           plan:dict)->dict:
 """Compare all real commands, recording old/new offset geometry only."""
 guard=audit_script_rebuild(original,table,new,newtable,plan,
                             require_fixed_offsets=False)
 require(guard["total_commands"]==51705 and
         guard["nontext_commands_byte_exact"]==46308 and
         guard["text_commands_replaced"]==4900 and
         guard["nontext_payload_changes"]==0 and
         guard["opcode_instruction_id_order_changes"]==0,
         "Event guard rejected complete script reconstruction")
 old,old_starts=read_commands(original,table)
 newer,new_starts=read_commands(new,newtable)
 moved=[(a,b) for a,b in zip(old,newer) if a.offset!=b.offset]
 nontext=sum(a.content is None for a,b in moved)
 require(len(moved)==guard["moved_command_offsets"]
         and nontext==guard["moved_nontext_command_offsets"],
         "Old/new offsets did not match independent event guard")
 if not moved or guard["all_command_offsets_preserved"]:
  raise ValueError("Variable-length reconstruction unexpectedly reports fixed offsets")
 moved_by_opcode=Counter(a.code for a,b in moved)
 return {
  "event_guard":guard,
  "source_script_bytes":len(original),
  "candidate_script_bytes":len(new),
  "SCRIPT_TBL_bytes":len(table),
  "script_block_starts_changed":sum(a!=b for a,b in
                                   zip(old_starts[:-1],new_starts[:-1])),
  "moved_commands":len(moved),
  "moved_nontext_commands":nontext,
  "moved_text_commands":len(moved)-nontext,
  "moved_opcode_counts":{f"0x{k:02X}":v for k,v in
                         sorted(moved_by_opcode.items())},
  "original_SCRIPT_DAT_sha256":hashlib.sha256(original).hexdigest(),
  "reflowed_private_MEMORY_ONLY_SHA256":hashlib.sha256(new).hexdigest(),
  "SCRIPT_TBL_changed_offsets_without_editing_other_fields":True,
  "PSP_MIPS_target_reference_fixups_proven":False,
  "PPSSPP_C_proven":False,
  "safe_release_candidate":False
 }

def audit(source_iso:Path|None=None)->dict:
 planned,meta=canonical_plan()
 result={"schema":"cladun.r26.full_script_offset_reflow_private.v1",
         "B_preflight":meta,
         "A_authenticated_original":source_iso is not None,
         "candidate_ISO_written":False,
         "commercial_text_or_bytes_exported":False,
         "official_new_integrations":0,
         "gameplay_C_pass":False}
 if source_iso is None:return result
 path=Path(source_iso)
 require(path.is_file() and not path.is_symlink() and
         file_sha256(path)==USA_SHA,"Only authenticated USA private ISO")
 script,table=original_script_children(path)
 rebuilt,new_table=text_command_rebuild(script,table,planned)
 measured=analyze_moving_offsets(script,table,rebuilt,new_table,planned)
 require(file_sha256(path)==USA_SHA,"Source modified while auditing")
 result["A_full_reflow_memory_only"]=measured
 result["source_original_unchanged"]=True
 return result

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--iso-original",type=Path)
 args=p.parse_args()
 print(json.dumps(audit(args.iso_original),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
