#!/usr/bin/env python3
"""R23 authenticated PSPFS type/graphics triage, METADATA ONLY; never extracts assets.

A graphic candidate is not an English-text graphic or an approved translated
asset. This only bounds the first PSPFS-level survey, not total game textures.
"""
from __future__ import annotations
import argparse,collections,hashlib,json
from pathlib import Path
try:
 from tools.f3_referencias_riesgo import USA_SHA,USA_SIZE,file_sha256
 from tools.extract_cladun import iso9660_entries,read_iso_file,pspfs_entries
except ModuleNotFoundError:
 from f3_referencias_riesgo import USA_SHA,USA_SIZE,file_sha256
 from extract_cladun import iso9660_entries,read_iso_file,pspfs_entries

EXPECTED_BY_EXTENSION={
 "DAT2":1,"DMD":187,"ARC":3,"MPB":37,"DAT":65,"TXT":1,
 "SPS":50,"SDT":1,"IDT":1,"LDT":3
}
GRAPHIC_ARC_NAMES={"FONT.ARC","SYSGRA.ARC"}
GRAPHIC_PRIMARY_EXTENSIONS={"MPB","IDT","LDT"}
OPTIONAL_GRAPHICS={"MPB","IDT","LDT","ARC"}

def extension(name:str)->str:
 if not isinstance(name,str) or "." not in name:
  raise ValueError("Unexpected PSPFS name")
 return name.rsplit(".",1)[1].upper()

def candidate(name:str)->bool:
 ext=extension(name)
 return ext in GRAPHIC_PRIMARY_EXTENSIONS or name in GRAPHIC_ARC_NAMES

def inventory_records(records:list[dict],*,verify_original:bool=True)->dict:
 if len(records)!=349:
  raise ValueError("Expected 349 PSPFS records")
 if [x["index"] for x in records]!=list(range(349)):
  raise ValueError("Index/reordering drift in PSPFS")
 names=[x["name"] for x in records]
 if len(set(names))!=349:
  raise ValueError("Duplicate PSPFS name")
 counts=collections.Counter(extension(x) for x in names)
 if verify_original and dict(counts)!=EXPECTED_BY_EXTENSION:
  raise ValueError("Source PSPFS extension inventory drift")
 if verify_original and (names[225]!="SYSGRA.ARC" or
     names[234]!="ANIME000.IDT" or names[235]!="ANIME001.LDT" or
     names[236]!="ANIME002.LDT" or names[308]!="FONT.ARC" or
     names[313]!="MAPTIP.LDT"):
  raise ValueError("Critical resource identity drift")
 potential=[{"index":x["index"],"name":x["name"],"stored_bytes":x["size_stored"]}
            for x in records if candidate(x["name"])]
 if verify_original and len(potential)!=43:
  raise ValueError("Expected 43 PSPFS graphic family candidates")
 return {
  "schema":"cladun.r23.pspfs_graphics_triage.v1",
  "evidence":"A_ORIGINAL_ISO_PSPFS_METADATA_ONLY_NOT_PPSSPP",
  "pspfs_members":349,
  "extension_counts":dict(sorted(counts.items())),
  "first_pass_graphic_family_candidates":len(potential),
  "candidate_members":potential,
  "excluded_7bit_maps_DMD_members":counts["DMD"],
  "audio_SPS_members":counts["SPS"],
  "other_nested_graphics_not_yet_enumerated":True,
  "english_text_bearing_graphics_identified":None,
  "graphics_full_inventory_complete":False,
  "ppsspp_visual_authorized":False,
  "graphics_edit_completion_percent":None,
  "graphic_candidates_are_not_total_graphics":True
 }

def inventory_original_iso(iso:Path)->dict:
 iso=Path(iso)
 if iso.is_symlink() or not iso.is_file() or iso.stat().st_size!=USA_SIZE:
  raise ValueError("Requires authenticated original USA ISO")
 if file_sha256(iso)!=USA_SHA:
  raise ValueError("Original ISO SHA-256 mismatch")
 _,files=iso9660_entries(iso)
 matches=[x for x in files if x["path"]=="PSP_GAME/USRDIR/DATA.DAT"]
 if len(matches)!=1 or matches[0]["directory"]:
  raise ValueError("DATA.DAT not unique")
 source=read_iso_file(iso,matches[0])
 records=pspfs_entries(source)
 result=inventory_records(records)
 result["source_iso_sha256"]=USA_SHA
 result["source_iso_bytes"]=USA_SIZE
 result["original_resources_modified"]=0
 result["commercial_asset_bytes_exported"]=False
 return result

def main()->None:
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--iso-original",type=Path,required=True)
 a=p.parse_args()
 print(json.dumps(inventory_original_iso(a.iso_original),ensure_ascii=False,indent=2))

if __name__=="__main__":
 main()
