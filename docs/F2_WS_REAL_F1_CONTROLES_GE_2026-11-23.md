# F2 — PPSSPP 1.20.4 REAL con WebSocket, F1 Opciones y Controles (23/11/2026)

**Estado: F2 ABIERTA.** En este relevo se corrigió el bloqueo local que impedía arrancar el servidor WebSocket de PPSSPP 1.20.4, se enlazó su socket TCP con el PID que mantenía abierto el archivo ISO y se obtuvieron capturas X11 y volcados GE reales tanto en USA como en la ISO española F1. Los 19 glifos solo se observaron parcialmente, y TUIKA no se rastreó desde su recurso a la GPU. F3–F6 siguen pendientes. El PR #7 debe permanecer DRAFT.

## A. Verificación de soportes comerciales sin publicarlos

- ISO original USA del usuario: **305.496.064 bytes**, SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.
- PPSSPP oficial AppImage Linux x86_64 v1.20.4: **50.689.748 bytes**, SHA256 `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`. Se usó el ejecutable intacto extraído de la AppImage verificada, en Xvfb 1280×720, ventana X11 960×544, renderizador por software.
- La sonda TUIKA regenerada sigue teniendo SHA256 `b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa`; solo tres bytes cambiados, con 348 vecinos PSPFS y 26 DSARC idénticos. **No se produjo nueva escena de gameplay A/B de TUIKA.** El magenta del splash SYSTEM PRiSM ya se encontraba en la ISO original (control negativo de relevo anterior).
- Se reconstruyó la candidata **F1 española**, **306.456.576 bytes** (más grande por reubicación append-only de contenedores, no por alteración de comandos de eventos) y SHA256 `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`, exactamente igual a la F1 canónica previa. Se mantuvo `--experimental-parcial --event-safe-only`: 3.724 sustituciones insertadas y 4.524 cambios de script diferidos. Sin subir ISO, BPS, FONT, imágenes de juego ni dumps comerciales a GitHub.

## B. Hallazgo de la causa del WebSocket ausente

La aplicación empaquetada usa un lanzador **Sharun**. En este contenedor Sharun descartaba por defecto el `LD_PRELOAD` privado que dirigía `SDL_AUDIODRIVER` a `dummy`. El proceso SDL fallaba al iniciar audio y moría **antes** de activar el depurador. La variable de Sharun `SHARUN_ALLOW_LD_PRELOAD=1` permite transmitir el shim de audio externo. Este ajuste es **específico del contenedor**, no un parche al juego ni al ejecutable PPSSPP. El archivo de configuración realmente leído por PPSSPP incluyó:

~~~ini
[Network]
RemoteDebuggerOnStartup = True
RemoteDebuggerLocal = True
RemoteISOPort = 24192
~~~

El servidor ahora escuchó realmente en el puerto TCP 24192. WebSocket oficial en `ws://127.0.0.1:24192/debugger`, subprotocolo `debugger.ppsspp.org`, devolvió `version: PPSSPP v1.20.4`, `game.status: NPUH10072 / CLADUN: This is an RPG!` y `cpu.status` con CPU ejecutándose. No atribuir esto a otros PPSSPP o entornos.

**Verificación de procedencia más estricta:** nuevo `tools/f2_ws_procedencia_ppsspp.py` lee `/proc/net/tcp` y `tcp6` con estado LISTEN `0A`, localiza inode del socket, coteja ese inode contra `/proc/<pid>/fd`, hace el handshake oficial y vuelve a comprobar PID/starttime, descriptor del **mismo inodo ISO** y SHA256. En prueba **REAL** contra F1: `websocket_listener_owned_by_same_ppsspp_pid=true`, `iso_fd_same_inode_open_before_after=true`, `argv_exact_iso_match=true`, pero `rendered_game_iso_identity_proven=false` y `mips_ram_ge_vram_chain_proven=false`. El PID observado es efímero. La ISO F1 mide **306.456.576**, no 305.496.064; un primer intento de testigo rechazó F1 por imponer equivocadamente el tamaño de USA a todos los roles, error corregido.

## C. Capturas reales de F1 por entrada PSP WebSocket

Se usaron mensajes `input.buttons.press` auténticos de PPSSPP (no falsos clics ni vídeo montado) para navegar:

