# F2 Cladun ES — Previsualización auténtica de recursos SYSGRA y texto inglés incrustado (22/11/2026)

**Estado F2: ABIERTA.** Este relevo generó una previsualización PRIVADA de los gráficos originales; NO es captura de PPSSPP, no demuestra contexto de ejecución ni traza RAM→GE→VRAM. No se instaló ni ejecutó PPSSPP 1.20.4 en el entorno actual.

## Entrada verificada e imagen generada

Desde la ISO USA auténtica del usuario de **305496064 bytes**, SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`, se utilizó `SYSGRA.ARC` (93696 bytes, 27 entradas DSARC, SHA-256 `63d9443084a2aeab8c2a3f79aebdb130eaf6c5d2e86f8be51346d7458ab81854`). Se reconstruyeron los 27 IMY en memoria, se aplicó el orden original de teselas PSP **16 bytes × 8 filas**, las paletas RGBA almacenadas y el orden de nibbles de textura 4 bpp. Los cuatro `PALETE_0...3.IMY` tipo `0x84` se presentan como 256 muestras de su tabla de colores, NO como sprites del juego.

Archivos **PRIVADOS** fuera de GitHub (incluyen arte original del juego):
- Atlas estático: `Cladun_F2_Atlas_SYSGRA_27_Previsualizacion_Privada_NO_PPSSPP_2026-11-22.png`, **177957 bytes**, SHA-256 `947f7a0b2ae98a879dc57fd5c6d8dc7b655cf6b80af3389073fcab5fc4e7ed7f`.
- Detalle de texto: `Cladun_F2_TUIKA_MES_Texto_Embebido_Previsualizacion_Privada.png`, **13731 bytes**, SHA-256 `d2ecd78a2a816c49d7f4c79f3a744c3760b510764883603157d45a8861eaedcb`.
- Manifiesto privado (sin bytes de arte): `Cladun_F2_Previsualizacion_SYSGRA_Manifest_PRIVADO_2026-11-22.json`, SHA-256 `a4e28f2fa9c055efb0a445625158213a1a9bb031a357ede43f16185e0a2be6ec`.

No se han añadido esos PNG a GitHub. **No llamarlos capturas de PPSSPP.**

## Nuevo hallazgo de localización: inglés incrustado en una textura

El recurso auténtico `TUIKA_MES.IMY` (SHA-256 de bytes comprimidos `c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127`) muestra frases inglesas **dibujadas directamente como píxeles**: «Gamble Merchant LV.», «Angel Guard LV.», «Demon Magic LV.», «Nullified traps!», «Scattered G!», «Replenished HP for all!», «Recovered SP!», «Attack all enemies on screen!» y «No special attack». Esto es evidencia de **texto gráfico pendiente de estudiar**, más allá de los **9237 registros del corpus**. No se atribuye ninguna escena de juego concreta sin PPSSPP.

Otros recursos, visibles solo como atlas de archivo:
- `KITAJIMA_KARI.IMY`: formas de botones de control; existe prueba histórica por sonda magenta en la pantalla CONTROLES, pero **sin nuevo gameplay en este relevo**.
- `SYS1.IMY`: numerosos iconos coloridos y símbolos; uso en HUD o combate **sin demostrar**.
- `MAHO_ST.IMY`: rótulos pixelados «LV», «Mana», «HP», «SP», «ATK», «DEF», «CRI», «BRK», «Walk» y «Run»; uso real **sin demostrar**.
- `DAMAGE.IMY`: dígitos y símbolos gráficos; uso real **sin demostrar**.

Para adaptar al español una cadena como «Replenished HP for all!» será necesaria **localización de textura** además de texto CP932 si el gráfico se dibuja en el juego. NO sustituir recursos ni alterar la paleta hasta probar presencia real y comprobar los 26 vecinos DSARC y los 348 PSPFS intactos.

## Código, control de fugas y pruebas

Nueva herramienta `tools/f2_previsualizar_sysgra_privado.py`: comando `python tools/f2_previsualizar_sysgra_privado.py --iso-usa /PRIVATE/USA.iso --salida-privada /PRIVATE/atlas-nuevo.png`. Exige ISO exacta por SHA/size, valida las 27 entradas del contenedor, orden PSP, paletas, posición original de nibbles, produce un PNG **solo en ruta absoluta fuera del checkout**, rechaza symlinks hacia el repositorio y sobrescritura de evidencias. Pillow se usa solo al crear la imagen privada; tests Python de algoritmos no lo requieren. Nuevas **17 pruebas sintéticas**: `tests/test_f2_previsualizar_sysgra_privado.py`.

Commit `a440785480a4fa8eee8bfb68c47ee0d065c3e71b`; GitHub Actions `45045487042` (push) y `45045491994` (PR) ambas **SUCCESS**. **291 tests Python** aprobados, además de Go, integridad de corpus/preflight y compilación Windows pública. NO prueban gameplay ni PPSSPP.

## Bloqueos y continuidad

La terminal sigue sin resolver `github.com` (`git fetch origin` y `git pull --ff-only` fallan), el AppImage PPSSPP 1.20.4 no está instalado y el intento de descarga oficial no tuvo éxito; F1 ISO canónica SHA `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986` no está disponible localmente. Nuevos PNG de gameplay PPSSPP: **0**. Nuevos dumps GE: **0**. PC MIPS RAM/VRAM de iconos demostrados: **0**. Los 19 glifos multicontesto y la regresión X11 Opciones 960×544 siguen pendientes.

No se modificó la ISO fuente, el corpus de 9237 textos, el integrador, el código de fuente ni `white_new_ink=False`; se preservó `--event-safe-only`. PR #7 sigue **DRAFT**; F3 intro inglesa, F4 4524 textos script pospuestos, F5 QA del juego y F6 BPS/EXE final permanecen pendientes.

Véanse `reports/RESULTADO_F2_PREVISUALIZACION_SYSGRA_2026-11-22.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json` y el prompt completo regenerado `prompts/SIGUIENTE_TAREA.md`.
