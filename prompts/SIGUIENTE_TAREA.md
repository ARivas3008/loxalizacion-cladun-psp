# CLADUN ES — RELEVO AUTÓNOMO F2: validar dos fuentes originales en PPSSPP y cerrar RAM→GE→VRAM

Actúa como ingeniero sénior PSP MIPS, PPSSPP oficial v1.20.4 con depurador WebSocket, GPU GE/VRAM, IMY/CLUT, ISO9660/PSPFS/DSARC, CP932 español, BPS y QA funcional de videojuegos. Ejecuta experimentos reales, modifica herramientas/código cuando corresponda, corre pruebas, publica GitHub y entrega evidencia auténtica. **No se permite inventar capturas, PC MIPS, direcciones RAM o VRAM, hashes, logs ni resultados jugables.**

**OBLIGACIÓN RECURSIVA INNEGOCIABLE:** AL FINAL REESCRIBE ÍNTEGRAMENTE el archivo `prompts/SIGUIENTE_TAREA.md` con un NUEVO prompt completo, autónomo y actualizado que contenga esta MISMA obligación de regeneración y muéstralo íntegro al usuario. Continuar en sucesivos relevos hasta implementar y comprobar F2, F3, F4, F5 y F6. No prometer trabajo futuro o asíncrono.

## 1. GitHub, permisos y lectura obligatoria

Repositorio: https://github.com/ARivas3008/loxalizacion-cladun-psp

Rama: `integracion-eventos-segura-20261120`; PR #7: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7; base `revision-manual-dialogos`. Conservar PR **DRAFT**, NO fusionar. Antes de escribir, verificar HEAD, tree, PR y ambas GitHub Actions. En checkout local intentar exactamente:
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
git status --short
git rev-parse HEAD

Si falla la descarga Git por DNS, registrar fallo real y usar GitHub conectado con `expected_sha`; nunca force-push ni sustitución de trabajo ajeno. En el relevo previo la terminal devolvió `Could not resolve host: github.com` y el checkout local quedó sin rama/HEAD.

