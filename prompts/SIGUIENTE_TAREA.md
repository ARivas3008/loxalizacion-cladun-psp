# CLADUN ES — R34 autónomo: acumulación de 1.302 + 146 y F1

Rama integracion-eventos-segura-20261120, PR #7 DRAFT. Sin force push ni merge. Verificar HEAD/CI. Leer reports/R33_PACKS_LARGOS.json, tools/r33_verificar_regresion.py, tools/r32_auditar_packs.py, tools/r31_bulk_padding.py y docs/R31_BULK_PADDING.md. R33 escribió 604 textos de gaps 3–6 y revalidó 90 de gap 7, 694 combinados, 245 bloques, 51.705 comandos, 46.308 no textuales exactos, 1.625 inicios, cero offsets movidos. ISO privada solo SCRIPT (sin fuente ni F1) SHA 5c305398f6c988fdbe93c30a13ace8cb1ecbec9e9b85023b2c7eaf492e26accd, 348 recursos ajenos exactos, BPS roundtrip exacto. R31 ya escribió 608 cortos por separado: 1.302/1.302 escritos entre relevos, pero NO todos combinados todavía. Oficial 3.724/8.248.

1. En checkout completo, con ISO original USA auténtica SHA b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f, ejecutar:
```bash
PYTHONPATH=tools:. python -m tools.r33_verificar_regresion /PRIVADO/USA.iso --pack long
PYTHONPATH=tools:. python -m tools.r32_auditar_packs /PRIVADO/USA.iso --pack all
PYTHONPATH=tools:. python tools/r31_bulk_padding.py --pack all --allow-experimental-padding --iso-original /PRIVADO/USA.iso --candidate /PRIVADO/R34_5172.iso
```
Confirmar 3.724 baseline +146 exactos +1302 padded, cero solapamiento, 349 PSPFS, fuente A1–B3, 2721 glifos originales, DSARC/ISO9660 y BPS roundtrip. Si checkout falla, ejecutar verificador independiente y separar con rigor lo efectivamente escrito de lo proyectado. No publicar ISO, BPS diagnóstico o recursos comerciales.
2. PPSSPP oficial 1.20.4 A/B/A de los gaps 1–7 con fuente correcta: ancho, wrapping, controles, prólogo, tutoriales, combate. No promover padding sin C. Resolver defectos detectados y ejecutar batería global, CI.
3. Después 2002 ligaduras R25 deduplicadas, 29 déficits R26 y referencias MIPS, F2–F6; cero P0/P1. Mantener rama experimental. Al terminar sustituir COMPLETAMENTE prompts/SIGUIENTE_TAREA.md por R35 autónomo con la misma obligación recursiva hasta 100% real de T/G/R/Q.
