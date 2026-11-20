#!/usr/bin/env python3
"""Consolida el plan lingüístico sin tocar la ISO ni los metadatos de extracción.

Entrada: qa/plan_revision_consolidada_2026-11-20.csv, con preimagen exacta.
Rechaza borradores parcialmente aplicados, marcadores rotos, códigos no
representables o cambios en campos distintos de `espanol`.
Usa el importador existente para mantener CSV, TXT, lecturas y bitácora.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

from aplicar_correcciones_editor import leer_csv, serializar_csv, validar
from generar_guion_hablantes import cargar

ROOT = Path(__file__).resolve().parents[1]
FIELDS = ["grupo_id", "text_id", "tipo", "original", "es_anterior",
          "es_corregido", "motivo"]
PLAN = ROOT / "qa/plan_revision_consolidada_2026-11-20.csv"
DRAFT = ROOT / "traduccion/CLADUN_BORRADOR_ES.csv"
SOURCE = ROOT / "corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv"
REPORT = ROOT / "qa/INFORME_REVISION_CONSOLIDADA_2026-11-20.json"
IMMUTABLE = ("grupo_id", "text_id", "tipo", "campo", "original",
             "origen", "indice_registro", "script", "script_id",
             "orden_script", "offset_hex", "capacidad_campo",
             "longitud_original_bytes", "bytes_hex", "idioma_origen")


def check(root: Path = ROOT):
    planpath = root / "qa/plan_revision_consolidada_2026-11-20.csv"
    header, plan = leer_csv(planpath)
    if header != FIELDS or not plan:
        raise ValueError("Plan vacío o columnas alteradas")
    h, existing = leer_csv(root / "traduccion/CLADUN_BORRADOR_ES.csv")
    sh, source = leer_csv(root / "corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv")
    if len(existing) != len(source) != 9237:
        raise ValueError("Número de registros distinto de 9237")
    if len(existing) != 9237:
        raise ValueError("El inventario no tiene 9237 entradas")
    for orig, dest in zip(source, existing):
        if any(orig.get(k) != dest.get(k) for k in IMMUTABLE):
            raise ValueError("Campo canónico alterado: " + dest["grupo_id"])
    by_id = {row["grupo_id"]: row for row in existing}
    if len(by_id) != 9237:
        raise ValueError("ID duplicado en corpus")
    seen = set()
    pending = []
    done = []
    edited = [dict(row) for row in existing]
    by_edited = {row["grupo_id"]: row for row in edited}
    for p in plan:
        gid = p["grupo_id"]
        if gid in seen or gid not in by_id:
            raise ValueError("ID repetido o ausente: " + gid)
        seen.add(gid)
        r = by_id[gid]
        for k in ("text_id", "tipo", "original"):
            if r[k] != p[k]:
                raise ValueError("Preimagen de origen incompatible: " + gid)
        if not p["motivo"].strip() or not p["es_corregido"].strip():
            raise ValueError("Traducción o justificación vacía: " + gid)
        if p["es_anterior"] == p["es_corregido"]:
            raise ValueError("Corrección sin cambio: " + gid)
        if r["espanol"] == p["es_corregido"]:
            done.append(gid)
        elif r["espanol"] == p["es_anterior"]:
            pending.append(gid)
            by_edited[gid]["espanol"] = p["es_corregido"]
        else:
            raise ValueError("Cambio ajeno al plan en " + gid)
    if pending and done:
        raise ValueError("Plan aplicado parcialmente; no se permiten mezclas")
    # Verifica todos los 9.237 originales, marcadores y codificación antes
    # de modificar un solo archivo.
    source_canonical = cargar(root / "corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv")
    changes = validar(existing, edited, h, h, source_canonical)
    if len(changes) != len(pending):
        raise ValueError("La validación no coincide con los IDs pendientes")
    return h, edited, plan, pending, done


def report(root: Path, plan: list[dict], pending: list[str],
           done: list[str]):
    _, translated = leer_csv(root / "traduccion/CLADUN_BORRADOR_ES.csv")
    count = Counter(row["tipo"] for row in translated)
    exceptions = [r["grupo_id"] for r in translated if not r["espanol"]]
    if exceptions != ["008723", "008724"]:
        raise ValueError("Las únicas dos excepciones deben ser los campos japoneses truncados")
    return {
        "estado": "CORPUS_COMPLETO_AUDITADO_ESTRUCTURALMENTE; EDICION_NARRATIVA_TOTAL_NO_CERTIFICADA",
        "registros": len(translated),
        "con_espanol": len(translated) - len(exceptions),
        "excepciones_fuente_japonesa": exceptions,
        "correcciones_planificadas": len(plan),
        "correcciones_pendientes": len(pending),
        "correcciones_aplicadas": len(done),
        "tipos_de_texto_verificados": dict(sorted(count.items())),
        "fuente_sha256": hashlib.sha256((root / "corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv").read_bytes()).hexdigest(),
        "traduccion_sha256": hashlib.sha256((root / "traduccion/CLADUN_BORRADOR_ES.csv").read_bytes()).hexdigest(),
        "plan_sha256": hashlib.sha256((root / "qa/plan_revision_consolidada_2026-11-20.csv").read_bytes()).hexdigest(),
        "sin_modificar_originales_y_offsets": True,
        "controles_textuales": "IDs, origen, texto fuente, bytes, offsets, marcadores, codificación, TXT y vistas regenerados",
        "reparacion_segundo_nivel_y_enciclopedia": "NO_DEMOSTRADA; requiere ejecución PPSSPP",
        "parche_binario_regenerado": False,
        "revision_narrativa_humana_9237": "NO_CERTIFICADA: revisión integral estructural y post-edición focalizada",
    }


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--aplicar", action="store_true")
    ap.add_argument("--raiz", type=Path, default=ROOT)
    args = ap.parse_args(argv)
    root = args.raiz.resolve()
    headers, edited, plan, pending, done = check(root)
    if args.aplicar and pending:
        with tempfile.TemporaryDirectory(prefix="cladun_rev_") as tmp:
            temp = Path(tmp) / "editado.csv"
            temp.write_text(serializar_csv(headers, edited), encoding="utf-8")
            subprocess.run([
                sys.executable, "tools/aplicar_correcciones_editor.py",
                "--entrada", str(temp), "--raiz", str(root),
                "--editor", "revision_consolidada_2026-11-20", "--aplicar"
            ], check=True, cwd=root)
        for tool in ("tools/generar_guion_hablantes.py",
                     "tools/reconstruir_guion_completo.py"):
            subprocess.run([sys.executable, tool], check=True, cwd=root)
    _, _, plan, pending, done = check(root)
    info = report(root, plan, pending, done)
    if args.aplicar:
        if pending:
            raise ValueError("No se aplicó todo el plan")
        (root / "qa/INFORME_REVISION_CONSOLIDADA_2026-11-20.json").write_text(
            json.dumps(info, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(json.dumps(info, ensure_ascii=False, indent=2))
    return info


if __name__ == "__main__":
    main()