Leer completos: `AGENTS.md`, `README.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, `docs/RESULTADO_F1_PPSSPP_2026-11-21.md`, `docs/RESULTADO_F2_ATLAS_PPSSPP_2026-11-21.md`, `docs/F2_ICONOS_TINTA_PPSSPP_2026-11-21.md`, `docs/F2_AUDITORIA_ORIGEN_SOLO_LECTURA_2026-11-21.md`, `docs/F2_QA_ESTATICA_WS_2026-11-21.md`, `docs/F2_LECTOR_GE_V6_2026-11-21.md`, `docs/F2_RELEVO_CAPTURA_RAM_2026-11-21.md`, `docs/F2_FE_ERRATAS_SHA256_SNAPSHOT_RAM_2026-11-21.md`, `docs/F2_RELEVO_WS_BREAKPOINT_2026-11-21.md`, `docs/F2_PREPARACION_DIRECCIONES_GE_2026-11-21.md`, `docs/F2_INVENTARIO_SYSGRA_2026-11-22.md`, `docs/F2_CATALOGO_GLOBAL_DSARC_2026-11-22.md`, `docs/F2_DOS_FUENTES_IMY_DECODIFICADAS_2026-11-22.md`, informes F2 de `reports/`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, este prompt, `tools/`, `tests/`, `patcher/` y `.github/workflows/`.

**No publicar ISO, BPS, EBOOT, DATA.DAT, FONT.ARC, IMY, texturas, RAM, GPU dumps, capturas PNG comerciales ni ejecutables del juego en GitHub.** Mantener estas evidencias en una ruta PRIVADA; a GitHub únicamente código, tests, métricas, documentación y SHA.

## 2. Fuente original y precedentes exactos

ISO original USA privada, proveniente del 7z aportado por el usuario: 305496064 bytes y SHA256 canónico (64 hex):
`b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`

NO usar su antigua variante errónea de 62 caracteres. Mantener `tests/test_f2_sha256_references.py`. ISO F1 canónica privada SHA `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`; BPS experimental USA→F1 SHA `daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd`; PPSSPP AppImage oficial Linux v1.20.4 SHA `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`.

F1 Opciones **aprobada históricamente en PPSSPP REAL**: Xvfb 1280×720, ventana X11 960×544, ancho interior 756px y exterior ~764px; ID 005709 diez espacios ideográficos más 7 ASCII, ID 005710 Sí, ID 005713 No con espacio ASCII al final. La textura framebuffer PSP NO acredita dimensiones de una ventana X11. Repetir con captura real y navegación.

Fuente F2: 2721 glifos originales conservados, 19 A1–B3 añadidos =2740, cadena completa `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō`. Tabla RAM de TEXTO `0x09075000` y MIPS PC `0x089089C8` con `lhu t2,0(t1)`: no son prueba del código de ICONOS. CLUT15 amarilla RGB(247,247,0), índice1 blanco RGB(255,255,255). `white_new_ink=True` altera optativamente 100 texels solo nuevos; preservar `False` por defecto hasta validación completa.

Iconos CONTROLES demostrados históricamente mediante sonda magenta: DATA.DAT→SYSGRA.ARC (PSPFS225 offset895488)→KITAJIMA_KARI.IMY (DSARC17/27, offset57856, 2480 bytes) SHA `0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190`, offset ISO 114723840 (0x06D68C00) **NO dirección RAM**. 27 bytes RGB alterados y seis iconos cambiados, 348 PSPFS y 26 DSARC vecinos idénticos. No extrapolar a HUD, tutorial o combate sin más pruebas.

## 3. NUEVA evidencia reproducible: dos fuentes decodificadas NO iguales

En el relevo anterior se autenticó ISO USA REAL y se decodificaron EN MEMORIA los dos recursos IMY tipo 0xA4, sin exportar gráficos. La herramienta `tools/f2_auditar_dos_fuentes_imy.py` valida ISO exacta, firma de cada miembro, stream, offsets, flags y geometría, y guarda solo estadísticas. Pruebas sintéticas en `tests/test_f2_auditar_dos_fuentes_imy.py`: **16 nuevas**, commit de código `5242371ee8b0410a6456ee9241d81a453445b1c6`. Actions push `45041694305` y PR `45041700035` ambas SUCCESS: **249 pruebas Python**, Go, integridad y compilación Windows pública. No demuestran gameplay.

Resultados REALES del binario USA:
- `SYSGRA.ARC/FONT.IMY` (PSPFS225, DSARC14): 4148 bytes almacenados, SHA `50143c165f10aa71ac77d4a2b09fd69012b1eceac4a102bf8e2b8157bf8b5915`; decodificado 4bpp **256×256**, 32768 bytes, índices píxel CLUT **0,1,15**, SHA decodificada `5d4ff855af1132ea0abf204b5a4c44ddce28b55758772feba21ce6163cc6c4fc`.
- `FONT.ARC/FONT_00.IMY` (PSPFS308, DSARC1): 17468 bytes almacenados, SHA `698bc5b398a16c3f2a4615527dac6a36dbae73666a7c45c3787bb00a728a8478`; decodificado 4bpp **512×256**, 65536 bytes, índices **0,1**, SHA decodificada `7bb085850b0eca09d03e6553565cd687be16d3af76fac2de076bc23b82cff3eb`.

**Conclusión válida:** no son copias idénticas de la misma imagen ni en formato comprimido ni descomprimido. **No se ha determinado cuál se usa en menús, HUD ni diálogos, ni que uno dibuje textos concretos.** Las paletas efectivas y el renderizado solo se comprueban en PPSSPP. Informe de 2 texturas REAL/PRIVADO: `CLADUN_F2_dos_fuentes_decodificadas_metrica_privada_2026-11-22.json`, SHA `9d4f13e039ee18c176b45d34b21c2376ce2ffde78f2251179aa18743a3b6cb9b`.

Auditorías anteriores: cuatro contenedores DSARC: SYS.DAT2 (6 PNG), SE.ARC (68 SPS), SYSGRA.ARC (27 IMY), FONT.ARC (7 BIN/IMY), total 108 recursos y 108 SHA distintos. `tools/f2_catalogo_global_dsarc_usa.py`, `tools/f2_inventario_sysgra_usa.py`. Doce nombres sugestivos de HUD/combate son **solo candidatos**, no atribuciones: HP_BAR, HP_KAO0, HP_KAO1, HP_KAO2, LVSP, LVSP_NUM, DAMAGE, EXP_BAR, MAHO_BAR, MAHO_ST, SYS1, ZOKUSEI. Comparar funcionalmente con controles positivos y negativos.

## 4. PRIORIDAD: PPSSPP 1.20.4 REAL, depurador, RAM y GPU

Buscar AppImage oficial en https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4. Comprobar versión y SHA esperado antes de ejecutar, no instalar otro binario y declarar PPSSPP 1.20.4 sin autenticación. En el último entorno no hubo PPSSPP ni ISO F1; red por DNS `Could not resolve host github.com`. Si continúa el bloqueo, consignar `NO EJECUTADO` y buscar una mejora REAL reproducible diferente, sin fabricar capturas.

Recuperar ISO F1 canónica o reproducirla con integrador seguro desde USA, en ruta PRIVADA, sin sobrescribir original, preservar `--experimental-parcial --event-safe-only`, autenticar SHA F1 exacto. Xvfb a 1280×720 y ventana PPSSPP 960×544, medir con scrot SOLO SI el emulador real está abierto.

En CONTROLES auténticos, depurador `ws://127.0.0.1:24192/debugger` subprotocolo `debugger.ppsspp.org`; confirmar `version`, `game.status`, `cpu.status`. Admitidos: `memory.read`, `memory.disasm`, `memory.breakpoint.list/add/remove`, `cpu.getAllRegs`, `cpu.stepping/resume`, `gpu.buffer.screenshot`, `gpu.record.dump`. No inventar `cpu.breakpoint.hit` ni `gpu.displaylist.disasm`.

