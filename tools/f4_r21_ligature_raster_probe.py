#!/usr/bin/env python3
"""R21 experimental ligature raster geometry probe. READ ONLY, never exports font."""
import argparse,hashlib,json,struct
from pathlib import Path
try:
 from tools.f4_r21_ligature_capacity import (read_canonical,select_pairs,WIDTHS)
except ModuleNotFoundError:
 from f4_r21_ligature_capacity import (read_canonical,select_pairs,WIDTHS)

def combine_two_cells(first:bytes,second:bytes,advance_first:int,advance_second:int)->tuple[bytes,dict]:
 if len(first)!=256 or len(second)!=256:
  raise ValueError("Raster must be 16x16x4bpp decoded pixels")
 if not (0<advance_first and 0<advance_second and advance_first+advance_second<=15):
  raise ValueError("Ligature advance exceeds 15 pixels")
 if any(v>15 for v in first+second):
  raise ValueError("Raster index is not a 4bpp value")
 out=bytearray(first);clipping=overlap=0;max_x=-1
 for y in range(16):
  for x in range(16):
   if first[y*16+x]:
    max_x=max(max_x,x)
 for y in range(16):
  for x in range(16):
   b=second[y*16+x]
   if not b:continue
   tx=x+advance_first
   if tx>=16:
    clipping+=1;continue
   max_x=max(max_x,tx)
   if out[y*16+tx]:
    overlap+=1
   else:
    out[y*16+tx]=b
 if clipping or overlap or max_x>=16:
  raise ValueError("Ligature clipped or original letter rasters overlap")
 return bytes(out),{"max_used_x":max_x,
                    "ink_pixels":sum(p>0 for p in out),
                    "composed_advance":advance_first+advance_second,
                    "clipped_pixels":clipping,
                    "overlap_pixels":overlap}

def original_raster_probe(iso:Path,pairs:list[str])->dict:
 try:
  from font_es_patch import archive,unswizzle,decode_imy_texture
  from font_es_narrow import atlas_slots
 except ModuleNotFoundError:
  from tools.font_es_patch import archive,unswizzle,decode_imy_texture
  from tools.font_es_narrow import atlas_slots
 _,_,_,_,arc,members=archive(iso)
 if [m["name"] for m in members]!=["FONT.BIN"]+[f"FONT_{i:02d}.IMY" for i in range(6)]:
  raise ValueError("Unexpected FONT.ARC member layout")
 b=arc[members[0]["offset"]:members[0]["offset"]+members[0]["size"]]
 count=struct.unpack_from("<I",b)[0]
 codes=[struct.unpack_from("<H",b,4+4*i)[0] for i in range(count)]
 if count!=2721 or codes[:95]!=list(range(32,127)):
  raise ValueError("Original ASCII font index changed")
 meta={chr(c):b[4+4*i+3] for i,c in enumerate(codes[:95])}
 for letter,width in WIDTHS.items():
  if meta[letter]!=width:raise ValueError("Wrong letter advance "+letter)
 raw=arc[members[1]["offset"]:members[1]["offset"]+members[1]["size"]]
 pixels=atlas_slots([unswizzle(decode_imy_texture(raw))])
 results=[]
 for pair in pairs:
  a,z=pair
  glyph,stats=combine_two_cells(pixels[ord(a)-32],pixels[ord(z)-32],meta[a],meta[z])
  if not any(glyph):raise ValueError("Empty composite "+pair)
  results.append({"pair":pair,**stats})
 return {"evidence":"A_ORIGINAL_FONT_RASTER_PRIVATE_NOT_C",
         "original_font_bin_sha256":hashlib.sha256(b).hexdigest(),
         "original_font00_imy_sha256":hashlib.sha256(raw).hexdigest(),
         "pairs_checked":len(results),
         "pairs_without_clipping_or_overlap":len(results),
         "max_pixel_x":max(x["max_used_x"] for x in results),
         "max_composite_advance":max(x["composed_advance"] for x in results),
         "original_glyph_rasters_modified":0,
         "new_font_archive_written":False,
         "visual_runtime_verified":False,
         "repacking_authorized":False}

def main():
 from f4_r21_ligature_capacity import analyze
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--iso-original",type=Path,required=True)
 p.add_argument("--borrador",type=Path,default=Path("traduccion/CLADUN_BORRADOR_ES.csv"))
 a=p.parse_args()
 rows=read_canonical(a.borrador)
 result=analyze(rows)
 print(json.dumps(original_raster_probe(a.iso_original,result["pairs"]),indent=2))

if __name__=="__main__":main()
