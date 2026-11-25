"""Private R49 package authentication and exact-slot prologue diagnostic.

Never use this absolute offset on an already rebuilt ISO. Never commit assets.
A successful check is binary evidence only, not PPSSPP or official approval.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]
REPORT=ROOT/"reports/G_R49_EDICION_CONTEXTUAL.json"
def require(ok,reason):
    if not ok:raise ValueError(reason)
def sha(blob):return hashlib.sha256(blob).hexdigest()
def file_sha(path):
    with Path(path).open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()
def apply_delta(old,delta,before,after):
    require(len(old)==len(delta) and sha(old)==before,"wrong delta extent or preimage")
    out=bytes(a^b for a,b in zip(old,delta))
    require(sha(out)==after and out!=old,"wrong delta output")
    return out
def package_check(package,manifest):
    p=manifest["package"]
    require(package.stat().st_size==p["bytes"] and file_sha(package)==p["sha256"],"R49 private ZIP hash")
    with zipfile.ZipFile(package) as z:
        names=z.namelist()
        require(len(names)==len(set(names))==p["files"],"ZIP member count or duplicate")
        require(all(not n.startswith("/") and ".." not in n.split("/") and chr(92) not in n for n in names),"unsafe ZIP member")
        for n,h in p["manifests"].items():require(sha(z.read(n))==h,"manifest hash: "+n)
        delta=z.read("prologo_stream_xor.bin")
    q=manifest["prologue"]
    require(len(delta)==q["bytes_before"]==q["bytes_after"]==4308 and sha(delta)==q["stream_delta_sha256"],"prologue delta")
    return delta
def build_private(iso,candidate,delta,manifest):
    require(iso.resolve()!=candidate.resolve() and not candidate.exists(),"never overwrite an ISO")
    require(iso.stat().st_size==manifest["source_iso_bytes"] and file_sha(iso)==manifest["source_iso_sha256"],"original USA ISO required")
    q=manifest["prologue"];at=q["absolute_iso_offset"];n=q["bytes_before"]
    candidate.parent.mkdir(parents=True,exist_ok=True)
    fd,tmp=tempfile.mkstemp(prefix=".cladun_r49_private_",dir=candidate.parent);os.close(fd)
    path=Path(tmp)
    try:
        with iso.open("rb") as src,path.open("wb") as out:
            remaining=at
            while remaining:
                part=src.read(min(1048576,remaining));require(bool(part),"short ISO");out.write(part);remaining-=len(part)
            old=src.read(n);new=apply_delta(old,delta,q["original_stream_sha256"],q["new_stream_sha256"])
            require(sum(a!=b for a,b in zip(old,new))==q["changed_iso_bytes"],"diff count")
            out.write(new)
            while part:=src.read(1048576):out.write(part)
        require(path.stat().st_size==manifest["source_iso_bytes"] and file_sha(path)==q["diagnostic_iso_sha256"],"diagnostic candidate hash")
        require(file_sha(iso)==manifest["source_iso_sha256"],"original changed")
        os.link(path,candidate)
    finally:path.unlink(missing_ok=True)
    return {"private_diagnostic_sha256":q["diagnostic_iso_sha256"],"only_prologue_reinserted":True,"full_accumulated_iso":False,"runtime_verified":False,"release_authorized":False}
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--package",type=Path,required=True);p.add_argument("--iso",type=Path);p.add_argument("--candidate",type=Path);a=p.parse_args()
    manifest=json.loads(REPORT.read_text(encoding="utf-8"));delta=package_check(a.package,manifest)
    require(bool(a.iso)==bool(a.candidate),"provide both --iso and --candidate or neither")
    print(json.dumps(build_private(a.iso,a.candidate,delta,manifest) if a.iso else {"package_hash_pass":True,"iso_written":False,"runtime_verified":False},indent=2))
if __name__=="__main__":main()
