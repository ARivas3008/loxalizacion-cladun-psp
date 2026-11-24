#!/usr/bin/env python3
"""Measure downstream command relocation exposure, not runtime MIPS references."""
from __future__ import annotations
import argparse
from collections import Counter,defaultdict
import json
from pathlib import Path
try:
    from tools.script_event_guard import read_commands,TEXT_OPS
    from tools.f3_referencias_riesgo import original_script_children
except ModuleNotFoundError:
    from script_event_guard import read_commands,TEXT_OPS
    from f3_referencias_riesgo import original_script_children

def exposure(data: bytes, table: bytes) -> dict:
    commands,starts=read_commands(data,table)
    blocks=defaultdict(list)
    for c in commands:
        blocks[c.block].append(c)
    counts=Counter()
    affected_nontext=0
    affected_text=0
    trailing=Counter()
    text_blocks=set()
    text_commands=0
    for block,items in blocks.items():
        suffix_nontext=0
        suffix_text=0
        for c in reversed(items):
            if c.content is not None:
                text_commands+=1
                text_blocks.add(block)
                trailing[suffix_nontext+suffix_text]+=1
                affected_nontext+=suffix_nontext
                affected_text+=suffix_text
                if suffix_nontext == 0:
                    counts['text_without_following_nontext']+=1
                if suffix_nontext+suffix_text == 0:
                    counts['text_last_command']+=1
                suffix_text+=1
            else:
                suffix_nontext+=1
    return {
        'schema':'cladun.r20.relocation_exposure.v1',
        'script_blocks':len(starts)-1,
        'commands':len(commands),
        'text_commands':text_commands,
        'text_bearing_blocks':len(text_blocks),
        'text_last_command':counts['text_last_command'],
        'text_without_following_nontext':counts['text_without_following_nontext'],
        'minimum_following_commands':min(trailing) if trailing else None,
        'maximum_following_commands':max(trailing) if trailing else None,
        'sum_following_nontext_commands_per_one_text_edit':affected_nontext,
        'sum_following_text_commands_per_one_text_edit':affected_text,
        'interpretation':'Each length-changing edit shifts subsequent commands within its block unless a different proven storage scheme is used; counts are exposures, not unique commands or verified MIPS references.',
        'variable_length_insertion_authorized':False,
        'control_flow_reference_model_verified':False,
        'ppsspp_runtime_verified':False,
    }

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iso-original',type=Path,required=True)
    a=ap.parse_args()
    data,table=original_script_children(a.iso_original)
    print(json.dumps(exposure(data,table),indent=2))

if __name__=='__main__':
    main()
