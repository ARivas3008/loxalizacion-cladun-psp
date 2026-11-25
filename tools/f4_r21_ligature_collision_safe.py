#!/usr/bin/env python3
"""R21 A-derived no-overlap ligature dictionary; no font edits or ISO output."""
from __future__ import annotations
import argparse,csv,hashlib,json
from collections import Counter
from pathlib import Path
try:
 from tools.f4_r21_ligature_capacity import (read_canonical,WIDTHS,CAPACITY,allowed_pair,matching,encode_fixed)
 from tools.charset_es import encode_spanish
except ModuleNotFoundError:
 from f4_r21_ligature_capacity import read_canonical,WIDTHS,CAPACITY,allowed_pair,matching,encode_fixed
 from charset_es import encode_spanish

# 151 pairs found to share ink pixels under exact FONT_00.IMY raster coordinates.
# Reverify against authenticated original font before considering any deployment.
COLLIDING_PAIRS=frozenset("""ia ib ic id ie if ig ih ij ik im in io ip iq ir is it iu iv iw ix iy iz ja jb jc jd je jf jg jh jk jm jn jo jp jq jr js jt ju jv jw jx jy jz la lb lc ld le lf lg lh lj lk lm ln lo lp lq lr ls lt lu lv lw lx ly lz rb rc re rg rh rk rm rn ro rp rq rr rs rt ru rv rw rx ry sa sb sc sd se sg sh sj sk sm sn so sp sr ss su sv sw sx sy sz ua ub uc ud ue uf ug uh uk um un uo up uq ur us ut uu uv uw ux uy uz za zb zg zh zj zk zm zn zp zr zs zu zv zw zx zy zz""".split())
ORIGINAL_FONT00_SHA256="698bc5b398a16c3f2a4615527dac6a36dbae73666a7c45c3787bb00a728a8478"
ORIGINAL_FONTBIN_SHA256="1f1f5692fecb3b4a66c50f4b20191c1f2658a32ca1220902a5888ae9a11afb46"
VALID_METRIC_PAIRS=frozenset(a+b for a in WIDTHS for b in WIDTHS if allowed_pair(a+b))
assert len(VALID_METRIC_PAIRS)==672 and len(COLLIDING_PAIRS)==151
assert COLLIDING_PAIRS<=VALID_METRIC_PAIRS
COLLISION_FREE_PAIRS=VALID_METRIC_PAIRS-COLLIDING_PAIRS
assert len(COLLISION_FREE_PAIRS)==521

