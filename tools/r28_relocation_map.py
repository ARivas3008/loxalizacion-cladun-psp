#!/usr/bin/env python3
"""R28: deterministic old/new command coordinates, never infer MIPS semantics.

Only private authentic ISO and canonical CSV. No game bytes are exported.
A matching integer in a payload is not a validated pointer.
"""
from __future__ import annotations
import argparse
from collections import Counter
import json
from pathlib import Path
import struct
try:
    from tools.f3_referencias_riesgo import original_script_children, file_sha256, USA_SHA, report_path
    from tools.r26_auditar_reubicacion_eventos_total import canonical_plan, analyze_moving_offsets
    from tools.integrar_parche_seguro import text_command_rebuild
    from tools.script_event_guard import read_commands
except ModuleNotFoundError:
    from f3_referencias_riesgo import original_script_children, file_sha256, USA_SHA, report_path
    from r26_auditar_reubicacion_eventos_total import canonical_plan, analyze_moving_offsets
    from integrar_parche_seguro import text_command_rebuild
    from script_event_guard import read_commands

PRIORITY = frozenset((435,1415,796,1235,1239,1393,1237,437,815,1025,
    1240,790,901,1236,836,865,909,1226,1257,788,966,1078,1134,1238,
    751,797,947,1051,1193))

def require(ok, message):
    if not ok:
        raise ValueError(message)

def relocation_map(before, after):
    """Identity is (block, order), with opcode and instruction ID as checks."""
    require(len(before) == len(after), "Command count mismatch")
    entries = []
    seen_old, seen_new, seen_key = set(), set(), set()
    for a, b in zip(before, after):
        key = (a.block, a.order)
        require((a.block, a.order, a.code, a.instruction_id) ==
                (b.block, b.order, b.code, b.instruction_id),
                "Command identity/order mismatch")
        require(key not in seen_key and a.offset not in seen_old and
                b.offset not in seen_new, "Non-bijective relocation")
        require((a.content is None) == (b.content is None),
                "Command text classification mismatch")
        if a.content is None:
            require(a.raw == b.raw, "Nontext mutation")
        seen_key.add(key)
        seen_old.add(a.offset)
        seen_new.add(b.offset)
        entries.append({"block": a.block, "order": a.order, "opcode": a.code,
            "instruction_id": a.instruction_id, "old_offset": a.offset,
            "new_offset": b.offset, "old_size": len(a.raw), "new_size": len(b.raw),
            "text": a.content is not None})
    require(all(a["old_offset"] < b["old_offset"] and a["new_offset"] < b["new_offset"]
                for a,b in zip(entries, entries[1:])), "Unordered offsets")
    return entries

def reference_triage(commands, entries, old_starts, new_starts, script_ids, priority=PRIORITY):
    """Sliding u32 windows; report coincidences only; never rewrite operands."""
    require(len(commands) == len(entries), "Geometry inventory mismatch")
    require(len(old_starts) == len(new_starts) == len(script_ids)+1,
            "Block boundary mismatch")
    require(len(set(script_ids)) == len(script_ids), "Ambiguous SCRIPT.TBL IDs")
    rel = {e["old_offset"]: e["new_offset"] for e in entries}
    require(len(rel) == len(entries), "Duplicate old coordinates")
    id_to_block = {v:i for i,v in enumerate(script_ids)}
    abs_hits=rel_hits=abs_changed=rel_changed=0
    priority_hits, by_opcode = Counter(), Counter()
    for cmd in commands:
        if cmd.content is not None:
            continue
        payload=cmd.raw[5:]
        for pos in range(max(0,len(payload)-3)):
            v=struct.unpack_from("<I",payload,pos)[0]
            if not v:
                continue
            if v in rel:
                abs_hits += 1
                abs_changed += rel[v] != v
            target=old_starts[cmd.block]+v
            if target < old_starts[cmd.block+1] and target in rel:
                rel_hits += 1
                rel_changed += rel[target]-new_starts[cmd.block] != v
        if cmd.code in (10,11,12) and len(payload)>=4:
            target=id_to_block.get(struct.unpack_from("<I",payload)[0]-100)
            if target in priority:
                priority_hits[target]+=1
                by_opcode[cmd.code]+=1
    return {"u32_absolute_numeric_matches":abs_hits,
        "u32_absolute_matches_target_moves":abs_changed,
        "u32_relative_numeric_matches":rel_hits,
        "u32_relative_matches_target_moves":rel_changed,
        "priority_blocks_with_candidate_incoming":len(priority_hits),
        "priority_incoming_candidates":sum(priority_hits.values()),
        "priority_incoming_by_opcode":dict(sorted(by_opcode.items())),
        "priority_incoming_by_block":dict(sorted(priority_hits.items())),
        "semantic_references_proven":False}

def identity_collisions(commands):
    pairs=Counter((c.block,c.instruction_id) for c in commands)
    triples=Counter((c.block,c.code,c.instruction_id) for c in commands)
    return {"duplicate_instruction_ids_within_block_excess":sum(v-1 for v in pairs.values()),
        "blocks_with_duplicate_ids":len({b for (b,_),v in pairs.items() if v>1}),
        "duplicate_block_opcode_instruction_id_excess":sum(v-1 for v in triples.values())}

def audit(iso):
    plan, _ = canonical_plan()
    data, table = original_script_children(iso)
    candidate, candidate_table = text_command_rebuild(data,table,plan)
    guard = analyze_moving_offsets(data,table,candidate,candidate_table,plan)
    before, old_starts=read_commands(data,table)
    after, new_starts=read_commands(candidate,candidate_table)
    entries=relocation_map(before,after)
    require(len(entries)==51705,"Unexpected command inventory")
    ids=[struct.unpack_from("<I",table,16+32*i)[0] for i in range(len(old_starts)-1)]
    moved=[e for e in entries if e["old_offset"]!=e["new_offset"]]
    stats={"commands":len(entries),"moved_commands":len(moved),
        "moved_nontext":sum(not e["text"] for e in moved),
        "moved_block_starts":sum(a!=b for a,b in zip(old_starts[:-1],new_starts[:-1])),
        "max_abs_offset_delta":max(abs(e["new_offset"]-e["old_offset"]) for e in moved),
        "candidate_script_bytes":len(candidate)}
    require(stats["moved_commands"]==guard["moved_commands"] and
        stats["moved_nontext"]==guard["moved_nontext_commands"],
        "Independent R26 offset guard disagreement")
    require(file_sha256(iso)==USA_SHA,"Source ISO changed")
    return {"schema":"cladun.r28.private_relocation_map.v1",
        "source_sha256":USA_SHA,"event_guard":guard,"geometry":stats,
        "identity":identity_collisions(before),
        "numeric_candidates":reference_triage(before,entries,old_starts,new_starts,ids),
        "mips_proven":False,"ppsspp_run":False,"new_official_integrations":0,
        "release_authorized":False,"map":entries}

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--iso-original",required=True,type=Path)
    p.add_argument("--map-private",required=True,type=Path)
    a=p.parse_args()
    target=report_path(a.map_private)
    result=audit(a.iso_original)
    target.parent.mkdir(parents=True,exist_ok=True)
    with target.open("x",encoding="utf-8") as f:
        json.dump(result,f,indent=2)
        f.write("\n")
    print(json.dumps({k:v for k,v in result.items() if k!="map"},indent=2))

if __name__=="__main__":
    main()
