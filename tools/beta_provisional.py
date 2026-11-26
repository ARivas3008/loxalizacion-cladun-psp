"""Private beta harness. R43 is control, R52 full experimental, R56 optional.
No BPS, no release, no automatic runtime PASS. Run from repository root.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from tools import integrar_parche_seguro as integrator
from tools.extract_cladun import iso9660_entries, read_iso_file, pspfs_entries, decompress, dsarc_entries
from tools.script_event_guard import read_commands, require

PROFILES = {"r43": (8214, 0, 0, 4866), "r52": (8247, 146, 104, 4899), "r56": (8236, 28, 5, 4888)}

def sha(path):
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()

def children(iso):
    _, records = iso9660_entries(iso)
    pkg = read_iso_file(iso, next(r for r in records if r["path"] == "PSP_GAME/USRDIR/DATA.DAT"))
    entries = pspfs_entries(pkg)
    require(len(entries) == 349, "Unexpected PSPFS count")
    e = next(e for e in entries if e["name"] == "SCRIPT.SDT")
    arc, _ = decompress(pkg[e["offset"]:e["offset"]+e["size_stored"]], e["size_expanded"])
    return {m["name"]: arc[m["offset"]:m["offset"]+m["size"]] for m in dsarc_entries(arc)}

def movement(before, after, profile):
    changes, moved, nontext, replaced = PROFILES[profile]
    require(set(before) == set(after) == {"SCRIPT.DAT", "SCRIPT.TBL", "AISCRIPT.DAT", "AISCRIPT.TBL"}, "Script children mismatch")
    for name in ("SCRIPT.TBL", "AISCRIPT.DAT", "AISCRIPT.TBL"):
        require(before[name] == after[name], "Changed sibling: " + name)
    a, aa = read_commands(before["SCRIPT.DAT"], before["SCRIPT.TBL"])
    b, bb = read_commands(after["SCRIPT.DAT"], after["SCRIPT.TBL"])
    require(aa == bb and len(a) == len(b) == 51705, "Script geometry mismatch")
    rows = []
    exact = texts = 0
    for x,y in zip(a,b):
        require((x.block,x.order,x.code,x.instruction_id)==(y.block,y.order,y.code,y.instruction_id), "Command identity changed")
        if x.content is None:
            require(x.raw == y.raw, "Nontext changed")
            exact += 1
        else:
            texts += x.content != y.content
        if x.offset != y.offset:
            rows.append({"case_id": f"{profile.upper()}-{len(rows)+1:03d}", "block":x.block, "order":x.order,
                         "opcode":f"0x{x.code:02X}", "instruction_id":x.instruction_id,
                         "original_offset":f"0x{x.offset:X}", "candidate_offset":f"0x{y.offset:X}",
                         "nontext":x.content is None, "status":"NOT_RUN",
                         "runtime_evidence_sha256":"","notes":""})
    require((exact,texts,len(rows),sum(r["nontext"] for r in rows))==(46308,replaced,moved,nontext), "Unexpected counts")
    return rows

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--iso", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True, help="New private directory outside repository")
    p.add_argument("--profile",choices=tuple(PROFILES),required=True)
    p.add_argument("--acepto-beta-experimental",action="store_true")
    p.add_argument("--corrective-ui",action="store_true",help="Experimental Save + white accent ink; R52 only")
    a=p.parse_args()
    require(not a.corrective_ui or a.profile=="r52","Corrective UI is restricted to R52")
    require(a.profile=="r43" or a.acepto_beta_experimental, "Experimental relocation requires opt-in")
    iso=a.iso.resolve(strict=True)
    require(sha(iso)==integrator.SOURCE_SHA256,"Wrong original ISO")
    output=a.output.resolve()
    root=Path(__file__).resolve().parents[1]
    require(root not in (output,*output.parents),"Private output must be outside repository")
    output.mkdir(parents=True,exist_ok=False)
    candidate=output/"candidate.iso"; report=output/"build.json"
    if a.profile=="r56":
        from tools.r55_private_accumulated import build_private
        result=build_private(iso,candidate,report,native_ellipsis=True)
    else:
        result=integrator.build(iso,candidate,report,experimental_partial=True,event_safe_only=True,
             verified_packs=True,unified_profile=True,extended_padding=True,verified_symbols=True,
             concise_verified=True,r39_verified=True,r40_verified=True,r42_verified=True,r43_verified=True,
             r52_local_optimized=a.profile=="r52", corrective_ui=a.corrective_ui)
    require(result["texto_aplicado"]==PROFILES[a.profile][0],"Unexpected insertion count")
    require(sha(iso)==integrator.SOURCE_SHA256 and sha(candidate)==result["iso_resultante_sha256"],"Hash mismatch")
    rows=movement(children(iso),children(candidate),a.profile)
    with (output/"movement_qa.csv").open("x",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=["case_id","block","order","opcode","instruction_id","original_offset","candidate_offset","nontext","status","runtime_evidence_sha256","notes"])
        w.writeheader();w.writerows(rows)
    summary={"profile":a.profile,"corrective_ui":a.corrective_ui,"original_sha256":sha(iso),"candidate_sha256":sha(candidate),
             "text_substitutions":PROFILES[a.profile][0],"resolved_without_change":1,
             "moved_commands":len(rows),"runtime_cases_passed":0,"runtime_verified":False,"release_authorized":False,
             "state":"STATIC_PASS_RUNTIME_NOT_RUN"}
    (output/"beta_status.json").write_text(json.dumps(summary,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,indent=2))

if __name__=="__main__":
    main()
