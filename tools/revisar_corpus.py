#!/usr/bin/env python3
"""Audita los campos textuales de Cladun PSP y crea un corpus sin traducciones.

Lee la ISO propia y la extracción intermedia generada por extract_cladun.py.
Separa cadenas textuales de nombres de archivo internos y falsos positivos.
No genera ni guarda instrucción/opcode alguno como salida de localización.
"""
from __future__ import annotations
import argparse, collections, csv, hashlib, json, re
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from extract_cladun import (iso9660_entries, read_iso_file, pspfs_entries,
                            decompress, dsarc_entries)

@dataclass(frozen=True)
class Campo:
    desplazamiento: int
    capacidad: int
    etiqueta: str
    uso: str = 'texto'  # texto, recurso_interno

# Posiciones estructurales examinadas en los archivos originales USA.
# Cada posición es RELATIVA al principio de un registro, no a la ISO.
CAMPOS: dict[str,list[Campo]] = {
    'DEFAULTTALK.DAT': [Campo(4,32,'personalidad'),Campo(36,64,'dialogo_1'),Campo(100,64,'dialogo_2')],
    'ARTIFACT.DAT': [Campo(48,24,'nombre'),Campo(72,96,'descripcion')],
    'BODY.DAT': [Campo(31,20,'nombre'),Campo(51,96,'descripcion')],
    'WEAPON.DAT': [Campo(40,20,'nombre'),Campo(60,96,'descripcion')],
    'SHIELD.DAT': [Campo(37,20,'nombre'),Campo(57,96,'descripcion')],
    'MAGIC.DAT': [Campo(108,20,'nombre'),Campo(128,96,'descripcion')],
    'CHAR.DAT': [Campo(248,20,'nombre'),Campo(268,128,'perfil'),Campo(396,32,'clase'),
                 Campo(428,256,'descripcion_clase'),Campo(684,128,'rasgo_1'),Campo(812,128,'rasgo_2')],
    'DUNGEON.DAT': [Campo(32,32,'nombre'),Campo(64,96,'descripcion'),Campo(160,96,'pista')],
    'MONSTER.DAT': [Campo(104,32,'nombre'),Campo(136,32,'especie'),Campo(168,200,'descripcion'),
                    Campo(368,164,'comportamiento')],
    'RMAPSET.DAT': [Campo(0,36,'nombre_area'),Campo(36,36,'archivo_mapa','recurso_interno')],
    'RMAPSET2.DAT': [Campo(0,36,'nombre_area'),Campo(36,36,'archivo_mapa','recurso_interno')],
    'TIPATTR.DAT': [Campo(0,16,'nombre_atributo')],
    'UP_MONSTER.DAT': [Campo(54,16,'nombre_monstruo')],
    'DIFFICULTY.DAT': [Campo(2,96,'nombre_def'),Campo(98,96,'nombre_atk')],
    'EFFECT.DAT': [Campo(46,14,'nombre_efecto'),Campo(60,44,'descripcion_efecto')],
    'BODY-EFFECT.DAT': [Campo(56,16,'nombre_efecto'),Campo(72,64,'descripcion_efecto')],
    'SHIELD-EFFECT.DAT': [Campo(56,16,'nombre_efecto'),Campo(72,64,'descripcion_efecto')],
    'WEAPON-EFFECT.DAT': [Campo(54,16,'nombre_efecto'),Campo(70,64,'descripcion_efecto')],
    'DAIHYOU.DAT': [Campo(162,20,'nombre_personaje')],
    'SIEN.DAT': [Campo(162,20,'nombre_personaje')],
}
TABLAS_NOMBRES = {'BOSSNAME.DAT','CHARNAMEMAN.DAT','CHARNAMEWOMAN.DAT'}
# Los datos siguientes tienen campos textuales, pero no se ha demostrado uso en HUD.
VERIFICAR_USO = {'DIFFICULTY.DAT','TIPATTR.DAT','UP_MONSTER.DAT','DAIHYOU.DAT','SIEN.DAT','EFFECT.DAT'}
IMAGENES = [
    ('DOT_NODATA.PNG','NO DATA','mensaje_grafico','texto'),
    ('NODATA.PNG','NO DATA','mensaje_grafico','texto'),
    ('DOT_PIC1.PNG','CLADUN','titulo_grafico','marca'),
    ('DOT_PIC1.PNG','This is an RPG!','titulo_grafico','texto'),
    ('PIC1.PNG','CLADUN','titulo_grafico','marca'),
    ('PIC1.PNG','This is an RPG!','titulo_grafico','texto'),
    ('DOT_SAVE.PNG','CLADUN','titulo_grafico','marca'),
    ('DOT_SAVE.PNG','This is an RPG!','titulo_grafico','texto'),
    ('SAVE.PNG','CLADUN','titulo_grafico','marca'),
    ('SAVE.PNG','This is an RPG!','titulo_grafico','texto'),
    ('DOT_NODATA.PNG','dot','rotulo_grafico','decoracion'),
    ('DOT_SAVE.PNG','dot','rotulo_grafico','decoracion')
]
MASTER_FIELDS=['grupo_id','text_id','tipo','campo','original','espanol','estado','revision_fuente',
               'origen','indice_registro','script','script_id','orden_script','offset_hex',
               'capacidad_campo','longitud_original_bytes','bytes_hex','idioma_origen','comentario']
