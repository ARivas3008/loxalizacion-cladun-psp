# F2 — Textura de iconos y tinta de los 19 glifos, PPSSPP real (21/11/2026)

**F2 ABIERTA.** Se identificó causalmente el recurso de los seis iconos de Controles y se comprobó en dos capturas reales la corrección optativa de tinta blanca de los 19 caracteres españoles. **No está trazada toda la cadena MIPS/GE a VRAM ni se verificaron todos los contextos o anclajes**. No activar la corrección por defecto ni cerrar el PR #7.

## 1. F1 y entorno inalterados

ISO USA original SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`, ISO canónica F1 `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`, BPS experimental USA→F1 `daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd`. Ninguno se modificó.

PPSSPP oficial AppImage 1.20.4 SHA-256 `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`. Nuevas pruebas con Xvfb :78, **fullscreen 1280×720**, render software, captura cruda `scrot`. **No trasladar cifras de pantalla fullscreen a las medidas F1 de 756px interiores / ≈764 exteriores, obtenidas con ventana 960×544**.

## 2. Recurso exacto para los botones de Controles

Ruta `PSP_GAME/USRDIR/DATA.DAT → SYSGRA.ARC → KITAJIMA_KARI.IMY`.

PSPFS `SYSGRA.ARC` índice **225**, offset en DATA.DAT **895488**; DSARC `KITAJIMA_KARI.IMY` índice **17** entre 27, offset en ARC **57856**, longitud **2480 bytes** y SHA-256 original `0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190`.

Se decodificaron los 27 miembros de `SYSGRA.ARC` y se diseñó `tools/generar_probe_f2_iconos.py`. Comprueba hashes/preimágenes y copia la ISO F1 privada para modificar **únicamente 27 bytes RGB en la paleta IMY del miembro**, preservando alfa y textura. ISO de diagnóstico SHA-256 `b634fe468158a7ba5c3242896d4b1c43e711de53a19869c3b469a4877bc2e73d`. 349 PSPFS, **348 ajenos byte a byte idénticos**; 27 miembros DSARC, **26 ajenos idénticos**; índices y ISO9660 intactos.

En PPSSPP real se compararon 2 PNG originales y 2 del experimento: los símbolos R, □, ×, ○, △, L pasaron a **magenta**. Píxeles distintos en ROI respectivamente: **1136, 1360, 1353, 1353, 1337, 1143**. El texto y marco de Controles dieron **0** diferencias. Se demuestra que **Controles usa este recurso gráfico**, NO que HUD, tutoriales o combate usen lo mismo. La rutina exacta de carga y el PC MIPS/GE/VRAM **NO han sido identificados**.

BPS privado diagnóstico **con fuente ISO F1**, SHA `4b0a47d9ff2b33f364be45f508ab4510776c0bb6b4cc7245236699c5fbe25c61`, reconstrucción byte por byte exacta.

## 3. Defecto de tinta de los 19 caracteres

`tools/generar_probe_f2_glifos.py` genera un CSV privado de **9.237** filas con un único contenido experimental en ID `005694`: `F2 áéíóú ÁÉÍÓÚ ñÑüÜ ¿¡ «» ō`. Conserva presentación F1 mediante `005709/005713`, porque la opción `--borrador` evita automáticamente esos overlays. **No se modificó ninguna fuente CSV/TXT canónica**. CSV aislado SHA `800709d105a86e6da3252c44e4a2138fa8fec01e51afd0283e27913d272f1f7e`, ISO diagnóstica desde USA con `--experimental-parcial --event-safe-only` SHA `58f98b65185f39f172de0b5da97b9ce6fecb009e61b9462632f602485c99e4ca`, BPS desde USA SHA `a95039e13f9ace10d7b14f7a2587c0297c4889bf5f87a0263da289d6cc40f971`, roundtrip exacto. Los **4.524** textos script de longitud distinta siguen aplazados.

**Fallo visual auténtico:** los acentos, comillas y trazos nuevos salían AMARILLOS sobre letras BLANCAS. En `FONT_00.IMY`, paleta índice **15 = RGB(247,247,0)** amarillo e índice **1 = RGB(255,255,255)** blanco. El generador anterior dibujaba las adiciones con índice 15.

La nueva opción **`font_es_narrow.patched_archive_narrow(...,white_new_ink=True)`** cambia **100 texels 15→1 de los 19 nuevos glifos A1–B3** sin tocar los 2.721 originales ni `FONT.BIN`, y sin alterar los otros **348 PSPFS**. Se dejó **False por defecto** para proteger la ISO F1 canónica. `tools/generar_probe_f2_tinta.py` verifica la preimagen ISO diagnóstica y reproduce ISO con tinta blanca SHA `a42731988835bddb9dc81ef6d242b9c5029030256f210838881a1d48aed2de33`. BPS diferencial **fuente ISO amarilla, NO USA**, SHA `2a698e1efaa1c2333dbd86ac8c3a9fabbd369382c4b8c7d3ad0ab7c7f2ffac3f`, roundtrip exacto.

En la ayuda x40..700, y624..700, criterio amarillo R>180, G>170, B<80: **516 píxeles amarillos → 0**; pixeles claros/blancos 10.560 → 11.046. **Dos PNG reales antes y dos después**. El color quedó corregido en **una pantalla de diagnóstico**; no se aprobaron todas las formas, anclajes, solapamientos ni representaciones multicontesto de los 19 glifos.

## 4. Evidencia y tests

ZIP **privado fuera de GitHub**, nueve PNG auténticos crudos e informes JSON (sin ISO ni BPS): `Cladun_ES_F2_Iconos_Tinta_19Glifos_PPSSPP_2026-11-21_EVIDENCIAS_PRIVADAS.zip` SHA `af93e1d702d1d53d10d9fcfb326030c1a62cfb7c4ea4482846d7f26a83c49cad`, **1.260.036 bytes**. Todos los hashes de PNG en `reports/RESULTADOS_F2_ICONOS_TINTA_PPSSPP_2026-11-21.json` y manifiesto privado. **NO subir ZIP, imágenes, ISO, BPS, imágenes de FONT, EBOOT ni RAM a GitHub.**

Se añadieron `tools/generar_probe_f2_iconos.py`, `tools/generar_probe_f2_glifos.py`, `tools/generar_probe_f2_tinta.py`, opt-in de `font_es_narrow.py`, y pruebas `tests/test_probe_iconos_f2.py`, `tests/test_probe_glifos_f2.py`, `tests/test_tinta_es_f2.py`. **152 tests Python locales PASS** (1 omitido), corpus/borrador/preinserción/integrabilidad PASS, `go test ./...` PASS. Verificar **GitHub Actions del último HEAD** de rama. Las pruebas de código no sustituyen captura PPSSPP.

## 5. Bloqueos y relevo obligatorio

F2 sigue **ABIERTA** por: rastrear la instrucción PC MIPS, carga/decodificación de KITAJIMA y comandos GE/VRAM; verificar HUD, ayudas, tutoriales y combate; comprobar los 19 glifos en textos/escenas diferentes y medir anclajes; solo entonces estudiar activar tinta blanca de forma canónica y repetir regresión F1 en ventana960×544 (ancho 756/≈764, Sí/No). Las fases F3 intro inglés, F4 4524 scripts, F5 gameplay y F6 BPS/EXE final están sin finalizar.

**Regenerar en la próxima sesión `reports/ESTADO_CONTINUIDAD_PPSSPP.json` y `prompts/SIGUIENTE_TAREA.md`, mostrar prompt nuevo completo y exigir de nuevo la generación recursiva de otro.**
