# CLADUN ES — SIGUIENTE RELEVO AUTÓNOMO F2: PPSSPP REAL, fuentes duplicadas en archivos distintos, MIPS→GE→VRAM y regresión F1

Especialidad obligatoria: ingeniería inversa PSP MIPS, PPSSPP oficial 1.20.4 con WebSocket debugger, GPU GE/VRAM, DSARC/PSPFS/ISO9660, IMY/CLUT, CP932 español, BPS y QA de interfaz. Ejecuta cambios y experimentos auténticos, valida SHA-256, publica código y evidencias METADATOS a GitHub. **No basta con redactar instrucciones. No inventes capturas, emulación, direcciones MIPS/VRAM, hashes o resultados funcionales.**

**OBLIGACIÓN RECURSIVA:** al terminar REESCRIBE COMPLETAMENTE este mismo archivo `prompts/SIGUIENTE_TAREA.md` con un NUEVO prompt autónomo íntegro, que nuevamente exija reescribirlo, y muéstralo íntegro al usuario. Repetir hasta que F2, F3, F4, F5 y F6 estén realmente implementadas y verificadas; nunca prometer trabajos en segundo plano.

## 1. GitHub: integridad del trabajo y fuentes obligatorias

Repositorio `https://github.com/ARivas3008/loxalizacion-cladun-psp`. Rama `integracion-eventos-segura-20261120`; PR #7 `https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7`, base `revision-manual-dialogos`, mantener **DRAFT**. Antes de modificar: verificar HEAD, árbol, PR, estado de las dos GitHub Actions y ausencia de trabajo paralelo. En checkout local ejecutar `git fetch origin`, `git switch integracion-eventos-segura-20261120`, `git pull --ff-only`, `git status --short`, `git rev-parse HEAD`. Si DNS impide Git directo, registrar fallo y usar conector GitHub con expected_sha; no afirmar sincronización falsa. Nunca forzar la referencia ni fusionar PR.

Leer ÍNTEGROS AGENTS.md, README.md, docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md, docs/RESULTADO_F1_PPSSPP_2026-11-21.md, docs/RESULTADO_F2_ATLAS_PPSSPP_2026-11-21.md, docs/F2_ICONOS_TINTA_PPSSPP_2026-11-21.md, docs/F2_AUDITORIA_ORIGEN_SOLO_LECTURA_2026-11-21.md, docs/F2_QA_ESTATICA_WS_2026-11-21.md, docs/F2_LECTOR_GE_V6_2026-11-21.md, docs/F2_RELEVO_CAPTURA_RAM_2026-11-21.md, docs/F2_FE_ERRATAS_SHA256_SNAPSHOT_RAM_2026-11-21.md, docs/F2_RELEVO_WS_BREAKPOINT_2026-11-21.md, docs/F2_PREPARACION_DIRECCIONES_GE_2026-11-21.md, docs/F2_INVENTARIO_SYSGRA_2026-11-22.md y NUEVA docs/F2_CATALOGO_GLOBAL_DSARC_2026-11-22.md. Leer informes F2 completos en reports/ incluyendo reports/RESULTADO_F2_CATALOGO_GLOBAL_DSARC_2026-11-22.json, reports/ESTADO_CONTINUIDAD_PPSSPP.json, este prompt y código/tests/patcher/.github/workflows.

PROHIBIDO subir ISO, BPS, EBOOT, DATA.DAT, FONT.ARC, IMY, PNG comerciales, RAM, dumps GE, texturas, ejecutables de juegos. Evidencias de esos tipos solo en ubicación privada externa al repo; subir únicamente código, tests, resumen de metadatos, informes no comerciales y SHA.

## 2. Referencias autenticadas e invariantes

