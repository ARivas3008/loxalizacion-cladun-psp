#!/usr/bin/env python3
"""Auditoría conservadora de referencia terminológica La Pucelle -> Cladun.

La tabla de La Pucelle solo sirve de consulta. Nunca escribe traducciones,
el glosario canónico, las fuentes del juego ni imágenes ISO/BPS.
"""
from __future__ import annotations

import argparse
import csv
import json
import unicodedata
from pathlib import Path


def leer(ruta: Path) -> list[dict[str, str]]:
    with Path(ruta).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def clave(valor: str) -> str:
    return unicodedata.normalize("NFC", valor.strip()).casefold()


def auditar(referencia: list[dict[str, str]],
            canonico: list[dict[str, str]]) -> dict:
    if not referencia or not canonico:
        raise ValueError("Ambos glosarios deben contener registros")
    requeridos_ref = {"termino", "espanol", "nombre_ingles", "confianza",
                      "estatus", "fuente_url", "nota"}
    requeridos_cla = {"original", "espanol", "estado"}
    if not requeridos_ref.issubset(referencia[0]):
        raise ValueError("Cabecera de La Pucelle incompleta")
    if not requeridos_cla.issubset(canonico[0]):
        raise ValueError("Cabecera de Cladun incompleta")

    # Solo se cruzan términos originales o equivalentes EN; la coincidencia
    # de una traducción española genérica no acredita equivalencia semántica.
    index: dict[str, list[dict[str, str]]] = {}
    for row in referencia:
        if "sin resolver" in clave(row["confianza"]) or "[sin resolver]" in clave(row["espanol"]):
            continue
        for field in ("termino", "nombre_ingles"):
            name = clave(row[field])
            if name and name not in {"sin equivalente fiable", "[sin resolver]"}:
                bucket = index.setdefault(name, [])
                if row not in bucket:
                    bucket.append(row)

    matches = []
    for term in canonico:
        for row in index.get(clave(term["original"]), []):
            matches.append({
                "original_cladun": term["original"],
                "espanol_cladun": term["espanol"],
                "termino_la_pucelle": row["termino"],
                "ingles_la_pucelle": row["nombre_ingles"],
                "espanol_la_pucelle": row["espanol"],
                "equivalencia": ("misma_traduccion_no_validada"
                                if clave(term["espanol"]) == clave(row["espanol"])
                                else "traduccion_distinta_requiere_contexto"),
                "decision": "revisar_humanamente_sin_transferencia_automatica"
            })
    return {
        "fuente": "ARivas3008/la-pucelle-ragnarok-localizacion/glosario/terminos_investigados.csv",
        "destino": "Cladun / traduccion/GLOSARIO_CANONICO.csv",
        "total_terminos_pucelle": len(referencia),
        "total_terminos_cladun": len(canonico),
        "sin_resolver_pucelle": sum(
            "sin resolver" in clave(x["confianza"]) or
            "[sin resolver]" in clave(x["espanol"]) for x in referencia),
        "coincidencias_exactas_original_o_ingles": len(matches),
        "coincidencias": matches,
        "terminos_importados_automaticamente": 0,
        "glosario_cladun_modificado": False,
        "regla": "Material de consulta; las coincidencias requieren contexto y aprobación humana.",
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--referencia", type=Path,
                    default=Path("referencias/la_pucelle/terminos_investigados.csv"))
    ap.add_argument("--cladun", type=Path,
                    default=Path("traduccion/GLOSARIO_CANONICO.csv"))
    ap.add_argument("--reporte", type=Path,
                    default=Path("reports/auditoria_referencia_la_pucelle.json"))
    args = ap.parse_args()
    result = auditar(leer(args.referencia), leer(args.cladun))
    args.reporte.parent.mkdir(parents=True, exist_ok=True)
    args.reporte.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n",
                            encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
