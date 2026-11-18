#!/usr/bin/env python3
"""QA reproducible del corpus de texto (sin requerir la ISO)."""
from __future__ import annotations
import argparse
import collections
import csv
import hashlib
import json
import re
from pathlib import Path

REQUIRED = ('grupo_id', 'text_id', 'tipo', 'original', 'espanol', 'estado',
            'revision_fuente', 'origen', 'offset_hex', 'bytes_hex',
            'longitud_original_bytes')
ESTADOS = {'pendiente_traduccion', 'requiere_comprobar_en_juego', 'requiere_reconstruccion'}

def rows(path: Path):
    with path.open('r', encoding='utf-8-sig', newline='') as stream:
        return list(csv.DictReader(stream))

def verificar(root: Path, *, guardar: bool = False) -> dict:
    master = root/'corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv'
    txt = root/'corpus/CLADUN_TODO_TEXTO_ORIGINAL.txt'
    valid = root/'corpus/confirmados_formato.csv'
    pend = root/'corpus/revisar_visibilidad.csv'
    decisiones = root/'qa/decisiones_auditoria.csv'
    data = rows(master)
    assert data, 'Corpus vacío'
    assert all(k in data[0] for k in REQUIRED), 'Cabeceras incompletas'
    ids, seq = set(), []
    errores = []
    for i, row in enumerate(data, 1):
        tag = row['text_id']
        seq.append(row['grupo_id'])
        if tag in ids: errores.append(f'ID duplicado: {tag}')
        ids.add(tag)
        if row['grupo_id'] != f'{i:06d}': errores.append(f'Orden inconsistente en {tag}')
        if not row['original'].strip(): errores.append(f'Texto vacío: {tag}')
        if row['espanol']: errores.append(f'Ya traducido: {tag}')
        if row['estado'] not in ESTADOS: errores.append(f'Estado desconocido: {tag}')
        if not row['origen']: errores.append(f'Falta fuente: {tag}')
        if row['offset_hex'] and not re.fullmatch(r'0x[0-9A-Fa-f]+', row['offset_hex']):
            errores.append(f'Offset inválido: {tag}')
        try: raw=bytes.fromhex(row['bytes_hex'])
        except ValueError:
            errores.append(f'Hex inválido: {tag}');continue
        length=row['longitud_original_bytes']
        if length and len(raw)!=int(length): errores.append(f'Longitud original inconsistente: {tag}')
        if raw and raw.decode('cp932',errors='replace')!=row['original']:
            errores.append(f'Bytes y texto distintos: {tag}')
    confirmados=rows(valid); pendientes=rows(pend)
    if len(confirmados)+len(pendientes)!=len(data):
        errores.append('Los subconjuntos no suman el total')
    if [r['text_id'] for r in confirmados] != [r['text_id'] for r in data if r['estado']=='pendiente_traduccion']:
        errores.append('Confirmados no coinciden con corpus maestro')
    if [r['text_id'] for r in pendientes] != [r['text_id'] for r in data if r['estado']!='pendiente_traduccion']:
        errores.append('Pendientes no coinciden con corpus maestro')
    text=txt.read_text(encoding='utf-8-sig')
    found=re.findall(r'^========== GRUPO (\d{6}) \| ID (.+?) ==========$',text,re.M)
    if found != [(r['grupo_id'],r['text_id']) for r in data]:
        errores.append('Orden y contenido de cabeceras TXT no coinciden')
    if len(re.findall(r'^========== FIN GRUPO \d{6} ==========$',text,re.M))!=len(data):
        errores.append('Cantidad de delimitadores TXT incorrecta')
    summary=json.loads((root/'reports/resumen.json').read_text(encoding='utf-8'))
    if summary['total_bloques_texto']!=len(data): errores.append('Informe de cobertura inconsistente')
    aud=rows(decisiones)
    if summary['auditoria_registros']!=len(aud): errores.append('Traza de auditoría inconsistente')
    report={
        'resultado':'OK' if not errores else 'ERROR',
        'bloques_originales':len(data),
        'fuente_formato_confirmado':len(confirmados),
        'pendientes_uso_o_decodificacion':len(pendientes),
        'registros_auditoria':len(aud),
        'distribucion_estados':dict(collections.Counter(r['estado'] for r in data)),
        'sha256_csv':hashlib.sha256(master.read_bytes()).hexdigest(),
        'sha256_txt':hashlib.sha256(txt.read_bytes()).hexdigest(),
        'errores':errores[:100]
    }
    if guardar:
        p=root/'reports/qa_integridad.json';p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return report

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--raiz',type=Path,default=Path(__file__).resolve().parent.parent)
    ap.add_argument('--guardar',action='store_true')
    args=ap.parse_args()
    result=verificar(args.raiz,guardar=args.guardar)
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(0 if result['resultado']=='OK' else 1)
