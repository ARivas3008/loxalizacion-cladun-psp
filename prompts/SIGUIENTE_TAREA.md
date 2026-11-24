# CLADUN ES — R18 DE ALTA INTENSIDAD: DECODIFICACIÓN IMY, FUENTE TRUNCADA, REINSERCIÓN Y QA HASTA EL 100 %

Repositorio https://github.com/ARivas3008/loxalizacion-cladun-psp; rama integracion-eventos-segura-20261120, base revision-manual-dialogos, PR #7 OPEN/DRAFT. HEAD inicial R17 1f5e520eb4dced2e80339490d8134a5daa87576b; verificar HEAD final R17 real y CI al comenzar. CI R16 45301658951 y 45301667734 SUCCESS verificados. Sin force push, merge o sobrescritura concurrente. Actúa como equipo sénior traducción, gráficos, ingeniería PSP MIPS/PPSSPP 1.20.4, ROMhacking, QA, Python/Go.

## 0. REGLA PERMANENTE DE TRABAJO EXTENDIDO Y RECURSIVA

Objetivo equivalente a aproximadamente 20 minutos efectivos (15–25 cuando las capacidades permitan, sin esperar artificialmente ni garantizar tiempo). Realiza 3–6 bloques sustanciales y múltiples ciclos investigación→implementación→pruebas positivas/negativas→corrección→regresión. Trabaja en las cuatro áreas si viable. Distribución flexible: 2 min auditoría HEAD/CI/PR, 6 investigación, 5 implementación, 3 traducción y gráficos, 3 QA, 1 consolidación. Si falla un método, ensaya alternativa distinta; si PPSSPP bloqueado, pasa a otro frente. No finalizar por una sola herramienta, documento, prueba sintética o tarea pequeña; no repetir auditorías sin hipótesis nueva ni inflar porcentajes.

**Si cualquiera de las cuatro áreas no llega al 100 % VERIFICADO, al finalizar sustituye por completo prompts/SIGUIENTE_TAREA.md con R19 autosuficiente, que exija la misma obligación recursiva y regla extendida.** Incluir HEAD, CI real, métricas A/B/C, rutas, comandos, fallos, soluciones alternativas, pendientes y criterios objetivos. Si no puedes escribir remoto, entregar prompt completo y marcar NO EJECUTADO. Solo cuando todas las áreas estén cerradas, generar informe final, checklist lanzamiento y mantenimiento; no generar relevos artificiales. No inventar resultados.

## 1. Estado actualizado R17 y prioridades NUEVAS

**Nuevo frente traducción y reinserción:** 42 propuestas no canónicas en `traduccion/propuestas/DEMO1001_LONGITUD_FIJA_R17.csv`, compatibles en tamaño exacto, de 85 diferidas en demo1001. En RAM sobre SCRIPT.DAT auténtico: 51.705 comandos, 46.308 no textuales byte exactos, 1.028 bytes textuales modificados, cero desplazamientos; SHA virtual 5e367618ebdbe617e5bf4efd01be21f17d2f14ecd5c6e47275fe2f3727f82037. Total hipotético 53 compatibles, 43 diferidas, 1 idéntica. Global oficial sigue 4.524. Revisar las 42 en contexto y documentar decisiones, sincronizar corpus CSV/TXT y anclas F3 solo al aceptar, jamás promover automáticamente. Reproducir `python tools/f3_simular_intro_mismo_tamano.py --propuestas traduccion/propuestas/DEMO1001_LONGITUD_FIJA_R17.csv --iso-original /ruta/privada/Cladun.iso`; sin ISO es B. Extender revisión a otros bloques de texto según longitud y contexto; construir variante privada y comprobar C antes de cerrar. Primer commit R17 5ac988384c9c3811f511d62141874eda48994bf3, CI 45303203679 y 45303209991 SUCCESS; verificar CI del HEAD final R17 al empezar. 28 pruebas sintéticas locales acumuladas (16 IMY y 12 helper inicial); la integración final cuenta además con prueba del CSV real en CI.


Leer docs/R17_AVANCE_ESTATICO_2026-11-23.md, reports/R17_AVANCE_ESTATICO_2026-11-23.json, tools/f3_anime_imy_r17.py, tests/test_f3_anime_imy_r17.py, tools/f3_anime_imy_estructuras.py y los archivos de continuidad.

