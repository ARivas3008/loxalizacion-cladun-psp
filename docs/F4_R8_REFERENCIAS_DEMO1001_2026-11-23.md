# CLADUN ES — F4-R8: 22 coincidencias numéricas de demo1001, no referencias demostradas (23/11/2026)

**F4 sigue BLOQUEADA para reubicación. F2/F3/F5/F6 siguen abiertas.** Se releyó la ISO original auténtica del usuario (305.496.064 bytes, SHA256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f) sin modificarla. La terminal no resolvió GitHub y PPSSPP oficial v1.20.4 no estaba disponible. No hay ejecución C nueva.

## A — resultado original auténtico

Se reparsearon **1.625 bloques, 51.705 comandos, 46.308 no textuales**. De ellos, siete bloques demo1001 contienen **878 comandos**. Las huellas originales de SCRIPT.DAT y SCRIPT.TBL coinciden con el baseline: c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358 y f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37.

Se inspeccionaron **101.659 ventanas little-endian u32** en payloads de comandos no textuales, incluyendo desplazamientos desalineados. Se compararon contra IDs, offsets absolutos e inicios relativos de comando del original.

| Igualdad numérica, NO referencia probada | Conteo | Fuente | Opcode y desplazamiento de argumento |
|---|---:|---|---|
| Igual a ID demo1001 | **1** | Otro bloque | 0x0A +0, ID 100100 |
| Igual a offset relativo de comando del mismo bloque demo1001 | **21** | demo1001 | 0x01 +0: 5; 0x02 +2: 4; 0x02 +6: 12 |
| Igual a offset absoluto de comando demo1001 | 0 | Todos los bloques | No observado |
| Igual a comienzo absoluto de bloque demo1001 | 0 | Todos los bloques | No observado |

De los 21 relativos, **16** ocurren en desplazamientos congruentes con +2 módulo 4. Las igualdades pueden ser valores ordinarios (por ejemplo 32, 85, 23 o 55). **No se ha demostrado que estos campos sean saltos, punteros, direcciones de RAM o instrucciones MIPS.** El barrido no descarta referencias de 16 bits, ordinales, indirectas, encriptadas u otros contenedores. Los 22 candidatos sirven únicamente para priorizar instrumentación real.

## B — herramientas y pruebas

Se añadieron tools/f4_referencias_demo1001.py y tests/test_f4_referencias_demo1001.py: **10 pruebas sintéticas locales PASS**. Junto con las 11 pruebas documentales preexistentes, **21 pruebas locales PASS** en el subconjunto presente, NO la suite completa del repositorio. El código autentica la ISO desde el parser existente y utiliza el lector oficial de comandos; produce solo histogramas sin texto comercial. La función nueva de barrido se aplicó de manera independiente a los comandos efectivamente extraídos del original; informe privado SHA256 7f23f8ae4ab52f97d6e6a86227a964325ec6f0c981c0de4644504bcff3b35c20.

Comandos en un checkout completo (NO se ejecutaron todos en esta sesión debido a DNS):

    python -m unittest discover -s tests -p 'test_f4_referencias_demo1001.py' -v
    python tools/f4_referencias_demo1001.py --iso-original /PRIVADO/USA.iso --reporte-privado /PRIVADO/F4_REFERENCIAS_NUEVO.json
    python tools/qa_cobertura_4_areas.py

La ISO, SCRIPT.DAT/TBL, EBOOT, fuentes, imágenes y BPS no se modificaron ni se enviaron a GitHub.

## C — bloqueo y siguiente prueba

No hubo PPSSPP oficial 1.20.4 en este relevo. No hay nuevo PC MIPS, GE/VRAM, escena de prólogo, captura ni vínculo dinámico para el opcode 0x0A o los 0x01/0x02. Es necesario autenticar PID/starttime, FD ISO y WS, detenerse sobre los tres opcodes durante demo1001, observar el consumo real del argumento y comprobar el destino y estado/retorno. Si el destino no es una referencia, eliminar la hipótesis y continuar búsqueda. No modificar 85 textos variables demo1001 ni los 4.524 SCRIPT.DAT globales bloqueados hasta tener modelo de eventos completo y regresión real.

**Invariantes:** --event-safe-only, white_new_ink=False, 2.721 glifos originales + 19 A1–B3, 349 PSPFS sin intervención, PR #7 OPEN/DRAFT; no merge ni contenido comercial en repositorio. T/G/R/Q: ninguno al 100%. La obligación recursiva continúa en prompts/SIGUIENTE_TAREA.md.
