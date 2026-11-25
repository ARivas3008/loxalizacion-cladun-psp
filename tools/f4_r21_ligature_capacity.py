#!/usr/bin/env python3
"""R21: 44-ligature fixed-width feasibility, no assets modified, no PPSSPP claims."""
import argparse,csv,hashlib,json,struct
from pathlib import Path
from collections import Counter
try:
 from tools.charset_es import encode_spanish,decode_spanish
except ModuleNotFoundError:
 from charset_es import encode_spanish,decode_spanish

CAPACITY=44
CODE_START=0xB4
CANONICAL_SHA1="400a9c9ec06f7456b5ec6e11f7502d711b0a976e"
WIDTHS=dict(zip("abcdefghijklmnopqrstuvwxyz",
                (7,7,7,7,7,7,7,7,3,5,7,3,8,7,7,7,7,5,6,7,6,7,8,7,7,6)))

def read_canonical(path):
 raw=Path(path).read_bytes()
 if hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()!=CANONICAL_SHA1:
  raise ValueError("Canonical draft SHA changed")
 with Path(path).open(encoding="utf-8-sig",newline="") as f:
  rows=list(csv.DictReader(f))
 if len(rows)!=9237 or len({r["grupo_id"] for r in rows})!=9237:
  raise ValueError("Missing or duplicate canonical IDs")
 return rows

def allowed_pair(s):
 return (len(s)==2 and s[0] in WIDTHS and s[1] in WIDTHS
         and WIDTHS[s[0]]+WIDTHS[s[1]]<=15)

def select_pairs(growing):
 counts=Counter(a+b for r in growing for a,b in zip(r["espanol"],r["espanol"][1:])
                if allowed_pair(a+b))
 return [s for s,n in sorted(counts.items(),key=lambda p:(-p[1],p[0]))[:CAPACITY]]

def matching(text,pairs):
 allowed=set(pairs);n=len(text);dp=[0]*(n+2)
 for i in range(n-1,-1,-1):
  dp[i]=dp[i+1]
  if text[i:i+2] in allowed:
   dp[i]=max(dp[i],1+dp[i+2])
 result=[];i=0
 while i<n:
  s=text[i:i+2]
  if s in allowed and dp[i]==1+dp[i+2]:
   result.append((i,s));i+=2
  else:i+=1
 return result

def decode_encoded(raw,pairs):
 if not 1<=len(pairs)<=CAPACITY:raise ValueError("Wrong dictionary")
 result=[];i=0
 while i<len(raw):
  b=raw[i]
  if CODE_START<=b<CODE_START+CAPACITY:
   if b-CODE_START>=len(pairs):raise ValueError("Unmapped experimental ligature code")
   result.append(pairs[b-CODE_START]);i+=1
  elif 0x81<=b<=0x9f or 0xe0<=b<=0xfc:
   if i+1>=len(raw):raise ValueError("Truncated SJIS lead")
   result.append(decode_spanish(raw[i:i+2]));i+=2
  else:
   result.append(decode_spanish(raw[i:i+1]));i+=1
 return "".join(result)

def encode_fixed(text,expected_bytes,pairs):
 if not 1<=len(pairs)<=CAPACITY or len(set(pairs))!=len(pairs) or not all(allowed_pair(s) for s in pairs):
  raise ValueError("Invalid dictionary")
 ordinary=encode_spanish(text);delta=len(ordinary)-expected_bytes
 if delta<=0:raise ValueError("Do not pad shorter or identical strings")
 candidates=matching(text,pairs)
 if len(candidates)<delta:raise ValueError("Not enough nonoverlapping ligatures")
 chosen=dict(candidates[:delta]);by_code={s:CODE_START+i for i,s in enumerate(pairs)}
 output=bytearray();i=0
 while i<len(text):
  if i in chosen:
   output.append(by_code[chosen[i]]);i+=2
  else:
   output.extend(encode_spanish(text[i]));i+=1
 if len(output)!=expected_bytes or decode_encoded(bytes(output),pairs)!=text:
  raise ValueError("Roundtrip or original byte-width invariant broken")
 return bytes(output)

def original_halfwidth_inventory(rows):
 found=0;broken=[]
 for r in rows:
  data=bytes.fromhex(r.get("bytes_hex",""));i=0
  while i<len(data):
   b=data[i]
   if 0x81<=b<=0x9f or 0xe0<=b<=0xfc:
    if i+1>=len(data):
     broken.append(r["grupo_id"]);break
    i+=2
   else:
    if 0xa1<=b<=0xdf:found+=1
    i+=1
 return found,broken

