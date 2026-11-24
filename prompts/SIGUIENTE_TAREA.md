# CLADUN ES — RELEVO AUTÓNOMO F4/F3-R16: LEER SCRIPT.DAT EN RAM AUTENTICADA, OBSERVAR DESPACHO MIPS Y PRESERVAR LOS CUATRO BLOQUEOS

**Corte local 23/11/2026 (UTC 24/11).** Repositorio https://github.com/ARivas3008/loxalizacion-cladun-psp. Rama `integracion-eventos-segura-20261120`, base `revision-manual-dialogos`, PR #7 OPEN/DRAFT SIN MERGE. HEAD inicial R15 `40ec6f9ee7e868840202aea797afad0d125c3057`. Commit código nuevo R15 `92e004461a293e07024175140f6a708303d8b0ab`; commit documental FINAL R15 es posterior: verificar SHA REAL mediante GitHub y sus workflows push/PR antes de atribuir éxito. Nunca force push ni merge prematuro.

Actúa como equipo sénior de PSP MIPS, PPSSPP oficial 1.20.4, ISO9660/PSPFS/DSARC, texturas IMY/CLUT, fuentes CP932 de un byte A1–B3, traducción española y QA. **Ejecuta las pruebas y correcciones REALES posibles en el mismo turno, no solo redactes un plan.** Clasifica rigurosamente evidencia **A** (ISO original autentificada offline), **B** (sintéticos/CI) y **C** (juego y memoria realmente observados en PPSSPP). Nunca inventes PCs, RAM, texturas, screenshots, hashes, triunfos CI, binarios o cierres.

## 0. REGLA RECURSIVA INNEGOCIABLE — DEBE COPIARSE COMPLETA EN EL SIGUIENTE RELEVO

**Si cualquiera de los cuatro apartados sigue por debajo del 100 % VERIFICADO, al terminar CADA relevo debes sustituir por completo prompts/SIGUIENTE_TAREA.md en la rama de trabajo mediante un NUEVO prompt autosuficiente y exigirle que haga lo mismo al acabar.** No copies sin actualizar el prompt anterior. Incluye HEAD real, PR y CI reales, estado de cuatro áreas, pruebas A/B/C, hashes reales, archivos concretos, comandos correctos, fallos, hipótesis, tareas no terminadas, próximos criterios de cierre y prohibiciones. Muéstralo íntegro al usuario. Continúa por relevos en nuevas sesiones **solo mientras** existan tareas pendientes; cuando estén **las cuatro al 100 % confirmado**, cambia el entregable a informe final, checklist de lanzamiento y prompt de mantenimiento pospublicación. No generes artificialmente otro relevo de desarrollo tras cierre completo. Si no tienes acceso a GitHub, entrega el archivo nuevo en el chat y marca la escritura remota como NO EJECUTADA.

Si PPSSPP no está disponible, realizar auditoría A y pruebas B sustantivas, describir el bloqueo reproducible y crear R17. La CI no sustituye C y no hay trabajo asíncrono.

## 1. ESTADO REAL Y RESULTADO NUEVO R15

| Área | Progreso cuantificable y bloqueo |
|---|---|
| T — traducción | **9.235/9.237** registros con borrador ES (99,98 % de escritura, **no** aprobación narrativa ni en juego). Dos originales truncados 008723/008724; glosario, 586 escenas/2.216 cajas, tildes/variables y rótulos/prólogo visibles pendientes. |
| G — edición gráfica | NO MEDIBLE global. 6 PNG SYS.DAT2 y 27 IMY SYSGRA investigados parcialmente. 2.721 glifos originales más 19 A1–B3; TUIKA_MES 4bpp/256x256 CLUT2 afecta 9.144 texeles, 3.506 protegidos. Falta prueba de combate, fuentes multicontesto y prólogo. |
| R — ROMhacking | **3.724/8.248** sustituciones históricas (45,15% de ese conjunto), **4.524 variables BLOQUEADAS**. 85 diálogos demo1001 de longitud variable BLOQUEADOS, 11 igual tamaño solo simulados, 1 sin cambio. No existe modelo completo de referencias MIPS ni candidato final BPS/EXE E2E. |
| Q — betatesting | **55 casos Q001–Q055 definidos**, NO universo total. Q054 localizador de RAM y Q055 dispatch MIPS nuevos NOT_RUN. Sin C nuevo R15; faltan mapas, batalla, TUIKA, guardar/cargar, enciclopedia, créditos/final y E2E Windows. |

**A AUTENTICADA:** archivo del usuario `Cladun_This_Is_An_RPG_USA_PSN_PSP-PLAYASiA.7z` extraído en carpeta PRIVADA. ISO USA original 305496064 bytes SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. DATA.DAT PSPFS 349; SCRIPT.DAT 633344 bytes SHA256 `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358` y SCRIPT.TBL SHA256 `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`; 1.625 scripts, 51.705 comandos, 46.308 no textuales. No suponer rutas privadas persistentes entre entornos. Original sin cambios.

