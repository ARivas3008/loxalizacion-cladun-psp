"""R42 authenticated 21 fixed-width proposals; no runtime or release claim."""
from pathlib import Path
import hashlib
import re
from tools.r29_integrar_longitud_fija import DRAFT, require
from tools.f4_r21_ligature_capacity import read_canonical, encode_fixed, decode_encoded
from tools.r35_ligaduras_acumuladas import PAIRS
from tools.r31_bulk_padding import serialized
from tools.charset_es import encode_spanish, ES_GLYPHS
from tools.r37_simbolos_preservados import multibyte_tokens, ICONS

OVERLAY = Path(__file__).resolve().parents[1] / "traduccion/propuestas/R42_CANDIDATOS.tsv"
IDS = frozenset("000079 001234 001247 001312 001626 001766 001850 001948 002041 002626 002939 003375 003812 004169 004170 004171 004172 004173 004174 004528 004600".split())
LINGUISTIC = frozenset("000079 001234 001247 001850 004169 004170 004171 004172 004173 004174".split())
PREIMAGE = "e2daa4fd942a222806bf87676c27ebbb3c2fe59c520b2ea6d54f94edc66b6877"
PLAN = "d98e149626b727e088c5f7abeb3d58fee5c4e1342fce1e9f8ad6840a31acd739"
FORMAT = re.compile(rb"(?:-?[0-9]+|[A-Z])%|[@#$%^&]+")

def audit(full, overlay=OVERLAY):
    done = {x["gid"] for x in full}
    require(len(full) == len(done) == 4840, "R40 profile drift")
    rows = {r["grupo_id"]: r for r in read_canonical(DRAFT)}
    raw = Path(overlay).read_bytes()
    require(raw.endswith(b"\n") and len(raw.splitlines()) == 21, "R42 overlay structure drift")
    plan = []
    for line in raw.decode("utf-8").splitlines():
        gid, offset, text = line.split("\t", 2)
        r = rows[gid]
        old = bytes.fromhex(r["bytes_hex"])
        at = int(offset, 16)
        require(gid in IDS and gid not in done and r["origen"] == "SCRIPT.SDT/SCRIPT.DAT"
                and at == int(r["offset_hex"], 16) and len(old) == int(r["longitud_original_bytes"]),
                "R42 source identity drift")
        tokens = multibyte_tokens(old)
        require(bool(tokens) == (gid in LINGUISTIC)
                and not any(t.decode("cp932") in ICONS for t in tokens),
                "R42 icon/control source rejected")
        require(text == text.strip() and text and all(32 <= ord(c) <= 126 or c in ES_GLYPHS for c in text)
                and b"\\" not in old and "\\" not in text, "R42 unknown symbol")
        ordinary = encode_spanish(text)
        if len(ordinary) > len(old):
            new = encode_fixed(text, len(old), PAIRS)
            pad = 0
        else:
            pad = len(old) - len(ordinary)
            require(pad <= 7, "R42 excessive padding")
            new = ordinary + b" " * pad
        require(len(new) == len(old) and new != old and 0 not in new
                and decode_encoded(new, PAIRS) == text + " " * pad
                and not multibyte_tokens(new) and FORMAT.findall(new) == FORMAT.findall(old),
                "R42 codec, width or format drift")
        plan.append({"gid":gid,"group_id":gid,"offset":at,"old":old,"new":new,"padding":pad})
    plan.sort(key=lambda x:x["offset"])
    require(len(plan) == len({x["gid"] for x in plan}) == 21
            and {x["gid"] for x in plan} == IDS
            and hashlib.sha256(serialized(plan,False)).hexdigest() == PREIMAGE
            and hashlib.sha256(serialized(plan)).hexdigest() == PLAN,
            "R42 authenticated plan fingerprint mismatch")
    combined = sorted(full+plan, key=lambda x:x["offset"])
    require(len(combined) == len({x["gid"] for x in combined}) == 4861
            and all(a["offset"]+len(a["old"])<=b["offset"] for a,b in zip(combined,combined[1:])),
            "R42 overlap or duplicate")
    return plan, {"new":21,"prior":8188,"total_if_built":8209,"remaining":39,
                  "source_language_multibyte":len(LINGUISTIC),"canonical_modified":False,
                  "runtime_verified":False,"release_authorized":False}
