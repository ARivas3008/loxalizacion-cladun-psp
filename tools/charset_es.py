#!/usr/bin/env python3
"""Cladun USA PSP Spanish codec (single-byte CP932 halfwidth slot A1-B3).

The engine treats private F5xx codes as double-width, causing visibly broken
spacing. Reserve nineteen single-byte halfwidth SJIS codes instead, while
relocating original atlas cells to keep their glyphs intact.
"""
from __future__ import annotations
import unicodedata

ES_GLYPHS = 'áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō'
CODE_BASE = 0xA1  # single-byte CP932 halfwidth range, absent in original FONT.BIN
ES_BYTES = {c:bytes([CODE_BASE+i]) for i,c in enumerate(ES_GLYPHS)}
ES_TO_PRIVATE = {c:b.decode('cp932') for c,b in ES_BYTES.items()}
PRIVATE_TO_ES = {v:k for k,v in ES_TO_PRIVATE.items()}
assert len(ES_GLYPHS)==len(ES_BYTES)==len(ES_TO_PRIVATE)==len(PRIVATE_TO_ES)==19

def encode_spanish(text: str) -> bytes:
    if '\ufffd' in text:
        raise ValueError('Texto fuente con U+FFFD; no reconstruir por suposición')
    mapped=''.join(ES_TO_PRIVATE.get(c,c) for c in unicodedata.normalize('NFC',text))
    return mapped.encode('cp932','strict')

def decode_spanish(data: bytes) -> str:
    return ''.join(PRIVATE_TO_ES.get(c,c) for c in data.decode('cp932','strict'))

def ascii_diagnostic_preview(text: str) -> str:
    """Diagnostic-only transliteration, never acceptable as a published translation."""
    symbols={'¿':'?','¡':'!','«':'"','»':'"','“':'"','”':'"','’':"'",'—':'-','–':'-','…':'...'}
    def convert(char):
        if char in symbols:return symbols[char]
        return ''.join(x for x in unicodedata.normalize('NFKD',char) if unicodedata.category(x)!='Mn')
    out=''.join(map(convert,text))
    out.encode('cp932','strict')
    return out

if __name__=='__main__':
    sample='¿Qué día es? ¡Sí, señor! Ñandú y pingüino. «Pudding», ō.'
    assert decode_spanish(encode_spanish(sample))==sample
    assert encode_spanish(ES_GLYPHS)==bytes(range(CODE_BASE,CODE_BASE+len(ES_GLYPHS)))
    print('CODEC ROUNDTRIP OK — visual verification pending')
