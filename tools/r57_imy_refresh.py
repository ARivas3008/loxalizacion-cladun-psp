"""Opt-in IMY literal-cache refresh. Independent decoding is required before use."""
import struct

def u16(data,pos):
    return struct.unpack_from("<H",data,pos)[0]

def prepare(raw,header):
    stride,rows=u16(header,8),u16(header,12)
    if len(raw)!=stride*rows or len(raw)%2 or stride<4 or stride%2:
        raise ValueError("R57 IMY geometry")
    words=[raw[i:i+2] for i in range(0,len(raw),2)]
    count=len(words);matches=[]
    for gap in (2,stride,stride+2,stride-2):
        d=gap//2;v=[0]*(count+17)
        for i in range(count-1,d-1,-1):
            if words[i]==words[i-d]:v[i]=min(16,v[i+1]+1)
        matches.append(v)
    prev={};nxt=[count+1]*count
    for i in range(count-1,-1,-1):
        nxt[i]=prev.get(words[i],count+1);prev[words[i]]=i
    best=[max((matches[k][i],-k) for k in range(4)) for i in range(count)]
    return words,best,nxt

def encode_refresh(raw,header,prepared,*,distance=320,next_limit=32,flush_cost=True):
    words,best,nxt=prepared
    if b"".join(words)!=raw:raise ValueError("R57 prepared input mismatch")
    count=len(words);flags,literals,pending,recent=bytearray(),bytearray(),bytearray(),{}
    def flush():
        for p in range(0,len(pending),32):
            y=pending[p:p+32];flags.append(len(y)//2-1);old=len(literals);literals.extend(y)
            for j in range(0,len(y),2):recent[bytes(y[j:j+2])]=old+j
        pending.clear()
    i=0
    while i<count:
        size,kind=best[i];kind=-kind;word=words[i]
        if size:
            flush();flags.append(0xc0+(kind<<4)+size-1);i+=size;continue
        prev=recent.get(word)
        for j in range(len(pending)-2,-1,-2):
            if pending[j:j+2]==word:prev=len(literals)+j;break
        delta=len(literals)+len(pending)-prev if prev is not None else 99999
        # Refresh a near-expiring literal if it is likely to be reused soon.
        # The literal is written normally; no new IMY flag or codec is introduced.
        refresh=delta>distance and nxt[i]-i<=next_limit and (pending or not flush_cost)
        if 2<=delta<=352 and delta%2==0 and not refresh:
            flush();flags.append(0x10+(delta-2)//2);i+=1;continue
        pending.extend(word);i+=1
        if len(pending)==32:flush()
    flush()
    if len(flags)>65535:raise ValueError("R57 IMY flag overflow")
    return bytes(header[:32])+struct.pack("<H",len(flags))+flags+literals
