# CLADUN ES — RELEVO AUTÓNOMO F2: PPSSPP 1.20.4 REAL, procedencia de iconos, 19 glifos y regresión F1

Actúa como especialista sénior de PSP MIPS, WebSocket PPSSPP oficial 1.20.4, listas GE/VRAM, IMY/CLUT, DSARC/PSPFS, codificación CP932, BPS, calidad del español y QA funcional. **Ejecuta cambios, pruebas, verificaciones y actualizaciones reales en GitHub**. No basta con escribir instrucciones y no debes inventar emulación, capturas, direcciones MIPS/VRAM ni hashes.

**OBLIGACIÓN RECURSIVA:** al terminar REESCRIBE COMPLETAMENTE este mismo archivo `prompts/SIGUIENTE_TAREA.md` con un NUEVO prompt autónomo completo, exige en el nuevo texto la misma obligación, y muéstralo íntegro al usuario. Continuar los relevos hasta completar, implementar y probar F2, F3, F4, F5 y F6. No declarar trabajo en segundo plano.

## 1. Repositorio, HEAD y documentos

Repositorio: https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama: `integracion-eventos-segura-20261120`
PR #7: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7
Base: `revision-manual-dialogos`.

Antes de cambiar archivos, comprobar HEAD actual, árbol, PR DRAFT y GitHub Actions. Si Git directo funciona, ejecutar `git fetch origin`, `git switch integracion-eventos-segura-20261120`, `git pull --ff-only`, `git status --short` y `git rev-parse HEAD`. Si DNS bloquea Git, usar el conector GitHub y decir expresamente que Git directo NO se ejecutó. Nunca forzar referencias, sobrescribir otros commits ni fusionar PR #7.

Leer íntegros `AGENTS.md`, `README.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, `docs/RESULTADO_F1_PPSSPP_2026-11-21.md`, `docs/RESULTADO_F2_ATLAS_PPSSPP_2026-11-21.md`, `docs/F2_ICONOS_TINTA_PPSSPP_2026-11-21.md`, `docs/F2_AUDITORIA_ORIGEN_SOLO_LECTURA_2026-11-21.md`, `docs/F2_QA_ESTATICA_WS_2026-11-21.md`, `docs/F2_LECTOR_GE_V6_2026-11-21.md`, `docs/F2_RELEVO_CAPTURA_RAM_2026-11-21.md`, `docs/F2_FE_ERRATAS_SHA256_SNAPSHOT_RAM_2026-11-21.md`, todos los informes F2 en `reports/`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, este prompt, y revisar `tools/`, `tests/`, `patcher/`, workflows `.github/`.

NO subir ISO, BPS, EBOOT, DATA.DAT, FONT.ARC, RAM, texturas, dumps GE ni capturas comerciales a GitHub. Evidencias de juego solo en carpeta PRIVADA externa al repositorio con hashes SHA256.

## 2. Referencias CORREGIDAS: comprobar hash de 64 caracteres

**ISO USA privada auténtica**: tamaño 305496064 bytes, SHA256 EXACTO (64 caracteres):
`b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`

**Importante:** variantes anteriores de 62 caracteres omitían DOS CEROS y se habían propagado a notas, informes y prompts. Se corrigieron en el relevo anterior y se agregó `tests/test_f2_sha256_references.py` para impedir regresión. Las constantes SHA en los analizadores principales YA eran correctas; no cambiarlas ni usar el SHA truncado. La última sesión reextrajo la ISO original del 7z y autenticó sus bytes, más los 2480 bytes del recurso IMY en offset 114723840.

ISO F1 canónica privada SHA256 `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`.
BPS experimental desde USA a F1 SHA256 `daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd`.
AppImage Linux PPSSPP oficial 1.20.4 SHA256 `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`.

F1 Opciones solo APROBADA HISTÓRICAMENTE en PPSSPP Xvfb 1280×720, VENTANA 960×544: 756 px interiores, aproximadamente 764 exteriores. ID 005709 diez espacios ideográficos + siete ASCII; 005710 «Sí»; 005713 «No» con espacio ASCII de presentación. Captura del framebuffer PSP NO demuestra las medidas de ventana 960×544; exigir captura X11 auténtica.

F2 fuente: 2721 glifos originales intactos, más 19 nuevos A1–B3: `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō`. Tabla de búsqueda de TEXTO código→índice MIPS RAM `0x09075000`, PC `0x089089C8`, instrucción `lhu t2,0(t1)`; NO identifica los iconos.

Origen CONTROLES: `DATA.DAT → SYSGRA.ARC` (PSPFS índice 225, offset local DATA.DAT 895488) `→ KITAJIMA_KARI.IMY` (DSARC índice 17 de 27, offset 57856, longitud 2480), SHA256 `0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190`. Offset ISO absoluto `114723840 = 0x06D68C00` NO ES una dirección RAM. Prueba PPSSPP anterior magenta aisló seis iconos de CONTROLES con 27 bytes RGB cambiados, 348 vecinos PSPFS y 26 DSARC intactos. NO extrapolar a HUD, tutoriales ni combate.

FONT_00.IMY: CLUT15 amarillo RGB(247,247,0) frente a CLUT1 blanco RGB(255,255,255). `white_new_ink=True` optativo reemplaza 100 texels de los glifos nuevos sin tocar 2721 originales; mantener `False` por defecto hasta QA funcional. ISO sonda amarilla SHA `58f98b65185f39f172de0b5da97b9ce6fecb009e61b9462632f602485c99e4ca`; ISO tinta blanca SHA `a42731988835bddb9dc81ef6d242b9c5029030256f210838881a1d48aed2de33`; BPS origen sonda amarilla→blanca SHA `2a698e1efaa1c2333dbd86ac8c3a9fabbd369382c4b8c7d3ad0ab7c7f2ffac3f`. Una ayuda antigua mostró amarillo 516→0; no es prueba multicontesto.

## 3. Nuevas herramientas seguras y sus límites

`tools/f2_ppsspp_ws_1204.py` usa WebSocket local `ws://127.0.0.1:24192/debugger`, subprotocolo `debugger.ppsspp.org`. PPSSPP 1.20.4 exige CPU/GPU en stepping para `gpu.buffer.screenshot`; la herramienta pausa, captura dos PNG PSP y reanuda solo si ella misma pausó. `gpu.record.dump` debe iniciarse PRIMERO con CPU corriendo para grabar el siguiente frame. Salida de volcado: `ESCENA_GE_PRIVATE.dump`. No confundir dos PNG de GPU con dos capturas de ventana X11.

