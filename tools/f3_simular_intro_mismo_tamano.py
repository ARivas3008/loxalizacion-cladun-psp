#!/usr/bin/env python3
"""F3: simulación RAM-ONLY de 11 textos demo1001 de tamaño IDÉNTICO.

NUNCA exporta SCRIPT.DAT modificado ni escribe ISO. La simulación estática
no demuestra saltos MIPS ni autoriza inserción, BPS o traducción final.
"""
from __future__ import annotations
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path

try:
    from tools import f3_anclar_intro as anchor
    from tools.charset_es import encode_spanish
    from tools.script_event_guard import read_commands, audit_script_rebuild
    from tools.f3_referencias_riesgo import original_script_children, report_path
except ModuleNotFoundError:
    import f3_anclar_intro as anchor
    from charset_es import encode_spanish
    from script_event_guard import read_commands, audit_script_rebuild
    from f3_referencias_riesgo import original_script_children, report_path


def prepare_plan(rows:list[dict],geometry:dict,*,canonical:bool=True)->tuple[list[dict],dict]:
    """Require original-byte anchor and translations BEFORE picking any edit."""
    score=anchor.evaluate_rows(rows,geometry,canonical=canonical)
    slots={s['offset']:s for s in geometry['text_spans']}
    plan=[]
    all_offsets=set()
    for row in rows:
        if row.get('script') not in anchor.SCRIPT_FILES:
            continue
        offset=int(row['offset_hex'],16)
        slot=slots[offset]
        old=bytes.fromhex(row['bytes_hex'])
        new=encode_spanish(row['espanol'])
        if offset in all_offsets:
            raise ValueError('Repeated original text offset')
        all_offsets.add(offset)
        if len(new)==len(old) and new!=old:
            plan.append({'offset':offset,'old':old,'new':new,'gid':row['grupo_id'],
                         'block':slot['block_index'],'order':slot['command_order'],
                         'script_id':slot['script_id']})
    plan.sort(key=lambda z:z['offset'])
    if canonical and (len(plan)!=11 or len(all_offsets)!=97 or
                      score['change_counts']!={'unequal':85,'same_length_changed':11,'unchanged':1}):
        raise ValueError('Not the certified 11/85/1 intro candidate set')
    for i,candidate in enumerate(plan):
        if not candidate['old'] or len(candidate['old'])!=len(candidate['new']):
            raise ValueError('Invalid same-size replacement')
        if i and plan[i-1]['offset']+len(plan[i-1]['old'])>candidate['offset']:
            raise ValueError('Overlapping text spans')
    return plan,score


def simulate_memory_only(source:bytes,table:bytes,geometry:dict,plan:list[dict],
                         *,expected_commands:int=51705)->dict:
    """Read and write only Python bytes, fully reparse; return metrics/hash ONLY."""
    commands,starts=read_commands(source,table)
    if len(commands)!=expected_commands:
        raise ValueError('Unexpected original command count')
    content={cmd.offset+7:cmd for cmd in commands if cmd.content is not None}
    source_pairs=[]
    for slot in geometry['text_spans']:
        cmd=content.get(slot['offset'])
        if (cmd is None or not cmd.content or cmd.block!=slot['block_index'] or
            cmd.order!=slot['command_order'] or len(cmd.content)!=slot['source_length']):
            raise ValueError('Original script no longer matches certified text geometry')
        source_pairs.append((slot,cmd.content))
    original_anchor=anchor.anchor_hash(source_pairs)
    if original_anchor!=geometry['source_and_order_sha256']:
        raise ValueError('Original ISO SCRIPT bytes/position root changed')
    if len({x['offset'] for x in plan})!=len(plan):
        raise ValueError('Duplicate candidate location')
    if len(plan)>len(source_pairs):
        raise ValueError('More candidate edits than original text')
    memory=bytearray(source)
    expected={}
    byid=Counter()
    changed_bytes=0
    for edit in plan:
        at,old,new=edit['offset'],edit['old'],edit['new']
        cmd=content.get(at)
        if (not old or old==new or len(old)!=len(new) or
            cmd is None or cmd.content!=old or
            (cmd.block,cmd.order)!=(edit['block'],edit['order']) or
            memory[at:at+len(old)]!=old):
            raise ValueError('Invalid candidate, changed source, or unsupported text command')
        memory[at:at+len(new)]=new
        expected[at]=(old,new,str(edit['gid']))
        byid[str(edit['script_id'])]+=1
        changed_bytes+=sum(a!=b for a,b in zip(old,new))
    updated=bytes(memory)
    guard=audit_script_rebuild(source,table,updated,table,expected,
                               require_fixed_offsets=True)
    if (guard['total_commands']!=expected_commands or
        guard['text_commands_replaced']!=len(plan) or
        guard['moved_command_offsets'] or guard['moved_script_starts'] or
        guard['nontext_payload_changes'] or not guard['all_command_offsets_preserved']):
        raise AssertionError('Structural security invariant not satisfied')
    return {'schema':'cladun.f3.demo1001_11_same_length_memory_simulation.v1',
            'scope':'RAM_ONLY_SCRIPT_DAT_NOT_ISO_NOT_PPSSPP',
            'original_anchor_sha256':original_anchor,
            'original_script_dat_sha256':hashlib.sha256(source).hexdigest(),
            'virtual_script_dat_sha256_NOT_A_FILE':hashlib.sha256(updated).hexdigest(),
            'original_script_tbl_sha256':hashlib.sha256(table).hexdigest(),
            'original_bytes':len(source),'virtual_bytes':len(updated),
            'equal_length_text_candidates_simulated':len(plan),
            'changed_payload_bytes':changed_bytes,
            'per_script_id_simulated':dict(sorted(byid.items())),
            'original_commands_reparsed':guard['total_commands'],
            'original_script_blocks':guard['total_script_blocks'],
            'nontext_commands_byte_exact':guard['nontext_commands_byte_exact'],
            'all_command_offsets_preserved':guard['all_command_offsets_preserved'],
            'moved_command_offsets':0,'moved_script_starts':0,
            'unmodified_other_intro_text_fields':len(source_pairs)-len(plan),
            'original_and_virtual_script_table_identical':True,
            'source_game_file_written':False,
            'new_ISO_created':False,
            'relocation_authorized':False,
            'MIPS_jumps_and_external_references_verified':False,
            'PPSSPP_executed':False,'integration_authorized':False}


