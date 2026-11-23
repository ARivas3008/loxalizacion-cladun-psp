# F3 — ANIME: tipos IMY auténticos y límites del descompresor (23/11/2026)

**F3 ABIERTA, F2 ABIERTA.** Esta auditoría no demuestra de dónde proceden las letras del prólogo inglés. Tampoco crea una ISO candidata ni modifica los recursos comerciales.

## Evidencia (A) original auténtica, solo lectura

Se extrajo el 7z aportado por el usuario en el entorno de análisis: ISO USA de **305.496.064 bytes**, SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`, coincidencia exacta. La terminal no resolvió `github.com` para clonar; los archivos públicos del repositorio sí se consultaron con el conector GitHub.

Se abrió `PSP_GAME/USRDIR/DATA.DAT` (offset ISO 113.770.496), y se verificó `PSPFS_V1` con **349** miembros. Para evitar confusiones, las cifras siguientes son **cabeceras literales IMY compatibles con un chequeo estructural**, NO cuadros decodificados ni texturas vistas en PPSSPP:

| Índice | Recurso | Bytes guardados | Firmas IMY | Tipos |
| --- | --- | ---: | ---: | --- |
| 234 | ANIME000.IDT | 3.537.936 | 231 | 0x00: 136; 0x02: 95 |
| 235 | ANIME001.LDT | 287.472 | 24 | 0x00: 24 |
| 236 | ANIME002.LDT | 2.067.856 | 0 | ninguno |

En las 255 cabeceras, la magnitud de encabezado `u32(+4)` corresponde exactamente a `stride * rows + 32`. Los tres primeros `u32` de los recursos (192, 24, 39) **no** se certifican como fotogramas.

## Ensayo estático controlado del algoritmo previo

`tools/f3_anime_imy_estructuras.py` simula las reglas de flags/lookback del descompresor IMY legado sobre bloques originales en memoria temporal, sin producir PNG, píxeles ni datos de imagen exportables. **Tipo 0x00: 160/160 compatibles con ese algoritmo** (136 + 24). **Tipo 0x02: 0/95 compatibles**: 55 fallos de lookback y 40 de longitud. Es una prueba de compatibilidad de flujo, **NO** de color, orden de píxeles, frames, deltas ni paletas. No se incorporó soporte 0x02 al repacker ni al parcheador.

Los SHA-256 originales de los tres miembros y los recuentos están en `reports/RESULTADO_F3_ANIME_IMY_ESTRUCTURAS_2026-11-23.json`. Ninguno de estos datos identifica la fuente de la frase observada `Some say, because the treasures were there.`. La sonda anterior que renombró ANIME000 causaba crash **antes del título**, de modo que solo prueba dependencia de arranque, no la composición de letras.

## Reproducir de forma privada

```bash
sha256sum /PRIVADO/Cladun_USA.iso
python tools/f3_anime_imy_estructuras.py --iso-original /PRIVADO/Cladun_USA.iso --reporte /PRIVADO/f3_imy_estructuras_nuevo.json
python -m unittest tests.test_f3_anime_imy_estructuras -v
```

El informe JSON generado contiene solo metadatos, no contiene ISO ni IMY ni gráficos. La herramienta requiere la **ISO original SHA exacto** y no autoriza otras variantes. Se ejecutaron 14 tests **(B) sintéticos** locales y el inventario (A) de los tres archivos originales: PASS. No se puede ejecutar `python -m unittest discover` de todo el repositorio desde esta terminal porque `git fetch` falla por DNS; GitHub Actions posterior al commit debe cubrir la suite de código.

## Exclusiones y trabajo que queda

No existe en este relevo **(C) nueva ejecución PPSSPP**: el AppImage 1.20.4 no está en el entorno y la terminal no resuelve GitHub para descargarlo. Conservar íntegramente la evidencia (C) *histórica* en `docs/F2_WS_REAL_F1_CONTROLES_GE_2026-11-23.md`, `docs/F2_MAPA_JUGABLE_GE_X11_F1_2026-11-23.md` y `docs/F3_PROLOGO_ANIME000_DEPENDENCIA_PPSSPP_REAL_2026-11-23.md`. **No** sustituir capturas, GPU/VRAM o pruebas gráficas por la compatibilidad de flags.

Separadamente, la ISO original autentica `SCRIPT.SDT/SCRIPT.DAT` SHA `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`, `SCRIPT.TBL` SHA `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`, 1.625 bloques y 51.705 comandos. Los 7 bloques `demo1001` de ID 100000/100100/100190/100101/100191/100110/100120 totalizan 878 comandos (**5/422/27/339/28/23/34**). Los **85** textos de tamaño cambiante continúan bloqueados por `--event-safe-only`. Las coincidencias numéricas en argumentos de opcodes no identifican por sí solas saltos MIPS o referencias reales; no reescribirlos por conjeturas.

**Siguiente experimento:** con PPSSPP oficial autenticado y el prólogo visible, registrar una carga I/O y GE en esa escena y contrastar textura/CLUT en RAM/VRAM con la ISO real. Solo si el enlace causal existe, diseñar una sonda cromática aislada reversible con A/B sincronizado; no renombrar miembros. Trabajar el modelo de control de flujo de 85 eventos en paralelo, sin desplazar instrucciones sin evidencia. F2 y F4–F6 permanecen abiertos.

El PR #7 debe conservarse DRAFT, sin merge, fuerza ni binarios comerciales en Git.
