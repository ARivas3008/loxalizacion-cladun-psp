# CLADUN ES — RELEVO F2 AUTÓNOMO: A/B REAL TUIKA EN COMBATE, 19 GLIFOS, GE/VRAM Y F3–F6

Actúa como ingeniero PSP MIPS/PPSSPP 1.20.4, depurador WebSocket, ISO9660/PSPFS/DSARC, IMY 4bpp/CLUT, fuentes CP932 y localización de Cladun. **EJECUTA diagnósticos y correcciones reales**, no te limites a un plan. Nunca inventes capturas, tramas GE, PCs MIPS, direcciones RAM/VRAM, hashes, resultados, acciones GitHub ni validaciones. Separa tres categorías: (A) ISO original auténtica; (B) tests sintéticos/CI; (C) ejecución genuina del juego.

**OBLIGACIÓN RECURSIVA INNEGOCIABLE:** al terminar ESTA tarea, sustituye COMPLETAMENTE `prompts/SIGUIENTE_TAREA.md` por OTRO PROMPT NUEVO, AUTÓNOMO E ÍNTEGRO, con el estado real, archivos, hashes, pruebas, bloqueos, comandos, GitHub y criterios siguientes. **MUESTRA EL NUEVO PROMPT COMPLETO AL USUARIO** y exige en su texto que el siguiente agente vuelva a generar otro prompt al terminar. Repite durante F2–F6, incluso si una fase queda bloqueada. No prometer trabajo diferido.

## 1. Identidad del proyecto y lectura obligatoria

Repositorio: https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama: `integracion-eventos-segura-20261120`; PR #7 https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7; base `revision-manual-dialogos`. **Mantener PR OPEN/DRAFT**, no fusionar, no forzar ref, ni alterar originales. Reconsultar HEAD y tree al iniciar; el HEAD anterior a este nuevo trabajo era `e66196ab1e83a39ed0fd1440a26625913e0ccf21`, pero deja de ser vigente tras el relevo actual.

Lee COMPLETOS, en este orden: `AGENTS.md`, `README.md`, `prompts/SIGUIENTE_TAREA.md`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `docs/F2_MAPA_JUGABLE_GE_X11_F1_2026-11-23.md`, `reports/RESULTADO_F2_MAPA_JUGABLE_F1_2026-11-23.json`, `docs/F2_WS_REAL_F1_CONTROLES_GE_2026-11-23.md`, `docs/F2_PPSSPP_REAL_X11_AB_TUIKA_2026-11-23.md`, `docs/F2_TUIKA_SUBREGIONES_PROTEGIDAS_2026-11-23.md`, `docs/F2_TUIKA_CATALOGO_ROTULOS_2026-11-22.md`, `docs/RESULTADO_F1_PPSSPP_2026-11-21.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md` y demás informes F2 que aparezcan en el estado JSON.

Herramientas: `tools/f2_iso_proceso_ppsspp.py`, `tools/f2_ws_procedencia_ppsspp.py`, `tools/f2_x11_ppsspp_procfs_capture.py`, `tools/f2_ppsspp_ws_1204.py`, `tools/f2_probe_tuika_palette_privado.py`, `tools/f2_cotejar_capturas_tuika.py`, `tools/f2_ge_dump_1204.py`, `tools/f2_ram_provenance_1204.py`, `tools/f2_qa_raster_19.py`, `tools/f2_tuika_proteger_subregiones.py`, `tools/f2_auditar_origen_iconos.py`, `tools/integrar_parche_seguro.py`, `tools/script_event_guard.py` y tests correspondientes. No asumir un checkout auténtico por la mera presencia de archivos copiados. Si `git fetch` falla por DNS, usar conector GitHub de forma segura con ref/expected_sha y `force:false`.

## 2. Evidencias verdaderas al cierre del 23/11/2026

