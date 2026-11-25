# F2 — Revisión de procedencia GE y modo --ge-only sin framebuffer (23/11/2026)

**F2 ABIERTA.** No se realizó nueva ejecución PPSSPP oficial en esta sesión: el contenedor dispone de Xvfb/OpenGL pero no del AppImage oficial v1.20.4, y la terminal falla al resolver github.com. No crear capturas o dumps GE con etiquetas C.

## Evidencia A: ISO USA y sonda privadas realmente autenticadas en esta sesión

Se extrajo de nuevo el único ISO dentro del 7z adjunto, mediante libarchive.so.13 (sin alterar 7z/original). ISO USA 305.496.064 bytes SHA256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f. Se creó en carpeta privada una sonda independiente; SHA256 b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa. Diferencia completa de archivos exactamente en offsets absolutos ISO [114744872,114744873,114744874] de RGB [249,251,249] a [255,0,255], alfa intacto.

Se verificó independientemente sobre ambos archivos reales la misma tabla PSPFS_V1 con 349 recursos: 348 vecinos de SYSGRA.ARC idénticos; SYSGRA.ARC es PSPFS índice 225, offset relativo 895488, tamaño 93696 bytes, original SHA256 63d9443084a2aeab8c2a3f79aebdb130eaf6c5d2e86f8be51346d7458ab81854. Tabla DSARC FL de 27 miembros idéntica; 26 miembros vecinos idénticos. Miembro TUIKA_MES.IMY índice 24, offset 78848, tamaño 7912 bytes, original SHA256 c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127; sonda SHA256 efcf4f41f57c300476e8ce54a32dea01f242dda3fbf3fb9c4e0b582bad8f5252. Reporte privado JSON solo de metadatos F2_ISO_Y_TUIKA_AUDITORIA_REAL_NUEVA_20261123.json, SHA256 60c40acff0726b79e0be60d4b98a7fd6886194c97de90b36ece35eea0230836e. No subir ISO ni sonda al Git.

**Interpretación limitada:** este A/B es aislamiento BINARIO; no es comparación de pantalla en habilidades ni prueba de carga GPU. El falso positivo del splash SYSTEM PRiSM (1.152 magenta ya nativos, 0 diferencias A/B) sigue descartado.

## Causa acotada del fallo gpu.buffer.* mediante código oficial (no prueba de backend ejecutado)

Se leyó el archivo oficial de la etiqueta PPSSPP v1.20.4: https://github.com/hrydgard/ppsspp/blob/v1.20.4/Core/Debugger/WebSocket/GPUBufferSubscriber.cpp . En GenericStreamBuffer, primero se rechaza CPU/GPU que no esté en stepping con mensaje Neither CPU or GPU is stepping; más adelante, tras invocar la función concreta, si esta devuelve false se informa Could not download output. gpu.buffer.screenshot usa GPUStepping::GPU_GetOutputFramebuffer(buf); renderColor y renderDepth tienen sus funciones específicas. Por eso el mensaje histórico «Could not download output» documenta **fallo del recuperador del búfer**, no un problema de decodificación base64/PNG posterior ni prueba suficiente para atribuir causa a OpenGL o llvmpipe. Aún hay que diagnosticar GPUStepping backend realmente en PPSSPP ejecutado.

## B: cambio causal del capturador con pruebas sintéticas

La herramienta tools/f2_ppsspp_ws_1204.py antes guardaba el dump GE real y luego intentaba dos capturas gpu.buffer.screenshot. En el backend histórico, la lectura de framebuffer falló, impidiendo generar manifest_PRIVATE.json completo. Se añadió --ge-only, que requiere --ge-dump. Con CPU ejecutándose solicita gpu.record.dump real, valida prefijo PPSSPPGE, guarda el volcado en carpeta PRIVADA y escribe el manifiesto; **no solicita gpu.buffer.*, no pausa CPU, no afirma imágenes ni rastreo MIPS→VRAM**. El origen del registro se etiqueta «gpu.record.dump ... (GE-only; no framebuffer PNG)», screenshots=[], flags de identidad y sincronización false.

Se añadieron 3 pruebas sintéticas a tests/test_f2_ppsspp_ws_1204.py: GE-only emulado no llama a framebuffer/pausa, rechaza --ge-only sin --ge-dump, y rechaza GE si CPU ya está detenida sin escribir archivo. Estas pruebas no ejecutan PPSSPP. La suite completa y CI serán comprobadas contra el HEAD publicado.

**No confundir:** una grabación GE es un registro de comandos, no una traza MIPS→RAM→GE→VRAM ni una fotografía. El parser tools/f2_ge_dump_1204.py sigue siendo un análisis independiente que produce direcciones candidatas, no identidad de TUIKA.

## Comandos verificables para un nuevo runtime C

En checkout auténtico, con las ISOs privadas y AppImage PPSSPP oficial 1.20.4 por SHA:

    python tools/f2_ws_procedencia_ppsspp.py --pid PID_ACTUAL --port 24192 --iso-privada /PRIVATE/USA.iso --tipo usa --informe-privado /PRIVATE/USA_WS_PID.json

Solo en una escena REAL de habilidad o trampa CONFIRMADA visualmente y con CPU corriendo:

    python tools/f2_ppsspp_ws_1204.py --scene HABILIDAD_TUIKA_REAL --salida-privada /PRIVATE/GE_A_NUEVO --port 24192 --ge-dump --ge-only --pid-ppsspp PID_ACTUAL --iso-en-proceso /PRIVATE/USA.iso --tipo-iso usa

Repetir con sonda y --tipo-iso sonda, PID/rutas NUEVOS; después analizar los dos dumps con tools/f2_ge_dump_1204.py y capturar X11 por separado con tools/f2_x11_ppsspp_procfs_capture.py. No usar f2_cotejar_capturas_tuika.py con un manifiesto GE-only porque requiere dos PNG **del framebuffer PSP** y no acepta capturas X11. Para una comparación X11, auditar manualmente escena/fase y producir informe privado con ROI/sincronización demostrado.

Más QA en checkout:

    python -m unittest discover -s tests -v
    python tools/verificar_integridad.py --raiz .
    python tools/verificar_borrador_es.py
    python tools/auditar_preinsercion_es.py --reporte /tmp/preflight_F2_GE_only.json
    python tools/reportar_integrabilidad_es.py --reporte /tmp/integrabilidad_F2_GE_only.json
    (cd patcher && go test ./...)
    git diff --check

Se mantiene F2 sin prueba 19/19 glifos multicontesto, textos/iconos HUD y A/B TUIKA en combate. Conservar F1 Opciones 756px interiores/≈764 exteriores, white_new_ink=False, 9.237 registros, 4.524 textos SCRIPT.DAT aplazados por --event-safe-only, 349 PSPFS y 2.721 glifos originales. F3 ANIME000/prólogo inglés, F4, F5 y F6 abiertas; no tocar el corpus, no subir binarios comerciales. PR #7 OPEN/DRAFT; relevo recursivo en prompts/SIGUIENTE_TAREA.md.