1. Arranque ISO F1, título original, seleccionar `Opciones`.
2. Menú principal de Opciones: cuadro interior visible desde x aproximadamente 342 a 1097 en ventana de escritorio (≈**756 px interiores y ≈764 exteriores**), igual a dimensiones históricas F1, sin la compresión de v0.1.5.
3. Opciones en español: `Vol. efectos`, `Vol. música`, `Tipo música`, `Decimales de daño`, `Efectos círculo`, `Capturas`, `Controles`, con valores `Sí/No`. Tildes «música»/«Sí» renderizadas sin introducir espacios visibles.
4. Se navegó mediante seis `input.buttons.press("down",duration=10)` hasta `Controles` y `input.buttons.press("cross",duration=10)` para abrir.
5. Pantalla Controles: `Correr` con R, `Bloquear` con □, `Ataque` con ×, `Saltar` con ○, `Magia` con △, `Cambiar` con L; también `Por defecto` y `Fin` y ayuda `Pulsa el botón para configurar.`. **Los seis iconos son visibles en esta pantalla real**, pero eso NO valida índices de fuentes en HUD, menús, combate o la procedencia de cada sprite de botones.

Las imágenes son **capturas directas de X11** de PPSSPP, de 960×544 para el juego y adicionalmente una captura del escritorio X11. No presentarlas como `gpu.buffer.screenshot` ni como un framebuffer PSP obtenido por WS.

## D. Registros gráficos GE reales

- Durante la pantalla título USA se recibió `gpu.record.dump` con cabecera `PPSSPPGE`: **10.367 bytes**, SHA256 `6defdec107b1c35c2b87d6a90cb1786f418256eeb5d4f81a52dc9586b57587b2`, **48 registros y 10 operaciones PRIM** al analizarlos con `tools/f2_ge_dump_1204.py`.
- Durante **Controles F1**, nuevo `gpu.record.dump` autenticado: **38.546 bytes**, SHA256 `e32efb103488f70c7e656217efdb0ea09b4747b5d77ea9d5af95747412c098af`, cabecera `PPSSPPGE`, **versión 6, 398 registros, 124 PRIM**. Se identificaron en el volcado 10 referencias `TEXADDR0`, 10 `CLUTADDR`, 10 `TEXFORMAT`, 10 `CLUTFORMAT`, 14 registros `TEXTURE0` y 11 `CLUT`.
- Las direcciones son **candidatas** y su geometría/procedencia aún no vinculan por sí mismas `SYSGRA.ARC/TUIKA_MES.IMY` ni `KITAJIMA_KARI.IMY`, ni prueban una cadena MIPS→RAM→GE→VRAM completa. `gpu.buffer.screenshot` llegó a responder `Could not download output` con el renderizador actual incluso después de detener CPU; revisar `gpu.buffer.renderColor` u otro backend real en próximo relevo. El mecanismo `gpu.record.dump` sí funciona.

## E. QA y límites

Se ejecutó en checkout local del snapshot completo `python -m unittest discover -s tests -q`: **491 tests Python, OK (uno omitido)**, con nueve tests sintéticos nuevos de socket+PID. `python tools/verificar_integridad.py --raiz .` y `python tools/verificar_borrador_es.py` sin errores: 9.237 registros, 9.235 español, dos excepciones; `cd patcher && go test ./...` OK. Los tests sintéticos no acreditan gameplay; solo las capturas y WS/GE descritos fueron reales.

**No completado:** TUIKA A/B durante combate/habilidades; asociación exacta de 19 glifos y fuente de iconos a comandos GE; signos «¿¡» en diálogos; colores amarillo/blanco multicontesto; F1 verificación de todo el juego; reparaciones F3 intro inglesa; 4.524 textos diferidos F4; QA exhaustivo F5, BPS/EXE final F6.

## F. Comandos principales de continuidad

~~~bash
# Original y PPSSPP privado, usar rutas reales y SHA autenticado
sha256sum /PRIVATE/USA.iso /PRIVATE/PPSSPP-v1.20.4-anylinux-x86_64.AppImage
# En este contenedor Sharun requería SHARUN_ALLOW_LD_PRELOAD=1 para que
# su shim de audio PRIVADO llegara al PPSSPPSDL intacto:
export SHARUN_ALLOW_LD_PRELOAD=1
export SDL_AUDIODRIVER=dummy
# verificar PID real, socket LISTEN, SHA ISO y handshake con una ISO F1 exacta
python tools/f2_ws_procedencia_ppsspp.py --pid PID_REAL --port 24192 \
  --iso-privada /PRIVATE/F1.iso --tipo f1 --informe-privado /PRIVATE/WS_PID_F1_NUEVO.json
# Seleccionar otro rol usa o sonda si corresponde, y rutas NUEVAS
python tools/f2_ge_dump_1204.py --entrada-privada /PRIVATE/GE_REAL.dump \
  --reporte-privado /PRIVATE/GE_ANALISIS_NUEVO.json
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
(cd patcher && go test ./...)
~~~

El nuevo prompt autónomo de relevo permanece en `prompts/SIGUIENTE_TAREA.md` y exige generar otro. **F2 queda abierta y PR #7 DRAFT hasta pruebas de habilidades y TUIKA auténticas.**
