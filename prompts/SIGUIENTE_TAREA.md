# CLADUN ES — RELEVO AUTÓNOMO F3-R3: PRÓLOGO IMY, 85 EVENTOS Y F2 TUIKA/GLIFOS; F4–F6 SIN CERRAR

**Fecha de corte: 2026-11-23.** Actúa como ingeniero sénior de PSP MIPS, PPSSPP 1.20.4 oficial, depurador WebSocket/GE/VRAM, ISO9660/PSPFS/DSARC, IMY y CP932 español. EJECUTA cambios y diagnósticos auténticos, no solo planes. Distingue A (ISO original y análisis real), B (tests sintéticos/CI) y C (PPSSPP genuino). Prohibido fabricar pruebas, imágenes, PCs, direcciones, hashes o estados de GitHub.

## 0. OBLIGACIÓN RECURSIVA INNEGOCIABLE

**AL FINAL REESCRIBE ÍNTEGRAMENTE `prompts/SIGUIENTE_TAREA.md` CON OTRO PROMPT NUEVO, AUTÓNOMO, ACTUALIZADO, QUE VUELVA A ORDENAR LA MISMA REGENERACIÓN RECURSIVA HASTA QUE F2–F6 ESTÉN REALMENTE COMPLETADAS. Muéstralo completo al usuario.** Aun con bloqueos, informa el estado verdadero, no prometas trabajo posterior en segundo plano.

## 1. Repositorio y sincronización, mantener trabajo paralelo

- Repo `https://github.com/ARivas3008/loxalizacion-cladun-psp`, rama `integracion-eventos-segura-20261120`; PR #7 `https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7`, base `revision-manual-dialogos`.
- Al iniciar F3-R2, HEAD real `46df9c92135821a74d8bcb9990212cd422aef67b` (histórico, NO asumir HEAD actual); contenía F2 paralelo con `tools/f2_ruta_ws_liberacion_segura.py` y el prompt F2. Comprobar refs/tree/PR **actuales**; no eliminar F2 al avanzar F3.
- Ejecutar `git fetch origin && git switch integracion-eventos-segura-20261120 && git pull --ff-only && git status --short && git rev-parse HEAD`. Si hay error de DNS GitHub, no fingir checkout: usar conector `fetch_file`, `create_blob/create_tree/create_commit/update_ref` con `expected_sha` y `force:false`.
- Leer íntegramente `AGENTS.md`, `README.md`, este prompt, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`; `docs/F3_ANIME_IMY_ESTRUCTURAS_2026-11-23.md`, `docs/F3_ANIME_TOPOLOGIA_2026-11-23.md`, `docs/F3_PROLOGO_ANIME000_DEPENDENCIA_PPSSPP_REAL_2026-11-23.md`, `docs/F3_INTRO_INTENTO_PPSSPP_Y_ORIGEN_SCRIPTS_2026-11-23.md`, los reportes y herramientas `tools/f3_anime_imy_estructuras.py`, `tools/f3_anime_topologia.py`, `tools/f3_auditar_intro.py`, `tools/f3_sonda_anime000_auditar.py`, todos los tests.
- También leer F2: `docs/F2_REVALIDACION_ISO_TUIKA_Y_RELEASE_WS_2026-11-23.md`, `docs/F2_MAPA_JUGABLE_GE_X11_F1_2026-11-23.md`, `docs/F2_WS_REAL_F1_CONTROLES_GE_2026-11-23.md`, `docs/F2_PPSSPP_REAL_X11_AB_TUIKA_2026-11-23.md`, `tools/f2_ruta_ws_liberacion_segura.py`, `tools/f2_ppsspp_ws_1204.py`, `tools/f2_ge_dump_1204.py`, `tools/f2_ws_procedencia_ppsspp.py`, `tools/f2_tuika_proteger_subregiones.py`. Para scripts: `tools/script_event_guard.py`, `tools/integrar_parche_seguro.py`, `tools/charset_es.py`.

## 2. Contrato original, ISO y PPSSPP — SOLO EN PRIVADO

- ISO USA usuario: **305496064 bytes**, SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f` (reextraída realmente del 7z usando libarchive en este relevo). ISO F1 canónica histórica: **306456576 bytes**, SHA256 `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`; BPS histórico SHA256 `daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd`.
- PPSSPP oficial Linux x86_64 1.20.4 AppImage: **50689748 bytes**, SHA256 `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`; URL `https://github.com/hrydgard/ppsspp/releases/download/v1.20.4/PPSSPP-v1.20.4-anylinux-x86_64.AppImage`. En F3-R2 no estuvo disponible: **NO** hubo nueva ejecución C ni imágenes auténticas PPSSPP. Sesiones históricas de otros relevos sí existen y deben preservarse.
- `PSP_GAME/USRDIR/DATA.DAT`: offset ISO **113770496**, PSPFS_V1 349. ANIME000.IDT índice 234, 3537936 bytes SHA `0e57353eb1d5f9688164b3453e57b0fd91ff77dee8e422844ba3fb0fef32eb37`; ANIME001.LDT 235, 287472 SHA `cb7f1354e38ced1a5b19f36c2b45d939e59094e33de901d4b43dc8d65faaa174`; ANIME002.LDT 236, 2067856 SHA `e1617dd4aea349f60953db9471e53c1524e9c3184b2566a4a732c3ecc756eec6`.
- Nunca publicar ISO, BPS, DATA.DAT, EBOOT, IMY, fuentes, gráficos comerciales, PNG/vídeos PPSSPP, GE/VRAM/RAM o dumps del juego. Solo código, pruebas sintéticas, métricas agregadas, documentación y hashes. Sondeos siempre privados; NO alterar corpus fuente ni rama base.