- ISO **USA original** del 7z del usuario: **305.496.064 bytes**, SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.
- ISO sonda CLUT2 magenta TUIKA: SHA-256 `b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa`, solo **3 bytes** modificados y vecinos PSPFS/DSARC iguales. Todavía NO se validó su efecto en una escena de combate/habilidades. La pantalla **SYSTEM PRiSM** tiene 1.152 píxeles magenta NATIVOS en original y sonda, **cero diferencias** en A/B de ese splash; no usarla como evidencia TUIKA.
- ISO **española F1** canónica: **306.456.576 bytes**, SHA-256 `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`, conservando `--event-safe-only` y **4.524** traducciones de scripts aplazadas. No exigirle el tamaño de USA ni confundirla con la sonda.
- PPSSPP **oficial v1.20.4** Linux x86_64 AppImage: **50.689.748 bytes**, SHA-256 `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`. Entorno Xvfb **1280×720**, ventana X11 **960×544**, GraphicsBackend **OpenGL sobre llvmpipe**, `SoftwareRenderer=False`. En este contenedor, el lanzador Sharun requirió `SHARUN_ALLOW_LD_PRELOAD=1` para transmitir un shim de audio externo que sustituía `SDL_AUDIODRIVER` por `dummy`. **El binario oficial no fue modificado.**
- WebSocket ya funciona: `ws://127.0.0.1:24192/debugger`, subprotocolo `debugger.ppsspp.org`, `version` devuelve PPSSPP 1.20.4, `game.status` = NPUH10072 y `cpu.status` CPU ejecutándose. El proceso que atiende WS mantiene el mismo archivo ISO abierto mediante FD, correlacionado por socket LISTEN/inodo y PID/starttime; eso **NO demuestra qué textura llegó a la GPU**.
- Antes se verificó F1 en **Opciones**, cuadro 756px interior/≈764px exterior, tildes «música», «Sí» correctas, y **Controles** con iconos R/L/□/×/○/△; GE real de esa pantalla, 398 registros. Estos hechos no certifican los 19 glifos en todo el juego.
- **NUEVO AVANCE REAL:** se continuó desde F1 Controles→Opciones→Título→Comenzar→música Real. La introducción contiene frases inglesas. Cuando aparece «START SKIP» en el diálogo de la Cheery Girl, pulsar START permitió llegar a un **primer mapa jugable** con personaje, HUD, tiles y desplazamiento por controles WebSocket. Se capturó X11 960×544 auténtico; se observaron cambios de posición. El mapa no se ha reproducido aún en la ISO USA ni en la sonda TUIKA, y no se obtuvo una escena confirmada de combate/trampa/habilidad.
- **GE REAL en mapa F1:** `gpu.record.dump` de **65.309 bytes**, SHA-256 `d2195fbedd6f430d2a3823db28c12f9f9a9bc789964adefead0bab19298f06b4`, cabecera PPSSPPGE v6, 989 registros, 301 PRIM, 43 TEXADDR0, 40 CLUTADDR, 270 TEXTURE0. NO se identificó TUIKA ni se trazó MIPS→RAM→GE→VRAM.
- Las tres peticiones `gpu.buffer.screenshot`, `gpu.buffer.renderColor` y `gpu.buffer.renderDepth` devolvieron **«Could not download output»** con CPU detenida; CPU reanudada. Las capturas PNG proceden de la ventana X11, **NO** del framebuffer PSP por WS.
- Se corrigió un problema del instrumento F2: `f2_iso_proceso_ppsspp.py`, `f2_x11_ppsspp_procfs_capture.py` y `f2_ppsspp_ws_1204.py` ahora admiten rol **f1** solo con SHA-256 y tamaño específicos, sin debilitar usa/sonda. Pruebas sintéticas rechazan roles desconocidos, tamaños inválidos, archivos previos, y ejercitan captura F1. Se probó la captura X11 F1 auténtica con PID/ISO y funcionó.
- QA local: **499 tests Python, 1 omitido, 0 fallos**; verificadores de integridad/corpus, preflight e integrabilidad estáticos y Go estándar PASS. **CI push/PR hay que verificarlo sobre el HEAD final nuevo**, no atribuir al HEAD antiguo.
- Evidencias privadas de esta etapa (NO en Git): `Cladun_F2_Continuacion_PPSSPP_Mapa_Ge_23-11-2026_PRIVADO.zip`, SHA-256 `cf63f5d8da8b831e1882c7f7204ad16abaa0656e600b10d6a73534b0dfb26b47`. Contiene PNG reales, GE, testigos y logs, sin ISO ni BPS.

