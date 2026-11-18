#!/usr/bin/env python3
"""QA estático del corpus Cladun sin necesidad de la ISO comercial."""
from __future__ import annotations
import argparse,csv,json,re
from pathlib import Path

ALLOWED={'pendiente_traduccion','requiere_comprobar_en_juego','requiere_reconstruccion'}

def rows(path):
    with path.open(encoding='utf-8-sig',newline='') as f:return list(csv.DictReader(f))

def validate(root:Path)->dict:
    files=root/'corpus'
    master=rows(files/'CLADUN_TODO_TEXTO_ORIGINAL.csv')
    confirmed=rows(files/'confirmados_formato.csv')
    pending=rows(files/'revisar_visibilidad.csv')
    rpt=json.loads((root/'reports/resumen.json').read_text(encoding='utf-8'))
    errors=[]
    def check(condition,reason):
        if not condition:errors.append(reason)
    check(len(master)==rpt['total_bloques_texto'],'Número de bloques incompatible con informe')
    check(len(master)==len(confirmed)+len(pending),'Separación de estados incompleta')
    check(len(confirmed)==rpt['confirmados_formato'],'Total confirmado incoherente')
    check(len(pending)==rpt['uso_en_juego_por_comprobar'],'Total pendiente incoherente')
    check(len({r['text_id'] for r in master})==len(master),'IDs repetidos')
    check(all(int(r['grupo_id'])==i for i,r in enumerate(master,1)),'Secuencia grupo_id alterada')
    check(all(r['original'].strip() for r in master),'Original vacío')
    check(all(not r['espanol'] for r in master),'El corpus ya contiene una traducción')
    check(all(r['estado'] in ALLOWED for r in master),'Estado no soportado')
    check(not any(r['campo']=='archivo_mapa' for r in master),'Contaminación por nombres de archivos internos')
    check(not any(r['origen']=='DATABASE.DAT/LV.DAT' for r in master),'Contaminación por flotantes de LV.DAT')
    badbytes=0
    for r in master:
        if r['bytes_hex']:
            try:
                data=bytes.fromhex(r['bytes_hex'])
                dec=data.decode('cp932',errors='replace')
                check(dec==r['original'],f"Hex/original diferentes: {r['text_id']}")
                check(len(data)==int(r['longitud_original_bytes']),f"Longitud inconsistente: {r['text_id']}")
                if r['capacidad_campo']:
                    check(len(data)<=int(r['capacidad_campo']),f"Capacidad excedida: {r['text_id']}")
                if '\ufffd' in dec:badbytes+=1
            except (ValueError,TypeError):errors.append('Hex o tamaño inválido: '+r['text_id'])
        elif r['origen'].endswith('.PNG'):
            check(not r['offset_hex'],'Los rótulos gráficos no tienen offset de cadena')
    check(badbytes==rpt['bytes_incompletos'],'Cantidad de cadenas truncadas cambió')
    text=(files/'CLADUN_TODO_TEXTO_ORIGINAL.txt').read_text(encoding='utf-8-sig')
    check(text.count('========== GRUPO ')==len(master),'TXT: cantidad incorrecta de grupos')
    check(text.count('FIN ORIGINAL\n')==len(master),'TXT: cantidad incorrecta de finales')
    check(text.count('ESPAÑOL EDICIÓN:\n')==len(master),'TXT: cantidad incorrecta de espacios de traducción')
    # Validación exhaustiva por bloque sin reconstruir manualmente miles de delimitadores.
    blocks=text.split('========== GRUPO ')
    for i,r in enumerate(master,1):
        block=blocks[i]
        check(f"ID {r['text_id']} ==========" in block,f"TXT: ID incompatible en grupo {i}")
        check('ORIGINAL:\n'+r['original']+'\nFIN ORIGINAL' in block,f"TXT: original incompatible en {r['text_id']}")
    if errors:raise AssertionError('Errores QA ('+str(len(errors))+'):\n'+'\n'.join(errors[:30]))
    return {'qa':'OK','bloques':len(master),'secciones_confirmadas':len(confirmed),
            'por_verificar':len(pending),'bytes_incompletos':badbytes}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--raiz',type=Path,default=Path(__file__).resolve().parents[1]);a=p.parse_args()
    print(json.dumps(validate(a.raiz),ensure_ascii=False,indent=2))
