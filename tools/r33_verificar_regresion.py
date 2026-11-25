#!/usr/bin/env python3
"""Reproduce the R33 authentic long-pack fingerprints on a local legal USA ISO."""
import argparse
import json
from pathlib import Path
from tools.r32_auditar_packs import audit

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"reports/R33_PACKS_LARGOS.json"
FIELDS={"records":"texts","plan_sha256":"plan_sha256",
        "script_sha256":"script_sha256","compressed_sha256":"compressed_sha256",
        "stored_size":"stored_bytes"}

def compare(actual, expected):
    for field,ref in FIELDS.items():
        if actual.get(field)!=expected[ref]:
            raise ValueError("R33 regression: "+field)
    if actual.get("repacked_blocks")!=len(expected["imy_repacked"]):
        raise ValueError("R33 recompressed block count changed")
    return True

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("iso",type=Path)
    parser.add_argument("--pack",choices=["3","4","5","6","7","long"],default="long")
    args=parser.parse_args()
    report=json.loads(REPORT.read_text(encoding="utf-8"))
    key="long_694" if args.pack=="long" else args.pack
    actual=audit(args.iso,args.pack)["packs"][args.pack]
    compare(actual,report["packs"][key])
    print(json.dumps({"pack":args.pack,"matched":True,"actual":actual,
                      "runtime_verified":False,"release_authorized":False},indent=2))

if __name__=="__main__":
    main()