`tools/f2_ram_provenance_1204.py` autentica firma exacta de KITAJIMA desde ISO original; `--scan-ram` recorre RAM PSP CON CPU DETENIDA y comprueba que ticks iniciales/finales no cambiaron, reanudando solo pausa propia; `--watch-address` registra PC, desensamblado y GPR ante evento, y NO reanuda pausas ajenas al watchpoint. Una firma RAM hallada NO acredita transferencia GE/VRAM. En la sesión precedente se probaron 13 tests locales sintéticos de esta sonda y GitHub Actions del código resultó SUCCESS, pero no hubo RAM real de PPSSPP.

`tools/f2_ge_dump_1204.py` lee grabaciones privadas PPSSPPGE v6, Zstd, contabiliza TEXADDR, CLUT, PRIM y comandos de transferencia, sin publicar datos gráficos. Solo adquiere valor probatorio junto a captura auténtica y correlación MIPS/VRAM. `tests/test_f2_sha256_references.py` comprueba los hashes fuente y rechaza nuevas referencias truncadas.

## 4. Prioridad operativa: arrancar emulador VERDADERO y reconstruir F1

Comprobar si el entorno dispone del AppImage oficial PPSSPP v1.20.4 (release oficial: https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4). Autenticar SHA exacto ANTES de arrancar; si descarga bloqueada por DNS, explicar bloqueo y no afirmar PPSSPP ejecutado. Comprobar Xvfb, scrot, control de ventana de 960×544 y la ISO F1: usar sólo un archivo F1 de SHA auténtico, generado de manera segura en ruta privada mediante integrador revisado si se puede. No sobrescribir la ISO USA.

Con Cladun REAL iniciado y CONTROLES visible, verificar `version`, `game.status`; capturar en directorio PRIVADO NUEVO:
`python tools/f2_ppsspp_ws_1204.py --scene CONTROLES --salida-privada /tmp/f2-controles-nuevo --port 24192 --ge-dump`
Después:
`python tools/f2_ge_dump_1204.py --entrada-privada /tmp/f2-controles-nuevo/CONTROLES_GE_PRIVATE.dump --reporte-privado /tmp/f2-ge-metadatos.json`

