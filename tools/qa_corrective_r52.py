"""R52 corrective QA: exact STRTBL identity, atlas delta and conservative width triage."""
import csv
import json
import re
import struct
from pathlib import Path

RESOURCE = "DATABASE.DAT/STRTBL.DAT"
MENU = {26: (0xc68, "Magic Circle/Equip"), 28: (0xc85, "Character Creation"),
        29: (0xc98, "Character Color"), 30: (0xca8, "Dungeon"), 34: (0xcc8, "Save"),
        421: (0x30b4, "Character creation"), 447: (0x326f, "Character color"),
        448: (0x327f, "Select dungeon")}
GLOSSARY = {"save":"guardar", "load":"cargar", "settings":"configuración",
            "options":"opciones", "equipment":"equipo", "equip":"equipar",
            "magic circle":"círculo mágico", "character creation":"creación de personajes",
            "dungeon":"mazmorra", "select dungeon":"seleccionar mazmorra",
            "cancel":"cancelar", "confirm":"confirmar", "return":"volver"}

def save_overlay(rows):
    """Only the authenticated Save menu slot; canonical CSV is not mutated."""
    result=[]; hits=[]
    for src,dst in rows:
        if src.get("origen")==RESOURCE and src.get("indice_registro")=="34":
            if (int(src["offset_hex"],16)!=0xcc8 or src["original"]!="Save" or
                dst["original"]!="Save" or bytes.fromhex(src["bytes_hex"])!=b"Save" or
                src["grupo_id"]!=dst["grupo_id"] or dst["espanol"] not in ("Ahorrar","Guardar")):
                raise ValueError("Save preimage changed; inspect manually")
            hits.append({"id":src["grupo_id"],"before":dst["espanol"],"after":"Guardar"})
            dst={**dst,"espanol":"Guardar"}
        result.append((src,dst))
    if len(hits)!=1: raise ValueError("Expected exactly one Save menu slot")
    return result,hits[0]

# Native advances measured from the authenticated FONT.BIN; not box widths.
COMPACT = {26:("005234","Círculo mágico/Equipar","Círculo/Equipar",107,133,87),
           28:("005236","Creación de personajes","Crear personajes",116,142,102),
           29:("005237","Color del personaje","Color",95,118,29)}

def compact_menu_overlay(rows):
    """Experimental compact main-menu labels only, never submenu titles."""
    result=[]; hits=[]; seen=set()
    for src,dst in rows:
        if src.get('origen')==RESOURCE and src.get('indice_registro') in ('26','28','29'):
            idx=int(src['indice_registro']); gid,before,after,original_px,before_px,after_px=COMPACT[idx]
            off,original=MENU[idx]
            if (idx in seen or src['grupo_id']!=gid or dst['grupo_id']!=gid or
                src['original']!=original or dst['original']!=original or
                int(src['offset_hex'],16)!=off or bytes.fromhex(src['bytes_hex'])!=original.encode('ascii') or
                dst['espanol']!=before or after_px>original_px):
                raise ValueError('Compact menu preimage changed; inspect manually')
            seen.add(idx);dst={**dst,'espanol':after}
            hits.append({'id':gid,'before':before,'after':after,'original_px':original_px,
                         'before_px':before_px,'after_px':after_px,'visual_verified':False})
        result.append((src,dst))
    if seen!=set(COMPACT): raise ValueError('Missing compact menu slots')
    return result,hits

def verify_ink_delta(old,new):
    """Narrow atlas: only A1–B3, only historical 15→1, no changed originals."""
    if len(old)!=3072 or len(new)!=3072 or any(len(x)!=256 for x in [*old,*new]):
        raise ValueError("Invalid atlas geometry")
    changes=0
    for i,(a,b) in enumerate(zip(old,new)):
        expected=bytes(1 if v==15 else v for v in a) if 95<=i<114 else a
        if b!=expected: raise ValueError(f"Unexpected ink delta at cell {i}")
        changes+=sum(x!=y for x,y in zip(a,b))
    if changes!=100: raise ValueError(f"Expected 100 historical ink texels, got {changes}")
    return changes

def font_metrics(raw):
    if len(raw)<4: raise ValueError("Truncated font")
    n=struct.unpack_from('<I',raw)[0]
    if len(raw)!=4+n*4: raise ValueError("Font table length mismatch")
    records=list(struct.iter_unpack('<HBB',raw[4:]))
    codes=[r[0] for r in records]
    if codes!=sorted(set(codes)): raise ValueError("Font codes not unique/sorted")
    return {code:advance for code,_,advance in records}

def advance(text,widths):
    """Plain Unicode text only. Widths keyed by Unicode character, not byte count."""
    if any(c not in widths for c in text): raise ValueError("Unknown glyph/control")
    return sum(widths[c] for c in text)

def wrap_plain(text,widths,max_px,max_lines):
    """Candidate only: reject controls, forced breaks, spacing and overflowing words."""
    if type(max_px)!=int or type(max_lines)!=int or max_px<=0 or max_lines<=0:
        raise ValueError("Invalid box geometry")
    if not text or text.strip()!=text or '  ' in text or any(c.isspace() and c!=' ' for c in text) or re.search(r'[%{}<>\\\[\]]',text):
        raise ValueError("Requires script-aware manual reflow")
    lines=[]; current=''
    for word in text.split(' '):
        if advance(word,widths)>max_px: raise ValueError("Word exceeds box")
        trial=(current+' '+word).strip()
        if advance(trial,widths)>max_px:
            lines.append(current);current=word
        else: current=trial
    lines.append(current)
    if len(lines)>max_lines or ' '.join(lines)!=text: raise ValueError("Box capacity exceeded")
    return lines

def audit_context(rows):
    """Whole corpus triage: never certify language or visual coverage from flags."""
    rows=list(rows); ids=set(); findings=[]; menu=[]; mazmorra=[]
    for r in rows:
        gid=r['grupo_id']
        if gid in ids: raise ValueError('Duplicate corpus ID')
        ids.add(gid)
        original=r['original'].strip().casefold(); es=r['espanol'].strip().casefold()
        if es=='mazmorra':
            mazmorra.append({'id':gid,'resource':r['origen'],'original':r['original']})
        if r['origen']==RESOURCE:
            if original in GLOSSARY and es!=GLOSSARY[original]:
                findings.append({'id':gid,'rule':'CONTEXT_REVIEW','expected':GLOSSARY[original]})
            idx=int(r['indice_registro'])
            if idx in MENU:
                off,source=MENU[idx]
                if int(r['offset_hex'],16)!=off or r['original']!=source:
                    raise ValueError('Menu source identity changed')
                menu.append({'id':gid,'index':idx,'offset':hex(off),'original':source,'spanish':r['espanol']})
    if len(menu)!=len(MENU): raise ValueError('Missing authenticated menu slots')
    # Exercise the overlays against the actual corpus too; no master edits.
    pairs,save=save_overlay([(r,r) for r in rows])
    _,compact=compact_menu_overlay(pairs)
    return {'rows_scanned':len(rows),'context_review':findings,'menu_slots':menu,
            'exact_mazmorra_labels':mazmorra,'save_overlay':save,'compact_overlay':compact,
            'visual_verified':False,'linguistic_certified':False}

def main():
    import argparse
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--draft',type=Path,required=True);a=p.parse_args()
    with a.draft.open(encoding='utf-8-sig',newline='') as f: result=audit_context(csv.DictReader(f))
    if result['rows_scanned']!=9237: raise ValueError('Unexpected corpus coverage')
    print(json.dumps(result,ensure_ascii=False,indent=2))
if __name__=='__main__': main()
