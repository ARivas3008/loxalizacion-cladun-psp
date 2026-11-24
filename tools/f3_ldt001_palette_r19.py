"""R19: non-destructive 15xRGBA8888 candidate hypothesis, not GPU-confirmed."""
from collections import Counter
import argparse,json
from pathlib import Path
try:
 from tools.f3_anime_ldt_r18 import records,imy_extent
except ModuleNotFoundError:
 from f3_anime_ldt_r18 import records,imy_extent

def inspect_tail(tail):
 if len(tail) not in (60,62):raise ValueError('unexpected tail length')
 pad=tail[:-60]
 if any(pad):raise ValueError('nonzero alignment')
 quads=[tuple(tail[len(pad)+4*i:len(pad)+4*(i+1)]) for i in range(15)]
 return {'alignment_bytes':len(pad),'unique_rgba_quads':len(set(quads)),'nonzero_rgba_quads':sum(any(q) for q in quads),'alpha_histogram':dict(sorted(Counter(q[3] for q in quads).items()))}

def inspect_member(blob):
 rows=[]
 for ident,body in records(blob,2):
  size,tail=imy_extent(body)
  rows.append({'record_id':ident,'decoded_bytes':size,**inspect_tail(tail)})
 return {'hypothesis':'15 RGBA8888 candidates, NOT GE verified','records':len(rows),'alignment_2_bytes':sum(r['alignment_bytes']==2 for r in rows),'records_with_nonzero_quads':sum(r['nonzero_rgba_quads']>0 for r in rows),'palette_runtime_proven':False,'repacking_authorized':False,'per_record':rows}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--member-private',type=Path,required=True);a=p.parse_args();print(json.dumps(inspect_member(a.member_private.read_bytes()),indent=2))
