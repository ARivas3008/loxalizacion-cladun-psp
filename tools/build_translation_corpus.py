#!/usr/bin/env python3
"""Construye CSVs de SOLO TEXTO traducible desde la extracción reproducible.

No interpreta ni exporta instrucciones del motor. No requiere los binarios del juego.
Los candidatos de fuentes binarias se conservan como candidatos, nunca como texto verificado.
"""
from __future__ import annotations
import argparse
import collections
import csv
import json
from pathlib import Path

CAMPOS = [
    'text_id','tipo','texto_original','traduccion_es','estado_traduccion','validacion_fuente',
    'fuente','archivo_script','id_script','indice_bloque','orden_en_bloque',
    'offset_hex','longitud_original_bytes','notas'
]

# Transcripción visual *manual* de los seis PNG de SYS.DAT2 examinados.
# El nombre/logo se conserva por trazabilidad, aunque pueda decidirse no traducirlo.
GRAFICOS = [
    ('DOT_NODATA.PNG','NO DATA','mensaje_grafico','confirmado_visual','Requiere modificar el gráfico, no una cadena binaria'),
    ('NODATA.PNG','NO DATA','mensaje_grafico','confirmado_visual','Requiere modificar el gráfico, no una cadena binaria'),
    ('DOT_PIC1.PNG','CLADUN','titulo_grafico','confirmado_visual','Nombre propio; revisar si debe mantenerse'),
    ('DOT_PIC1.PNG','This is an RPG!','titulo_grafico','confirmado_visual','Lema gráfico; si se traduce, requiere editar la imagen'),
    ('PIC1.PNG','CLADUN','titulo_grafico','confirmado_visual','Nombre propio; revisar si debe mantenerse'),
    ('PIC1.PNG','This is an RPG!','titulo_grafico','confirmado_visual','Lema gráfico; si se traduce, requiere editar la imagen'),
    ('DOT_SAVE.PNG','CLADUN','titulo_grafico','confirmado_visual','Nombre propio; revisar si debe mantenerse'),
    ('DOT_SAVE.PNG','This is an RPG!','titulo_grafico','confirmado_visual','Lema gráfico; si se traduce, requiere editar la imagen'),
    ('SAVE.PNG','CLADUN','titulo_grafico','confirmado_visual','Nombre propio; revisar si debe mantenerse'),
    ('SAVE.PNG','This is an RPG!','titulo_grafico','confirmado_visual','Lema gráfico; si se traduce, requiere editar la imagen'),
    ('DOT_NODATA.PNG','dot','rotulo_grafico','pendiente_validacion','Marca/etiqueta decorativa en la imagen: verificar función y traducción'),
    ('DOT_SAVE.PNG','dot','rotulo_grafico','pendiente_validacion','Marca/etiqueta decorativa en la imagen: verificar función y traducción'),
]

def write(path: Path, rows: list[dict]):
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        writer=csv.DictWriter(f,fieldnames=CAMPOS, extrasaction='ignore')
        writer.writeheader();writer.writerows(rows)

def run(root: Path):
    src=root/'corpus/todo_el_texto.csv'
    with src.open(encoding='utf-8-sig',newline='') as f:
        original=list(csv.DictReader(f))
    assert len(original)==9647, 'Corpus inesperado: se debe revisar el generador antes de continuar.'
    allids=[x['text_id'] for x in original]
    assert len(allids)==len(set(allids)), 'Identificadores de texto duplicados.'
    verified=[];pending=[];ignored=[]
    for x in original:
        text=x['original']
        if not text.strip():
            ignored.append((x,'espacio_vacio'))
            continue
        if x['source']=='DATABASE.DAT/LV.DAT':
            ignored.append((x,'datos_numericos_confundidos_con_texto'))
            continue
        trust='confirmado_estructura' if x['confidence']=='confirmado' else 'pendiente_validacion'
        formatted=dict(
            text_id=x['text_id'],tipo=x['category'],texto_original=text,
            traduccion_es='',estado_traduccion='pendiente',validacion_fuente=trust,
            fuente=x['source'],archivo_script=x['script_file'],id_script=x['script_id'],
            indice_bloque=x['file_index'],orden_en_bloque=x['command_index'],
            offset_hex=x['offset_hex'],longitud_original_bytes=x['byte_length'],
            notas='Conservar variables, símbolos y saltos de línea tal como aparecen en el original' if '%' in text else ''
        )
        (verified if trust=='confirmado_estructura' else pending).append(formatted)
    graphics=[]
    for i,(file,label,cat,trust,note) in enumerate(GRAFICOS,1):
        graphics.append(dict(text_id=f'CLD-GFX-{i:04d}',tipo=cat,
              texto_original=label,traduccion_es='',estado_traduccion='pendiente',
              validacion_fuente=trust,fuente='SYS.DAT2/'+file,
              archivo_script='',id_script='',indice_bloque='',orden_en_bloque='',
              offset_hex='',longitud_original_bytes='',notas=note))
    # La tabla maestra conserva estrictamente el orden del corpus original,
    # agregando al final las referencias gráficas en el orden definido arriba.
    full=verified+pending+graphics
    by_id={r['text_id']:r for r in full}
    full=[by_id[x] for x in allids if x in by_id]+graphics
    assert len(full)==len(by_id)
    write(root/'corpus/textos_para_traducir.csv',full)
    write(root/'corpus/confirmados.csv',verified+[g for g in graphics if g['validacion_fuente']=='confirmado_visual'])
    write(root/'corpus/pendientes_validacion.csv',pending+[g for g in graphics if g['validacion_fuente']=='pendiente_validacion'])
    write(root/'corpus/textos_graficos.csv',graphics)
    descartes=[]
    for x,cause in ignored:
        descartes.append(dict(text_id=x['text_id'],tipo='NO_TRADUCIR',texto_original=x['original'],
                   validacion_fuente='descartado',fuente=x['source'],indice_bloque=x['file_index'],
                   offset_hex=x['offset_hex'],notas=cause))
    write(root/'reports/registros_no_traducibles.csv',descartes)
    summary=dict(
        total_registros_raw=len(original),
        confirmados_no_vacios=len(verified),
        candidatos_no_vacios=len(pending),
        graficos_confirmados=sum(g['validacion_fuente']=='confirmado_visual' for g in graphics),
        graficos_por_validar=sum(g['validacion_fuente']=='pendiente_validacion' for g in graphics),
        vacios_descartados=sum(c=='espacio_vacio' for _,c in ignored),
        falsos_positivos_descartados=sum(c=='datos_numericos_confundidos_con_texto' for _,c in ignored),
        total_para_traducir_y_revisar=len(full),
        recuento_por_tipo=dict(collections.Counter(x['tipo'] for x in full)),
        advertencia='Los candidatos necesitan validación; la cobertura absoluta del juego NO está demostrada.'
    )
    (root/'reports/resumen_localizacion.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    assert len(verified)+len(pending)+len(ignored)==len(original)
    assert len(full)==len(verified)+len(pending)+len(graphics)
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Exportar únicamente elementos de texto para traducción')
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);args=parser.parse_args()
    run(args.root)
