# R19 — Investigación estática independiente (avance parcial)

**A (ISO auténtica, privada):** ANIME001.LDT contiene 24 IMY; tras cada flujo aparecen 60 o 62 bytes. Los 62 bytes empiezan por `00 00`, y los últimos 60 admiten una partición en 15 cuádruplas. Siete registros contienen datos no nulos (1010, 5999, 6400, 6410, 6950, 6960, 6980); 10 de 24 requieren alineación de 2 bytes. Muchas cuádruplas presentan cuarto byte `FF`, compatible con una **hipótesis** RGBA8888; sin lectura GE/VRAM, NO se confirma que sean paletas PSP. No repack.

**A (SCRIPT original, verificación privada independiente):** 64 sustituciones de igual longitud, 2007 bytes de payload, 1773 bytes distintos; SHA256 virtual `8b41c60d6e0def06672398dc4e195bcac5da98de7ba57a8ffe2995cde3f584cd`. 51705 comandos conservados, 46308 no textuales intactos y offsets sin cambios. Cinco corrupciones intencionadas detectadas por comparación independiente (opcode, ID, longitud de comando, longitud textual, terminador). Ningún cambio canónico, ISO reconstruida ni prueba C.

**B:** cinco tests sintéticos nuevos para la partición y alineación, PASS local. El nuevo analizador no requiere ni publica datos comerciales. **C:** no ejecutada; PPSSPP oficial ausente. **T/G/R/Q:** no cerradas.

**Reproducir:** `python -m unittest discover -s tests -p 'test_f3_ldt001_palette_r19.py' -v`. Para el miembro extraído legítimamente en privado: `python tools/f3_ldt001_palette_r19.py --member-private /PRIVADO/ANIME001.LDT` (no adjuntar el miembro ni sus bytes al repositorio). El reporte público `reports/R19_AUDITORIA_PARCIAL.json` contiene únicamente métricas.
