#!/usr/bin/env python3
"""R26: prove 100%-text SCRIPT resize capacity against original PSP ISA geometry.

Proof levels:
B: canonic 9,237-row UTF-8 corpus with git-blob fingerprint; compute all
   5,207 nonempty SCRIPT fields' EXACT serialized CP932/19-es-code lengths.
A: authentic SHA-256 ISO, original SCRIPT.DAT/TBL with all 51,705 parsed
   commands, 1,625 starts and 14,621 original padding bytes. Match every
   translated script name/id to the original 32-byte table record.
C: *never claimed*. This capacity proof cannot identify hidden MIPS
   control-flow pointers, renderer behavior, font alignment or PPSSPP health.
No game texts, commercial resources, ISO, patches or dialogue are output.
"""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
import struct
from pathlib import Path

try:
 from tools.charset_es import encode_spanish
 from tools.f4_r21_ligature_capacity import read_canonical,matching
 from tools.f4_r21_ligature_collision_safe import analyze_collision_free
 from tools.f3_referencias_riesgo import original_script_children,USA_SHA,file_sha256
 from tools.script_event_guard import read_commands
except ModuleNotFoundError:
 from charset_es import encode_spanish
 from f4_r21_ligature_capacity import read_canonical,matching
 from f4_r21_ligature_collision_safe import analyze_collision_free
 from f3_referencias_riesgo import original_script_children,USA_SHA,file_sha256
 from script_event_guard import read_commands

SCRIPT="SCRIPT.SDT/SCRIPT.DAT"
BLOCKS=1625
COMMANDS=51705
NONTEXT=46308
TEXT_SLOTS=5397
TRACKED=5207
OFFICIAL_DONE=3724
TOTAL_CHANGES=8248

def require(ok,msg):
 if not ok:raise ValueError(msg)

def census(rows:list[dict])->tuple[dict,dict]:
 """Net target-original byte change by original (name,script-id)."""
 sums=defaultdict(int)
 hist=Counter()
 for r in rows:
  if r["origen"]!=SCRIPT:continue
  spanish=r["espanol"]
  require(bool(spanish),"Missing Spanish SCRIPT text: "+r["grupo_id"])
  original=bytes.fromhex(r["bytes_hex"])
  new=encode_spanish(spanish)
  require(original and new,"Empty translated or original script text")
  delta=len(new)-len(original)
  hist["growing" if delta>0 else "shrinking" if delta<0 else "equal"]+=1
  hist["positive_byte_delta"]+=max(0,delta)
  hist["negative_byte_delta"]+=max(0,-delta)
  require(r["script"] and r["script_id"].isdigit(),"Unknown script name or ID")
  sums[(r["script"],int(r["script_id"]))]+=delta
 require(sum(hist[k] for k in ("growing","shrinking","equal"))==TRACKED,
         "Unexpected number of SCRIPT texts")
 require((hist["growing"],hist["shrinking"],hist["equal"],
          hist["positive_byte_delta"],hist["negative_byte_delta"])==
         (2883,1641,683,17108,7414),
         "Canonical full script corpus drift")
 return dict(sums),dict(hist)

def optimized_44_census(rows:list[dict])->tuple[dict,dict]:
 """Hypothetical minimum net widths without changing the 44-code font.

 Only source-ASCII/no-control growing strings get ligatures. Non-fittable
 growing strings use EVERY available collision-free matching pair, leaving
 residual length changes; shortened strings have their NATURAL byte lengths
 (no visual trailing spaces). This is a *capacity LOWER BOUND*, NOT a
 generator for a valid 100% in-place patch.
 """
 result=analyze_collision_free(rows)
 pairs=result["pairs"]
 require(len(pairs)==44 and result["strict_candidates"]==2002,
         "Source font/codebook candidate set changed")
 sums=defaultdict(int)
 saved=0;unsafe=0;safe_unfit=0;safe_unfit_bytes=0
 for r in rows:
  if r["origen"]!=SCRIPT:continue
  original=bytes.fromhex(r["bytes_hex"])
  spanish=r["espanol"]
  new=encode_spanish(spanish)
  d=len(new)-len(original)
  if d>0:
   source_safe=(all(32<=c<=126 and c not in (37,92) for c in original)
                and "%" not in spanish and "\\" not in spanish
                and spanish.isprintable())
   if source_safe:
    compressible=len(matching(spanish,pairs))
    can_save=min(d,compressible)
    saved+=can_save
    d-=can_save
    if d>0:
     safe_unfit+=1;safe_unfit_bytes+=d
   else:
    unsafe+=1
  sums[(r["script"],int(r["script_id"]))]+=d
 require(len(sums)==586,"Original SCRIPT corpus key drift")
 require((saved,unsafe,safe_unfit,safe_unfit_bytes,sum(sums.values()))==
         (14076,74,807,2482,-4382),
         "Canonical 44-ligature lower bound drift")
 return dict(sums),{
  "capacity_mode":"44_COLLISION_FREE_PLUS_SHORTER_UNPADDED_THEORETICAL",
  "safe_ligature_savings_bytes":saved,
  "growing_rows_preserved_without_ligatures_due_controls":unsafe,
  "safe_growing_rows_still_resized_after_max_matches":safe_unfit,
  "safe_remaining_positive_text_byte_growth":safe_unfit_bytes,
  "full_script_theoretical_net_delta_bytes":sum(sums.values()),
  "source_script_commands_would_move_in_this_mode":True,
  "safe_to_deploy_or_claim_100pct":False,
  "font_DSARC_16byte_runtime_proven":False
 }

