# CLADUN ES — RELEVO AUTÓNOMO F3: PRÓLOGO INGLÉS, ANIME000 Y 85 EVENTOS; F2 ABIERTA Y F4–F6

Actúa como ingeniero sénior de PSP MIPS, PPSSPP oficial 1.20.4, depuración WebSocket/GE/VRAM, ISO9660/PSPFS/DSARC, animaciones IMY y codec CP932 español. REALIZA pruebas auténticas, modifica código solo con causalidad y verificaciones, actualiza GitHub y entrega evidencias. No inventes imágenes, hashes, memoria, instrucciones, datos de juego ni pruebas que no hayas ejecutado. Diferencia evidencia (A) original real, (B) tests sintéticos/CI y (C) PPSSPP auténtico.

**OBLIGACIÓN RECURSIVA INNEGOCIABLE:** Al terminar REESCRIBE COMPLETAMENTE prompts/SIGUIENTE_TAREA.md con un OTRO PROMPT NUEVO completo, autónomo, actualizado con estado, archivos, hashes, comandos y pendientes; ese prompt vuelve a ordenar la MISMA REGENERACIÓN RECURSIVA hasta F2–F6 realmente completadas. Muéstralo íntegro al usuario y no prometas trabajo en segundo plano.

## 1. Repositorio y contratos

- Repo https://github.com/ARivas3008/loxalizacion-cladun-psp
- Rama integracion-eventos-segura-20261120. PR #7 https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7, base revision-manual-dialogos. Mantener ABIERTO, DRAFT, sin merge, sin force push.
- Último HEAD antes de añadir este relevo F3 A/B/A: 1fd924f0a5b06769b1a060f1778cd2f02621e628; la rama había incorporado cambios F2 adicionales y se conservarán al hacer commit. Es histórico, por lo que comprobar SHA ACTUAL, tree, PR y dos GitHub Actions de push y pull_request en HEAD FINAL, no los del anterior.
- Leer completos AGENTS.md, README.md, prompts/SIGUIENTE_TAREA.md, reports/ESTADO_CONTINUIDAD_PPSSPP.json, docs/F3_INTRO_INTENTO_PPSSPP_Y_ORIGEN_SCRIPTS_2026-11-23.md, docs/F3_PROLOGO_ANIME000_DEPENDENCIA_PPSSPP_REAL_2026-11-23.md, reports/RESULTADO_F3_PROLOGO_ANIME000_2026-11-23.json, tools/f3_auditar_intro.py, tools/f3_sonda_anime000_auditar.py y tests/test_f3_sonda_anime000_auditar.py.
- Conservar los trabajos F2 de 23/11: docs/F2_WS_REAL_F1_CONTROLES_GE_2026-11-23.md y docs/F2_PPSSPP_REAL_X11_AB_TUIKA_2026-11-23.md; tools/f2_ws_procedencia_ppsspp.py, tools/f2_ppsspp_ws_1204.py, tools/f2_ge_dump_1204.py, tools/f2_tuika_proteger_subregiones.py y reports respectivos. Leer docs/RESULTADO_F1_PPSSPP_2026-11-21.md, tools/script_event_guard.py, tools/integrar_parche_seguro.py, tools/charset_es.py y tests de integración.
- Prohibido publicar ISO, BPS, DATA.DAT, PSP EBOOT, animaciones, IMY, fuentes comerciales, PNG de juego, capturas de PPSSPP, RAM, GPU/GE/VRAM ni binarios de los juegos. Solamente código, tests sintéticos, métricas y hashes públicos; evidencia gráfica y sonda ISO, SOLO PRIVADAS, fuera de Git. No editar el corpus original ni la rama base.

Comprobar primero un checkout VERDADERO: git fetch origin; git switch integracion-eventos-segura-20261120; git pull --ff-only; git status --short; git rev-parse HEAD. Si la terminal carece de DNS github.com no fingir clone. El conector GitHub funciona: fetch ref/tree/PR, create_blob/create_tree/create_commit/update_ref con expected_sha y force:false.

## 2. PPSSPP real, versión y lanzamiento reproducible

ISO USA ORIGINAL exacta de usuario: 305496064 bytes; SHA256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f.
ISO F1 CANÓNICA histórica: 306456576 bytes; SHA256 496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986. BPS USA→F1 histórico daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd.
Emulador oficial PPSSPP 1.20.4 Linux x86_64 AppImage, 50689748 bytes, SHA256 661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21, descarga oficial https://github.com/hrydgard/ppsspp/releases/download/v1.20.4/PPSSPP-v1.20.4-anylinux-x86_64.AppImage.

