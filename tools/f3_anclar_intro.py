#!/usr/bin/env python3
"""F3-R5: unir los 97 textos demo1001 con la ISO original mediante SHA.

Lee ISO privada opcional y borrador CSV; publica SOLO métricas y hashes.
La deriva de offsets es hipotética: NO resuelve intérprete MIPS ni relocaliza.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path
import struct

try:
    from tools.charset_es import encode_spanish, decode_spanish
    from tools.f3_referencias_riesgo import original_script_children
    from tools.script_event_guard import read_commands
except ModuleNotFoundError:
    from charset_es import encode_spanish, decode_spanish
    from f3_referencias_riesgo import original_script_children
    from script_event_guard import read_commands

DOMAIN = b'CLADUN:F3:DEMO1001:SOURCE_AND_ORDER:v2\0'
ANCHOR_SHA256 = 'b0d42d8cd871246addf08a54e02c2a84cda52cab39f5810ef5ba2d9173e3e34e'
ISO_SHA256 = 'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
DRAFT_BLOB_SHA1 = '400a9c9ec06f7456b5ec6e11f7502d711b0a976e'
SCRIPT_FILES = {'demo1001_00.dsf', 'demo1001_01.dsf'}
SCRIPT_IDS = {
    100000:'demo1001_00.dsf',100100:'demo1001_00.dsf',100190:'demo1001_00.dsf',
    100101:'demo1001_01.dsf',100191:'demo1001_01.dsf',
    100110:'demo1001_01.dsf',100120:'demo1001_01.dsf',
}
TEXT_OPS = frozenset((0x66,0x69,0x6e))
GEOMETRY_REL = Path('reports/F3_DEMO1001_GEOMETRIA_ORIGINAL_2026-11-23.json')
DRAFT_REL = Path('traduccion/CLADUN_BORRADOR_ES.csv')


def git_blob_hash(raw: bytes) -> str:
    return hashlib.sha1(f'blob {len(raw)}\0'.encode('ascii')+raw).hexdigest()


def anchor_hash(spans: list[tuple[dict, bytes]]) -> str:
    h=hashlib.sha256();h.update(DOMAIN)
    seen=set()
    for span,original in sorted(spans,key=lambda p:p[0]['offset']):
        off,sid,block,order=(span[k] for k in ('offset','script_id','block_index','command_order'))
        if not all(isinstance(z,int) and z>=0 for z in (off,sid,block,order)) or off in seen:
            raise ValueError('Offsets duplicados o metadatos corruptos')
        seen.add(off)
        if len(original)>65535:raise ValueError('Longitud original fuera de rango')
        h.update(struct.pack('<IIHHH',off,sid,block,order,len(original)))
        h.update(original)
    return h.hexdigest()


def check_geometry(manifest:dict,*,require_canonical:bool=True)->dict:
    if manifest.get('schema')!='cladun.f3.intro_source_geometry.v2':
        raise ValueError('Esquema de geometría incorrecto')
    blocks=manifest['blocks'];text=manifest['text_spans']
    if len({r['block_index'] for r in blocks})!=len(blocks):
        raise ValueError('Bloques duplicados')
    blockmap={r['block_index']:r for r in blocks}
    if len({(r['block_index'],r['command_order']) for r in text})!=len(text):
        raise ValueError('Órdenes de texto duplicados')
    if len({r['offset'] for r in text})!=len(text):
        raise ValueError('Offsets de texto duplicados')
    if sorted(x['offset'] for x in text)!=[x['offset'] for x in text]:
        raise ValueError('Offsets no ordenados')
    for s in text:
        b=blockmap.get(s['block_index'])
        if (not b or s['script_id']!=b['script_id'] or s['script_file']!=b['name']
            or s['following_commands']!=b['command_count']-s['command_order']-1
            or not 0<=s['command_order']<b['command_count'] or s['source_length']<1):
            raise ValueError('Texto no corresponde a geometría de su script')
    if require_canonical:
        if (manifest.get('original_iso_sha256')!=ISO_SHA256 or
            manifest.get('source_and_order_sha256')!=ANCHOR_SHA256 or
            len(blocks)!=7 or sum(b['command_count'] for b in blocks)!=878 or
            len(text)!=97 or sum(s['source_length'] for s in text)!=2728 or
            {b['script_id']:b['name'] for b in blocks}!=SCRIPT_IDS):
            raise ValueError('Geometría diferente de la ISO auténtica')
    return blockmap


def load_geometry(path:Path)->dict:
    """Expandir metadatos públicos compactos sin texto comercial."""
    compact=json.loads(path.read_text(encoding='utf-8'))
    if compact.get('schema')!='cladun.f3.intro_source_geometry_compact.v3':
        raise ValueError('Geometría compacta v3 requerida')
    blocks=[{'block_index':x[0],'script_id':x[1],'name':x[2],
             'command_count':x[3],'source_start':x[4],'source_end':x[5]}
            for x in compact['blocks']]
    byblock={b['block_index']:b for b in blocks}
    spans=[]
    for off,b,order,length in compact['spans']:
        block=byblock.get(b)
        if block is None:raise ValueError('El texto refiere un bloque ausente')
        spans.append({'offset':off,'script_id':block['script_id'],
                      'script_file':block['name'],'block_index':b,'command_order':order,
                      'source_length':length,
                      'following_commands':block['command_count']-order-1})
    manifest={'schema':'cladun.f3.intro_source_geometry.v2',
              'original_iso_sha256':compact['original_iso_sha256'],
              'source_and_order_sha256':compact['anchor_sha256'],
              'blocks':blocks,'text_spans':spans}
    check_geometry(manifest)
    return manifest


def iso_source_spans(iso:Path):
    """Solo ISO autenticada por parser preexistente: no exporta bytes."""
    script,table=original_script_children(iso)
    commands,starts=read_commands(script,table)
    if len(commands)!=51705 or len(starts)!=1626:
        raise ValueError('SCRIPT.DAT original inesperado')
    ids=[struct.unpack_from('<I',table,16+32*i)[0] for i in range(1625)]
    names=[table[16+i*32+8:16+i*32+32].split(b'\0',1)[0].decode('ascii','strict') for i in range(1625)]
    byblock=defaultdict(list)
    for c in commands:byblock[c.block].append(c)
    blocks=[];spans=[]
    for i,name in enumerate(names):
        if name not in SCRIPT_FILES:continue
        if SCRIPT_IDS.get(ids[i])!=name:raise ValueError('Script demo1001 inesperado')
        sequence=byblock[i]
        blocks.append({'block_index':i,'script_id':ids[i],'name':name,'command_count':len(sequence),
                       'source_start':starts[i],'source_end':starts[i+1]})
        for c in sequence:
            if c.code not in TEXT_OPS or not c.content:continue
            spans.append(({'offset':c.offset+7,'script_id':ids[i],'script_file':name,
                           'block_index':i,'command_order':c.order,
                           'source_length':len(c.content),
                           'following_commands':len(sequence)-c.order-1},c.content))
    spans.sort(key=lambda z:z[0]['offset'])
    if len(spans)!=97 or len(blocks)!=7:raise ValueError('Conteo demo1001 incorrecto')
    return blocks,spans


def verify_original_iso(iso:Path,manifest:dict)->dict:
    check_geometry(manifest)
    blocks,spans=iso_source_spans(iso)
    if blocks!=manifest['blocks'] or [z[0] for z in spans]!=manifest['text_spans']:
        raise ValueError('Geometría no coincide con ISO original')
    root=anchor_hash(spans)
    if root!=ANCHOR_SHA256:raise ValueError('Raíz de bytes fuente/orden incorrecta')
    return {'original_iso_authenticated':True,'source_span_root_matches':True,
            'original_source_and_order_sha256':root,'source_strings':97,
            'source_text_bytes':sum(len(z[1]) for z in spans)}


def evaluate_rows(rows:list[dict],manifest:dict,*,canonical:bool=True)->dict:
    blockmap=check_geometry(manifest,require_canonical=canonical)
    if canonical and len(rows)!=9237:
        raise ValueError('Borrador no tiene las 9.237 filas originales')
    selected=[r for r in rows if r.get('script') in SCRIPT_FILES]
    geo=manifest['text_spans'];by_offset={s['offset']:s for s in geo}
    if len(selected)!=len(geo):raise ValueError('Número de filas demo1001 no coincide')
    seen=set();translated={};raw_spans=[];stats=Counter();groups=defaultdict(Counter)
    for row in selected:
        if row.get('origen')!='SCRIPT.SDT/SCRIPT.DAT':
            raise ValueError('Origen intro incorrecto')
        off=int(row['offset_hex'],16)
        if off in seen or off not in by_offset:
            raise ValueError('Offset repetido o ausente de geometría original')
        seen.add(off);g=by_offset[off]
        src=bytes.fromhex(row['bytes_hex']);sid=int(row['script_id'])
        if (sid!=g['script_id'] or row['script']!=g['script_file'] or
            int(row['longitud_original_bytes'])!=len(src) or len(src)!=g['source_length'] or
            src.decode('cp932','strict')!=row['original']):
            raise ValueError('Identidad o bytes originales cambiados')
        if not row['espanol']:raise ValueError('Texto español sin traducir')
        dest=encode_spanish(row['espanol'])
        if decode_spanish(dest)!=row['espanol']:
            raise ValueError('Español sin roundtrip CP932 A1-B3')
        translated[off]=len(dest)-len(src)
        raw_spans.append((g,src))
        label=('unequal' if dest!=src and len(dest)!=len(src) else
               'same_length_changed' if dest!=src else 'unchanged')
        stats[label]+=1;groups[sid][label]+=1
    if seen!=set(by_offset):raise ValueError('Faltan registros fuente intro')
    root=anchor_hash(raw_spans)
    if root!=manifest['source_and_order_sha256']:
        raise ValueError('Raíz SHA original ISO no coincide con borrador GitHub')
    if canonical and (root!=ANCHOR_SHA256 or sum(len(src) for _,src in raw_spans)!=2728 or
        sum(len(src)+translated[g['offset']] for g,src in raw_spans)!=2859 or
        dict(stats)!={'unequal':85,'same_length_changed':11,'unchanged':1}):
        raise ValueError('Clasificación/español canónico cambió')
    projected=[]
    for block_index,block in sorted(blockmap.items()):
        changes={s['command_order']:translated[s['offset']]
                 for s in geo if s['block_index']==block_index}
        running=0;shifted=0;largest=0;sum_abs_shifts=0
        for order in range(block['command_count']):
            if running:
                shifted+=1
                largest=max(largest,abs(running))
                sum_abs_shifts+=abs(running)
            running+=changes.get(order,0)
        nonzero=[v for v in changes.values() if v]
        projected.append({'script_id':block['script_id'],'script_name':block['name'],
                          'source_commands':block['command_count'],
                          'translated_rows':len(changes),'changed_length_rows':len(nonzero),
                          'sum_positive_bytes':sum(v for v in nonzero if v>0),
                          'sum_negative_bytes':sum(v for v in nonzero if v<0),
                          'net_text_byte_delta':running,
                          'hypothetical_commands_with_changed_start':shifted,
                          'hypothetical_max_absolute_start_shift':largest,
                          'hypothetical_sum_absolute_shifts':sum_abs_shifts})
    return {'source_root_sha256':root,
        'source_and_order_authenticated_against_iso_manifest':canonical,
        'total_draft_rows':len(rows),'intro_rows':len(selected),
        'source_bytes':sum(len(src) for _,src in raw_spans),
        'spanish_bytes':sum(len(src)+translated[g['offset']] for g,src in raw_spans),
        'change_counts':dict(sorted(stats.items())),
        'by_script_id':{str(k):dict(v) for k,v in sorted(groups.items())},
        'simple_concat_projection':projected,
        'simulation_ignores_padding_and_control_flow':True,
        'mips_jumps_resolved':False,'relocation_authorized':False,
        'preserve_event_safe_only':True}


def read_draft(path:Path)->tuple[list[dict],str]:
    raw=path.read_bytes()
    with path.open('r',encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        expected={'grupo_id','origen','script','script_id','offset_hex','bytes_hex',
                  'longitud_original_bytes','espanol','original'}
        if not reader.fieldnames or not expected.issubset(reader.fieldnames):
            raise ValueError('Borrador CSV sin columnas canónicas')
        rows=list(reader)
    return rows,git_blob_hash(raw)


def audit(draft:Path,geometry:Path,iso:Path|None=None)->dict:
    manifest=load_geometry(geometry)
    rows,blob=read_draft(draft)
    if blob!=DRAFT_BLOB_SHA1:raise ValueError('SHA blob borrador canónico cambió')
    result=evaluate_rows(rows,manifest)
    iso_result=verify_original_iso(iso,manifest) if iso is not None else None
    return {'schema':'cladun.f3.intro_iso_to_draft_anchor.v2',
            'evidence':'A_ISO_ORIGINAL_ANCHOR_B_GITHUB_DRAFT_CHECK_NOT_C_PPSSPP',
            'draft_git_blob_sha1':blob,'original_iso_sha256':ISO_SHA256,
            'original_iso_reverified_during_this_call':iso_result is not None,
            'iso_validation':iso_result,**result,
            'binary_or_game_assets_modified':False,'runtime_ppsspp_executed':False}


def main()->None:
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--borrador-es',type=Path,default=DRAFT_REL)
    p.add_argument('--geometria',type=Path,default=GEOMETRY_REL)
    p.add_argument('--iso-original',type=Path)
    p.add_argument('--reporte-privado',type=Path)
    args=p.parse_args()
    result=audit(args.borrador_es,args.geometria,args.iso_original)
    if args.reporte_privado:
        try:
            from tools.f3_referencias_riesgo import report_path
        except ModuleNotFoundError:
            from f3_referencias_riesgo import report_path
        path=report_path(args.reporte_privado)
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open('x',encoding='utf-8') as out:
            json.dump(result,out,indent=2,ensure_ascii=False);out.write('\n')
    print(json.dumps({'draft_sha1_verified':True,
                      'original_iso_verified_here':args.iso_original is not None,
                      'anchor_matches':True,'intro_rows':result['intro_rows'],
                      'blocked_changed_length':result['change_counts']['unequal'],
                      'projected_block_shift':[(r['script_id'],r['net_text_byte_delta'],
                                               r['hypothetical_commands_with_changed_start'])
                                              for r in result['simple_concat_projection']],
                      'relocation_authorized':False},ensure_ascii=False))


if __name__=='__main__':main()