def block_costs(blocks:list[dict],script_net:dict)->dict:
 """Compute whether each original fixed-size block could contain full text.

 This is a necessary capacity condition only, NOT sufficient for safety:
 replacing variable-length text moves subsequent command offsets even when
 there is free padding. We DO NOT produce an executable relocation here.
 """
 require(len(blocks)==BLOCKS,"SCRIPT.TBL block count differs")
 seen=set()
 exceeded=[]
 total_padding=0
 positive_blocks=negative_blocks=zero_blocks=0
 positive_net=negative_net=0
 for block in blocks:
  key=(block["name"],block["script_id"])
  require(key not in seen,"Duplicated SCRIPT.TBL key")
  seen.add(key)
  slack=block["padding"]
  require(type(slack) is int and 0<=slack<=32,"Bad original script padding")
  delta=script_net.get(key,0)
  total_padding+=slack
  positive_blocks+=delta>0
  negative_blocks+=delta<0
  zero_blocks+=delta==0
  positive_net+=max(0,delta)
  negative_net+=min(0,delta)
  if delta>slack:
   exceeded.append({
    "block_index":block["index"],
    "script_id":block["script_id"],
    "script_file":block["name"],
    "original_padding_bytes":slack,
    "uncompressed_net_growth_bytes":delta,
    "missing_bytes_if_starts_fixed":delta-slack,
   })
 require(set(script_net)<=seen,"Corpus script IDs missing from original TBL")
 exceeded.sort(key=lambda x:(-x["missing_bytes_if_starts_fixed"],x["block_index"]))
 return {
  "source_script_blocks":len(blocks),
  "corpus_script_ids_matched":len(script_net),
  "original_all_blocks_padding_bytes":total_padding,
  "net_total_translated_script_growth_bytes":positive_net+negative_net,
  "blocks_with_positive_net_growth":positive_blocks,
  "blocks_with_negative_net_growth":negative_blocks,
  "blocks_with_zero_net_growth":zero_blocks,
  "positive_per_block_net_growth_bytes":positive_net,
  "negative_per_block_net_growth_bytes":negative_net,
  "blocks_exceeding_original_local_padding":len(exceeded),
  "minimum_extra_bytes_needed_across_overflow_blocks":sum(
      x["missing_bytes_if_starts_fixed"] for x in exceeded),
  "largest_single_block_overflow_bytes":(
      exceeded[0]["missing_bytes_if_starts_fixed"] if exceeded else 0),
  "top_overflow_scripts_metadata_only":exceeded[:20],
  "source_script_fixed_block_starts_full_english_to_spanish_feasible":not exceeded,
  "runtime_mips_event_reference_model_verified":False,
 }

