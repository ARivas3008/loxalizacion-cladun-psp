# CLADUN ES — F4 R14: manifiesto de nueve sondas y preflight seguro PPSSPP oficial 1.20.4

**Corte: 23/11/2026. Estado:** evidencia A de ISO auténtica, B de pruebas sintéticas y **C NO EJECUTADA**. No se modifica la ISO ni se altera ningún evento, gráfico, fuente o archivo comercial.

## 1. Autenticación de datos originales y sondas exactas

ISO USA original **305.496.064 bytes** SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. `SCRIPT.DAT` SHA256 `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`; `SCRIPT.TBL` SHA256 `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`. **1.625 scripts, 51.705 comandos, 46.308 no textuales.** La función pura `build_manifest` pasó sobre datos auténticos extraídos con parser independiente de ISO9660/PSPFS/DSARC; el informe privado solo de metadatos tiene SHA256 `4b979163721dea3ba539c601f85ba7d449eb31e3f4807cb99ef72b0e5b63ab62`.

| Bloque/orden | Offset SCRIPT.DAT | Op | ID comando | Argumento u32 | Bloque si −100 | Bloque si literal |
|---|---:|---|---:|---:|---:|---:|
| 20/20 | 7420 | 0x0A | 818 | 100100 | 757 | 758 |
| 757/2 | 218095 | 0x0A | 8 | 100200 | 758 | 764 |
| 758/1 | 218133 | 0x0C | 18 | 100290 | 759 | 765 |
| 758/415 | 223351 | 0x0C | 523 | 100 | no coincide | 89 |
| 758/416 | 223360 | 0x0A | 525 | 100201 | 760 | 766 |
| 759/23 | 223602 | 0x0C | 573 | 100 | no coincide | 89 |
| 760/1 | 223637 | 0x0C | 7 | 100291 | 761 | no coincide |
| 760/336 | 227968 | 0x0C | 413 | 100 | no coincide | 89 |
| 761/23 | 228194 | 0x0C | 457 | 100 | no coincide | 89 |

**Todos los offsets son del SCRIPT.DAT descomprimido, no direcciones RAM.** Esas nueve observaciones combinan cinco candidatos de enlace y cuatro casos `0x0C` con argumento `100`. El ID literal `100` sí existe en SCRIPT.TBL (bloque 89), mientras que al restar 100 daría ID0 ausente; ello es únicamente un contraste numérico. Ni las cinco conexiones ni el significado de `100` están confirmados por PSP MIPS.

Comando reproducible únicamente con ISO propia fuera del repositorio:

```bash
python tools/f4_r14_manifest_sondas.py --iso-original /PRIVADO/Cladun_USA_original.iso --reporte-privado /PRIVADO/R14_SONDAS_NUEVO.json
python -m unittest discover -s tests -p 'test_f4_r14*.py' -v
```

## 2. Error técnico descubierto: campos reales del protocolo oficial v1.20.4

Se consultó directamente el tag **hrydgard/ppsspp v1.20.4** (no el `master` posterior): `Core/Debugger/WebSocket/GameSubscriber.cpp`, `WebSocket.cpp`, `MemorySubscriber.cpp`, `CPUCoreSubscriber.cpp` y `BreakpointSubscriber.cpp`. En v1.20.4, la respuesta al evento `version` contiene **`name` y `version`, no PID ni ruta de ISO**. No usar documentación más reciente para atribuir esos campos a v1.20.4. La ruta de WebSocket es `/debugger` con subprotocolo `debugger.ppsspp.org`; `game.status` comunica el ID de juego y `memory.read`/breakpoints están implementados, aunque no se ejercitaron con Cladun.

Para suplir la limitación sin confiar solo en un puerto, se creó `tools/f4_r14_ppsspp_preflight.py`. Antes de cualquier captura exige hash SHA256 exacto de ISO USA y AppImage oficial; después inspecciona `/proc/PID/stat` (starttime), `/proc/PID/exe` y `APPIMAGE`, compara el inode de la ISO con los descriptores abiertos `/proc/PID/fd`, y cruza inodes de sockets TCP LISTEN con `/proc/net/tcp*` y el PID. Finalmente establece una conexión WS **solo lectura** y solicita `version` (v1.20.4) y `game.status` (disc ID NPUH10072). Repite identidad del proceso para detectar cambio de starttime. No escribe RAM, no instala breakpoints, no hace capturas; un preflight positivo sería **procedencia, no traza MIPS de los eventos**.

Ejemplo, solo si realmente se dispone del AppImage con hash autenticado y proceso abierto:

```bash
python -m pip install websocket-client
python tools/f4_r14_ppsspp_preflight.py --iso-original /PRIVADO/Cladun_USA_original.iso --appimage /PRIVADO/PPSSPP-v1.20.4-anylinux-x86_64.AppImage --pid PID_REAL --port 24192 --reporte-privado /PRIVADO/R15_PPSSPP_PROCEDENCIA_NUEVO.json
```

El hash histórico exigido del AppImage es `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`; **no pudo comprobarse contra un archivo descargado en R14**, porque no está disponible. En una ejecución real debe validarse antes de aceptar la identidad. El intento real de preflight en este turno falló con exit code 1: `Official PPSSPP AppImage absent or hash differs`. Correctamente **NO creó** reporte C.

## 3. Pruebas B, controles de cierre y siguientes pasos

**36 tests B sintéticos PASS local**: 16 del manifiesto de comandos y argumentos; 13 de `/proc` y socket con fixtures falsos; 7 del protocolo WS con respuestas simuladas y rechazo de errores. Los tests no juegan Cladun. Se añadió Q052 (procedencia PPSSPP v1.20.4 y FD ISO) y Q053 (ejecución real de las nueve sondas) como **NOT_RUN**. La matriz pasa a 53 casos definidos, todavía no universo completo.

**Pendientes:** PPSSPP oficial 1.20.4 en este entorno; identificar desde RAM real la ubicación del SCRIPT.DAT descomprimido; determinar por observación real cuál de 757/758 se ejecuta, significado del argumento 100 en 0x0C y retornos; localizar frase inglesa de prólogo y textura/GE; TUIKA combates; 19 glifos multicontesto; 4.524 eventos variables; 85 de demo1001; QA de juego y BPS/EXE final.

**Prohibiciones conservadas:** `--event-safe-only`, `white_new_ink=False`, conservar los 2.721 glifos originales y 19 A1–B3, no recolorar CLUT2 global, no subir ISO/IMY/FONT/EBOOT/BPS con contenido comercial ni capturas/dumps RAM al GitHub público. PR #7 continúa DRAFT y NO MERGED. T/G/R/Q siguen sin alcanzar 100%.
