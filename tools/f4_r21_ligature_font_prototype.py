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
 if len(pairs)!=N_LIGATURES or len(set(pairs))!=N_LIGATURES:
  raise ValueError("Exactly 44 distinct ligatures needed")
 recs=[existing[4+4*i:4+4*(i+1)] for i in range(n)]
 extra=[]
 for i,pair in enumerate(pairs):
  if len(pair)!=2 or pair[0] not in WIDTHS or pair[1] not in WIDTHS:
   raise ValueError("Invalid pair")
  advance=WIDTHS[pair[0]]+WIDTHS[pair[1]]
  if advance>15:raise ValueError("Pair beyond 16-pixel atlas slot")
  extra.append(struct.pack("<HBB",FIRST_NEW+i,0,advance))
 result=struct.pack("<I",TOTAL)+b"".join(recs[:INSERT]+extra+recs[INSERT:])
 output_codes=[struct.unpack_from("<H",result,4+4*i)[0] for i in range(TOTAL)]
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
  j=i+(N_LIGATURES if i>=INSERT else 0)
  if result[j]!=old[i]:
   raise ValueError("Historical glyph raster modified")
 return result,{"ligature_rasters":len(new),"max_used_x":most_right,
                 "new_raster_ink_pixels":pixels,
                 "preserved_existing_19_plus_2721_glyphs":N_BASE+N_ACCENTS}

def build_in_memory(iso:Path,draft:Path):
 try:
  from font_es_narrow import build_narrow_font_arc_from_iso,atlas_slots,encode_atlas
  from font_es_patch import archive,unswizzle,decode_imy_texture
  from extract_cladun import dsarc_entries
 except ModuleNotFoundError:
  from tools.font_es_narrow import build_narrow_font_arc_from_iso,atlas_slots,encode_atlas
  from tools.font_es_patch import archive,unswizzle,decode_imy_texture
  from tools.extract_cladun import dsarc_entries
 rows=read_canonical(draft)
 pairs=analyze_collision_free(rows)["pairs"]
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
  offset=b["offset"] if i==0 else (len(out)+511)//512*512+16
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
 return {"schema":"cladun.r21.font_63_glyphs_in_memory.v1",
   "evidence":"A_ORIGINAL_ISO_OFFLINE_NOT_PPSSPP",
   "new_font_arc_sha256_private_only":hashlib.sha256(out).hexdigest(),
   "base_font_arc_bytes":len(old_arc),
   "narrow_19_arc_bytes":len(narrow),"experimental_63_arc_bytes":len(out),
   "font_original_slot_margin":free_old,
   "can_write_in_original_slot_without_relocation":len(out)<=len(old_arc)+free_old,
   "preserved_original_base_glyphs":N_BASE,
   "preserved_existing_spanish_glyphs":N_ACCENTS,
   **metric,
   "iso_written":False,"font_arc_exported":False,
   "ppsspp_render_verified":False,"safe_deployment_authorized":False}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--iso-original",type=Path,required=True)
 p.add_argument("--borrador",type=Path,default=Path("traduccion/CLADUN_BORRADOR_ES.csv"))
 a=p.parse_args()
 print(json.dumps(build_in_memory(a.iso_original,a.borrador),ensure_ascii=False,indent=2))
if __name__=="__main__":main()
