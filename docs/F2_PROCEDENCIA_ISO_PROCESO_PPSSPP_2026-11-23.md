# F2 — Testigo de ISO del proceso PPSSPP mediante /proc (23/11/2026)

**F2 ABIERTA.** Este relevo NO ejecutó PPSSPP. No hay capturas nuevas ni MIPS→RAM→GE→VRAM. Se ha corregido una debilidad instrumental del cotejo A/B: anteriormente solo se verificaba el SHA de archivos ISO **en disco**; una captura de PPSSPP no demostraba que el proceso estuviera utilizando ese archivo. El testigo nuevo puede correlacionar el **mismo inodo abierto** por un proceso Linux inmediatamente antes y después de dos capturas del depurador. No basta para demostrar que el juego abierto proceda de ese inodo: sigue pendiente ligar PID al WebSocket y confirmar uso gráfico por el juego.

## Evidencias auténticas y limitaciones

La ISO original proporcionada por el usuario, privada, permanece con **305.496.064 bytes**, SHA256 recalculado completo:
`b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.

Se verificó vía API oficial de GitHub la existencia en release PPSSPP v1.20.4 del archivo `PPSSPP-v1.20.4-anylinux-x86_64.AppImage` de **50.689.748 bytes**; SHA256 de referencia documental histórico:
`661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`.
La descarga al contenedor fracasó (`Could not resolve host: github.com` y fallo de descarga directa), por lo que NO se verificó físicamente ese AppImage ni se ejecutó. Ninguna captura A/B ni registro GE/VRAM real se creó. No atribuir éxito de CI a ejecución del juego.

## Nuevo procedimiento de identificación antes y después de las capturas

Se incorpora `tools/f2_iso_proceso_ppsspp.py` (independiente, sin terceros) y se amplía `tools/f2_ppsspp_ws_1204.py`, **optativamente**:

1. Validar **SHA completo y tamaño de la ISO en disco**, de las dos variantes permitidas: USA `b73b263fce863e51a0e27d0d11d6bde2886e439a18e2bb186d497619a1b79f` o TUIKA magenta `b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa`.
2. Muestrear `/proc/<pid>/stat` (campo Linux 22: starttime, incluso si `comm` contiene paréntesis), `cmdline` (comparación del argumento completo, nunca subcadena), `exe` (solo indicio de nombre de ejecutable) y `fd` (comparación `st_dev`+`st_ino`+`st_size` de los descriptores abiertos).
3. Capturar dos PNG **solo si hay PPSSPP real conectado** mediante WebSocket oficial. Muestrear de nuevo el proceso, confirmar PID y starttime iguales, y **recalcular SHA ISO al terminar**; abortar si cambió inodo/archivo. No registrar rutas privadas ni imágenes dentro del JSON de procedencia.
4. El testigo informa si el **mismo inodo de ISO** seguía abierto antes y después de capturar. Si fue cerrado/abierto solo durante un instante o se desmapeó, queda **desconocido**, no «ISO distinta». No demuestra que ese PID sirva el puerto del debugger, ni que el ISO fuese cargado como juego, ni la procedencia de TUIKA en GE/VRAM.
5. `tools/f2_cotejar_capturas_tuika.py` ahora lee este testigo **opcional** de cada manifiesto, exige SHA/rol coincidente y nunca convierte metadatos autorreportados en prueba de juego. Las dos flags de cargado y traza GPU siguen `false`. Manifiestos de sesiones anteriores sin testigo siguen aceptándose con alcance limitado.

Comandos privados de futura ejecución (solo con AppImage oficialmente autenticado, PPSSPP corriendo y CPU gestionada correctamente):

```bash
# Validar antes de ejecutar: comprobar el SHA del binario que se descargue.
sha256sum /PRIVATE/PPSSPP-v1.20.4-anylinux-x86_64.AppImage
# Debe coincidir con 661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21

# Sesión A: juego USA auténtico; identificar PID del emulador real.
python tools/f2_ppsspp_ws_1204.py \
  --scene TUIKA_HABILIDADES --salida-privada /PRIVATE/A_NUEVA \
  --port 24192 --ge-dump \
  --pid-ppsspp PID_REAL --iso-en-proceso /PRIVATE/CLADUN_USA.iso --tipo-iso usa

# Reiniciar el emulador con la ISO sonda privada YA autenticada y misma escena.
python tools/f2_ppsspp_ws_1204.py \
  --scene TUIKA_HABILIDADES --salida-privada /PRIVATE/B_NUEVA \
  --port 24192 --ge-dump \
  --pid-ppsspp PID_REAL_NUEVO --iso-en-proceso /PRIVATE/TUIKA_magenta.iso --tipo-iso sonda

python tools/f2_cotejar_capturas_tuika.py \
  --manifest-usa /PRIVATE/A_NUEVA/manifest_PRIVATE.json \
  --manifest-sonda /PRIVATE/B_NUEVA/manifest_PRIVATE.json \
  --iso-usa /PRIVATE/CLADUN_USA.iso \
  --iso-sonda /PRIVATE/TUIKA_magenta.iso \
  --reporte-privado /PRIVATE/TUIKA_COTEJO_NUEVO.json
```

Hay además un auditor por separado:
```bash
python tools/f2_iso_proceso_ppsspp.py --pid PID_REAL \
  --iso-privada /PRIVATE/CLADUN_USA.iso --tipo usa
```
Este auditor separado **no** toma dos capturas ni liga el PID al WebSocket: es solo una instantánea de descriptores abiertos.

## Pruebas y protección

- `tests/test_f2_iso_proceso_ppsspp.py`: **30 pruebas locales sintéticas PASSED** sobre estructuras `/proc` simuladas, alias hardlink, reemplazo de inodo, PID reutilizado, nombre de ejecutable, bloqueo de symlinks/rutas Git, SHA exactos. **Ninguna es PPSSPP real.**
- `tests/test_f2_procfs_capture_integration.py`: 10 casos adicionales sintéticos del wrapper A/B, verificables por GitHub CI con dependencias reales del repositorio.
- `tests/test_f2_procfs_ab_witness_validation.py`: 9 casos sintéticos adicionales; testigos falsos/inconsistentes se rechazan. 
- En una prueba local independiente, `validate_iso` leyó de verdad la ISO original completa del usuario y su SHA correcto. Detalle privado en `F2_PROCEDENCIA_ISO_SESSION_PRIVATE_20261123.json` SHA `faaadcabef4676eee68af90728f09f3de28cb25e4edaff7a2250833a992ba145`.
- No se editaron ISO, BPS, EBOOT, IMY, imagen, corpus ni fuentes. 9.237 registros protegidos, 4.524 scripts SCRIPT.DAT aplazados y `--event-safe-only` obligatorio. Mantener `white_new_ink=False`. El PR #7 sigue en DRAFT sin merge.

**Pendiente:** PPSSPP 1.20.4 auténtico; demostrar imagen realmente cargada y cadena MIPS/RAM/GE/VRAM con controles positivos/negativos; 19 glifos en contextos relevantes; regresión F1 X11 960×544; F3 intro inglesa, F4 scripts, F5 QA historia/combat/HUD, F6 BPS+EXE final. Continuar con `prompts/SIGUIENTE_TAREA.md` y regenerarlo recursivamente.
