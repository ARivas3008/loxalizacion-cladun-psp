# Cladun F2 — Sonda cromática auténtica TUIKA_MES.IMY, solo 3 bytes, sin PPSSPP (22/11/2026)

**F2 continúa ABIERTA.** Se ejecutó una sonda privada sobre la **ISO USA original real**, no una emulación ni un montaje. La meta fue preparar un control positivo/negativo para probar en PPSSPP si el juego selecciona los rótulos ingleses incrustados como píxeles en `SYSGRA.ARC/TUIKA_MES.IMY`. La mera presencia de esas frases dentro de la textura original **NO acredita** su aparición en ninguna escena.

## Autenticación del binario real

- Archivo 7z aportado por el usuario: entrada ISO extraída por libarchive, **305496064 bytes**. SHA-256 USA original **completo**: `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.
- PSPFS **349** entradas; entrada **225 SYSGRA.ARC**: offset relativo a DATA.DAT **895488**, tamaño **93696**, SHA `63d9443084a2aeab8c2a3f79aebdb130eaf6c5d2e86f8be51346d7458ab81854`.
- DSARC **27** entradas; entrada **24 TUIKA_MES.IMY**, offset relativo a SYSGRA **78848**, tamaño **7912**, SHA `c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127`.
- Paleta IMY 16 RGBA: **índice 2** tenía RGBA **(249,251,249,255)** (tono casi blanco, opaco); la variante privada usa **(255,0,255,255)** (magenta, misma opacidad).

## Sonda realmente construida: diferencias exactas en ISO

Se copió la ISO original a otra ruta **privada** mediante apertura exclusiva, sin sobrescribir fuentes ni evidencias anteriores. Se cambiaron **exactamente 3 bytes RGB**, dejando intacto el alfa. Offset absoluto en la ISO (decimal): **114744872**, **114744873**, **114744874**, con cambios hexadecimales `F9→FF`, `FB→00`, `F9→FF`. No cambió ningún otro byte de los **305496064**. El lector comparó el contenido completo byte por byte; no es una inferencia basada solo en tamaños.

| Invariante sobre original frente a sonda | Resultado |
|---|---|
| Bytes modificados en todo el disco ISO | **3** |
| Vecinos PSPFS no tocados | **348 de 348** |
| Miembros DSARC vecinos no tocados | **26 de 26** |
| Tablas PSPFS/DSARC | **Idénticas** |
| Alfa y bytes comprimidos de TUIKA | **Sin modificación** |
| Resto de ISO9660, offsets, archivos y cabeceras | **Idéntico** |

ISO privada de sonda (NO versionar ni compartir como parche público): `cladun_tuika_rgba2_magenta_probe_20261122.iso` SHA-256 `b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa`. Nuevo SHA de miembro TUIKA `efcf4f41f57c300476e8ce54a32dea01f242dda3fbf3fb9c4e0b582bad8f5252`, nuevo SHA del contenedor SYSGRA `403f391c4b1ab2c8618ac5d098f0a4316b7fd8262ecb80f7f39a2553ec06c758`.

**Alcance:** el color cambia TODOS los píxeles que usan el índice 2 en TUIKA, no solo una frase. Su función es diagnóstico A/B para futuras capturas reales. La ISO experimental no contiene una traducción nueva, sino únicamente un marcador de tinta. La ISO original, el corpus y el integrador permanecen intactos.

Informe privado de evidencia, **solo hashes/metadatos**: `CLADUN_F2_probe_TUIKA_rgba2_INTEGRIDAD_PRIVADA_2026-11-22.json`, SHA `05287b3af776794936e5a548f351585f2413e12877fea9ac62d58292a53b438d`.

## Código, controles sintéticos y GitHub

El código de la sonda se ha publicado en `tools/f2_probe_tuika_palette_privado.py`, con `tests/test_f2_probe_tuika_palette_privado.py` (**22 pruebas sintéticas**). Valida ISO por SHA y tamaño antes de escribir, verifica descriptores PSPFS/DSARC, exige el IMY y el RGBA exactos, rechaza salida dentro de checkout/symlinks/sobrescrituras y falla ante cualquier otro byte modificado; compara 348 vecinos PSPFS y 26 vecinos DSARC. 

Comando privado reproducible:

`python tools/f2_probe_tuika_palette_privado.py --iso-usa /PRIVATE/USA.iso --salida-iso-privada /PRIVATE/TUIKA_magenta.iso --reporte-privado /PRIVATE/resultado.json`

Commit de código `ff91106a6997019bbd532c449160101df04f460a`. Dos GitHub Actions de código `45051308641` (push) y `45051315010` (pull request) **SUCCESS**: **313 pruebas Python**, controles de integridad/preinserción, Go y compilación pública Windows sin BPS. El binario comercial no está en CI. **La construcción auténtica de la ISO experimental se ejecutó en el entorno privado con script independiente; las pruebas del código publicado en CI son sintéticas.** No confundir lo uno con lo otro.

## Límite actual: F2 no está cerrada

PPSSPP oficial 1.20.4 AppImage **NO instalado**, descarga `github.com` desde terminal bloqueada por DNS. No está disponible la ISO F1 canónica anterior. No se ejecutó PPSSPP, no se adquirió ninguna captura de juego nueva, ni dump GPU auténtico, ni MIPS PC propio de iconos, ni correlación RAM→GE→VRAM. No están comprobados visualmente los 19 glifos ni regresada Opciones F1 X11 960×544 en este relevo.

**Siguiente paso experimental:** comparar original USA y sonda en la misma escena real de juego en PPSSPP 1.20.4; verificar captura A/B, tinta magenta únicamente donde aparezca TUIKA, comprobar otros rótulos con controles negativos y correlacionar el recurso comprimido con RAM MIPS, GE y VRAM. Solo entonces planificar repintado español con su atlas/CLUT y recomprensión sin desplazar recursos. Sin material comercial en GitHub; no modificar `white_new_ink=False`, `--event-safe-only` ni 9237 registros. PR #7 sigue DRAFT, F3–F6 continúan pendientes.

Informes: `reports/RESULTADO_F2_SONDA_TUIKA_CLUT_2026-11-22.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`; nuevo relevo recursivo: `prompts/SIGUIENTE_TAREA.md`.
