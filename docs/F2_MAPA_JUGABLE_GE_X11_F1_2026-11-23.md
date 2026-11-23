# F2 — Del inicio al mapa jugable de F1, GE real y captura X11 autenticada (23/11/2026)

**F2 PERMANECE ABIERTA.** Este relevo continuó la ejecución auténtica de Cladun español F1 sobre **PPSSPP oficial 1.20.4** hasta el primer mapa jugable, mediante entrada PSP por WebSocket. **NO se llegó a demostrar TUIKA en combate, trampas ni habilidades; no existe comparación A/B USA/sonda de esas escenas**. Se corrigió una limitación instrumental que rechazaba F1 en el capturador X11 aun cuando su ISO era canónica. No se modificó ninguna ISO comercial, script ni atlas.

## Evidencia real, no sintética

- ISO original USA SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`, 305.496.064 bytes; sonda TUIKA magenta SHA-256 `b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa` (solo 3 bytes CLUT2 diferentes). Esos dos archivos **no** fueron ejecutados en las escenas nuevas de este relevo.
- ISO traducida F1 SHA-256 `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`, **306.456.576 bytes**; AppImage PPSSPP oficial v1.20.4 SHA-256 `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`, 50.689.748 bytes. Xvfb :98 1280×720, X11 960×544, **GraphicsBackend OpenGL sobre llvmpipe** (no confundirlo con `SoftwareRenderer=True`), socket WS TCP 24192. Binario PPSSPP intacto; shim privado Sharun/SDL audio externo ya documentado.
- Autenticación real F1 por `tools/f2_ws_procedencia_ppsspp.py`: mismo PID mantiene abierta la ISO F1 autenticada y posee el socket LISTEN del WebSocket, con PID/starttime estable. `version` responde PPSSPP v1.20.4, `game.status` NPUH10072 y `cpu.status` ejecutándose. Captura X11 con el mismo PID/ISO corregida.
- Recorrido observado: salir de **Controles** con **Fin**, regresar a Opciones y título, elegir **Comenzar**, confirmar música **Real**, dejar avanzar la introducción (contiene inglés), y cuando la escena con la «Cheery Girl» muestra **START SKIP**, pulsar START. Se llegó al **primer mapa jugable** con personaje, terreno, HUD y cámara que responde a los controles. Se observó desplazamiento real por mapa; NO se acreditó enemigo, efecto TUIKA ni combate completado.
- Experimento aislado `triangle` dentro del mapa con `input.buttons.send`, capturas secuenciales; **sin mensaje TUIKA demostrado en ese contexto**. No extrapolar a otros lugares.
- Capturas privadas X11 reales del intro/mapeo, conservadas fuera de GitHub.

## GE real en mapa de F1

Se ejecutó `gpu.record.dump` mientras CPU ejecutaba; dump auténtico `PPSSPPGE` de **65.309 bytes**, SHA-256 `d2195fbedd6f430d2a3823db28c12f9f9a9bc789964adefead0bab19298f06b4`. El parser `tools/f2_ge_dump_1204.py` (v6) informó **989 registros, 301 PRIM, 43 TEXADDR0 y 40 CLUTADDR**, además de 270 `TEXTURE0`, 342 `REGISTERS`, 301 `VERTICES`. Direcciones parciales **no autenticadas como TUIKA**. Ningún PC MIPS de iconos ni referencia de VRAM probada.

Con CPU detenida, las consultas reales `gpu.buffer.screenshot`, `gpu.buffer.renderColor` y `gpu.buffer.renderDepth` devolvieron las tres **`Could not download output`**. Se reanudó CPU. Este resultado es específico de la sesión OpenGL/llvmpipe; no prueba que esos métodos fallen en otros backends. Las imágenes entregadas son capturas de ventana **X11**, no framebuffer PSP obtenido del depurador.

## Bug del capturador: F1 rechazada sin fundamento

`tools/f2_x11_ppsspp_procfs_capture.py` y `tools/f2_iso_proceso_ppsspp.py` solo aprobaban `usa|sonda`, pese a disponer ya de F1 canónica y a que el testigo de WS admitía F1. Al intentar una captura X11 real con `--tipo f1`, CLI la rechazó; se añadió:

- F1 SHA-256 canónico y tamaño **306.456.576** en `f2_iso_proceso_ppsspp.validate_iso` manteniendo los SHA/longitudes de USA y sonda.
- Roles `f1` para los CLIs `f2_iso_proceso_ppsspp.py`, `f2_x11_ppsspp_procfs_capture.py`, `f2_ppsspp_ws_1204.py`.
- Rechazo explícito de rol desconocido antes de leer archivos.
- Nuevas pruebas sintéticas de tamaño F1 correcto/incorrecto, roles y captura integrada sin sobrescritura.
- Se corrigió un `NameError` detectado por el primer intento real del capturador y se repitió: **captura X11 F1 autenticada CORRECTA**, PID e inodo ISO coincidentes, sin declarar procedencia GE.

## QA y seguridad

La suite completa de código local tras los cambios pasó **499 pruebas Python**, una omitida, cero fallos. `verificar_integridad.py`, `verificar_borrador_es.py`, `auditar_preinsercion_es.py`, `reportar_integrabilidad_es.py` y `go test ./...` pasaron con alcance estático. Los originales del corpus tienen **9.237 entradas, 9.235 españolas y 2 excepciones**; **4.524** traducciones de script de longitud diferente siguen aplazadas por `--event-safe-only`.

**El paquete privado** `Cladun_F2_Continuacion_PPSSPP_Mapa_Ge_23-11-2026_PRIVADO.zip` se entrega fuera del checkout: incluye 5 PNG reales, dump GE, análisis GE, dos testigos y logs, **sin ISO, BPS ni archivos extraídos**.

### Siguiente bloqueo de mayor valor

Repetir el recorrido de inicio en **ISO USA y sonda** para alcanzar la **misma escena de trampas/combate/habilidades** (no solamente un mapa sin mensajes), establecer el estado sincronizado y realizar A/B del efecto CLUT2 magenta; registrar capturas X11 y GE real por escena, y solo atribuir textura después de evidencia. Investigar en paralelo `gpu.buffer.*` con un backend distinto como prueba separada. F2, 19 glifos multicontesto y F3–F6 continúan ABIERTOS. PR #7 debe seguir DRAFT. **No publicar archivos comerciales en GitHub ni eliminar `--event-safe-only`.**
