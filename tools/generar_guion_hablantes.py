#!/usr/bin/env python3
"""Genera vistas bilingües trazables de Cladun sin editar sus 9.237 originales.

Los nombres de personaje están en opcodes 0x6E (tipo personaje_interlocutor).
La atribución se limita al mensaje inmediato y los textos contiguos:
la ausencia de otro opcode no autoriza atribuciones indiscriminadas.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import json
from pathlib import Path

TOTAL = 9237
SCRIPT_SOURCE = "SCRIPT.SDT/SCRIPT.DAT"
ALLOWED = {"dialogo", "opcion", "personaje_interlocutor"}


def cargar(ruta: Path) -> list[dict]:
    with ruta.open("r", encoding="utf-8-sig", newline="") as file:
        rows = list(csv.DictReader(file))
    if len(rows) != TOTAL:
        raise ValueError(f"Cantidad de registros inesperada: {len(rows)} (esperados {TOTAL})")
    ids = [r["grupo_id"] for r in rows]
    if len(set(ids)) != len(ids):
        raise ValueError("El CSV tiene grupo_id duplicados")
    return rows


def asegurar_fuente(corpus: list[dict], draft: list[dict]):
    # Estos valores son los que se usan en el contrato del repositorio.
    claves = ("grupo_id", "text_id", "tipo", "campo", "original", "origen", "indice_registro",
              "script", "script_id", "orden_script", "offset_hex", "bytes_hex")
    for original, es in zip(corpus, draft):
        for clave in claves:
            if original.get(clave, "") != es.get(clave, ""):
                raise ValueError(f"Fuente inmutable distinta: {original['grupo_id']} / {clave}")


def id_bloque(row: dict) -> tuple[str, str, str]:
    return row["script"], row["script_id"], row["indice_registro"]


def construir(entradas: list[dict]) -> tuple[list[dict], dict]:
    """Marca seguridad de atribución a partir de nombres 0x6E.

    Solo se considera atribución de continuidad si la separación de órdenes
    entre entradas textuales es 1 o 2. El primer diálogo inmediatamente
    posterior al speaker suele aparecer a +2; se aceptan hasta +6 para ese
    primer diálogo pero se documenta como asociación probable.
    No conocemos todos los cambios de cuadro, así que esto NO es verdad
    narrativa certificada ni inferencia de identidad del personaje.
    """
    salida, conteos = [], Counter()
    grupo_ant = None
    speaker = None
    speaker_es = None
    speaker_ref = None
    order_prev = None
    last_kind = ""
    for row in entradas:
        if row["origen"] != SCRIPT_SOURCE or row["tipo"] not in ALLOWED:
            continue
        current = id_bloque(row)
        if current != grupo_ant:
            speaker = speaker_es = speaker_ref = None
            order_prev = None
            last_kind = ""
            grupo_ant = current
        order = int(row["orden_script"])
        item = dict(row)
        item.update({"hablante_original": "", "hablante_es": "", "hablante_id": "",
                     "atribucion": "sin_hablante_verificable", "distancia_orden": ""})
        if row["tipo"] == "personaje_interlocutor":
            speaker = row["original"].strip()
            speaker_es = (row["espanol"] or row["original"]).strip()
            speaker_ref = row["text_id"]
            item.update({"hablante_original": speaker, "hablante_es": speaker_es,
                         "hablante_id": speaker_ref, "atribucion": "opcode_0x6E_nombre_explicito"})
        else:
            delta = order - order_prev if order_prev is not None else None
            item["distancia_orden"] = "" if delta is None else str(delta)
            if speaker is not None:
                if last_kind == "personaje_interlocutor" and delta is not None and 1 <= delta <= 6:
                    certainty = "primer_mensaje_tras_nombre_probable" if delta > 2 else "primer_mensaje_tras_nombre"
                    item.update({"hablante_original": speaker, "hablante_es": speaker_es,
                                 "hablante_id": speaker_ref, "atribucion": certainty})
                elif last_kind == "dialogo" and delta is not None and 1 <= delta <= 2:
                    item.update({"hablante_original": speaker, "hablante_es": speaker_es,
                                 "hablante_id": speaker_ref, "atribucion": "continuidad_corta_probable"})
                else:
                    # Muchos cambios de interlocutor se realizan mediante otros
                    # comandos no incluidos en el corpus textual. No arrastrar nombres.
                    speaker = speaker_es = speaker_ref = None
            if row["tipo"] == "opcion":
                # Las opciones representan elecciones, no voz de NPC.
                item.update({"hablante_original": "", "hablante_es": "", "hablante_id": "",
                             "atribucion": "opcion_del_jugador"})
                speaker = speaker_es = speaker_ref = None
        last_kind = row["tipo"]
        order_prev = order
        salida.append(item)
        if row["tipo"] != "personaje_interlocutor":
            conteos[item["atribucion"]] += 1
    return salida, dict(conteos)


def guion(rows: list[dict]) -> str:
    parts = [
        "CLADUN: THIS IS AN RPG! (USA/PSP) | GUION DE REVISION BILINGUE",
        "NO ES UN SCRIPT REINSERTABLE. NO MODIFICAR LOS IDENTIFICADORES NI LOS BYTES FUENTE.",
        "El nombre entre corchetes procede de 0x6E o de continuidad corta probable.",
        "[HABLANTE NO VERIFICADO] = no es posible atribuir con seguridad el texto a un personaje.",
        "IMPORTANTE: una nueva ventana o cambio de voz puede ocurrir sin un nuevo 0x6E.", "",
    ]
    current = None
    for row in rows:
        key = id_bloque(row)
        if key != current:
            current = key
            parts += ["", "=" * 85, f"ESCENA: {key[0]} | script_id: {key[1]} | bloque: {key[2]}", "=" * 85]
        if row["tipo"] == "personaje_interlocutor":
            parts += [f"[NOMBRE DE PANTALLA 0x6E] {row['espanol'] or row['original']}  ",
                      f"  id={row['text_id']} | original: {row['original']}"]
            continue
        if row["tipo"] == "opcion":
            title = "[OPCION DEL JUGADOR]"
        else:
            title = "[" + (row["hablante_es"] or "HABLANTE NO VERIFICADO") + "]"
        parts += [f"{title}  [ID {row['text_id']} | grupo {row['grupo_id']} | orden {row['orden_script']}]",
                  f"  ES: {row['espanol'] if row['espanol'] else '[SIN TRADUCCION]'}",
                  f"  EN: {row['original']}",
                  f"  ATRIBUCION: {row['atribucion']}", ""]
    return "\n".join(parts).rstrip() + "\n"


def total_texto(script_rows: list[dict], all_rows: list[dict]) -> str:
    # El guion contiene TODOS los 0x66, 0x69, 0x6E en orden; los restantes se
    # agregan en un apéndice numerado por grupo, nunca se eliminan registros.
    other = [x for x in all_rows if x["origen"] != SCRIPT_SOURCE or x["tipo"] not in ALLOWED]
    parts = [guion(script_rows).rstrip(), "", "#" * 85,
             f"APENDICE: OTROS ELEMENTOS DE TEXTO ({len(other)})", "#" * 85]
    last_category = None
    for row in other:
        if row["tipo"] != last_category:
            last_category = row["tipo"]
            parts += ["", f"--- {last_category.upper()} ---", ""]
        parts += [f"[{row['text_id']}] grupo={row['grupo_id']} recurso={row['origen']}",
                  f"  ES: {row['espanol'] or '[SIN TRADUCCION]'}",
                  f"  EN: {row['original']}", ""]
    return "\n".join(parts).rstrip() + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--fuente", type=Path, default=Path("corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv"))
    p.add_argument("--borrador", type=Path, default=Path("traduccion/CLADUN_BORRADOR_ES.csv"))
    p.add_argument("--salida", type=Path, default=Path("lectura"))
    args = p.parse_args(argv)
    source = cargar(args.fuente)
    draft = cargar(args.borrador)
    asegurar_fuente(source, draft)
    script_rows, counts = construir(draft)
    args.salida.mkdir(parents=True, exist_ok=True)
    (args.salida / "CLADUN_GUION_CON_HABLANTES_ES.txt").write_text(guion(script_rows), encoding="utf-8-sig")
    (args.salida / "CLADUN_LECTURA_TOTAL_CON_HABLANTES_ES.txt").write_text(total_texto(script_rows, draft), encoding="utf-8-sig")
    fieldnames = ["grupo_id", "text_id", "tipo", "script", "script_id", "indice_registro", "orden_script",
                  "hablante_es", "hablante_original", "hablante_id", "atribucion", "distancia_orden",
                  "original", "espanol"]
    with (args.salida / "CLADUN_AUDITORIA_HABLANTES.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        w.writeheader()
        w.writerows(script_rows)
    status = {"total_csv": len(draft), "total_texto_script": len(script_rows),
              "total_fuera_script": len(draft) - len(script_rows),
              "conteos_atribucion": counts,
              "csv_fuente_sha256": hashlib.sha256(args.fuente.read_bytes()).hexdigest(),
              "csv_borrador_sha256": hashlib.sha256(args.borrador.read_bytes()).hexdigest(),
              "aviso": "Atribución de guion es una guía y no evidencia visual completa. Debe cotejarse en PPSSPP."}
    (args.salida / "CLADUN_RESUMEN_HABLANTES.json").write_text(
        json.dumps(status, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(status, indent=2, ensure_ascii=False))
    return status


if __name__ == "__main__":
    main()