def authentic_block_metadata(data:bytes,table:bytes)->tuple[list[dict],dict]:
 commands,starts=read_commands(data,table)
 require(len(commands)==COMMANDS
         and sum(c.content is None for c in commands)==NONTEXT
         and sum(c.content is not None for c in commands)==TEXT_SLOTS,
         "Source event command inventory drift")
 require(len(starts)==BLOCKS+1 and starts[-1]==len(data),
         "Original SCRIPT.TBL boundary drift")
 final=[starts[i] for i in range(BLOCKS)]
 for cmd in commands:final[cmd.block]=cmd.offset+len(cmd.raw)
 blocks=[]
 for i in range(BLOCKS):
  row=table[16+32*i:16+32*(i+1)]
  require(len(row)==32,"SCRIPT.TBL truncated")
  ident,start=struct.unpack_from("<II",row)
  raw_name=row[8:28].split(b"\0",1)[0]
  name=raw_name.decode("ascii","strict")
  require(start==starts[i],"SCRIPT.TBL indexed start mismatch")
  remaining=starts[i+1]-final[i]
  require(0<=remaining<=32,"Unexpected source padding bytes")
  require(not any(data[final[i]:starts[i+1]]),"Nonzero source padding")
  blocks.append({
   "index":i,"name":name,"script_id":ident,
   "padding":remaining
  })
 return blocks,{
  "source_bytes":len(data),
  "source_table_bytes":len(table),
  "script_blocks":len(blocks),
  "source_total_commands":len(commands),
  "source_nontext_commands":NONTEXT,
  "source_text_slots":TEXT_SLOTS,
 }

def audit(draft:Path,source_iso:Path|None=None)->dict:
 rows=read_canonical(draft)
 groups,counts=census(rows)
 optimistic,optimized_counts=optimized_44_census(rows)
 report={
  "schema":"cladun.r26.authentic_full_script_local_capacity.v1",
  "corpus_evidence":"B_CANONICAL_CSV_CP932",
  "source_original_status":"NOT_SUPPLIED" if source_iso is None else "A_AUTHENTIC",
  "translated_script_rows":TRACKED,
  "original_fixed_width_suitable_rows":counts["equal"],
  **counts,
  "net_text_growth_bytes":counts["positive_byte_delta"]-counts["negative_byte_delta"],
  "optimized_44_theoretical":optimized_counts,
  "historical_integrated_unchanged":OFFICIAL_DONE,
  "historical_total":TOTAL_CHANGES,
  "current_official_romhacking_percent":round(OFFICIAL_DONE/TOTAL_CHANGES*100,4),
  "100pct_reached":False,
  "authentic_script_rebuilt":False,
  "game_tested_ppsspp_C":False,
  "source_PSP_MIPS_event_pointers_verified":False,
  "publication_authorized":False,
 }
 if source_iso is not None:
  path=Path(source_iso)
  require(path.is_file() and not path.is_symlink()
          and file_sha256(path)==USA_SHA,"Authenticated private source ISO required")
  script,table=original_script_children(path)
  original,stats=authentic_block_metadata(script,table)
  capacity=block_costs(original,groups)
  optimized_capacity=block_costs(original,optimistic)
  require((
   optimized_capacity["source_script_blocks"],
   optimized_capacity["corpus_script_ids_matched"],
   optimized_capacity["original_all_blocks_padding_bytes"],
   optimized_capacity["net_total_translated_script_growth_bytes"],
   optimized_capacity["blocks_exceeding_original_local_padding"],
   optimized_capacity["minimum_extra_bytes_needed_across_overflow_blocks"],
   optimized_capacity["largest_single_block_overflow_bytes"]
   )==(1625,586,14621,-4382,29,215,34),
   "Optimized 44-pair A/B lower-bound cross-proof drift")
  require((
   capacity["source_script_blocks"],
   capacity["corpus_script_ids_matched"],
   capacity["original_all_blocks_padding_bytes"],
   capacity["net_total_translated_script_growth_bytes"],
   capacity["blocks_exceeding_original_local_padding"],
   capacity["minimum_extra_bytes_needed_across_overflow_blocks"],
   capacity["largest_single_block_overflow_bytes"]
   )==(1625,586,14621,9694,253,8077,1459),
   "R26 original/corpus A cross-proof changed; abort")
  report.update({
   "original_iso_sha256":USA_SHA,
   "authentic_A_readonly":True,
   "source_structure":stats,
   "local_script_capacity":capacity,
   "optimized_44_local_capacity":optimized_capacity,
   "source_iso_modified":False,
  })
 return report

def main()->None:
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--borrador",type=Path,
                default=Path("traduccion/CLADUN_BORRADOR_ES.csv"))
 p.add_argument("--iso-original",type=Path,
                help="Optional private USA ISO (SHA checked); no bytes exported")
 a=p.parse_args()
 print(json.dumps(audit(a.borrador,a.iso_original),
                  ensure_ascii=False,indent=2))

if __name__=="__main__":main()
