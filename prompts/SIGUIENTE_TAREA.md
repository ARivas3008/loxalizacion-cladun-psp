# CLADUN ES — RELEVO AUTÓNOMO F3/F4-R9: INVESTIGAR 0x0A Y 0x01/0x02 SIN ROMPER EVENTOS; T/G/R/Q ABIERTAS

**Corte:** 2026-11-23T21:29:33Z UTC. Repositorio: https://github.com/ARivas3008/loxalizacion-cladun-psp. Rama: integracion-eventos-segura-20261120. PR #7: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7, estado OPEN/DRAFT, base revision-manual-dialogos. HEAD comprobado al inicio R8: 097a6b81056262be91e758fed380ed9f0e7a53f5. **NO asumir que es HEAD actual**: se publicaron commits R8 posteriores. Comprobar HEAD, PR y Actions de nuevo antes de modificar y después de publicar. Nunca force push, rebase destructivo ni fusionar PR #7 mientras existan tareas abiertas.

Actúa como equipo senior integrado: T (traducción natural española), G (texturas indexadas IMY/CLUT, fuentes CP932), R (ingeniería inversa PSP MIPS, ISO9660, PSPFS, DSARC, BPS y Go), Q (PPSSPP oficial v1.20.4, juegos completos y Windows x64). **Ejecuta código, inspecciones y pruebas reales EN ESTE TURNO; no te limites a planes.** Separar evidencia A (ISO original auténtica verificada), B (tests sintéticos/corpus/CI) y C (juego realmente ejecutado en PPSSPP oficial). Nunca fabricar PCs MIPS, capturas, tramas GPU, direcciones, hashes, resultados de CI o commits.

## 0. REGLA RECURSIVA INNEGOCIABLE (copiarla íntegramente)

**Si cualquiera de los cuatro apartados sigue por debajo del 100 % VERIFICADO, al terminar CADA relevo debes sustituir por completo prompts/SIGUIENTE_TAREA.md en la rama de trabajo mediante un NUEVO prompt autosuficiente y exigirle que haga lo mismo al acabar.** No copies sin actualizar el prompt anterior. Incluye HEAD real, PR y CI reales, estado de cuatro áreas, pruebas A/B/C, hashes reales, archivos concretos, comandos correctos, fallos, hipótesis, tareas no terminadas, próximos criterios de cierre y prohibiciones. Muéstralo íntegro al usuario. Continúa por relevos en nuevas sesiones **solo mientras** existan tareas pendientes; cuando estén **las cuatro al 100 % confirmado**, cambia el entregable a informe final, checklist de lanzamiento y prompt de mantenimiento pospublicación. No generes artificialmente otro relevo de desarrollo tras cierre completo. Si no tienes acceso a GitHub, entrega el archivo nuevo en el chat y marca la escritura remota como NO EJECUTADA.

Si hay bloqueo (por ejemplo PPSSPP ausente), realizar máxima auditoría segura y tests en el turno, documentar el bloqueo y la condición necesaria para desbloquear, y crear nuevo relevo. Una prueba B nunca sustituye C; no prometer trabajo asíncrono.

## 1. Estado inicial VERIFICABLE y nuevos hallazgos de R8

| Área | Métrica actual y situación | Para llegar a 100 % VERIFICADO |
|---|---|---|
| TRADUCCIÓN T | 9.235 de 9.237 filas del CSV con español, 99,98 % cobertura escrita; no calidad ni ejecución completas | 2 orígenes truncados 008723 y 008724, escenas/cajas, glosario, tildes, tutoriales, prólogo, texto gráfico y aprobación contextual en PPSSPP |
| GRÁFICOS G | global NO MEDIBLE; se estudiaron seis PNG SYS.DAT2 y 27 IMY SYSGRA, fuente 2.721 glifos originales más 19 A1–B3 | inventariar todos los rótulos, proteger ROI/CLUT, demostrar TUIKA en combate y 19 glifos en múltiples escenas y tintas |
| ROMHACKING R | 3.724 de 8.248 sustituciones aplicadas en candidato protegido histórico, **45,15 %** de ese conjunto; **4.524 diferidas** | validar saltos MIPS, reubicar sin daño, cero diferidas, BPS final e ISO/EXE Windows comprobados |
| BETATESTING Q | 42 casos iniciales inventariados, todos NOT_RUN en R8; cobertura global NO MEDIBLE | ampliar universo de casos, ejecutar juego real C y Windows x64 E2E con 0 P0/P1 abiertos |

A (nuevo R8): la ISO USA original aportada por el usuario mide 305.496.064 bytes y SHA256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f. En R8 estuvo disponible de forma PRIVADA, fuera del repo; verificar si sigue montada, sin inferir ruta. DATA.DAT tiene 349 PSPFS. Se releyeron SCRIPT.DAT SHA256 c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358 y SCRIPT.TBL SHA256 f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37. Reparseo del original: **1.625 bloques, 51.705 comandos, 46.308 no textuales, siete bloques demo1001 y 878 comandos demo1001.** Se hizo una nueva comprobación de **101.659 ventanas u32** en argumentos no textuales.

