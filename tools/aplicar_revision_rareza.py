#!/usr/bin/env python3
"""Aplica SOLO las correcciones de rareza justificadas en un libro mayor CSV.

No edita IDs, ingles, offsets, otros metadatos ni recursos PSP. Coteja las
alertas originales; exige preimagen exacta; por defecto solo verifica.
El modo --aplicar usa el importador de Cladun para mantener sincronizados
ambos TXT antiguos y las vistas de guion, con respaldos locales.
"""
from __future__ import annotations
import argparse
import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from collections import Counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from charset_es import encode_spanish, decode_spanish
from verificar_borrador_es import TOKEN

LEDGER_FIELDS = ('text_id', 'es_anterior', 'es_corregido', 'motivo', 'segmento')


def leer(path: Path):
    with path.open(encoding='utf-8-sig', newline='') as f:
        rdr = csv.DictReader(f)
        return list(rdr.fieldnames or []), list(rdr)


def _ids_alertados(alerts: list[dict]) -> set[str]:
    found = set()
    for a in alerts:
        found.update(t.strip() for t in a['ids'].split('|') if t.strip())
    return found


def validar_plan(rows: list[dict], ledger: list[dict], alerts: list[dict]) -> tuple[str, list[dict]]:
    if len(rows) != 9237:
        raise ValueError('El corpus de trabajo no tiene 9237 entradas')
    ids = {r['text_id']: r for r in rows}
    if len(ids) != len(rows):
        raise ValueError('ID de texto repetido en el corpus')
    allowed = _ids_alertados(alerts)
    if not ledger:
        raise ValueError('No hay correcciones')
    changed = []
    seen = set()
    done = 0
    for a in ledger:
        key = a['text_id']
        if key in seen:
            raise ValueError(f'Corrección duplicada: {key}')
        seen.add(key)
        if key not in ids or key not in allowed:
            raise ValueError(f'ID ajeno a las rarezas auditadas: {key}')
        old = ids[key]
        new = a['es_corregido']
        if not new or not new.strip():
            raise ValueError(f'No se permite borrar traducción: {key}')
        if a['es_anterior'] == new:
            raise ValueError(f'No hay cambio real: {key}')
        if sorted(TOKEN.findall(old['original'])) != sorted(TOKEN.findall(new)):
            raise ValueError(f'Marcador incompatible en {key}')
        try:
            if decode_spanish(encode_spanish(new)) != new:
                raise ValueError('codificación no reversible')
        except (ValueError, UnicodeError) as e:
            raise ValueError(f'Codificación inválida {key}: {e}') from e
        if old['espanol'] == new:
            done += 1
        elif old['espanol'] == a['es_anterior']:
            changed.append(a)
        else:
            raise ValueError(f'El texto original del plan no coincide con la rama: {key}')
    if changed and done:
        raise ValueError('Estado parcialmente aplicado; no se permite una aplicación mixta')
    return ('ya_aplicado' if done == len(ledger) else 'pendiente'), changed


