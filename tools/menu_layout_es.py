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
LAYOUT_TRANSLATION = SOURCE_TRANSLATION + "　" * 10 + " " * 6

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
        "verificacion_ppsspp": "CORRECCION_740PX_INTERIOR_VS_756PX_USA_ORIGINAL",
        "faltan": ["margen residual de 16px", "valor EN de 005710", "QA de todas las escenas"],
    }