Con CPU corriendo, directorio PRIVADO NUEVO:
`python tools/f2_ppsspp_ws_1204.py --scene CONTROLES --salida-privada /tmp/f2-controles-REAL-nuevo --port 24192 --ge-dump`

Analizar solo un dump real:
`python tools/f2_ge_dump_1204.py --entrada-privada /tmp/f2-controles-REAL-nuevo/CONTROLES_GE_PRIVATE.dump --reporte-privado /tmp/f2-ge-REAL-nuevo.json`

Verificar origen comprimido RAM con:
`python tools/f2_ram_provenance_1204.py --iso-usa /PRIVATE/USA.iso --salida-privada /tmp/f2-ram-origen-REAL-nuevo --solo-origen`

Después `--scan-ram` en carpeta distinta con CPU detenida y ticks estables; solo si existe coincidencia PSP RAM exacta, nueva sesión y `--watch-address 0xDIRECCION_PSP_RAM` usando un depurador único, nunca 0x06D68C00. Atribuir pausas solo si `reason == "memory.breakpoint"` y `relatedAddress` igual a rango vigilado. Capturar PC MIPS realmente observado, lectura/descompresión RAM, selección CLUT, TEXADDR/PRIM/TRANSFERSTART y dirección VRAM candidata con bytes y dibujo final demostrados. Un hash de textura, una coincidencia RAM o un registro GE aislados NO prueban cadena causal.

Contrastar SEPARADAMENTE KITAJIMA, SYSGRA/FONT.IMY y FONT.ARC/FONT_00.IMY, además de los 12 candidatos, en CONTROLES, HUD, tutorial, ayuda, diálogos y combate; controls positivos y negativos, al menos DOS PNG PPSSPP auténticos por escena y SHA de cada uno, datos comerciales en PRIVADO. Para F1 exigir ventana X11 genuina 960×544, no framebuffer PSP.

## 5. Los 19 signos y seguridad integral

Verificar cada `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō` visualmente en varios contextos PPSSPP: ancho, advance, altura/acento, interlineado, recorte de `í` x4 y mayúsculas y15, interacción con □ ○ × △ y L/R, CLUT, navegación y retorno. Si faltan ejemplos naturales, generar CSV diagnóstico PRIVADO de 9237 registros con `tools/generar_probe_f2_glifos.py`, comparar `tools/generar_probe_f2_tinta.py` sin editar textos canónicos. No cambiar `white_new_ink=False` hasta F1 regresada.

Blindaje obligatorio: 349 PSPFS, 345 fuera de los cuatro contenedores autorizados, 348 vecinos PSPFS en sondas aisladas, 26 vecinos DSARC de KITAJIMA, otros archivos ISO9660 sin cambios; SCRIPT.DAT 51705 comandos, 46308 no textuales, 1625 inicios, 0 desplazamientos, 4524 traducciones de script pospuestas. NUNCA eliminar `--event-safe-only`. BPS solo experimental privado, `--experimental --event-safe-only`, SHA de entrada/salida y roundtrip exacto.

Ejecutar en checkout si es viable:
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
`(cd patcher && go test ./...)`
`git diff --check`

Si el Git directo sigue bloqueado, comprobar desde los logs GitHub Actions del HEAD FINAL: tests Python/Go, integridad, compilación pública Windows, PR DRAFT, SHA y branch; no presentar CI como emulación.

## 6. F3–F6 y relevo obligatorio

F2 sigue ABIERTA hasta demostrar el uso real en memoria/GE/VRAM de iconos y fuentes, 19 glifos multicontesto y F1 960×544. F3: intro todavía inglesa; F4: ingeniería y protección de saltos/referencias de 4524 cambios pendientes; F5: juego integral, diálogos, combates, HUD, retratos, inventario, enciclopedia, guardado/carga; F6: BPS final y EXE Windows, prueba de aplicación y QA end-to-end. Mantener PR #7 en DRAFT mientras falten.

Al terminar publicar SOLO informes, herramientas y tests, actualizar `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, hashes y estados NO PROBADO, y comprobar las DOS Actions del HEAD final. Nunca subir datos comerciales.

**RECURSIVIDAD OBLIGATORIA HASTA F2–F6 VERIFICADAS: REESCRIBE ÍNTEGRAMENTE `prompts/SIGUIENTE_TAREA.md` CON OTRO PROMPT AUTÓNOMO COMPLETO; INCLUYE ESTA MISMA OBLIGACIÓN Y MUÉSTRALO ÍNTEGRO AL USUARIO AL FINAL.**
