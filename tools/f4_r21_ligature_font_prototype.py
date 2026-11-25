#!/usr/bin/env python3
"""R21 protected in-memory 19+44 font prototype; DOES NOT write private/commercial assets."""
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path
try:
 from tools.f4_r21_ligature_capacity import read_canonical,WIDTHS
 from tools.f4_r21_ligature_collision_safe import analyze_collision_free
 from tools.f4_r21_ligature_raster_probe import combine_two_cells
except ModuleNotFoundError:
 from f4_r21_ligature_capacity import read_canonical,WIDTHS
 from f4_r21_ligature_collision_safe import analyze_collision_free
 from f4_r21_ligature_raster_probe import combine_two_cells

FIRST_NEW=0xB4
N_BASE=2721
N_ACCENTS=19
N_LIGATURES=44
TOTAL=N_BASE+N_ACCENTS+N_LIGATURES
INSERT=95+N_ACCENTS

def create_records(existing:bytes,pairs:list[str])->bytes:
 n=struct.unpack_from("<I",existing)[0]
 if n!=N_BASE+N_ACCENTS or len(existing)!=4+4*n:
  raise ValueError("Only narrow 19-glyph font may be extended")
 codes=[struct.unpack_from("<H",existing,4+4*i)[0] for i in range(n)]
 if (codes[:95]!=list(range(32,127))
     or codes[95:INSERT]!=list(range(0xA1,0xB4))
     or codes[INSERT]<0x8140 or codes!=sorted(set(codes))):
  raise ValueError("Unexpected original/new font code ordering")
 if not 0<=len(pairs)<=N_LIGATURES or len(set(pairs))!=len(pairs):
  raise ValueError("Expected 0..44 distinct ligatures")
 recs=[existing[4+4*i:4+4*(i+1)] for i in range(n)]
 extra=[]
 for i,pair in enumerate(pairs):
  if len(pair)!=2 or pair[0] not in WIDTHS or pair[1] not in WIDTHS:
   raise ValueError("Invalid pair")
  advance=WIDTHS[pair[0]]+WIDTHS[pair[1]]
  if advance>15:raise ValueError("Pair beyond 16-pixel atlas slot")
  extra.append(struct.pack("<HBB",FIRST_NEW+i,0,advance))
 result=struct.pack("<I",N_BASE+N_ACCENTS+len(pairs))+b"".join(recs[:INSERT]+extra+recs[INSERT:])
 output_codes=[struct.unpack_from("<H",result,4+4*i)[0] for i in range(N_BASE+N_ACCENTS+len(pairs))]
 if output_codes!=sorted(set(output_codes)):
  raise ValueError("Font index no longer sorted")
 return result

def insert_raster_slots(old:list[bytes],pairs:list[str])->tuple[list[bytes],dict]:
 if len(old)!=3072 or any(len(x)!=256 for x in old):
  raise ValueError("Expect six pages of 512 16x16 glyph cells")
 new=[];most_right=0;pixels=0
 for pair in pairs:
  a,b=pair
  glyph,metrics=combine_two_cells(old[ord(a)-32],old[ord(b)-32],
                                   WIDTHS[a],WIDTHS[b])
  if not any(glyph):
   raise ValueError("Empty two-letter raster")
  new.append(glyph)
  most_right=max(most_right,metrics["max_used_x"])
  pixels+=metrics["ink_pixels"]
 result=old[:INSERT]+new+old[INSERT:N_BASE+N_ACCENTS]
 result+=[bytes(256)]*(3072-len(result))
 if len(result)!=3072:
  raise ValueError("Font atlas exceeds six pages")
 for i in range(N_BASE+N_ACCENTS):
  j=i+(len(pairs) if i>=INSERT else 0)
  if result[j]!=old[i]:
   raise ValueError("Historical glyph raster modified")
 return result,{"ligature_rasters":len(new),"max_used_x":most_right,
                 "new_raster_ink_pixels":pixels,
                 "preserved_existing_19_plus_2721_glyphs":N_BASE+N_ACCENTS}

def slot_safety(original_arc_bytes:int,generated_arc_bytes:int,free_bytes:int)->dict:
 if not all(isinstance(x,int) for x in (original_arc_bytes,generated_arc_bytes,free_bytes)):
  raise ValueError("Font slot geometry must be integer")
 if original_arc_bytes<=0 or generated_arc_bytes<=0 or free_bytes<0:
  raise ValueError("Unsafe font slot geometry")
 capacity=original_arc_bytes+free_bytes
 excess=max(0,generated_arc_bytes-capacity)
 return {"original_arc_bytes":original_arc_bytes,
         "generated_arc_bytes":generated_arc_bytes,
         "maximum_in_place_arc_bytes":capacity,
         "in_place_excess_bytes":excess,
         "can_write_in_place":excess==0,
         "append_only_relocation_needed":excess>0,
         "PPSSPP_verified":False}

def require_font_slot_safe(original_arc_bytes:int,generated_arc_bytes:int,free_bytes:int):
 verdict=slot_safety(original_arc_bytes,generated_arc_bytes,free_bytes)
 if not verdict["can_write_in_place"]:
  raise ValueError("BLOCKED: font expansion exceeds PSPFS slot by "
                   +str(verdict["in_place_excess_bytes"])+" bytes")
 return verdict

