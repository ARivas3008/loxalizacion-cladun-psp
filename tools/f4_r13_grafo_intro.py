#!/usr/bin/env python3
"""CLADUN F4 R13: graph of static SCRIPT opcode 0A/0B/0C number matches.

Numeric matches do not demonstrate runtime control flow. Read-only, no assets.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import struct

OP_SIZES={0x0a:4,0x0b:5,0x0c:4}
INTRO_BLOCKS=set(range(757,764))
ORIGINAL_SHA='b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'

def analyze_static_links(commands, ids, names, starts):
    if not ids or len(ids)!=len(names) or len(starts)!=len(ids)+1:
        raise ValueError('Inconsistent SCRIPT.TBL')
    if len(set(ids))!=len(ids) or starts!=sorted(starts) or starts[0]!=0:
        raise ValueError('Duplicate IDs or invalid starts')
    index={v:i for i,v in enumerate(ids)}
    counts={op:Counter() for op in OP_SIZES}
    mapped_sources={op:set() for op in OP_SIZES}
    mapped_targets={op:set() for op in OP_SIZES}
    seen=set();selected=[]
    intro_with_0c=defaultdict(lambda:{'mapped':0,'operand_100':0})
    for c in commands:
        if not 0<=c.block<len(ids) or not starts[c.block]<=c.offset<starts[c.block+1]:
            raise ValueError('Command outside block')
        if c.offset in seen:raise ValueError('Duplicate command offset')
        seen.add(c.offset)
        if c.content is not None or c.code not in OP_SIZES:continue
        op=c.code;n=OP_SIZES[op]
        if len(c.raw)!=5+n or struct.unpack_from('<H',c.raw,3)[0]!=n:
            raise ValueError('Opcode payload size/header mismatch')
        val=struct.unpack_from('<I',c.raw,5)[0]
        shifted=index.get(val-100) if val>=100 else None
        literal=index.get(val)
        co=counts[op];co['total']+=1
        if shifted is None:
            co['unmatched']+=1
            co['unmatched_value_'+str(val)]+=1
        else:
            co['mapped']+=1
            if names[c.block]==names[shifted]:co['same_name']+=1
            if c.block==shifted:co['same_block']+=1
            mapped_sources[op].add(c.block);mapped_targets[op].add(shifted)
        if c.block in INTRO_BLOCKS and op==0x0c:
            if shifted is None and val==100:intro_with_0c[c.block]['operand_100']+=1
            elif shifted is not None:intro_with_0c[c.block]['mapped']+=1
        if c.block in INTRO_BLOCKS or (c.block==20 and c.order==20):
            selected.append({'source_block':c.block,'source_script_id':ids[c.block],
                'source_script_name':names[c.block],'source_order':c.order,
                'source_offset':c.offset,'opcode':f'0x{op:02X}','operand':val,
                'minus100_target_id':val-100 if shifted is not None else None,
                'minus100_target_block':shifted,'literal_target_block':literal})
    result={f'0x{op:02X}':{
        'total':counts[op]['total'],'minus100_id_matches':counts[op]['mapped'],
        'same_script_name_matches':counts[op]['same_name'],
        'same_block_matches':counts[op]['same_block'],
        'distinct_source_blocks_mapped':len(mapped_sources[op]),
        'distinct_target_blocks_mapped':len(mapped_targets[op]),
        'nonmatching_operands':{k.replace('unmatched_value_',''):v for k,v in sorted(counts[op].items()) if k.startswith('unmatched_value_')}
    } for op in OP_SIZES}
    return {'opcode_counts':result,'selected_intro_edges':selected,
        'intro_0c_mapped_and_value100':{str(k):v for k,v in sorted(intro_with_0c.items())},
        'runtime_MIPS_execution_proven':False,'event_relocation_permitted':False,
        'interpretation':'Only integer-derived candidate graph, not actual runtime flow or subroutine calls'}

def audit_original(iso):
    try:
        from tools.f3_referencias_riesgo import original_script_children
        from tools.script_event_guard import read_commands
    except ModuleNotFoundError:
        from f3_referencias_riesgo import original_script_children
        from script_event_guard import read_commands
    data,table=original_script_children(Path(iso))
    commands,starts=read_commands(data,table)
    if len(commands)!=51705 or len(starts)!=1626 or sum(x.content is None for x in commands)!=46308:
        raise ValueError('Incorrect genuine-ISO counts')
    ids=[struct.unpack_from('<I',table,16+32*i)[0] for i in range(1625)]
    names=[table[16+32*i+8:16+(i+1)*32].split(b'\x00',1)[0].decode('ascii','strict') for i in range(1625)]
    result=analyze_static_links(commands,ids,names,starts)
    expected={'0x0A':(862,860,86,0,515,278),
              '0x0B':(166,158,142,0,113,139),
              '0x0C':(102,66,64,0,63,61)}
    for op,tup in expected.items():
        row=result['opcode_counts'][op]
        got=tuple(row[k] for k in ('total','minus100_id_matches',
            'same_script_name_matches','same_block_matches',
            'distinct_source_blocks_mapped','distinct_target_blocks_mapped'))
        if got!=tup:raise ValueError(f'R13 genuine ISO graph mismatch {op}: {got}')
    links=[(20,20,'0x0A',100100,757),(757,2,'0x0A',100200,758),
           (758,1,'0x0C',100290,759),(758,416,'0x0A',100201,760),
           (760,1,'0x0C',100291,761)]
    observed={(x['source_block'],x['source_order'],x['opcode'],x['operand'],x['minus100_target_block']) for x in result['selected_intro_edges']}
    if any(link not in observed for link in links):raise ValueError('Intro chain mismatch')
    pairs=result['intro_0c_mapped_and_value100']
    if pairs.get('758')!={'mapped':1,'operand_100':1} or pairs.get('760')!={'mapped':1,'operand_100':1}:
        raise ValueError('Intro 0C pairing mismatch')
    return {'schema':'cladun.f4.r13_intro_static_link_graph.v1',
        'evidence':'A_AUTHENTIC_USA_ISO_STATIC_NOT_PPSSPP',
        'iso_sha256':ORIGINAL_SHA,
        'script_dat_sha256':'c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358',
        'script_tbl_sha256':'f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37',
        'script_blocks':1625,'commands':51705,'nontext_commands':46308,
        'required_intro_candidate_links':[{'source_block':b,'source_order':o,'opcode':op,
            'operand':v,'target_block_if_minus100':t} for b,o,op,v,t in links],
        **result,'ppsspp_executed':False,'original_iso_modified':False}

def main():
    try:from tools.f3_referencias_riesgo import report_path
    except ModuleNotFoundError:from f3_referencias_riesgo import report_path
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso-original',type=Path,required=True)
    p.add_argument('--reporte-privado',type=Path,required=True)
    args=p.parse_args();target=report_path(args.reporte_privado)
    result=audit_original(args.iso_original)
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open('x',encoding='utf-8') as f:
        json.dump(result,f,indent=2,ensure_ascii=False);f.write('\n')
    print(json.dumps({'checks':'OK','opcode_counts':result['opcode_counts'],
        'intro_required_candidates':len(result['required_intro_candidate_links']),
        'runtime_verified':False,'relocalization_authorized':False},ensure_ascii=False))
if __name__=='__main__':main()