def audit(draft:Path,geometry_path:Path,iso:Path|None=None)->dict:
    geometry=anchor.load_geometry(geometry_path)
    rows,blob=anchor.read_draft(draft)
    if blob!=anchor.DRAFT_BLOB_SHA1:
        raise ValueError('Authentic 9237-row Git draft blob SHA changed')
    plan,score=prepare_plan(rows,geometry)
    summary={'schema':'cladun.f3.demo1001_11_same_length_plan.v1',
             'source_draft_blob_sha1':blob,
             'original_iso_source_anchor_sha256':score['source_root_sha256'],
             'intro_original_text_rows':score['intro_rows'],
             'same_length_candidates':len(plan),
             'changed_length_blocked':score['change_counts']['unequal'],
             'unchanged_intro_fields':score['change_counts']['unchanged'],
             'iso_original_reverified_this_call':iso is not None,
             'script_in_memory_simulation_executed':iso is not None,
             'game_asset_written':False,'event_safe_only_still_required':True,
             'runtime_PPSSPP_verified':False,'gameplay_pass_proven':False,
             'deployment_authorized':False}
    if iso is None:
        return summary
    data,table=original_script_children(Path(iso))
    result=simulate_memory_only(data,table,geometry,plan)
    if result['equal_length_text_candidates_simulated']!=11:
        raise ValueError('Wrong number of same-size intro edits')
    summary['simulation']=result
    return summary


def audit_proposals(draft:Path,geometry_path:Path,proposals:Path,iso:Path|None=None)->dict:
    """Authenticate the canonical draft and test proposals separately; never deploy."""
    try:
        from tools.f3_propuestas_longitud_fija import proposal_plan, read_proposals
    except ModuleNotFoundError:
        from f3_propuestas_longitud_fija import proposal_plan, read_proposals
    geometry=anchor.load_geometry(geometry_path)
    rows,blob=anchor.read_draft(draft)
    if blob!=anchor.DRAFT_BLOB_SHA1:
        raise ValueError('Authentic 9237-row Git draft blob SHA changed')
    _,score=prepare_plan(rows,geometry)
    plan=proposal_plan(rows,geometry,read_proposals(proposals))
    summary={'schema':'cladun.f3.review_proposals_plan.v1',
             'source_draft_blob_sha1':blob,'same_length_candidates':len(plan),
             'canonical_blocked_different_length':score['change_counts']['unequal'],
             'changed_length_blocked':score['change_counts']['unequal']-len(plan),
             'remaining_count_is_hypothetical':True,
             'canonical_draft_modified':False,
             'iso_original_reverified_this_call':iso is not None,
             'script_in_memory_simulation_executed':iso is not None,
             'game_asset_written':False,'event_safe_only_still_required':True,
             'runtime_PPSSPP_verified':False,'gameplay_pass_proven':False,
             'deployment_authorized':False}
    if iso is not None:
        data,table=original_script_children(Path(iso))
        result=simulate_memory_only(data,table,geometry,plan)
        result['schema']='cladun.f3.review_proposals_memory_simulation.v1'
        summary['simulation']=result
    return summary


def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--borrador-es',type=Path,default=anchor.DRAFT_REL)
    p.add_argument('--geometria',type=Path,default=anchor.GEOMETRY_REL)
    p.add_argument('--iso-original',type=Path,
                   help='Optional exact SHA original USA. Without ISO only checks Git draft.')
    p.add_argument('--reporte-privado',type=Path,
                   help='New absolute JSON outside all Git worktrees (no commercial payload)')
    p.add_argument('--propuestas',type=Path,help='Review-only CSV; no canonical changes or deployment')
    args=p.parse_args()
    out=(audit_proposals(args.borrador_es,args.geometria,args.propuestas,args.iso_original)
         if args.propuestas is not None else audit(args.borrador_es,args.geometria,args.iso_original))
    if args.reporte_privado is not None:
        path=report_path(args.reporte_privado)
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('x',encoding='utf-8') as f:
            json.dump(out,f,ensure_ascii=False,indent=2);f.write('\n')
    print(json.dumps({'same_length_candidates':out['same_length_candidates'],
                      'blocked_different_length':out['changed_length_blocked'],
                      'original_iso_checked_here':out['iso_original_reverified_this_call'],
                      'memory_simulation_done':out['script_in_memory_simulation_executed'],
                      'all_offsets_preserved':out.get('simulation',{}).get('all_command_offsets_preserved'),
                      'deployment_authorized':False,
                      'PPSSPP_verified':False},ensure_ascii=False))


if __name__=='__main__':main()
