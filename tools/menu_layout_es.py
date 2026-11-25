#!/usr/bin/env python3
"""F1: corrección de presentación de Opciones sin modificar el texto literario.

El motor dimensiona Opciones con el relleno de STRTBL.DAT 005709.
PPSSPP 1.20.4: original 756px internos; v0.1.5 324px;
con SOLO este relleno 740px. La ventana vuelve a ser legible;
el diferencial residual de 16px y las otras pantallas siguen bajo QA.

No se aplica sobre --borrador experimental, para preservar los controles
aislados y evitar una doble transformación.
"""
from __future__ import annotations

from charset_es import encode_spanish

GROUP_ID = "005709"
SOURCE_ORIGINAL = "Show decimal points for damage" + "　" * 7
SOURCE_TRANSLATION = "Decimales de daño"
LAYOUT_TRANSLATION = SOURCE_TRANSLATION + "　" * 10 + " " * 7

def patch_canonical_menu_layout(rows):
    """Devuelve copias inmutables, modifica exclusivamente 005709.espanol."""
    output = []
    modified = 0
    for source, dest in rows:
        if source["grupo_id"] != GROUP_ID:
            output.append((source, dest))
            continue
        if (source["origen"] != "DATABASE.DAT/STRTBL.DAT"
                or source["original"] != SOURCE_ORIGINAL
                or dest["original"] != SOURCE_ORIGINAL
                or dest["espanol"] != SOURCE_TRANSLATION
                or source["bytes_hex"].upper() !=
                SOURCE_ORIGINAL.encode("cp932").hex().upper()):
            raise ValueError("F1: preimagen 005709 desconocida, no aplicar")
        encode_spanish(LAYOUT_TRANSLATION)  # Asegura codificación PSP reversible.
        output.append((source, {**dest, "espanol": LAYOUT_TRANSLATION}))
        modified += 1
    if modified != 1:
        raise ValueError("F1: ID 005709 ausente o duplicado")
    return output, {
        "id": GROUP_ID,
        "recurso": "DATABASE.DAT/STRTBL.DAT",
        "original_es": SOURCE_TRANSLATION,
        "presentacion_es": repr(LAYOUT_TRANSLATION),
        "cambios_solo_en_presentacion": True,
        "corpus_y_borrador_maestros_inmutables": True,
        "verificacion_ppsspp": "OPCIONES_756PX_INTERIOR_CANONICO_IGUAL_USA_PPSSPP_2026_11_21",
        "faltan": ["F2 símbolos por código/índice del atlas", "F3 introducción", "F4 scripts", "F5 QA aventura"],
    }


# F1 QA real 21/11/2026: «No» requiere un ASCII final para igualar
# el avance original OFF=84px. El texto literario conserva «No» sin relleno.
VALUES_EXPECTED = {
    "005710": ("          ON", "          Sí"),
    "005713": ("         OFF", "         No"),
}

def patch_canonical_menu_values(rows):
    output, changed, verified = [], 0, set()
    for src, dst in rows:
        gid = src["grupo_id"]
        if gid not in VALUES_EXPECTED:
            output.append((src, dst))
            continue
        original, translated = VALUES_EXPECTED[gid]
        if (gid in verified or src["origen"] != "DATABASE.DAT/STRTBL.DAT"
                or src["original"] != original or dst["original"] != original
                or src["bytes_hex"].upper() != original.encode("cp932").hex().upper()
                or dst["espanol"] != translated):
            raise ValueError(f"F1: preimagen de valor desconocida: {gid}")
        verified.add(gid)
        if gid == "005713":
            fixed = translated + " "
            encode_spanish(fixed)
            dst = {**dst, "espanol": fixed}
            changed += 1
        output.append((src, dst))
    if verified != set(VALUES_EXPECTED) or changed != 1:
        raise ValueError("F1: no se verificaron ambos valores ON/OFF")
    return output, {
        "originales_y_redaccion_es_inmutables": True,
        "anclaje_solo_presentacion": "005713 agrega un espacio ASCII final",
        "IDs_verificados": sorted(verified),
        "qa_ppsspp_menu_opciones": "PROBADO_VISUALMENTE_2026-11-21_NO_F2",
    }