**Resultado nuevo que debe guiar F4:** una coincidencia de ID script 100100 en un comando de otro bloque con opcode 0x0A y payload +0; **21 coincidencias de enteros relativos en comandos demo1001**: 0x01+0 (5), 0x02+2 (4), 0x02+6 (12). Dieciséis relativas caen en offsets +2 mod 4. Cero coincidencias u32 con offsets absolutos de comando o comienzo absoluto de bloque demo1001. **Coincidencia no es puntero, salto, PC ni referencia semántica; no se descartan otras formas de referencias.** Ver docs/F4_R8_REFERENCIAS_DEMO1001_2026-11-23.md y reports/F4_R8_REFERENCIAS_DEMO1001_2026-11-23.json. SHA256 informe privado de metadatos 7f23f8ae4ab52f97d6e6a86227a964325ec6f0c981c0de4644504bcff3b35c20.

B: nuevo tools/f4_referencias_demo1001.py con tests/test_f4_referencias_demo1001.py (**10 pruebas sintéticas PASS locales**). Con 11 pruebas sintéticas previas de QA documental, 21 tests de ese subconjunto PASS local, NO suite completa. Verificar Actions del HEAD actual. C: **PPSSPP v1.20.4 NO ejecutado en R8**, no hay PCs/GE/VRAM/combate/prologo nuevos. Históricamente F1 Opciones 756px interior y primer mapa alcanzado en PPSSPP, pero no certificación de aventura.

## 2. Lectura y arranque obligado

Leer completos antes de modificar: AGENTS.md, README.md, CHANGELOG.md, docs/REPRODUCIBILIDAD.md, docs/PROTOCOLO_REINSERCION_FAIL_CLOSED.md, docs/INTEGRACION_EVENTOS_PROTEGIDOS_2026-11-20.md, docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md, docs/F4_R8_REFERENCIAS_DEMO1001_2026-11-23.md, reports/F4_R8_REFERENCIAS_DEMO1001_2026-11-23.json, tools/f4_referencias_demo1001.py, tools/f3_referencias_riesgo.py, tools/script_event_guard.py, tools/f3_anclar_intro.py, tools/f3_simular_intro_mismo_tamano.py, tools/f3_presupuesto_padding_intro.py, docs/F3_R6_PADDING_ORIGINAL_Y_CAPACIDAD_2026-11-23.md, docs/F3_ANIME_IMY_ESTRUCTURAS_2026-11-23.md, docs/F2_TUIKA_SUBREGIONES_PROTEGIDAS_2026-11-23.md, reports/ESTADO_CONTINUIDAD_PPSSPP.json, reports/COBERTURA_4_AREAS.json, qa/MATRIZ_BETATESTING_COBERTURA.csv, docs/ESTADO_CIERRE_4_AREAS.md y este prompt.

Comandos en checkout auténtico (no fingir si DNS impide obtenerlo):

    git fetch origin
    git switch integracion-eventos-segura-20261120
    git pull --ff-only
    git status --short
    git rev-parse HEAD
    python -m unittest discover -s tests -v
    python -m unittest discover -s tests -p 'test_f4_referencias_demo1001.py' -v
    python tools/qa_cobertura_4_areas.py
    python tools/qa_cobertura_4_areas.py --require-closed
    python tools/verificar_integridad.py --raiz .
    python tools/verificar_borrador_es.py
    python tools/auditar_preinsercion_es.py --reporte /tmp/cladun-preflight.json
    python tools/reportar_integrabilidad_es.py --reporte /tmp/cladun-integrabilidad.json
    (cd patcher && go test ./...)
    git diff --check

El comando --require-closed debe devolver no cero hasta que haya cuatro cierres. Con ISO autenticada en ruta PRIVADA, crear informes JSON NUEVOS fuera de Git:

    python tools/f4_referencias_demo1001.py --iso-original /PRIVADO/Cladun_USA_original.iso --reporte-privado /PRIVADO/F4_REFERENCIAS_R9_NUEVO.json
    python tools/f3_simular_intro_mismo_tamano.py --iso-original /PRIVADO/Cladun_USA_original.iso --reporte-privado /PRIVADO/F3_SIM_R9_NUEVO.json
    python tools/f3_presupuesto_padding_intro.py --iso-original /PRIVADO/Cladun_USA_original.iso --reporte-privado /PRIVADO/F3_PADDING_R9_NUEVO.json

Sin terminal GitHub, usar conector GitHub con lectura de HEAD, actualización no forzada y comprobación de CI push y PR en el HEAD FINAL. No publicar ISO, DATA.DAT, EBOOT, BPS con recursos comerciales sustanciales, FONT, IMY, capturas, dumps RAM/GE/VRAM ni imágenes del juego.

## 3. P0 — Experimentos concretos para avanzar en F4

