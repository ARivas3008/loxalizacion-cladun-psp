# CLADUN F2 — Comparación REAL de dos IMY decodificadas, sin emulador (22/11/2026)

**F2 ABIERTA.** La evidencia nueva procede de la ISO USA original del usuario. NO se arrancó PPSSPP 1.20.4, NO hay captura nueva, NO se observó GE/VRAM, ni PC de iconos. La auditoría lee datos comerciales únicamente de modo privado y publica solo hashes y métricas.

## Auditoría binaria REAL sobre la ISO original

ISO privada de **305496064 bytes**, SHA-256:
`b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`

Se identificaron los dos recursos IMY ya autenticados por SHA y estructura DSARC. Se reconstruyó su contenido de píxeles de 4 bits por índice **en memoria**, con comprobación de fin de stream y sin guardar PNG, datos de CLUT ni bytes gráficos.

| Métrica real | SYSGRA.ARC/FONT.IMY | FONT.ARC/FONT_00.IMY |
|---|---|---|
| Índice PSPFS / DSARC | 225 / 14 | 308 / 1 |
| Bytes comprimidos | 4148 | 17468 |
| Campo IMY en +4 | 0x8060 | 0x0060 |
| Flags comprimidas | 3910 | 17342 |
| Resolución de datos 4 bpp | **256 × 256** | **512 × 256** |
| Bytes decodificados | 32768 | 65536 |
| Índices de píxel CLUT utilizados | 0, 1, 15 | 0, 1 |
| Conteos de píxel por índice | 0:61045, 1:2119, 15:2372 | 0:99164, 1:31908 |
| Decodificación del stream completo | Sí | Sí |

SHA256 de la matriz decodificada SYSGRA FONT.IMY:
`5d4ff855af1132ea0abf204b5a4c44ddce28b55758772feba21ce6163cc6c4fc`

SHA256 de la matriz decodificada FONT.ARC FONT_00.IMY:
`7bb085850b0eca09d03e6553565cd687be16d3af76fac2de076bc23b82cff3eb`

**Conclusión limitada pero verificable:** las dos imágenes originales NO tienen la misma geometría ni los mismos bytes 4bpp decodificados. El segundo es el atlas de FONT.ARC que se viene adaptando; el primero es otro recurso de SYSGRA.ARC cuya **función durante el renderizado todavía NO se ha probado**. Los índices utilizados no determinan por sí solos los colores visibles ni la procedencia funcional de la pantalla.

## Código y ejecución

Nuevo lector de solo lectura `tools/f2_auditar_dos_fuentes_imy.py` con 16 pruebas sintéticas de errores de geometría, lookbacks, flags, truncamiento, firmas, tipos y end-of-stream en `tests/test_f2_auditar_dos_fuentes_imy.py`. La ISO exacta es obligatoria: 305496064 bytes y SHA-256 canónico.

Ejemplo privado: `python tools/f2_auditar_dos_fuentes_imy.py --iso-usa /PRIVATE/USA.iso --reporte /PRIVATE/nuevo-reporte.json`

Informe realmente generado localmente: `CLADUN_F2_dos_fuentes_decodificadas_metrica_privada_2026-11-22.json`; SHA-256:
`9d4f13e039ee18c176b45d34b21c2376ce2ffde78f2251179aa18743a3b6cb9b`

Commit de código `5242371ee8b0410a6456ee9241d81a453445b1c6`. Sus GitHub Actions push `45041694305` y PR `45041700035` terminaron SUCCESS: **249 pruebas Python**, Go y compilación Windows pública (sin ISO/BPS). Estas pruebas NO equivalen a capturas PPSSPP.

## Bloqueos y garantías

La terminal sigue sin resolver github.com (`git fetch origin` y `git pull --ff-only` fallan con DNS; el checkout vacío también impide `git switch`). No existe AppImage PPSSPP oficial v1.20.4 localmente ni ISO F1 canónica de SHA conocido. No se generó ISO candidata/BPS, no se cambió corpus, ningún 2721 glifo original fue modificado, no se tocó la configuración `white_new_ink=False` ni se retiró `--event-safe-only`. PR #7 se conserva DRAFT.

Pendiente imprescindible: correlación real MIPS/RAM→GE→VRAM y función de cada FONT.IMY, validación visual de los **19 caracteres** `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō` en varios contextos y nueva regresión de Opciones F1 en ventana auténtica X11 960×544, interior 756/exterior ~764. F3–F6 permanecen pendientes.

Informe estructurado: `reports/RESULTADO_F2_DOS_FUENTES_IMY_2026-11-22.json`; relevo `prompts/SIGUIENTE_TAREA.md`.
