"""Review-only fixed-width proposals. No canonical edits or binary writes."""
import csv
from pathlib import Path
try:
    from tools.charset_es import encode_spanish, decode_spanish
except ModuleNotFoundError:
    from charset_es import encode_spanish, decode_spanish

FIELDS=('grupo_id','offset_hex','longitud_original_bytes','propuesta_es','estado')
STATUS='PROPUESTA_REVISION_NO_CANONICA'

def read_proposals(path:Path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if tuple(reader.fieldnames or ())!=FIELDS:
            raise ValueError('Invalid proposal columns')
        rows=list(reader)
    if not rows:
        raise ValueError('Empty proposal set')
    return rows

def proposal_plan(rows,geometry,proposals):
    """Caller must first authenticate canonical draft and geometry with F3 anchor."""
    by_gid={r['grupo_id']:r for r in rows}
    slots={s['offset']:s for s in geometry['text_spans']}
    if len(by_gid)!=len(rows) or len(slots)!=len(geometry['text_spans']):
        raise ValueError('Duplicate canonical IDs or geometry offsets')
    result=[];seen=set();seen_offsets=set()
    for p in proposals:
        if set(p)!=set(FIELDS) or p['estado']!=STATUS:
            raise ValueError('Not a review-only proposal')
        gid=p['grupo_id'];r=by_gid.get(gid);at=int(p['offset_hex'],16);slot=slots.get(at)
        if (r is None or slot is None or gid in seen or at in seen_offsets or
            r['origen']!='SCRIPT.SDT/SCRIPT.DAT' or int(r['offset_hex'],16)!=at or
            int(r['script_id'])!=slot['script_id'] or int(r['orden_script'])!=slot['command_order']):
            raise ValueError('Proposal ID/offset/order mismatch or duplicate')
        old=bytes.fromhex(r['bytes_hex']);new=encode_spanish(p['propuesta_es']);draft=encode_spanish(r['espanol'])
        if (not old or any(b<32 or b>126 for b in old) or b'%' in old or b'\\' in old or
            not p['propuesta_es'] or p['propuesta_es']!=p['propuesta_es'].strip() or
            not p['propuesta_es'].isprintable() or '%' in p['propuesta_es'] or '\\' in p['propuesta_es'] or
            decode_spanish(new)!=p['propuesta_es']):
            raise ValueError('Unsupported source or proposal control/format characters')
        if (len(old)!=int(r['longitud_original_bytes']) or len(old)!=int(p['longitud_original_bytes']) or
            len(old)!=slot['source_length'] or len(new)!=len(old) or len(draft)==len(old) or new==old):
            raise ValueError('Proposal must replace a previously deferred exact-width slot')
        result.append({'offset':at,'old':old,'new':new,'gid':gid,'block':slot['block_index'],
                       'order':slot['command_order'],'script_id':slot['script_id']})
        seen.add(gid);seen_offsets.add(at)
    result.sort(key=lambda x:x['offset'])
    if not result or any(a['offset']+len(a['old'])>b['offset'] for a,b in zip(result,result[1:])):
        raise ValueError('Empty/overlapping proposal set')
    return result
