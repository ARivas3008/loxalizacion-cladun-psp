# R28 — mapa de reubicación: diagnóstico A/B, sin promoción de cobertura

Fecha 24/11/2026. HEAD inicial 557eefa77629e7c571b38e1192f9595cefe912cf, CI push 45401089669 y PR 45401106305 SUCCESS. PR #7 OPEN/DRAFT. Se autenticó de nuevo la ISO original de 305.496.064 bytes (SHA-256 exacta histórica); SCRIPT.DAT/TBL y AISCRIPT.DAT/TBL extraídos privadamente. No se modificó la ISO.

El conector GitHub permite leer el blob íntegro del CSV de 3.919.106 bytes, pero el contenedor no puede resolver github.com ni descargar el checkout o PPSSPP. Se procesaron los 5.207 textos SCRIPT del blob 400a9c9ec06f7456b5ec6e11f7502d711b0a976e y transfirieron exclusivamente las diferencias de longitud, ordenadas por offset. Las clases de caracteres CP932/19 signos españoles y los totales anteriores coinciden: 2.883 crecen 17.108 bytes, 1.641 se acortan 7.414 bytes, 683 mantienen longitud. El cotejo FNV32 de los pares offset/longitud original es 2593180738 en ambos entornos (control de transferencia, no hash criptográfico).

En memoria sobre SCRIPT.DAT auténtico se reconstruyeron los 4.524 campos de longitud variable con bytes ASCII sintéticos del tamaño proyectado, conservando los otros comandos. Resultado: 643.136 B frente a 633.344 B, 51.555/51.705 offsets de comando desplazados, 46.164/46.308 no textuales desplazados, 1.615/1.625 inicios de bloque movidos, desplazamiento máximo 9.878 B. Los 46.308 no textuales se cotejaron byte a byte. Esto mide geometría, **no inserción de traducción real** ni ISO candidata completa.

No basta la identidad por instruction_id: 1.040 bloques presentan duplicados; 8.668 apariciones exceden una por (bloque, ID), y 3.214 exceden una por (bloque, opcode, ID). La clave estable para el mapa es (bloque, orden), con ID y opcode como verificación; no se infiere cómo el motor resuelve los saltos.

Escaneo u32 deslizante: 2.883 coincidencias numéricas con offsets absolutos (2.562 destinos movidos), 1.451 relativas al bloque (105 destinos cambian su posición relativa). Tres coincidencias opcode 0x0A con SCRIPT ID = operando − 100 conducen a bloques prioritarios 1193, 1393 y 1415. Todas son coincidencias, no referencias confirmadas; no se modifica ningún operando por ellas.

Nueva herramienta: `tools/r28_relocation_map.py` reconstruye en memoria con el planificador canónico Python, verifica el guard R26 y emite un mapa privado de 51.705 pares antiguos/nuevos, sin texto/bytes comerciales. Incluye controles de identidad biyectiva, orden, no-texto exacto y clasificación. Las métricas publicadas proceden de la simulación independiente de longitudes descrita arriba; no se ejecutó el wrapper íntegro contra la ISO en este entorno. Se agregaron 10 pruebas unitarias para CI.

```bash
python -m unittest discover -s tests -p 'test_r28*' -v
python tools/r28_relocation_map.py --iso-original /PRIVADO/Cladun_USA.iso --map-private /PRIVADO/R28_MAPA_51705.json
```

La reubicación no se autoriza hasta demostrar semántica MIPS, resolver los 29 déficits de capacidad de la alternativa de ligaduras o justificar otra estrategia, y validar PPSSPP. Cobertura oficial permanece 3.724/8.248; no hay C nuevo. Ver reports/R28_ROMHACKING_GEOMETRIA.json.
