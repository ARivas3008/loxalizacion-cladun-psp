# Resultado F2 — atlas, MIPS real y dos sondas PPSSPP (21/11/2026)

**F2 ABIERTA.** Los datos de la fuente se preservan; se ha demostrado una ruta real código→índice de glifos de texto y, mediante controles positivos y negativos, que los seis iconos del menú Controles **no provienen de las celdas alteradas del atlas FONT.ARC** en ninguno de los dos experimentos. Falta encontrar el recurso gráfico y rutina real de los iconos; no está probado el render de todos los glifos A1–B3.

## 1. Auditoría binaria de las ISOs

Original USA SHA-256 `b73b263fce863e51a0e27d0d11d6bde2886e439a18e2bb186d497619a1b79f` (305.496.064 bytes), F1 canónica `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`. La auditoría independiente ejecutada `tools/auditar_atlas_f2.py` reconstruyó `FONT.BIN` y sus seis `FONT_00–05.IMY`: 2.721 glifos originales → 2.740 españoles, 19 nuevos de un byte `A1-B3` en el índice 95. **Los 2.721 originales preservan códigos, métricas y raster 16×16 exactos**, desplazados +19. FONT.ARC mantiene sus siete miembros.

Ejemplos código CP932/índice antiguo→nuevo: □ 81A0 166→185; ○ 819B 162→181; × 817E 143→162; △ 81A2 168→187. L ASCII índice44, R ASCII índice50 intactos.

## 2. Desensamblado REAL en RAM PSP, no EBOOT de disco

El EBOOT del ISO tiene formato `~PSP` cifrado; `BOOT.BIN` está vacío. Se usó PPSSPP 1.20.4 oficial SHA `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21` con Xvfb :67, resolución 1280×720 y software renderer. Depurador WebSocket `ws://127.0.0.1:24192/debugger` (solo interfaz local), subprotocolo `debugger.ppsspp.org`. Módulo **CLDN_TRIAL** cargado en `0x08804000`, tabla `FONT.BIN` en RAM `0x09075000`. Copia RAM descifrada retenida privada, nunca GitHub.

Punto de lectura sobre la letra C (`0x09075090`), **1867 lecturas**; registros □ (`0x090752E8`) y ○ (`0x090752D8`) **0 lecturas durante esa pantalla**. PC real `0x089089C8` ejecutó `lhu t2,0(t1)` y forma parte de una **búsqueda binaria** `0x089089A0..0x08908A18` de registros de cuatro bytes, comparando códigos y devolviendo índice. Resultado probado para texto C: **código→índice**. Contadores cero no prueban que no exista otra ruta ni identifican textura de botones.

## 3. Experimentos old/new: ambos en PPSSPP real

`tools/generar_probe_f2_indice.py` generó dos ISOs **privadas desde F1**, alterando solo siete celdas de `FONT.ARC`: C/L/R como control positivo y □○×△ en índices nuevos frente a antiguos. No se modifica `FONT.BIN`, CSV, TXT, eventos ni otras texturas. 349 PSPFS; **348 de 348 recursos ajenos al archivo FONT.ARC byte a byte exactos**, inventario ISO9660 intacto.

| Sondeo | SHA-256 ISO privada | SHA-256 BPS diagnóstico desde F1 |
|---|---|---|
| Posiciones NUEVAS | `77d101111409794e2db25cc4c0eb0707149078416759aa3dd4a3d68db1113b90` | `375750f62421e2f8fd5a40883479e19367e5632b07e9a97ed452e89b434737ac` |
| Posiciones ANTIGUAS | `48cf0228f6084bf3359db534651054960c3c94388bf4afa114b9af493630798d` | `cb29cc5299bf29dde2c311d435fc721b21264eb9aa463af336cde5e9ccefecda` |

**Ambos BPS fueron reaplicados y reconstruyeron la ISO correspondiente exactamente**. *Son BPS de diagnóstico con origen en ISO F1 canónica; NO parches sobre la ISO original USA y NO son para publicar.*

En PPSSPP real con screenshots scrot sin editar, los iconos R, □, ×, ○, △ y L mantuvieron sus píxeles en la misma región de Controles: **0 diferencias en cada ROI contra la pantalla F1**, tanto en OLD como NEW. El control C sí se renderizó como bloque, con **504 píxeles diferentes en «Correr»** y **536 en «Cambiar»**. Así se demuestra que la alteración del atlas funcionó y que **los iconos de Controles no se dibujan desde esas celdas**; aún se debe localizar la textura / rutina real y comprobar HUD, tutoriales, otros menús.

## 4. Regresión de F1 y evidencia privada

Opciones F1 se volvió a capturar real: fila y106 y RGB>125 en x160..1104 dan x342..1097, **756px interiores / ~764 exteriores**, sin tocar los rótulos Sí/No. `--event-safe-only` y 4.524 textos script aplazados se mantienen.

ZIP privado `Cladun_ES_F2_PPSSPP_Pruebas_Indices_2026-11-21_EVIDENCIAS_PRIVADAS.zip`: ocho PNG reales sin retoques, mapa de fuente y reportes ROI/SHA. SHA-256 `a4320955f84210776cd5857ed2174d2f81c437b3cf2ba712e92d4b6764b1c2b8`. **Nunca subir capturas ni recursos comerciales al repositorio.**

## 5. Código, tests, bloqueos y relevo

Commits de código F2 `202ff8d92513106f2e24a193c5032500bcc74c2d` incluyen `tools/auditar_atlas_f2.py`, `tools/generar_probe_f2_indice.py`, `tests/test_atlas_f2.py` con seis tests nuevos. GitHub Actions del commit: runs **44959226947** y **44959222272** SUCCESS, **146 Python tests**, corpus/borrador/integrabilidad PASS, Go PASS, Windows build sin payload PASS. Suite local del *snapshot parcial* dio un error por ausencia de archivo `referencias/la_pucelle/terminos_investigados.csv` no exportado; GitHub checkout completo sí pasó. No confundir tests CI con PPSSPP real.

**F2 ABIERTA**: pendiente localizar textura y función de dibujado de iconos, ensayar HUD/tutoriales/combate, y mostrar las 19 letras españolas A1–B3 incluidas ¿¡, ñ/Ñ, ü/Ü, áéíóú/ÁÉÍÓÚ, «» y ō en escenas auténticas, dos capturas por estado. La futura modificación debe preservar F1 y seguridad de eventos. F3 intro inglesa, F4 4524 scripts, F5 aventura, F6 BPS/EXE completos continúan sin terminar.

La siguiente tarea **debe regenerar de nuevo** `prompts/SIGUIENTE_TAREA.md` y `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, mostrar el prompt y mantener PR #7 draft.


## Continuación 21/11: textura de iconos de Controles y 19 glifos

La anterior descripción de «textura aún desconocida» quedó superada **solo para Controles**: la paleta de `SYSGRA.ARC/KITAJIMA_KARI.IMY` produce cambios controlados de 6 iconos en PPSSPP real, texto sin diferencias. Los 19 glifos españoles se mostraron en una ayuda y la tinta amarilla CLUT15 se corrigió optativamente a blanco CLUT1 con 100 texels y dos PNG reales, pero F2 sigue ABIERTA. Informe completo: [F2_ICONOS_TINTA_PPSSPP_2026-11-21.md](F2_ICONOS_TINTA_PPSSPP_2026-11-21.md). Estado y hashes: [RESULTADOS_F2_ICONOS_TINTA_PPSSPP_2026-11-21.json](../reports/RESULTADOS_F2_ICONOS_TINTA_PPSSPP_2026-11-21.json).
