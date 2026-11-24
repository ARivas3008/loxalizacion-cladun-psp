#!/usr/bin/env python3
"""R23: isolated PRIVATE ISO pilot for compact 19+44 font, never a release patch.

The DSARC child IMY offsets change from historic 512+16 to 16+16 packing.
This is *not* validated against PSP runtime; use only with your own original
USA ISO and run PPSSPP A/B/A before any release.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import shutil
import struct
from pathlib import Path

try:
 from tools.f4_r21_ligature_font_prototype import build_in_memory
 from tools.font_es_patch import archive, ensure, sha256_file
 from tools.font_es_guard import same_file_except, outside_equal
 from tools.extract_cladun import iso9660_entries, read_iso_file, pspfs_entries, dsarc_entries
except ModuleNotFoundError:
 from f4_r21_ligature_font_prototype import build_in_memory
 from font_es_patch import archive, ensure, sha256_file
 from font_es_guard import same_file_except, outside_equal
 from extract_cladun import iso9660_entries, read_iso_file, pspfs_entries, dsarc_entries

SOURCE_SHA="b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f"
FONT_SHA="420613ae4a16595b00c75d17bfb86290e57a30419d81ddbc6f245035e63c9805"
FONT_NAMES=["FONT.BIN"]+[f"FONT_{i:02d}.IMY" for i in range(6)]


def candidate_path(candidate:Path,source:Path)->Path:
 """Fail closed: new PRIVATE file outside repositories, never overwrite input."""
 path=Path(candidate)
 if not path.is_absolute() or path.is_symlink() or path.exists():
  raise ValueError("Candidate must be a NEW absolute private path")
 target=path.resolve(strict=False)
 origin=Path(source).resolve(strict=True)
 repo=Path(__file__).resolve().parents[1]
 if (target==origin or target==repo or repo in target.parents or
     any((p/".git").exists() for p in target.parents)):
  raise ValueError("Do not write ISO to original or a repository")
 if not target.parent.exists():
  raise ValueError("Private candidate directory must already exist")
 return target


def audit_pspfs_isolation(original:bytes,candidate:bytes,arc:bytes)->dict:
 """Compare all 349 PSPFS records and every byte outside the font-only span."""
 ensure(len(original)==len(candidate),"DATA.DAT length changed")
 before=pspfs_entries(original)
 after=pspfs_entries(candidate)
 ensure(len(before)==len(after)==349,"Unexpected PSPFS inventory")
 ensure([x["name"] for x in before]==[x["name"] for x in after],
        "PSPFS files reordered")
 old=next(x for x in before if x["name"]=="FONT.ARC")
 new=next(x for x in after if x["name"]=="FONT.ARC")
 ensure(old["index"]==new["index"]==308,"FONT.ARC index changed")
 ensure((old["offset"],old["size_stored"])==(11776,143888),
        "Original FONT.ARC extent changed")
 ensure(old["size_expanded"]==new["size_expanded"]==0,
        "Unexpected FONT.ARC compression")
 ensure(new["offset"]==old["offset"] and new["size_stored"]==len(arc),
        "FONT.ARC table was not updated safely")
 next_offset=min(x["offset"] for x in before if x["offset"]>old["offset"])
 slot=next_offset-old["offset"]
 ensure(slot==144384 and len(arc)<=slot,"Font would overwrite SE.ARC")
 ensure(not any(original[old["offset"]+old["size_stored"]:next_offset]),
        "Font original slot margin is not empty")
 for x,y in zip(before,after):
  for key in ("name","index","offset","size_expanded"):
   ensure(x[key]==y[key],f"Unrelated PSPFS metadata modified: {x['name']}.{key}")
  if x["index"]==old["index"]:
   continue
  ensure(x["size_stored"]==y["size_stored"],
         "Unrelated member size changed: "+x["name"])
  o=x["offset"];n=x["size_stored"]
  ensure(original[o:o+n]==candidate[o:o+n],
         "Unrelated member bytes changed: "+x["name"])
 font_meta=16+old["index"]*32+24
 allowed_font_end=old["offset"]+max(old["size_stored"],len(arc))
 outside_equal(original,candidate,[
  (font_meta,font_meta+4),
  (old["offset"],allowed_font_end)
 ],"DATA.DAT")
 ensure(candidate[old["offset"]:old["offset"]+len(arc)]==arc,
        "FONT.ARC content mismatch")
 ensure(not any(candidate[old["offset"]+len(arc):next_offset]),
        "Nonzero obsolete FONT.ARC tail/padding")
 children=dsarc_entries(arc)
 ensure(len(children)==7 and [x["name"] for x in children]==FONT_NAMES,
        "FONT.ARC DSARC changed")
 ensure(all((x["offset"]-16)%16==0 for x in children[1:]),
        "IMY child offset is not 16-byte aligned")
 ensure(all(x["offset"]+x["size"]<=len(arc) for x in children),
        "IMY child out of bounds")
 fontbin=arc[children[0]["offset"]:children[0]["offset"]+children[0]["size"]]
 ensure(len(fontbin)==4+2784*4 and struct.unpack_from("<I",fontbin)[0]==2784,
        "44+19+2721 font records not present")
 codes=[struct.unpack_from("<H",fontbin,4+4*i)[0] for i in range(2784)]
 ensure(codes==sorted(set(codes)) and codes[95:95+63]==list(range(0xA1,0xE0)),
        "Spanish and ligature codebook not ordered")
 return {"source_pspfs":len(before),"other_resources_byte_exact":348,
         "font_stored_bytes":len(arc),"font_slot_bytes":slot,
         "slot_margin_bytes":slot-len(arc),
         "original_font_codes":2721,"spanish_codes":19,"ligature_codes":44,
         "isolation":"STATIC_BINARY_PASS_NOT_GAMEPLAY"}


def write_and_audit(source:Path,candidate:Path,arc:bytes)->dict:
 target=candidate_path(candidate,source)
 data,pack,entries,font,old_arc,kids=archive(source)
 ensure(hashlib.sha256(old_arc).hexdigest()==FONT_SHA,
        "Unexpected original font SHA")
 start=data["offset"]+font["offset"]
 ensure(len(arc)<=144384,"Compact font exceeds original PSPFS slot")
 try:
  shutil.copyfile(source,target)
  with target.open("r+b") as f:
   f.seek(start);f.write(arc)
   # When smaller than original, clear retired bytes of FONT.ARC only.
   if len(arc)<font["size_stored"]:
    f.write(bytes(font["size_stored"]-len(arc)))
   f.seek(data["offset"]+16+font["index"]*32+24)
   f.write(struct.pack("<I",len(arc)))
  original_iso,original_table=iso9660_entries(source)
  candidate_iso,candidate_table=iso9660_entries(target)
  ensure(original_table==candidate_table,"ISO9660 inventory modified")
  original_data=next(x for x in original_table if x["path"]=="PSP_GAME/USRDIR/DATA.DAT")
  other_data=next(x for x in candidate_table if x["path"]=="PSP_GAME/USRDIR/DATA.DAT")
  ensure(original_data==other_data,"ISO9660 DATA.DAT extent changed")
  same_file_except(source,target,original_data["offset"],
                   original_data["offset"]+original_data["size"])
  candidate_pack=read_iso_file(target,other_data)
  result=audit_pspfs_isolation(pack,candidate_pack,arc)
  ensure(target.stat().st_size==source.stat().st_size,
         "ISO size changed")
  result.update({"private_candidate_sha256":sha256_file(target),
                 "original_iso_sha256":SOURCE_SHA,
                 "iso9660_unchanged":True,
                 "iso_original_bytes":source.stat().st_size,
                 "ppsspp_tested":False,
                 "runtime_16byte_dsarc_alignment_supported":None,
                 "release_authorized":False})
  return result
 except BaseException:
  target.unlink(missing_ok=True)
  raise


def main():
 ap=argparse.ArgumentParser(description=__doc__)
 ap.add_argument("--iso-original",type=Path,required=True)
 ap.add_argument("--borrador",type=Path,default=Path("traduccion/CLADUN_BORRADOR_ES.csv"))
 ap.add_argument("--candidate",type=Path,
                 help="EXPERIMENTAL: write a new private ISO outside Git, never for distribution")
 args=ap.parse_args()
 iso=args.iso_original
 if iso.is_symlink() or not iso.is_file() or sha256_file(iso)!=SOURCE_SHA:
  raise ValueError("Requires authenticated original Cladun USA ISO")
 if args.candidate:
  candidate_path(args.candidate,iso)
 arc,plan=build_in_memory(iso,args.borrador,ligature_count=44,
                          member_alignment=16,include_binary=True)
 ensure(plan["ligature_count"]==44 and
        plan["preserved_original_base_glyphs"]==2721 and
        plan["preserved_existing_spanish_glyphs"]==19,
        "Source font preservation failed")
 ensure(plan["can_write_in_original_slot_without_relocation"],
        "Compact font is too large")
 ensure(len(arc)==144000 and plan["remaining_slot_bytes_after_repack"]==384,
        "Original baseline or 16-byte compact packing drifted")
 if args.candidate:
  report=write_and_audit(iso,args.candidate,arc)
 else:
  report={"status":"A_IN_MEMORY_ONLY","font_arc_bytes":len(arc),
          "slot_free_bytes":384,"ISO_written":False}
 report.update({"schema":"cladun.r23.compact_font_private_candidate.v1",
                "44_ligatures":True,
                "6_imy_roundtrip":True,
                "historical_512_byte_member_alignment_changed":True,
                "ppsspp_gameplay_C":False,
                "release_authorized":False})
 print(json.dumps(report,ensure_ascii=False,indent=2))


if __name__=="__main__":
 main()
