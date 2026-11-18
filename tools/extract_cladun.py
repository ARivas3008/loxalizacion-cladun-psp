#!/usr/bin/env python3
"""Extractor verificable para Cladun: This Is an RPG (USA PSP).
Usar exclusivamente con una ISO obtenida legítimamente. Python 3.10+, sin dependencias.
Extrae las tablas, los textos y los índices. No redistribuye los binarios del juego.
"""
from __future__ import annotations
import argparse, collections, csv, gzip, hashlib, json, re, struct, sys
from pathlib import Path

SECTOR = 2048
SCRIPT_TEXT_OPS = {0x66: 'dialogo', 0x69: 'opcion', 0x6e: 'personaje_interlocutor'}
DIRECT_NAME_TABLES = {'BOSSNAME.DAT', 'CHARNAMEMAN.DAT', 'CHARNAMEWOMAN.DAT'}
RECORD_CATEGORIES = {
    'ARTIFACT.DAT':'objetos_artefactos','WEAPON.DAT':'objetos_armas','BODY.DAT':'objetos_armaduras',
    'SHIELD.DAT':'objetos_escudos','MAGIC.DAT':'habilidades_magia','DUNGEON.DAT':'lugares_mazmorras',
    'MONSTER.DAT':'monstruos','CHAR.DAT':'personajes','BOSSNAME.DAT':'nombres_jefes',
    'CHARNAMEMAN.DAT':'nombres_personajes','CHARNAMEWOMAN.DAT':'nombres_personajes',
    'RMAPSET.DAT':'lugares','RMAPSET2.DAT':'lugares','TIPATTR.DAT':'atributos',
    'DEFAULTTALK.DAT':'dialogos_predeterminados','STRTBL.DAT':'interfaz',
}


def sha256(d: bytes)->str:return hashlib.sha256(d).hexdigest()
def u32(d: bytes, off=0)->int:return struct.unpack_from('<I',d,off)[0]
def u16(d: bytes, off=0)->int:return struct.unpack_from('<H',d,off)[0]
def xoff(n: int)->str:return f'0x{n:08X}'
def read_name(b: bytes)->str:return b.split(b'\0',1)[0].decode('ascii','replace').strip()