ISO USA PRIVADA del 7z aportado: 305496064 bytes, SHA-256 EXACTO de 64 hex:
`b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.
No reintroducir la versión incorrecta de 62 caracteres; mantener tests/test_f2_sha256_references.py. ISO F1 canónica SHA `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`. BPS experimental USA→F1 SHA `daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd`. AppImage PPSSPP Linux oficial v1.20.4 SHA `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`.

F1 Opciones aprobada HISTÓRICAMENTE en PPSSPP real Xvfb 1280×720, ventana X11 960×544, interior 756 px, exterior ~764 px. ID 005709 diez espacios ideográficos más 7 ASCII; 005710 «Sí»; 005713 «No» + espacio ASCII de presentación. Una captura PSP framebuffer no demuestra ancho de ventana X11: volver a medir usando scrot/X11.

F2: 2721 glifos originales conservados + 19 A1–B3 `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō`. Tabla MIPS de TEXTO `0x09075000`, PC `0x089089C8`, instrucción `lhu t2,0(t1)`: NO identificar como iconos. ICONOS CONTROLES históricamente aislados en DATA.DAT→SYSGRA.ARC (PSPFS índice 225, offset 895488)→KITAJIMA_KARI.IMY (DSARC índice 17/27, offset 57856, longitud 2480), SHA `0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190`, offset ISO absoluto 114723840 NO es RAM. Prueba magenta previa: 27 bytes RGB cambiados y seis iconos de CONTROLES, 348 vecinos PSPFS +26 DSARC intactos. HUD/combate NO probados.

Tinta FONT_00.IMY: CLUT15 amarilla RGB(247,247,0) y CLUT1 blanca RGB(255,255,255). `white_new_ink=True` optativa cambia 100 texels nuevos sin tocar los 2721 originales; conservar `False` predeterminado. ISOs experimentales amarilla `58f98b65185f39f172de0b5da97b9ce6fecb009e61b9462632f602485c99e4ca`, blanca `a42731988835bddb9dc81ef6d242b9c5029030256f210838881a1d48aed2de33` y BPS amarillo→blanco `2a698e1efaa1c2333dbd86ac8c3a9fabbd369382c4b8c7d3ad0ab7c7f2ffac3f`; una ayuda anterior de amarillo 516→0 NO acredita todos los 19 caracteres.

## 3. NUEVO hallazgo real del relevo precedente: hay cuatro DSARC, no solo SYSGRA

Se releyó la ISO USA auténtica, con fuente derivada de ISO9660 en vez de inventar offsets. DATA.DAT offset ISO 113770496; 349 PSPFS. Los cuatro contenedores DSARC reconocidos por firma en la tabla son:
- PSPFS 0: SYS.DAT2, 6 PNG.
- PSPFS 188: SE.ARC, 68 SPS.
- PSPFS 225: SYSGRA.ARC, 27 IMY.
- PSPFS 308: FONT.ARC, 7 recursos BIN/IMY.
**Total 108 miembros, 108 SHA-256 diferentes**, todos comprobados y sin solapamientos. Informe detallado PRIVADO de 108 filas `CLADUN_F2_catalogo_DSARC_108_privado_2026-11-22.json`, SHA `9938fd9fc0eba271494ecdfeec49c1ffd95291b0abecdc33ca65ee97c00bc567` (SOLO metadatos).

Posible línea nueva de investigación visual: **SYSGRA.ARC/FONT.IMY** SHA `50143c165f10aa71ac77d4a2b09fd69012b1eceac4a102bf8e2b8157bf8b5915` es distinto EN BYTES almacenados de **FONT.ARC/FONT_00.IMY** SHA `698bc5b398a16c3f2a4615527dac6a36dbae73666a7c45c3787bb00a728a8478`. NO afirmar que sean diferentes visualmente o se usen en un contexto sin observación. Se debe comparar su papel funcional, especialmente interfaz y HUD, antes de cerrar F2.

Herramienta nueva `tools/f2_catalogo_global_dsarc_usa.py` autentica ISO y verifica todas las estructuras y firmas sin exportar recursos; `tests/test_f2_catalogo_global_dsarc_usa.py` contiene 12 tests sintéticos. Commits de código `375eec3d7bcb3dbc878f9579ed49e9af92279091` y corrección real de orden de validación `822a17dc457ec761a56164db6fdcbc8b7fa8f93d`. El primer CI falló por solapamiento detectado como cabecera PNG mala y se corrigió para verificar primero la topología; Actions del código reparado push `45040317705` y PR `45040322660` ambas SUCCESS con **233 tests Python**, Go e integridad y build Windows. Son pruebas estáticas, NO PPSSPP.

Anteriormente se identificaron solo por nombre 12 candidatos SYSGRA: HP_BAR, HP_KAO0, HP_KAO1, HP_KAO2, LVSP, LVSP_NUM, DAMAGE, EXP_BAR, MAHO_BAR, MAHO_ST, SYS1, ZOKUSEI. NO asignarles HUD o combate hasta comprobarlos funcionalmente.

## 4. PRIORIDAD: conseguir PPSSPP oficial y probar verdadera procedencia gráfica

Comprobar PPSSPP AppImage real desde `https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4`; validar SHA exacto antes de ejecutar. En anterior entorno AppImage y F1 no estaban presentes; Git/curl no resolvían DNS. Si sigue bloqueado, señalar SIN EJECUCIÓN, jamás inventar PNG/GE, y realizar una mejora verificable alternativa. Xvfb 1280×720, scrot y ventana 960×544 solo sirven como evidencia cuando hay emulador funcionando con juego.

Recuperar ISO F1 canónica privada o reconstruirla desde la USA mediante integrador auditado y `--experimental-parcial --event-safe-only`, manteniendo ISO original intacta; exigir hash exacto. No compartir ningún binario comercial. El PR permanece DRAFT.

Con juego REAL visible en CONTROLES, debugger WebSocket `ws://127.0.0.1:24192/debugger`, subprotocolo `debugger.ppsspp.org`. Verificar `version`, `game.status`, `cpu.status`. PPSSPP 1.20.4 admite `memory.read`, `memory.disasm`, `memory.breakpoint.list/add/remove`, `cpu.getAllRegs`, `cpu.stepping/resume`, `gpu.buffer.screenshot`, `gpu.record.dump`; no inventar `cpu.breakpoint.hit` ni `gpu.displaylist.disasm`.

