"""Read-only R45 triage. Numeric matches are not proven MIPS references."""
from collections import Counter, defaultdict
import argparse
import json
from pathlib import Path


def scan(commands, starts, deltas):
    shift = defaultdict(int)
    moved = {}
    used = set()
    for c in commands:
        if shift[c.block]:
            moved[c.offset] = (c.block, c.offset + shift[c.block], c.content is not None)
        if c.offset + 7 in deltas and c.content is not None:
            shift[c.block] += deltas[c.offset + 7]
            used.add(c.offset + 7)
    if used != set(deltas):
        raise ValueError('Text slot not found')
    local = {(b, p - starts[b]): p for p, (b, _, _) in moved.items()}
    counts = Counter(dict.fromkeys(('absolute_16', 'absolute_32', 'local_16', 'local_32'), 0))
    hits = []
    for c in commands:
        if c.content is not None:
            continue
        payload = c.raw[5:]
        for width in (2, 4):
            for i in range(len(payload) - width + 1):
                v = int.from_bytes(payload[i:i+width], 'little')
                if v in moved:
                    counts[f'absolute_{width*8}'] += 1
                target = local.get((c.block, v))
                if target is None:
                    continue
                counts[f'local_{width*8}'] += 1
                hits.append({'block': c.block, 'source_offset': c.offset,
                             'source_opcode': f'{c.code:02X}', 'payload_offset': i,
                             'width': width, 'target_old': target,
                             'target_new': moved[target][1], 'target_text': moved[target][2]})
    return {'moved_commands': len(moved), 'moved_nontext': sum(not t for _, _, t in moved.values()),
            'moved_blocks': len({b for b, _, _ in moved.values()}), 'counts': dict(counts),
            'unique_sources': len({h['source_offset'] for h in hits}),
            'unique_targets': len({h['target_old'] for h in hits}),
            'hit_blocks': len({h['block'] for h in hits}),
            'even_payload_offsets': sum(h['payload_offset'] % 2 == 0 for h in hits),
            'hits': hits, 'reference_semantics_proven': False, 'release_authorized': False}


def audit(iso):
    from tools.f3_referencias_riesgo import original_script_children
    from tools.script_event_guard import read_commands
    from tools.r44_local_experimental import RESIDUAL, DONORS
    from tools.r35_ligaduras_acumuladas import PAIRS
    from tools.f4_r21_ligature_capacity import matching
    from tools.charset_es import encode_spanish
    data, table = original_script_children(iso)
    commands, starts = read_commands(data, table)
    by_slot = {c.offset + 7: c for c in commands if c.content is not None}
    deltas = {}
    for line in RESIDUAL.read_text(encoding='utf-8').splitlines():
        gid, offset, text = line.split('\t', 2)
        p = int(offset, 16)
        d = len(encode_spanish(text)) - len(matching(text, PAIRS)) - len(by_slot[p].content)
        if d <= 0 or p in deltas:
            raise ValueError('Residual drift: ' + gid)
        deltas[p] = d
    if len(deltas) != 33 or sum(deltas.values()) != 40:
        raise ValueError('R44 residual geometry drift')
    for line in DONORS.read_text(encoding='utf-8').splitlines():
        gid, offset, saved, _ = line.split('\t', 3)
        p = int(offset, 16)
        if p in deltas or p not in by_slot or int(saved) not in (1, 2):
            raise ValueError('Donor drift: ' + gid)
        deltas[p] = -int(saved)
    if len(deltas) != 51 or sum(deltas.values()) != 18:
        raise ValueError('R44 donor geometry drift')
    result = scan(commands, starts, deltas)
    if (len(commands), result['moved_commands'], result['moved_nontext'], result['moved_blocks']) != (51705, 2712, 2221, 24):
        raise ValueError('R44 movement geometry drift')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso-original', type=Path, required=True)
    print(json.dumps(audit(p.parse_args().iso_original), indent=2))
