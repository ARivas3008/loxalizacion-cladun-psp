# R21 — Prototipo de FONT.ARC extendido 19+44, en memoria

`tools/f4_r21_ligature_font_prototype.py` encadena el generador **existente** de 19 glifos (`font_es_narrow.py`) con una nueva inserción de 44 ligaduras B4–DF. Construye 2784 registros FONT.BIN, conserva los 2721 originales y los 19 españoles, compone 44 celdas 16×16 con los rásteres ASCII originales, recompone las seis páginas IMY y verifica el roundtrip de todas las celdas. Solo publica métricas y SHA de la hipotética fuente, **no** imágenes ni bytes comerciales. No escribe ISO, PSPFS, DSARC en disco, BPS ni ejecutable.

**Aún por validar en fuente auténtica con el comando** `python tools/f4_r21_ligature_font_prototype.py --iso-original /PRIVADO/Cladun.iso`. Si el FONT.ARC resultante supera los **496 bytes libres** del slot PSPFS original, nunca colocarlo allí: requeriría ruta de relocalización append-only probada, guardas completas y ejecución C. No confundir un éxito sintético o de IMY con legibilidad real en pantalla.

No habilitar ligaduras ni cambiar el codec canónico de F2 automáticamente. Mantener `--event-safe-only`, `white_new_ink=False` y 4524 variables oficialmente pendientes hasta que haya inserción efectiva y pruebas PPSSPP.