En el relevo precedente se reextrajeron los dos binarios auténticos (ISO del 7z y AppImage oficial previamente transportado por Actions). En Xvfb 1280x720, PPSSPP SDL 960x544 se arrancó de verdad con Vulkan/llvmpipe software y produjo screenshots originales. En este contenedor Xvfb con GLX hizo fallar GL; el lanzamiento más reproducible usó Xvfb -extension GLX, una configuración realmente cargada de PPSSPP con GraphicsBackend = 3 (VULKAN), VK_ICD_FILENAMES y VK_DRIVER_FILES apuntando al lvp_icd.json PRIVADO de Mesa Debian13, SDL_AUDIODRIVER=dummy y shim de audio LD_PRELOAD EXTERNO permitido con SHARUN_ALLOW_LD_PRELOAD=1. No alterar AppImage oficial. Comprobar su hash y los logs: Booted /PRIVATE/USA.iso y el menú real; no asumir éxito por el SHA documental.

Comandos de referencia con rutas de archivo revalidadas:
    sha256sum /PRIVATE/Cladun_USA.iso /PRIVATE/PPSSPP-v1.20.4-anylinux-x86_64.AppImage
    Xvfb :88 -screen 0 1280x720x24 -ac -extension GLX +render -noreset &
    export DISPLAY=:88
    export SDL_AUDIODRIVER=dummy
    export SHARUN_ALLOW_LD_PRELOAD=1
    export VK_DRIVER_FILES=/PRIVATE/lvp_absolute.json
    export VK_ICD_FILENAMES=/PRIVATE/lvp_absolute.json
    # Comprobar la sección PPSSPP GraphicsBackend = 3 (VULKAN) del INI realmente cargado.
    # Lanzar solamente PPSSPP oficial autenticado, con los argumentos reales del entorno.

F2 recuperó además servidor WebSocket REAL puerto 24192 con SHARUN_ALLOW_LD_PRELOAD=1; `version`, `game.status`, `cpu.status` y `gpu.record.dump` llegaron a responder. F1 Opciones/Controles mostraba 756px interior, ~=764 exterior, etiquetas música/Sí/No y seis iconos; dump GE real de Controles 38.546 bytes, 398 registros/124 PRIM. NO confundir la existencia de GE con traza causal de la textura del prólogo.

### Actualización F2 simultánea que DEBE conservarse
Otro relevo de F2 llegó REALMENTE con ISO F1 española al primer mapa jugable de Cladun en PPSSPP oficial 1.20.4: se navegó por WebSocket desde título/Opciones/Controles hasta Comenzar, música Real y START SKIP, y se observó movimiento del personaje con HUD. Backend OpenGL/llvmpipe de aquella sesión, Xvfb :98, 960×544; NO confundir con nuestro Vulkan/llvmpipe en Xvfb :88. Fue autenticado el mismo PID con socket debugger y descriptor F1. Se generó GE PPSSPPGE real de 65.309 bytes SHA d2195fbedd6f430d2a3823db28c12f9f9a9bc789964adefead0bab19298f06b4, 989 registros, 301 PRIM, 43 TEXADDR0 y 40 CLUTADDR. Se reparó la aceptación de F1 de 306456576 bytes en f2_iso_proceso_ppsspp/f2_x11_ppsspp_procfs_capture/f2_ppsspp_ws_1204 y sus tests; el capturador X11 F1 autenticado ya pasó. Ver docs/F2_MAPA_JUGABLE_GE_X11_F1_2026-11-23.md y reports/RESULTADO_F2_MAPA_JUGABLE_F1_2026-11-23.json. TODAVÍA NO existe escena combat/habilidad con TUIKA A/B, ni 19 glifos multicontesto, ni prueba de textura prologo MIPS→GE→VRAM.

## 3. F3: dos orígenes/problemas diferentes

A. PRÓLOGO VISUAL ANTERIOR A LA NARRATIVA demo1001: PPSSPP oficial real muestra frases en inglés sobre fondo animado, tanto en USA como en F1 canónica histórica. Ejemplo observado: "Some say, because the treasures were there." La frase completa no apareció como ASCII literal en los 349 recursos PSPFS descomprimidos; un match de "some say" fue un falso positivo en DATABASE.DAT/MONSTER.DAT (biografía de monstruo). Su textura, codificación o animación todavía NO se identificó.

