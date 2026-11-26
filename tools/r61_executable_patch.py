"""Reproduce locally tested R61 from private R60 ISO and its PPSSPP ELF dump."""
import argparse, hashlib, shutil
from pathlib import Path
SOURCE='df5082784e3ca8a610abffbaf768271aa171ba9614fac75ee28fd06de23ab362'
DUMP='e5be427f73544f4ff6cf629b65b0b2f4c4ae3a83b3cf56b04c6b8b37835b713c'
TARGET_ELF='a2535005b45e68906cc9f76147d86df4407b7f83ddd1fea1fb44bd96c1837b94'
TARGET='954ecc6f5514c884e7c0a25a25e7a0d075a5c6e5c8f38e02dd8ea75e13940f37'
OFFSET=0x110000
SIZE=2158864
PATCHES=((0x163b30,b'Vencidos'),(0x17f28,bytes.fromhex('ff0024327fff85241f00a52c0d00a0140000163420ff85241d00a52c0900a014000000004cff85242c00a52c0100b6380d0000100a000434000000000000000000000000')),(0x186dc,bytes.fromhex('ff00a6307fffc7241f00e72c0e00e0140000113420ffc7241d00e72c0a00e014000000004cffc7242c00e72c0100f1380d0000100000000000000000000000000000000000000')))
def digest(path):
    with path.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def require(ok,msg):
    if not ok: raise ValueError(msg)
def patch_elf(raw):
    require(len(raw)==SIZE and raw[:4]==b'\x7fELF' and hashlib.sha256(raw).hexdigest()==DUMP,'Wrong private ELF dump')
    require(raw.count(b'Defeated\n%7d\0')==1,'Unexpected format')
    out=bytearray(raw)
    for off,data in PATCHES: out[off:off+len(data)]=data
    require(hashlib.sha256(out).hexdigest()==TARGET_ELF,'Patched ELF hash mismatch')
    return out
def run(source,dump,target):
    require(digest(source)==SOURCE,'Wrong R60 ISO')
    require(not target.exists(),'Output already exists')
    elf=patch_elf(dump.read_bytes())
    shutil.copyfile(source,target)
    try:
        with target.open('r+b') as f: f.seek(OFFSET); f.write(elf)
        require(digest(target)==TARGET,'R61 hash mismatch')
    except Exception:
        target.unlink(); raise
    print(TARGET)
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for x in ('source','dump','target'): p.add_argument(x,type=Path)
    a=p.parse_args();run(a.source,a.dump,a.target)
