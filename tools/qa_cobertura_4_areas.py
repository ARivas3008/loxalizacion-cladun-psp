#!/usr/bin/env python3
"""Verifica la veracidad estructural de la cobertura T/G/R/Q (no ejecuta el juego).

Un PASS de este validador solo acredita consistencia documental y nunca QA C.
"""
from __future__ import annotations
import argparse
import csv
import json
from pathlib import Path

REQUIRED = ('caso_id', 'área', 'modo/escena', 'precondición', 'save_state',
            'pasos_reproducibles', 'expectativa_original', 'expectativa_es',
            'ISO_SHA256', 'PPSSPP_version_hash_backend', 'tipo_evidencia',
            'evidencia_sha256_privada', 'estado', 'bloqueo', 'issue', 'commit_resolucion')
AREAS = ('traduccion', 'graficos', 'romhacking', 'betatesting')
STATES = {'PASS', 'FAIL', 'BLOCKED', 'NOT_RUN'}

def is_sha(value: str) -> bool:
    return len(value) == 64 and all(c in '0123456789abcdef' for c in value.lower())

def fraction(obj, label: str, *, complete: bool = False) -> None:
    if not isinstance(obj, dict) or 'hechos' not in obj or 'total' not in obj:
        raise ValueError(f'{label}: faltan hechos/total')
    a, b = obj['hechos'], obj['total']
    if a is None or b is None:
        if complete:
            raise ValueError(f'{label}: cobertura desconocida no cierra al 100%')
        if a is not None or b is not None:
            raise ValueError(f'{label}: fracción incompleta')
        return
    if type(a) is not int or type(b) is not int or b <= 0 or not 0 <= a <= b:
        raise ValueError(f'{label}: fracción inválida')
    if complete and a != b:
        raise ValueError(f'{label}: no hay cobertura completa')

def inspect(coverage: dict, rows: list[dict]) -> dict:
    if coverage.get('schema') != 'cladun.cobertura_cuatro_areas.v1':
        raise ValueError('Esquema de cobertura no reconocido')
    if not rows:
        raise ValueError('No hay casos QA; no equivale a 100%')
    seen = set()
    stats = {x: 0 for x in STATES}
    for r in rows:
        if not all(k in r for k in REQUIRED):
            raise ValueError('Falta columna en matriz QA')
        cid = r['caso_id']
        if not cid or cid in seen:
            raise ValueError('Caso QA vacío o duplicado')
        seen.add(cid)
        if not r['modo/escena'] or not r['pasos_reproducibles'] or not r['expectativa_es']:
            raise ValueError(f'{cid}: especificación de caso insuficiente')
        state = r['estado']
        if state not in STATES:
            raise ValueError(f'{cid}: estado inválido')
        stats[state] += 1
        if state == 'PASS':
            if (r['tipo_evidencia'] != 'C' or not is_sha(r['ISO_SHA256'])
                or not is_sha(r['evidencia_sha256_privada'])
                or not r['PPSSPP_version_hash_backend'] or r['bloqueo']):
                raise ValueError(f'{cid}: PASS sin evidencia runtime suficiente')
    for area in AREAS:
        if area not in coverage or type(coverage[area].get('cierre_100')) is not bool:
            raise ValueError(f'{area}: estado de cierre inválido')
    t, g, r, q = (coverage[a] for a in AREAS)
    fraction(t['borrador'], 'traduccion.borrador')
    fraction(t['aprobados_contextualmente'], 'traduccion.aprobados_contextualmente', complete=t['cierre_100'])
    fraction(t['en_juego'], 'traduccion.en_juego', complete=t['cierre_100'])
    fraction(g['aprobados_ppsspp'], 'graficos.aprobados_ppsspp', complete=g['cierre_100'])
    fraction(q['aprobados'], 'betatesting.aprobados', complete=q['cierre_100'])
    fraction(r['sustituciones'], 'romhacking.sustituciones', complete=r['cierre_100'])
    if any(x['cierre_100'] for x in (t,g,r,q)):
        if t['cierre_100'] and (not t['inventario_visible_completo'] or t['borrador']['hechos'] != t['borrador']['total']):
            raise ValueError('Traducción cerrada con textos pendientes o sin inventario')
        if g['cierre_100'] and not g['inventario_completo']:
            raise ValueError('Gráficos cerrados sin inventario total')
        if r['cierre_100'] and (r['diferidas'] != 0 or not r['relocalizaciones_seguras_demostradas'] or not r['release_bps_exe_e2e']):
            raise ValueError('ROMhacking cerrado sin reubicación y E2E')
        if q['cierre_100'] and (not q['matriz_completa'] or stats['PASS'] != len(rows) or q['aprobados'] != {'hechos': len(rows), 'total': len(rows)} or q['p0_p1_abiertos'] != 0):
            raise ValueError('Betatesting cerrado con casos/bloqueos abiertos')
    return {'total_casos':len(rows),'estados':stats,'areas_cerradas':[a for a in AREAS if coverage[a]['cierre_100']],
            'reporte':'VALIDACION_DE_METADATOS_SOLAMENTE_NO_ES_PPSSPP'}

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--cobertura', type=Path, default=Path('reports/COBERTURA_4_AREAS.json'))
    ap.add_argument('--matriz', type=Path, default=Path('qa/MATRIZ_BETATESTING_COBERTURA.csv'))
    ap.add_argument('--require-closed', action='store_true')
    args = ap.parse_args()
    coverage = json.loads(args.cobertura.read_text(encoding='utf-8'))
    with args.matriz.open(encoding='utf-8-sig', newline='') as f:
        reader=csv.DictReader(f)
        if reader.fieldnames != list(REQUIRED):
            raise ValueError('Encabezados inesperados en matriz QA')
        rows=list(reader)
    result=inspect(coverage, rows)
    print(json.dumps(result,ensure_ascii=False,sort_keys=True))
    return 1 if args.require_closed and len(result['areas_cerradas']) != len(AREAS) else 0

if __name__ == '__main__':
    raise SystemExit(main())