A: ISO autenticada, ANIME000 SHA256 0e57353eb1d5f9688164b3453e57b0fd91ff77dee8e422844ba3fb0fef32eb37. 192 registros u32 consecutivos, 231 flujos, unidad2 tipo00 136/136, unidad4 tipo02 95/95, límites y cola cero. 82/95 descartan literal2 por cola no nula; stride y stride/2 dan bytes distintos en 82, ambos válidos estructuralmente. No utilizar candidato para repack hasta corroborar imagen y CLUT, no afirmar frames o origen de letras. Probar contra textura real GE/VRAM en Q057 o localizar rutina de descompresión en entorno autorizado, analizar offsets de estructura IDT y LDT distintos. No asumir que ANIME001/002 tienen mismo framing. Reproducir:
python tools/f3_anime_imy_estructuras.py --iso-original /PRIVADO/USA.iso --reporte /PRIVADO/R18_anime_nuevo.json
python -m unittest discover -s tests -p 'test_f3_anime_imy_r17.py' -v

T: grupos 008723 y 008724, NO text_id. TIPATTR.DAT 11492 B SHA 305fd0e55ec860873645fb64a14814344e906d8b0f819275c9cae279d06434b7, 302 registros stride38, offsets 8148/8186, 15 B + NUL en campos 16. Truncamiento original confirmado, sin copia en DATABASE.DAT. No reconstruir por intuición, Q058 localizar visualidad y contexto, contrastar edición legítima si accesible. No repetir búsqueda idéntica. Revisar escenas enteras, corpus 9237/9235, 586 escenas/2216 cajas, glosario, concordancia, tildes, signos, ancho, variables, marcadores, saltos; preservar fuente, IDs y sincronizar CSV/TXT ES/TXT bilingüe/guion en mismo commit y registro de decisiones. Rutas: corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv, corpus/CLADUN_TODO_TEXTO_ORIGINAL.txt, traduccion/CLADUN_BORRADOR_ES.csv, traduccion/GLOSARIO_CANONICO.csv, qa/decisiones_auditoria.csv. Si conector devuelve contenido vacío en CSV grande, recuperar por fetch_blob; no sobreescribir ni editar parcialmente archivos derivados. Revisar que cambios al CSV actualicen anclas F3-R5/R6 con nueva evidencia original, nunca desactivar guardas.

R: todos 1625 bloques terminan 0x08; no hay texto como último comando. 14621 bytes padding final total, no habilita movimiento. Explorar redacción de longitud exactamente igual sin perder calidad, distinguir propuestas y aplicar solo tras auditoría/sincronización; no truncar ni rellenar arbitrariamente. Investigar referencias y modelo MIPS para 4524 variables. Mantener --event-safe-only. 3724/8248 cambios históricos (45,15% del conjunto), sin candidata nueva.

G: inventario gráfico completo no medible; revisar SYS.DAT2, SYSGRA.ARC, FONT.ARC/FONT.BIN, TUIKA_MES.IMY, KITAJIMA_KARI.IMY y ANIME. 6 PNG históricos, 27 IMY históricos; conservar 2721 glifos y 19 A1–B3, white_new_ink=False. No recolor global CLUT2, 3506 texeles identificados protegidos y máscaras F2 más restrictivas. No modificar retratos, sprites, tiles, mapas, controles ni otros recursos ajenos. Ver tools/font_es_patch.py, tools/font_es_guard.py, tools/graficos_texto_es.py, tools/charset_es.py.

B: 16 tests locales PASS, suite completa local no ejecutada. C: PPSSPP AppImage no presente y DNS error 6; NO nuevas capturas/PC/RAM/GE. Q: 58 casos definidos (Q057/Q058 NOT_RUN), universo no certificado, 0 nuevos PASS C. No confundir A/B con C. Los cuatro cierres false.

## 2. Contexto R16 vigente (histórico, no repetir sin necesidad) y procedimiento dinámico

## 1. Estado R16
- T: 9.235/9.237 registros con borrador (99,98% escrito, NO calidad final). Originales truncados 008723/008724, 586 escenas/2.216 cajas, glosario y texto gráfico pendientes de verificación contextual.
- G: denominador global desconocido. 6 PNG SYS.DAT2, 27 IMY SYSGRA, 2.721 glifos originales +19 A1–B3; TUIKA_MES.IMY CLUT2 9.144 texeles, 3.506 protegidos. Falta combate y tintas multicontesto.
- R: 3.724/8.248 sustituciones históricas (45,15% de ese conjunto), 4.524 variables bloqueadas; demo1001 85 variables, 11 igual longitud solo simuladas, 1 idéntica. No cierre MIPS ni BPS/EXE final.
- Q: 56 casos definidos, Q056 NOT_RUN, sin C nuevo. No es denominador completo; cero P0/P1 obligatorio antes de cierre.