def ejecutar(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--raiz', type=Path, default=ROOT)
    ap.add_argument('--plan', type=Path, default=Path('qa/revision_rareza_2026-11-20.csv'))
    ap.add_argument('--aplicar', action='store_true')
    args = ap.parse_args(argv)
    root = args.raiz.resolve()
    plan = args.plan if args.plan.is_absolute() else root / args.plan
    csv_path = root / 'traduccion/CLADUN_BORRADOR_ES.csv'
    prev_alerts = root / 'qa/alertas_reconstruccion_antes_revision.csv'
    heads, rows = leer(csv_path)
    pheads, ledger = leer(plan)
    if pheads != list(LEDGER_FIELDS):
        raise ValueError('Columnas del plan alteradas')
    _, alerts = leer(prev_alerts)
    status, pending = validar_plan(rows, ledger, alerts)
    origin_hash = hashlib.sha256((root / 'corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv').read_bytes()).hexdigest()
    summary = {'estado':status, 'total_corpus':len(rows), 'correcciones_justificadas':len(ledger),
               'entradas_sin_modificar':len(rows)-len(ledger),
               'cambios_nombres':sum(x['motivo'].startswith('Nombre propio') for x in ledger),
               'cambios_contexto':sum(x['motivo'].startswith('Comparación') for x in ledger),
               'cambios_puntuacion':sum(x['motivo'].startswith('Punto') for x in ledger),
               'fuente_original_sha256':origin_hash,
               'excepcion':'2 fragmentos japoneses de origen truncado quedan sin reconstruir',
               'advertencia':'Cambios editoriales: NO implican validación visual PPSSPP ni nuevo parche compilado'}
    if not args.aplicar or status == 'ya_aplicado':
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return summary
    patch = {x['text_id']: x['es_corregido'] for x in pending}
    with tempfile.TemporaryDirectory(prefix='cladun_rareza_') as tempdir:
        edited = Path(tempdir) / 'CLADUN_BORRADOR_ES_CORREGIDO.csv'
        with edited.open('w', encoding='utf-8-sig', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=heads, lineterminator='\r\n')
            writer.writeheader()
            for row in rows:
                output = dict(row)
                if output['text_id'] in patch:
                    output['espanol'] = patch[output['text_id']]
                writer.writerow(output)
        subprocess.run([sys.executable, 'tools/aplicar_correcciones_editor.py',
                        '--entrada', str(edited), '--raiz', str(root),
                        '--aplicar', '--editor', 'revision_rareza_2026-11-20'],
                       cwd=root, check=True)
    # Las vistas se regeneran de los datos nuevos, no a partir del informe.
    for tool in ('tools/generar_guion_hablantes.py', 'tools/reconstruir_guion_completo.py',
                 'tools/verificar_borrador_es.py'):
        subprocess.run([sys.executable,tool], cwd=root, check=True)
    # Cotejo final del libro mayor y de las excepciones preservadas.
    _, current = leer(csv_path)
    assert validar_plan(current, ledger, alerts)[0] == 'ya_aplicado'
    report = json.loads((root/'lectura/CLADUN_RESUMEN_RECONSTRUCCION.json').read_text(encoding='utf-8'))
    summary['estado'] = 'aplicado'
    summary['alertas_residuales'] = report['alertas_heuristicas']
    summary['total_alertas_residuales'] = sum(report['alertas_heuristicas'].values())
    summary['csv_traduccion_sha256'] = hashlib.sha256(csv_path.read_bytes()).hexdigest()
    out = root / 'qa/INFORME_REVISION_RAREZA_2026-11-20.json'
    out.write_text(json.dumps(summary, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    # La lista remanente es una cola de validación, no una orden de sustitución.
    _, residual = leer(root / 'lectura/CLADUN_ALERTAS_RECONSTRUCCION.csv')
    def clasificar(x):
        tag=x['alerta'].split(' (',1)[0]
        if tag=='SIN_TRADUCCION':
            return ('origen_truncado_no_inventar', 'Requiere inspección de bytes originales antes de traducir')
        if tag=='NOMBRE_PROPIO_TRADUCIDO_REVISAR':
            return ('nombre_descriptivo_o_apodo_pendiente', 'No cambiar sin comprobar su identidad en el juego')
        if tag=='UNION_ENTRE_CAJAS_POR_ORACION_INCOMPLETA_REVISAR':
            return ('inferencia_de_segmentacion', 'No unir más cajas sin verificar el flujo de opcodes')
        return ('heuristica_pendiente_de_contexto', 'No se hizo sustitución sin evidencia suficiente')
    pend = root / 'qa/REVISION_RAREZA_PENDIENTES.csv'
    with pend.open('w',encoding='utf-8-sig',newline='') as f:
        fields=['segmento_id','escena','ids','alerta','estado_revision','motivo','espanol_unido','original_unido']
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for x in residual:
            state,detail=clasificar(x)
            w.writerow({**x,'estado_revision':state,'motivo':detail})
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return summary


if __name__ == '__main__':
    ejecutar()