B. DIÁLOGOS NORMALES demo1001: ISO PSP_GAME/USRDIR/DATA.DAT → PSPFS 231 SCRIPT.SDT → SCRIPT.DAT/SCRIPT.TBL, scripts demo1001_00.dsf / demo1001_01.dsf. 7 bloques, 878 comandos, 98 opcodes de texto incluido uno vacío, 97 textos no vacíos (2728 bytes originales). Borrador traduccion/CLADUN_BORRADOR_ES.csv 9237 filas ya tiene español para los 97; codificados en CP932 A1–B3 ocupan 2859 bytes. 85 cambian longitud y están APLAZADOS por --event-safe-only, 11 longitud igual son candidatos, 1 no cambia. No declarar todo el inglés resuelto por integrar los 85.

## 4. Descubrimiento NUEVO de F3: dependencia de ANIME000 en arranque, NO prueba de letras

Inventario auténtico PSPFS 234 ANIME000.IDT (3.537.936 bytes; 231 ocurrencias IMY), 235 ANIME001.LDT (287.472 bytes; 24 ocurrencias IMY), 236 ANIME002.LDT (2.067.856 bytes; cero ocurrencias IMY literales). Los tipos IMY ANIME 0x00/0x02 no son automáticamente el formato SYSGRA 0xA4; decodificar con modelo correcto antes de repintar.

Prueba A/B/A auténtica en PPSSPP oficial:
- A ISO USA original intacta, SHA b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f: boot, título Start/Continue/Options, selección musical y prólogo INGLÉS reales; screenshot X11 SHA256 8dbd15865eb008d2036d59e7e3bab3d130c3dfd438732c1f455dc456b22812ab.
- B SONDA PRIVADA EN COPIA ORIGINAL SOLO PARA DIAGNÓSTICO: en descriptor PSPFS índice 234, offset absoluto ISO 113778009, letra I del nombre ANIME000.IDT 0x49→X 0x58, nuevo ANIME000.XDT. Se verificó EXACTAMENTE UN byte alterado en 305496064, payload ANIME intacto, sonda privada SHA256 576e9699395dd142b666ed3b9d121db5037c63302dc0c4eee862a04ccfcdbb36. PPSSPP REAL alcanzó Booted pero ANTES del título se detuvo con pantalla azul INVALID MEMORY ACCESS, PC PSP 0x08809498, dirección 0x00000015; PNG real privado SHA 87f9c2b4d451b41a4dc890daf031cb60cdd44d9a09ec9f8094f6244c8c78cd89.
- A control repetido: relanzar la ISO original devolvió menú jugable, screenshot real SHA256 893c975382aa89437d7e9b7691eab9cdc9c525d0a490ae1f6e884c6499a57ba5.

CONCLUSIÓN ESTRICTA: el nombre/referencia ANIME000.IDT es necesario en el arranque; cambiarlo deja el juego NO JUGABLE. **NO** demuestra que ANIME000 contenga las letras del prólogo, porque el fallo precede a esa escena. No volver a renombrar recursos para preparar una traducción. **Nunca** añadir la ISO sonda al repo ni distribuirla. La herramienta nueva tools/f3_sonda_anime000_auditar.py hace SOLO LECTURA: SHA de ambas ISO, control de PSPFS y diff de un byte; tests/test_f3_sonda_anime000_auditar.py contiene 14 tests sintéticos PASS. Resultado privado del auditor SHA 6709edd4dd80494054ffaef2e9121cfbd9b951fb9f1cf32b9b3ff2e7bf9693a7.

Comando de verificación privada, solo si la sonda de diagnóstico ya existe y nunca para un parche:
    python tools/f3_sonda_anime000_auditar.py --iso-original /PRIVATE/USA.iso --iso-sonda-privada /PRIVATE/ANIME000_UNBYTE_DIAG.iso --reporte-privado /PRIVATE/f3_guardia_nueva.json

## 5. Siguiente experimento PRIORITARIO de F3

