# CLADUN ES — SIGUIENTE RELEVO AUTÓNOMO: PPSSPP REAL y trazabilidad de las 27 texturas SYSGRA, F1 y 19 glifos

Actúa como especialista sénior en PSP MIPS/GE, PPSSPP oficial v1.20.4, texturas indexadas y CLUT, IMY, DSARC/PSPFS/ISO9660, CP932, BPS y localización al español. **Ejecuta trabajo real, experimentos, pruebas y cambios**; actualiza GitHub con SHA comprobable y separa binario auténtico / CI sintético / juego ejecutado. No inventes una captura, dirección RAM/VRAM, PC MIPS, dump, SHA, BPS ni prueba funcional.

**RECURSIVIDAD OBLIGATORIA:** al terminar esta tarea, REESCRIBE COMPLETAMENTE el propio archivo `prompts/SIGUIENTE_TAREA.md` con un NUEVO prompt autónomo completo, que incluya otra vez esta misma obligación. Muéstralo íntegro en tu respuesta. Repite cada relevo hasta lograr F2, F3, F4, F5 y F6 realmente terminadas y comprobadas. No prometer resultados posteriores o asíncronos.

## 1. GitHub y archivos que deben revisarse

Repositorio: https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama de trabajo: `integracion-eventos-segura-20261120`
PR #7: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7
Rama base: `revision-manual-dialogos`. PR siempre **DRAFT**, sin merge, sin force push ni pérdida de cambios previos.

ANTES de editar verificar rama, HEAD SHA, tree SHA, PR y Actions `push` y `pull_request`. En checkout local ejecutar: `git fetch origin`, `git switch integracion-eventos-segura-20261120`, `git pull --ff-only`, `git status --short`, `git rev-parse HEAD`. Si fallan por DNS, dejar registro real y usar conector GitHub con `expected_sha`, nunca afirmar que hubo fetch/pull exitoso.

Leer completos `AGENTS.md`, `README.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, `docs/RESULTADO_F1_PPSSPP_2026-11-21.md`, `docs/RESULTADO_F2_ATLAS_PPSSPP_2026-11-21.md`, `docs/F2_ICONOS_TINTA_PPSSPP_2026-11-21.md`, `docs/F2_AUDITORIA_ORIGEN_SOLO_LECTURA_2026-11-21.md`, `docs/F2_QA_ESTATICA_WS_2026-11-21.md`, `docs/F2_LECTOR_GE_V6_2026-11-21.md`, `docs/F2_RELEVO_CAPTURA_RAM_2026-11-21.md`, `docs/F2_FE_ERRATAS_SHA256_SNAPSHOT_RAM_2026-11-21.md`, `docs/F2_RELEVO_WS_BREAKPOINT_2026-11-21.md`, `docs/F2_PREPARACION_DIRECCIONES_GE_2026-11-21.md`, `docs/F2_INVENTARIO_SYSGRA_2026-11-22.md`, `docs/F2_CATALOGO_GLOBAL_DSARC_2026-11-22.md`, `docs/F2_DOS_FUENTES_IMY_DECODIFICADAS_2026-11-22.md`, NUEVO `docs/F2_SYSGRA_27_IMY_PALETAS_2026-11-22.md`, informes F2 de `reports/`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, este prompt y los archivos de `tools/`, `tests/`, `patcher/`, `.github/workflows/`.

**PRIVACIDAD:** NO publicar ISO, BPS, EBOOT, DATA.DAT, FONT.ARC, IMY, RAM, screenshots de juego, volcados GPU, texturas ni ejecutables comerciales en GitHub. Almacenar esos datos exclusivamente en carpetas privadas externas al repositorio; subir código libre, pruebas sintéticas, documentación, SHA y métricas.

## 2. Referencias exactas verificadas e invariantes

ISO original USA proporcionada en 7z: **305496064 bytes**, SHA-256 exacto de 64 dígitos `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. NO usar antiguo SHA erróneo de 62 caracteres. ISO F1 canónica de antecedente SHA `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`; BPS USA→F1 SHA `daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd`. AppImage oficial PPSSPP Linux 1.20.4 SHA `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`.

