# F2 — QA geométrica y capturas WebSocket PPSSPP 1.20.4 (21/11/2026)

Estado: F2 ABIERTA. No se afirma RAM→GE→VRAM, QA multicontesto ni regresión F1 ejecutadas en esta sesión.

Se autenticó y decodificó realmente la ISO USA original (305496064 bytes, SHA-256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f) y el atlas FONT.ARC de 2721 registros. Se regeneraron los 19 caracteres CP932 A1–B3 sobre las celdas base y se midieron por píxel 16x16: **100 texels de índice15**, coherentes con el ensayo amarillo→blanco previo. El detalle público está en reports/RESULTADOS_F2_QA_ESTATICA_WS_2026-11-21.json. Detalle privado más amplio, con hashes de raster: f2_metricas_19_glifos_original_20261121.json SHA256 88edb8a2cf1a920f1ff7480cbe4b06f44d5441a1183720b71a07b393a49bfb80.

Riesgos a validar en PPSSPP, NO errores confirmados: la **í** extiende su bbox horizontal de x2..3 a x2..4 (métrica cruda 0103); **ÁÉÍÓÚÑÜ** alcanzan y15 tras desplazar el cuerpo dos filas, con posibles problemas de recorte/interlineado no comprobados. Los signos ¿¡ preservan margen izquierdo x0 y las comillas ocupan x0..7. No deducir avance visual solo de los dos bytes de métrica FONT.BIN.

Se incorporaron herramientas y unit tests:
- tools/f2_qa_raster_19.py: recalcula las 19 geometrías de la ISO original autenticada, NO escribe imágenes ni ISO.
- tools/f2_ppsspp_ws_1204.py: cliente LOCAL WebSocket para obtener dos PNG auténticos y opcional dump GPU privado de una escena, con verificación de versión/título y salida exclusiva fuera de Git. Solo produce evidencia real si conecta a PPSSPP real.
- tests/test_f2_qa_raster_19.py y tests/test_f2_ppsspp_ws_1204.py: pruebas sintéticas. El entorno de trabajo local adicional ejecutó 24 unitarios sintéticos PASS.

Se leyó el código oficial de PPSSPP tag **v1.20.4**: WebSocket expone version, game.status, memory.read, memory.disasm, cpu.stepping, memory.breakpoint.*, gpu.buffer.screenshot/texture/clut, gpu.record.dump. No están en esa etiqueta los eventos gpu.displaylist.disasm ni cpu.breakpoint.hit de documentación reciente; no construir una traza sobre eventos inexistentes. El dump de GPU por sí mismo no establece PC MIPS ni cadena de transferencia.

Comando para futuro entorno REAL con PPSSPP oficial 1.20.4 iniciado y depurador habilitado:
python tools/f2_ppsspp_ws_1204.py --scene CONTROLES --salida-privada /tmp/CLADUN_F2_CONTROLES_REAL --port 24192 --ge-dump

Limites: esta sesión NO dispuso de la AppImage oficial PPSSPP 1.20.4 ni de la ISO privada F1 canónica, por lo que NO generó PNG, GPU dumps reales, ISO nuevas, BPS, PCs MIPS/GE, direcciones VRAM o medición F1 960x544. Las 24 pruebas sintéticas y CI no son evidencia funcional del videojuego.

Seguridad: solo código/tests/docs; ISO original, corpus, FONT.ARC canónica, white_new_ink=False, 349 PSPFS/4524 scripts protegidos quedan sin modificar. Los informes antiguos de 51705 comandos, 46308 no textuales, 1625 scripts y cero desplazamientos siguen siendo históricos, no una candidata recompilada en este relevo. F1 Opciones 756px interior/~764 exterior continúa como resultado anterior y debe repetirse bajo ventana 960x544 antes de activar el blanco.

Relevo recursivo: prompts/SIGUIENTE_TAREA.md. Mantener PR #7 DRAFT. F3 introducción, F4 4524 textos, F5 recorrido, F6 BPS/EXE pendientes.