Con CPU CORRIENDO, en carpeta PRIVADA NUEVA:
`python tools/f2_ppsspp_ws_1204.py --scene CONTROLES --salida-privada /tmp/cladun-f2-controles-real --port 24192 --ge-dump`
`python tools/f2_ge_dump_1204.py --entrada-privada /tmp/cladun-f2-controles-real/CONTROLES_GE_PRIVATE.dump --reporte-privado /tmp/cladun-f2-ge-real.json`
`python tools/f2_ram_provenance_1204.py --iso-usa /PRIVATE/USA.iso --salida-privada /tmp/cladun-f2-origen-real --solo-origen`

Para RAM, `--scan-ram` con CPU realmente detenida y ticks verificados; si existe firma en RAM auténtica, en contexto nuevo y con un solo debugger usar `--watch-address 0xDIRECCION_PSP_RAM`; jamás el offset ISO 0x06D68C00. Solo atribuir un watchpoint con `reason == memory.breakpoint` y `relatedAddress == inicio`; preservar pausas y puntos de vigilancia ajenos. Correlacionar PC MIPS real, lectura comprimida, descompresor, escritura en RAM, registros TEXADDR/CLUT, PRIM/TRANSFERSTART, transferencias a VRAM y pixel final. `tools/f2_ge_dump_1204.py` publica CANDIDATOS de direcciones, NO causalidad por sí solo. Comparar por separado KITAJIMA, SYSGRA/FONT.IMY, FONT.ARC/FONT_00.IMY y candidatos HUD/combate con controles positivos y negativos.

Capturar al menos DOS PNG auténticos por CONTROLES, HUD, tutorial, ayuda, diálogos y combate y hash SHA individual PRIVADO; registrar evidencia X11 cuando se mida ventana, nunca un montaje.

## 5. QA de 19 glifos, F1 y seguridad total

Validar individualmente `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō` en PPSSPP real y múltiples pantallas, además de L/R/□○×△, ancho, avance, altura, acentos, márgenes y clipping (í x4 y mayúsculas y15), líneas y CLUT. Usar `tools/generar_probe_f2_glifos.py` y `tools/generar_probe_f2_tinta.py` solo en CSV/ISO diagnósticos PRIVADOS, sin alterar 9237 registros canónicos. No habilitar tinta blanca predeterminada antes de probar F1 Opciones actual y navegación, IDs 005709/005710/005713, ventana 960×544 y márgenes 756/~764.

Comprobar invariantes: 349 PSPFS, 345 recursos fuera de cuatro contenedores autorizados, 348 vecinos PSPFS en sondas aisladas FONT.ARC/SYSGRA.ARC, 26 DSARC vecinos KITAJIMA, ISO9660 restante idéntico; SCRIPT.DAT 51705 comandos, 46308 no textuales, 1625 inicios, desplazamientos cero y 4524 traducciones de script aplazadas. NO retirar `--event-safe-only`. Si se genera BPS solo experimental y privado: `--experimental --event-safe-only`, SHA origen/salida y roundtrip exacto.

Ejecutar comandos cuando exista checkout local:
`python -m unittest discover -s tests -v`
`python tools/verificar_integridad.py --raiz .`
`python tools/verificar_borrador_es.py`
`python tools/auditar_preinsercion_es.py --reporte /tmp/f2-preflight.json`
`python tools/reportar_integrabilidad_es.py --reporte /tmp/f2-integrabilidad.json`
`python tools/f2_auditar_origen_iconos.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-origen.json`
`python tools/f2_qa_raster_19.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-glifos.json`
`python tools/f2_inventario_sysgra_usa.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-sysgra.json`
`python tools/f2_catalogo_global_dsarc_usa.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-dsarc.json`
`(cd patcher && go test ./...)`
`git diff --check`

Diferenciar pruebas Python/Go/Windows en GitHub Actions de emulación real y comparar el SHA del HEAD FINAL del PR con los dos workflows. Registrar explícitamente comandos omitidos y ausencia de recursos, sin declarar ejecuciones ficticias.

## 6. Fases pendientes y relevo recursivo al terminar

F2 ABIERTA hasta demostrar cadena RAM→MIPS→GE→VRAM de iconos, fuente de tipografía de cada contexto, 19 glifos multicontesto y F1 de ventana real. F3 intro inglesa; F4 ingeniería de saltos y referencias seguros de 4524 textos SCRIPT.DAT; F5 recorrer historia, combate, HUD, inventario, retratos, enciclopedia y guardado/carga; F6 crear BPS final y EXE Windows con QA completo. No merge de PR #7 hasta terminar.

Al concluir actualizar código, pruebas, docs y `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, registrar commit y hashes reales y diferenciar HECHO / NO PROBADO. No subir materiales comerciales. Reescribir **POR COMPLETO** `prompts/SIGUIENTE_TAREA.md` con un nuevo prompt autónomo, mostrarlo íntegro al usuario y exigir de nuevo la misma obligación para la siguiente tarea. RECURSIVIDAD OBLIGATORIA HASTA F2–F6 CERRADAS DE VERDAD.
