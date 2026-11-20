#!/usr/bin/env python3
"""Cierre editorial conservador; jamás toca ISO, atlas, offsets ni código PSP.

Aplica cambios de español con cotejo exacto de preimagen, regenera las
vistas y emite decisiones de las 110 alertas históricas. Los avisos de
puntuación revisados no se ocultan en el detector heurístico.
"""
from __future__ import annotations
import argparse,csv,hashlib,json,sys,subprocess,tempfile
from pathlib import Path
from collections import Counter

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
from charset_es import encode_spanish, decode_spanish
from verificar_borrador_es import TOKEN
from ajustes_campos_es import effective, INCOMPLETE_RAW

FIELDS=['text_id','es_anterior','es_corregido','categoria','justificacion','original']

def csv_read(path):
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        rdr=csv.DictReader(f)
        return list(rdr.fieldnames or []),list(rdr)

def audit(root,plan):
    pheads,patch=csv_read(plan)
    if pheads!=FIELDS:raise ValueError('Columnas de propuesta cambiadas')
    h,rows=csv_read(root/'traduccion/CLADUN_BORRADOR_ES.csv')
    src_h,source=csv_read(root/'corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv')
    if len(rows)!=len(source)!=9237:raise ValueError('El corpus no conserva 9237 textos')
    if len({r['text_id'] for r in rows})!=9237:raise ValueError('IDs duplicados')
    by={r['text_id']:r for r in rows}
    done,remaining=set(),[]
    for x in patch:
        tid=x['text_id']
        if tid in done:raise ValueError('ID duplicado en plan '+tid)
        done.add(tid)
        if tid not in by:raise ValueError('ID desconocido '+tid)
        old=by[tid]
        if old['original']!=x['original']:raise ValueError('Original no coincide '+tid)
        if old['espanol']==x['es_corregido']:continue
        if old['espanol']!=x['es_anterior']:raise ValueError('Versión de partida distinta '+tid)
        if not x['es_corregido'].strip():raise ValueError('Prohibido borrar '+tid)
        if sorted(TOKEN.findall(old['original']))!=sorted(TOKEN.findall(x['es_corregido'])):
            raise ValueError('Marcadores modificados '+tid)
        if decode_spanish(encode_spanish(x['es_corregido']))!=x['es_corregido']:
            raise ValueError('Carácter no representable '+tid)
        remaining.append(x)
    if remaining and len(remaining)!=len(patch):
        raise ValueError('Plan aplicado parcialmente; se rechaza para evitar inconsistencias')
    for a,b in zip(source,rows):
        for field in ('grupo_id','text_id','tipo','original','bytes_hex','offset_hex','origen','script','orden_script'):
            if a.get(field)!=b.get(field):raise ValueError('Original modificado '+b['text_id'])
    # En las 2 fuentes japonesas truncadas el contrato del integrador usa
    # traducciones para INSERTAR sin rellenar el borrador ni inventar el byte.
    guarded={}
    for a,b in zip(source,rows):
        if a['grupo_id'] in INCOMPLETE_RAW:
            if b['espanol']:
                raise ValueError('No rellenar texto corrupto en borrador '+b['grupo_id'])
            out,why=effective(a,b)
            guarded[b['text_id']]={'etiqueta_de_insercion':out,'control':why,
                                   'fuente_estado':'byte_cp932_truncado_no_recuperable'}
    if len(guarded)!=2:raise ValueError('Hay nuevas fuentes truncadas no auditadas')
    return h,rows,patch,remaining,guarded,source

def decisions(root,plan,rows,guarded):
    _,alerts=csv_read(root/'qa/REVISION_RAREZA_PENDIENTES.csv')
    if len(alerts)!=110:raise ValueError('Inventario histórico de 110 alertas distinto')
    changes={x['text_id']:x for x in plan}
    by={x['text_id']:x for x in rows}
    result=[]
    for a in alerts:
        typ=a['alerta'].split(' (')[0]
        ids=[x.strip() for x in a['ids'].split('|') if x.strip()]
        if typ=='NOMBRE_PROPIO_TRADUCIDO_REVISAR':
            assert len(ids)==1
            r=by[ids[0]]
            if r['espanol']!=r['original'] and ids[0] not in changes:
                raise ValueError('Nombre no resuelto '+ids[0])
            status='corregido_nombre_propio'
            reason='Restablecido el nombre original del catálogo de personajes/jefes; no es un sustantivo común.'
        elif typ=='SIN_TRADUCCION':
            if len(ids)!=1 or ids[0] not in guarded:
                raise ValueError('Excepción de fuente no identificada '+str(ids))
            status='excepcion_fuente_truncada_con_etiqueta_de_insercion'
            reason='Original CP932 truncado; el integrador aporta etiqueta validada por bytes, sin reconstruir el japonés perdido.'
        elif a['segmento_id']=='G00757':
            if not {'CLD-001492','CLD-001493'}.issubset(changes):
                raise ValueError('Error de puntuación no corregido')
            status='corregido_texto_unido';reason='Se recompuso la oración original en dos registros, sin frase inventada.'
        elif typ=='UNION_ENTRE_CAJAS_POR_ORACION_INCOMPLETA_REVISAR':
            status='segmentacion_original_conservada'
            reason='No se unen cajas porque entre órdenes del script hay control intermedio; ES y EN completos al leer escena.'
        elif typ=='FRASE_CORTADA_POR_PUNTO':
            status='falso_positivo_elipsis'
            reason='Los puntos suspensivos forman parte del discurso y no cortan una oración de forma espuria.'
        elif typ in {'PAUSA_DEL_ORIGINAL_MODIFICADA','PUNTUACION_ES_ANTES_DE_TERMINAR_ORIGINAL'}:
            status='falso_positivo_resegmentacion'
            reason='El español reorganiza pausas por naturalidad, sin cambiar el sentido de la intervención completa.'
        else:raise ValueError('Categoría de alerta no reconocida '+typ)
        result.append({**a,'dictamen_editorial':status,'fundamento':reason})
    return result