## 3. TAREA PRIORITARIA, NO SALTAR F2

**Objetivo:** encontrar y reproducir **la misma escena de combate/habilidades/trampas** en USA y sonda TUIKA, y vincular un cambio de color/GE a `SYSGRA.ARC/TUIKA_MES.IMY` sin falsos positivos.

1. Autentica PPSSPP y las dos ISOs privadas por SHA-256 y tamaño. No subirlas a Git.
2. Arranca **ISO USA** con PPSSPP 1.20.4, WS 24192 y X11, valida PID, starttime, inodo FD ISO y socket LISTEN con `tools/f2_ws_procedencia_ppsspp.py`; captura X11 testigo con `tools/f2_x11_ppsspp_procfs_capture.py`. **Los PIDs anteriores no sirven para la sesión nueva.**
3. Desde título, `Comenzar`→música Real, deja pasar intro; observa el indicador `START SKIP` cuando comienza el diálogo Cheery Girl, pulsa START. **Esta ruta se verificó en F1, todavía no en USA/sonda.** No asumir que el botón se puede activar en un instante no comprobado. Si hay pantallas adicionales, documentarlas.
4. Ya en primer mapa, identifica visualmente caminos/enemigos/trampas. Con controles `input.buttons.press` o `input.buttons.send` (asegurar RELEASE de cada botón; una captura anterior dejó momentáneamente LEFT activo al agotar el timeout) llega a un evento con texto de habilidades, trampas, recuperación de SP o ataque especial. Las 14 franjas del atlas TUIKA son mixtas y contienen zonas protegidas; no editarlas.
5. Reproduce con la **sonda** desde el mismo estado, sin intercambiar savestates que puedan traer texturas/ram de otra ISO sin validarlo. Mejor secuencia de entradas replicable o guardado original/carga comprobada. Captura A y B en misma posición y fase/ticks lo más sincronizados posible; comprueba por píxeles región, escenario y texto. El magenta natural del splash no es prueba.
6. Con CPU ejecutándose, graba `gpu.record.dump` real en cada pantalla de interés, coteja TEXADDR/CLUT/PRIM con RAM y el recurso IMY. No inventar direcciones MIPS, identidad de textura, CLUT aplicado ni transferencia VRAM. Si no hay GE visible, reconocerlo.
7. Investiga por separado por qué `gpu.buffer.screenshot/renderColor/renderDepth` fallan en OpenGL/llvmpipe, quizá probando otro backend oficialmente soportado. Registrar condiciones y errores; no presentar captura X11 como framebuffer PSP.
8. Audita los 19 glifos `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō` en diálogos, ayuda, HUD, tutorial, combate y menus; símbolos L/R/□/○/×/△, paletas blanca y amarilla, ancho/corte/interlineado. Distingue `FONT.ARC/FONT_00.IMY` (512×256) de `SYSGRA.ARC/FONT.IMY` (256×256). Mantener `white_new_ink=False` hasta QA real multicontesto.
9. Regresión F1 Opciones ancho≈764 px y tildes; mantener corpus inmutable, 349 PSPFS protegidas, 51.705 comandos, 46.308 no textuales y 1.625 scripts. **Nunca quitar `--event-safe-only` ni forzar offsets para insertar los 4.524 pendientes.**

## 4. Comandos (sustituir rutas privadas y PID por valores actuales)

