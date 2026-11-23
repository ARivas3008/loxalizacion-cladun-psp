# CLADUN ES — RELEVO F2 AUTÓNOMO: A/B REAL TUIKA EN HABILIDADES, LIBERACIÓN WS, 19 GLIFOS; F3–F6 ABIERTAS

Actúa como ingeniero sénior de PSP MIPS/PPSSPP oficial 1.20.4, WebSocket, ISO9660/PSPFS/DSARC, IMY 4bpp/CLUT, GE/VRAM, fuentes CP932 A1–B3 y localización española. EJECUTA trabajo y pruebas auténticas, diagnostica y modifica código únicamente con causalidad y verificaciones. Nunca inventes capturas, hashes, instrucciones/PC MIPS, direcciones RAM/VRAM, tramas GE, resultados PPSSPP o acciones GitHub. Separa A (ISO auténtica e inspección binaria), B (tests sintéticos/CI) y C (ejecución genuina PPSSPP).

**OBLIGACIÓN RECURSIVA INNEGOCIABLE:** Al terminar ESTA tarea, sustituye COMPLETAMENTE prompts/SIGUIENTE_TAREA.md por un OTRO PROMPT NUEVO, AUTÓNOMO E ÍNTEGRO, actualizado con estado, archivos, hashes, pruebas, bloqueos, comandos, GitHub y criterios verificables; MUESTRA EL NUEVO PROMPT COMPLETO AL USUARIO. Este nuevo prompt exigirá que el siguiente agente repita la MISMA REGENERACIÓN RECURSIVA al concluir, durante F2–F6, incluso si una fase sigue bloqueada. No prometer trabajo futuro ni declarar fases terminadas sin evidencia.

## 1. Repositorio, ref y lecturas obligatorias

Repositorio: https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama: integracion-eventos-segura-20261120
PR #7: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7
Base: revision-manual-dialogos. Mantener OPEN/DRAFT, no fusionar, no forzar refs ni alterar los originales. HEAD antes del relevo que produjo este prompt: b8118782f29c3ae273767f2499da2b778b421858; es HISTÓRICO, comprobar el HEAD real al comenzar. Conservar el avance F3 simultáneo de ANIME000.

Leer COMPLETOS por este orden: AGENTS.md; README.md; prompts/SIGUIENTE_TAREA.md; reports/ESTADO_CONTINUIDAD_PPSSPP.json; docs/F2_REVALIDACION_ISO_TUIKA_Y_RELEASE_WS_2026-11-23.md; reports/RESULTADO_F2_REVALIDACION_ORIGINAL_Y_RELEASE_2026-11-23.json; docs/F2_MAPA_JUGABLE_GE_X11_F1_2026-11-23.md; reports/RESULTADO_F2_MAPA_JUGABLE_F1_2026-11-23.json; docs/F2_WS_REAL_F1_CONTROLES_GE_2026-11-23.md; docs/F2_PPSSPP_REAL_X11_AB_TUIKA_2026-11-23.md; docs/F2_TUIKA_SUBREGIONES_PROTEGIDAS_2026-11-23.md; docs/F2_TUIKA_CATALOGO_ROTULOS_2026-11-22.md; docs/RESULTADO_F1_PPSSPP_2026-11-21.md; docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md; docs/F3_INTRO_INTENTO_PPSSPP_Y_ORIGEN_SCRIPTS_2026-11-23.md; docs/F3_PROLOGO_ANIME000_DEPENDENCIA_PPSSPP_REAL_2026-11-23.md; reports/RESULTADO_F3_PROLOGO_ANIME000_2026-11-23.json; otros documentos referenciados por el estado JSON.

Herramientas: tools/f2_ruta_ws_liberacion_segura.py; tools/f2_ws_procedencia_ppsspp.py; tools/f2_x11_ppsspp_procfs_capture.py; tools/f2_ppsspp_ws_1204.py; tools/f2_iso_proceso_ppsspp.py; tools/f2_probe_tuika_palette_privado.py; tools/f2_cotejar_capturas_tuika.py; tools/f2_ge_dump_1204.py; tools/f2_ram_provenance_1204.py; tools/f2_qa_raster_19.py; tools/f2_tuika_proteger_subregiones.py; tools/f2_auditar_origen_iconos.py; tools/script_event_guard.py; tools/integrar_parche_seguro.py; tests correspondientes. Ruta visual TENTATIVA docs/F2_RUTA_VISUAL_WS_EJEMPLO_2026-11-23.json; sus checkpoints son instrucciones de operador, no gameplay acreditado.

