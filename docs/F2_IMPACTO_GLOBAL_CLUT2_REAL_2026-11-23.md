# F2 — Cobertura auténtica de CLUT2 en TUIKA: 9.144 texeles, riesgo para iconos/dígitos (2026-11-23)

**F2 ABIERTA.** En este relevo se inspeccionó físicamente la ISO comercial original y una sonda privada TUIKA. La evidencia es **A estática auténtica**, NO C (PPSSPP). Se incorporó un auditor de solo lectura para reproducir y blindar los cálculos; sus tests usan rasters sintéticos (B).

## Evidencia A nueva: el cambio de tres bytes afecta un índice de paleta global

Archivos privados leídos por bloques:
- Original USA: 305.496.064 bytes, SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.
- Sonda TUIKA: 305.496.064 bytes, SHA256 `b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa`.
- Comparación de ISO completo: exactamente tres diferencias, offsets `114744872, 114744873, 114744874`, RGB `(249,251,249)→(255,0,255)`; alfa original intacta.

De la original se leyó TUIKA_MES.IMY a offset absoluto `113770496+895488+78848`, longitud 7912; SHA del miembro `c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127`. Se decodificó el IMY A4 4bpp tipo 0x60 con flags originales, se aplicó unswizzle PSP 16×8, y se comprobaron **tres hashes ya fijados**:
- Descompresión de índices empaquetados: `3c181786f72008c144a2187d362d289d453b4f00d93fe5f8cb2facc0f23d14d5`.
- Índices lineales de 256×256: `a3da2c0d728288c2842b0d9164f4dd220c4713eaa19b3559ef7105f837f8106d`.
- Máscara de texeles que valen 2: `382ae8d2ffa8908979050b5e83f38ec9967b461bbf9b614dd92775da90e409ba`.

Histograma AUTÉNTICO: índice 0 **45.784**, índice 1 **10.608**, índice 2 **9.144**. Total 65.536 (=256×256). La modificación global de CLUT2 colorearía los **9.144 texeles (13,95 %)** si ese atlas y esa CLUT se llegaran a renderizar. Su bbox en atlas es `[2,2,247,249]`, no toda la textura está vacía o restringida a una etiqueta.

## El hallazgo crítico: 3.506 texeles del índice 2 están en siete subregiones protegidas

| Región del atlas original | Texeles indexados por CLUT2 |
|---|---:|
| banda 00, mezcla japonesa | 1.110 |
| banda 10, etiqueta G-star provisional | 338 |
| banda 10, iconos de control | 84 |
| banda 11, símbolos de control | 270 |
| banda 12, dígitos 0–9 | 600 |
| banda 13, dígitos 0–9 | 512 |
| banda 13, texto provisional de ataque especial | 592 |
| **Total en las siete subregiones** | **3.506** |
| Fuera de esas siete subregiones | 5.638 |

Dentro de los sectores estrictamente LOCKED, la cuenta del índice 2 es **2.576**; las dos regiones PROVISIONAL_LABEL_LOCKED suman otros **930**. Los separadores transparentes de índice 0 permanecen transparentes. Estos nombres son hipótesis de atlas; NO implican que el HUD o una habilidad los dibuje en PPSSPP.

**Consecuencia de ingeniería:** una sonda de CLUT2 es un contraste cromático GLOBAL, no una intervención solo en texto. Cambiarla como solución final podría recolorear números, iconos, etiquetas japonesas y otros trazos. Conservar sonda únicamente como diagnóstico, sin aprobar ninguna ROI de edición de píxeles ni declarar el juego reparado.

## Nueva implementación B

- `tools/f2_tuika_clut2_cobertura.py`: auditor de solo lectura que exige ambos SHA ISO, tamaños, miembro TUIKA exacto, identidad del pixel stream original/sonda, los tres hashes raster ya auditados, y los tres cambios permitidos en el ISO completo. Reutiliza decodificador IMY y unswizzle del proyecto; produce **solo JSON agregado de metadatos**, nunca PNG, IMY ni atlas comercial.
- `tests/test_f2_tuika_clut2_cobertura.py`: 14 ensayos sintéticos para histograma, texeles protegidos, dígitos/iconos, bbox, separadores transparentes, rutas privadas, no sobrescritura y symlinks. No son ejecución PPSSPP.
- El cálculo original del relevo se efectuó sobre bytes comerciales reales con una implementación privada de decodificación y se contrastó contra hashes preexistentes. GitHub CI debe probar las importaciones del auditor nuevo contra módulos auténticos del repo. Aún no se puede llamar prueba C.

Comando de repetición con fuentes privadas y ruta de informe nueva:

    python tools/f2_tuika_clut2_cobertura.py --iso-usa /PRIVATE/USA.iso --iso-sonda /PRIVATE/SONDA.iso --reporte-privado /PRIVATE/TUIKA_CLUT2_COBERTURA_NUEVA.json
    python -m unittest discover -s tests -p 'test_f2_tuika_clut2_cobertura.py' -v

## Bloqueo C y continuidad F2–F6

No hay PPSSPP 1.20.4 oficial disponible en este contenedor. Se intentó resolver/descargar `github.com` y la terminal respondió `Could not resolve host: github.com`; Xvfb está presente, pero sin AppImage oficial no hay nuevo arranque, combate, capturas X11 o PSP framebuffer, tramas GE, MIPS ni VRAM. Las pruebas C anteriores de F1 Opciones/mapa se mantienen como históricas, no se atribuyen a esta sesión.

F2 requiere un A/B en **habilidad o combate verdaderos** USA/sonda con capturas X11 testificadas, `tools/f2_cotejar_x11_tuika.py`, `gpu.record.dump --ge-only` y vínculo real a TUIKA/MIPS/RAM/GE/VRAM, seguido de QA de los 19 glifos `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō` en múltiples contextos. Proteger 7 subregiones, dígitos y símbolos; white_new_ink=False.

F3 conserva resultados IMY ANIME000 (231 cabeceras: 136 tipo00/95 tipo02 sin decoder), y auditoría de candidatos SCRIPT (4.680 coincidencias de IDs, NO saltos). Mantener 85 textos demo1001 y 4.524 scripts pospuestos por `--event-safe-only`. F4–F6 abiertas. Corpus 9.237 filas, 2.721 glifos antiguos intactos; PR #7 OPEN/DRAFT. No subir ISOs, BPS, juegos, FONT, EBOOT, dumps ni capturas comerciales al repositorio.

La obligación recursiva exige reemplazar íntegramente `prompts/SIGUIENTE_TAREA.md` al cerrar cada relevo.
