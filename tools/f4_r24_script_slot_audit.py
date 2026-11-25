#!/usr/bin/env python3
"""R24 authentic SCRIPT.SDT slot and compressor replay; READ ONLY.

Records whether even a no-op recompression fits the original compressed PSPFS
slot. No "safe in-place" claim without a verified result. The canonical pilot
uses append-only relocation with immutable event command offsets.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
try:
 from tools.f3_referencias_riesgo import USA_SHA,file_sha256
 from tools.extract_cladun import iso9660_entries,read_iso_file,pspfs_entries,dsarc_entries,decompress
 from tools.imy_repack_safe import recompress
 from tools.script_event_guard import read_commands
except ModuleNotFoundError:
 from f3_referencias_riesgo import USA_SHA,file_sha256
 from extract_cladun import iso9660_entries,read_iso_file,pspfs_entries,dsarc_entries,decompress
 from imy_repack_safe import recompress
 from script_event_guard import read_commands

def slot_safety(stored:int,next_start:int,start:int,repacked:int)->dict:
 if any(type(x)!=int for x in (stored,next_start,start,repacked)):
  raise ValueError("Slot geometry must use integers")
 if stored<=0 or start<0 or next_start<=start+stored or repacked<=0:
  raise ValueError("Invalid PSPFS slot")
 slot=next_start-start
 overflow=max(0,repacked-slot)
 return {"slot_bytes":slot,"stored_original_bytes":stored,
         "recompressed_bytes":repacked,"excess_bytes":overflow,
         "can_write_inplace":overflow==0,"must_use_append_only":overflow>0}

def audit(source:Path)->dict:
 source=Path(source)
 if source.is_symlink() or not source.is_file() or file_sha256(source)!=USA_SHA:
  raise ValueError("Original ISO mismatch")
 _,files=iso9660_entries(source)
 dat=next(f for f in files if f["path"]=="PSP_GAME/USRDIR/DATA.DAT")
 pack=read_iso_file(source,dat)
 entries=pspfs_entries(pack)
 if len(entries)!=349:raise ValueError("PSPFS count mismatch")
 entry=entries[231]
 if (entry["name"],entry["offset"],entry["size_stored"],entry["size_expanded"])!=(
    "SCRIPT.SDT",9652224,699624,930304):
  raise ValueError("SCRIPT.SDT baseline mismatch")
 next_off=min(e["offset"] for e in entries if e["offset"]>entry["offset"])
 stored=pack[entry["offset"]:entry["offset"]+entry["size_stored"]]
 raw,codec=decompress(stored,entry["size_expanded"])
 if codec!="IMY_8_bloques":raise ValueError("SCRIPT codec mismatch")
 kids={x["name"]:x for x in dsarc_entries(raw)}
 if set(kids)!={"AISCRIPT.DAT","AISCRIPT.TBL","SCRIPT.DAT","SCRIPT.TBL"}:
  raise ValueError("SCRIPT DSARC members mismatch")
 script=kids["SCRIPT.DAT"];tbl=kids["SCRIPT.TBL"]
 data=raw[script["offset"]:script["offset"]+script["size"]]
 table=raw[tbl["offset"]:tbl["offset"]+tbl["size"]]
 commands,_=read_commands(data,table)
 if len(commands)!=51705 or sum(x.content is None for x in commands)!=46308:
  raise ValueError("SCRIPT geometry changed")
 packed=recompress(stored,raw)
 after,after_codec=decompress(packed,entry["size_expanded"])
 if after!=raw or after_codec!=codec:raise ValueError("No-op IMY roundtrip failed")
 margin=slot_safety(len(stored),next_off,entry["offset"],len(packed))
 return {"schema":"cladun.r24.authentic_script_slot_recompression.v1",
         "evidence":"A_AUTHENTIC_PRIVATE_NO_RUNTIME",
         "source_iso_sha256":USA_SHA,
         "script_stored_sha256":hashlib.sha256(stored).hexdigest(),
         "script_uncompressed_sha256":hashlib.sha256(raw).hexdigest(),
         "script_dat_sha256":hashlib.sha256(data).hexdigest(),
         "script_tbl_sha256":hashlib.sha256(table).hexdigest(),
         "script_blocks":1625,"commands":51705,"nontext_commands":46308,
         "script_expanded_bytes":len(raw),"no_op_recompression_verified":True,
         **margin,
         "commercial_payload_exported":False,
         "write_attempted":False,"PPSSPP_verified":False,
         "new_official_integrations":0}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--iso-original",required=True,type=Path)
 a=p.parse_args()
 print(json.dumps(audit(a.iso_original),ensure_ascii=False,indent=2))
if __name__=="__main__":
 main()
