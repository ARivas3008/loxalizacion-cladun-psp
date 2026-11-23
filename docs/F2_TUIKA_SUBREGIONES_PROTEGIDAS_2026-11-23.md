# F2 — Separación autenticada de 7 subregiones en TUIKA y guardia antidaño (23/11/2026)

**F2 continúa ABIERTA.** Se utilizó la ISO USA original del 7z del usuario: 305.496.064 bytes, SHA256 completo `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. Se inspeccionó `SYSGRA.ARC/TUIKA_MES.IMY` original (SHA256 `c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127`) mediante descompresión IMY 4bpp y *unswizzle* PSP 16×8, **no** PPSSPP. El índice lineal de 256×256 bytes (un valor 0–15 por píxel), solo en memoria, se autenticó con SHA `a3da2c0d728288c2842b0d9164f4dd220c4713eaa19b3559ef7105f837f8106d`. No se exportaron píxeles ni arte comercial al repositorio.

## Nuevo descubrimiento: separación exacta de dígitos y rótulos

La anterior clasificación de 14 bandas ocultaba que algunas bandas mezclan letras, controles y números. Ahora se han registrado los **rangos de columnas de los componentes**, comprobando los valores exactos de CLUT0/1/2 y SHA256 del raster de cada zona, en el original real.

| Banda | Componente | x inicial–final | y inicial–final | Índice0 (transparente) | Índice1 (negro opaco) | Índice2 (blanco) | Estado |
|---|---|---|---|---:|---:|---:|---|
| 0 | Inglés y grafía japonesa combinados | 1–240 | 2–15 | 1190 | 1060 | 1110 | PROTEGER |
| 10 | Rótulo «G Star On!» provisional | 4–79 | 181–196 | 468 | 410 | 338 | NO APROBADO PARA EDITAR |
| 10 | Símbolos de controles | 92–115 | 181–196 | 192 | 108 | 84 | PROTEGER |
| 11 | Símbolos y teclas | 1–136 | 199–214 | 1546 | 360 | 270 | PROTEGER |
| 12 | Dígitos 0–9 | 1–138 | 218–231 | 688 | 644 | 600 | PROTEGER |
| 13 | Dígitos 0–9 | 1–108 | 236–249 | 484 | 516 | 512 | PROTEGER |
| 13 | «No special attack» | 112–248 | 236–249 | 745 | 581 | 592 | NO APROBADO PARA EDITAR |

Los valores 0, 1 y 2 son índices de la textura original. La clasificación de los textos se basa en lectura visual manual previa y **no prueba que aparezcan en pantalla**.

Separadores comprobados **íntegramente transparentes (índice0)**, no solo «sin píxeles blancos»:
- Franja 10: x=80–91, y=181–196, **192 posiciones** de índice0 entre el rótulo y los iconos.
- Franja 13: x=109–111, y=236–249, **42 posiciones** de índice0 entre dígitos y «No special attack».
- Dentro de franja 13: x=190–199, y=236–249, **140 posiciones** de índice0 entre palabras.

El componente de dígitos y el rótulo inglés están separados en el raster guardado; esto **no garantiza** que el espacio baste para una traducción española. La región completa de la banda y el recorte del texto no son ROI seguras hasta validar su uso/encuadre en PPSSPP.

## Protección implementada, con negativa por defecto

Se agregó `tools/f2_tuika_proteger_subregiones.py`. Autentica en disco la ISO por tamaño y SHA, el miembro TUIKA por SHA, el índice IMY descomprimido por SHA, y el raster lineal/7 subregiones por SHA antes de producir un JSON privado **sin arte**. Impone tres separadores transparentes y clasifica los **9.738 píxeles/posiciones bloqueados** que deben preservar números, iconos, grafía japonesa y huecos. El helper `guard_candidate` opera **solo en memoria**, recibe dos planos indexados del mismo tamaño y no permite cambiar ningún píxel por defecto; futuras máscaras explícitas nunca pueden intersectar un área bloqueada. El resultado del guardia NO acredita fidelidad visual, runtime ni inserción segura del contenedor y no escribe ISO/parche.

El reporte JSON privado derivado de índices auténticos quedó en `TUIKA_protected_subregions_authentic_static_PRIVATE.json`, SHA256 `ab23878975415fed52ba0f97cdca4f75be973ab1b52768459397e82b51138439`. El informe **público** contiene solo coordenadas, recuentos y SHA de subregiones: `reports/RESULTADO_F2_TUIKA_SUBREGIONES_2026-11-23.json`.

## Pruebas reales vs sintéticas

**Auténticas offline:** el 7z proporcionado se extrajo por libarchive; ISO de 305496064 bytes autenticada por SHA; el decodificador original IMY y el *unswizzle* independiente produjeron la superficie esperada y pasaron la autenticación de **7 subregiones y 3 huecos**, con **todas sus huellas SHA**. No hubo edición de los bytes de juego ni capturas falsas.

**Sintéticas:** `tests/test_f2_tuika_proteger_subregiones.py` añade **32 tests locales PASS** para posiciones bloqueadas, rechazo de cambios no autorizados, separadores, rutas Git y symlinks, longitud e índices inválidos. Los tests no muestran el videojuego. En el entorno actual no había checkout Git real; los CI de GitHub permiten comprobar la integración en el repositorio.

**No ejecutadas:** PPSSPP 1.20.4 (AppImage ausente; terminal DNS para github.com fallida), fotogramas A/B, MIPS→RAM→GE→VRAM, 19 glifos en múltiples escenas, nueva regresión F1 en ventana X11 960×544. Estas pruebas siguen exigidas. La ISO F1 canónica histórica SHA `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986` no se reconstruyó esta vez.

Comando de inspección privado, con carpeta fuera del repositorio, y nombre nuevo:

```bash
python tools/f2_tuika_proteger_subregiones.py \
  --iso-usa /PRIVATE/CLADUN_USA_original.iso \
  --reporte-privado /PRIVATE/TUIKA_SUBREGIONES_NUEVO.json
```

## Invariantes y siguiente acción

Protegidos: 9.237 entradas del corpus, 2.721 glifos originales, 19 nuevos sin activar blanco predeterminado (`white_new_ink=False`), 349 PSPFS, 4 DSARC, 4.524 sustituciones SCRIPT.DAT aplazadas, 51.705 comandos y 46.308 no textuales, 1.625 comienzos; `--event-safe-only` obligatorio. Ningún recurso comercial/versionado alterado. PR #7 DRAFT sin merge. F2 aún abierta; F3 intro inglesa, F4 scripts, F5 QA y F6 BPS+EXE integrales pendientes. Solo tras A/B real se evaluaría, con máscara y QA, si puede traducirse una zona concreta. Recursividad obligatoria del relevo: `prompts/SIGUIENTE_TAREA.md`.