AUDIT_FIELDS=['text_id_anterior','origen','indice_registro','offset_anterior','original_anterior',
              'decision','detalle','text_id_nuevo','offset_nuevo','original_nuevo']

def leer_csv(path:Path)->list[dict[str,str]]:
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def escribir_csv(path:Path,filas:list[dict],campos:list[str])->None:
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=campos,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(filas)

def bytes_base(iso:Path)->tuple[dict[str,bytes],str]:
    _,entries=iso9660_entries(iso)
    pk=next(x for x in entries if x['path']=='PSP_GAME/USRDIR/DATA.DAT')
    pack=read_iso_file(iso,pk)
    info=next(x for x in pspfs_entries(pack) if x['name']=='DATABASE.DAT')
    b,_=decompress(pack[info['offset']:info['offset']+info['size_stored']],info['size_expanded'])
    db={}
    for m in dsarc_entries(b):
        db[m['name']]=b[m['offset']:m['offset']+m['size']]
    return db,hashlib.sha256(iso.read_bytes()).hexdigest()

def campos_archivo(nombre:str,b:bytes):
    n=int.from_bytes(b[:4],'little')
    if nombre=='MAHO-JIN.DAT':
        if n!=104:raise ValueError('MAHO-JIN.DAT: cantidad de registros inesperada')
        for i in range(n):
            off=28+i*32
            yield i,Campo(12,20,'nombre_circulo'),off,b[off:off+20]
        return
    if nombre in TABLAS_NOMBRES:
        if len(b)!=4+n*32:raise ValueError(f'{nombre}: estructura no coincide')
        for i in range(n):
            off=4+i*32
            yield i,Campo(0,32,'nombre'),off,b[off:off+32]
        return
    if nombre not in CAMPOS:return
    if n<=0 or (len(b)-16)%n:raise ValueError(f'{nombre}: registros irregulares')
    stride=(len(b)-16)//n
    for i in range(n):
        for field in CAMPOS[nombre]:
            if field.desplazamiento+field.capacidad>stride:
                raise ValueError(f'{nombre} registro {i}: campo fuera de límites')
            off=16+i*stride+field.desplazamiento
            yield i,field,off,b[off:off+field.capacidad]

def original_de_campo(raw:bytes)->tuple[str,bytes]:
    raw=raw.split(b'\x00',1)[0]
    if not raw:return '',b''
    text=raw.decode('cp932',errors='replace') # Sustituciones marcadas y bytes_hex preservados.
    if '\x00' in text or any(ord(x)<32 and x not in '\n\r\t' for x in text):
        raise ValueError('Caracteres de control inesperados en campo textual')
    return text,raw

def deteccion_idioma(texto:str)->str:
    return 'japones_o_mixto' if any('\u3040'<=c<='\u30ff' or '\u4e00'<=c<='\u9fff' or '\uff61'<=c<='\uff9f' for c in texto) else 'ingles_o_simbolos'

def tipo_campo(fname:str,oldcat:str|None)->str:
    tipos={
        'DEFAULTTALK.DAT':'dialogos_predeterminados',
        'ARTIFACT.DAT':'objetos_artefactos','BODY.DAT':'objetos_armaduras',
        'WEAPON.DAT':'objetos_armas','SHIELD.DAT':'objetos_escudos',
        'MAGIC.DAT':'habilidades_magia','CHAR.DAT':'personajes',
        'DUNGEON.DAT':'lugares_mazmorras','MONSTER.DAT':'monstruos',
        'RMAPSET.DAT':'lugares','RMAPSET2.DAT':'lugares',
        'TIPATTR.DAT':'atributos_terreno',
        'UP_MONSTER.DAT':'monstruos_auxiliares',
        'DIFFICULTY.DAT':'etiquetas_dificultad',
        'EFFECT.DAT':'efectos','BODY-EFFECT.DAT':'efectos_armaduras',
        'SHIELD-EFFECT.DAT':'efectos_escudos','WEAPON-EFFECT.DAT':'efectos_armas',
        'DAIHYOU.DAT':'nombres_personajes','SIEN.DAT':'nombres_personajes',
        'MAHO-JIN.DAT':'circulos_magicos',
        'BOSSNAME.DAT':'nombres_jefes',
        'CHARNAMEMAN.DAT':'nombres_personajes',
        'CHARNAMEWOMAN.DAT':'nombres_personajes',
    }
    return tipos.get(fname,oldcat or 'base_datos')

