"""R18: validate a review-only global fixed-width overlay; no binary writes."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import struct
try:
    from tools.f3_anclar_intro import read_draft,DRAFT_BLOB_SHA1,DRAFT_REL
    from tools.f3_propuestas_longitud_fija import proposal_plan,read_proposals
    from tools.script_event_guard import read_commands,audit_script_rebuild
except ModuleNotFoundError:
    from f3_anclar_intro import read_draft,DRAFT_BLOB_SHA1,DRAFT_REL
    from f3_propuestas_longitud_fija import proposal_plan,read_proposals
    from script_event_guard import read_commands,audit_script_rebuild

OVERLAY=Path('traduccion/propuestas/SCRIPT_LONGITUD_FIJA_R18.csv')
SCRIPT_SHA='c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358'
TABLE_SHA='f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37'

def draft_geometry(rows):
    spans=[]
    for r in rows:
        if r['origen']!='SCRIPT.SDT/SCRIPT.DAT':continue
        spans.append({'offset':int(r['offset_hex'],16),'script_id':int(r['script_id']),
                      'command_order':int(r['orden_script']),'block_index':int(r['indice_registro']),
                      'source_length':int(r['longitud_original_bytes'])})
    return {'text_spans':spans}

def iso_geometry(data,table):
    if hashlib.sha256(data).hexdigest()!=SCRIPT_SHA or hashlib.sha256(table).hexdigest()!=TABLE_SHA:
        raise ValueError('Original SCRIPT hashes differ')
    commands,starts=read_commands(data,table)
    if len(commands)!=51705 or len(starts)!=1626 or sum(c.content is None for c in commands)!=46308:
        raise ValueError('Original SCRIPT counts differ')
    return {'text_spans':[{'offset':c.offset+7,'script_id':struct.unpack_from('<I',table,16+32*c.block)[0],
                          'command_order':c.order,'block_index':c.block,'source_length':len(c.content)}
                         for c in commands if c.content is not None]},commands

def simulate(data,table,rows,proposals):
    geometry,commands=iso_geometry(data,table)
    plan=proposal_plan(rows,geometry,proposals)
    by_offset={c.offset+7:c for c in commands if c.content is not None}
    virtual=bytearray(data);expected={};changed=0
    for e in plan:
        at,old,new=e['offset'],e['old'],e['new']
        if by_offset[at].content!=old:raise ValueError('Source payload differs')
        virtual[at:at+len(old)]=new;expected[at]=(old,new,e['gid']);changed+=sum(x!=y for x,y in zip(old,new))
    result=audit_script_rebuild(data,table,bytes(virtual),table,expected,require_fixed_offsets=True)
    if not result['all_command_offsets_preserved'] or result['nontext_commands_byte_exact']!=46308:
        raise ValueError('Event guard refused overlay')
    return {'overlay_count':len(plan),'changed_bytes':changed,'payload_bytes':sum(len(e['new']) for e in plan),
            'virtual_script_sha256':hashlib.sha256(virtual).hexdigest(),'all_command_offsets_preserved':True,
            'nontext_commands_byte_exact':46308,'commands_reparsed':51705,'deployment_authorized':False,'PPSSPP_executed':False}

def audit(draft,overlay,iso=None):
    rows,sha=read_draft(draft)
    if sha!=DRAFT_BLOB_SHA1 or len(rows)!=9237:raise ValueError('Canonical draft hash or count differs')
    proposals=read_proposals(overlay)
    # CI-only geometry is from authenticated Git draft, not direct ISO evidence.
    plan=proposal_plan(rows,draft_geometry(rows),proposals)
    result={'schema':'cladun.r18.overlay_review_only.v1','canonical_draft_sha1':sha,
            'overlay_count':len(plan),'payload_bytes':sum(len(e['new']) for e in plan),
            'scope':'B_CANONICAL_GIT_PLAN_ONLY','canonical_modified':False,'deployment_authorized':False}
    if iso is not None:
        try:from tools.f3_referencias_riesgo import original_script_children
        except ModuleNotFoundError:from f3_referencias_riesgo import original_script_children
        data,table=original_script_children(iso)
        result.update(simulate(data,table,rows,proposals),scope='A_ORIGINAL_STATIC_MEMORY_ONLY_NOT_C')
    return result

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--borrador',type=Path,default=DRAFT_REL)
    p.add_argument('--propuestas',type=Path,default=OVERLAY);p.add_argument('--iso-original',type=Path)
    a=p.parse_args();print(json.dumps(audit(a.borrador,a.propuestas,a.iso_original),indent=2))
