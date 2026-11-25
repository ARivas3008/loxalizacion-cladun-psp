"""R56 native ellipsis donation; only an explicitly experimental presentation change."""
from tools.script_event_guard import require
from tools.r35_ligaduras_acumuladas import PAIRS
from tools.f4_r21_ligature_capacity import decode_encoded

RESIDUAL=0x88621
DONOR=0x8862c

def extend_donors(baseline,residuals,donors):
    require(RESIDUAL in residuals and DONOR in baseline and DONOR not in donors,
            "R56 manifest drift")
    old,new,gid=baseline[DONOR]
    ro,rn,rgid=residuals[RESIDUAL]
    require((gid,rgid,len(old),len(new),len(ro),len(rn))==("004508","004507",8,8,3,4)
            and decode_encoded(new,PAIRS)=="¡Pues...!"
            and decode_encoded(rn,PAIRS)=="¡Oh!" and new.count(b"...")==1,
            "R56 exact presentation preimage drift")
    updated=new.replace(b"...",bytes.fromhex("8163"))
    require(len(updated)==7 and decode_encoded(updated,PAIRS)=="¡Pues…!",
            "R56 native ellipsis roundtrip")
    return {**donors,DONOR:(old,updated,gid)}

def verify_native_glyph(iso):
    import struct
    from tools.font_es_patch import archive
    from tools.extract_cladun import dsarc_entries
    _,_,_,_,arc,_=archive(iso)
    member=next(x for x in dsarc_entries(arc) if x["name"]=="FONT.BIN")
    raw=arc[member["offset"]:member["offset"]+member["size"]]
    n=struct.unpack_from("<I",raw)[0]
    require(n==2721 and len(raw)==4+4*n,"R56 source font geometry")
    records={struct.unpack_from("<H",raw,4+4*i)[0]:raw[6+4*i:8+4*i] for i in range(n)}
    require(records.get(0x8163)==bytes((0,13)) and records.get(0x2e)==bytes((0,2)),
            "R56 native ellipsis metrics drift")
    return {"code":"8163","advance":13,"three_ascii_dots_advance":6,"runtime_verified":False}
