#!/usr/bin/env python3
"""Fail-closed Cladun PSP ISO resource isolation validator for TEXT edits.

Source and candidate must have identical ISO9660/PSPFS structure, filenames,
lengths and offsets. Only explicitly allowed *equal-length decoded text spans*
may differ. FONT.ARC must be verified in its own independent step.
This proves binary isolation, not game runtime, text layout or PPSSPP rendering.
"""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from extract_cladun import iso9660_entries,read_iso_file,pspfs_entries,decompress,dsarc_entries

BASE_SHA256='b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'

def require(ok,reason):
    if not ok:raise ValueError(reason)

def file_hash(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for piece in iter(lambda:f.read(1024*1024),b''):h.update(piece)
    return h.hexdigest()

def spans_from_args(specs):
    result={}
    for spec in specs:
        path,off,size=spec.rsplit(':',2)
        a,n=int(off,0),int(size,0)
        require(path and a>=0 and n>0,f'Invalid range: {spec}')
        require(path!='FONT.ARC' and not path.startswith('FONT.ARC/'), 'FONT.ARC requires font_es_guard.py')
        result.setdefault(path,[]).append((a,a+n))
    for path,spans in result.items():
        spans.sort()
        for (a,b),(c,d) in zip(spans,spans[1:]):
            require(b<=c,f'Overlapping ranges in {path}')
    require(result,'No authorized text range supplied')
    return result

def exact_except(a,b,spans,label):
    require(len(a)==len(b),f'Length changed: {label}')
    end=0;changed=0
    for lo,hi in sorted(spans):
        require(end<=lo<hi<=len(a),f'Invalid span: {label} [{lo},{hi})')
        require(a[end:lo]==b[end:lo],f'Unauthorized bytes before offset {lo} in {label}')
        changed+=sum(c!=d for c,d in zip(a[lo:hi],b[lo:hi]))
        end=hi
    require(a[end:]==b[end:],f'Unauthorized trailing bytes in {label}')
    return changed

def inspect(iso):
    _,entries=iso9660_entries(Path(iso))
    record=next((r for r in entries if r['path']=='PSP_GAME/USRDIR/DATA.DAT'),None)
    require(record is not None,'DATA.DAT not found')
    package=read_iso_file(Path(iso),record)
    table=pspfs_entries(package)
    require(len(table)==349,'Unexpected PSPFS count')
    return entries,record,package,table

def same_file_outside(source,candidate,lo,hi):
    with Path(source).open('rb') as fa,Path(candidate).open('rb') as fb:
        for start,end in ((0,lo),(hi,Path(source).stat().st_size)):
            fa.seek(start);fb.seek(start)
            while start<end:
                n=min(1024*1024,end-start)
                require(fa.read(n)==fb.read(n),'ISO bytes outside DATA.DAT changed')
                start+=n

def codec(source,expanded):
    if not expanded:return 'RAW'
    if source[12:14]==b'\x1f\x8b':return 'GZIP'
    return 'IMY'

def decoded(source,expanded):
    data,label=decompress(source,expanded)
    return data

def validate(source,candidate,allowed,expected_sha=BASE_SHA256):
    source,candidate=Path(source),Path(candidate)
    require(source.resolve()!=candidate.resolve(),'Cannot compare same ISO')
    require(source.stat().st_size==candidate.stat().st_size,'ISO length changed')
    actual=file_hash(source)
    require(actual==expected_sha,'Unrecognized source ISO SHA256')
    ea,da,a,ta=inspect(source)
    eb,db,b,tb=inspect(candidate)
    require(ea==eb and da==db,'ISO9660 offsets/sizes/paths changed')
    same_file_outside(source,candidate,da['offset'],da['offset']+da['size'])
    require(len(ta)==len(tb),'PSPFS number changed')
    require(ta==tb,'PSPFS table changed: name, length, or offset')
    names={x['name'] for x in ta}
    require(set(k.split('/')[0] for k in allowed)<=names,'Unknown PSPFS parent')
    changed_parents=[];modified_decoded=0;cursor=0
    authorized_parents={x.split('/')[0] for x in allowed}
    for e in sorted(ta,key=lambda x:x['offset']):
        name=e['name'];start=e['offset'];length=e['size_stored'];expanded=e['size_expanded']
        require(cursor<=start and start+length<=len(a),'PSPFS entries overlap or are outside DATA.DAT')
        require(a[cursor:start]==b[cursor:start],f'Archive index or padding changed before {name}')
        old=a[start:start+length];new=b[start:start+length]
        if name not in authorized_parents:
            require(old==new,f'Non-text resource was altered: {name}')
        else:
            require(codec(old,expanded)==codec(new,expanded),f'Codec changed in {name}')
            if old!=new:
                raw_old=decoded(old,expanded)
                raw_new=decoded(new,expanded)
                require(len(raw_old)==len(raw_new),'Decoded member length changed')
                kids_old=dsarc_entries(raw_old)
                kids_new=dsarc_entries(raw_new)
                if kids_old:
                    require([(x['name'],x['offset'],x['size']) for x in kids_old]==
                            [(x['name'],x['offset'],x['size']) for x in kids_new],
                            f'Nested DSARC table/offsets changed: {name}')
                    child_ranges=[]
                    for child in kids_old:
                        key=name+'/'+child['name']
                        q=child['offset'];t=q+child['size']
                        ranges=allowed.get(key,[])
                        if ranges:modified_decoded+=exact_except(raw_old[q:t],raw_new[q:t],ranges,key)
                        else:require(raw_old[q:t]==raw_new[q:t],f'Non-text DSARC member changed: {key}')
                        child_ranges.extend([(q+lo,q+hi) for lo,hi in ranges])
                    modified_parent=exact_except(raw_old,raw_new,child_ranges,name+' parent')
                    require(modified_parent>=1,'No declared byte difference')
                else:
                    require(name in allowed,f'Unspecified text child of {name}')
                    modified_decoded+=exact_except(raw_old,raw_new,allowed[name],name)
                changed_parents.append(name)
        cursor=start+length
    require(a[cursor:]==b[cursor:],'Trailing package padding changed')
    require(modified_decoded>0,'No decoded authorized bytes changed')
    return {'status':'PASS_TEXT_ISOLATION_ONLY','original_sha256':actual,
            'candidate_sha256':file_hash(candidate),'pspfs_entries_checked':len(ta),
            'resources_untouched':len(ta)-len(changed_parents),
            'edited_parents':changed_parents,'authorized_decoded_bytes_changed':modified_decoded,
            'pspfs_metadata_and_offsets_unchanged':True,'all_other_resources_byte_identical':True,
            'iso_size_and_layout_unchanged':True,'ppsspp_gameplay_tested':False,
            'spanish_translation_reinsertion_complete':False}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--original',type=Path,required=True)
    p.add_argument('--candidate',type=Path,required=True)
    p.add_argument('--sha256-original',default=BASE_SHA256)
    p.add_argument('--permit',action='append',required=True)
    p.add_argument('--report',type=Path)
    args=p.parse_args()
    try:out=validate(args.original,args.candidate,spans_from_args(args.permit),args.sha256_original)
    except Exception as e:out={'status':'REJECTED','reason':str(e)}
    data=json.dumps(out,ensure_ascii=False,indent=2)+'\n'
    print(data)
    if args.report:args.report.write_text(data,encoding='utf-8')
    return 0 if out['status'].startswith('PASS') else 1

if __name__=='__main__':raise SystemExit(main())
