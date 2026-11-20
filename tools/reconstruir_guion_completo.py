#!/usr/bin/env python3
"""Construye guiones de Cladun por ESCENA > CUADRO > fragmentos.

Conserva cada uno de los 9237 IDs originales sin escribir en el CSV maestro,
la ISO o los recursos binarios. NO infiere identidades sin marcador cercano.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

TOTAL = 9237
SCRIPT = "SCRIPT.SDT/SCRIPT.DAT"
TEXT_TYPES = {"dialogo", "opcion", "personaje_interlocutor"}
TERMINAL_ES = re.compile(r'[.!?…](?:[»"\']+)?\s*$')
TERMINAL_EN = re.compile(r'[.!?…](?:[»"\']+)?\s*$')


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as src:
        data = list(csv.DictReader(src))
    return data


def validate(source: list[dict], trans: list[dict]):
    if len(source) != len(trans) or len(source) != TOTAL:
        raise ValueError(f"Se esperaban {TOTAL} registros fuente y traducción en idéntico orden")
    fields = ("grupo_id", "text_id", "tipo", "original", "origen", "indice_registro", "script",
              "script_id", "orden_script", "offset_hex", "bytes_hex", "campo")
    seen = set()
    for n, (old, new) in enumerate(zip(source, trans), 1):
        if new["grupo_id"] in seen:
            raise ValueError("ID de grupo duplicado: " + new["grupo_id"])
        seen.add(new["grupo_id"])
        if any(old.get(f, "") != new.get(f, "") for f in fields):
            raise ValueError(f"El corpus fuente cambió en la fila {n}")


def escena(row: dict) -> tuple:
    return row["indice_registro"], row["script_id"], row["script"]


def join_exact(parts: list[str]) -> str:
    """Conservar literalmente los fragmentos; añadir solo separador visual.

    No elimina puntos que la traducción automática introdujo por error.
    La vista de QA debe dejar ver esos puntos y el mapa de fragmentos.
    """
    out = ""
    for i, part in enumerate(parts):
        # Los espacios originales internos se mantienen. Solo separamos campos.
        if i:
            out += "" if out.endswith((" ", "\n")) or part.startswith((" ", "\n")) else " "
        out += part
    return out


def flags_join(rows: list[dict]) -> list[str]:
    warnings: list[str] = []
    for prev, nxt in zip(rows, rows[1:]):
        a = prev["original"].strip()
        b = nxt["original"].strip()
        e = prev["espanol"].strip()
        f = nxt["espanol"].strip()
        if not a or not b or not e or not f:
            continue
        if not TERMINAL_EN.search(a) and TERMINAL_ES.search(e):
            warnings.append(f"PUNTUACION_ES_ANTES_DE_TERMINAR_ORIGINAL ({prev['text_id']}→{nxt['text_id']})")
        if (e.endswith(('.', '!', '?')) and f[:1].islower()
                and not TERMINAL_EN.search(a)):
            warnings.append(f"FRASE_CORTADA_POR_PUNTO ({prev['text_id']}→{nxt['text_id']})")
        if a.endswith((",", ":", ";")) and not e.endswith((",", ":", ";")):
            warnings.append(f"PAUSA_DEL_ORIGINAL_MODIFICADA ({prev['text_id']})")
    if any(int(b['orden_script']) != int(a['orden_script'])+1 for a,b in zip(rows, rows[1:])):
        warnings.append('UNION_ENTRE_CAJAS_POR_ORACION_INCOMPLETA_REVISAR')
    if any(not x['espanol'].strip() for x in rows):
        warnings.append("FRAGMENTO_SIN_TRADUCCION")
    if any('\ufffd' in x['espanol'] for x in rows):
        warnings.append("CARACTER_SUSTITUCION_UFFFD")
    return list(dict.fromkeys(warnings))


def build(source: list[dict], trans: list[dict]):
    validate(source, trans)
    groups: dict[tuple, list[dict]] = defaultdict(list)
    other: list[dict] = []
    for row in trans:
        if row['origen'] == SCRIPT and row['tipo'] in TEXT_TYPES:
            groups[escena(row)].append(row)
        else:
            other.append(row)

    items: list[dict] = []
    used: set[str] = set()
    warnings: list[dict] = []
    counts = Counter()
    turn_no = 0

    def append(item: dict):
        nonlocal turn_no
        turn_no += 1
        item['segmento_id'] = f'G{turn_no:05d}'
        item['ids'] = [x['text_id'] for x in item['rows']]
        item['grupos'] = [x['grupo_id'] for x in item['rows']]
        item['EN'] = join_exact([x['original'] for x in item['rows']])
        item['ES'] = join_exact([x['espanol'] for x in item['rows']])
        item['flags'] = flags_join(item['rows']) if item['tipo'] == 'dialogo' else []
        used.update(item['ids'])
        for label in item['flags']:
            warnings.append({'segmento_id':item['segmento_id'],
                             'escena': item['script'],
                             'ids':' | '.join(item['ids']),
                             'alerta':label,
                             'espanol_unido':item['ES'], 'original_unido':item['EN']})
        counts[item['tipo']] += 1
        items.append(item)

    for key, rows in groups.items():
        # Mantener orden de aparición en la extracción y comprobar monotonía.
        if any(int(b['orden_script']) <= int(a['orden_script']) for a,b in zip(rows,rows[1:])):
            raise ValueError(f"Orden no estrictamente ascendente en {key}")
        speaker: dict | None = None
        pending: dict | None = None
        pending_speaker_order: int | None = None

        def flush():
            nonlocal pending
            if pending is not None:
                append(pending)
                pending = None

        for row in rows:
            ordinal = int(row['orden_script'])
            typ = row['tipo']
            if typ == 'personaje_interlocutor':
                flush()
                speaker = row
                pending_speaker_order = ordinal
                append({'tipo':'nombre','rows':[row],'escena':key,
                        'script':row['script'],'hablante':row['espanol'] or row['original'],
                        'atribucion':'nombre_0x6E_explicito','orden_inicial':ordinal,
                        'orden_final':ordinal})
                continue
            if typ == 'opcion':
                flush()
                append({'tipo':'opcion','rows':[row],'escena':key,
                        'script':row['script'],'hablante':'ELECCION DEL JUGADOR',
                        'atribucion':'no_es_voz','orden_inicial':ordinal,'orden_final':ordinal})
                speaker = None
                pending_speaker_order = None
                continue
            # Un texto 0x66 por campo. Campos con órdenes consecutivos
            # forman líneas sucesivas de UNA misma caja; un salto indica
            # instrucción de control y otra caja (posible cambio de voz).
            if pending is not None:
                gap = ordinal - pending['orden_final']
                prev_en = pending['rows'][-1]['original'].strip()
                # Una oración físicamente partida por UN comando no textual
                # puede seguir siendo la misma intervención. Se une SOLO si
                # el inglés deja la sintaxis abierta y retoma en minúscula;
                # queda marcada como inferencia para revisión humana.
                continuation = (gap == 2 and prev_en and
                                not TERMINAL_EN.search(prev_en) and
                                row['original'].strip()[:1].islower())
                if gap == 1 or continuation:
                    pending['rows'].append(row)
                    pending['orden_final'] = ordinal
                    continue
            flush()
            if speaker is not None and pending_speaker_order is not None \
                    and 1 <= ordinal - pending_speaker_order <= 6:
                name = speaker['espanol'] or speaker['original']
                certainty = 'marcador_0x6E_inmediato' if ordinal-pending_speaker_order<=2 \
                    else 'marcador_0x6E_cercano_por_verificar'
            else:
                name = 'HABLANTE NO VERIFICADO'
                certainty = 'sin_marcador_de_hablante_para_esta_caja'
            # No arrastrar nombres a sucesivas cajas: incluso si los diálogos
            # se encuentran en el mismo bloque, puede haber otras voces.
            speaker = None
            pending_speaker_order = None
            pending = {'tipo':'dialogo','rows':[row],'escena':key,
                       'script':row['script'],'hablante':name,
                       'atribucion':certainty,'orden_inicial':ordinal,
                       'orden_final':ordinal}
        flush()

    # Todos los elementos que no son script van en el apéndice, sin alterarlos.
    for row in other:
        used.add(row['text_id'])
        if row['tipo'] in {'nombres_personajes','nombres_jefes'}:
            en = row['original'].strip()
            es = row['espanol'].strip()
            if (en and es and en != es and len(en.split()) == 1
                    and re.fullmatch(r'[A-Za-z][A-Za-z\-\']*', en)):
                warnings.append({'segmento_id':'RECURSO', 'escena':row['origen'],
                                 'ids':row['text_id'],
                                 'alerta':'NOMBRE_PROPIO_TRADUCIDO_REVISAR',
                                 'espanol_unido':es,'original_unido':en})
        if not row['espanol'].strip():
            warnings.append({'segmento_id':'RECURSO','escena':row['origen'],
                             'ids':row['text_id'],'alerta':'SIN_TRADUCCION',
                             'espanol_unido':'','original_unido':row['original']})
    if len(used) != TOTAL or used != {x['text_id'] for x in trans}:
        raise ValueError('El guion reconstruido no conserva exactamente los 9237 IDs')
    return groups, items, other, warnings, counts


def _human_line(label: str, content: str) -> str:
    if '\n' not in content and '\r' not in content:
        return f'{label}: {content}'
    return f'{label}: '+content.replace('\r\n','\n').replace('\r','\n').replace('\n','\n  ')


def render(items: list[dict], other: list[dict], mode: str, with_appendix: bool = False) -> str:
    assert mode in ('lectura','revision')
    parts = ["CLADUN: THIS IS AN RPG! — GUION COMPLETO RECONSTRUIDO",
             "Edición USA PSP | Versión de lectura, NO es texto listo para insertar.",
             "Las líneas de una misma caja de diálogo se reúnen en un párrafo completo.",
             "Cada nueva caja se conserva separada: puede cambiar el interlocutor.",
             "Los nombres solo se afirman cuando hay un marcador 0x6E cercano.",
             "El español sigue el CSV literalmente; los errores no se corrigen a escondidas.", ""]
    current = None
    for item in items:
        key = item['escena']
        if key != current:
            current = key
            parts += ['\n'+'='*86,
                      f"ESCENA | {key[2]} | script_id={key[1]} | bloque={key[0]}",
                      '='*86]
        typ = item['tipo']
        if typ == 'nombre':
            parts += [f"[NOMBRE EN PANTALLA] {item['hablante']}" +
                      (f"   ({item['ids'][0]})" if mode == 'revision' else '')]
            continue
        if typ == 'opcion':
            parts.append(f"  OPCIÓN: {item['ES']}"+
                         (f"   [{item['ids'][0]}]" if mode=='revision' else ''))
            continue
        human = item['hablante']
        if mode == 'lectura':
            parts += ['\n'+_human_line(human,item['ES'])]
        else:
            parts += ['\n' + f"{human} | CUADRO {item['segmento_id']} [{item['atribucion']}]",
                      _human_line('ES',item['ES']),
                      _human_line('EN',item['EN']),
                      'IDS: ' + ', '.join(item['ids']) +
                      f" | órdenes {item['orden_inicial']}-{item['orden_final']}"]
            if item['flags']:
                parts.append('ALERTAS: '+'; '.join(item['flags']))
    if with_appendix:
        parts += ['\n'+'#'*86,'APÉNDICE: TODOS LOS TEXTOS NO NARRATIVOS',
                  'Cada elemento mantiene su ID; no se confunden nombres, menús ni instrucciones.',
                  '#'*86]
        currentfile = None
        currentrec = None
        for row in other:
            newfile = row['origen']
            if newfile != currentfile:
                parts += ['\n'+'='*70, 'RECURSO: '+newfile, '='*70]
                currentfile = newfile
                currentrec = None
            if row['indice_registro'] != currentrec:
                currentrec = row['indice_registro']
                parts.append('\nREGISTRO: '+(currentrec or '(sin índice)'))
            parts += [f"[{row['text_id']}] {row['tipo']} | {row['campo']}",
                      _human_line('ES',row['espanol'] or '[SIN TRADUCCION]'),
                      _human_line('EN',row['original'])]
    return '\n'.join(parts).rstrip()+'\n'


def write_report(out: Path, source_path: Path, trans_path: Path, groups: dict,
                 items: list[dict], other: list[dict], warnings: list[dict], counts: Counter) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    def dump(name, text):
        (out/name).write_text(text, encoding='utf-8-sig')
    dump('CLADUN_GUION_RECONSTRUIDO_LECTURA_ES.txt',render(items,other,'lectura'))
    dump('CLADUN_GUION_RECONSTRUIDO_COTEJO_ES_EN.txt',render(items,other,'revision'))
    dump('CLADUN_TODO_TEXTO_RECONSTRUIDO_ES_EN.txt',render(items,other,'revision',True))
    cols = ['segmento_id','tipo','script','indice_registro','script_id','orden_inicial',
            'orden_final','hablante','atribucion','ids','grupos','fragmentos',
            'original_completo','espanol_completo','alertas','propuesta_es','nota_editorial']
    with (out/'CLADUN_MAPA_DE_DIALOGOS_RECONSTRUIDOS.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=cols)
        writer.writeheader()
        for item in items:
            writer.writerow({
                'segmento_id':item['segmento_id'],'tipo':item['tipo'],
                'script':item['script'],'indice_registro':item['escena'][0],
                'script_id':item['escena'][1], 'orden_inicial':item['orden_inicial'],
                'orden_final':item['orden_final'],'hablante':item['hablante'],
                'atribucion':item['atribucion'], 'ids':' | '.join(item['ids']),
                'grupos':' | '.join(item['grupos']), 'fragmentos':len(item['rows']),
                'original_completo':item['EN'],'espanol_completo':item['ES'],
                'alertas':' | '.join(item['flags']),'propuesta_es':'', 'nota_editorial':''})
    fields=['segmento_id','escena','ids','alerta','espanol_unido','original_unido']
    with (out/'CLADUN_ALERTAS_RECONSTRUCCION.csv').open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields)
        writer.writeheader();writer.writerows(warnings)
    tally=Counter(w['alerta'].split(' (',1)[0] for w in warnings)
    data={
        'estado':'RECONSTRUCCION_DE_LECTURA_NO_REINSERCION',
        'total_registros_originales':TOTAL,
        'fragmentos_script':sum(len(i['rows']) for i in items),
        'registros_otros_recursos':len(other),
        'escenas':len(groups),
        'cuadros_dialogo_reconstruidos':counts['dialogo'],
        'nombres_de_hablante':counts['nombre'],
        'opciones':counts['opcion'],
        'cuadros_dialogo_de_multiples_fragmentos':sum(i['tipo']=='dialogo' and len(i['rows'])>1 for i in items),
        'fragmentos_reunidos_en_cuadros_largos':sum(len(i['rows']) for i in items if i['tipo']=='dialogo' and len(i['rows'])>1),
        'atribuciones_por_fiabilidad':dict(Counter(i['atribucion'] for i in items if i['tipo']=='dialogo')),
        'alertas_heuristicas':dict(tally),
        'csv_fuente_sha256':hashlib.sha256(source_path.read_bytes()).hexdigest(),
        'csv_borrador_sha256':hashlib.sha256(trans_path.read_bytes()).hexdigest(),
        'integridad':{'ids_conservados':TOTAL,'csv_original_sin_modificar':True,
                      'traduccion_sin_reescribir':True,'prueba_visual_ppsspp':False},
        'advertencia':'Los cuadros se agrupan por comandos de texto consecutivos, no por identidad narrativa. Los saltos de control se conservan como separación; el lector debe revisar cambios de hablante y las alertas.'
    }
    (out/'CLADUN_RESUMEN_RECONSTRUCCION.json').write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return data


def main(args=None):
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--fuente',type=Path,default=Path('corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv'))
    ap.add_argument('--borrador',type=Path,default=Path('traduccion/CLADUN_BORRADOR_ES.csv'))
    ap.add_argument('--salida',type=Path,default=Path('lectura'))
    opts=ap.parse_args(args)
    a=read_csv(opts.fuente);b=read_csv(opts.borrador)
    g,items,other,warnings,counts=build(a,b)
    info=write_report(opts.salida,opts.fuente,opts.borrador,g,items,other,warnings,counts)
    print(json.dumps(info,ensure_ascii=False,indent=2))
    return info


if __name__=='__main__':
    main()