**NUEVO R15 — NUEVE HUELLAS ÚNICAS DEL SCRIPT.DAT REAL.** Los offsets `7420, 218095, 218133, 223351, 223360, 223602, 223637, 227968, 228194` identifican nueve secuencias de 32 bytes, cada una aparece exactamente una vez dentro de SCRIPT.DAT original. Se preparó informe A privado SOLO DE HASHES con SHA256 de archivo de metadatos `5f86438b2ff6b670a663f41630394359f7458bb37b9341f78d564fb12e8a8554`. En `reports/F4_R15_HUELLAS_RAM_2026-11-23.json` se guardan los offsets y hashes, **NO los bytes del juego**.

**Nueva herramienta R15 `tools/f4_r15_localizador_ram.py`** y `tests/test_f4_r15_localizador_ram.py`: **33 tests B sintéticos PASS local**; total de **87 tests PASS del checkout parcial local R13/R14/R15, NO suite completa del repositorio**. El lector con WS oficial v1.20.4 usa evento `memory.read` (respuesta base64); exige ISO y AppImage SHA exacto, PID/starttime+FD ISO+socket, WS versión y game.status. Escanea rangos PSP explícitos `0x08000000..0x0C000000`, máx. 32MiB, lee en fragmentos 4–64KiB con solapamiento 31B. Para una base candidata exige **al menos 3 huellas** concordantes y comprueba todas + SHA256 de los **633344 bytes completos** si existe una imagen continua. **Esto únicamente demostraría presencia de la imagen de script en RAM, NO ejecución del intérprete, control de flujo ni semántica de 0x0A/0x0B/0x0C**. No usa escrituras RAM. Un resultado sin coincidencias no prueba que los scripts no estén: pueden estar cargados por fragmentos o transformados en memoria. `memory.read` puede pausar momentáneamente la CPU; limitar intervalos. Comprobar CI R15 HEAD FINAL REAL.

**AppImage OFICIAL v1.20.4:** se consultaron metadatos del release oficial `https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4` y se corroboraron nombre `PPSSPP-v1.20.4-anylinux-x86_64.AppImage`, longitud **50.689.748 bytes** y digest SHA256 `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`. **NO SE DESCARGÓ**: DNS github.com inoperante en la terminal, descarga alternativa falló y no hay AppImage instalado. C NO EJECUTADA: ninguna base RAM/PC, no fotos, no traces, no pruebas Q050/Q051/Q053/Q054/Q055.

## 2. ARCHIVOS A LEER Y COMANDOS REPRODUCIBLES

Leer íntegros antes de editar: `AGENTS.md`, `README.md`, `CHANGELOG.md`, `docs/REPRODUCIBILIDAD.md`, `docs/PROTOCOLO_REINSERCION_FAIL_CLOSED.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, `docs/INTEGRACION_EVENTOS_PROTEGIDOS_2026-11-20.md`, `docs/F4_R15_HUELLAS_RAM_2026-11-23.md`, `reports/F4_R15_HUELLAS_RAM_2026-11-23.json`, `tools/f4_r15_localizador_ram.py`, `tests/test_f4_r15_localizador_ram.py`, `tools/f4_r14_manifest_sondas.py`, `tools/f4_r14_ppsspp_preflight.py`, `tools/f4_r13_grafo_intro.py`, `tools/f4_r12_candidatos_especiales.py`, `tools/script_event_guard.py`, `tools/f3_referencias_riesgo.py`, `docs/F3_ANIME_IMY_ESTRUCTURAS_2026-11-23.md`, `docs/F2_TUIKA_SUBREGIONES_PROTEGIDAS_2026-11-23.md`, `qa/MATRIZ_BETATESTING_COBERTURA.csv`, `reports/COBERTURA_4_AREAS.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `docs/ESTADO_CIERRE_4_AREAS.md`, `prompts/SIGUIENTE_TAREA.md`.

En checkout real (si DNS falla, usar conector GitHub para lecturas/commits no forzados y verificar CI sin fingir ejecución local):
```bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
git rev-parse HEAD
git status --short
python -m unittest discover -s tests -v
python -m unittest discover -s tests -p 'test_f4_r15_localizador_ram.py' -v
python tools/qa_cobertura_4_areas.py
python tools/qa_cobertura_4_areas.py --require-closed  # debe FALLAR si alguna área abierta
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/cladun-preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/cladun-integrabilidad.json
(cd patcher && go test ./...)
git diff --check
```

Preparar huellas únicamente A con ISO original propia y reporte privado nuevo:
```bash
python tools/f4_r15_localizador_ram.py --modo preparar \
  --iso-original /PRIVADO/Cladun_USA_original.iso \
  --reporte-privado /PRIVADO/R16_HUELLAS_NUEVO.json
```

Con PPSSPP oficial realmente instalado, ISO/FD/WS autenticados y un rango RAM **inspeccionado previamente**, no inventar direcciones de datos:
```bash
python tools/f4_r15_localizador_ram.py --modo escanear \
  --iso-original /PRIVADO/Cladun_USA_original.iso \
  --appimage /PRIVADO/PPSSPP-v1.20.4-anylinux-x86_64.AppImage \
  --pid PID_REAL --port 24192 --ram-start INICIO_HEX --ram-end FIN_HEX \
  --reporte-privado /PRIVADO/R16_RAM_NUEVO.json
```