1. Identificar en contexto REAL de prólogo qué recursos se cargan sin bloquear el inicio, mediante PPSSPP WebSocket oficial de la sesión o registro PSP I/O. Capturar GPU GE real durante frase y verificar TEXADDR/CLUT/PRIM, RAM y textura frente a ISO original; no atribuir PC a fuente por el nombre de archivo.
2. Si no hay traza, investigar los encabezados ANIME000.IDT/ANIME001.LDT y paletas con parsers fail-closed, exclusivamente en privado. Elegir una sonda CROMÁTICA ISOLADA y NO DESTRUCTIVA en una textura/CLUT concreta cuyos bytes puedan autenticar; comprobar íntegramente el resto de PSPFS, DSARC y comandos, probar que el juego sigue entrando al prólogo, y hacer A/B PIXEL SINCRONIZADO con CONTROL NEGATIVO. Un crash antes de escena no confirma la procedencia de ninguna letra.
3. Una vez identificado el origen del texto visual, reconstruir únicamente el área de las letras de esas frases en español sin invadir números, iconos o fondos; validar dimensiones 480x272 PSP y ventana 960x544, rendimiento, tildes, paletas e integridad. NO publicar la imagen comercial.
4. Por separado, modelar las referencias/saltos de SCRIPT.DAT e intérprete MIPS para los 85 cambios de longitud en 4 IDs demo1001. Crear pruebas independientes de punteros, saltos y orden de 51705 comandos y 1625 entradas antes de una ISO privada experimental. No quitar --event-safe-only ni declarar safe por preservar opcodes si se mueven offsets.
5. Reproducir la INTRO COMPLETA en PPSSPP auténtico USA/F1/candidato, con registros/capturas privadas reales, episodios, efectos, retratos y texto. No cerrar F3 antes de ello.

## 6. F2/F4–F6 e integridad

F2 ABIERTA: rastro funcional de TUIKA en combate/habilidades, 19 glifos áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō multicontexto, iconos controles/HUD/combat, GE/VRAM y regresión F1. F2 WS/GE X11 demostrados anteriormente deben preservarse. SYSTEM PRiSM ya tenía 1152 píxeles magenta tanto en USA como sonda, diferencia cero: no usarlo de evidencia TUIKA.
F3 ACTIVA: prólogo inglés visual de origen desconocido y 85 scripts demo1001 bloqueados.
F4: integrar con seguridad los 4524 textos SCRIPT.DAT aplazados. F5: QA integral juego/saves/enciclopedia/combate/HUD/retratos. F6: BPS final y EXE Windows aplicados y probados end-to-end sin distribuir ISO/assets.
Preservar 9237 registros, 9235 español/2 excepciones, 349 PSPFS, 46308 comandos no textuales, 2721 glifos originales +19 nuevos A1–B3 y white_new_ink=False por defecto. Las pruebas de runtime y las de integridad binaria son distintas. PR #7 DRAFT sin merge.

## 7. Pruebas, commit y RECURSIVIDAD FINAL

En checkout verdadero ejecutar:
    python -m unittest discover -s tests -v
    python -m unittest tests.test_f3_auditar_intro tests.test_f3_sonda_anime000_auditar -v
    python tools/verificar_integridad.py --raiz .
    python tools/verificar_borrador_es.py
    python tools/auditar_preinsercion_es.py --reporte /tmp/f3_preflight_nuevo.json
    python tools/reportar_integrabilidad_es.py --reporte /tmp/f3_integrabilidad_nuevo.json
    (cd patcher && go test ./...)
    git diff --check

En el relevo anterior se ejecutó suite LOCAL del snapshot público con nuevo test: 517 Python PASS, uno omitido, integridad/CSV y Go PASS; comprobar nuevamente CI de ambas Actions sobre el HEAD FINAL tras publicación en GitHub. No confundir CI con PPSSPP.

Al terminar: (1) pruebas y cambios auténticos, sin falsear; (2) documentación e informes públicos de métricas (jamás binarios comerciales), y reports/ESTADO_CONTINUIDAD_PPSSPP.json actualizado preservando hallazgos F2; (3) commit con expected_sha/force:false en rama sin merge del PR #7; (4) verificar exactamente dos validaciones principales CI push y PR SUCCESS sobre el mismo SHA final; (5) **REESCRIBIR COMPLETAMENTE prompts/SIGUIENTE_TAREA.md CON UN NUEVO PROMPT AUTÓNOMO E ÍNTEGRO QUE EXIJA DE NUEVO TODA ESTA MISMA OBLIGACIÓN RECURSIVA; MOSTRARLO ÍNTEGRO AL USUARIO.** Continuar hasta F2–F6 efectivamente completadas.