~~~bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
git rev-parse HEAD
git status --short
sha256sum /PRIVATE/USA.iso /PRIVATE/TUIKA_sonda.iso /PRIVATE/F1.iso /PRIVATE/PPSSPP-v1.20.4-anylinux-x86_64.AppImage

# F1 ahora es rol permitido y tiene tamaño propio. En USA usar --tipo usa:
python tools/f2_ws_procedencia_ppsspp.py --pid PID_ACTUAL --port 24192 --iso-privada /PRIVATE/USA.iso --tipo usa --informe-privado /PRIVATE/WS_A_NUEVO.json
python tools/f2_x11_ppsspp_procfs_capture.py --display :98 --pid PID_ACTUAL --iso /PRIVATE/USA.iso --tipo usa --png-privado /PRIVATE/A_REAL_NUEVO.png --manifiesto-privado /PRIVATE/A_PROCFS_NUEVO.json

# SOLO en una ESCENA TUIKA observada realmente, no al inicio:
python tools/f2_ppsspp_ws_1204.py --scene TUIKA_HABILIDADES --salida-privada /PRIVATE/WS_A_NUEVO --port 24192 --ge-dump --pid-ppsspp PID_ACTUAL --iso-en-proceso /PRIVATE/USA.iso --tipo-iso usa
# Repetir ISO sonda con --tipo sonda en otra instancia/ruta; verificar ambos:
python tools/f2_cotejar_capturas_tuika.py --manifest-usa /PRIVATE/WS_A_NUEVO/manifest_PRIVATE.json --manifest-sonda /PRIVATE/WS_B_NUEVO/manifest_PRIVATE.json --iso-usa /PRIVATE/USA.iso --iso-sonda /PRIVATE/TUIKA_sonda.iso --reporte-privado /PRIVATE/AB_NUEVO.json

python tools/f2_ge_dump_1204.py --entrada-privada /PRIVATE/GE_REAL.dump --reporte-privado /PRIVATE/GE_ANALISIS_NUEVO.json
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/preflight_nuevo.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/integrabilidad_nuevo.json
(cd patcher && go test ./...)
git diff --check
~~~

`f2_ppsspp_ws_1204.py` aún puede bloquearse al leer framebuffer en este backend, incluso con `--ge-dump`: si falla, conservar los dumps GE por un capturador privado independiente y capturas X11 con testigos; documentar la limitación. La etiqueta de escena no demuestra su contenido.

## 5. F3–F6 solo después de resolver F2 con pruebas

F3: localizar y traducir la introducción inglesa con recurso/IDs comprobados, conservando scripts y gráficos. F4: modelar referencias/saltos del intérprete MIPS de SCRIPT.DAT y reubicar sin romper eventos las 4.524 traducciones pendientes; sin hacer cambios de offsets no autorizados. F5: QA completo de pisos, combate, ciudad, enciclopedia, HUD, inventario, retratos, mapas y guardado/carga, paletas/glifos/íconos. F6: BPS roundtrip y hashing, EXE privado Windows x64 realmente probado, release final solo con QA integral.

## 6. CIERRE OBLIGATORIO

Debes entregar causas y cambios auténticos, pruebas y límites, hashes, capturas/GE privados sin archivos comerciales en Git, nuevo informe `docs/`, JSON `reports/`, estado actualizado `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, commit GitHub sin force y PR #7 aún OPEN/DRAFT; verificar CI push y PR **SUCCESS sobre el MISMO HEAD final**, o declarar impedimento concreto. **REESCRIBIR ENTERO `prompts/SIGUIENTE_TAREA.md` Y MOSTRARLO ÍNTEGRO AL USUARIO**. El nuevo prompt debe contener la misma obligación recursiva. Si TUIKA y los 19 glifos siguen sin prueba multicontesto, mantener F2 abierta y diseñar el próximo experimento verificable, no saltar artificialmente a F3.