def make_record(raw:dict[str,str], *, campo:str='', capacidad:int|str='',
                estado:str='pendiente_traduccion', revision:str='verificado_formato',
                comentario:str='', texto:str|None=None, offset:str|None=None, text_id:str|None=None)->dict:
    return dict(text_id=text_id or raw['text_id'],tipo=raw.get('category',''),campo=campo,
                original=raw['original'] if texto is None else texto,espanol='',estado=estado,
                revision_fuente=revision,origen=raw['source'],indice_registro=raw.get('file_index',''),
                script=raw.get('script_file',''),script_id=raw.get('script_id',''),
                orden_script=raw.get('command_index',''),
                offset_hex=offset or raw.get('offset_hex',''),capacidad_campo=capacidad,
                longitud_original_bytes=raw.get('byte_length',''),bytes_hex=raw.get('raw_hex',''),
                idioma_origen=deteccion_idioma(raw['original'] if texto is None else texto),
                comentario=comentario)

def exportar_txt(path: Path, filas: list[dict]) -> None:
    """Vista única en texto plano. Conserva ID, tipo y orden, sin traducir."""
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w', encoding='utf-8-sig', newline='\n') as f:
        f.write('CLADUN: THIS IS AN RPG! (PSP USA)\n')
        f.write('CORPUS COMPLETO DE TEXTO ORIGINAL — SIN TRADUCCIÓN AL ESPAÑOL\n')
        f.write(f'TOTAL: {len(filas)} GRUPOS | UNA ENTRADA POR POSICIÓN DE ORIGEN\n')
        f.write('NOTA: ORDEN DE EXTRACCIÓN; ALGUNOS TEXTOS REQUIEREN COMPROBAR SU USO EN PANTALLA.\n\n')
        for i,row in enumerate(filas,1):
            f.write(f"========== GRUPO {i:06d} | ID {row['text_id']} ==========\n")
            f.write(f"TIPO: {row['tipo']}\nESTADO: {row['estado']}\nRECURSO: {row['origen']}\n")
            if row['script']:
                f.write(f"SCRIPT: {row['script']} | ORDEN: {row['orden_script']}\n")
            f.write(f"ORIGINAL:\n{row['original']}\n========== FIN GRUPO {i:06d} ==========\n\n")

