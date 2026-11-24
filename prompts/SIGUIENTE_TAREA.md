# CLADUN ES — R17: desbloquear PPSSPP oficial y comprobar carga segmentada antes de modificar eventos

Repositorio https://github.com/ARivas3008/loxalizacion-cladun-psp, rama `integracion-eventos-segura-20261120`, PR #7 OPEN/DRAFT contra `revision-manual-dialogos`. HEAD al inicio R16: `fdc8cc3093da4a385815c2d7d61507dd2f00abed` (push 45300259865 y PR 45300268809 SUCCESS). Verificar HEAD final R16 y Actions de ese SHA antes de editar; no force push ni merge.

Actúa como ingeniero sénior PSP MIPS, PPSSPP v1.20.4, ISO9660/PSPFS/DSARC, IMY/CLUT, fuentes A1–B3, localización y QA. Ejecuta pruebas reales, no inventes evidencia A (ISO original), B (tests/CI) ni C (ejecución PPSSPP).

## 0. REGLA RECURSIVA INNEGOCIABLE
**Si cualquiera de los cuatro apartados sigue por debajo del 100 % VERIFICADO, al terminar CADA relevo debes sustituir por completo prompts/SIGUIENTE_TAREA.md en la rama de trabajo mediante un NUEVO prompt autosuficiente y exigirle que haga lo mismo al acabar.** No copies sin actualizar el prompt anterior. Incluye HEAD real, PR y CI reales, estado de cuatro áreas, pruebas A/B/C, hashes reales, archivos concretos, comandos correctos, fallos, hipótesis, tareas no terminadas, próximos criterios de cierre y prohibiciones. Muéstralo íntegro al usuario. Continúa por relevos en nuevas sesiones **solo mientras** existan tareas pendientes; cuando estén **las cuatro al 100 % confirmado**, cambia el entregable a informe final, checklist de lanzamiento y prompt de mantenimiento pospublicación. No generes artificialmente otro relevo de desarrollo tras cierre completo. Si no tienes acceso a GitHub, entrega el archivo nuevo en el chat y marca la escritura remota como NO EJECUTADA.

Si no se dispone del emulador, no repetir indefinidamente la misma auditoría. Identificar el requisito externo concreto y, en paralelo, realizar solo trabajo nuevo verificable de T/G/R/Q. Si no hay avance posible sin C, registrar el bloqueo y generar el relevo de desbloqueo R18, sin fingir ejecución.

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
python tools/f4_r14_ppsspp_preflight.py --iso-original /PRIVADO/Cladun_USA_original.iso --appimage /PRIVADO/PPSSPP-v1.20.4-anylinux-x86_64.AppImage --pid PID_REAL --port 24192 --reporte-privado /PRIVADO/R17_SESION_NUEVA.json
python tools/f4_r16_bloques_ram.py --modo preparar --iso-original /PRIVADO/Cladun_USA_original.iso --reporte-privado /PRIVADO/R17_BLOQUES_NUEVO.json
python tools/f4_r16_bloques_ram.py --modo escanear --iso-original /PRIVADO/Cladun_USA_original.iso --appimage /PRIVADO/PPSSPP-v1.20.4-anylinux-x86_64.AppImage --pid PID_REAL --port 24192 --ram-start INICIO_HEX --ram-end FIN_HEX --reporte-privado /PRIVADO/R17_RAM_BLOQUES_NUEVO.json
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

Si DNS impide checkout, usar conector GitHub sin force y distinguir tests locales parciales de CI. Actualizar los cuatro archivos de cobertura/continuidad/QA/documentación sin perder historia. Entregar antes/después T/G/R/Q, denominadores, evidencias, hashes, HEAD y CI push/PR reales. Reemplazar íntegramente prompts/SIGUIENTE_TAREA.md por R18 con regla 0 y mostrarlo al usuario. Solo al cerrar las cuatro áreas, entregar informe de lanzamiento y mantenimiento.