F1 Opciones **aprobada históricamente en PPSSPP real**, Xvfb 1280×720, ventana auténtica 960×544, 756px interiores / ~764 exteriores; ID 005709 diez espacios ideográficos y 7 ASCII, ID 005710 Sí, ID 005713 No y espacio ASCII. Exigir nueva captura X11 de esa ventana para regresión F1: framebuffer PSP no acredita el tamaño de la ventana.

F2: 2721 glifos originales y 19 A1–B3 `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō` =2740. Tabla de TEXTO en RAM `0x09075000`, PC `0x089089C8` con `lhu t2,0(t1)`: NO es PC de iconos. Tinta FONT_00.IMY: CLUT15 amarilla (247,247,0), CLUT1 blanca (255,255,255). `white_new_ink=True` cambia optativamente 100 texels nuevos, preservando glifos originales; debe mantenerse `False` por defecto hasta QA visual + F1.

Iconos CONTROLES demostrados históricamente por sonda magenta: DATA.DAT→SYSGRA.ARC (PSPFS225, offset local 895488)→KITAJIMA_KARI.IMY (DSARC17, offset 57856, tamaño 2480), SHA `0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190`. Offset ISO absoluto 114723840 = 0x06D68C00: **NO es PSP RAM**. Sonda cambió 27 bytes RGB y seis iconos de CONTROLES, 348 vecinos PSPFS y 26 DSARC intactos. No extrapolar a HUD/combate.

## 3. Nuevo avance binario real: los 27 IMY decodificados y variantes de paleta

El relevo anterior autenticó nuevamente la ISO USA real y reconstruyó **27/27** miembros de SYSGRA.ARC íntegramente en memoria, sin exportar imágenes. Contenedor original SYSGRA.ARC SHA `63d9443084a2aeab8c2a3f79aebdb130eaf6c5d2e86f8be51346d7458ab81854`, 93696 bytes, DSARC con 27 registros. Herramienta `tools/f2_auditar_27_imy_sysgra.py` con **25 pruebas sintéticas** en `tests/test_f2_auditar_27_imy_sysgra.py`, commit de código `70d3aed096f57234fb66038c320cef2e21311b49`. Ambas GitHub Actions `push 45042960385` y `pull_request 45042967194` SUCCESS, **274 pruebas Python**, Go, integridad y compilación pública Windows. CI NO prueba PPSSPP real.

Dos variantes IMY identificadas sobre datos originales:
- Modo cabecera `0x60`: paleta con 16 entradas RGBA; flags en `0x60`; **14 recursos**.
- Modo cabecera `0x20`: paleta con 256 entradas RGBA; flags en `0x420`; **13 recursos**.
- 23 cabeceras de formato `0xA4` y 4 de `0x84`. 14 archivos terminan con dos bytes nulos, y 13 sin relleno final. Algunos streams tienen 1–3 comandos nulos de alineación. El decodificador falla ante relleno inválido, solapamiento DSARC, longitudes inválidas, tipo/codec no admitido, geometría errónea o SHA original incorrecto.
- **24 superficies de índices descomprimidas únicas** entre 27 IMY. `PALETE_0.IMY`, `PALETE_1.IMY`, `PALETE_2.IMY` y `PALETE_3.IMY` comparten SHA de índices `076a27c79e5ace2a3d47f9dd2e83e4ff6ea8872b3c2218f66c92b89b55f36560` (512 bytes); almacenan cuatro paletas RGBA256 con hashes diferentes. Esto prueba variantes de COLOR almacenadas, NO dónde/si se seleccionan durante la ejecución.
- `SYSGRA.ARC/FONT.IMY` tiene textura indexada 256×256 y SHA decodificada `5d4ff855af1132ea0abf204b5a4c44ddce28b55758772feba21ce6163cc6c4fc`; `FONT.ARC/FONT_00.IMY` 512×256, SHA `7bb085850b0eca09d03e6553565cd687be16d3af76fac2de076bc23b82cff3eb`. Son imágenes distintas pero sus funciones en juego requieren PPSSPP.
- Auditoría completa previa de cuatro contenedores DSARC: `SYS.DAT2` 6 PNG, `SE.ARC` 68 SPS, `SYSGRA.ARC` 27 IMY, `FONT.ARC` 7 recursos =108 miembros con 108 SHA almacenados diferentes.

