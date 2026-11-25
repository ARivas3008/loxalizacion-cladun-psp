"""R46: reproduce the isolated 78 changes and reject unsafe fixed-offset promotion."""
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path
from tools.f3_referencias_riesgo import original_script_children
from tools.script_event_guard import read_commands, audit_script_rebuild
from tools.r44_local_experimental import RESIDUAL, DONORS, width, rebuild
from tools.r35_ligaduras_acumuladas import PAIRS
from tools.f4_r21_ligature_capacity import matching
from tools.charset_es import encode_spanish

ROOT = Path(__file__).resolve().parents[1] / 'traduccion/propuestas'
EXPECTED = '357c3cebcb0dec9de6a27a520548de0c91f537aeba75aa15129b935c9804dc51'
PREVIOUS = '34f3716f98dbbf70554c3d993f9816f408ed74e732a014b38e8c7dce377763f8'


def individual_geometry(commands, starts, slot, delta):
    if delta <= 0 or slot not in {c.offset+7 for c in commands if c.content is not None}:
        raise ValueError('Not a growing text slot')
    c = next(c for c in commands if c.offset+7 == slot and c.content is not None)
    later = [x for x in commands if x.block == c.block and x.order > c.order]
    last = later[-1] if later else c
    padding = starts[c.block+1] - last.offset - len(last.raw)
    return {'subsequent_commands': len(later),
            'subsequent_nontext_commands': sum(x.content is None for x in later),
            'block_tail_padding': padding, 'additional_bytes': delta,
            'individual_block_capacity_passed': delta <= padding,
            'individual_fixed_offsets_passed': not later and delta <= padding}


def audit(iso):
    data, table = original_script_children(iso)
    commands, starts = read_commands(data, table)
    slots = {c.offset+7: c.content for c in commands if c.content is not None}
    expected = {}
    def add(gid, at, text, n):
        old = slots[at]
        new = width(text, n)
        if at in expected or old == new:
            raise ValueError('Duplicate or unchanged: '+gid)
        expected[at] = (old, new, gid)
    for name in ('R42_CANDIDATOS.tsv', 'R43_CANDIDATOS.tsv'):
        for line in (ROOT/name).read_text(encoding='utf-8').splitlines():
            gid, offset, text = line.split('\t', 2)
            at = int(offset, 16)
            add(gid, at, text, len(slots[at]))
    add('003766', 467759, 'Por favor, intenta superar', len(slots[467759]))
    prev = bytearray(data)
    for at, (old, new, _) in expected.items():
        if len(old) != len(new):
            raise ValueError('Previous slot width changed')
        prev[at:at+len(old)] = new
    if len(expected) != 27 or hashlib.sha256(prev).hexdigest() != PREVIOUS:
        raise ValueError('R43 isolated SHA drift')
    audit_script_rebuild(data, table, bytes(prev), table, expected, require_fixed_offsets=True)
    individual = []
    for line in RESIDUAL.read_text(encoding='utf-8').splitlines():
        gid, offset, text = line.split('\t', 2)
        at = int(offset, 16)
        n = len(encode_spanish(text)) - len(matching(text, PAIRS))
        individual.append({'id': gid, **individual_geometry(commands, starts, at, n-len(slots[at]))})
        add(gid, at, text, n)
    for line in DONORS.read_text(encoding='utf-8').splitlines():
        gid, offset, save, text = line.split('\t', 3)
        at = int(offset, 16)
        add(gid, at, text, len(slots[at])-int(save))
    if len(expected) != 78 or len(individual) != 33:
        raise ValueError('Diagnostic count drift')
    result, tbl, report = rebuild(data, table, expected)
    if hashlib.sha256(result).hexdigest() != EXPECTED:
        raise ValueError('R44 isolated SHA drift')
    try:
        audit_script_rebuild(data, table, result, tbl, expected, require_fixed_offsets=True)
    except ValueError as e:
        if 'Bloqueo de seguridad' not in str(e):
            raise
    else:
        raise ValueError('Unsafe R44 candidate unexpectedly admitted')
    if any(r['individual_fixed_offsets_passed'] for r in individual):
        raise ValueError('Individual geometry drift')
    return {'r44_sha256': EXPECTED, 'previous_sha256': PREVIOUS, 'isolated_changes': len(expected),
            'individual': individual, 'fixed_offset_gate_passed': False,
            'event_audit': report, 'release_authorized': False, 'runtime_verified': False}


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--iso-original', type=Path, required=True)
    print(json.dumps(audit(p.parse_args().iso_original), indent=2))
