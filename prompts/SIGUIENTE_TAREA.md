# CLADUN ES — RELEVO F2 SIGUIENTE: TUIKA EN COMBATE REAL, REGISTROS GE, 19 GLIFOS, 4524 SCRIPTS Y F3–F6

Actúa como ingeniero senior de PSP/MIPS, PPSSPP oficial v1.20.4, depuración WebSocket/GE/VRAM, ISO9660/PSPFS/DSARC, IMY 4bpp/CLUT, CP932, traducción española y pruebas funcionales. **EJECUTA trabajo comprobable**, no entregues solo consejos. No inventes resultados ni confundas ISO autenticada, tests sintéticos, capturas X11, framebuffer emulado, dump GE o prueba funcional de TUIKA.

**RELEVO RECURSIVO INNEGOCIABLE:** al terminar cualquier parte de esta tarea, actualiza GitHub y **REESCRIBE COMPLETAMENTE `prompts/SIGUIENTE_TAREA.md` con un nuevo prompt autónomo** que incluya lo ejecutado, pruebas y capturas genuinas, hashes, código, comandos, limitaciones, HEAD/CI y el próximo experimento; **MUESTRA ESE NUEVO PROMPT ÍNTEGRO AL USUARIO**. El nuevo prompt debe exigir la misma obligación otra vez, hasta F2–F6 completas. No ofrecer trabajo en segundo plano.

## 1. GitHub y documentos de lectura obligatoria