def compact_member_offset(end:int,alignment:int=512)->int:
 """Return DSARC child start (16-byte header bias), never a PSPFS offset.

 Alignment 16 is a *runtime-unverified experiment*. Historical members use
 512-byte alignment +16, so do not substitute this for a release build.
 """
 if type(end) is not int or end<0 or alignment not in (16,32,64,128,256,512):
  raise ValueError("Unsupported DSARC offset/alignment")
 return ((end+alignment-1)//alignment)*alignment+16


def build_in_memory(iso:Path,draft:Path,*,ligature_count:int=44,
                    member_alignment:int=512,include_binary:bool=False):
 try:
  from font_es_narrow import build_narrow_font_arc_from_iso,atlas_slots,encode_atlas
  from font_es_patch import archive,unswizzle,decode_imy_texture
  from extract_cladun import dsarc_entries
 except ModuleNotFoundError:
  from tools.font_es_narrow import build_narrow_font_arc_from_iso,atlas_slots,encode_atlas
  from tools.font_es_patch import archive,unswizzle,decode_imy_texture
  from tools.extract_cladun import dsarc_entries
 rows=read_canonical(draft)
 if not isinstance(ligature_count,int) or not 0<=ligature_count<=N_LIGATURES:
  raise ValueError("Ligature count must be 0..44")
 compact_member_offset(0,member_alignment)
 pairs=analyze_collision_free(rows)["pairs"][:ligature_count]
 original_meta=archive(iso)
 _,_,_,font_resource,old_arc,_=original_meta
 narrow,_=build_narrow_font_arc_from_iso(iso)
 kids=dsarc_entries(narrow)
 if [m["name"] for m in kids]!=["FONT.BIN"]+[f"FONT_{i:02d}.IMY" for i in range(6)]:
  raise ValueError("Wrong seven font members")
 b=kids[0]
 oldbin=narrow[b["offset"]:b["offset"]+b["size"]]
 newbin=create_records(oldbin,pairs)
 imys=[narrow[m["offset"]:m["offset"]+m["size"]] for m in kids[1:]]
 slots=atlas_slots([unswizzle(decode_imy_texture(data)) for data in imys])
 newslots,metric=insert_raster_slots(slots,pairs)
 textures=encode_atlas(newslots,imys)
 header=bytearray(narrow[:b["offset"]]);out=bytearray(header)
 table_start=(16+len(kids)*2+3)//4*4
 for i,content in enumerate([newbin]+textures):
  offset=b["offset"] if i==0 else compact_member_offset(len(out),member_alignment)
  if len(out)<offset:out.extend(bytes(offset-len(out)))
  out.extend(content)
  struct.pack_into("<II",out,table_start+i*48+40,len(content),offset)
 if len(out)%16:out.extend(bytes(16-len(out)%16))
 again=dsarc_entries(out)
 if len(again)!=7 or [x["name"] for x in again]!=[x["name"] for x in kids]:
  raise ValueError("Font archive table damaged")
 check=atlas_slots([unswizzle(decode_imy_texture(
        out[m["offset"]:m["offset"]+m["size"]])) for m in again[1:]])
 if check!=newslots:raise ValueError("IMY recompression altered at least one glyph")
 # The original FONT.ARC has only 496 bytes before the next PSPFS resource:
 # never write a result into that slot without independent relocation guards.
 free_old=min(x["offset"] for x in original_meta[2] if x["offset"]>font_resource["offset"])-(font_resource["offset"]+font_resource["size_stored"])
 safety=slot_safety(len(old_arc),len(out),free_old)
 result={"schema":"cladun.r23.font_63_glyphs_compact_experiment.v1",
   "evidence":"A_ORIGINAL_ISO_OFFLINE_NOT_PPSSPP",
   "new_font_arc_sha256_private_only":hashlib.sha256(out).hexdigest(),
   "base_font_arc_bytes":len(old_arc),
   "narrow_19_arc_bytes":len(narrow),"experimental_63_arc_bytes":len(out),
   "font_original_slot_margin":free_old,
   "ligature_count":len(pairs),
   "member_alignment_bytes_experimental":member_alignment,
   "member_offsets": [m["offset"] for m in again],
   "historical_512_plus_16_alignment_preserved":member_alignment==512,
   "remaining_slot_bytes_after_repack":len(old_arc)+free_old-len(out),
   "can_write_in_original_slot_without_relocation":safety["can_write_in_place"],
   "shortfall_in_original_slot_bytes":safety["in_place_excess_bytes"],
   "append_only_relocation_needed":safety["append_only_relocation_needed"],
   "preserved_original_base_glyphs":N_BASE,
   "preserved_existing_spanish_glyphs":N_ACCENTS,
   **metric,
   "iso_written":False,"font_arc_exported":False,
   "ppsspp_render_verified":False,"safe_deployment_authorized":False}
 if include_binary:
  return bytes(out),result
 return result

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--iso-original",type=Path,required=True)
 p.add_argument("--borrador",type=Path,default=Path("traduccion/CLADUN_BORRADOR_ES.csv"))
 p.add_argument("--ligatures",type=int,choices=range(45),default=44,
                help="Use first N collision-free pairs; 4 is in-slot candidate")
 p.add_argument("--member-alignment",type=int,choices=(16,32,64,128,256,512),default=512,
                help="EXPERIMENTAL: 16-byte DSARC packing is not PPSSPP-approved")
 p.add_argument("--require-in-place",action="store_true",
                help="Fail rather than silently requiring PSPFS relocation")
 a=p.parse_args()
 result=build_in_memory(a.iso_original,a.borrador,ligature_count=a.ligatures,
                        member_alignment=a.member_alignment)
 print(json.dumps(result,ensure_ascii=False,indent=2))
 if a.require_in_place and not result["can_write_in_original_slot_without_relocation"]:
  raise SystemExit("BLOCKED: generated FONT.ARC exceeds original PSPFS slot")
if __name__=="__main__":main()