Informe REAL PRIVADO de metadatos de 27: `CLADUN_F2_SYSGRA_27_IMY_Decodificados_privado_2026-11-22.json`, tamaño 32673 bytes, SHA-256 `b17966be9d0f3a40570893453f38a5b6a24a52ec928427bc237680bfad24d717`. **NO contiene píxeles, matrices de índices ni paletas crudas.** Los nombres `HP_BAR`, `DAMAGE`, `EXP_BAR`, `MAHO_BAR`, `SYS1` etc. son aún hipótesis de uso HUD/batalla por nombre.

## 4. PRIORIDAD EXCLUYENTE: PPSSPP auténtico, iconos RAM→GE→VRAM y 19 glifos

Comprobar primero si existe un binario oficial PPSSPP 1.20.4 en el sistema; si no, intentar el AppImage desde https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4 y autenticar SHA exacto ANTES de ejecutarlo. El último entorno no resolvía `github.com` desde terminal y NO tenía PPSSPP ni ISO F1 canónica. No fingir instalación/ejecución, capturas ni GE. Si no es posible, desarrollar y validar otra mejora técnica auténtica y registrar el bloqueo preciso.

Recuperar F1 privada canónica o reconstruirla mediante el integrador oficial conservando `--experimental-parcial --event-safe-only`, verificar el SHA esperado, mantener ISO USA inalterada. Para PPSSPP usar Xvfb 1280×720 y ventana 960×544, scrot auténtico para regresión. Con CONTROLES abierto, debugger `ws://127.0.0.1:24192/debugger`, subprotocolo `debugger.ppsspp.org`. Confirmar `version`, `game.status`, `cpu.status`. Eventos válidos: `memory.read`, `memory.disasm`, `memory.breakpoint.list/add/remove`, `cpu.getAllRegs`, `cpu.stepping/resume`, `gpu.buffer.screenshot`, `gpu.record.dump`. NO inventar `cpu.breakpoint.hit` ni `gpu.displaylist.disasm`.

Con CPU **corriendo** y carpeta privada nueva, ejecutar:
`python tools/f2_ppsspp_ws_1204.py --scene CONTROLES --salida-privada /tmp/cladun-f2-controles-real-nuevo --port 24192 --ge-dump`
`python tools/f2_ge_dump_1204.py --entrada-privada /tmp/cladun-f2-controles-real-nuevo/CONTROLES_GE_PRIVATE.dump --reporte-privado /tmp/cladun-f2-ge-real-nuevo.json`
`python tools/f2_ram_provenance_1204.py --iso-usa /PRIVATE/USA.iso --salida-privada /tmp/cladun-f2-origen-real-nuevo --solo-origen`

Después `--scan-ram` con CPU detenida/ticks estables; `--watch-address 0xDIRECCION_PSP_RAM` SOLO si hay coincidencia real exacta y en sesión controlada nueva, nunca el offset ISO 0x06D68C00. Conservar pausas y breakpoints ajenos; atribuir solo cuando `reason == "memory.breakpoint"` y `relatedAddress` coincidan. Exigir PC MIPS auténtico, lectura/descompresión, dirección RAM, TEXTADDR/CLUT, PRIM/TRANSFERSTART, datos transferidos a VRAM y píxeles finales correlacionados. Un hash, un candidato de dirección GE o una firma RAM aislada NO prueban la cadena.

