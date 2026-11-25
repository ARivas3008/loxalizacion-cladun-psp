# F2 — Mapa estático de catorce franjas de TUIKA_MES.IMY (22/11/2026)

**F2 ABIERTA. No se ejecutó PPSSPP en esta sesión.** Datos nuevos procedentes de una ISO USA auténtica aportada por el usuario y de una sonda privada aislada. No representan fotogramas ni confirman qué aparece en pantalla. Una franja NO necesariamente representa una frase independiente y sus coordenadas NO están aprobadas como región de edición.

## Autenticación binaria repetida

- ISO USA extraída del 7z mediante libarchive: 305496064 bytes, SHA256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f.
- ISO TUIKA magenta reconstruida, privada e independiente: SHA256 b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa.
- Un cotejo integral byte a byte confirmó que solo cambiaron los offsets absolutos decimales 114744872, 114744873 y 114744874 (RGB 249,251,249 → 255,0,255). Alfa intacto. 348 PSPFS vecinos y 26 DSARC vecinos intactos, tablas intactas.
- TUIKA_MES.IMY original: SHA256 c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127.
- Índices de 4bpp decodificados y unswizzle PSP 16×8: superficie 256×256, SHA256 3c181786f72008c144a2187d362d289d453b4f00d93fe5f8cb2facc0f23d14d5. Índice 2: exactamente 9144 píxeles. Máscara SHA256 382ae8d2ffa8908979050b5e83f38ec9967b461bbf9b614dd92775da90e409ba.

## Nuevo resultado: intervalos y separaciones

| Franja | Filas y (inclusive) | Columnas x CLUT2 | Píxeles CLUT2 | Filas vacías después |
|---:|---:|---:|---:|---:|
| 0 | 2–15 | 4–239 | 1110 | 4 |
| 1 | 20–33 | 2–149 | 730 | 4 |
| 2 | 38–51 | 2–117 | 534 | 4 |
| 3 | 56–69 | 2–117 | 578 | 4 |
| 4 | 74–87 | 2–125 | 564 | 4 |
| 5 | 92–105 | 2–123 | 532 | 4 |
| 6 | 110–123 | 2–91 | 432 | 4 |
| 7 | 128–141 | 2–179 | 784 | 4 |
| 8 | 146–159 | 2–99 | 504 | 4 |
| 9 | 164–177 | 2–227 | 980 | 3 |
| 10 | 181–196 | 5–114 | 422 | 2 |
| 11 | 199–214 | 2–135 | 270 | 3 |
| 12 | 218–231 | 2–137 | 600 | 4 |
| 13 | 236–249 | 2–247 | 1104 | 6 |

**Suma = 9144 píxeles; 14 franjas, 200 filas activas, 12 bandas de altura 14 y 2 de altura 16.** Esos rectángulos describen únicamente la extensión de CLUT2; otros índices podrían estar en el interior. No usar las coordenadas para reemplazar todo el rectángulo sin una guarda adicional.

## Herramienta y QA

Nuevo analizador: tools/f2_mapa_franjas_tuika.py. Exige dos ISOs autenticadas mediante tools/f2_cotejar_impacto_clut_tuika.py, valida tamaño, 14 bandas, 9144 píxeles y huella completa. Calcula x/y, límites, separaciones, recuentos y SHA por franja, sin exportar píxeles comerciales. Nuevo conjunto: tests/test_f2_mapa_franjas_tuika.py, **18/18 pruebas sintéticas locales PASS** (sin PPSSPP). Informes más exhaustivos privados: TUIKA_14_FRANJAS_EVIDENCIA_ESTATICA_PRIVADA_20261122.json, SHA256 23f02aa43e4d153c3d62ff065676788c34d6116890f158466ab5c0d9cf8f866e; no se sube a GitHub. Informe público SOLO de metadatos: reports/RESULTADO_F2_MAPA_FRANJAS_TUIKA_2026-11-22.json.

Ejemplo de ejecución sobre ISOs auténticas, usando una ubicación privada nueva:

    python tools/f2_mapa_franjas_tuika.py --iso-usa /PRIVATE/USA.iso --iso-sonda /PRIVATE/TUIKA_magenta.iso --reporte-privado /PRIVATE/TUIKA_franjas.json

## Límites y continuidad

PPSSPP oficial AppImage 1.20.4 ausente; descarga y clone GitHub fallaron por DNS. ISO F1 canónica histórica no se encuentra aquí. **Cero nuevas capturas de PPSSPP**, cero comandos GE de juego auténticos, ninguna cadena MIPS→RAM→GE→VRAM probada ni nueva regresión F1 de ventana X11 960×544. Las 14 franjas no están vinculadas todavía a escenas. Faltan 19 glifos multicontesto; F3 intro, F4 4524 scripts, F5 gameplay y F6 BPS/EXE final.

No se modificaron corpus de 9237, 2721 glifos originales, ISO canónica, integrador, BPS o código de fuentes. white_new_ink=False y --event-safe-only quedan vigentes. PR #7 continúa DRAFT. Regenerar íntegramente prompts/SIGUIENTE_TAREA.md con obligación recursiva al siguiente relevo; nunca subir ISO, CLUT, PNG, IMY o dumps a GitHub.
