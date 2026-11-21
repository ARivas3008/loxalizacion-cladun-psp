#!/usr/bin/env python3
"""F1: ensayos aislados de espaciado del menú. No certifica render PPSSPP.

No modifica corpus ni borrador: escribe una copia CSV para --borrador del
integrador. La ISO original exacta se usa SOLO para leer las métricas.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from charset_es import ES_GLYPHS, ES_BYTES, encode_spanish
from font_es_patch import BASE_GLYPHS, SOURCE_SHA256, archive

SOURCE = ROOT / "corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv"
DRAFT = ROOT / "traduccion/CLADUN_BORRADOR_ES.csv"
PREFIX_IDS = ("005695", "005696", "005697")
SUFFIX_IDS = ("005698", "005709")
TARGET_IDS = PREFIX_IDS + SUFFIX_IDS


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for part in iter(lambda: f.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def read_rows(path: Path) -> tuple[list[str], list[dict]]:
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader.fieldnames or []), list(reader)


def load_metrics(iso: Path) -> tuple[dict[int, int], str]:
    # archive() coteja el SHA exacto, el PSPFS y FONT.ARC.
    _, _, _, _, font_arc, children = archive(iso)
    glyph = children[0]
    assert glyph["name"] == "FONT.BIN"
    font_bin = font_arc[glyph["offset"]:glyph["offset"] + glyph["size"]]
    n = struct.unpack_from("<I", font_bin)[0]
    if n != 2721 or len(font_bin) != 4 + 4 * n:
        raise ValueError("FONT.BIN no coincide con la estructura original")
    metrics = {}
    for i in range(n):
        code, unused, advance = struct.unpack_from("<HBB", font_bin, 4 + i * 4)
        if code in metrics or not 0 < advance <= 16:
            raise ValueError("FONT.BIN: código o avance inválido")
        metrics[code] = advance
    if len(BASE_GLYPHS) != len(ES_GLYPHS) or len(ES_BYTES) != 19:
        raise ValueError("Mapeo de 19 glifos no coincide")
    for es, source in zip(ES_GLYPHS, BASE_GLYPHS):
        code = ES_BYTES[es][0]
        if code in metrics:
            raise ValueError("Slot español A1-B3 ocupado en original")
        metrics[code] = metrics[ord(source)]
    return metrics, hashlib.sha256(font_bin).hexdigest()


def advance(text: str, metrics: dict[int, int]) -> int:
    total = 0
    for char in text:
        b = encode_spanish(char)
        if len(b) == 1:
            code = b[0]
        elif len(b) == 2:
            code = (b[0] << 8) | b[1]
        else:
            raise ValueError("Carácter no representable: " + repr(char))
        if code not in metrics:
            raise ValueError("FONT.BIN carece de glifo: " + repr(char))
        total += metrics[code]
    return total


def preserve_prefix(original: str, spanish: str) -> str:
    prefix = re.match(r"^[ \u3000]*", original).group(0)
    tail = re.search(r"[ \u3000]*$", original).group(0)
    translated = spanish.strip(" \u3000")
    if original.count("%2d"):
        if original.count("%2d") != translated.count("%2d"):
            raise ValueError("Placeholder %2d no conservado")
    if not prefix and not tail:
        raise ValueError("Texto sin sangría original")
    return prefix + translated + tail


def match_suffix_width(original: str, spanish: str, metrics: dict[int, int]) -> str:
    # Sólo rellenar posiciones que YA existían como relleno en la versión USA.
    if not re.search(r"[ \u3000]+$", original):
        raise ValueError("No existe relleno final original")
    label = spanish.rstrip(" \u3000")
    target = advance(original, metrics)
    baseline = advance(label, metrics)
    if baseline > target:
        raise ValueError("Etiqueta española excede el avance original")
    candidates = []
    for wide in range(0, 33):
        for ascii_spaces in range(0, 33):
            trial = label + "\u3000" * wide + " " * ascii_spaces
            width = advance(trial, metrics)
            candidates.append((abs(width - target), int(width > target),
                               wide + ascii_spaces, ascii_spaces, trial))
    result = min(candidates)[-1]
    if advance(result, metrics) != target:
        raise ValueError("No es posible igualar el ancho con espacios originales")
    return result


def variant(original: str, spanish: str, gid: str, metrics: dict[int, int]) -> str:
    if gid in PREFIX_IDS:
        return preserve_prefix(original, spanish)
    if gid in SUFFIX_IDS:
        return match_suffix_width(original, spanish, metrics)
    raise ValueError("ID ajeno al experimento F1: " + gid)


def build(source: Path, draft: Path, iso: Path, csv_out: Path, report_out: Path,
          selected: tuple[str, ...] = TARGET_IDS) -> dict:
    selected = tuple(dict.fromkeys(selected))
    if not selected or set(selected) - set(TARGET_IDS):
        raise ValueError("Los IDs deben pertenecer al conjunto F1")
    if csv_out.resolve() in (draft.resolve(), source.resolve()):
        raise ValueError("No sobrescribir el corpus ni el borrador canónico")
    if csv_out.resolve() == report_out.resolve():
        raise ValueError("CSV e informe deben ser archivos diferentes")
    if csv_out.exists() or report_out.exists():
        raise FileExistsError("Destinos ya existentes: no sobrescribir evidencias")
    if sha256(iso) != SOURCE_SHA256:
        raise ValueError("SHA-256 ISO original incorrecto")
    fields, rows = read_rows(draft)
    _, originals = read_rows(source)
    if len(rows) != 9237 or len(originals) != len(rows):
        raise ValueError("Corpus incompleto")
    metrics, font_hash = load_metrics(iso)
    changes = []
    for src, row in zip(originals, rows):
        if (src["grupo_id"] != row["grupo_id"] or
                src["original"] != row["original"] or
                src["bytes_hex"] != row["bytes_hex"] or
                src["offset_hex"] != row["offset_hex"]):
            raise ValueError("Fuente o alineación de IDs inconsistente")
        gid = row["grupo_id"]
        if gid not in selected:
            continue
        if src["origen"] != "DATABASE.DAT/STRTBL.DAT":
            raise ValueError("ID no pertenece a STRTBL.DAT")
        before = row["espanol"]
        after = variant(src["original"], before, gid, metrics)
        if before == after:
            raise ValueError("Variante sin cambio efectivo: " + gid)
        changes.append({
            "grupo_id": gid,
            "original_repr": repr(src["original"]),
            "espanol_anterior_repr": repr(before),
            "espanol_variante_repr": repr(after),
            "ancho_original": advance(src["original"], metrics),
            "ancho_es_anterior": advance(before, metrics),
            "ancho_es_variante": advance(after, metrics),
            "codigo_texto_original_inmutable": True,
        })
        row["espanol"] = after
    if len(changes) != len(selected):
        raise ValueError("Faltan IDs del experimento")
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    with csv_out.open("x", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    result = {
        "schema": "cladun.menu_f1.static_experiment.v1",
        "estado": "SOLO_CANDIDATA_CSV_SIN_PPSSPP",
        "iso_original_sha256": SOURCE_SHA256,
        "font_bin_original_sha256": font_hash,
        "csv_borrador_canonico_sha256": sha256(draft),
        "csv_variante_sha256": sha256(csv_out),
        "numero_registros": 9237,
        "ids_elegidos": list(selected),
        "filas_cambiadas": changes,
        "integracion_ejecucion": "PENDIENTE",
        "integridad_pspfs": "PENDIENTE",
        "capturas_ppsspp": "PENDIENTE",
        "hipotesis": "El avance y las sangrías podrían intervenir en ancho de ventana; sin atribución causal aún.",
    }
    with report_out.open("x", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return result


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--iso", type=Path, required=True, help="ISO USA original verificada (privada)")
    p.add_argument("--salida-csv", type=Path, required=True)
    p.add_argument("--reporte", type=Path, required=True)
    p.add_argument("--ids", nargs="+", choices=TARGET_IDS, default=list(TARGET_IDS))
    args = p.parse_args()
    report = build(SOURCE, DRAFT, args.iso, args.salida_csv,
                   args.reporte, tuple(args.ids))
    print(json.dumps({"estado": report["estado"],
                      "cambios": report["filas_cambiadas"]},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
