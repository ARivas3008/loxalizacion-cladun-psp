# CLADUN ES — R31 autónomo: ejecutar acumulado 3.870 y seguir integración segura

Objetivo ROMhacking 100% real. Rama integracion-eventos-segura-20261120, PR #7 DRAFT sin merge/force push. Verificar HEAD y CI. Leer docs/R30_INTEGRACION_REPETICIONES.md, reports/R30_INTEGRACION_REPETICIONES.json, tools/r30_integrar_repeticiones.py, tools/r29_integrar_longitud_fija.py, tools/r28_relocation_map.py, docs/R26_ROMHACKING_100_AUDITORIA_2026-11-24.md. R30 añadió 90 a 56 en SCRIPT auténtico, 146 sin mover offsets; ISO USA aislada 26 ASCII, 348 PSPFS intactos. No hay C ni candidata acumulada.

1. Checkout íntegro y PPSSPP 1.20.4 oficial; ISO SHA b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f. Ejecutar:
```bash
python -m unittest discover -s tests -p 'test_r30*' -v
python tools/r30_integrar_repeticiones.py --iso-original /PRIVADO/Cladun_USA.iso --candidate /PRIVADO/R31_3870_EXPERIMENTAL.iso
```
Verificar 146 nuevos textos, 120 con fuente española existente, 0 desplazamientos, 46.308 no textuales exactos, 348 recursos ajenos exactos vs base, fuente y controles en PPSSPP A/B/A. No contar 26 ASCII dos veces. No publicar ISO.
2. Seleccionar más alternativas exactas por contexto, repetir validación de pares y controles; no forzar abreviaturas, relleno o ligaduras sin prueba. Investigar MIPS y 29 déficits de R26 con mapa R28. Conservar 3.724 oficiales hasta verificación C; no sustituir por 3.870 proyectadas.
3. Ejecutar pruebas globales, Go, QA cuatro áreas, verificar CI de HEAD, publicar evidencias no comerciales, actualizar cifras A/B/C por separado. Completar campaña, BPS y EXE Win64 E2E antes de liberar. Al finalizar reemplazar COMPLETAMENTE prompts/SIGUIENTE_TAREA.md por R32 autónomo con recursividad hasta 100% T/G/R/Q. No prometer ejecución automática.