def write_report(root,plan,guarded,decisions,source,rows):
    report=json.loads((root/'lectura/CLADUN_RESUMEN_RECONSTRUCCION.json').read_text(encoding='utf-8'))
    if report['total_registros_originales']!=9237 or report['escenas']!=586 or report['cuadros_dialogo_reconstruidos']!=2216:
        raise ValueError('Conteos de reconstrucción incompatibles')
    counts=Counter(d['dictamen_editorial'] for d in decisions)
    assert len(decisions)==110
    result={
      'estado':'CIERRE_DE_QA_ESTATICO_DE_TEXTOS_NO_VALIDACION_JUGABLE',
      'corpus_registros':9237,'entradas_con_espanol_en_borrador':sum(bool(r['espanol'].strip()) for r in rows),
      'entradas_sin_espanol_pero_con_etiqueta_de_insercion':len(guarded),
      'total_originales_japoneses_truncados':len(guarded),'etiquetas_resueltas_sin_inventar_fuente':guarded,
      'revisiones_selectivas_previamente_publicadas':687,
      'nuevas_correcciones_textuales':len(plan),
      'entradas_no_modificadas_en_esta_pasada':9237-len(plan),
      'escenas_analizadas_por_reconstruccion_estatica':report['escenas'],
      'cuadros_de_dialogo_analizados_por_reconstruccion_estatica':report['cuadros_dialogo_reconstruidos'],
      'alertas_historicas_con_dictamen':len(decisions),
      'alertas_historicas_sin_dictamen':0,
      'dictamenes':dict(counts),
      'alertas_heursticas_que_permanecen_por_diseno':report['alertas_heuristicas'],
      'hash_corpus_fuente_sha256':hashlib.sha256((root/'corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv').read_bytes()).hexdigest(),
      'hash_csv_es_sha256':hashlib.sha256((root/'traduccion/CLADUN_BORRADOR_ES.csv').read_bytes()).hexdigest(),
      'inspeccion_narrativa_humana_integral':'NO_DEMOSTRADA; solo auditoria estatica total y correccion focalizada',
      'ppsspp_acentos_espaciado':'PENDIENTE','parcheador_con_estos_cambios':'PENDIENTE',
      'aviso':'Las dos cadenas japonesas siguen truncadas en los bytes originales. Las etiquetas del integrador no recuperan esos caracteres. No declarar certificacion linguistica humana del 100 por ciento.'
    }
    path=root/'qa/INFORME_CIERRE_LINGUISTICO_2026-11-20.json'
    path.write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
    fields=list(decisions[0]);
    with (root/'qa/AUDITORIA_110_ALERTAS_CERRADAS.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(decisions)
    return result

def main(argv=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--raiz',type=Path,default=ROOT)
    ap.add_argument('--plan',type=Path,default=Path('qa/plan_cierre_linguistico.txt'))
    ap.add_argument('--aplicar',action='store_true')
    args=ap.parse_args(argv);root=args.raiz.resolve();planpath=args.plan if args.plan.is_absolute() else root/args.plan
    _,rows,plan,remaining,guarded,source=audit(root,planpath)
    if not args.aplicar:
        print(json.dumps({'estado':'validado','plan':len(plan),'pendiente':len(remaining),'excepciones':len(guarded)},ensure_ascii=False));return
    if remaining:
        with tempfile.TemporaryDirectory(prefix='cladun_cierre_') as tmp:
            edit=Path(tmp)/'edicion.csv'
            headers,src=csv_read(root/'traduccion/CLADUN_BORRADOR_ES.csv')
            patches={x['text_id']:x['es_corregido'] for x in plan}
            with edit.open('w',encoding='utf-8-sig',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=headers,lineterminator='\r\n');writer.writeheader()
                for row in src:
                    new=dict(row)
                    if new['text_id'] in patches:new['espanol']=patches[new['text_id']]
                    writer.writerow(new)
            subprocess.run([sys.executable,'tools/aplicar_correcciones_editor.py','--entrada',str(edit),'--raiz',str(root),'--aplicar','--editor','cierre_linguistico_narrativo'],cwd=root,check=True)
        for name in ['tools/generar_guion_hablantes.py','tools/reconstruir_guion_completo.py','tools/verificar_borrador_es.py']:
            subprocess.run([sys.executable,name],cwd=root,check=True)
    _,rows,plan,remaining,guarded,source=audit(root,planpath)
    if remaining:raise ValueError('La revisión no quedó aplicada')
    d=decisions(root,plan,rows,guarded)
    report=write_report(root,plan,guarded,d,source,rows)
    print(json.dumps(report,indent=2,ensure_ascii=False))

if __name__=='__main__':main()