Antes de cualquier modificación:
    git fetch origin
    git switch integracion-eventos-segura-20261120
    git pull --ff-only
    git rev-parse HEAD
    git status --short

No declarar checkout Git real por archivos copiados. Si git falla por DNS, usar conector GitHub con branch/tree actuales, create_blob/create_tree/create_commit/update_ref expected_sha y force:false. Revalidar rama antes de cada escritura para no perder commits paralelos.

## 2. Estado auténtico A/B/C al cierre del relevo anterior

A. ISO USA original extraída en sesión real desde el 7z aportado, mediante libarchive.so.13: 305.496.064 bytes, SHA256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f. Copia sonda TUIKA magenta: 305.496.064 bytes, SHA256 b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa. Solo tres bytes RGB en offsets absolutos 114744872–114744874, F9 FB F9 a FF 00 FF, sin alterar alfa. Tabla PSPFS 349 idéntica y 348/348 vecinos invariables; tabla DSARC de 27 idéntica y 26/26 miembros vecinos invariables. TUIKA original SHA c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127. Informe privado de SOLO METADATOS CLADUN_F2_2026-11-23_VALIDACION_A_PRIVADA.json SHA d048ab7901be937700a37b83a852b9b845367597dc4bc3c04f3ac9340be33443. Sondas/ISOs jamás en Git. Aislamiento binario no significa textura en combate.

B. Se creó tools/f2_ruta_ws_liberacion_segura.py y 17 tests focalizados sintéticos PASS en tests/test_f2_ruta_ws_liberacion_segura.py. La fuente oficial PPSSPP 1.20.4 InputSubscriber.cpp establece que input.buttons.send cambia estados que persisten, y input.buttons.press confirma después del número de fotogramas. La nueva herramienta autentica ISO/WS/PID/socket/FD/CPU, exige checkpoints visuales manuales, 12 botones oficiales y duration 1–120; después de cada pulsación envía RELEASE de todos los botones con ACK. En timeout envía liberación de emergencia y luego release ticketado, abortando si falta confirmación. No dibuja ni crea pruebas del juego. Los 17 tests son clientes simulados, NO PPSSPP ni suite integral; volver a ejecutar todos los tests y CI final.

C. ESTE relevo NO ejecutó PPSSPP oficial, por no tener AppImage oficial ni F1 canónica en el entorno y por fallo DNS en terminal. NO generó nuevos PNG X11/GE/WS ni direcciones MIPS, memoria o VRAM. Historias verificadas en sesiones PREVIAS, no atribuirlas a la actual:
- AppImage oficial Linux x86_64 PPSSPP 1.20.4: 50.689.748 bytes, SHA256 661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21. Xvfb 1280×720 y ventana X11 960×544, OpenGL/llvmpipe o Vulkan/lvp según sesión; Sharun requirió SHARUN_ALLOW_LD_PRELOAD=1 y shim externo de audio en ciertas sesiones, sin cambiar binario.
- ISO F1 española canónica: 306.456.576 bytes, SHA256 496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986. F1 Opciones comprobadas en PPSSPP real: 756 px interiores y aproximadamente 764 exteriores, música/Sí correctos e iconos R/L/□/×/○/△ visibles en Controles, pero NO 19 glifos multicontesto.
- WebSocket 24192 debugger.ppsspp.org real devolvió version v1.20.4, game.status NPUH10072 y cpu.status ejecutándose; mismo PID con socket LISTEN y FD de ISO, no prueba textura GPU.
- En F1 se alcanzó primer mapa real después de música Real, diálogo Cheery Girl y marcador START SKIP; se observó movimiento, HUD, tiles y personaje, SIN combate TUIKA acreditado.
- Dump PPSSPPGE real F1 mapa 65.309 bytes, SHA d2195fbedd6f430d2a3823db28c12f9f9a9bc789964adefead0bab19298f06b4, 989 registros, 301 PRIM, 43 TEXADDR0 y 40 CLUTADDR; NO hay identidad TUIKA MIPS→RAM→GE→VRAM.
- Las tres peticiones gpu.buffer.screenshot, gpu.buffer.renderColor y gpu.buffer.renderDepth devolvieron Could not download output con CPU detenida en OpenGL/llvmpipe; CPU fue reanudada. Las PNG fueron capturas X11, no framebuffer PSP WS.
- En splash SYSTEM PRiSM ambos USA y sonda mostraron 1.152 píxeles magenta NATURALES y cero diferencias A/B. Nunca usar splash como confirmación TUIKA.