## 3. Hallazgos F3 de este relevo — evidencia A y B, NO C

- `tools/f3_anime_topologia.py` es auditor SOLO LECTURA de estructura de cabeceras IMY, intervalos consecutivos, rachas y repeticiones SHA de intervalos, anclado en ISO USA SHA exacto y 3 SHA de miembros. **14 tests sintéticos locales PASS** en `tests/test_f3_anime_topologia.py` y auditoría de ISO privada PASS. Informe `reports/RESULTADO_F3_ANIME_TOPOLOGIA_2026-11-23.json`, doc `docs/F3_ANIME_TOPOLOGIA_2026-11-23.md`. Informe privado SHA `5cb78034a1495497a874a4f502dd21eaa07b2ac5796c392e4ea7db1539fa04e6`.
- ANIME000: 231 cabeceras (136 tipo 00, 95 tipo 02), todas alineadas a 4; 31 rachas, transiciones 00→00=121, 00→02=15, 02→00=15, 02→02=79; racha mayor 00=101, 02=36; 17 intervalos de tipo 02 byte-idénticos adicionales. ANIME001: 24 tipo 00. ANIME002: 0 firmas IMY. Primera firma ANIME000 en offset 7568; intervalo hasta la siguiente 1211392 bytes. Estos son **intervalos de cabeceras literales**, NO frames certificados, ni texturas, ni paletas.
- Auditor previo `tools/f3_anime_imy_estructuras.py`: 160/160 tipo 00 compatibles con flujo IMY convencional; 95/95 tipo 02 incompatibles (55 lookbacks, 40 longitudes). No asumir códec delta ni recodificar 02 sin modelo.
- Sonda A/B/A previa renombró únicamente un byte PSPFS ANIME000.IDT→ANIME000.XDT, y provocó crash antes del título en PPSSPP real (PC 0x08809498, lectura 0x15); restaurar USA recuperó. **NO acredita letras del prólogo**, NO repetir ablación disruptiva. Frase inglesa observada 'Some say, because the treasures were there.' no se encontró completa en ASCII PSPFS; 'some say' en MONSTER.DAT es falso positivo.

## 4. Siguiente acción F3 PRIORIDAD 1: fuente REAL de las letras del prólogo

1. Revalidar PPSSPP 1.20.4 oficial+ISO USA exactos. Reproducir arranque→título→selección musical→prólogo en Xvfb 1280×720, ventana 960×544; backend REAL según logs/INI. Ejemplo histórico Vulkan/lvp Xvfb :88 con `-extension GLX`, `SDL_AUDIODRIVER=dummy`, `SHARUN_ALLOW_LD_PRELOAD=1`, `VK_ICD_FILENAMES`/`VK_DRIVER_FILES` JSON lvp privado; otros relevos usaron OpenGL/llvmpipe Xvfb :98. No confundir sesiones.
2. Vincular PID, socket WebSocket 24192, FD ISO, version, game.status y cpu.status del MISMO proceso, luego trazar PSP I/O, descompresión, direcciones RAM, GE `gpu.record.dump` TEXADDR/CLUT/PRIM y VRAM mientras la frase aparece. No atribuir una textura por nombre o firma IMY.
3. Si no hay correlación de runtime, investigar estructura de índice ANIME000 y semántica IMY 0x02 con guardas fail-closed y evidencia independiente. La repetición de 17 intervalos no prueba delta ni la imagen del prólogo.
4. Solo con textura y paleta demostradas, sonda cromática NO disruptiva y reversible en copia privada, guardia 349 PSPFS/DSARC/ISO9660, controles A/B sincronizados en misma escena. Traducir el texto gráfico únicamente dentro de su ROI validado (PSP 480×272 / X11 960×544) y comprobar letras, CLUT, tildes, fondos, iconos y rendimiento sin publicar capturas.

## 5. Siguiente acción F3 PRIORIDAD 2: 85 textos demo1001

- DATA.DAT → PSPFS 231 SCRIPT.SDT → SCRIPT.DAT/SCRIPT.TBL; 7 bloques demo1001_00/01, 878 comandos y 98 opcodes de texto, 97 no vacíos (2728 bytes ingleses). Los 97 tienen español (2859 bytes A1–B3): **85 cambian longitud y están BLOQUEADOS**, 11 tienen longitud compatible, 1 idéntico. Correlacionar con `tools/f3_auditar_intro.py` y CSV canónico. SCRIPT.DAT SHA `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`; SCRIPT.TBL SHA `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`.
- Estudiar intérprete MIPS y referencias internas/externas de salto, sin inferir que un entero numéricamente igual a un offset sea un salto. Construir modelo/test fail-closed para 51705 comandos, 46308 no textuales, 1625 scripts y todos los destinos antes de alterar longitud. **NO quitar `--event-safe-only`** ni publicar ISO experimental sin A/B PPSSPP completo.

