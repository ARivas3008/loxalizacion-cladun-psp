"""R43: five new authentic fixed-width slots, plus a context-preserving repair.
003765 is a proper name and ellipsis, not a byte substitution. Keep the original
target denominator and record that disposition separately. No runtime claim.
"""
from pathlib import Path
import hashlib
from tools.r29_integrar_longitud_fija import DRAFT, require
from tools.f4_r21_ligature_capacity import read_canonical, encode_fixed, decode_encoded
from tools.r35_ligaduras_acumuladas import PAIRS
from tools.r31_bulk_padding import serialized
from tools.charset_es import encode_spanish, ES_GLYPHS
from tools.r37_simbolos_preservados import multibyte_tokens

OVERLAY = Path(__file__).resolve().parents[1] / "traduccion/propuestas/R43_CANDIDATOS.tsv"
IDS = frozenset("003017 003233 003639 004010 004919".split())
PREIMAGE = "26d9424ca372d43b667908ccb6f0c5017fb98dbc0a8e221696d3ac9fae7c50bd"
PLAN = "b49562791de082cd4e1badccc1a76bf9aef545ccb7368716246422c49f3e3538"
REPAIR_ID = "003766"
UNCHANGED_ID = "003765"

def audit(full, overlay=OVERLAY):
    done = {x["gid"]:x for x in full}
    require(len(full)==len(done)==4861 and REPAIR_ID in done and UNCHANGED_ID not in done,
            "R42 profile drift")
    rows = {r["grupo_id"]:r for r in read_canonical(DRAFT)}
    raw = Path(overlay).read_bytes()
    require(raw.endswith(b"\n") and len(raw.splitlines())==5,"R43 overlay shape drift")
    selected = []
    for line in raw.decode("utf-8").splitlines():
        gid, offset, text = line.split("\t",2)
        r=rows[gid]; old=bytes.fromhex(r["bytes_hex"]); at=int(offset,16)
        require(gid in IDS and gid not in done and r["origen"]=="SCRIPT.SDT/SCRIPT.DAT"
                and at==int(r["offset_hex"],16) and len(old)==int(r["longitud_original_bytes"]),
                "R43 source slot drift")
        require(multibyte_tokens(old)==([bytes.fromhex("8168")] if gid=="004010" else [])
                and text and text==text.strip() and all(32<=ord(c)<=126 or c in ES_GLYPHS for c in text)
                and chr(92) not in old.decode("cp932")+text and "%" not in old.decode("cp932")+text,
                "R43 symbol/control drift")
        ordinary=encode_spanish(text)
        if len(ordinary)>len(old):
            new=encode_fixed(text,len(old),PAIRS); pad=0
        else:
            pad=len(old)-len(ordinary); require(pad<=7,"R43 padding limit")
            new=ordinary+b" "*pad
        require(len(new)==len(old) and new!=old and 0 not in new
                and not multibyte_tokens(new) and decode_encoded(new,PAIRS)==text+" "*pad,
                "R43 codec/width mismatch")
        selected.append({"gid":gid,"group_id":gid,"offset":at,"old":old,"new":new})
    selected.sort(key=lambda x:x["offset"])
    require(len(selected)==len({x["gid"] for x in selected})==5
            and {x["gid"] for x in selected}==IDS
            and hashlib.sha256(serialized(selected,False)).hexdigest()==PREIMAGE
            and hashlib.sha256(serialized(selected)).hexdigest()==PLAN,"R43 source/plan digest drift")
    p=rows[UNCHANGED_ID]; q=rows[REPAIR_ID]; before=done[REPAIR_ID]
    p_old=bytes.fromhex(p["bytes_hex"]); q_old=bytes.fromhex(q["bytes_hex"])
    require(p["origen"]==q["origen"]=="SCRIPT.SDT/SCRIPT.DAT"
            and p["script_id"]==q["script_id"] and p["indice_registro"]==q["indice_registro"]
            and int(q["orden_script"])==int(p["orden_script"])+1
            and p["original"]=="Despina..." and p["espanol"]=="Despina... Por favor."
            and q["original"]=="Please. Please try to" and q["espanol"]=="Intenta superar"
            and int(q["offset_hex"],16)==int(p["offset_hex"],16)+len(p_old)+8
            and hashlib.sha256(p_old).hexdigest()=="fe6f1a3799d25ab88b952394615448b0fbe87da27cdebb020f04ad23b5e466ea"
            and q_old.hex()=="506c656173652e20506c656173652074727920746f"
            and before["old"]==q_old and before["offset"]==int(q["offset_hex"],16)
            and before["new"].hex()=="496e74656e74612073757065726172202020202020",
            "R43 contextual repair preimage mismatch")
    repaired=encode_fixed("Por favor, intenta superar",len(q_old),PAIRS)
    repair={**before,"new":repaired}
    require(repaired.hex()=="50c220666176c22c2069bdb5bf2073757065726172"
            and hashlib.sha256(serialized([repair])).hexdigest()=="748c58497c9892490f645cdd2854cdd8ca60fc43ed04eeff1aa7f506a861d6d8",
            "R43 contextual repair digest mismatch")
    combined=sorted([repair if x["gid"]==REPAIR_ID else x for x in full]+selected,key=lambda x:x["offset"])
    require(len(combined)==len({x["gid"] for x in combined})==4866
            and all(a["offset"]+len(a["old"])<=b["offset"] for a,b in zip(combined,combined[1:])),
            "R43 overlap/duplicate")
    return selected,repair,{"new":5,"repair_existing_id":REPAIR_ID,"resolved_without_new_bytes":1,
            "resolved_without_change_id":UNCHANGED_ID,"total_if_built":8214,"resolved_original_target":8215,
            "remaining":33,"runtime_verified":False,"release_authorized":False}
