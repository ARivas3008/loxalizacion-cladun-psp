#!/usr/bin/env python3
"""Importa cambios de SOLO `espanol` desde el editor offline.

Modo predeterminado: solo valida y genera un informe; --aplicar es obligatorio
para escribir. Preserva originales y sincroniza ambos TXT históricos, genera
vistas de lectura y una bitácora de cambios, sin tocar binarios/ISO.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

from charset_es import encode_spanish, decode_spanish
from generar_guion_hablantes import cargar, asegurar_fuente, construir, guion, total_texto
from verificar_borrador_es import TOKEN

ROW_HEADER = re.compile(r"(?m)^\[(\d{6})\] [^\n]+\n")
BILI_MARKER = re.compile(r"(?m)^ESPAÑOL \([^\n]*\):\n")
LOG_COLS = ['fecha_utc', 'grupo_id', 'text_id', 'script', 'orden_script', 'espanol_anterior',
            'espanol_nuevo', 'editor', 'nota']


def leer_csv(path:Path):
    with path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        heads=list(reader.fieldnames or [])
        return heads,list(reader)


def validar(antes:list[dict], despues:list[dict], heads1:list[str], heads2:list[str], fuente:list[dict]):
    if heads1 != heads2:raise ValueError('Columnas cambiadas de lugar o renombradas')
    if len(antes)!=9237 or len(despues)!=9237:raise ValueError('Deben conservarse las 9237 filas')
    asegurar_fuente(fuente,despues)
    out=[]
    for old,new in zip(antes,despues):
        ident=old['grupo_id']
        if any(old[col]!=new[col] for col in heads1 if col != 'espanol'):
            raise ValueError(f'La entrada {ident} contiene columnas alteradas, fuera de español')
        if old['espanol']==new['espanol']:continue
        if not new['espanol'].strip():raise ValueError(f'{ident}: no borrar texto español')
        if sorted(TOKEN.findall(old['original'])) != sorted(TOKEN.findall(new['espanol'])):
            raise ValueError(f'{ident}: cambio incompatible de marcador protegido')
        try:
            data=encode_spanish(new['espanol'])
            if decode_spanish(data)!=new['espanol']:
                raise ValueError('Codificación no reversible')
        except (ValueError,UnicodeError) as e:
            raise ValueError(f'{ident}: carácter no insertable: {e}') from e
        out.append((old,new))
    return out


def actualizar_txt(txt:str, changes:list[tuple[dict,dict]], is_bilingual:bool)->str:
    """Conserva bytes textuales de encabezados, y modifica solo contenido de IDs editados."""
    updates={a['grupo_id']:(a,b) for a,b in changes}
    matches=list(ROW_HEADER.finditer(txt))
    if len(matches)!=9237:raise ValueError(f'TXT histórico no tiene 9.237 encabezados: {len(matches)}')
    out=[txt[:matches[0].start()]]
    visited=set()
    for i,m in enumerate(matches):
        end=matches[i+1].start() if i+1<len(matches) else len(txt)
        block=txt[m.start():end]
        key=m.group(1)
        if key in updates:
            old,new=updates[key]
            if is_bilingual:
                marker=BILI_MARKER.search(block)
                if not marker:raise ValueError(f'{key}: falta etiqueta ESPAÑOL en TXT bilingüe')
                at=marker.end()
            else:
                at=m.end()-m.start()
            prev=old['espanol']
            # Las vistas originales llevan el texto español sin comillas extra.
            if not block[at:].startswith(prev):
                raise ValueError(f'{key}: TXT no coincide con CSV (antes de edición)')
            after=at+len(prev)
            if after<len(block) and block[after] not in '\n\r':
                raise ValueError(f'{key}: frontera inesperada en TXT')
            block=block[:at]+new['espanol']+block[after:]
            visited.add(key)
        out.append(block)
    if len(visited)!=len(changes):raise ValueError('Algún grupo a editar no estaba en TXT')
    return ''.join(out)


def serializar_csv(headers:list[str],rows:list[dict])->str:
    buff=io.StringIO(newline='')
    writer=csv.DictWriter(buff,fieldnames=headers,extrasaction='ignore',lineterminator='\r\n')
    writer.writeheader();writer.writerows(rows)
    return '\ufeff'+buff.getvalue()


def main(args=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--entrada',required=True,type=Path,help='CSV exportado por el editor offline')
    ap.add_argument('--raiz',type=Path,default=Path('.'))
    ap.add_argument('--aplicar',action='store_true',help='Escribir CSV, TXT históricos, lectura y QA')
    ap.add_argument('--editor',default='revision_manual',help='Identificador de revisión, sin datos personales')
    opts=ap.parse_args(args)
    root=opts.raiz.resolve()
    csv_path=root/'traduccion/CLADUN_BORRADOR_ES.csv'
    plain=root/'traduccion/CLADUN_BORRADOR_ES.txt'
    bilingual=root/'traduccion/CLADUN_BORRADOR_BILINGUE_FAQ.txt'
    src_path=root/'corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv'
    heads,original=leer_csv(csv_path)
    edit_heads,edited=leer_csv(opts.entrada)
    src=cargar(src_path)
    changes=validar(original,edited,heads,edit_heads,src)
    report={'modo':'aplicado' if opts.aplicar else 'previsualizacion','total_corpus':len(original),
            'entradas_modificadas':len(changes), 'ids':[x['text_id'] for x,_ in changes[:30]],
            'aviso':'Esta operación NO construye ISO ni valida el render de PPSSPP'}
    if not opts.aplicar:
        print(json.dumps(report,ensure_ascii=False,indent=2));return report
    if not changes:
        print(json.dumps(report,ensure_ascii=False,indent=2));return report
    prev_txt=plain.read_text(encoding='utf-8-sig')
    prev_bili=bilingual.read_text(encoding='utf-8-sig')
    new_plain=actualizar_txt(prev_txt,changes,False)
    new_bili=actualizar_txt(prev_bili,changes,True)
    scripts,summary=construir(edited)
    log=root/'qa/correcciones_manuales.csv'
    log_rows=[]
    if log.exists():
        old_headers,log_rows=leer_csv(log)
        if old_headers!=LOG_COLS:raise ValueError('Cabecera de bitácora incompatibles')
    stamp=datetime.now(timezone.utc).isoformat(timespec='seconds')
    for a,b in changes:
        log_rows.append({'fecha_utc':stamp,'grupo_id':a['grupo_id'],'text_id':a['text_id'],
                         'script':a['script'],'orden_script':a['orden_script'],
                         'espanol_anterior':a['espanol'],'espanol_nuevo':b['espanol'],
                         'editor':opts.editor,'nota':'pendiente de revisión visual en PPSSPP'})
    audit_headers=['grupo_id','text_id','tipo','script','script_id','indice_registro','orden_script',
                   'hablante_es','hablante_original','hablante_id','atribucion','distancia_orden','original','espanol']
    writes={
        csv_path:serializar_csv(heads,edited),
        plain:'\ufeff'+new_plain,
        bilingual:'\ufeff'+new_bili,
        root/'lectura/CLADUN_GUION_CON_HABLANTES_ES.txt':'\ufeff'+guion(scripts),
        root/'lectura/CLADUN_LECTURA_TOTAL_CON_HABLANTES_ES.txt':'\ufeff'+total_texto(scripts,edited),
        log:serializar_csv(LOG_COLS,log_rows),
        root/'lectura/CLADUN_AUDITORIA_HABLANTES.csv':serializar_csv(audit_headers,scripts),
    }
    # Guardar backups fuera de los archivos versionados antes de sustituirlos.
    backup=root/'.local/backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup.mkdir(parents=True,exist_ok=False)
    for dest in writes:
        if dest.exists():
            shutil.copy2(dest,backup/dest.name)
    # Asegurar que TODAS las salidas se pueden escribir antes de reemplazarlas.
    with tempfile.TemporaryDirectory(prefix='cladun_edicion_',dir=root) as tmp:
        staged=[]
        for k,(dst,text) in enumerate(writes.items()):
            dst.parent.mkdir(parents=True,exist_ok=True)
            temp=Path(tmp)/str(k)
            temp.write_text(text,encoding='utf-8')
            staged.append((temp,dst))
        for temp,dst in staged:os.replace(temp,dst)
    report['respaldo']=str(backup)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    return report

if __name__=='__main__':main()
