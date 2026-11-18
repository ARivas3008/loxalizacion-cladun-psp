#!/usr/bin/env python3
"""Mapa español -> CP932 PUA (F040-F052). NO implica glifos ni parche jugable."""
from __future__ import annotations
import unicodedata

ES_GLYPHS = "áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō"
ES_TO_PRIVATE = {c: chr(0xE000+i) for i,c in enumerate(ES_GLYPHS)}
PRIVATE_TO_ES = {value: key for key,value in ES_TO_PRIVATE.items()}

def encode_spanish(text: str) -> bytes:
    if "\ufffd" in text:
        raise ValueError("Caracteres originales corruptos; no reconstruir por suposición")
    mapped = "".join(ES_TO_PRIVATE.get(c, c) for c in unicodedata.normalize("NFC",text))
    return mapped.encode("cp932","strict")

def decode_spanish(data: bytes) -> str:
    return "".join(PRIVATE_TO_ES.get(c,c) for c in data.decode("cp932","strict"))

def ascii_diagnostic_preview(text: str) -> str:
    """Solo ensayo sin tildes: NO se permite publicar como traducción final."""
    symbols={"¿":"?","¡":"!","«":'"',"»":'"',"“":'"',"”":'"',"’":"'","—":"-","–":"-","…":"..."}
    def convert(char):
        if char in symbols:return symbols[char]
        return "".join(x for x in unicodedata.normalize("NFKD",char) if unicodedata.category(x)!="Mn")
    out="".join(map(convert,text))
    out.encode("cp932","strict")
    return out

if __name__=="__main__":
    sample="¿Qué día es? ¡Sí, señor! Ñandú y pingüino. «Pudding»"
    encoded=encode_spanish(sample)
    assert decode_spanish(encoded)==sample
    assert [encode_spanish(c).hex().upper() for c in ES_GLYPHS]==[
        f"F0{i+0x40:02X}" for i in range(len(ES_GLYPHS))]
    print("OK: codificación reversible, atlas FONT.ARC todavía pendiente.")
