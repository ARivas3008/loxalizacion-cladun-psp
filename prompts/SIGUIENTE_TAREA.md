# CLADUN ES — R30 autónomo: ejecutar acumulado 3.780, ampliar integración de longitud fija y cerrar ROMhacking

Objetivo 100% real. Verificar HEAD, CI push y PR #7 OPEN/DRAFT de rama integracion-eventos-segura-20261120, sin force push/merge. Leer docs/R29_INTEGRACION_LONGITUD_FIJA.md, reports/R29_INTEGRACION_LONGITUD_FIJA.json, tools/r29_integrar_longitud_fija.py, tools/r28_relocation_map.py y docs/R26_ROMHACKING_100_AUDITORIA_2026-11-24.md. R29 aplicó 56 textos a SCRIPT.DAT auténtico, 16 a ISO USA privada (348 PSPFS exactos, 51.705 offsets fijos, 46.308 no textuales intactos); 40 requieren fuente existente, no hay PPSSPP. El acumulado de 3.780 está implementado pero no ejecutado. No publicar ISO, BPS no aprobado ni activos comerciales.

1. Con checkout completo y original SHA b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f, ejecutar:
```bash
python -m unittest discover -s tests -p 'test_r29*' -v
python tools/r29_integrar_longitud_fija.py --iso-original /PRIVADO/Cladun_USA.iso --candidate /PRIVADO/R30_3780_EXPERIMENTAL.iso
```
Comprobar cada uno de los 56 IDs, 348 recursos ajenos exactos contra base, 3 DSARC hermanos, 0 offsets movidos, 19 glifos correctos. Ejecutar PPSSPP oficial 1.20.4 real A/B/A con PID/FD, render y eventos.
2. Buscar más alternativas de igual ancho sin cambiar sentido ni marcadores; no sumar 56 a 3.724 sin pruebas C. Trabajar lotes extensos, excluir duplicados y preservar glosario/género/contexto. No usar 44 ligaduras ni espacios finales sin prueba de render. Resolver referencias MIPS mediante R28 mapa por bloque/orden; 29 déficits de capacidad y 4.524 diferidas siguen bloqueados oficialmente.
3. Correr pruebas globales, Go, corpus, QA cuatro áreas y CI para HEAD. Actualizar informes y contadores según evidencia A/B/C; mantener 0 P0/P1 como criterio. Verificar BPS/EXE Windows E2E y campaña. No confundir prueba binaria con jugabilidad. Al terminar sustituir completamente prompts/SIGUIENTE_TAREA.md por R31 autónomo con obligación recursiva hasta 100% T/G/R/Q. No prometer ejecución automática.