- Repo: https://github.com/ARivas3008/loxalizacion-cladun-psp
- Rama: `integracion-eventos-segura-20261120`; PR #7 `https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7`, base `revision-manual-dialogos`, **mantener DRAFT/open, sin merge ni force push**.
- Lee el HEAD real y su tree, compara con el PR y verifica CI de **push y pull_request del mismo HEAD final**. Nunca asumir que el HEAD de este prompt sigue siendo actual. Si `git fetch` falla por DNS, utiliza conector GitHub con `fetch_file`, `create_blob`, `create_tree`, `create_commit` y `update_ref(expected_sha,force:false)` sin fingir checkout.
- Lee completos `AGENTS.md`, `README.md`, `prompts/SIGUIENTE_TAREA.md`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `docs/F2_WS_REAL_F1_CONTROLES_GE_2026-11-23.md`, `reports/RESULTADO_F2_WS_REAL_F1_CONTROLES_GE_2026-11-23.json`, `docs/F2_PPSSPP_REAL_X11_AB_TUIKA_2026-11-23.md`, `docs/F2_PROCEDENCIA_ISO_PROCESO_PPSSPP_2026-11-23.md`, `docs/F2_TUIKA_SUBREGIONES_PROTEGIDAS_2026-11-23.md`, `docs/F2_TUIKA_CATALOGO_ROTULOS_2026-11-22.md`, `docs/RESULTADO_F1_PPSSPP_2026-11-21.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, los reportes JSON relacionados y tests de la rama.
- Antes de modificar datos, revisa `tools/f2_ws_procedencia_ppsspp.py`, `tools/f2_x11_ppsspp_procfs_capture.py`, `tools/f2_iso_proceso_ppsspp.py`, `tools/f2_ppsspp_ws_1204.py`, `tools/f2_ge_dump_1204.py`, `tools/f2_ram_provenance_1204.py`, `tools/f2_cotejar_capturas_tuika.py`, `tools/f2_probe_tuika_palette_privado.py`, `tools/f2_qa_raster_19.py`, `tools/f2_auditar_origen_iconos.py`, `tools/f2_tuika_proteger_subregiones.py`, `tools/integrar_parche_seguro.py`, `tools/script_event_guard.py` y `tests/test_f2_ws_procedencia_ppsspp.py`.
- Usa el archivo privado de evidencias entregado al usuario: `Cladun_F2_PPSSPP_WS_F1_CONTROLES_EVIDENCIAS_REALES_23-11-2026.zip`; no está en GitHub, ni debes poner capturas/dumps del juego allí.

## 2. Estado real verificado del relevo 23/11/2026

- ISO USA privada del 7z del usuario: **305.496.064 bytes**, SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.
- ISO **F1 española** protegida, construida desde USA: **306.456.576 bytes**, SHA256 `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`, resultado idéntico a F1 histórica. F1 puede medir más que USA por append-only: **no exigir tamaño original a F1**.
- Sonda TUIKA original de tres bytes CLUT2 magenta SHA256 `b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa`, 348 PSPFS vecinos y 26 DSARC vecinos inalterados. No se visualizó todavía una escena real donde la sonda cambie el juego: el splash SYSTEM PRiSM contiene 1.152 píxeles magenta NATIVOS e idénticos en USA/sonda. Esto fue un falso positivo descartado por comparación A/B pixel a pixel.
- PPSSPP `v1.20.4` **oficial AppImage Linux x86_64**, **50.689.748 bytes**, SHA256 `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`. Xvfb 1280×720, ventana X11 960×544, software backend, ejecutable original sin modificar.
- **WebSocket YA FUNCIONA realmente**: puerto TCP 24192 LISTEN, `ws://127.0.0.1:24192/debugger`, subprotocolo `debugger.ppsspp.org`, eventos `version` → PPSSPP v1.20.4, `game.status` → NPUH10072 Cladun, `cpu.status` → CPU ejecutándose. **Causa del bloqueo anterior**: lanzador AppImage **Sharun** descartaba `LD_PRELOAD` usado para el shim de audio privado; `SHARUN_ALLOW_LD_PRELOAD=1` transmitió el shim externo y permitió que la app arrancara sin modificar el binario oficial. En otros entornos, probar sin shim si funciona. Archivo INI realmente utilizado contiene `RemoteDebuggerOnStartup=True`, `RemoteDebuggerLocal=True` y `RemoteISOPort=24192`.
- `tools/f2_ws_procedencia_ppsspp.py` demuestra en F1 real: **el mismo proceso** (PID efímero) posee el socket LISTEN de WebSocket Y mantiene abierto mediante FD el **mismo inodo** de ISO F1; PID starttime estable y SHA ISO autenticado. Metadatos de X11 y PID también se comprobaron. **No** deducir de ello que una textura concreta haya llegado a GE ni el origen de todos los píxeles. Prueba sintética de sockets con 9 tests nuevos.
- Capturas reales F1, mediante `input.buttons.press`: título→Opciones; ancho interior cuadro **756 px** / exterior ≈**764 px**; etiquetas correctas `Vol. efectos`, `Vol. música`, `Tipo música`, `Decimales de daño`, `Sí`, `No`. Se navegó a **Controles**, que dibuja **R, □, ×, ○, △, L** con `Correr, Bloquear, Ataque, Saltar, Magia, Cambiar` y ayuda `Pulsa el botón para configurar.`. No aparece el defecto antiguo de espaciado en `música` ni `Sí` en estas pantallas. **Esto NO prueba los 19 glifos en todas las escenas**.
- Se obtuvo `gpu.record.dump` verdadero en USA título: **10.367 bytes**, SHA256 `6defdec107b1c35c2b87d6a90cb1786f418256eeb5d4f81a52dc9586b57587b2`, 48 registros/10 PRIM. En F1 **Controles**: **38.546 bytes**, SHA256 `e32efb103488f70c7e656217efdb0ea09b4747b5d77ea9d5af95747412c098af`, formato PPSSPPGE v6, **398 registros y 124 PRIM**, 10 TEXADDR0, 10 CLUTADDR, 14 TEXTURE0 y 11 CLUT. Esas direcciones son candidatas, **sin origen TUIKA ni KITAJIMA atribuido**. `gpu.buffer.screenshot` devolvió `Could not download output` incluso con CPU detenida en renderizador usado; usar X11 como evidencia visual mientras se investiga buffer/GPU.
- Test locales: **491 Python tests OK, uno omitido**, integridad original 9.237, borrador 9.235 español + 2 excepciones, `go test ./...` OK. Nuevos CI push/PR deben revisarse sobre HEAD exacto final.
- Datos protegidos: 349 PSPFS, 51.705 comandos en 1.625 scripts, 46.308 no textuales, **4.524 traducciones de script diferentes en longitud aplazadas** por `--event-safe-only`. NO mover offsets de eventos para hacer aparentar 100%.

