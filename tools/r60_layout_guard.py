"""Provisional R60 cell audit. Scope: observed bestiary, not global MIPS proof."""
from __future__ import annotations


def classify_padding(raw: bytes) -> dict:
    """ASCII space classification without altering original bytes."""
    return {
        'leading': len(raw)-len(raw.lstrip(b' ')),
        'trailing': len(raw)-len(raw.rstrip(b' ')),
        'consecutive': b'  ' in raw,
        'internal_consecutive': b'  ' in raw.strip(b' '),
    }


def check_bestiary(raw: bytes, field: str) -> str:
    """Conservative single-byte cell bounds; controls and multibyte remain pending."""
    limit = {'nombre':17,'descripcion':35,'comportamiento':35}.get(field)
    if limit is None:
        return 'geometry_pending'
    if any((x<32 and x!=10) or 0x81<=x<=0x9f or x>=0xe0 or 0xb4<=x<=0xdf for x in raw):
        return 'encoding_pending'
    lines=raw.split(b'\n')
    if len(lines)>(1 if field=='nombre' else 5) or any(len(line)>limit for line in lines):
        return 'overflow'
    return 'pass_provisional_cell_bound'


def group_advance_result(plain_end: int, ligature_end: int, tolerance: int=2) -> str:
    """Compare same final marker; tolerance in 960x544 screenshot pixels."""
    if tolerance<0:
        raise ValueError('Negative tolerance')
    return 'PASS' if abs(plain_end-ligature_end)<=tolerance else 'FAIL_RENDER_ADVANCE'
