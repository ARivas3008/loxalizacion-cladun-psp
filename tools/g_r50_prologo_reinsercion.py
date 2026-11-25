"""R50 canonical user text; authenticate package before using any delta."""
import argparse
import json
from pathlib import Path
import zipfile
try:
    from tools.g_r49_prologo_reinsercion import package_check, build_private, require, sha
except ModuleNotFoundError:
    from g_r49_prologo_reinsercion import package_check, build_private, require, sha

ROOT=Path(__file__).resolve().parents[1]
def verify_text(manifest):
    canonical=(ROOT/manifest["canonical_text_path"]).read_bytes()
    require(sha(canonical)==manifest["prologue"]["text_sha256"],"canonical text hash")
    require(canonical.decode("utf-8").splitlines()==manifest["prologue"]["text"],"canonical lines differ")
    require(manifest["pic0"]["text"]==manifest["prologue"]["text"][-3:],"PIC0 text differs")
    return canonical
def verify_package(package,manifest):
    canonical=verify_text(manifest)
    delta=package_check(package,manifest)
    with zipfile.ZipFile(package) as z:
        require(z.read("prologo_es.txt")==canonical,"obsolete prologue package")
        t=json.loads(z.read("R49_titulo.json"))
        pic=next(x for x in t["rows"] if x["asset"]=="PIC0.PNG")
        require([x["text"] for x in pic["labels"][1:]]==manifest["pic0"]["text"],"PIC0 narrative mismatch")
        require(pic["new_sha256"]==manifest["pic0"]["new_sha256"],"PIC0 encoded output mismatch")
    return delta
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--package",type=Path,required=True);p.add_argument("--iso",type=Path);p.add_argument("--candidate",type=Path);a=p.parse_args()
    r=json.loads((ROOT/"reports/G_R50_PROLOGO_CANONICO.json").read_text(encoding="utf-8"))
    delta=verify_package(a.package,r)
    require(bool(a.iso)==bool(a.candidate),"provide --iso and --candidate together")
    print(json.dumps(build_private(a.iso,a.candidate,delta,r) if a.iso else {"package_hash_pass":True,"canonical_text_pass":True,"runtime_verified":False},indent=2))
if __name__=="__main__":main()