def analyze_collision_free(rows:list[dict],*,samples:int=0)->dict:
 script=[r for r in rows if r["origen"]=="SCRIPT.SDT/SCRIPT.DAT" and r["espanol"]]
 grows=[];shrinks=equals=0
 for row in script:
  delta=len(encode_spanish(row["espanol"]))-len(bytes.fromhex(row["bytes_hex"]))
  if delta>0:grows.append((row,delta))
  elif delta<0:shrinks+=1
  else:equals+=1
 freq=Counter(pair for row,_ in grows for pair in
              (row["espanol"][i:i+2] for i in range(len(row["espanol"])-1))
              if pair in COLLISION_FREE_PAIRS)
 pairs=[pair for pair,_ in sorted(freq.items(),key=lambda p:(-p[1],p[0]))[:CAPACITY]]
 if len(pairs)!=CAPACITY or not set(pairs)<=COLLISION_FREE_PAIRS:
  raise ValueError("No collision-free 44-pair codebook")
 fitted=strict=filtered=bytes_kept=residual=0
 sample=[]
 for row,delta in grows:
  max_saved=len(matching(row["espanol"],pairs))
  if max_saved<delta:
   residual+=delta-max_saved
   continue
  fitted+=1
  original=bytes.fromhex(row["bytes_hex"])
  if (any(c<32 or c>126 or c in (37,92) for c in original)
      or "%" in row["espanol"] or "\\" in row["espanol"]
      or not row["espanol"].isprintable()):
   filtered+=1
   continue
  encoded=encode_fixed(row["espanol"],len(original),pairs)
  if len(encoded)!=len(original):
   raise ValueError("Byte-count mismatch despite simulation")
  strict+=1
  bytes_kept+=len(original)
  if len(sample)<samples:
   sample.append({"group_id":row["grupo_id"],"old_bytes":len(original),
                  "saved_bytes":delta})
 if (len(script),equals,len(grows),shrinks,fitted,strict,filtered,bytes_kept)!=(5207,683,2883,1641,2042,2002,40,61723):
  raise ValueError("Canonical corpus/44 safe pairs changed; invalidate findings")
 return {"schema":"cladun.r21.collision_free_ligature_feasibility.v1",
         "evidence":"B_STATIC_WITH_A_VALIDATED_COLLISION_LIST_NOT_C",
         "font00_sha256_for_blacklist":ORIGINAL_FONT00_SHA256,
         "candidate_pairs_with_15px_budget":len(VALID_METRIC_PAIRS),
         "font_raster_colliding_pairs":len(COLLIDING_PAIRS),
         "collision_free_pairs":len(COLLISION_FREE_PAIRS),
         "pairs":pairs,
         "codebook_sha256":hashlib.sha256(",".join(pairs).encode("ascii")).hexdigest(),
         "growing":len(grows),"shrinking":shrinks,"equal_width":equals,
         "theoretically_fittable":fitted,"growing_not_fittable":len(grows)-fitted,
         "strict_candidates":strict,"strict_exclusions":filtered,
         "strict_candidate_payload_bytes":bytes_kept,
         "remaining_overflow_bytes":residual,"sample_metadata":sample,
         "font_archive_modified":False,"runtime_verified":False,
         "integrated_into_canonical":False,"deployment_authorized":False}

def verify_own_iso_raster(iso:Path)->dict:
 try:
  from font_es_patch import archive,unswizzle,decode_imy_texture
  from font_es_narrow import atlas_slots
  from f4_r21_ligature_raster_probe import combine_two_cells
 except ModuleNotFoundError:
  from tools.font_es_patch import archive,unswizzle,decode_imy_texture
  from tools.font_es_narrow import atlas_slots
  from tools.f4_r21_ligature_raster_probe import combine_two_cells
 _,_,_,_,arc,members=archive(iso)
 font=arc[members[0]["offset"]:members[0]["offset"]+members[0]["size"]]
 texture=arc[members[1]["offset"]:members[1]["offset"]+members[1]["size"]]
 if (hashlib.sha256(font).hexdigest()!=ORIGINAL_FONTBIN_SHA256
     or hashlib.sha256(texture).hexdigest()!=ORIGINAL_FONT00_SHA256):
  raise ValueError("Original FONT SHA mismatch")
 slots=atlas_slots([unswizzle(decode_imy_texture(texture))])
 detected=set()
 for pair in sorted(VALID_METRIC_PAIRS):
  a,b=pair
  try:
   combine_two_cells(slots[ord(a)-32],slots[ord(b)-32],WIDTHS[a],WIDTHS[b])
  except ValueError as exc:
   if "clipped" not in str(exc) and "overlap" not in str(exc):
    raise
   detected.add(pair)
 if detected!=COLLIDING_PAIRS:
  raise ValueError("Collision manifest drift; do not generate a font")
 return {"evidence":"A_ORIGINAL_ISO_FONT_RASTER_ONLY",
         "pairs_checked":len(VALID_METRIC_PAIRS),
         "collisions_confirmed":len(detected),
         "safe_composites_confirmed":len(VALID_METRIC_PAIRS)-len(detected),
         "original_font00_sha256":ORIGINAL_FONT00_SHA256,
         "raster_exported":False,"PPSSPP_verified":False}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--borrador",type=Path,default=Path("traduccion/CLADUN_BORRADOR_ES.csv"))
 p.add_argument("--iso-original",type=Path)
 a=p.parse_args()
 result=analyze_collision_free(read_canonical(a.borrador),samples=12)
 if a.iso_original:result["authentic_collision_verification"]=verify_own_iso_raster(a.iso_original)
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
