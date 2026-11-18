#!/usr/bin/env python3
"""Valida estructura y marcadores del borrador español frente al CSV original."""
from pathlib import Path
import csv
import json
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
ORIGINAL = ROOT / "corpus" / "CLADUN_TODO_TEXTO_ORIGINAL.csv"
TRANSLATION = ROOT / "traduccion" / "CLADUN_BORRADOR_ES.csv"
TOKEN = re.compile(r'%(?:\d+\$)?[-+0#]*\d*(?:\.\d+)?[sdifouxXc]|[①-⑳]|\\[nrt]|\{[a-zA-Z_][^{}]*\}|<[^>]+>')

def load(path):
    with path.open("r", encoding="utf-8-sig", newline="") as file:
        return list(csv.DictReader(file))

def run():
    a, b = load(ORIGINAL), load(TRANSLATION)
    errors = []
    check_fields = ["grupo_id", "text_id", "tipo", "campo", "original", "estado",
                    "revision_fuente", "origen", "indice_registro", "script", "script_id",
                    "orden_script", "offset_hex", "capacidad_campo",
                    "longitud_original_bytes", "bytes_hex", "idioma_origen", "comentario"]
    if len(a) != len(b):
        errors.append(f"Filas: original={len(a)} borrador={len(b)}")
    completed = 0
    for i, (src, dst) in enumerate(zip(a,b), 1):
        for fld in check_fields:
            if src.get(fld, "") != dst.get(fld, ""):
                errors.append(f"{i}: cambió {fld}")
        es = dst.get("espanol","")
        if es:
            completed += 1
            if sorted(TOKEN.findall(src["original"])) != sorted(TOKEN.findall(es)):
                errors.append(f"{i}: cambió un marcador protegido")
    data = {"fuente":len(a), "borrador":len(b), "con_espanol":completed,
            "sin_espanol":len(b)-completed, "errores":errors}
    print(json.dumps(data, ensure_ascii=False, indent=2))
    return 0 if not errors else 1

if __name__ == "__main__":
    sys.exit(run())
