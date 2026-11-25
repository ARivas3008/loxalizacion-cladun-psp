# F2 — Réplica autenticada de sonda TUIKA y cotejo A/B (22/11/2026)

**F2 ABIERTA. Ninguna ejecución nueva PPSSPP.** En este relevo se ha reextraído la ISO real aportada por el usuario, construido una sonda privada de tres bytes y añadido un comparador estricto de capturas para futuras sesiones con PPSSPP. Los tests de imágenes son **sintéticos**: no confundirlos con gameplay.

## Experimento real de ISO (no emulador)

- ISO USA: 305496064 bytes, SHA256: b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f.
- Sonda privada TUIKA: 305496064 bytes, SHA256: b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa.
- Se recorrieron los **305496064 bytes** del original y de la sonda; únicamente difieren los offsets decimales **114744872–114744874**, RGB original (249,251,249) versus (255,0,255), alfa 255 inalterado.
- La tabla PSPFS de 349 elementos es idéntica; **348/348** miembros ajenos a SYSGRA intactos. SYSGRA posee 27 miembros DSARC, **26/26** vecinos de TUIKA idénticos y tabla DSARC inalterada.
- SHA del TUIKA original c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127; sonda efcf4f41f57c300476e8ce54a32dea01f242dda3fbf3fb9c4e0b582bad8f5252. Estos datos no prueban uso durante el juego.

## Nueva herramienta y pruebas

- Herramienta: tools/f2_cotejar_capturas_tuika.py; tests: tests/test_f2_cotejar_capturas_tuika.py.
- **21/21 tests locales PASS con PNG/manifiestos fabricados solo para probar software**. No han sido emitidos por PPSSPP.
- Para cada versión, exige dos imágenes PNG, hashes SHA256, dimensiones, escena/título/versión declarados, manifiesto WebSocket de PPSSPP 1.20.4 y los SHA auténticos de ambos archivos ISO en disco.
- Rechaza symlinks, rutas de repositorios Git, sobrescrituras, capturas manipuladas y escenas diferentes. Calcula diferencias por píxel y posibles nuevas regiones magenta. No incluye píxeles comerciales en el informe.
- **No puede atestiguar qué ISO cargó realmente PPSSPP, la alineación temporal ni la procedencia MIPS→RAM→GE→VRAM**. Un resultado con cero magentas NO descarta TUIKA. Un candidato positivo exige ROI y control negativo manual. Framebuffer PSP no certifica regresión F1 de ventana X11.

### Comandos para una sesión auténtica futura (solo directorios privados nuevos)

Captura de ISO original y después ISO sonda, usando el mismo estado de juego y etiqueta de escena:

    python tools/f2_ppsspp_ws_1204.py --scene TUIKA_HABILIDADES --salida-privada /PRIVATE/usa_frames --port 24192 --ge-dump
    python tools/f2_ppsspp_ws_1204.py --scene TUIKA_HABILIDADES --salida-privada /PRIVATE/sonda_frames --port 24192 --ge-dump
    python tools/f2_cotejar_capturas_tuika.py --manifest-usa /PRIVATE/usa_frames/manifest_PRIVATE.json --manifest-sonda /PRIVATE/sonda_frames/manifest_PRIVATE.json --iso-usa /PRIVATE/USA.iso --iso-sonda /PRIVATE/TUIKA_magenta.iso --reporte-privado /PRIVATE/ab_analisis_nuevo.json

**La sesión no se realizó**: PPSSPP oficial 1.20.4 no está disponible y la descarga falló. El SHA oficial del AppImage Linux x86_64 sí se verificó en metadata del release: 661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21. También falló git clone por DNS a github.com; la ISO F1 canónica no está montada aquí. No hay capturas PPSSPP nuevas ni dump GE; falta QA multicontesto de 19 glifos, F1 960×544, procedencia de iconos HUD/tutorial/combate y F3–F6.

No se cambió corpus de 9237 entradas, integrador, white_new_ink=False ni --event-safe-only; 4524 textos SCRIPT.DAT siguen aplazados y PR #7 permanece DRAFT. Estado en reports/RESULTADO_F2_COTEJO_CAPTURAS_AB_2026-11-22.json y reports/ESTADO_CONTINUIDAD_PPSSPP.json; nuevo relevo íntegro en prompts/SIGUIENTE_TAREA.md.
