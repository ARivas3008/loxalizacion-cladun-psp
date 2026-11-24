# CLADUN ES — R15: localizador de SCRIPT.DAT en RAM sin escrituras (23/11/2026)

**Estado real:** A ISO USA auténtica en modo lectura + B 33 tests nuevos + **C NO EJECUTADA**. No se encontró el emulador oficial 1.20.4 en el entorno. La descarga del AppImage falló y tampoco funcionó la descarga alternativa. No se han obtenido direcciones RAM, PC MIPS ni capturas de juego. Los 4.524 diálogos variables siguen protegidos.

## 1. Autenticidad y 9 huellas estrictamente únicas

ISO USA original 305.496.064 bytes, SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. SCRIPT.DAT extraído privadamente, 633.344 bytes, SHA256 `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`. Se revalidó la extracción real independiente ISO9660 → PSPFS 349 → SCRIPT.SDT DSARC → SCRIPT.DAT/TBL: **1.625 bloques, 51.705 comandos, 46.308 no textuales**. Ninguna fuente original fue modificada.

Los nueve offsets del manifiesto R14 `7420, 218095, 218133, 223351, 223360, 223602, 223637, 227968, 228194` permiten obtener ventanas de **32 bytes**, cada una aparece **exactamente una vez en los 633.344 bytes de SCRIPT.DAT auténtico**. Sus SHA256, sin los bytes originales, quedan en `reports/F4_R15_HUELLAS_RAM_2026-11-23.json`. Informe privado solo metadatos SHA256 `5f86438b2ff6b670a663f41630394359f7458bb37b9341f78d564fb12e8a8554`. Las huellas no son PCs ni direcciones físicas PSP y su unicidad **dentro del archivo** no prueba unicidad en la RAM de PPSSPP.

## 2. Comprobador de lectura RAM, sin mutaciones

`tools/f4_r15_localizador_ram.py` obtiene los nueve fragmentos solo a partir de SCRIPT.DAT original SHA exacto. Su ejecución real se bloquea si faltan la ISO exacta, el AppImage oficial con hash exacto, PID/starttime, descriptor FD ISO en el proceso, socket del mismo proceso, WebSocket `debugger.ppsspp.org`, `version v1.20.4` y `game.status NPUH10072`. Reutiliza `tools/f4_r14_ppsspp_preflight.py`.

El protocolo **oficial PPSSPP 1.20.4** en `Core/Debugger/WebSocket/MemorySubscriber.cpp` implementa `memory.read` con parámetros `address`, `size` y respuesta `base64`. El escáner envía únicamente eventos `memory.read`, con ticket, sin `memory.write`, sin instalación de breakpoints y sin publicar bytes. Limita el intervalo solicitado explícitamente por el operador a **32 MiB** en direcciones PSP `0x08000000..0x0C000000`, lectura 4–64 KiB en fragmentos y solapamiento 31 bytes entre lecturas para que una firma que cruce un límite de fragmento no se pierda.

Cada coincidencia produce un **candidato** de base de SCRIPT.DAT, nunca una dirección supuesta. Solo si al menos tres huellas señalan la misma base se verifican todas y se calcula SHA256 de la **imagen continua completa** de 633.344 bytes en RAM. Una copia idéntica del archivo en RAM probaría su presencia, **no que una instrucción haya sido ejecutada, ni llamadas/retornos o validación de eventos**. Si el juego carga scripts por bloques, comprime o transforma datos en RAM, puede no encontrarse una copia completa; resultado negativo NO demuestra ausencia de contenido ni invalida ID+100.

Cuidado: el código oficial de `memory.read` utiliza un bloqueo de memoria/CPU; aunque no escribe bytes, puede pausar momentáneamente el emulador. Se recomienda una ventana pequeña y concreta, no escaneo indiscriminado durante combate.

## 3. Evidencia B y comandos exactos

En el entorno real R15 ejecuté `python -m unittest discover -s tests -p 'test_f4_r15*' -v`: **33 tests sintéticos PASS**. Los 87 tests disponibles en el checkout parcial (R13/R14/R15) también PASS, **no equivalen a la suite completa del repositorio**. Las pruebas incluyen localización sintética de la copia, firmas que cruzan fragmentos, SHA256 completo positivo y negativo, falsos positivos descartados, límites de RAM, lecturas incompletas, datos base64 inválidos, error de WS y garantía de que no hay escrituras.

En checkout completo, con tu propia ISO original, modo estático A:
```bash
python tools/f4_r15_localizador_ram.py --modo preparar \
  --iso-original /PRIVADO/Cladun_USA_original.iso \
  --reporte-privado /PRIVADO/R16_HUELLAS_NUEVO.json
python -m unittest discover -s tests -p 'test_f4_r15_localizador_ram.py' -v
```

Únicamente DESPUÉS de obtener AppImage oficial y sesión autenticada (Q052), elegir explícitamente un intervalo RAM válido, comprobado con el depurador, y ejecutar:
```bash
python tools/f4_r15_localizador_ram.py --modo escanear \
  --iso-original /PRIVADO/Cladun_USA_original.iso \
  --appimage /PRIVADO/PPSSPP-v1.20.4-anylinux-x86_64.AppImage \
  --pid PID_REAL --port 24192 --ram-start INICIO_HEX --ram-end FIN_HEX \
  --reporte-privado /PRIVADO/R16_RAM_NUEVO.json
```
Estos parámetros no son direcciones encontradas. No copiar un ejemplo como base RAM verificada; medir rangos del proceso real.

## 4. Descarga oficial, bloqueos y rutas siguientes

GitHub Release oficial `https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4` confirmó por metadatos del propio archivo el AppImage Linux x86_64: **50.689.748 bytes**, SHA256 `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`. **No se consiguió descargarlo**: terminal sin DNS github.com, no hay ejecutable PPSSPP instalado ni evidencia C nueva. Q054 (buscar imagen RAM) y Q055 (observar ejecución MIPS después de ubicarla) se incorporan como `NOT_RUN`, matriz **55 casos** definidos, todavía no universo de betatesting cerrado.

Siguiente secuencia: obtener PPSSPP oficial y verificar byte a byte, ISO SHA exacta, Q052 procedimiento PID/FD/WS, luego Q054 localización real en RAM; si localización da resultado SHA correcto, colocar breakpoints solo con dirección PC **observada** y probar Q050/Q051/Q053/Q055 sobre la secuencia 20→757→758→760 y retornos. Si no hay copia continua, inspeccionar carga segmentada sin inferir que no existen scripts. F3 sigue sin procedencia de texto inglés del prólogo, F2 TUIKA combate y 19 glifos multicontesto pendientes; no se libera ningún texto de longitud variable.

Conservar `--event-safe-only`, `white_new_ink=False`, atlas antiguo y recursos PSPFS ajenos. No publicar ISO/EBOOT/DATA.DAT/IMY/FONT, audio, capturas, RAM/GE/VRAM o BPS con assets comerciales. PR #7 DRAFT, no merge. T/G/R/Q `cierre_100=false`.