### Actualización F2 paralela obligatoria: GE-only después de 79e80351

El commit histórico F2 `79e803510d2f2d5f08efe3d2b6cc7ff0810692db` añadió a `tools/f2_ppsspp_ws_1204.py` el modo **`--ge-dump --ge-only`**: exige dump GE, no solicita `gpu.buffer.*`, no declara framebuffer, no detiene CPU y guarda manifiesto privado sin PNG. Incorporó 3 pruebas sintéticas, doc `docs/F2_GE_ONLY_WEB_SOCKET_SIN_FRAMEBUFFER_2026-11-23.md`, reporte `reports/RESULTADO_F2_GE_ONLY_Y_ISO_2026-11-23.json`. La explicación de `Could not download output` a partir del código oficial de PPSSPP solo acredita fallo del proveedor del búfer, NO que OpenGL sea la causa. **Conservar estos cambios y el ensayo TUIKA A/B pendiente.**

Para escena A/B real con WS autenticado, tras alcanzar combate verdadero, usar GE-only con PID y sonda distintos, sin confundir el dump con screenshot: `python tools/f2_ppsspp_ws_1204.py --scene HABILIDAD_TUIKA_REAL --salida-privada /PRIVADO/GE_A --port 24192 --ge-dump --ge-only --pid-ppsspp PID --iso-en-proceso /PRIVADO/USA.iso --tipo-iso usa`. Hacer testigo X11 por separado; **no** alimentar al cotejador PNG framebuffer con manifiesto GE-only.

## 6. F2 y F4–F6 — preservación obligatoria

- F1 Opciones anterior cerrado en alcance limitado: 756 px interior/≈764 exterior, 'Sí/No' y seis iconos en Controles. F2 abierta: TUIKA en combate/habilidades sin A/B real, 19 glifos áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō multicontesto no probados, faltan iconos HUD y la cadena MIPS→RAM→GE→VRAM. GE de primer mapa F1 histórico: 65309 B, 989 registros, 301 PRIM, 43 TEXADDR0, 40 CLUTADDR, SHA `d2195fbedd6f430d2a3823db28c12f9f9a9bc789964adefead0bab19298f06b4`; NO prueba textura TUIKA. SYSTEM PRiSM magenta 1152 px en original y sonda (diferencia 0) es falso positivo. Conservar `tools/f2_ruta_ws_liberacion_segura.py` con botón release/ACK; su CI sintética no es gameplay.
- F4: 4524 textos SCRIPT.DAT de tamaño cambiante pendientes. F5: QA aventura, retratos, mapa, iconos, saves, segundo nivel, combate, enciclopedia y regresión F1. F6: BPS final y EXE Windows x64 aplicados end-to-end con recursos comerciales únicamente privados.
- Conservar 9237 entradas, 9235 español/2 excepciones, 349 PSPFS, 2721 glifos originales + 19 A1–B3, `white_new_ink=False`, `--event-safe-only`, corpus y base sin cambios. **F2–F6 abiertas, PR #7 DRAFT sin merge.**

## 7. Pruebas, GitHub y cierre recursivo

Ejecutar, cuando exista checkout REAL:

    python -m unittest discover -s tests -v
    python -m unittest discover -s tests -p 'test_f3_anime_topologia.py' -v
    python tools/verificar_integridad.py --raiz .
    python tools/verificar_borrador_es.py
    python tools/auditar_preinsercion_es.py --reporte /tmp/f3_preflight.json
    python tools/reportar_integrabilidad_es.py --reporte /tmp/f3_integrabilidad.json
    (cd patcher && go test ./...)
    git diff --check

Para auditoría privada: `python tools/f3_anime_topologia.py --iso-original /PRIVADO/USA.iso --reporte-privado /PRIVADO/f3_topologia_nuevo.json`. No llamar tests sintéticos gameplay. Actualiza documentación, reportes y `reports/ESTADO_CONTINUIDAD_PPSSPP.json` conservando F2/F3; verifica CI push y PR SUCCESS en MISMO HEAD final, y PR #7 OPEN/DRAFT. Si falla algún control, informa fallo sin inventar.

**OBLIGACIÓN RECURSIVA INNEGOCIABLE: REEMPLAZAR ÍNTEGRAMENTE ESTE PROMPT POR UN NUEVO RELEVO AUTÓNOMO A LA TERMINACIÓN, INCLUYENDO ESTADO, FICHEROS, HASHES, TESTS, COMANDOS, BLOQUEOS, GITHUB Y EL MISMO MANDATO DE REGENERACIÓN; MOSTRAR SU TEXTO COMPLETO AL USUARIO, AUNQUE F2–F6 SIGAN ABIERTAS.**
