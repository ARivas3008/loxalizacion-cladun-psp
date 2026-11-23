# F2 — PPSSPP auténtico, X11→PID→ISO y control A/B de TUIKA (23/11/2026)

**F2 CONTINÚA ABIERTA.** Esta etapa sí ejecutó PPSSPP oficial 1.20.4 en Linux x86_64 con la ISO USA original y la sonda TUIKA, pero **no** accedió a la escena de habilidades ni obtuvo trazas por WebSocket, GE, RAM o VRAM. Las capturas X11 son reales; no confundirlas con framebuffer PSP aislado.

## A. Originales comerciales autenticados, fuera de Git

La ISO USA extraída del 7z del usuario ocupa **305.496.064 bytes** y su SHA256 es `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. Se reconstruyó la sonda TUIKA por código existente: ISO SHA256 `b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa`. **Solo tres bytes** cambiados (offsets 114744872–114744874), 348/348 PSPFS vecinos y 26/26 DSARC vecinos byte a byte iguales. Tablas intactas. Nunca subir ISO/IMY/FONT/BPS/dumps de juego al repositorio.

## B. Tests locales sintéticos/estáticos

El AppImage oficial PPSSPP v1.20.4 se extrajo de un ZIP previo del proyecto, y se midieron **50.689.748 bytes** y SHA256 `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`. La prueba Python `python -m unittest discover -s tests -q` pasó **482 tests, uno omitido** (incluidos 7 tests nuevos del testigo X11). `tools/verificar_integridad.py` y `tools/verificar_borrador_es.py` pasaron (9.237 registros, 9.235 español, 2 excepciones); preflight y reporte de integrabilidad pasaron con alcance estático. `go test ./...` pasó; `go test -tags cladun_embedded ./...` no pudo ejecutarse completo **porque el BPS privado está omitido por seguridad**, no por un bug confirmado. La build Windows x64 sin BPS pasó. Nada de ello certifica gameplay.

## C. Ejecución REAL de las dos ISO

PPSSPP oficial inalterado se lanzó bajo Xvfb **1280×720**, ventana SDL/X11 **960×544**, renderizador software. En este contenedor el lanzador reescribía `SDL_AUDIODRIVER=dummy` a `pulseaudio`; un **shim LD_PRELOAD PRIVADO** interceptó `getenv("SDL_AUDIODRIVER")` para devolver `dummy` y permitir ejecutar. Es una adaptación externa de audio, no modificación del PPSSPP oficial, y debe declararse al reproducir.

El título de X11 `NPUH10072 : CLADUN: This is an RPG!` tenía `_NET_WM_PID` igual al PID del emulador, y `/proc/<pid>/fd` reveló el mismo inodo ISO abierto antes y después de capturar. Se verificó PID/starttime, SHA original/sonda, nombre de ventana y tamaño real de captura. PIDs observados: USA 1574 y 2141, sonda 1948; son efímeros. Herramienta nueva `tools/f2_x11_ppsspp_procfs_capture.py` y test `tests/test_f2_x11_ppsspp_procfs_capture.py`. **La propiedad X11 procede del cliente y un fd abierto no prueba qué ISO se dibuja en GE**.

## Hallazgo central: falso positivo de magenta en SYSTEM PRiSM

En un fotograma del splash «SYSTEM PRiSM» se contaron **1.152 píxeles RGB(255,0,255)** de la sonda. Después se grabó el **MISMO splash** con la ISO original, y se comprobó:

- PNG USA real: SHA256 `c20b515ddee01cdfd1bd55de184c079fc1a50ad45df9512dc5d9bf2a15fa078f`.
- PNG de sonda real: **mismo SHA256 exacto**.
- Comparación pixel RGB 960×544: **CERO diferencias**.
- Ambos tienen **1.152 píxeles magenta exactos**.

Los triángulos de SYSTEM PRiSM ya eran magenta en el juego sin modificar; **NO constituyen evidencia de TUIKA_MES.IMY ni de que la sonda haya afectado al render**. Sin captura A/B sincronizada habríamos informado falsamente que la sonda surtió efecto. Las capturas, manifiestos privados y el comparativo se entregan al usuario fuera de Git.

## Alcance que NO se ha superado

Se intentaron `RemoteDebuggerOnStartup=True` y `--debugger=24192`, pero **no se detectó escucha TCP en 24192**; ninguna llamada real `version`, `game.status`, `cpu.status`, `gpu.buffer.screenshot`, `gpu.record.dump` ni `memory.read` funcionó. La prueba es X11, no WS/GE. El menú F1 no se volvió a comprobar en esta ejecución; solo existe su aprobación histórica. No se ha llegado a combate/habilidades, probado los 19 glifos en múltiples escenas, confirmado iconos por índice ni rastreado TUIKA desde MIPS a VRAM. Mantener F2 ABIERTA, `white_new_ink=False`, y diferenciar `FONT.ARC/FONT_00.IMY` de `SYSGRA.ARC/FONT.IMY`. F3–F6 y 4.524 scripts aplazados continúan pendientes. **No quitar `--event-safe-only` ni fusionar PR #7**.

## Comandos para siguiente sesión (rutas privadas nuevas, sin overwrite)

~~~bash
sha256sum /PRIVATE/USA.iso /PRIVATE/PPSSPP-v1.20.4-anylinux-x86_64.AppImage
python tools/f2_probe_tuika_palette_privado.py --iso-usa /PRIVATE/USA.iso --salida-iso-privada /PRIVATE/TUIKA_magenta.iso --reporte-privado /PRIVATE/probe.json
# PPSSPP real ya iniciado, su ventana X11 960x544, PID leído de /proc:
python tools/f2_x11_ppsspp_procfs_capture.py --display :95 --pid PID_REAL \
  --iso /PRIVATE/USA.iso --tipo usa --png-privado /PRIVATE/A.png \
  --manifiesto-privado /PRIVATE/A.json
# Repetir con otra instancia, PID, ISO y --tipo sonda.
# Solo cuando un servidor WebSocket REAL esté escuchando:
python tools/f2_ppsspp_ws_1204.py --scene TUIKA_HABILIDADES \
  --salida-privada /PRIVATE/WS_A --port 24192 \
  --pid-ppsspp PID_REAL --iso-en-proceso /PRIVATE/USA.iso --tipo-iso usa
python -m unittest discover -s tests -v
(cd patcher && go test ./...)
~~~

Relevo actualizado y obligación recursiva en `prompts/SIGUIENTE_TAREA.md`. **No declarar F2 finalizada hasta observar uso funcional de TUIKA en escena real y completar 19 glifos, símbolos y regresión F1.**