ISO USA original 305496064 B SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`; DATA.DAT PSPFS 349; SCRIPT.DAT 633344 B SHA256 `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`; SCRIPT.TBL SHA256 `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`; 1.625 bloques, 51.705 comandos, 46.308 no textuales.

R16 A: ocho cuerpos sin padding en bloques 20,757–763, tamaños 340,34,5269,221,4355,238,332,415 B respectivamente. Cada cuerpo tiene dos huellas disjuntas de 16 B únicas en SCRIPT.DAT. Cuatro huellas R15 cruzan fin de comandos (7420,218095,223602,227968), una cruza slot (223602). B: 14 tests nuevos PASS, 101 tests del checkout parcial PASS, 8/8 cuerpos originales encontrados en RAM artificial inversa y separada. NO RAM real. Informe privado metadatos SHA256 `f6105a09bb2bec1e58518c594bc3a6db2f9a85c18d2013394f77196513201939`. Herramienta `tools/f4_r16_bloques_ram.py`, pruebas `tests/test_f4_r16_bloques_ram.py`, `docs/F4_R16_BLOQUES_RAM_2026-11-23.md`, `reports/F4_R16_BLOQUES_RAM_2026-11-23.json`. Núcleo probado con parser independiente, CLI con checkout completo pendiente de ejecutar contra ISO. C NO EJECUTADA: PPSSPP ausente, DNS github.com error 6.

## 2. Desbloqueo prioritario
Obtener AppImage desde https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4, archivo `PPSSPP-v1.20.4-anylinux-x86_64.AppImage`, 50.689.748 B, SHA256 `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`. Si el entorno no lo descarga, pedir que se adjunte PRIVADAMENTE, no subir a GitHub; alternativa ejecutar en Linux propio y aportar evidencias. Validar tamaño/hash y arranque. Autenticar ISO, PID/starttime, FD ISO, socket WS24192 del mismo PID, version/game.status NPUH10072 mediante preflight R14. version no devuelve PID/path.

```bash
python tools/f4_r14_ppsspp_preflight.py --iso-original /PRIVADO/Cladun_USA_original.iso --appimage /PRIVADO/PPSSPP-v1.20.4-anylinux-x86_64.AppImage --pid PID_REAL --port 24192 --reporte-privado /PRIVADO/R18_SESION_NUEVA.json
python tools/f4_r16_bloques_ram.py --modo preparar --iso-original /PRIVADO/Cladun_USA_original.iso --reporte-privado /PRIVADO/R18_BLOQUES_NUEVO.json
python tools/f4_r16_bloques_ram.py --modo escanear --iso-original /PRIVADO/Cladun_USA_original.iso --appimage /PRIVADO/PPSSPP-v1.20.4-anylinux-x86_64.AppImage --pid PID_REAL --port 24192 --ram-start INICIO_HEX --ram-end FIN_HEX --reporte-privado /PRIVADO/R18_RAM_BLOQUES_NUEVO.json
```

Rangos PSP comprobados previamente, no inventar direcciones. Q052/Q054/Q056: usar R15 para copia continua y R16 para carga por bloques; presencia de cuerpo exacto dos veces no demuestra dispatch. Si no hay resultados, investigar carga parcial/transformada. No publicar RAM ni bytes comerciales. No llamar resultados de fixtures evidencia C.

Q050/Q051/Q053/Q055: observar PC MIPS y lookup/retorno de nueve sondas R14 (offset SCRIPT.DAT, no RAM): 20/20=7420,757/2=218095,758/1=218133,758/415=223351,758/416=223360,759/23=223602,760/1=223637,760/336=227968,761/23=228194. Contrastar ID literal vs argumento−100: 20→757→758→760, 758→759,760→761. Significado de 0x0C argumento100, 0x0A valores0/1, 0x0B valor3 y quinto byte100/101 desconocidos. No inferir saltos; observar MIPS real y control A/B/A. No liberar 85 intro variables ni 4.524 globales hasta demostrar referencias completas y reparseo 51.705 comandos, no-textos intactos, recursos ajenos intactos. Mantener --event-safe-only.

## 3. Trabajo paralelo y cierre
T: revisar registros, glosario, escenas, tildes/variables y fuente de dos truncados sin inventar. Sincronizar CSV/TXT/guiones y conservar corpus original. G/F3: localizar frase inglesa del prólogo vía I/O→RAM→GE/VRAM real; no renombrar ANIME000 (crash previo), firmas IMY no prueban letras. F2: TUIKA en combate y 19 glifos áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō, preservar 2.721 originales, white_new_ink=False y no recolor global CLUT2. QA: juego completo, segundo nivel, guardar/cerrar/cargar, combate, enciclopedia, final/créditos, audio, sprites/tiles/retratos y regresión F1. F6: solo tras cierre T/G/R/Q real, BPS roundtrip y EXE Windows x64 GUI E2E con negativos, hashes y revisión legal; no subir ISO, EBOOT, DATA.DAT, texturas, FONT, screenshots, RAM/GE/VRAM ni BPS con assets comerciales.

## 4. Repositorio y validación
Leer AGENTS.md, README.md, CHANGELOG.md, docs/REPRODUCIBILIDAD.md, docs/PROTOCOLO_REINSERCION_FAIL_CLOSED.md, docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md, docs/INTEGRACION_EVENTOS_PROTEGIDOS_2026-11-20.md, docs/F4_R16_BLOQUES_RAM_2026-11-23.md, docs/F4_R15_HUELLAS_RAM_2026-11-23.md, docs/F4_R14_SONDAS_Y_PPSSPP_2026-11-23.md, tools/f4_r16_bloques_ram.py, tools/f4_r15_localizador_ram.py, tools/f4_r14_ppsspp_preflight.py, tools/f4_r14_manifest_sondas.py, tools/script_event_guard.py, tools/f3_referencias_riesgo.py, docs/F3_ANIME_IMY_ESTRUCTURAS_2026-11-23.md, docs/F2_TUIKA_SUBREGIONES_PROTEGIDAS_2026-11-23.md, reports/COBERTURA_4_AREAS.json, reports/ESTADO_CONTINUIDAD_PPSSPP.json, qa/MATRIZ_BETATESTING_COBERTURA.csv y docs/ESTADO_CIERRE_4_AREAS.md.

```bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
git rev-parse HEAD
git status --short
python -m unittest discover -s tests -v
python tools/qa_cobertura_4_areas.py
python tools/qa_cobertura_4_areas.py --require-closed # debe fallar hasta cierre
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/cladun-preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/cladun-integrabilidad.json
(cd patcher && go test ./...)
git diff --check
```

Si DNS impide checkout, usar conector GitHub sin force y distinguir tests locales parciales de CI. Actualizar los cuatro archivos de cobertura/continuidad/QA/documentación sin perder historia. Entregar antes/después T/G/R/Q, denominadores, evidencias, hashes, HEAD y CI push/PR reales. Reemplazar íntegramente prompts/SIGUIENTE_TAREA.md por R19 con regla 0 y mostrarlo al usuario. Solo al cerrar las cuatro áreas, entregar informe de lanzamiento y mantenimiento.


## Criterios de cierre profesional
T: inventario visible completo, todos los registros y escenas aprobados contextual y visualmente, textos gráficos contabilizados. G: inventario total, render y métricas de todos rótulos/glifos, sin daño a iconos y gráficos. R: 0 sustituciones diferidas, guardas por miembro PSPFS/DSARC y comandos, referencias demostradas, BPS/EXE comprobados E2E. Q: matriz completa, PASS C auténtico en todos los casos (identificador, candidata y hash, procedimiento, expectativa, observado, evidencia privada, severidad, corrección y retest), 0 P0/P1, partida de principio a fin. Probar menús, opciones, controles, prólogo, niveles, mapas, combates, jefes, HUD, inventario, equipo, clases, habilidades, enciclopedia, guardado/cierre/carga, finales, créditos, audio, integridad gráfica, parche BPS y EXE Windows. No distribuir recursos comerciales, imágenes, dumps o ISO; candidata privada solo después de guardas. Lanzamiento final incluye BPS diferencial, EXE x64, hashes, negativos, E2E, manual, documentación, historial, QA e integridad. 

Informe final de cada relevo: tabla T/G/R/Q antes/después, cambios reales, A/B/C separados, pruebas y resultados negativos, commit/PR/CI reales, bloqueos y soluciones, siguiente prompt. Ejecuta tanto trabajo sustancial como permita el turno, sin confundir duración objetivo con evidencia ni prometer trabajo futuro.
