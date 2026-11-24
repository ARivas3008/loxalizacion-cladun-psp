# CLADUN ES — R29 autónomo: cierre ROMhacking con mapa exacto y PPSSPP

Objetivo 100% real, no 100% de planificación. Rama integracion-eventos-segura-20261120, PR #7 DRAFT, sin force push/merge. Antes de editar comprobar HEAD y CI. Leer docs/R28_ROMHACKING_GEOMETRIA.md, reports/R28_ROMHACKING_GEOMETRIA.json, tools/r28_relocation_map.py y docs/R26_ROMHACKING_100_AUDITORIA_2026-11-24.md, reports/R26_29_BLOQUES_PRIORIDAD.csv, tools/r26_piloto_total_8248_privado.py, tools/r26_auditar_reubicacion_eventos_total.py, tools/integrar_parche_seguro.py, tools/script_event_guard.py. Mantener T/G/R/Q independientes. No publicar ISO, binarios ni diálogos del juego como nuevos artefactos.

R28 autenticó ISO y reprodujo la geometría con longitudes del corpus y sustituciones ASCII sintéticas en RAM: 51.555 comandos movidos, 46.164 no textuales, 1.615 inicios, máximo 9.878 B, SCRIPT proyectado 643.136 B. Los 46.308 nontext permanecen exactos. Los IDs se repiten incluso por bloque+opcode; usar (bloque, orden) como clave del mapa. Las 2.562 coincidencias absolutas movidas y 105 relativas movidas NO son punteros probados. Investigar prioritariamente bloques 1193,1393,1415, que reciben coincidencias 0x0A con valor−100; los restantes 26 no quedan descartados. No cambiar operandos sin semántica real.

1. Checkout íntegro + PPSSPP oficial 1.20.4 en entorno con DNS funcional o binario aportado. Autenticar ISO SHA b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f. Ejecutar tests R28 y auditor real:
```bash
python tools/r28_relocation_map.py --iso-original /PRIVADO/Cladun_USA.iso --map-private /PRIVADO/R29_MAPA_51705.json
python tools/r26_auditar_reubicacion_eventos_total.py --iso-original /PRIVADO/Cladun_USA.iso
python tools/r26_piloto_total_8248_privado.py --manifest /PRIVADO/R29_MANIFIESTO_8248.json
```
Comparar números con proyección y diagnosticar cualquier diferencia. El mapa privado no contiene activos y no se publica por defecto.
2. Identificar dispatcher y semántica real de referencias con PPSSPP WS, MIPS PC y FD/PID autenticados. No usar coincidencias como parches. Auditar 29 bloques/215 B de déficit residual de ligaduras, y crear candidato seguro. Si procede un piloto de riesgo privado, el comando R26 exige --i-accept-experimental-moving-event-offsets; NO liberar candidato experimental.
3. A/B/A original/candidato/original: Opciones F1, 19 glifos, 44 ligaduras si se usan, prólogo, eventos, combate, mapas, guardado/carga, recursos no textuales, 8.248 IDs y matriz Q001–Q075. Validar BPS/Win64 E2E. Solo promover sustituciones con evidencia requerida A/B/C, 0 P0/P1 y aprobación contextual. Oficial 3.724/8.248 =45,15%, 4.524 diferidas hasta pruebas.
4. Ejecutar unittest completo, verificadores de corpus, QA 4 áreas, Go y git diff --check; comprobar CI push y PR HEAD exacto. Actualizar informes y estado solo según resultados. Si entorno bloqueado, ejecutar todas las pruebas independientes posibles y documentarlo. Al terminar reemplazar completamente prompts/SIGUIENTE_TAREA.md con R30 autónomo, con instrucciones recursivas equivalentes hasta cierre. No prometer ejecución automática.