def analyze(rows):
 script=[r for r in rows if r["origen"]=="SCRIPT.SDT/SCRIPT.DAT" and r["espanol"]]
 growing=[];shorter=equal=0
 for r in script:
  old=len(bytes.fromhex(r["bytes_hex"]));new=len(encode_spanish(r["espanol"]))
  if new>old:growing.append({**r,"overflow":new-old})
  elif new<old:shorter+=1
  else:equal+=1
 pairs=select_pairs(growing)
 if len(pairs)!=CAPACITY:raise ValueError("Insufficient ligature pairs")
 theoretical_fit=unresolved_bytes=total_excess=0;sample=[]
 for r in growing:
  excess=r["overflow"];n=len(matching(r["espanol"],pairs))
  total_excess+=excess
  if n>=excess:
   theoretical_fit+=1
   if len(sample)<12:
    encoded=encode_fixed(r["espanol"],len(bytes.fromhex(r["bytes_hex"])),pairs)
    sample.append({"grupo_id":r["grupo_id"],"proposed_bytes":len(encoded),
                   "saved_bytes":excess})
  else:unresolved_bytes+=excess-n
 used,broken=original_halfwidth_inventory(rows)
 if (len(script),equal,len(growing),shorter,theoretical_fit)!=(5207,683,2883,1641,2120):
  raise ValueError("Corpus or capacity computation drift")
 if used!=0 or broken!=["008723","008724"]:
  raise ValueError("Source code collisions or unexpected source truncation")
 return {"schema":"cladun.r21.experimental_ligature_feasibility.v1",
   "evidence":"B_CANONICAL_STATIC_NOT_PPSSPP",
   "original_rows":len(rows),"script_rows":len(script),
   "equal_width":equal,"growing":len(growing),"shrinking":shorter,
   "available_codes":"B4-DF","candidate_ligatures":len(pairs),"pairs":pairs,
   "theoretically_fittable_growing":theoretical_fit,
   "still_overflow_growing":len(growing)-theoretical_fit,
   "total_growing_excess_bytes":total_excess,"residual_excess_bytes":unresolved_bytes,
   "original_standalone_A1_DF_codepoints":used,
   "source_truncation_groups":broken,"roundtrip_samples_metadata":sample,
   "font_modified":False,"emulator_proven":False,"approved_for_reinsertion":False}

def audit_font(iso):
 try:from font_es_patch import archive
 except ModuleNotFoundError:from tools.font_es_patch import archive
 _,_,_,_,arc,members=archive(iso)
 member=members[0]
 raw=arc[member["offset"]:member["offset"]+member["size"]]
 count=struct.unpack_from("<I",raw)[0]
 codes=[struct.unpack_from("<H",raw,4+i*4)[0] for i in range(count)]
 if count!=2721 or codes!=sorted(set(codes)) or any(0xa1<=c<=0xdf for c in codes):
  raise ValueError("Original FONT.BIN geometry / codes mismatch")
 for ch,w in WIDTHS.items():
  if raw[4+4*codes.index(ord(ch))+3]!=w:
   raise ValueError("Original font metric mismatch "+ch)
 padding=members[1]["offset"]-(member["offset"]+member["size"])
 if padding<63*4 or count+63>3072:
  raise ValueError("No space for 63 hypothetical entries")
 return {"evidence":"A_AUTHENTIC_FONT_STATIC","font_arc_sha256":hashlib.sha256(arc).hexdigest(),
         "font_bin_sha256":hashlib.sha256(raw).hexdigest(),"original_glyphs":count,
         "free_font_table_padding_bytes":padding,
         "padding_remaining_after_19_plus_44_entries":padding-63*4,
         "free_atlas_cells_after_63_entries":3072-count-63,
         "pixels_written":0,"runtime_verified":False}

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--borrador",type=Path,default=Path("traduccion/CLADUN_BORRADOR_ES.csv"))
 p.add_argument("--iso-original",type=Path)
 a=p.parse_args()
 result=analyze(read_canonical(a.borrador))
 if a.iso_original:result["authenticated_font"]=audit_font(a.iso_original)
 print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=="__main__":main()
