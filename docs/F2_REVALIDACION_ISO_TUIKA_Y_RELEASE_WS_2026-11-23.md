# F2 — ISO original/sonda autenticadas y control seguro WebSocket (23/11/2026)

Estado: F2 ABIERTA; PR #7 OPEN/DRAFT. En este relevo se revalidaron binariamente los originales del usuario y se implementó un controlador de entradas PPSSPP con liberación explícita. NO hubo nueva ejecución PPSSPP auténtica; no hay capturas, GE, RAM ni VRAM nuevos.

## A. ISO auténtica y comparación de copia experimental
Se extrajo mediante libarchive.so.13 la imagen ISO del 7z aportado por el usuario. Tiene 305.496.064 bytes y SHA256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f. La copia TUIKA CLUT2 cambió únicamente los offsets absolutos 114744872–114744874 de RGB F9 FB F9 a FF 00 FF, sin cambiar alfa 255. SHA256 resultante: b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa; coincide con la sonda histórica.

La tabla PSPFS de 349 entradas y 348 recursos vecinos fueron byte por byte iguales. La tabla DSARC de 27 miembros y 26 vecinos de TUIKA fueron idénticos. SHA del miembro TUIKA original c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127. Informe privado de metadatos SHA256 d048ab7901be937700a37b83a852b9b845367597dc4bc3c04f3ac9340be33443. No se versionaron ISO, BPS ni archivos de juego. Este aislamiento NO demuestra efecto gráfico de TUIKA en combate.

## B. Nueva prevención de botones retenidos
Nuevos tools/f2_ruta_ws_liberacion_segura.py y tests/test_f2_ruta_ws_liberacion_segura.py. La implementación oficial v1.20.4 de PPSSPP (Core/Debugger/WebSocket/InputSubscriber.cpp) confirma que input.buttons.send manipula estados persistentes y input.buttons.press responde tras el número de fotogramas. La nueva ruta JSON exige checkpoints manuales, nombres de 12 botones válidos (ltrigger/rtrigger), duraciones 1–120 fotogramas, autenticación de ISO/WS/PID por f2_ws_procedencia_ppsspp.correlate, CPU ejecutándose y confirmación visual. Tras cada pulsación envía input.buttons.send con todos los botones false y espera ACK. Si press agota el tiempo, envía liberación de emergencia y posterior liberación con ACK; si este falta, informa error y no certifica que la pulsación fue liberada. No genera ni simula capturas.

17 pruebas B sintéticas focalizadas se ejecutaron localmente y pasaron, con 0 fallos. Probaron ausencia de checkpoint, nombres y duraciones inválidos, fallo de press, fallo de release, CPU detenida y no atribución de gameplay. No se ha ejecutado en este relevo la suite integral del checkout: contrastar GitHub Actions al HEAD final.

Ejemplo de ruta guiada: docs/F2_RUTA_VISUAL_WS_EJEMPLO_2026-11-23.json. Su contenido NO prueba que el recorrido se haya realizado en USA o sonda.

## C. Emulación real: solo evidencia histórica, no nueva
La AppImage PPSSPP oficial v1.20.4 no está en el entorno de esta ejecución y la red terminal no resuelve GitHub; tampoco está disponible la ISO F1 canónica. Por tanto NO se han ejecutado ni USA ni sonda en combate o habilidades aquí, ni obtenido nuevos fotogramas X11, dumps GE o direcciones de CPU/VRAM. Los hallazgos anteriores subsisten: F1 llegó realmente al primer mapa con START SKIP, X11 960×544 y GE PPSSPPGE v6 de 65.309 bytes / 989 registros / 301 PRIM, SHA d2195fbedd6f430d2a3823db28c12f9f9a9bc789964adefead0bab19298f06b4; no demostró TUIKA. En SYSTEM PRiSM USA y sonda tenían 1.152 magenta naturales, con 0 diferencias: control negativo.

F1 Opciones conserva, según las capturas históricas, 756 px interiores y aproximadamente 764 exteriores. Los 19 glifos áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō siguen sin validación multicontesto. Mantener white_new_ink=False, proteger las bandas mixtas de TUIKA, 9.237 filas de corpus, 2.721 glifos originales y 4.524 traducciones de SCRIPT.DAT aplazadas bajo --event-safe-only. F3 inglesa/ANIME000 permanece independiente y sin procedencia de letras probada. F4–F6 abiertas.

## Experimento prioritario reproducible
Con dos ISOs exactas y AppImage oficial autenticado, arrancar PPSSPP limpio USA con WS 24192, verificar el mismo PID/socket LISTEN/FD ISO, título, selección Real y START SKIP de Cheery Girl solamente cuando sea visible; llegar a mapa y evento confirmado de trampas/habilidad/combate. Repetir sonda desde arranque limpio, sin savestate cruzado. Usar ruta JSON guiada para liberar botones. Capturar A/B en escena equiparable y comparar ROI/paleta; hacer gpu.record.dump con CPU ejecutándose, enlazar CLUT/TEXADDR/PRIM a la textura y a RAM/VRAM, sin inventar direcciones. Una diferencia magenta es candidata y requiere controles y evidencia causal. Investigar fallos gpu.buffer.screenshot/renderColor/renderDepth en backend distinto como cuestión separada.

Comandos orientativos (sustituir rutas y PID reales):

    sha256sum /PRIVATE/USA.iso /PRIVATE/TUIKA_SONDA.iso /PRIVATE/PPSSPP-v1.20.4-anylinux-x86_64.AppImage
    python tools/f2_ws_procedencia_ppsspp.py --pid PID --port 24192 --iso-privada /PRIVATE/USA.iso --tipo usa --informe-privado /PRIVATE/W_A.json
    python tools/f2_ruta_ws_liberacion_segura.py --ruta-json docs/F2_RUTA_VISUAL_WS_EJEMPLO_2026-11-23.json --pid PID --port 24192 --iso-privada /PRIVATE/USA.iso --tipo usa --informe-privado /PRIVATE/REC_A.json
    python -m unittest discover -s tests -v
    python tools/verificar_integridad.py --raiz .
    python tools/verificar_borrador_es.py
    python tools/auditar_preinsercion_es.py --reporte /tmp/preflight_f2.json
    python tools/reportar_integrabilidad_es.py --reporte /tmp/integrabilidad_f2.json
    (cd patcher && go test ./...)

Conservar PR #7 OPEN/DRAFT; no fusionar, no forzar rama, no subir material comercial. Generar nuevo prompt autónomo recursivo tras cada relevo.