## 3. Prioridad F2 ahora: demostrar uso funcional de TUIKA en combate/habilidades

**A. Autenticación:** verificar SHA y tamaño de USA/sonda/F1/PPSSPP en ficheros reales. Nada de confundir un hash documental con bytes presentes.

**B. Inicio:** PPSSPP real con WebSocket activo. Si usas Sharun en este contenedor, `SHARUN_ALLOW_LD_PRELOAD=1` + shim externo ya probado; no modificar executable. Valida INI de la sesión, puerto TCP y handshake. Ejecuta `f2_ws_procedencia_ppsspp.py` por PID e ISO específicos y `f2_x11_ppsspp_procfs_capture.py` si capturas X11; no reutilices PID de sesión anterior.

**C. Control reproducible:** usar interfaz real o WS oficial `input.buttons.press` con `button` y `duration`, que se comprobó contra el juego. La pantalla título ha respondido a círculo en una de las transiciones y Opciones a cruz; no asumir botones globales fijos sin observar. Documenta cada paso hasta combate/efecto/trampa. Guarda estado válido si el juego lo permite, fuera de Git, y reproduce con USA y sonda.

**D. A/B TUIKA:** llegar a un mensaje donde `SYSGRA.ARC/TUIKA_MES.IMY` pueda usarse. Capturar ISO USA (A) y sonda (B) en la **misma escena y estado** con control temporal y región de pantalla, excluyendo el splash SYSTEM PRiSM. Buscar diferencia localizada magenta, incluir negativo/positivo. Si no hay cambio, registrar resultado negativo solo para la escena probada. No editar franjas TUIKA, japoneses, números, iconos, ni CLUT/ROI a ciegas; 7 subregiones y tres huecos transparentes están protegidos.

**E. GPU/VRAM:** grabar `gpu.record.dump` real en el mismo momento de la escena usando CPU ejecutándose; analizarlo con `f2_ge_dump_1204.py`. Intentar `gpu.buffer.renderColor` mientras CPU/GPU se detiene para investigar por qué `gpu.buffer.screenshot` da `Could not download output`, o probar otro backend real, registrando los resultados. Investigar secuencia `IMY→decodificación RAM→GE TEXADDR/CLUT/PRIM/TRANSFERSTART→VRAM→píxel` con evidencia binaria/runtime; no inventar PC MIPS/VRAM. Capturas X11 y volcados GE son distintas clases de evidencia. No atribuir iconos al PC `0x089089C8` (proceso de fuente textual).

**F. 19 glifos:** probar `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō` y `L/R/□/○/×/△` en ayuda, diálogo, HUD, tutorial, equipamiento, combate y menús; distintas CLUT blanco/amarillo y recorte de signos. Diferenciar `FONT.ARC/FONT_00.IMY` (512×256) de `SYSGRA.ARC/FONT.IMY` (256×256), y conservar `white_new_ink=False` salvo validación visual multicontesto. Registrar cada carácter/contexto, no marcar 19/19 por ver `música` y `Sí`.

**G. Regresión F1 y seguridad:** confirmar Opciones≈764 px exterior y ayudas `005709/005710 Sí/005713 No`, sin colisiones, retratos intactos, eventos no cambiados. No desactivar `--event-safe-only`, no alterar offsets de SCRIPT.DAT ni otros assets ajenos.

## 4. Comandos reproducibles en directorios privados NUEVOS

~~~bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
git status --short
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
sha256sum /PRIVATE/USA.iso /PRIVATE/SONDA_TUIKA.iso /PRIVATE/F1.iso /PRIVATE/PPSSPP-v1.20.4-anylinux-x86_64.AppImage
# Usar el PID ACTUAL de PPSSPP; puerto 24192 LISTEN real:
python tools/f2_ws_procedencia_ppsspp.py --pid PID_REAL --port 24192 \
  --iso-privada /PRIVATE/F1.iso --tipo f1 \
  --informe-privado /PRIVATE/WS_PID_F1_NUEVO.json