def revisar(iso:Path,raw_path:Path,out:Path)->dict:
    db,iso_hash=bytes_base(iso)
    old=leer_csv(raw_path)
    bysrc:dict[str,list[dict]]=collections.defaultdict(list)
    for x in old:bysrc[x['source']].append(x)
    ordered=[];seen=set();report=[];discard=[];manual=[];count_corrected=0
    sources_order=list(dict.fromkeys(x['source'] for x in old))
    def add(row):
        if not row['original'].strip():return
        if row['text_id'] in seen:raise ValueError('ID duplicado '+row['text_id'])
        seen.add(row['text_id']);ordered.append(row)
    def exclusion(orig,decision,detalle):
        line=dict(text_id_anterior=orig.get('text_id',''),origen=orig.get('source',''),
                  indice_registro=orig.get('file_index',''),offset_anterior=orig.get('offset_hex',''),
                  original_anterior=orig.get('original',''),decision=decision,detalle=detalle,
                  text_id_nuevo='',offset_nuevo='',original_nuevo='')
        report.append(line);discard.append(line)
    for source in sources_order:
        rows=bysrc[source]
        if not source.startswith('DATABASE.DAT/'):
            for x in rows:
                if not x['original'].strip():
                    exclusion(x,'excluido_vacio','Cadena vacía en fuente reconocida')
                    continue
                add(make_record(x,revision='verificado_formato',campo=('linea_creditos' if source=='STAFFROLL.TXT' else 'cadena')))
            continue
        fname=source.split('/',1)[1]
        if fname=='STRTBL.DAT':
            for x in rows:
                if x['original'].strip():add(make_record(x,revision='verificado_tabla_punteros',campo='mensaje_interfaz'))
                else:exclusion(x,'excluido_vacio','Slot sin texto')
            continue
        if fname in ('LV.DAT',):
            for x in rows:exclusion(x,'descartado_binario','Datos numéricos confundidos con Shift-JIS')
            continue
        if fname not in CAMPOS and fname not in TABLAS_NOMBRES and fname!='MAHO-JIN.DAT':
            for x in rows:exclusion(x,'no_esquema_textual','Sin evidencia de campo de texto real')
            continue
        # Candidate originals are matched to verified slots, including previously shifted offsets.
        assigned:set[str]=set()
        old_by_rec=collections.defaultdict(list)
        for x in rows:old_by_rec[str(x['file_index'])].append(x)
        for idx,field,offset,fieldbytes in campos_archivo(fname,db[fname]):
            try:txt,rawbytes=original_de_campo(fieldbytes)
            except ValueError as err:
                raise ValueError(f'{fname}[{idx}]: {err}') from err
            if not txt.strip():continue
            prior=[x for x in old_by_rec.get(str(idx),[]) if x['text_id'] not in assigned and abs(int(x['offset_hex'],16)-offset)<=4]
            if not prior:prior=[x for x in old_by_rec.get(str(idx),[]) if x['text_id'] not in assigned and x['original']==txt.strip()]
            if not prior and fname=='MAHO-JIN.DAT':
                prior=[x for x in rows if x['text_id'] not in assigned and int(x['offset_hex'],16)==offset and x['original']==txt.strip()]
            previous=prior[0] if prior else None
            if previous:assigned.add(previous['text_id'])
            identifier=previous['text_id'] if previous else f'CLD-F-{fname.replace(".DAT","").replace("-","_")}-{idx:04d}-{field.etiqueta}'
            if field.uso=='recurso_interno':
                temp=previous or {'text_id':identifier,'source':source,'file_index':idx,'offset_hex':f'0x{offset:08X}','original':txt}
                exclusion(temp,'referencia_archivo_no_traducible','Ruta/referencia interna de recurso')
                continue
            status='pendiente_traduccion';verdict='campo_binario_confirmado';note='Campo de texto reconstruido con longitud y offset; presencia en pantalla por validar.'
            if '\ufffd' in txt:
                status='requiere_reconstruccion';verdict='bytes_no_decodificables';note='Fuente con byte(s) CP932 incompleto(s): no inventar caracteres; revisar bytes_hex y pantalla.'
            elif fname in VERIFICAR_USO or (deteccion_idioma(txt)=='japones_o_mixto' and fname not in TABLAS_NOMBRES):
                status='requiere_comprobar_en_juego';verdict='texto_real_uso_pendiente'
                note='Campo real de texto; falta verificar si se muestra en el juego y no es una etiqueta interna.'
            if previous and (previous['original']!=txt or previous['offset_hex']!=f'0x{offset:08X}'):
                count_corrected+=1
                report.append(dict(text_id_anterior=previous['text_id'],origen=source,indice_registro=idx,
                    offset_anterior=previous['offset_hex'],original_anterior=previous['original'],
                    decision='corregido_por_campo',detalle='Reconstruido desde posición estructural verificada',
                    text_id_nuevo=identifier,offset_nuevo=f'0x{offset:08X}',original_nuevo=txt))
            if not previous:
                report.append(dict(text_id_anterior='',origen=source,indice_registro=idx,
                    offset_anterior='',original_anterior='',decision='recuperado_omitido',
                    detalle='Campo textual no detectado por filtro heurístico de letras/símbolos',
                    text_id_nuevo=identifier,offset_nuevo=f'0x{offset:08X}',original_nuevo=txt))
            row=dict(text_id=identifier,tipo=tipo_campo(fname,previous['category'] if previous else ''),
                campo=field.etiqueta,original=txt,espanol='',estado=status,revision_fuente=verdict,
                origen=source,indice_registro=idx,script='',script_id='',orden_script='',
                offset_hex=f'0x{offset:08X}',capacidad_campo=field.capacidad,
                longitud_original_bytes=len(rawbytes),bytes_hex=rawbytes.hex().upper(),idioma_origen=deteccion_idioma(txt),comentario=note)
            add(row)
        for x in rows:
            if x['text_id'] not in assigned:
                exclusion(x,'descartado_fuera_de_campos','Detectado por heurística pero fuera de los campos textuales de la tabla')
        if fname=='MAHO-JIN.DAT' and not rows:
            raise AssertionError('Se esperaba un inventario candidato MAHO-JIN')
    # La tabla MAHO-JIN figuraba en los datos antiguos, por lo que ya está incluida.
    # Textos de imágenes examinados visualmente: el logo CLADUN no se traduce; dot es decorativo.
    graphic_audit=[]
    for i,(filename,txt,category,kind) in enumerate(IMAGENES,1):
        id_=f'CLD-GFX-{i:04d}'
        meta={'text_id_anterior':id_,'origen':'SYS.DAT2/'+filename,'indice_registro':'',
             'offset_anterior':'','original_anterior':txt,'text_id_nuevo':'','offset_nuevo':'','original_nuevo':''}
        if kind in ('marca','decoracion'):
            report.append({**meta,'decision':'no_traducir' if kind=='marca' else 'descartado_decoracion',
                           'detalle':'Nombre comercial protegido' if kind=='marca' else 'Marca gráfica decorativa'})
            continue
        add(dict(text_id=id_,tipo=category,campo='rotulo_rasterizado',original=txt,espanol='',
                 estado='pendiente_traduccion',revision_fuente='verificado_visual',
                 origen='SYS.DAT2/'+filename,indice_registro='',script='',script_id='',orden_script='',
                 offset_hex='',capacidad_campo='',longitud_original_bytes='',bytes_hex='',idioma_origen='ingles_o_simbolos',
                 comentario='Imagen: requiere modificar gráfico, no el script.'))
    for i,r in enumerate(ordered,1):r['grupo_id']=f'{i:06d}'
    total=collections.Counter(r['estado'] for r in ordered)
    reconciled=[r for r in ordered if r['revision_fuente']!='verificado_visual']
    confirmed=[r for r in ordered if r['estado']=='pendiente_traduccion']
    possible=[r for r in ordered if r['estado'] in ('requiere_comprobar_en_juego','requiere_reconstruccion')]
    # El informe de cambios registra cada candidata de la extracción anterior.
    audited_ids={x['text_id_anterior'] for x in report if x['text_id_anterior']}
    assert len({r['text_id'] for r in ordered})==len(ordered)
    files=out/'corpus'
    escribir_csv(files/'CLADUN_TODO_TEXTO_ORIGINAL.csv',ordered,MASTER_FIELDS)
    exportar_txt(files/'CLADUN_TODO_TEXTO_ORIGINAL.txt',ordered)
    escribir_csv(files/'confirmados_formato.csv',confirmed,MASTER_FIELDS)
    escribir_csv(files/'revisar_visibilidad.csv',possible,MASTER_FIELDS)
    escribir_csv(out/'qa/decisiones_auditoria.csv',report,AUDIT_FIELDS)
    recurso_conteos=collections.Counter(x['origen'] for x in ordered)
    contingencias=collections.Counter(x['origen'] for x in possible)
    escribir_csv(out/'metadata/resumen_recursos.csv',[
        {'recurso':source,'bloques_textuales':count,'por_verificar':contingencias[source]}
        for source,count in recurso_conteos.items()],
        ['recurso','bloques_textuales','por_verificar'])
    # Registro de cambios desde la anterior edición. Se distingue cantidad de modificaciones de campos.
    data=dict(version='0.3.0-auditoria',edicion='USA/PSP',iso_sha256=iso_hash,
              total_bloques_texto=len(ordered),confirmados_formato=len(confirmed),
              uso_en_juego_por_comprobar=len(possible),bytes_incompletos=sum(r['estado']=='requiere_reconstruccion' for r in ordered),graficos_texto=sum(r['revision_fuente']=='verificado_visual' for r in ordered),
              nuevos_recuperados=sum(r['decision']=='recuperado_omitido' for r in report),
              correcciones_fuente=count_corrected,
              exclusiones_por_criterio=dict(collections.Counter(x['decision'] for x in discard)),
              auditoria_registros=len(report),
              advertencia='No hay prueba de cobertura textual absoluta ni validación en PPSSPP. No se ha traducido ningún texto.')
    (out/'reports').mkdir(parents=True,exist_ok=True)
    (out/'reports/resumen.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return data

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--iso',type=Path,required=True)
    p.add_argument('--raw',type=Path,required=True,help='corpus/todo_el_texto.csv de la extracción intermedia')
    p.add_argument('--salida',type=Path,default=Path('.'))
    a=p.parse_args()
    print(json.dumps(revisar(a.iso,a.raw,a.salida),ensure_ascii=False,indent=2))