## 3. PRIORIDAD F2: escena A/B TUIKA verdadera

1. Autentica tamaños/hashes USA, sonda y PPSSPP por SHA256; crea la sonda solo en carpeta PRIVADA externa con tools/f2_probe_tuika_palette_privado.py o revalídala. ISO original inmutable.
2. Arranca PPSSPP oficial con backend declarado realmente, X11 960×544 y WS 24192. Comprueba PID/starttime actual, FD inodo ISO, socket LISTEN del MISMO PID, version, game.status y CPU corriendo con tools/f2_ws_procedencia_ppsspp.py. PIDs viejos carecen de validez.
3. Inicia USA desde título, selecciona Comenzar, música Real, deja intro y SOLO cuando aparezca START SKIP en Cheery Girl pulsa START. Documenta pantallas adicionales. Sigue hasta una escena de habilidad, trampa, combate o recuperación SP que muestre de verdad los rótulos candidatos de TUIKA. El mapa primero sin combate no basta.
4. Usa tools/f2_ruta_ws_liberacion_segura.py con ruta guiada y checkpoints manuales para cada etapa. No asumas que el recorrido ejemplo ya ocurrió. Release de teclas tras cada press y en timeout, validar ACK; si release no confirma reinicia sesión, no contamines A/B con entradas persistentes.
5. Reproduce desde arranque limpio con sonda, sin intercambiar savestates con caché/VRAM/RAM sin verificación. Anota entradas reales, estados, posición, fase y ticks sin inventarlos. Captura X11 testigos y, si funciona, framebuffer PSP auténtico WS; etiqueta separadamente su origen.
6. Durante escenario de interés y CPU corriendo, gpu.record.dump en ambos; analiza TEXADDR/CLUT/PRIM/VRAM y relaciones con IMY original, PPSSPP memoria y PC MIPS demostrado. No equiparar dirección de GE candidata a identidad TUIKA hasta vinculación causal. El dump no prueba textura por sí solo.
7. Compara fotogramas A/B de misma escena y tiempo, ROI, texto y valores RGB. tools/f2_cotejar_capturas_tuika.py exige manifiestos WS con PNG válidas; NO pasarle testigos X11 como si fueran framebuffer WS. Alinear primero; incluso magenta novedoso es candidato hasta descartar diferencias temporales y encontrar causalidad.
8. Investiga por separado fallos de gpu.buffer.* con otro backend genuino si es posible; nunca fabricar framebuffer PSP a partir de captura X11 ni suponer que funciona.
9. Protege números, símbolos, letras japonesas y separadores transparentes en las 14 franjas/7 subregiones de TUIKA. No editar banda entera ni asignar el origen solo por el nombre del IMY.

F2-TUIKA se cierra únicamente tras A/B realmente sincronizado de un evento funcional y vínculo causal textura/CLUT GPU documentado. Si no hay escena, F2 ABIERTA.

## 4. F2 glifos y regresión F1

Revisa visualmente en PPSSPP REAL los 19 signos áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō en ayudas, diálogos, menús, HUD, tutoriales y combate con tinta blanca/amarilla, anchuras y cortes/interlineados. Distingue FONT.ARC/FONT_00.IMY 512×256 de SYSGRA.ARC/FONT.IMY 256×256. KITAJIMA_KARI.IMY ya fue causal para iconos de Controles en experimento anterior, pero no acredita HUD/combat. Mantén 2.721 glifos originales intactos y white_new_ink=False por defecto hasta QA en varias escenas. Repite regresión F1 Opciones 756/≈764.

## 5. F3–F6: preservar avance, no saltar F2

