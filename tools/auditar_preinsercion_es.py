#!/usr/bin/env python3
"""Preflight estático y conservador del borrador español de Cladun PSP.

No modifica binarios ni certifica el renderizador, PPSSPP, las dimensiones
de las ventanas o la compatibilidad del cargador del juego.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import hashlib
import json
from pathlib import Path
import re

from charset_es import encode_spanish, decode_spanish
from verificar_borrador_es import TOKEN

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv"
DRAFT = ROOT / "traduccion/CLADUN_BORRADOR_ES.csv"
SOURCE_SHA256 = "b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f"
IMMUTABLE = (
    "grupo_id", "text_id", "tipo", "campo", "original", "estado",
    "revision_fuente", "origen", "indice_registro", "script", "script_id",
    "orden_script", "offset_hex", "capacidad_campo",
    "longitud_original_bytes", "bytes_hex", "idioma_origen", "comentario",
)
SCRIPT = "SCRIPT.SDT/SCRIPT.DAT"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        reader = csv.DictReader(stream)
        missing = set(IMMUTABLE) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path}: columnas ausentes: {sorted(missing)}")
        return list(reader)


def check_row(src: dict[str, str], dst: dict[str, str]) -> dict:
    """Clasifica UNA unidad: aprobado para editar = NUNCA (requiere runtime)."""
    gid = src["grupo_id"]
    base = {
        "grupo_id": gid,
        "text_id": src["text_id"],
        "origen": src["origen"],
        "revision_es": dst.get("revision_es", ""),
        "bytes_originales": None,
        "bytes_es": None,
        "capacidad": None,
        "estado": "",
        "aprobado_para_insertar": False,
    }
    differences = [key for key in IMMUTABLE if src.get(key, "") != dst.get(key, "")]
    if differences:
        base["estado"] = "BLOQUEADO_FUENTE_MODIFICADA"
        base["detalle"] = ", ".join(differences)
        return base

    text = dst.get("espanol", "")
    if not text:
        base["estado"] = "BLOQUEADO_SIN_TRADUCCION"
        return base
    if src["estado"] == "requiere_reconstruccion" or "\ufffd" in src["original"]:
        base["estado"] = "BLOQUEADO_FUENTE_INCOMPLETA"
        return base
    if sorted(TOKEN.findall(src["original"])) != sorted(TOKEN.findall(text)):
        base["estado"] = "BLOQUEADO_MARCADOR"
        return base
    if "\x00" in text or "\r" in text:
        base["estado"] = "BLOQUEADO_CONTROL_INESPERADO"
        return base
    if src["tipo"] in ("mensaje_grafico", "titulo_grafico") or not src["offset_hex"]:
        base["estado"] = "BLOQUEADO_IMAGEN_O_SIN_OFFSET"
        return base

    try:
        source_bytes = bytes.fromhex(src["bytes_hex"])
        if not source_bytes or source_bytes.decode("cp932", "strict") != src["original"]:
            raise ValueError("bytes fuente incompatibles con original")
        if int(src["longitud_original_bytes"]) != len(source_bytes):
            raise ValueError("longitud de fuente discrepante")
        if int(src["offset_hex"], 16) < 0:
            raise ValueError("offset de fuente negativo")
    except (ValueError, UnicodeError) as exc:
        base["estado"] = "BLOQUEADO_BYTES_ORIGINALES"
        base["detalle"] = str(exc)
        return base
    base["bytes_originales"] = len(source_bytes)

    try:
        encoded = encode_spanish(text)
        if decode_spanish(encoded) != text:
            raise ValueError("texto no reversible (normalización Unicode o códec)")
    except (ValueError, UnicodeError) as exc:
        base["estado"] = "BLOQUEADO_CODIFICACION"
        base["detalle"] = str(exc)
        return base
    base["bytes_es"] = len(encoded)

    if src["origen"] == SCRIPT:
        if len(encoded) != len(source_bytes):
            base["estado"] = "BLOQUEADO_CAMBIO_LONGITUD_SCRIPT"
            return base
    elif src["capacidad_campo"]:
        try:
            capacity = int(src["capacidad_campo"])
        except ValueError:
            base["estado"] = "BLOQUEADO_CAPACIDAD_INVALIDA"
            return base
        base["capacidad"] = capacity
        if capacity <= 0 or len(encoded) + 1 > capacity:
            base["estado"] = "BLOQUEADO_DESBORDE_CAMPO"
            return base
    else:
        base["estado"] = "BLOQUEADO_SIN_MODELO_DE_CAPACIDAD"
        return base

    # Estructura estática compatible con el contrato conocido; el inyector
    # todavía deberá demostrar bytes vecinos intactos y comportamiento en juego.
    base["estado"] = "CANDIDATO_A_ENSAYO_NO_VALIDADO"
    return base


def audit(source: Path = SOURCE, draft: Path = DRAFT) -> tuple[dict, list[dict]]:
    originals, translated = read_csv(source), read_csv(draft)
    if len(originals) != len(translated):
        raise ValueError(f"Filas diferentes: {len(originals)} vs {len(translated)}")
    rows = [check_row(a, b) for a, b in zip(originals, translated)]
    statuses = Counter(row["estado"] for row in rows)
    if any(row["estado"] == "BLOQUEADO_FUENTE_MODIFICADA" for row in rows):
        raise ValueError("El borrador alteró metadatos o texto fuente: interrupción obligatoria")
    summary = {
        "tipo": "PREINSERCION_ESTATICA_NO_RUNTIME",
        "total": len(rows),
        "estados": dict(sorted(statuses.items())),
        "candidatos_a_ensayo": statuses["CANDIDATO_A_ENSAYO_NO_VALIDADO"],
        "aprobados_para_insertar": 0,
        "sin_validacion_ppsspp": True,
        "sin_verificacion_ancho_texto": True,
        "sin_demostracion_de_parser_y_punteros": True,
        "codigos_espanoles_experimentales": "F5A0-F5B2",
        "regla": "Si no cabe o faltan metadatos: bloquear. Nunca desplazar tiles, retratos u otros miembros.",
    }
    return summary, rows


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for part in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(part)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--original", type=Path, default=SOURCE)
    parser.add_argument("--borrador", type=Path, default=DRAFT)
    parser.add_argument("--iso", type=Path, help="ISO USA propia: comprobar huella; no escribir sobre ella")
    parser.add_argument("--reporte", type=Path)
    parser.add_argument("--filas", type=Path)
    parser.add_argument("--estricto", action="store_true", help="Fallar si hay cualquier bloqueado (normal durante revisión)")
    args = parser.parse_args()
    if args.iso and file_sha256(args.iso) != SOURCE_SHA256:
        raise ValueError("ISO incorrecta: SHA-256 no coincide")
    summary, rows = audit(args.original, args.borrador)
    result = json.dumps(summary, ensure_ascii=False, indent=2) + "\n"
    print(result)
    if args.reporte:
        args.reporte.parent.mkdir(parents=True, exist_ok=True)
        args.reporte.write_text(result, encoding="utf-8")
    if args.filas:
        args.filas.parent.mkdir(parents=True, exist_ok=True)
        with args.filas.open("w", encoding="utf-8-sig", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=[
                "grupo_id", "text_id", "origen", "revision_es", "bytes_originales",
                "bytes_es", "capacidad", "estado", "aprobado_para_insertar", "detalle",
            ])
            writer.writeheader()
            writer.writerows(rows)
    if args.estricto and summary["candidatos_a_ensayo"] != summary["total"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