**F4-a: comando externo 0x0A que contiene u32 igual al ID 100100.** Con PPSSPP oficial 1.20.4 autenticar binario, PID/starttime, ISO en file descriptor, WebSocket propio 24192 y juego efectivo; reproducir la escena que consume ese comando. Registrar verdadero PC y lecturas RAM. Investigar si el argumento +0 funciona como ID de destino, variable o literal. Demostrar destino efectivo, stack/estado y retorno con dos rutas; si no lo es, descartar hipótesis. No elevar esa sola igualdad numérica a referencia probada.

**F4-b: 21 coincidencias relativas.** En los siete bloques demo1001, instrumentar opcode 0x01 offset +0 y opcode 0x02 offsets +2/+6; determinar si los enteros son comandos, ordinales, tiempos/contadores u otro formato observando comportamiento real. Distinguir referencias de 16 bits, relativas a bloque, referencias a script externo, IDs de comando y punteros del intérprete. Los valores pequeños pueden ser coincidencias accidentales. Desarrollar modelo reversible solo tras prueba MIPS, tests negativos y comparación A/B PPSSPP.

**F4-c: 85 textos variables demo1001.** Los 97 textos en siete bloques incluyen 11 cambios de misma longitud simulados en memoria, 85 variables bloqueados y 1 idéntico. Una concatenación hipotética afectaría 588/878 inicios y +131 bytes netos; padding original 48 bytes y faltan al menos 144 bytes en tres bloques alineados a 16. No mover un solo comando sin semántica comprobada de todos los saltos relevantes. Extender después el reubicador fail-closed por lotes a 4.524 traducciones pospuestas, con reparseo 51.705 comandos, sin alterar no-textos, audio, retratos, sprites ni tiles. Mantener --experimental-parcial --event-safe-only hasta seguridad demostrada.

## 4. P0 F3 — Prologo gráfico

Frase inglesa visible: "Some say, because the treasures were there." La procedencia de sus letras NO está probada. ANIME000.IDT contiene 231 firmas IMY (136 tipo00, 95 tipo02), no 231 frames demostrados; renombrar ANIME000 provocó crash antes del título y NO prueba dónde están las letras. No repetir esa sonda destructiva. PPSSPP original con juego real → escena exacta → traza I/O→RAM→GE/VRAM con TEXADDR/CLUT/PRIM → origen verificable. Según resultado, edición de ROI bitmap o localización de script concreta, con original/sonda/original y sin CLUT global. No llamar a demo1001 fuente de esta frase sin prueba.

## 5. P1 — Traducción, gráficos, QA y F6

T: revisar 9.237 registros, naturalidad por escena/hablante, glosario, 2.216 cajas/586 escenas, variables/códigos/tildes, 008723/008724 origen truncado. Mantener corpus origen inmutable; sincronizar CSV, dos TXT, guiones y logs de cambios del mismo commit. Texto fuera del CSV y texto del prólogo deben incorporarse al universo visible.

G: SYS.DAT2 seis PNG; SYSGRA.ARC 27 IMY; TUIKA_MES.IMY 256×256 4bpp con 9.144 texeles en CLUT2 y 3.506 en siete subregiones protegidas. No cambiar CLUT2 global como release. A/B/A en combate verdadero y máscaras ROI seguras; 19 glifos áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō en HUD, diálogos, menús y combate; preservar 2.721 glifos originales y white_new_ink=False.

Q: completar y ejecutar qa/MATRIZ_BETATESTING_COBERTURA.csv (42 casos iniciales, no universo cerrado), capturas privadas reales con SHA, PID/ISO/PPSSPP/backend, PASS/FAIL/BLOCKED/NOT_RUN honestos, retest F1, segundo nivel, inventario/enciclopedia, batalla/TUIKA, guardar-cerrar-reabrir-cargar, finales y créditos; 0 P0/P1 para cierre. No fingir screenshots.

F6: solo cuando 0 sustituciones diferidas, 100% de textos y gráficos verificados y QA C completo, generar BPS final desde ISO original con roundtrip y SHA exactos, y EXE Windows x64 con pruebas E2E de interfaz, negativos y regresión. Revisar viabilidad legal de distribución diferencial. No fusionar PR #7 antes de los cierres.

## 6. Entrega obligatoria y siguiente prompt

Entregar tabla T/G/R/Q antes/después, numeradores/denominadores reales, áreas NO MEDIBLES cuando corresponda, fuente A/B/C, SHA de ISO original y artefactos nuevos, lista exacta de rutas y commits, PPSSPP y CI reales o NO EJECUTADOS, errores y rollback. Actualizar reports/ESTADO_CONTINUIDAD_PPSSPP.json, reports/COBERTURA_4_AREAS.json, qa/MATRIZ_BETATESTING_COBERTURA.csv y docs/ESTADO_CIERRE_4_AREAS.md conservando registros anteriores.

**Al concluir, REEMPLAZAR ÍNTEGRAMENTE prompts/SIGUIENTE_TAREA.md con otro prompt autónomo más específico R10, copiar la REGLA RECURSIVA 0, registrar HEAD/CI/PR efectivos, y mostrar el texto nuevo ENTERO al usuario.** Mantener T/G/R/Q abiertos hasta 100% realmente probado; si todo cierra, cambiar a informe final y mantenimiento.
