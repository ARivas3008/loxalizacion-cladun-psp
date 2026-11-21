#!/usr/bin/env python3
"""F1 QA: mide PNG auténticos entregados externamente; NO autentica su origen.

El autor debe proporcionar capturas sin editar desde PPSSPP real. Este programa
solo verifica los bytes PNG y su geometría; jamás genera capturas del juego.
La medición y=106 vale para Opciones en Xvfb 1280x720, ventana 960x544+160+88.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image

EXPECTED_RESOLUTION = (1280, 720)
ROW = 106
LEFT, RIGHT = 160, 1104
THRESHOLD = 125
EXPECTED_F1_RIGHT = 1097
PNG_SIGNATURE = bytes.fromhex("89504E470D0A1A0A")


def sha256_file(path: Path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def measure_options(image):
    """Segmento más largo con R,G,B > 125 en fila y=106 y x=160..1104."""
    if image.size != EXPECTED_RESOLUTION:
        raise ValueError("Se requiere PNG 1280x720 sin reescalar")
    rgb = image.convert("RGB")
    line = [all(channel > THRESHOLD for channel in rgb.getpixel((x, ROW)))
            for x in range(LEFT, RIGHT + 1)]
    spans, start = [], None
    for k, light in enumerate(line + [False]):
        if light and start is None:
            start = k
        elif not light and start is not None:
            spans.append((LEFT + start, LEFT + k - 1))
            start = None
    if not spans:
        raise ValueError("No se encontró segmento brillante en la fila y=106")
    begin, end = max(spans, key=lambda pair: pair[1] - pair[0])
    inside = end - begin + 1
    if inside < 300 or end > RIGHT:
        raise ValueError("Ventana no reconocida; verificar imagen/posición")
    return {
        "fila_y": ROW, "intervalo_x": [LEFT, RIGHT], "umbral_rgb_estrictamente_mayor": THRESHOLD,
        "borde_izquierdo_x": begin, "borde_derecho_x": end,
        "interior_px": inside,
        "exterior_estimado_px": inside + 8,
        "metodo": "Segmento máximo brillante; exterior +8 px aproximado; NO detección semántica",
    }


def analyze_manifest(manifest_path, *, require_two_states=False):
    manifest_path = Path(manifest_path)
    content = json.loads(manifest_path.read_text(encoding="utf-8"))
    if content.get("schema") != "cladun.f1.ppsspp_png_inputs.v1":
        raise ValueError("Esquema de manifiesto no reconocido")
    entries = content.get("capturas")
    if not isinstance(entries, list) or not entries:
        raise ValueError("No hay PNG en el manifiesto")
    unique = set()
    screens = {}
    versions = {}
    result = []
    for item in entries:
        if not all(isinstance(item.get(k), str) and item[k].strip()
                   for k in ("ruta", "pantalla", "version", "estado")):
            raise ValueError("Faltan campos de captura")
        source = Path(item["ruta"]).expanduser()
        if not source.is_absolute():
            source = (manifest_path.parent / source).resolve()
        key = (item["pantalla"], item["version"], item["estado"])
        if key in unique:
            raise ValueError("Captura/estado repetido: " + str(key))
        unique.add(key)
        if not source.is_file():
            raise FileNotFoundError(source)
        with source.open("rb") as check:
            if check.read(8) != PNG_SIGNATURE:
                raise ValueError("Archivo no es un PNG: " + str(source))
        checksum = sha256_file(source)
        expected = item.get("sha256_esperado")
        if expected is not None and (not isinstance(expected, str) or checksum != expected.lower()):
            raise ValueError("SHA-256 PNG difiere de la evidencia: " + str(source))
        with Image.open(source) as image:
            if image.format != "PNG" or image.size != EXPECTED_RESOLUTION:
                raise ValueError("Formato o resolución no coinciden: " + str(source))
            row = {"archivo": str(source), "sha256_png": checksum,
                   "pantalla": item["pantalla"], "version": item["version"],
                   "estado": item["estado"], "resolucion": list(image.size)}
            if item["pantalla"].casefold() == "opciones":
                row["medicion"] = measure_options(image)
        result.append(row)
        screens.setdefault((item["version"], item["pantalla"]), set()).add(item["estado"])
        versions.setdefault(item["version"], set()).add(item["pantalla"])
    if require_two_states:
        incomplete = [f"{version}:{screen}" for (version, screen), states in screens.items()
                      if len(states) < 2]
        if incomplete:
            raise ValueError("Faltan dos estados por versión/pantalla: " + ", ".join(incomplete))
    return {
        "schema": "cladun.f1.png_metrics.v1",
        "estado": "METRICAS_DE_PNG_NO_CERTIFICAN_AUTENTICIDAD_PPSSPP",
        "origen_capturas": content.get("origen", "PROCEDENCIA_DECLARADA_POR_OPERADOR_NO_COMPROBABLE"),
        "cantidad_capturas_png": len(result),
        "requiere_2_estados": bool(require_two_states),
        "capturas": result,
        "notas": [
            "Ningún PNG ha sido generado ni modificado por la herramienta",
            "El SHA autentica bytes, no que procedan de una sesión PPSSPP real",
            "El segmento corresponde a la fila y=106, solo pantalla Opciones",
            "Sin comparar contra una sesión real, F1 permanece abierta",
        ]
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifiesto", required=True, type=Path)
    parser.add_argument("--reporte", required=True, type=Path)
    parser.add_argument("--exigir-dos-estados", action="store_true")
    a = parser.parse_args()
    if a.reporte.exists() or a.reporte.resolve() == a.manifiesto.resolve():
        raise FileExistsError("Informe debe ser archivo nuevo e independiente")
    data = analyze_manifest(a.manifiesto, require_two_states=a.exigir_dos_estados)
    a.reporte.parent.mkdir(parents=True, exist_ok=True)
    with a.reporte.open("x", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({k:v for k,v in data.items() if k!="capturas"},ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()
