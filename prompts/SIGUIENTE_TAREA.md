# CLADUN ES — R33 autónomo: cierre de packs largos y acumulación auténtica

Rama integracion-eventos-segura-20261120; PR #7 DRAFT. No force push, merge ni publicación de recursos comerciales. Verificar HEAD y CI reales. Leer reports/R32_AUDITORIA_PACKS.json, tools/r32_auditar_packs.py, tools/r31_bulk_padding.py y docs/R31_BULK_PADDING.md. R32 verificó ISO USA SHA b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f, 349 PSPFS, 1186 DSARC hijos, 77 bloques IMY, 1302 preimágenes; escribió 90 textos de gap 7 en SCRIPT.DAT auténtico y recomprimió 5/8 IMY, roundtrip exacto, 51705 comandos, 46308 no textuales intactos y cero offsets movidos. No ISO acumulada F1, no PPSSPP C. Otros 604 gap 3–6 no escritos. No contabilizar 90 como oficiales.

1. Checkout completo, con PYTHONPATH=tools:. ejecutar:
```bash
PYTHONPATH=tools:. python -m tools.r32_auditar_packs /PRIVADO/USA.iso --pack all
PYTHONPATH=tools:. python -m unittest discover -s tests -v
```
Comprobar todos los paquetes individuales, short 608, long 694, all 1302; confirmar SHA gap 7 y compararlo con el verificador independiente. Corregir cualquier discrepancia de compresión sin alterar geometría.
2. Construir ISO acumulada F1 experimental con tools/r31_bulk_padding.py --pack all --allow-experimental-padding --iso-original /PRIVADO/USA.iso --candidate /PRIVADO/R33_5172.iso; comprobar 3724 baseline +146 exactos +1302 acolchados sin solapamiento. Auditar 349 recursos, DSARC/ISO9660, 51705 comandos y BPS roundtrip. No confundir proyección 5172/8248 con hecho.
3. PPSSPP oficial 1.20.4 A/B/A en opciones, prólogo, tutoriales, diálogos y combate, medir ancho, wrapping, puntuación y eventos para todos los gaps 1–7. Si hay regresión, aislar por familia y no promover. Mantener 3724/8248 oficiales hasta C.
4. Luego 2002 ligaduras R25 en bloques grandes deduplicados, 29 déficits R26, referencias MIPS y QA F2-F6. CI real, evidencias A/B/C, cero P0/P1. Al terminar sustituir COMPLETAMENTE prompts/SIGUIENTE_TAREA.md por R34 autónomo con la misma obligación recursiva hasta 100% real de las cuatro áreas.