def csvout(path:Path, cols:list[str], rows:list[dict]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.DictWriter(f,fieldnames=cols,extrasaction='ignore');w.writeheader();w.writerows(rows)


def iso9660_entries(iso:Path):
    with iso.open('rb') as f:
        f.seek(SECTOR*16);pvd=f.read(SECTOR)
        if pvd[:7]!=b'\x01CD001\x01':raise ValueError('No es ISO9660 válido (PVD no encontrado)')
        volume=pvd[40:72].decode('ascii','replace').strip()
        def entry(b:bytes):
            if len(b)<34:return None
            size=b[0]
            if size==0:return None
            nam=b[33:33+b[32]].decode('ascii','replace').split(';')[0]
            return {'name':nam,'offset':u32(b,2)*SECTOR,'size':u32(b,10),'directory':bool(b[25]&2)}
        root=entry(pvd[156:156+pvd[156]])
        rows=[]
        def browse(dirent,prefix):
            f.seek(dirent['offset']);buf=f.read(dirent['size']);pos=0
            while pos<len(buf):
                ln=buf[pos]
                if not ln:pos=(pos//SECTOR+1)*SECTOR;continue
                item=entry(buf[pos:pos+ln]);pos+=ln
                if not item or item['name'] in ('\x00','\x01'):continue
                item['path']=f"{prefix}/{item['name']}" if prefix else item['name'];rows.append(item)
                if item['directory']:browse(item,item['path'])
        browse(root,'')
        for i,r in enumerate(rows):r['index']=i;r['iso_offset_hex']=xoff(r['offset'])
        return volume,rows


def read_iso_file(iso:Path, record:dict)->bytes:
    with iso.open('rb') as f:
        f.seek(record['offset']);return f.read(record['size'])


def imy_decode(raw:bytes,start:int)->bytes:
    if raw[start:start+4]!=b'IMY\x00':raise ValueError('Cabecera IMY no encontrada')
    stride=u16(raw,start+8);typ=raw[start+10];rows=u16(raw,start+12);nflags=u16(raw,start+32)
    if typ>>4!=1:raise ValueError(f'Tipo IMY no soportado: {typ:02x}')
    flags=raw[start+34:start+34+nflags]
    data_start=start+34+nflags;rp=data_start;out=bytearray();target=stride*rows
    lookback=(2,stride,stride+2,stride-2)
    for fl in flags:
        if len(out)>=target:break
        if (fl&0xC0)==0xC0:
            distance=lookback[(fl>>4)&3]
            if distance<1 or len(out)<distance:raise ValueError('Lookback IMY inválido')
            for _ in range((fl&15)+1):
                off=len(out)-distance;out.extend(out[off:off+2])
        elif fl&0xF0:
            # Indica desplazamiento dentro del flujo de bytes literales (no del texto ya reconstruido).
            distance=(fl-16)*2+2
            if rp-distance<data_start:raise ValueError('Lookback IMY fuera del flujo literal')
            out.extend(raw[rp-distance:rp-distance+2])
        else:
            length=(fl+1)*2
            if rp+length>len(raw):raise ValueError('IMY truncado')
            out.extend(raw[rp:rp+length]);rp+=length
    if len(out)!=target:raise ValueError(f'IMY: {len(out)} bytes, esperados {target}')
    return bytes(out)


def decompress(data:bytes,expanded:int):
    if expanded==0:return data,'sin_comprimir'
    if data[12:14]==b'\x1f\x8b':
        result=gzip.decompress(data[12:]);kind='gzip'
    else:
        if len(data)<12:raise ValueError('Paquete IMY truncado')
        n=u32(data);total=u32(data,4)
        if not 0<n<=512:raise ValueError('Número de bloques IMY inválido')
        offsets=struct.unpack_from('<'+'I'*n,data,8)
        result=b''.join(imy_decode(data,x) for x in offsets)
        kind=f'IMY_{n}_bloques'
    if len(result)!=expanded:raise ValueError(f'Longitud incorrecta {len(result)} != {expanded}')
    return result,kind


def pspfs_entries(blob:bytes):
    if blob[:8]!=b'PSPFS_V1':raise ValueError('PSPFS_V1 no encontrado')
    n=u32(blob,8)
    if not 0<n<10000:raise ValueError('Cantidad de archivos inconsistente')
    # Cladun usa registros de 32 B: nombre ASCII de 20 B, tamaño expandido, tamaño almacenado, offset.
    entries=[]
    for i in range(n):
        base=16+i*32;rec=blob[base:base+32]
        if len(rec)!=32:raise ValueError('Tabla PSPFS truncada')
        name=read_name(rec[:20]);size,stored,off=struct.unpack_from('<III',rec,20)
        if off+stored>len(blob):raise ValueError(f'Archivo {name} fuera del archivo principal')
        entries.append({'index':i,'name':name,'table_offset':xoff(base),'offset':off,
                        'offset_hex':xoff(off),'size_stored':stored,'size_expanded':size})
    return entries


def dsarc_entries(blob:bytes):
    magic=blob[:8]
    if magic not in (b'DSARC FL',b'DSARCIDX'):return []
    n=u32(blob,8)
    if n>10000:raise ValueError('DSARC con demasiados registros')
    table_start=16 if magic==b'DSARC FL' else ((16+n*2+3)//4)*4
    entries=[]
    for i in range(n):
        base=table_start+i*48;row=blob[base:base+48]
        if len(row)<48:raise ValueError('Tabla DSARC truncada')
        name=read_name(row[:40]);size,off=struct.unpack_from('<II',row,40)
        if not name or off+size>len(blob):raise ValueError(f'DSARC corrupto: {name} ({i})')
        entries.append({'index':i,'name':name,'offset':off,'offset_hex':xoff(off),
                        'table_offset_hex':xoff(base),'size':size,'format':magic.decode('ascii')})
    return entries


def cp932(raw:bytes):
    try:return raw.decode('cp932'), 'cp932'
    except UnicodeDecodeError:return raw.decode('cp932',errors='replace'),'cp932_con_reemplazo'


def valid_text(s:str, minlen:int=2)->bool:
    if not s or '\ufffd' in s or '\x00' in s:return False
    if any(ord(ch)<32 and ch not in '\t\r\n' for ch in s):return False
    letters=sum(ch.isalpha() for ch in s)
    return letters>=minlen and not re.fullmatch(r'[A-Za-z]{1,2}',s.strip())


def scan_field_text(raw:bytes,base_offset:int, minletters=3):
    """Candidatos de texto terminados en NUL en registros binarios, con offset exacto.
    Son candidatos: la estructura interna de cada campo no se considera confirmada.
    """
    results=[];seen=set()
    i=0
    # Detectar runs de ASCII imprimible y Shift-JIS. Invalidar caracteres de control salvo \t/\n.
    while i<len(raw):
        start=i; chars=[]
        while i<len(raw):
            c=raw[i]
            if c in (9,10,13) or 32<=c<=126:
                chars.append(bytes([c]));i+=1;continue
            if 0xA1<=c<=0xDF:
                chars.append(bytes([c]));i+=1;continue
            if (0x81<=c<=0x9F or 0xE0<=c<=0xFC) and i+1<len(raw) and (0x40<=raw[i+1]<=0x7E or 0x80<=raw[i+1]<=0xFC):
                chars.append(raw[i:i+2]);i+=2;continue
            break
        if chars:
            b=b''.join(chars);nextbyte=raw[i] if i<len(raw) else None
            s,enc=cp932(b)
            if nextbyte==0 and valid_text(s,minletters):
                st=s.strip()
                if st and (base_offset+start,st) not in seen:
                    results.append({'offset':base_offset+start,'original':st,'encoding':enc,
                                    'raw_hex':b.hex().upper(),'byte_length':len(b)})
                    seen.add((base_offset+start,st))
            if i==start:i+=1
        else:i+=1
    return results


def script_table(table:bytes,name:str):
    n=u32(table);assert len(table)==16+32*n,(name,len(table),n)
    rows=[]
    for i in range(n):
        off=16+i*32; sid,start=struct.unpack_from('<II',table,off)
        fname=read_name(table[off+8:off+32])
        rows.append({'table':name,'index':i,'script_id':sid,'start':start,'name':fname})
    return rows


def parse_commands(binblob:bytes,tabrows:list[dict],source:str):
    cmds=[];strings=[]
    for i,t in enumerate(tabrows):
        pos=t['start'];end=tabrows[i+1]['start'] if i+1<len(tabrows) else len(binblob)
        if not 0<=pos<=end<=len(binblob):raise ValueError('Segmento fuera del archivo')
        block_start=pos;seq=0
        while pos+5<=end:
            if not any(binblob[pos:end]):break
            op=binblob[pos];instruction_id=u16(binblob,pos+1);paramlen=u16(binblob,pos+3)
            if pos+5+paramlen>end:raise ValueError(f'Instr. truncada a {pos:#x} ({source})')
            payload=binblob[pos+5:pos+5+paramlen]
            cmds.append({'source':source,'block_index':i,'script_id':t['script_id'],'script_file':t['name'],
                         'command_index':seq,'instruction_id':instruction_id,'opcode_hex':f'0x{op:02X}',
                         'offset_hex':xoff(pos),'arguments_length':paramlen})
            if op in SCRIPT_TEXT_OPS and source.endswith("/SCRIPT.DAT"):
                if paramlen<3 or u16(payload)+3!=len(payload) or payload[-1]!=0:
                    raise ValueError(f'Payload textual inesperado a {pos:#x} ({source})')
                content=payload[2:-1]
                s,enc=cp932(content)
                strings.append({'category':SCRIPT_TEXT_OPS[op],'source':source,'original':s,
                                'file_index':i,'script_id':t['script_id'],'script_file':t['name'],
                                'command_index':seq,'instruction_id':instruction_id,'opcode_hex':f'0x{op:02X}',
                                'offset':pos+7,'offset_hex':xoff(pos+7),'byte_length':len(content),
                                'raw_hex':content.hex().upper(),'encoding':enc,'confidence':'confirmado'})
            pos+=5+paramlen;seq+=1
        if any(binblob[pos:end]):raise ValueError(f'Resto binario no reconocido a {pos:#x}')
    return cmds,strings


def strtbl_entries(b:bytes,source:str):
    first=u32(b)
    if first%4 or first>len(b):raise ValueError('Cabecera STRTBL errónea')
    n=first//4
    offsets=struct.unpack_from('<'+'I'*n,b)
    valid=[(i,o) for i,o in enumerate(offsets) if first<=o<len(b)]
    if any(a[1]>b[1] for a,b in zip(valid,valid[1:])):raise ValueError('Orden STRTBL inconsistente')
    out=[]
    for j,(i,start) in enumerate(valid):
        end=valid[j+1][1] if j+1<len(valid) else len(b)
        raw=b[start:end].rstrip(b'\0')
        s,enc=cp932(raw)
        out.append({'category':'interfaz_sistema','source':source,'file_index':i,'offset':start,
                    'offset_hex':xoff(start),'original':s,'encoding':enc,'byte_length':len(raw),
                    'raw_hex':raw.hex().upper(),'confidence':'confirmado'})
    return out,n


def database_records(blobs:dict[str,bytes]):
    inventory=[];texts=[]
    for fname,b in blobs.items():
        if fname=='STRTBL.DAT':continue
        n=u32(b)
        header,step=None,None
        if fname in DIRECT_NAME_TABLES and len(b)==4+n*32:
            header,step=4,32
        else:
            # Mayoría de tablas de datos: cabecera de 16 bytes, registros del mismo tamaño.
            if n and (len(b)-16)>0 and (len(b)-16)%n==0:header,step=16,(len(b)-16)//n
        if step is None:
            inventory.append({'name':fname,'record_index':'','count_header':n,'stride':'',
                              'header_bytes':'','status':'variable_o_no_confirmado','offset_hex':'0x00000000'})
            runs=scan_field_text(b,0)
            for run in runs:
                texts.append({'category':RECORD_CATEGORIES.get(fname,'base_datos'),
                              'source':f'DATABASE.DAT/{fname}','file_index':'', 'confidence':'candidato', **run,
                              'offset_hex':xoff(run['offset'])})
            continue
        for i in range(n):
            off=header+i*step;chunk=b[off:off+step]
            inventory.append({'name':fname,'record_index':i,'count_header':n,'stride':step,
                              'header_bytes':header,'status':'tamano_verificado','offset_hex':xoff(off)})
            if fname in DIRECT_NAME_TABLES:
                val=chunk.split(b'\0',1)[0]
                s,enc=cp932(val)
                if s:
                    texts.append({'category':RECORD_CATEGORIES.get(fname,'base_datos'),
                                  'source':f'DATABASE.DAT/{fname}','file_index':i,'confidence':'confirmado',
                                  'original':s,'offset':off,'offset_hex':xoff(off),'encoding':enc,
                                  'byte_length':len(val),'raw_hex':val.hex().upper()})
            else:
                for run in scan_field_text(chunk,off):
                    texts.append({'category':RECORD_CATEGORIES.get(fname,'base_datos'),
                                  'source':f'DATABASE.DAT/{fname}','file_index':i,'confidence':'candidato', **run,
                                  'offset_hex':xoff(run['offset'])})
    return inventory,texts


def staffroll_rows(raw:bytes):
    output=[];pos=0
    for i,line in enumerate(raw.splitlines(keepends=True)):
        content=line.rstrip(b'\r\n');s,enc=cp932(content)
        output.append({'category':'creditos','source':'STAFFROLL.TXT','file_index':i,
                       'offset':pos,'offset_hex':xoff(pos),'original':s,'byte_length':len(content),
                       'encoding':enc,'raw_hex':content.hex().upper(),'confidence':'confirmado'})
        pos+=len(line)
    return output


def main():
    pa=argparse.ArgumentParser(description='Extraer e indexar texto de Cladun PSP (USA) sin redistribuir el juego')
    pa.add_argument('iso',type=Path,help='Ruta a la ISO del juego (extraer el .7z previamente)')
    pa.add_argument('-o','--output',type=Path,default=Path('.'))
    args=pa.parse_args();out=args.output;out.mkdir(exist_ok=True,parents=True)
    volume,iso_index=iso9660_entries(args.iso)
    csvout(out/'indices/iso9660.csv',['index','path','directory','offset','iso_offset_hex','size'],iso_index)
    pkg=next((x for x in iso_index if x['path']=='PSP_GAME/USRDIR/DATA.DAT'),None)
    if not pkg:raise ValueError('DATA.DAT no encontrado en la ISO')
    pack=read_iso_file(args.iso,pkg)
    entries=pspfs_entries(pack);decoded={};psp_index=[];decode_errors=[]
    for e in entries:
        src=pack[e['offset']:e['offset']+e['size_stored']]
        try:
            content,codec=decompress(src,e['size_expanded'])
            decoded[e['name']]=content
            psp_index.append({**e,'codec':codec,'decoded_size':len(content),'sha256':sha256(content),'status':'OK'})
        except Exception as exc:
            decode_errors.append({'file':e['name'],'error':str(exc)})
            psp_index.append({**e,'codec':'fallo','decoded_size':'','sha256':'','status':str(exc)})
    csvout(out/'indices/pspfs.csv',['index','name','table_offset','offset','offset_hex','size_stored','size_expanded','codec','decoded_size','sha256','status'],psp_index)
    if decode_errors:raise RuntimeError(f'No se han descomprimido {len(decode_errors)} entradas: {decode_errors[:3]}')
    dsindex=[];nested={}
    # Todos los archivos de paquete: DSARC FL y DSARCIDX, incluso las tablas RMAP.
    for e in entries:
        name=e['name'];b=decoded[name]; members=dsarc_entries(b)
        for r in members:
            child=b[r['offset']:r['offset']+r['size']]
            key=f'{name}/{r["name"]}'
            nested[key]=child
            dsindex.append({'parent_index':e['index'],'parent':name,'index':r['index'],
                            'name':r['name'],'offset_hex':r['offset_hex'],
                            'table_offset_hex':r['table_offset_hex'],'size':r['size'],
                            'format':r['format'],'sha256':sha256(child)})
    csvout(out/'indices/dsarc.csv',['parent_index','parent','index','name','offset_hex','table_offset_hex','size','format','sha256'],dsindex)
    scriptblocks=[];commands=[];texts=[];script_stats={}
    for family in ('SCRIPT','AISCRIPT'):
        d=nested[f'SCRIPT.SDT/{family}.DAT'];tab=nested[f'SCRIPT.SDT/{family}.TBL']
        blocks=script_table(tab,f'{family}.TBL')
        com,txt=parse_commands(d,blocks,f'SCRIPT.SDT/{family}.DAT')
        for i,t in enumerate(blocks):
            end=blocks[i+1]['start'] if i+1<len(blocks) else len(d)
            scriptblocks.append({'source':f'SCRIPT.SDT/{family}.DAT','table':t['table'],
                                 'block_index':i,'script_id':t['script_id'],'script_file':t['name'],
                                 'offset_hex':xoff(t['start']),'end_hex':xoff(end),'size':end-t['start']})
        commands+=com;texts+=txt
        script_stats[family]={'blocks':len(blocks),'commands':len(com),'text_entries':len(txt),
                              'distinct_script_names':len({x['name'] for x in blocks})}
    csvout(out/'indices/script_blocks.csv',['source','table','block_index','script_id','script_file','offset_hex','end_hex','size'],scriptblocks)
    csvout(out/'indices/script_commands.csv',['source','block_index','script_id','script_file','command_index','instruction_id','opcode_hex','offset_hex','arguments_length'],commands)
    # Particiones de 5.000 comandos para revisar en GitHub sin archivos enormes.
    for part_start in range(0,len(commands),5000):
        csvout(out/f'indices/comandos/parte_{part_start//5000+1:02d}.csv',
               ['source','block_index','script_id','script_file','command_index','instruction_id','opcode_hex','offset_hex','arguments_length'],
               commands[part_start:part_start+5000])
    strings,capacity=strtbl_entries(nested['DATABASE.DAT/STRTBL.DAT'],'DATABASE.DAT/STRTBL.DAT')
    texts+=strings
    db={key.split('/',1)[1]:v for key,v in nested.items() if key.startswith('DATABASE.DAT/')}
    db_records,db_strings=database_records(db);texts+=db_strings
    csvout(out/'indices/database_records.csv',['name','record_index','count_header','stride','header_bytes','status','offset_hex'],db_records)
    texts+=staffroll_rows(decoded['STAFFROLL.TXT'])
    # También detectar otras cadenas NUL con aspecto textual, en archivos no tratados como narración.
    supplemental=[]
    ignored_types={'.SPS','.MPB','.PNG','.IMY','.BIN','.LDT','.IDT'}
    treated={'SCRIPT.SDT','DATABASE.DAT','STAFFROLL.TXT'}
    for e in entries:
        name=e['name'];suffix=Path(name).suffix.upper()
        if name in treated or suffix in ignored_types or len(decoded[name])>2_000_000:continue
        if name.endswith('.DMD'):
            # DMD contiene estructuras de mapas; conservar candidatos separados.
            pass
        for run in scan_field_text(decoded[name],0,minletters=5):
            supplemental.append({'source':name,'category':'binario_otro_candidato','file_index':'',
                                 'confidence':'candidato_sin_estructura','offset_hex':xoff(run['offset']),**run})
    csvout(out/'reports/textos_binarios_no_confirmados.csv',
           ['source','category','file_index','confidence','offset','offset_hex','original','encoding','byte_length','raw_hex'],supplemental)
    # Proporcionar IDs persistentes dentro del mismo orden lógico de los archivos.
    for k,row in enumerate(texts,1):
        row['text_id']=f'CLD-{k:06d}'
        row['translation_es']=''
        row['review_status']='pendiente'
    fields=['text_id','category','source','file_index','script_id','script_file','command_index','instruction_id',
            'opcode_hex','offset','offset_hex','byte_length','encoding','confidence','original','translation_es','review_status','raw_hex']
    csvout(out/'corpus/todo_el_texto.csv',fields,texts)
    for label,pred in [
        ('dialogos',lambda x:x['category'] in ('dialogo','opcion','personaje_interlocutor')),
        ('interfaz_hud',lambda x:x['category']=='interfaz_sistema'),
        ('objetos_lugares_personajes',lambda x:x['source'].startswith('DATABASE.DAT/') and x['category']!='interfaz_sistema'),
        ('creditos',lambda x:x['category']=='creditos')]:
        csvout(out/f'corpus/{label}.csv',fields,[t for t in texts if pred(t)])
    catcount=collections.Counter(t['category'] for t in texts)
    report={'game':'Cladun: This Is an RPG (USA/PSP)','volume_id':volume,
            'iso_bytes':args.iso.stat().st_size,'iso_sha256':sha256(args.iso.read_bytes()),
            'source_data_dat_sha256':sha256(pack), 'files_iso':sum(not r['directory'] for r in iso_index),
            'pspfs_files':len(entries),'pspfs_decoded':len(decoded),'dsarc_members':len(dsindex),
            'script_stats':script_stats,'strtbl_slots':capacity,'strtbl_nonempty':len(strings),
            'total_text_rows_including_blank_credits':len(texts),'text_by_category':dict(catcount),
            'database_record_rows':len(db_records),'supplemental_unconfirmed_candidates':len(supplemental),
            'validation':{'pspfs_all_decoded':not decode_errors,'script_commands_all_parsed':True,
                          'translation_quality_checked':False,'on_device_verified':False,
                          'text_in_graphics_OCR_checked':False,'complete_coverage_proven':False},
            'notes':['Los datos de script tienen offset exacto, opcode, índice de bloque y nombre DSF.',
                     'Los campos de texto de registros binarios son candidatos sin esquema completo.',
                     'No se distribuyen archivos binarios, música, fuentes ni imágenes del juego.']}
    (out/'reports/cobertura.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__':main()