F3 ABIERTA: prólogo visual inglés aún sin fuente demostrada. La prueba A/B/A real previa que renombró únicamente ANIME000.IDT a ANIME000.XDT en una copia ISO falló antes de título con INVALID MEMORY ACCESS en PC 0x08809498 y dirección 0x00000015; volver a USA recuperó arranque. Eso demuestra dependencia de nombre/arranque, NO letras en ANIME000. Sonda diagnóstica SHA 576e9699395dd142b666ed3b9d121db5037c63302dc0c4eee862a04ccfcdbb36, jamás distribuir. demo1001_00/01 contiene 97 líneas traducidas en borrador, de las que 85 cambian longitud y siguen aplazadas. Identificar recurso del prólogo y flujo antes de tocar.
F4: modelar saltos y referencias del intérprete SCRIPT.DAT/MIPS antes de permitir los 4.524 textos script de longitudes distintas; preservar 51.705 comandos, 46.308 no textuales, 1.625 comienzos. No desactivar --event-safe-only ni forzar offsets. 
F5: QA integral de pisos, ciudad, combate, trampas, habilidades, HUD, inventario, enciclopedia, retratos, tiles, partidas guardadas/cargadas, audio y menú.
F6: BPS roundtrip y hashes, 349 PSPFS y recursos protegidos, EXE Windows x64 privado ejecutado de verdad, publicación solo tras QA integral.

Invariantes: corpus original 9.237 filas, 9.235 español/2 excepciones; 19 nuevos glifos CP932 un byte A1–B3 y 2.721 originales preservados; 349 PSPFS; white_new_ink=False; --experimental-parcial --event-safe-only; 4.524 scripts pospuestos. No subir ISO, BPS, DATA.DAT, EBOOT, FONT, IMY, dumps RAM/GE, fotos o PNG comerciales a GitHub.

## 6. Comandos y cierre obligatorio

    sha256sum /PRIVATE/USA.iso /PRIVATE/TUIKA_SONDA.iso /PRIVATE/PPSSPP-v1.20.4-anylinux-x86_64.AppImage
    python tools/f2_ws_procedencia_ppsspp.py --pid PID_ACTUAL --port 24192 --iso-privada /PRIVATE/USA.iso --tipo usa --informe-privado /PRIVATE/WS_A.json
    python tools/f2_ruta_ws_liberacion_segura.py --ruta-json docs/F2_RUTA_VISUAL_WS_EJEMPLO_2026-11-23.json --pid PID_ACTUAL --port 24192 --iso-privada /PRIVATE/USA.iso --tipo usa --informe-privado /PRIVATE/RUTA_A.json
    python tools/f2_x11_ppsspp_procfs_capture.py --display :98 --pid PID_ACTUAL --iso /PRIVATE/USA.iso --tipo usa --png-privado /PRIVATE/A_REAL.png --manifiesto-privado /PRIVATE/A_X11.json
    python tools/f2_ge_dump_1204.py --entrada-privada /PRIVATE/GE_REAL.dump --reporte-privado /PRIVATE/GE_ANALISIS.json
    python -m unittest discover -s tests -v
    python tools/verificar_integridad.py --raiz .
    python tools/verificar_borrador_es.py
    python tools/auditar_preinsercion_es.py --reporte /tmp/preflight_f2_nuevo.json
    python tools/reportar_integrabilidad_es.py --reporte /tmp/integrabilidad_f2_nuevo.json
    (cd patcher && go test ./...)
    git diff --check

Para sonda: repetir con --tipo sonda, PID y rutas nuevos. No ejecutar comandos de WS si puerto no escucha. Capturas reales y manifest privados fuera de checkout, sin sobrescribir. Clasifica explícitamente A/B/C. Generar nuevo informe docs/, JSON reports/ y actualizar reports/ESTADO_CONTINUIDAD_PPSSPP.json preservando F2/F3. Commit sin fuerza, verificar PR #7 OPEN/DRAFT y los dos CI push/pull_request SUCCESS sobre MISMO HEAD final; si CI no finalizó, informar pendiente, no atribuir éxitos de otra revisión.

**OBLIGACIÓN RECURSIVA INNEGOCIABLE — REITERADA:** REEMPLAZA POR COMPLETO prompts/SIGUIENTE_TAREA.md por otro prompt AUTÓNOMO NUEVO al terminar y MUESTRA ÍNTEGRO ese nuevo prompt al usuario. Debe reiterar la misma exigencia de regenerar el siguiente prompt hasta cerrar realmente F2–F6, aunque persistan bloqueos. No prometer trabajo diferido.
