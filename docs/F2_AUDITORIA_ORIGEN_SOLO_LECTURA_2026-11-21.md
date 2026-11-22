# F2 — Auditoría independiente del origen de iconos (solo lectura), 21/11/2026

**Estado F2: ABIERTA.** Este relevo NO obtuvo una traza RAM→GE→VRAM, una captura nueva de PPSSPP, una ISO F1 canónica local ni una QA multicontesto nueva de los 19 glifos.

## Verificación nueva contra el archivo 7z del usuario

Se extrajo de manera auténtica el ISO USA original, sin alterarlo: 305.496.064 bytes, SHA-256 **b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f**. Importante: un hash copiado en una solicitud anterior tenía 62 dígitos y no era SHA-256 completo; este valor de 64 se midió de nuevo y coincide con los informes vigentes.

La herramienta añadida tools/f2_auditar_origen_iconos.py analiza SOLO LECTURA el PVD ISO9660, DATA.DAT, índices PSPFS y DSARC y preimagen IMY. Los resultados nuevos son: DATA.DAT en offset absoluto ISO 113.770.496 (191.697.408 bytes); 349 PSPFS; SYSGRA.ARC índice 225, offset 895.488 y longitud almacenada 93.696; 27 miembros DSARC; KITAJIMA_KARI.IMY índice 17, offset local 57.856, longitud 2.480; offset absoluto de ese IMY en ISO **114.723.840 / 0x06D68C00**, SHA-256 **0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190**.

Una simulación privada **en memoria**, sin escribir ISO ni parche, modificó exclusivamente las componentes RGB de las entradas de paleta 5 a 15, reproduciendo exactamente **27 bytes diferentes**. La cabecera, canales alfa y raster del miembro no se alteraron. Esto corrobora el control binario de la sonda previa. **NO equivale a demostrar la carga MIPS/GE ni el uso en HUD, tutorial, diálogo o combate.**

## Pruebas ejecutadas y límites

Se ejecutaron localmente siete tests unitarios de tablas PSPFS y DSARC sintéticas y validación de hashes, todos correctos; además se recorrió la ISO real original y se validó su SHA. No se crearon nuevas ISO diagnósticas, BPS ni PNG. Los tests originales de integración completa, Python y Go deben verificarse también en GitHub Actions sobre el nuevo HEAD; no se afirmará su ejecución local sin tener un checkout completo.

El entorno no dispone de la AppImage oficial PPSSPP 1.20.4 ni de la ISO privada F1. Por ello **no se realizó** la medición F1 de 756 interiores / ~764 exteriores a 960×544 ni el seguimiento del depurador WebSocket; las evidencias PPSSPP anteriores se preservan como HISTÓRICAS, no como pruebas de esta sesión. Tampoco se activó por defecto white_new_ink, que permanece optativa.

## Seguridad y continuación

No se modificaron recursos del juego, CSV/TXT canónicos, atlas, integrador, BPS, glifos o modos event-safe. Se mantienen como invariantes históricos los 51.705 comandos de SCRIPT.DAT, 46.308 no textuales, 1.625 inicios de script, cero offsets y 4.524 traducciones de script aplazadas. El PR #7 sigue borrador.

Pendiente F2: trazas verificables de descompresión RAM→GE→VRAM, controles positivos/negativos en otros contextos; QA con mediciones/capturas auténticas de los 19 caracteres; y regresión F1 bajo PPSSPP real 960×544 antes de decidir activar tinta blanca. F3 introducción, F4 scripts, F5 jugabilidad y F6 BPS/EXE integral continúan pendientes.

Datos: reports/RESULTADO_F2_AUDITORIA_ORIGEN_2026-11-21.json. Relevo obligatorio recursivo: prompts/SIGUIENTE_TAREA.md.
