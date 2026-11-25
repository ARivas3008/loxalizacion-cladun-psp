#!/usr/bin/env python3
"""F1: generar CSV PRIVADO de +1 espacio ideográfico para 005709.

No reconstruye ISO, no ejecuta PPSSPP, no modifica corpus ni borrador canónico.
El hash de ISO histórica es una ASSERTION pendiente, no resultado de este script.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from auditar_preinsercion_es import SOURCE, DRAFT
from experimento_menu_f1 import read_rows, load_metrics, advance, sha256
from font_es_patch import SOURCE_SHA256
from integrar_parche_seguro import source_rows
from menu_layout_es import (
    GROUP_ID, SOURCE_ORIGINAL, SOURCE_TRANSLATION,
)

EXTRA = "\u3000"
LAYOUT_MINIMAL_HISTORICO = SOURCE_TRANSLATION + "　" * 10 + " " * 6
LAYOUT_PLUS_ONE = LAYOUT_MINIMAL_HISTORICO + EXTRA
EXPECTED_ISO_PLUS_ONE = "f97fa355fce8d7ab55a81fc711e944185ebdce4a320a5077695cb445acd303c8"
EXPECTED_BPS_PLUS_ONE = "279bd99d7a0cfb87fd1bb4a03ee67ecc250d51563e14f12e213283922a8634fc"


def prepare_plus_one(pairs):
    """Solo modifica 005709.espanol, exige preimagen verificada y 9237 filas."""
    if len(pairs) != 9237:
        raise ValueError("Recuento de corpus inesperado")
    changed = 0
    after = []
    for src, dest in pairs:
        if src["grupo_id"] == GROUP_ID:
            if (src["original"] != SOURCE_ORIGINAL
                    or src["origen"] != "DATABASE.DAT/STRTBL.DAT"
                    or dest["espanol"] != SOURCE_TRANSLATION
                    or src["bytes_hex"].upper() != SOURCE_ORIGINAL.encode("cp932").hex().upper()):
                raise ValueError("005709 preimagen inesperada")
            dest = {**dest, "espanol": LAYOUT_PLUS_ONE}
            changed += 1
        after.append((src, dest))
    if changed != 1:
        raise ValueError("005709 ausente o duplicado")
    differing = [(a["grupo_id"], [k for k in b if b[k] != d[k]])
                 for (a, b), (_s, d) in zip(pairs, after) if b != d]
    if differing != [(GROUP_ID, ["espanol"])]:
        raise ValueError("F1: modificación fuera de 005709")
    return after


def build(csv_out: Path, report_out: Path, *, iso: Path | None = None):
    csv_out, report_out = Path(csv_out), Path(report_out)
    forbidden = {SOURCE.resolve(), DRAFT.resolve()}
    if (csv_out.resolve() in forbidden or report_out.resolve() in forbidden
            or csv_out.resolve() == report_out.resolve()):
        raise ValueError("No sobrescribir fuentes canónicas")
    if csv_out.exists() or report_out.exists():
        raise FileExistsError("Usar destinos completamente nuevos")
    pairs = source_rows()
    changed = prepare_plus_one(pairs)
    metrics = None
    font_sha = None
    if iso is not None:
        if sha256(iso) != SOURCE_SHA256:
            raise ValueError("ISO USA SHA-256 no coincide")
        metrics, font_sha = load_metrics(iso)
        before_width = advance(SOURCE_ORIGINAL, metrics)
        min_width = advance(LAYOUT_MINIMAL_HISTORICO, metrics)
        extra_width = advance(LAYOUT_PLUS_ONE, metrics)
        if (before_width, min_width, extra_width) != (303, 303, 318):
            raise ValueError("Métricas de fuente inesperadas")
    fields, _ = read_rows(DRAFT)
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    with csv_out.open("x", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(dest for _src, dest in changed)
    result = {
        "schema": "cladun.f1.extra_ideographic_isolated.v1",
        "estado": "SOLO_CSV_NO_PPSSPP_NO_ISO_NUEVA",
        "iso_original_sha256_esperado": SOURCE_SHA256,
        "iso_original_verificada_en_esta_ejecucion": iso is not None,
        "font_sha256": font_sha,
        "total_filas": len(changed),
        "unico_id_modificado": GROUP_ID,
        "texto_literario_original": SOURCE_TRANSLATION,
        "presentacion_extra_repr": repr(LAYOUT_PLUS_ONE),
        "cambio_espaciado": "10 U+3000 + 6 ASCII + 1 U+3000",
        "ancho_fuente_original_px": 303 if metrics is not None else None,
        "ancho_fuente_minimo_px": 303 if metrics is not None else None,
        "ancho_fuente_extra_px": 318 if metrics is not None else None,
        "iso_variante_sha256_historico_esperado_NO_REPRODUCIDO": EXPECTED_ISO_PLUS_ONE,
        "bps_variante_sha256_historico_esperado_NO_REPRODUCIDO": EXPECTED_BPS_PLUS_ONE,
        "parcheador_requiere": ["--borrador", "--experimental-parcial", "--event-safe-only"],
        "verificacion_iso_nueva": "NO_EJECUTADA",
        "capturas_ppsspp": "NO_EJECUTADAS",
        "csv_maestro_modificado": False,
        "csv_variante_sha256": sha256(csv_out),
    }
    with report_out.open("x", encoding="utf-8") as handle:
        json.dump(result, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    return result


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--salida-csv", required=True, type=Path)
    ap.add_argument("--reporte", required=True, type=Path)
    ap.add_argument("--iso", type=Path, help="ISO USA original privada para cotejar fuente")
    args = ap.parse_args()
    result = build(args.salida_csv, args.reporte, iso=args.iso)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