Cualquier resultado debe reportar base RAM, PID/starttime, ISO/PPSSPP hash exacto, número de huellas y SHA256 completo SI LO HAY, no publicar dumps ni inferir llamadas. Si ninguna base continua coincide, implementar búsqueda segmentada/por bloque en vez de declarar fallo del formato o cambiar offsets. La lectura WS no equivale a la ejecución de comandos.

## 3. P0 F4: DEL LOCALIZADOR AL INTÉRPRETE MIPS EJECUTADO

Prioridad inmediata: obtener el AppImage verificado oficial desde una vía de red legítima, validar digest/tamaño local y ejecutar ISO USA exacta. Autenticar la procedencia con `tools/f4_r14_ppsspp_preflight.py` y Q052; comprobar `version` / `game.status NPUH10072` pero recordar que respuesta `version` v1.20.4 NO incluye PID ni ruta, se requieren `/proc`, FD y socket.

Ejecutar Q054: ubicar realmente la imagen de SCRIPT.DAT (si está continua) con herramienta R15. Caso sin imagen continua: revisar qué bloques se cargan separadamente desde SCRIPT.SDT y buscar huellas por bloques sin falsear evidencias. Ejecutar Q053 y Q055: conseguir PC MIPS real del despachador que **lee** el comando desde una dirección PSP observada y determinar lookup, stack, retorno, cambios de bloque y valores especiales. No suponer que offset SCRIPT.DAT = PC o RAMaddr.

Contrastar las nueve sondas de R14:
`20/20→757?` u32 100100, `757/2→758?` u32 100200, `758/1→759?` 0x0C 100290, `758/415` 0x0C 100, `758/416→760?` 0x0A 100201, `759/23` 0x0C 100, `760/1→761?` 0x0C 100291, `760/336` 0x0C 100, `761/23` 0x0C 100. Bloques 757/758/760 no son saltos acreditados aún. Revisar también `0x0B` byte 100/101 y u32=3 (8), `0x0A` u32=0/1 y otras referencias indirectas.

**NO RELocalizar** 85 variables de demo1001 ni 4.524 globales antes de tener modelo completo probado y ensayo privado reversible A/B/A con parseo de 51.705 comandos y comparación exacta de 46.308 no-textos/349 PSPFS, sprites/tiles/retratos/fuentes intactos. Mantener `--event-safe-only`.

## 4. PRIORIDADES T/G/Q Y F6

T: terminar naturalidad/contexto/glosario para 9.237 filas, 586 escenas/2.216 cajas, acentos/variables y fuentes truncadas 008723/008724 sin inventar originales; sincronizar CSV/TXT/guiones y localizar texto de prólogo/gráficos fuera del corpus. No T=100 por filas escritas.

G: 19 glifos `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō` A1–B3 y 2.721 antiguos, `white_new_ink=False`; no alterar globalmente CLUT2/TUIKA_MES.IMY. Verificar en PPSSPP combate, HUD, Opciones, diálogos, distintas tintas; origen inglés de `Some say, because the treasures were there.` vía I/O→RAM→GE/VRAM/TEXADDR/CLUT/PRIM real, no solo ANIME000.

Q: definir denominador completo más allá de 55 casos, ejecutar save/load, intro, nivel segundo, batallas, HUD, retratos/tiles/audio, enciclopedia, finales/créditos, regresión F1. Mantener Q050–Q055 NOT_RUN hasta evidencia C y cero P0/P1.

F6: solo al cerrar T/G/R/Q 100% verificado, reconstruir BPS original→candidata y EXE Windows x64 GUI con SHA E2E, negativos y revisión legal, sin subir ISO, EBOOT, DATA.DAT, fuentes, texturas, gráficos, capturas, RAM/GE/VRAM o BPS con recursos comerciales. PR #7 DRAFT, no merge.

## 5. INFORMES, GITHUB Y RELEVO INFINITO HASTA CIERRE REAL

Actualizar históricamente `reports/COBERTURA_4_AREAS.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `qa/MATRIZ_BETATESTING_COBERTURA.csv`, `docs/ESTADO_CIERRE_4_AREAS.md`, reports/docs y tests. No eliminar estados anteriores. Entregar tabla de cuatro áreas con porcentajes verificables y NO MEDIBLE cuando falta denominador, diferencias antes/después, QA PASS/NOT_RUN, fuente A/B/C, SHA reales, pruebas e inconsistencias, HEAD final GitHub, PR y CI push/PR DEL SHA FINAL. No llamar 100% a la suite B.

**AL FINAL, SI UNA SOLA ÁREA SIGUE SIN 100% REAL VERIFICADO, REEMPLAZA COMPLETAMENTE `prompts/SIGUIENTE_TAREA.md` POR UN PROMPT AUTÓNOMO R17 CON LA MISMA REGLA RECURSIVA 0, EJECÚTALO EN GITHUB Y MUESTRA SU TEXTO ÍNTEGRO AL USUARIO.** Solo tras cierre real de T/G/R/Q, entregar informe de lanzamiento y prompt de mantenimiento.