Para origen (solo binario):
`python tools/f2_ram_provenance_1204.py --iso-usa /PRIVATE/USA.iso --salida-privada /tmp/f2-origen-nuevo --solo-origen`
Para scan RAM real usar NUEVA carpeta y `--scan-ram`. Únicamente si una dirección RAM PSP se observa legítimamente, reiniciar contexto para hacer watchpoint `--watch-address 0xDIRECCION_RAM` en OTRA carpeta. Correlacionar lecturas/escrituras, buffer comprimido, descompresor, salida, PC MIPS real, comandos GE, CLUT, textura, transferencia VRAM y dibujo final. Un PC de texto o un stop por otra causa NO prueban iconos. Registrar para cada eslabón DEMOSTRADO o NO PROBADO.

Realizar controles positivo y negativo sobre CONTROLES, HUD, tutoriales, ayudas, diálogos y combate sin asumir recursos compartidos. Guardar al menos dos PNG auténticos por contexto, SHA de cada PNG, sin retoques ni montajes. Para la geometría F1 usar captura de VENTANA real con scrot/X11 a 960×544, no framebuffer PSP.

## 5. QA 19 glifos e invariantes

Revisar individualmente `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō`, interacción con L/R/□○×△, anchura y avance, márgenes, altura, clipping, interlineado, í x4 y mayúsculas y15. Comparar texto blanco original con blanco opcional; usar CSV diagnóstico PRIVADO de 9237 registros mediante `tools/generar_probe_f2_glifos.py` y `tools/generar_probe_f2_tinta.py` sin tocar corpus canónico. No habilitar tinta blanca por defecto antes de comprobar F1 Opciones real 960×544 y los IDs 005709, 005710, 005713, navegación y regreso.

Conservar 349 PSPFS, 345 recursos ajenos a cuatro contenedores, 348 vecinos en sondas FONT.ARC/SYSGRA.ARC, 26 DSARC vecinos KITAJIMA, ISO9660 ajeno exacto; SCRIPT.DAT 51705 comandos, 46308 no textuales, 1625 inicios, cero desplazamientos, 4524 traducciones script aplazadas. NUNCA eliminar `--event-safe-only`. Integración candidata desde USA `--experimental-parcial --event-safe-only`; BPS experimental `--experimental --event-safe-only`; validar SHA origen/salida y roundtrip exacto.

Ejecutar `python -m unittest discover -s tests -v`; `python tools/verificar_integridad.py --raiz .`; `python tools/verificar_borrador_es.py`; `python tools/auditar_preinsercion_es.py --reporte /tmp/f2-preflight.json`; `python tools/reportar_integrabilidad_es.py --reporte /tmp/f2-integrabilidad.json`; `python tools/f2_auditar_origen_iconos.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-audit.json`; `python tools/f2_qa_raster_19.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-raster.json`; `(cd patcher && go test ./...)`; `git diff --check`. Si no hay checkout/Git/PPSSPP, ejecutar todo lo posible y documentar lo omitido; verificar CI real sobre HEAD FINAL para Python, Go y compilación Windows, sin llamar a eso prueba PPSSPP.

## 6. Fases y relevo recursivo FINAL OBLIGATORIO

F2 ABIERTA hasta probar RAM→GE→VRAM de iconos, 19 glifos multicontesto y nueva regresión F1. F3: intro inglesa; F4: saltos y referencias seguras para 4524 scripts aplazados; F5: recorrer aventura, combate, HUD, inventario, retratos, enciclopedia y guardado/carga; F6: BPS final, EXE Windows y QA integral. Mantener PR #7 DRAFT hasta terminar todo.

Actualizar informes docs/reports y `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, identificar los commits, SHA reales o NO GENERADO de ISO/BPS/PNG, y separar estática/binaria de visual/funcional.

**AL TERMINAR REESCRIBIR COMPLETAMENTE `prompts/SIGUIENTE_TAREA.md` CON OTRO PROMPT AUTÓNOMO ÍNTEGRO, MOSTRARLO AL USUARIO Y EXIGIR EN ÉL REGENERAR DE NUEVO EL MISMO ARCHIVO. CONTINUAR RECURSIVAMENTE HASTA F2–F6 COMPLETADOS Y VERIFICADOS REALMENTE.**