# Repetir con --tipo usa o sonda, rutas nuevas, cuando se inicie otra ISO.
python tools/f2_x11_ppsspp_procfs_capture.py --display :98 --pid PID_REAL \
  --iso /PRIVATE/USA.iso --tipo usa \
  --png-privado /PRIVATE/A_REAL.png --manifiesto-privado /PRIVATE/A_PROCFS.json
# Una vez EN ESCENA TUIKA real, no solo splash:
python tools/f2_ppsspp_ws_1204.py --scene TUIKA_HABILIDADES \
  --salida-privada /PRIVATE/WS_A_NUEVA --port 24192 --ge-dump \
  --pid-ppsspp PID_REAL --iso-en-proceso /PRIVATE/USA.iso --tipo-iso usa
# Repetir con sonda y otro PID. Cotejar:
python tools/f2_cotejar_capturas_tuika.py \
  --manifest-usa /PRIVATE/WS_A_NUEVA/manifest_PRIVATE.json \
  --manifest-sonda /PRIVATE/WS_B_NUEVA/manifest_PRIVATE.json \
  --iso-usa /PRIVATE/USA.iso --iso-sonda /PRIVATE/SONDA_TUIKA.iso \
  --reporte-privado /PRIVATE/AB_TUIKA_NUEVO.json
python tools/f2_ge_dump_1204.py --entrada-privada /PRIVATE/GE_REAL.dump \
  --reporte-privado /PRIVATE/GE_ANALISIS_NUEVO.json
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/preflight_nuevo.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/integrabilidad_nuevo.json
(cd patcher && go test ./...)
git diff --check
~~~

Los comandos A/B dependen de conseguir **sesiones reales en el contexto correcto**. No generan pruebas de TUIKA por sí solos. No colocar archivo de screenshot, dump, ISO, DATA.DAT, EBOOT, IMG/IMY, FONT.ARC, BPS, PPSSPP o EXE con payload dentro del checkout ni GitHub; solo código, tests sintéticos, JSON con métricas y docs. No modificar el corpus original ni las ramas base.

## 5. Fases posteriores F3–F6

**F3:** textos de intro en inglés: encontrar recurso/ID exacto, traducir sin alterar eventos, captura antes/después real.

**F4:** resolver de forma probada referencias de saltos y offsets en SCRIPT.DAT/SCRIPT.TBL/intérprete MIPS para incorporar con seguridad los **4.524** cambios aplazados, verificando órdenes/opcodes y pruebas runtime. Nunca proclamar cobertura completa por sólo reconstruir strings.

**F5:** campaña con QA de clases, combate, ciudad, pisos, enciclopedia, mapas, HUD, equipos, retratos, guardado/carga, paletas, iconos y glifos.

**F6:** BPS con roundtrip/hash, integridad PSPFS/DSARC, actualización hashes del parcheador Go, EXE x64 con BPS privado realmente probado en Windows, documentación y publicación después del QA, sin compartir ISO comercial.

## 6. Entregables y RELEVO RECURSIVO INNEGOCIABLE

Al terminar debes: (1) identificar cambios y causas verdaderamente demostradas; (2) distinguir tests sintéticos de capturas PPSSPP, sockets y GPU reales; (3) entregar evidencias privadas auténticas, hashes ISO/BPS/GE y nuevas regresiones; (4) actualizar un informe en `docs/`, JSON en `reports/` y `reports/ESTADO_CONTINUIDAD_PPSSPP.json`; (5) crear commit verificable sin force, mantener PR #7 DRAFT y verificar **dos CI SUCCESS sobre el mismo HEAD final** o registrar bloqueo; (6) **REESCRIBIR COMPLETAMENTE `prompts/SIGUIENTE_TAREA.md` y MOSTRAR SU CONTENIDO ÍNTEGRO AL USUARIO**. Ese nuevo prompt debe repetir textualmente esta obligación recursiva y llevar archivos, hashes, comandos, tareas y pruebas. Si F2 sigue sin prueba TUIKA multicontesto, **seguir F2 en el próximo relevo**; no saltar artificialmente a F3.
