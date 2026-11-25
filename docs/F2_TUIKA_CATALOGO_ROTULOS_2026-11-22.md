# F2 — Transcripción visual provisional y protección de regiones de TUIKA_MES.IMY (22/11/2026)

**Estado: F2 ABIERTA.** Se inspeccionó una textura IMY **auténtica** de la ISO USA aportada por el usuario, no un fotograma PPSSPP. La lectura del inglés es una **interpretación visual manual de una previsualización privada**, no una extracción de cadenas de bytes, una prueba de su aparición en juego ni una autorización para editar.

## Evidencia binaria ejecutada

ISO original privada: 305.496.064 bytes, SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. El fichero se extrajo del 7z con libarchive; SHA recalculado. TUIKA original, DSARC índice 24 de SYSGRA.ARC: SHA-256 `c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127`. Reconstrucción IMY 4bpp + unswizzle PSP 16×8 verificada por raster indexado comprimido SHA `3c181786f72008c144a2187d362d289d453b4f00d93fe5f8cb2facc0f23d14d5` y máscara CLUT2 SHA `382ae8d2ffa8908979050b5e83f38ec9967b461bbf9b614dd92775da90e409ba`.

**Hallazgo medido, no meramente inferido:** En los rectángulos de extensión CLUT2 hay **9.144 píxeles de tinta blanca (índice2), 8.625 píxeles negros opacos (índice1) y 11.839 transparentes (índice0)**, suma **29.608** posiciones de rectángulo; no basta editar el índice2: se destruirían contornos/antialias y otros elementos en repintados burdos. **Los rectángulos no son ROI seguras.**

## Catálogo provisional de los 14 renglones del gráfico

| Banda | y | Tipo | Lectura visual del original | Propuesta española (NO aprobada) |
|---:|---:|---|---|---|
| 0 | 2–15 | mixto | Normal & Warrior LV.; glifos japoneses adyacentes | pendiente por grafía y glosario |
| 1 | 20–33 | nivel | Gamble Merchant LV. | pendiente por glosario |
| 2 | 38–51 | nivel | Angel Guard LV. | pendiente por glosario |
| 3 | 56–69 | nivel | Demon Magic LV. | pendiente por glosario |
| 4 | 74–87 | nivel | Hell Dragon LV. | pendiente por glosario |
| 5 | 92–105 | mensaje | Nullified traps! | ¡Trampas anuladas! |
| 6 | 110–123 | mensaje | Scattered G! | ¡G dispersos! (revisar moneda/género) |
| 7 | 128–141 | mensaje | Replenished HP for all! | ¡HP recuperados para todos! |
| 8 | 146–159 | mensaje | Recovered SP! | ¡SP recuperados! |
| 9 | 164–177 | mensaje | Attack all enemies on screen! | ¡Ataca a todos los enemigos en pantalla! |
| 10 | 181–196 | rótulo + controles | G Star On! y símbolos | pendiente |
| 11 | 199–214 | iconos | símbolos de controles, letra F, signos | no tratar como frase |
| 12 | 218–231 | números | dígitos 0–9 | no traducir |
| 13 | 236–249 | números + mensaje | dígitos 0–9 junto a No special attack | Solo «Sin ataque especial» como borrador; números se preservan |

**No se han transcrito con certeza** los caracteres japoneses ni todos los controles de las bandas mixtas. La expresión `G Star On!` podría requerir verificación de terminología contextual. Las propuestas pueden exceder el ancho de los sprites; no se han aprobado ni insertado. En particular la franja 13 contiene números y frase **en la misma fila**, por lo que repintar la fila completa borraría glifos numéricos.

## Herramientas y controles

Nueva `tools/f2_tuika_rotulos_privado.py`: valida SHA de ISO y miembro original, decodifica índices originales y la geometría registrada, audita **CLUT0/CLUT1/CLUT2 por rectángulo**, incorpora lectura visual manual marcada como no certificada, exige un informe JSON privado nuevo, rechaza rutas Git y sobrescritura. No publica PNG, atlas ni datos de raster. **Toda banda informa `safe_to_replace_whole_band=false`, `safe_to_replace_bbox=false` y `safe_to_replace_clut2_only=false`.**

`tests/test_f2_tuika_rotulos_privado.py`: **23 pruebas sintéticas locales PASS**, entre ellas protecciones de ruta, clasificación de números/iconos, recuentos de tinta negra y rechazo de edición; la ejecución local usó dependencias equivalentes simplificadas porque no había checkout Git sincronizado, mientras GitHub CI comprueba integración contra módulos originales. El auditor **sí se ejecutó contra la ISO original auténtica** en modo privado, con suma verificable de 9.144 blancos, 8.625 negros, 11.839 transparentes. JSON de salida privada `TUIKA_ROTULOS_original_sha_validado_20261122.json`, SHA `82fc0710130a333ca9cf23a3d4b23638713e1436da9432f7fe6fd7f0d70bbfd3`. No subir ese archivo ni previsualizaciones comerciales.

Comando privado tras verificar que la ISO es original y elegir una salida inexistente:

```bash
python tools/f2_tuika_rotulos_privado.py \
  --iso-usa /PRIVATE/Cladun_USA_ORIGINAL.iso \
  --reporte-privado /PRIVATE/TUIKA_ROTULOS_AUDIT_NUEVO.json
```

La herramienta no modifica ISOs ni el corpus. La sonda magenta sigue siendo un experimento privado independiente de 3 bytes (SHA `b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa`).

## Próxima prueba funcional obligatoria

PPSSPP oficial 1.20.4 sigue **NO DISPONIBLE** en este relevo: DNS de github.com falla y no existe AppImage instalado. No se generaron capturas A/B nuevas, dumps GE auténticos, ni traza MIPS→RAM→GE→VRAM; no se probaron los 19 glifos en múltiples contextos y no se repitió F1 con X11 960×544. Para cada rótulo primero identificar dónde se dibuja y el recorte exacto en PPSSPP (origen + sonda), separar controles y números, concordar glosario HP/SP/G, elegir máscara editable SOLO tras QA visual. Conservar `white_new_ink=False`, `--event-safe-only`, las 9237 traducciones y las 4524 SCRIPT.DAT aplazadas. PR #7 DRAFT; F3–F6 pendientes. Relevo obligatorio recursivo: `prompts/SIGUIENTE_TAREA.md`.
