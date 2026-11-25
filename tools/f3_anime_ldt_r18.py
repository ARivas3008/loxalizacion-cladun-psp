"""Authenticated LDT structural audit; no assets exported, no repack."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
import zlib
try:
    from tools.f3_anime_imy_r17 import decode_bounded
except ModuleNotFoundError:
    from f3_anime_imy_r17 import decode_bounded

ISO_SHA='b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
MEMBERS={235:('ANIME001.LDT',287472,'cb7f1354e38ced1a5b19f36c2b45d939e59094e33de901d4b43dc8d65faaa174'),236:('ANIME002.LDT',2067856,'e1617dd4aea349f60953db9471e53c1524e9c3184b2566a4a732c3ecc756eec6')}

def records(blob, kind):
    if len(blob)<16 or any(blob[4:16]):raise ValueError('LDT header')
    n=struct.unpack_from('<I',blob)[0]
    if not 0<n<=10000:raise ValueError('LDT count')
    p=16;seen=set();out=[]
    for _ in range(n):
        if p+16>len(blob):raise ValueError('LDT record header truncated')
        size,ident,a,b=struct.unpack_from('<4I',blob,p)
        end=p+16+size
        if not size or size%4 or end>len(blob) or (a,b)!=(kind,2) or ident in seen:
            raise ValueError('LDT record geometry or ID')
        out.append((ident,blob[p+16:end]));seen.add(ident);p=end
    if p!=len(blob):raise ValueError('LDT tail unaccounted')
    return out

def imy_extent(body):
    if len(body)<34 or body[:4]!=b'IMY\0':raise ValueError('LDT IMY header')
    _,stride,kind,mode,rows=struct.unpack_from('<IHBBH',body,4)
    n=struct.unpack_from('<H',body,32)[0];base=34+n
    if kind!=0 or mode!=8 or stride!=64 or not rows or not n or base>len(body):raise ValueError('LDT IMY geometry')
    out=0;rp=base
    for fl in body[34:base]:
        if out==stride*rows:break
        if fl<16:rp+=(fl+1)*2;out+=(fl+1)*2
        elif fl>=192:out+=((fl&15)+1)*2
        else:out+=2
        if out>stride*rows or rp>len(body):raise ValueError('LDT IMY overflow')
    if out!=stride*rows:raise ValueError('LDT IMY short')
    decoded,consumed,_=decode_bounded(body,0,rp,unit=2)
    if consumed!=rp:raise ValueError('LDT IMY consumption')
    return len(decoded),body[rp:]

def gzip_payload(body,start,limit,expected):
    if not 0<=start<limit<=len(body) or start+8>limit or not 0<expected<=4*1024*1024:raise ValueError('GZIP extent')
    stored,expanded=struct.unpack_from('<II',body,start);end=start+8+stored
    if not stored or end>limit or expanded!=expected or any(body[end:limit]):raise ValueError('GZIP length/padding')
    try:
        obj=zlib.decompressobj(31);data=obj.decompress(body[start+8:end],expected+1)
    except zlib.error as exc:raise ValueError('GZIP decode/CRC') from exc
    if not obj.eof or obj.unused_data or obj.unconsumed_tail or len(data)!=expected:raise ValueError('GZIP exact output')
    return len(data),limit-end

def nested_geometry(ident,body):
    if len(body)<52:raise ValueError('LDT nested header')
    id2,a,b,c,d,n,p,*offs=struct.unpack_from('<13I',body)
    if id2!=ident or not 0<n<=256 or not p or offs[0]!=52 or offs!=sorted(offs) or offs[-1]+12*n>len(body):raise ValueError('LDT nested offsets')
    if [y-x for x,y in zip(offs,offs[1:])]!=[8*a,40*b,48*c,16*d,4*p]:raise ValueError('LDT nested section sizes')
    descriptors=[struct.unpack_from('<IHHBBH',body,offs[-1]+12*i) for i in range(n)]
    starts=[x[0] for x in descriptors]
    if starts!=sorted(set(starts)) or starts[0]<offs[-1]+12*n or any(x%16 for x in starts):raise ValueError('LDT payload pointers')
    result=[]
    for (start,w,h,bpp,mode,flags),limit in zip(descriptors,starts[1:]+[len(body)]):
        if not w or not h or bpp not in (4,8) or mode!=16 or flags!=272 or w*h*bpp%8:raise ValueError('LDT descriptor')
        size,padding=gzip_payload(body,start,limit,w*h*bpp//8)
        result.append((bpp,size,padding))
    return result

def analyze(one,two):
    r1=records(one,2);r2=records(two,0);tails=Counter();nonzero=0;imysize=0;tex=Counter();pads=Counter();gzip_bytes=0
    for _,body in r1:
        size,tail=imy_extent(body);imysize+=size;tails[len(tail)]+=1;nonzero+=any(tail)
    for ident,body in r2:
        for bpp,size,pad in nested_geometry(ident,body):tex[bpp]+=1;pads[pad]+=1;gzip_bytes+=size
    return {'ldt001_records':len(r1),'ldt001_imy_streams':len(r1),'ldt001_decoded_bytes':imysize,'ldt001_unclassified_tail_lengths':dict(sorted(tails.items())),'ldt001_nonzero_tails':nonzero,'ldt002_records':len(r2),'ldt002_nested_gzip_payloads':sum(tex.values()),'ldt002_bpp_field_counts':dict(sorted(tex.items())),'ldt002_decoded_bytes':gzip_bytes,'ldt002_zero_padding_histogram':dict(sorted(pads.items())),'ldt_member_bytes_accounted':[len(one),len(two)],'runtime_or_visual_proven':False,'repacking_authorized':False}

def audit(iso):
    if iso.is_symlink() or not iso.is_file() or iso.stat().st_size!=305496064:raise ValueError('ISO source')
    with iso.open('rb') as f:
        if hashlib.file_digest(f,'sha256').hexdigest()!=ISO_SHA:raise ValueError('ISO hash')
        f.seek(113770496);t=f.read(16+349*32)
        if t[:8]!=b'PSPFS_V1' or struct.unpack_from('<I',t,8)[0]!=349:raise ValueError('PSPFS')
        members=[]
        for i,(name,n,sha) in MEMBERS.items():
            row=t[16+i*32:48+i*32];expanded,stored,off=struct.unpack_from('<III',row,20)
            if row[:20].split(b'\0')[0].decode('ascii')!=name or expanded or stored!=n or off<len(t) or off+n>191697408:raise ValueError('PSPFS member')
            f.seek(113770496+off);data=f.read(n)
            if hashlib.sha256(data).hexdigest()!=sha:raise ValueError('LDT hash')
            members.append(data)
    return {'iso_sha256':ISO_SHA,'evidence':'A_STATIC_NOT_C',**analyze(*members)}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--iso-original',type=Path,required=True);a=p.parse_args();print(json.dumps(audit(a.iso_original),indent=2))
