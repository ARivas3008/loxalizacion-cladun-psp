#!/usr/bin/env python3
"""F3: comprobar INTRO de Cladun USA contra ISO ORIGINAL y borrador español.

Solo lectura. No reconstruye eventos, no mueve comandos y no inserta datos.
El inventario demuestra origen estructural, NO una escena ejecutada en PPSSPP.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import struct
from collections import Counter, defaultdict
from pathlib import Path

try:
    from tools.extract_cladun import (iso9660_entries, read_iso_file, pspfs_entries,
                                      dsarc_entries, decompress, script_table)
    from tools.charset_es import encode_spanish, decode_spanish
except ModuleNotFoundError:
    from extract_cladun import (iso9660_entries, read_iso_file, pspfs_entries,
                               dsarc_entries, decompress, script_table)
    from charset_es import encode_spanish, decode_spanish

USA_SHA = 'b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f'
ISO_SIZE = 305496064
FILES = frozenset(('demo1001_00.dsf', 'demo1001_01.dsf'))
EXPECTED_IDS = {
    100000: 'demo1001_00.dsf',
    100100: 'demo1001_00.dsf',
    100190: 'demo1001_00.dsf',
    100101: 'demo1001_01.dsf',
    100191: 'demo1001_01.dsf',
    100110: 'demo1001_01.dsf',
    100120: 'demo1001_01.dsf',
}
TEXT_OPS = frozenset((0x66, 0x69, 0x6E))
SCRIPT_SOURCE = 'SCRIPT.SDT/SCRIPT.DAT'


def digest_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for part in iter(lambda: f.read(4 * 1024 * 1024), b''):
            h.update(part)
    return h.hexdigest()


def safe_private_output(path: Path, repo_root: Path | None = None) -> Path:
    path = Path(path).expanduser()
    if not path.is_absolute() or path.suffix.lower() != '.json' or path.is_symlink():
        raise ValueError('Se exige nuevo JSON privado en ruta absoluta, sin symlink')
    path = path.resolve(strict=False)
    repo = (repo_root or Path(__file__).resolve().parents[1]).resolve()
    if path == repo or repo in path.parents or path.exists():
        raise ValueError('No sobrescribir ni crear en el repositorio')
    if any((ancestor / '.git').exists() for ancestor in path.parents):
        raise ValueError('No publicar informe en cualquier repositorio Git')
    return path


def parse_commands(raw: bytes, start: int, end: int) -> tuple[int, int, dict[int, bytes]]:
    if not 0 <= start <= end <= len(raw):
        raise ValueError('Límites de script inválidos')
    pos = start
    count = text_count = 0
    strings: dict[int, bytes] = {}
    while pos + 5 <= end:
        if not any(raw[pos:end]):
            break
        op = raw[pos]
        length = struct.unpack_from('<H', raw, pos + 3)[0]
        finish = pos + 5 + length
        if finish > end:
            raise ValueError('Instrucción se extiende más allá del script')
        count += 1
        if op in TEXT_OPS:
            if length < 3 or struct.unpack_from('<H', raw, pos + 5)[0] + 3 != length or raw[finish - 1] != 0:
                raise ValueError('Payload textual inesperado')
            text_count += 1
            content = raw[pos + 7:finish - 1]
            if content:
                if pos + 7 in strings:
                    raise ValueError('Offset textual duplicado')
                strings[pos + 7] = content
        pos = finish
    if any(raw[pos:end]):
        raise ValueError('Cola no interpretada en script')
    return count, text_count, strings


def inventory_script(script_data: bytes, script_table_raw: bytes) -> tuple[dict, dict[int, dict]]:
    rows = script_table(script_table_raw, 'SCRIPT.TBL')
    if len(rows) != 1625:
        raise ValueError('No son 1625 scripts originales')
    chosen = [(i, r) for i, r in enumerate(rows) if r['name'] in FILES]
    if {r['script_id']:r['name'] for _,r in chosen} != EXPECTED_IDS or len(chosen) != 7:
        raise ValueError('Identificación de capítulos demo1001 cambió')
    stats = []
    texts: dict[int,dict] = {}
    for i, r in chosen:
        start = r['start']
        end = rows[i+1]['start'] if i+1 < len(rows) else len(script_data)
        cmds, txtcmds, items = parse_commands(script_data, start, end)
        stats.append({
            'script_id':r['script_id'], 'script_file':r['name'],
            'commands_count':cmds, 'text_opcodes_including_empty':txtcmds,
            'nonempty_text_fields':len(items),
            'script_start_offset':start, 'script_end_offset':end,
        })
        for off,data in items.items():
            if off in texts:
                raise ValueError('Los intervalos de dos scripts se solapan')
            texts[off] = {'raw':data, 'script_id':r['script_id'],
                          'script_file':r['name']}
    if len(texts) != 97 or sum(x['commands_count'] for x in stats) != 878:
        raise ValueError('La escena original ya no coincide con el inventario autenticado')
    if sum(x['text_opcodes_including_empty'] for x in stats) != 98:
        raise ValueError('Contador de opcodes textuales original alterado')
    return {
        'script_records':stats, 'script_records_total':len(stats),
        'total_commands_in_7_blocks':sum(r['commands_count'] for r in stats),
        'total_text_opcodes_including_empty':98,
        'nonempty_text_fields':len(texts),
        'intro_runtime_playback_proven':False,
    }, texts


def audit_draft(draft: Path, texts: dict[int, dict]) -> dict:
    with Path(draft).open('r', encoding='utf-8-sig',newline='') as f:
        reader = csv.DictReader(f)
        required = {'grupo_id','origen','script','script_id','offset_hex',
                    'bytes_hex','longitud_original_bytes','espanol','original'}
        if not reader.fieldnames or not required.issubset(reader.fieldnames):
            raise ValueError('Borrador sin columnas requeridas')
        all_rows = list(reader)
    if len(all_rows) != 9237:
        raise ValueError('Corpus canónico de 9237 filas no encontrado')
    matches = [r for r in all_rows if r['script'] in FILES]
    if len(matches) != 97:
        raise ValueError('Cantidad de filas intro distinta de 97')
    categories = Counter()
    by_id = defaultdict(Counter)
    seen_offsets = set()
    total_old = total_new = 0
    ids = []
    for row in matches:
        if row['origen'] != SCRIPT_SOURCE:
            raise ValueError('Origen SCRIPT.DAT distinto')
        offset = int(row['offset_hex'],16)
        if offset in seen_offsets or offset not in texts:
            raise ValueError('Traducción no asociada a un offset original')
        seen_offsets.add(offset)
        raw = bytes.fromhex(row['bytes_hex'])
        stored = texts[offset]
        if (raw != stored['raw'] or int(row['longitud_original_bytes']) != len(raw)
                or int(row['script_id']) != stored['script_id']
                or row['script'] != stored['script_file']):
            raise ValueError('Identidad de texto vs SCRIPT original inválida')
        if raw.decode('cp932','strict') != row['original']:
            raise ValueError('Columna original no coincide con bytes CP932')
        if not row['espanol']:
            raise ValueError('Falta traducción española en introducción')
        translated = encode_spanish(row['espanol'])
        if decode_spanish(translated) != row['espanol']:
            raise ValueError('Texto español no recuperable en charset v0.1.5')
        result = ('BLOQUEADO_DIFERENTE_LONGITUD' if len(translated)!=len(raw)
                  else 'CANDIDATO_LONGITUD_COMPATIBLE' if translated!=raw
                  else 'SIN_CAMBIO')
        categories[result] += 1
        by_id[str(stored['script_id'])][result] += 1
        total_old += len(raw)
        total_new += len(translated)
        ids.append(row['grupo_id'])
    if seen_offsets != set(texts):
        raise ValueError('El borrador no cubre toda la introducción original')
    if dict(categories) != {
        'BLOQUEADO_DIFERENTE_LONGITUD':85,
        'CANDIDATO_LONGITUD_COMPATIBLE':11,
        'SIN_CAMBIO':1,
    }:
        raise ValueError('Las 97 clasificaciones cambiaron; reevaluar antes de integrar')
    return {
        'source':'CURRENT_PUBLIC_GITHUB_SPANISH_DRAFT_MATCHED_TO_REAL_ISO',
        'original_corpus_rows':len(all_rows),
        'intro_draft_rows':len(matches),
        'first_group_id':min(ids),'last_group_id':max(ids),
        'classification':dict(categories),
        'by_script_id':{k:dict(v) for k,v in sorted(by_id.items())},
        'original_text_bytes_total':total_old,
        'spanish_encoded_text_bytes_total':total_new,
        'all_spanish_rows_have_translation':all(bool(r['espanol']) for r in matches),
        'different_length_script_changes_authorized':False,
        'existing_f1_iso_runtime_translations_verified':False,
    }


def audit(iso: Path, draft: Path | None = None) -> dict:
    iso = Path(iso)
    if not iso.is_file() or iso.stat().st_size != ISO_SIZE or digest_file(iso) != USA_SHA:
        raise ValueError('ISO original USA incorrecta: tamaño o SHA')
    _, iso_entries = iso9660_entries(iso)
    regular = [r for r in iso_entries if not r['directory']]
    pvd_pmf = sum(r['path'].lower().endswith('.pmf') for r in regular)
    entry = next((r for r in regular if r['path'] == 'PSP_GAME/USRDIR/DATA.DAT'),None)
    if entry is None:
        raise ValueError('DATA.DAT ausente')
    pack = read_iso_file(iso,entry)
    psp = pspfs_entries(pack)
    if len(psp) != 349 or psp[231]['name'] != 'SCRIPT.SDT':
        raise ValueError('PSPFS inesperado')
    compressed = pack[psp[231]['offset']:psp[231]['offset']+psp[231]['size_stored']]
    archive,_ = decompress(compressed,psp[231]['size_expanded'])
    children = {c['name']:archive[c['offset']:c['offset']+c['size']] for c in dsarc_entries(archive)}
    if set(children) != {'AISCRIPT.DAT','AISCRIPT.TBL','SCRIPT.DAT','SCRIPT.TBL'}:
        raise ValueError('DSARC SCRIPT.SDT inesperado')
    source,raw = inventory_script(children['SCRIPT.DAT'],children['SCRIPT.TBL'])
    result = {
        'schema':'cladun.f3.intro_iso_and_draft_readonly.v1',
        'scope':'REAL_ISO_STATIC_AND_GITHUB_DRAFT_NOT_PPSSPP',
        'original_iso_size':ISO_SIZE,'original_iso_sha256':USA_SHA,
        'original_script_dat_sha256':hashlib.sha256(children['SCRIPT.DAT']).hexdigest(),
        'original_script_tbl_sha256':hashlib.sha256(children['SCRIPT.TBL']).hexdigest(),
        'iso9660_pmf_named_files':pvd_pmf,
        'pspfs_pmf_named_files':sum(e['name'].lower().endswith('.pmf') for e in psp),
        'no_pmf_name_does_not_rule_out_other_video_codecs':True,
        'original_intro_inventory':source,
        'draft_evaluation':audit_draft(draft,raw) if draft is not None else None,
        'binary_files_modified':False,'intro_translations_inserted':False,
        'script_command_offsets_changed':False,
        'ppsspp_gameplay_executed':False,'intro_in_game_span_correspondence_proven':False,
        'recommendation':'No insertar 85 cambios de longitud sin modelo de saltos/referencias y QA PPSSPP. 11 candidatos longitud igual NO equivalen a prueba F1 runtime.',
    }
    return result


def main() -> None:
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--iso-usa',type=Path,required=True)
    ap.add_argument('--borrador-es',type=Path)
    ap.add_argument('--reporte-privado',type=Path,required=True)
    args=ap.parse_args()
    output=safe_private_output(args.reporte_privado)
    result=audit(args.iso_usa,args.borrador_es)
    output.parent.mkdir(parents=True,exist_ok=True)
    with output.open('x',encoding='utf-8') as out:
        json.dump(result,out,ensure_ascii=False,indent=2)
        out.write('\n')
    print(json.dumps({'iso_original_verified':True,
                      'intro_fields':result['original_intro_inventory']['nonempty_text_fields'],
                      'draft_evaluation_complete':result['draft_evaluation'] is not None,
                      'ppsspp_gameplay_proven':False},ensure_ascii=False))


if __name__=='__main__':
    main()
