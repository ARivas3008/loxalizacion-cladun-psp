#!/usr/bin/env python3
"""F1: variantes privadas ON/OFF con corrección 005709; NO es QA visual.

Genera un borrador CSV separado. No modifica el texto canónico ni recursos.
La prueba visual debe decidir si los valores/píxeles encajan.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from auditar_preinsercion_es import SOURCE, DRAFT
from charset_es import decode_spanish, encode_spanish
from experimento_menu_f1 import advance, load_metrics, read_rows, sha256
from font_es_patch import SOURCE_SHA256
from integrar_parche_seguro import source_rows
from menu_layout_es import GROUP_ID, LAYOUT_TRANSLATION, patch_canonical_menu_layout

EXPECTED = {
    "005710": ("          ON", "          Sí"),
    "005713": ("         OFF", "         No"),
}
LABELS = {
    "si-no": {"005710": "Sí", "005713": "No"},
    # Solo experimento de presentacion: el espacio final de No iguala
    # los 84 px de OFF segun FONT.BIN USA; no validar sin PPSSPP.
    "si-no-espacio-final": {"005710": "Sí", "005713": "No "},
    "activado-desactivado": {"005710": "Activado", "005713": "Desactivado"},
}
CONTROL_IDS = ("005711", "005712")


def prepare_rows(pairs, *, mode="si-no", selected=("005710", "005713")):
    """Valida originales y genera únicamente el overlay privado de F1."""
    if mode not in LABELS:
        raise ValueError("Modo ON/OFF desconocido")
    ids = tuple(dict.fromkeys(selected))
    if not ids or set(ids) - set(EXPECTED):
        raise ValueError("Solo son admisibles 005710/005713")
    adjusted, layout = patch_canonical_menu_layout(pairs)
    result, changes, found = [], [], set()
    controls_found = set()
    for src, dst in adjusted:
        gid = src["grupo_id"]
        if gid in CONTROL_IDS:
            controls_found.add(gid)
        if gid not in ids:
            result.append((src, dst))
            continue
        expected_source, expected_spanish = EXPECTED[gid]
        if (gid in found or src["origen"] != "DATABASE.DAT/STRTBL.DAT" or
                src["original"] != expected_source or
                dst["original"] != expected_source or
                src["bytes_hex"].upper() != expected_source.encode("cp932").hex().upper() or
                dst["espanol"] != expected_spanish):
            raise ValueError(f"Preimagen o recurso no reconocido: {gid}")
        prefix = expected_source[:len(expected_source) - len(expected_source.lstrip(" "))]
        after = prefix + LABELS[mode][gid]
        coded = encode_spanish(after)
        if decode_spanish(coded) != after:
            raise ValueError(f"Codificación no reversible: {gid}")
        result.append((src, {**dst, "espanol": after}))
        changes.append({"grupo_id": gid, "original_repr": repr(expected_source),
                        "anterior_repr": repr(expected_spanish),
                        "variante_repr": repr(after),
                        "original_text": expected_source,
                        "variante_text": after,
                        "sangria_ascii_original_conservada": True,
                        "anclaje_derecho_visual_validado": False})
        found.add(gid)
    if found != set(ids) or controls_found != set(CONTROL_IDS):
        raise ValueError("Faltan valores o IDs de contexto de Opciones")
    if len(result) != len(pairs):
        raise ValueError("Recuento alterado")
    return result, {"layout_005709": layout, "cambios_onoff": changes,
                    "ids_contexto_intactos": list(CONTROL_IDS),
                    "ids_tocados_presentacion": [GROUP_ID, *ids]}


def build(csv_out: Path, report_out: Path, *, mode="si-no",
          selected=("005710", "005713"), iso: Path | None = None):
    csv_out, report_out = Path(csv_out), Path(report_out)
    protected = {SOURCE.resolve(), DRAFT.resolve()}
    if (csv_out.resolve() in protected or report_out.resolve() in protected or
            csv_out.resolve() == report_out.resolve()):
        raise ValueError("Está prohibido sobrescribir corpus/borrador canónicos")
    if csv_out.exists() or report_out.exists():
        raise FileExistsError("Solo se permiten destinos de salida nuevos")
    pairs = source_rows()
    if len(pairs) != 9237:
        raise ValueError("Recuento canónico inesperado")
    rows, info = prepare_rows(pairs, mode=mode, selected=selected)
    if iso is not None:
        if sha256(iso) != SOURCE_SHA256:
            raise ValueError("ISO original no coincide en SHA-256")
        metrics, font_hash = load_metrics(iso)
        for changed in info["cambios_onoff"]:
            changed["avance_original_px"] = advance(changed["original_text"], metrics)
            changed["avance_variante_px"] = advance(changed["variante_text"], metrics)
            changed["diferencia_avance_px"] = (changed["avance_variante_px"] -
                                                changed["avance_original_px"])
    else:
        font_hash = None
    report = {
        "schema": "cladun.menu_f1.onoff_isolated_experiment.v1",
        "estado": "CSV_PRIVADO_NO_PROBADO_EN_PPSSPP",
        "modo": mode, "iso_original_sha256_esperado": SOURCE_SHA256,
        "iso_original_verificada_en_esta_ejecucion": iso is not None,
        "font_bin_sha256": font_hash,
        "csv_canonico_sha256": sha256(DRAFT),
        "entradas_conservadas": len(rows),
        "qa_visual_real": "NO_EJECUTADA",
        "iso_bps": "NO_CONSTRUIDOS_POR_ESTA_HERRAMIENTA",
        "event_safe_only_obligatorio_en_integracion": True,
        **info,
    }
    fields, _ = read_rows(DRAFT)
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    report_out.parent.mkdir(parents=True, exist_ok=True)
    with csv_out.open("x", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(dst for _src, dst in rows)
    report["csv_variante_sha256"] = sha256(csv_out)
    with report_out.open("x", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
        f.write("\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--salida-csv", type=Path, required=True)
    parser.add_argument("--reporte", type=Path, required=True)
    parser.add_argument("--modo", choices=LABELS, default="si-no")
    parser.add_argument("--ids", nargs="+", choices=EXPECTED, default=list(EXPECTED))
    parser.add_argument("--iso", type=Path,
                        help="ISO USA privada para medir avances; sin esta solo se genera CSV")
    a = parser.parse_args()
    result = build(a.salida_csv, a.reporte, mode=a.modo, selected=a.ids, iso=a.iso)
    print(json.dumps({"estado": result["estado"], "cambios": result["cambios_onoff"]},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
