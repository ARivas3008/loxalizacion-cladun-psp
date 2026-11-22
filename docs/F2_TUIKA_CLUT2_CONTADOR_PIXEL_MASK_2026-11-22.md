# F2: impacto real de la sonda TUIKA sobre 9.144 píxeles (22/11/2026)

**F2 ABIERTA.** Análisis auténtico de **dos ISOs privadas** (original USA y sonda magenta), sin ejecutar PPSSPP 1.20.4. El resultado es una **previsualización y máscara contrafactual de texturas**, NO una captura ni prueba de uso en juego.

## Fuentes verificadas

| Fuente privada | SHA-256 completo |
|---|---|
| ISO USA original, 305496064 bytes | `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f` |
| ISO sonda magenta, mismo tamaño | `b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa` |
| TUIKA_MES.IMY original | `c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127` |
| TUIKA_MES.IMY magenta | `efcf4f41f57c300476e8ce54a32dea01f242dda3fbf3fb9c4e0b582bad8f5252` |

La sonda anterior ya había demostrado el cambio exacto de **tres bytes RGB** de `SYSGRA.ARC/TUIKA_MES.IMY`, dejando **348/348 vecinos PSPFS** y **26/26 vecinos DSARC** y el resto de la ISO sin modificaciones, alfa original conservada. Código de esa sonda: `tools/f2_probe_tuika_palette_privado.py`. No se alteró ningún script, recurso textual, icono, fuente ni tabla.

## Nueva auditoría de píxeles, desde bytes IMY originales

La herramienta `tools/f2_cotejar_impacto_clut_tuika.py` valida ambos SHA ISO completos, extrae exclusivamente TUIKA en su offset original, autentica los SHA de los dos miembros y usa la decodificación IMY auditada (`f2_auditar_27_imy_sysgra.py`) y el **unswizzle PSP de bloques 16 bytes × 8 filas** (`f2_previsualizar_sysgra_privado.py`).

Se demostró que los **32.768 bytes de índices 4bpp descomprimidos son exactamente idénticos** en ambas versiones. Solo cambió la entrada CLUT n.º 2: de RGBA **(249,251,249,255)** a **(255,0,255,255)**; todos los otros colores y el canal alfa están intactos. El raster tiene **256×256 = 65.536 píxeles**, con esta distribución:

| Índice | Píxeles | Efecto |
|---|---:|---|
| 0 | **45.784** | Sin modificación |
| 1 | **10.608** | Sin modificación |
| 2 | **9.144** | Blanco original → magenta de diagnóstico |
| 3–15 | **0** | Sin uso en esta textura |

El índice 2 afecta **9.144 píxeles (13,952637 %) de los 65.536** y deja **56.392** sin cambio visual calculado. Esos píxeles se distribuyen en **200 filas**, agrupadas en **14 franjas horizontales**. Bounding box de la máscara: **x=2..247, y=2..249**. SHA-256 de máscara binaria (0/255, recorrido horizontal) `382ae8d2ffa8908979050b5e83f38ec9967b461bbf9b614dd92775da90e409ba`. SHA de índices descomprimidos `3c181786f72008c144a2187d362d289d453b4f00d93fe5f8cb2facc0f23d14d5`.

La imagen privada consta de **tres paneles**: textura original descomprimida, contrafactual magenta y máscara de píxeles afectados. Es un material estático del asset con texto gráfico inglés, *no procedencia RAM/GE/VRAM ni render del juego*. La sonda colorea cualquier píxel con índice 2, no únicamente letras individuales.

- Comparación privada (NO GitHub): `CLADUN_F2_TUIKA_CLUT2_ANÁLISIS_ESTATICO_NO_PPSSPP_2026-11-22.png`, **16.809 bytes**, SHA `ec595486a96922d2066883cee9e2d4d895c3eda4525168d4dc15d865c659f50b`.
- Informe privado (solo métricas, no píxeles): `CLADUN_F2_TUIKA_CLUT2_CUANTIFICACION_PRIVADA_2026-11-22.json`, SHA `4c0836c0661bebc876b6271bffb516f88de435df3af1efcf39c49dc36d169c8d`.

## Código, controles y alcance

Nuevo `tools/f2_cotejar_impacto_clut_tuika.py` y `tests/test_f2_cotejar_impacto_clut_tuika.py`: **19 tests sintéticos nuevos**, incluidos cambios ajenos a la paleta, modificación del alfa, SHA erróneos, segmentación por filas, orden de nibbles PSP, rutas relativas o ubicadas dentro del checkout, symlinks y sobrescritura. Código commit `3241f5ca9463e202e3b9b1371bf0deefa52f4673`. Ambos flujos CI de ese código: push `45052513223` y PR `45052519322`. Push SUCCESS, **332 tests Python**, integridad, Go y compilación pública Windows, sin assets de juego en CI. PPSSPP NO forma parte del CI.

Ejemplo reproducible solo con ISOs PRIVADAS nuevas y auténticas:

```bash
python tools/f2_cotejar_impacto_clut_tuika.py \
  --iso-usa /PRIVATE/CLADUN_USA.iso \
  --iso-sonda /PRIVATE/CLADUN_TUIKA_magenta.iso \
  --reporte-privado /PRIVATE/reporte_TUIKA.json \
  --png-privado /PRIVATE/comparacion_TUIKA.png
```

La ejecución auténtica local generó los SHA anteriores desde las dos ISOs verificadas. Las pruebas de GitHub **son sintéticas** y no contienen la ISO, IMY ni PNG originales.

## F2–F6 aún pendientes

PPSSPP oficial 1.20.4 no está instalado; `curl` y `git fetch` fallan porque `github.com` no resuelve. La ISO F1 canónica anterior no está disponible aquí. **No hubo ejecución PPSSPP**, ni dos capturas reales original/sonda, ni dump GE, ni rutina MIPS/VRAM de iconos comprobada, ni nueva validación de los 19 glifos ni regresión F1 X11 960×544. Los textos ingleses incrustados en `TUIKA_MES.IMY` son un riesgo de localización gráfica detectado por análisis estático; determinar su contexto de uso sigue pendiente.

Mantener `white_new_ink=False`, `--event-safe-only`, corpus canónico 9237, F4 4524 scripts aplazados, PR #7 DRAFT. No fusionar ni publicar BPS o EXE final por este resultado. Continuar con PPSSPP real, F3 intro, F4 scripts, F5 QA end-to-end y F6 release.

Estado en `reports/ESTADO_CONTINUIDAD_PPSSPP.json`; informe `reports/RESULTADO_F2_TUIKA_CLUT2_PIXELES_2026-11-22.json`; relevo completo en `prompts/SIGUIENTE_TAREA.md`.
