#!/usr/bin/env python3
"""R21 review-only ligature overlay; authentic ISO simulation is entirely in RAM."""
import argparse,hashlib,json
from pathlib import Path
try:
 from tools.f4_r21_ligature_capacity import read_canonical,analyze,encode_fixed
 from tools.f3_referencias_riesgo import original_script_children
 from tools.script_event_guard import read_commands,audit_script_rebuild
 from tools.charset_es import encode_spanish
except ModuleNotFoundError:
 from f4_r21_ligature_capacity import read_canonical,analyze,encode_fixed
 from f3_referencias_riesgo import original_script_children
 from script_event_guard import read_commands,audit_script_rebuild
 from charset_es import encode_spanish

def make_plan(rows):
 report=analyze(rows)
 pairs=report["pairs"]
 plan=[];filtered=0;attempted=0
 for row in rows:
  if row["origen"]!="SCRIPT.SDT/SCRIPT.DAT" or not row["espanol"]:
   continue
  old=bytes.fromhex(row["bytes_hex"])
  if len(encode_spanish(row["espanol"]))<=len(old):
   continue
  attempted+=1
  if (any(c<32 or c>126 or c in (37,92) for c in old)
      or "%" in row["espanol"] or "\\" in row["espanol"]
      or not row["espanol"].isprintable()):
   filtered+=1
   continue
  try:
   newer=encode_fixed(row["espanol"],len(old),pairs)
  except ValueError:
   continue
  if newer==old:continue
  off=int(row["offset_hex"],16)
  plan.append({"offset":off,"group_id":row["grupo_id"],
               "old":old,"new":newer,"bytes":len(old)})
 plan.sort(key=lambda z:z["offset"])
 if len({x["group_id"] for x in plan})!=len(plan) or len({x["offset"] for x in plan})!=len(plan):
  raise ValueError("Duplicate ligature overlay span")
 for left,right in zip(plan,plan[1:]):
  if left["offset"]+left["bytes"]>right["offset"]:
   raise ValueError("Ligature candidate spans overlap")
 return plan,{"schema":"cladun.r21.review_only_ligature_overlay.v1",
   "evidence":"B_STATIC_CORPUS_ONLY","growing_texts":attempted,
   "candidate_rows_with_controls_excluded":filtered,
   "candidates_after_strict_source_controls":len(plan),
   "candidate_payload_bytes":sum(x["bytes"] for x in plan),
   "candidate_codebook_hash":hashlib.sha256(",".join(pairs).encode("ascii")).hexdigest(),
   "font_patched":False,"canonical_approved":False,
   "runtime_proven":False,"deployment_authorized":False}

def simulate_authenticated(original_script,original_table,plan):
 before,_=read_commands(original_script,original_table)
 if len(before)!=51705 or sum(c.content is None for c in before)!=46308:
  raise ValueError("Unexpected original SCRIPT geometry")
 original_index={c.offset+7:c for c in before if c.content is not None}
 virtual=bytearray(original_script)
 expected={}
 changed=0
 for item in plan:
  at=item["offset"];old=item["old"];new=item["new"]
  command=original_index.get(at)
  if command is None or command.content!=old or original_script[at:at+len(old)]!=old:
   raise ValueError("Authenticated command preimage mismatch: "+item["group_id"])
  if at in expected:raise ValueError("Duplicate offset")
  virtual[at:at+len(old)]=new
  expected[at]=(old,new,item["group_id"])
  changed+=sum(a!=b for a,b in zip(old,new))
 audit=audit_script_rebuild(original_script,original_table,bytes(virtual),original_table,
                            expected,require_fixed_offsets=True)
 if audit["text_commands_replaced"]!=len(plan) or audit["nontext_commands_byte_exact"]!=46308:
  raise ValueError("Event audit did not prove fixed widths")
 return {"evidence":"A_AUTHENTIC_SCRIPT_MEMORY_ONLY_NOT_C",
   "original_script_sha256":hashlib.sha256(original_script).hexdigest(),
   "table_sha256":hashlib.sha256(original_table).hexdigest(),
   "virtual_script_sha256":hashlib.sha256(virtual).hexdigest(),
   "candidate_changes":len(plan),"changed_payload_bytes":changed,
   "commands_reparsed":audit["total_commands"],
   "nontext_commands_byte_exact":audit["nontext_commands_byte_exact"],
   "moved_command_offsets":audit["moved_command_offsets"],
   "moved_script_starts":audit["moved_script_starts"],
   "model_control_flow_MIPS_verified":False,"PPSSPP_verified":False,
   "ISO_created":False,"deployment_authorized":False}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--borrador",type=Path,default=Path("traduccion/CLADUN_BORRADOR_ES.csv"))
 p.add_argument("--iso-original",type=Path)
 a=p.parse_args()
 plan,report=make_plan(read_canonical(a.borrador))
 if a.iso_original:
  source,tbl=original_script_children(a.iso_original)
  report["original_iso_replay"]=simulate_authenticated(source,tbl,plan)
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