Probar los iconos en CONTROLES, HUD, tutorial, ayuda, diálogos y combate SEPARADAMENTE, con controles positivos/negativos y dos PNG reales por pantalla con SHA privado. Para colores, comparar paletas PALETE_0..3 mediante evidencia REAL de selección, no solo nombre. Contrastar SYSGRA/FONT.IMY y FONT.ARC/FONT_00.IMY en cada contexto.

Validar en PPSSPP cada uno de los 19 glifos `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō`, avance/ancho/interlineado, tildes y clipping (í repetida x4, mayúsculas y15), botones □○×△ y L/R, color CLUT y cambios de línea. Si faltan ejemplos, crear CSV diagnóstico PRIVADO a partir de 9237 registros con `tools/generar_probe_f2_glifos.py`, sin modificar corpus canónico; comparar `tools/generar_probe_f2_tinta.py` sin habilitar tinta blanca por defecto. Repetir F1 Opciones y medir ventana X11 960×544, 756/~764, 005709/005710 Sí/005713 No y navegación.

## 5. Blindaje binario y pruebas

Preservar 349 registros PSPFS, 345 fuera de cuatro contenedores autorizados, 348 vecinos PSPFS para sonda aislada FONT.ARC/SYSGRA.ARC y 26 vecinos DSARC de KITAJIMA; ISO9660 ajeno intacto; SCRIPT.DAT 51705 comandos, 46308 no textuales, 1625 inicios, cero desplazamientos y 4524 textos script pospuestos. **NUNCA retirar `--event-safe-only`.** BPS solo PRIVADO/experimental con `--experimental --event-safe-only`, hash de fuente/candidata y roundtrip. Mantener PR DRAFT.

En checkout disponible:
`python -m unittest discover -s tests -v`
`python tools/verificar_integridad.py --raiz .`
`python tools/verificar_borrador_es.py`
`python tools/auditar_preinsercion_es.py --reporte /tmp/f2-preflight.json`
`python tools/reportar_integrabilidad_es.py --reporte /tmp/f2-integrabilidad.json`
`python tools/f2_auditar_origen_iconos.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-origen.json`
`python tools/f2_qa_raster_19.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-19.json`
`python tools/f2_inventario_sysgra_usa.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-sysgra.json`
`python tools/f2_catalogo_global_dsarc_usa.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-dsarc.json`
`python tools/f2_auditar_dos_fuentes_imy.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-dos-imy.json`
`python tools/f2_auditar_27_imy_sysgra.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-27-imy.json`
`(cd patcher && go test ./...)`
`git diff --check`

Cuando Git local no esté disponible, obtener resultados de Python/Go/Windows e integridad desde GitHub Actions del **HEAD FINAL**, no afirmar que ejecutaste los comandos localmente. Verificar `push` y `pull_request` SUCCESS en el HEAD final y que PR #7 sigue DRAFT.

## 6. Relevo obligatorio y fases siguientes

F2 ABIERTA hasta PPSSPP real con iconos trazados RAM→MIPS→GE→VRAM, los 19 glifos en varios contextos y F1 regresada auténticamente. F3: corregir la intro aún inglesa; F4: analizar saltos y referencias de 4524 textos script; F5: jugar aventura, combate, HUD, retratos, inventario, enciclopedia, guardar y cargar; F6: BPS final, EXE Windows y QA integral de principio a fin. Sin merge hasta verificar.

Al terminar **actualizar GitHub**: herramientas/tests, informe técnico, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, hashes privados y datos NO GENERADOS/NO PROBADOS. Reescribir POR COMPLETO `prompts/SIGUIENTE_TAREA.md` con otro prompt autónomo, fechado, completo y con nueva obligación recursiva, mostrarlo ÍNTEGRO al usuario. **RECURSIVIDAD OBLIGATORIA HASTA IMPLEMENTAR Y DEMOSTRAR F2, F3, F4, F5 Y F6.**
