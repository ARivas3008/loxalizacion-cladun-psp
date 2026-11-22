# CLADUN ES — RELEVO AUTÓNOMO F2: verificar inglés incrustado en gráficos y demostrar iconos/fuentes en PPSSPP real

Actúa como especialista sénior PSP MIPS, PPSSPP 1.20.4 oficial y su WebSocket debugger, GPU GE y VRAM, PSPFS/DSARC, IMY y CLUT, descompresión/swizzle 4 bpp, texto CP932, BPS y QA de juegos. **Ejecuta cambios reales, pruebas reproducibles y commits en GitHub**. No finjas que una imagen decodificada de la ISO es una captura de PPSSPP; no atribuyas contexto a un recurso por su nombre o contenido sin prueba funcional. No inventes hashes, registros MIPS/GE, direcciones RAM/VRAM ni resultados.

**RELEVO RECURSIVO OBLIGATORIO:** al finalizar, REESCRIBE POR COMPLETO el archivo `prompts/SIGUIENTE_TAREA.md` con otro prompt integral, autónomo y actualizado que vuelva a exigir literalmente la misma obligación. Muéstralo íntegramente al usuario. Repetir hasta completar y demostrar F2, F3, F4, F5 y F6; jamás prometer trabajo en segundo plano.

## 1. Repositorio, seguridad y lectura previa

Repositorio: https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama: `integracion-eventos-segura-20261120`.
PR #7: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7, base `revision-manual-dialogos`, mantener **DRAFT**, no merge, no force push.

Antes de editar, verificar HEAD, tree SHA, estado PR y ambas Actions de ese HEAD. Intentar localmente `git fetch origin`, `git switch integracion-eventos-segura-20261120`, `git pull --ff-only`, `git status --short`, `git rev-parse HEAD`. En el entorno precedente Git falló por `Could not resolve host github.com`; usar el conector GitHub con `expected_sha` si se repite; no afirmar fetch/pull falsos.

Leer íntegramente `AGENTS.md`, `README.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, `docs/RESULTADO_F1_PPSSPP_2026-11-21.md`, `docs/RESULTADO_F2_ATLAS_PPSSPP_2026-11-21.md`, `docs/F2_ICONOS_TINTA_PPSSPP_2026-11-21.md`, `docs/F2_AUDITORIA_ORIGEN_SOLO_LECTURA_2026-11-21.md`, `docs/F2_QA_ESTATICA_WS_2026-11-21.md`, `docs/F2_LECTOR_GE_V6_2026-11-21.md`, `docs/F2_RELEVO_CAPTURA_RAM_2026-11-21.md`, `docs/F2_FE_ERRATAS_SHA256_SNAPSHOT_RAM_2026-11-21.md`, `docs/F2_RELEVO_WS_BREAKPOINT_2026-11-21.md`, `docs/F2_PREPARACION_DIRECCIONES_GE_2026-11-21.md`, `docs/F2_INVENTARIO_SYSGRA_2026-11-22.md`, `docs/F2_CATALOGO_GLOBAL_DSARC_2026-11-22.md`, `docs/F2_DOS_FUENTES_IMY_DECODIFICADAS_2026-11-22.md`, `docs/F2_SYSGRA_27_IMY_PALETAS_2026-11-22.md` y **NUEVO** `docs/F2_PREVISUALIZACION_PRIVADA_SYSGRA_TEXTO_EN_GRAFICOS_2026-11-22.md`. Leer `reports/` relevantes, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, este prompt, `tools/`, `tests/`, `patcher/` y `.github/workflows/`.

**PROHIBICIÓN DE PUBLICACIÓN:** no subir a GitHub ISO, BPS, EBOOT, DATA.DAT, FONT.ARC, imágenes del juego, IMY, fuentes comerciales, RAM, GE dump, texturas ni PNG de previsualización. Solo código, pruebas sintéticas, documentación, métricas y hashes. Los materiales comerciales y pruebas privadas permanecen fuera del repo.

## 2. Fuentes binarias auténticas y estado consolidado

ISO USA original del usuario: **305496064 bytes**, SHA256 `b73b263fce863e51a0e27d0d11d6bde2886e439a18e2bb186d497619a1b79f`; nunca usar el antiguo hash de 62 caracteres. ISO F1 canónica previa SHA `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`, BPS USA→F1 SHA `daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd`. PPSSPP Linux AppImage oficial v1.20.4 SHA `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`.

F1 Opciones pasó **históricamente PPSSPP real** con Xvfb 1280×720, ventana auténtica 960×544, 756px interiores y ~764 exteriores, ID 005709 diez espacios ideográficos más 7 ASCII, 005710 Sí, 005713 No con espacio ASCII. Nueva regresión X11 aún no repetida; framebuffer PSP no prueba tamaños de ventana X11.

F2 conserva 2721 glifos originales más 19 español A1–B3 = 2740: `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō`. CLUT15 amarilla RGB247,247,0, CLUT1 blanca 255,255,255; `white_new_ink=True` opcional modifica solo 100 texels nuevos, **NO habilitar por defecto** sin QA F1+19 en PPSSPP. PC `0x089089C8` y tabla `0x09075000` son evidencia de búsqueda de TEXTO, no iconos. Iconos CONTROLES demostrados históricamente con sonda magenta en `SYSGRA.ARC/KITAJIMA_KARI.IMY` (DSARC17; tamaño2480; SHA `0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190`). Offset ISO 114723840=0x06D68C00 NO es PSP RAM. No extrapolar a otras escenas.

ISO usa DATA.DAT PSPFS de **349 recursos** y cuatro contenedores DSARC: SYS.DAT2 (6), SE.ARC (68), SYSGRA.ARC (27), FONT.ARC (7), total 108 recursos; 108 SHA de miembros distintos. SYSGRA.ARC (PSPFS225, offset local895488) ocupa 93696 bytes SHA `63d9443084a2aeab8c2a3f79aebdb130eaf6c5d2e86f8be51346d7458ab81854`. Se decodificaron 27/27 IMY en memoria, 24 superficies de índices únicas; 14 paletas de 16 RGBA y 13 de 256; PALETE_0..3 comparten la misma matriz de índices y tienen cuatro RGBA diferentes. No se ha demostrado su selección en PPSSPP.

Dos recursos FONT distintos: SYSGRA/FONT.IMY 256×256 4bpp, SHA decodificada `5d4ff855af1132ea0abf204b5a4c44ddce28b55758772feba21ce6163cc6c4fc`; FONT.ARC/FONT_00.IMY 512×256 4bpp, SHA `7bb085850b0eca09d03e6553565cd687be16d3af76fac2de076bc23b82cff3eb`. Sin función de contexto todavía.

## 3. NUEVO hallazgo de localización: texto inglés dibujado en TUIKA_MES.IMY

El relevo precedente reconstruyó gráficamente TODOS los IMY originales de SYSGRA aplicando descompresión real, unswizzle GE 16×8 y paletas RGBA verdaderas, sin utilizar PPSSPP. Previsualización privada: `Cladun_F2_Atlas_SYSGRA_27_Previsualizacion_Privada_NO_PPSSPP_2026-11-22.png`, **177957 bytes**, SHA `947f7a0b2ae98a879dc57fd5c6d8dc7b655cf6b80af3389073fcab5fc4e7ed7f`. Detalle privado de texto `Cladun_F2_TUIKA_MES_Texto_Embebido_Previsualizacion_Privada.png`, SHA `d2ecd78a2a816c49d7f4c79f3a744c3760b510764883603157d45a8861eaedcb`. Manifiesto privado `Cladun_F2_Previsualizacion_SYSGRA_Manifest_PRIVADO_2026-11-22.json`, SHA `a4e28f2fa9c055efb0a445625158213a1a9bb031a357ede43f16185e0a2be6ec`. Estos PNG contienen arte original, NO subirlos al repo.

**TUIKA_MES.IMY** almacenado SHA `c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127` contiene *texto inglés embebido como píxeles* claramente legible: «Gamble Merchant LV.», «Angel Guard LV.», «Nullified traps!», «Scattered G!», «Replenished HP for all!», «Recovered SP!», «Attack all enemies on screen!» y «No special attack». Por tanto, los 9237 textos de corpus no constituyen necesariamente TODAS las palabras visibles: hay una tarea de **localización gráfica potencial**. Aún NO está demostrado en qué escenas se usa ni se ha repintado el recurso. No editarlo antes de probar su uso real y estudiar límites de ancho/compresión/reubicación.

La vista previa también muestra iconos en `SYS1.IMY`, rótulos «LV Mana HP SP ATK DEF CRI BRK Walk Run» en `MAHO_ST.IMY` y números en `DAMAGE.IMY`. Se describe únicamente el **contenido del asset**, no su función de ejecución.

**Código nuevo:** `tools/f2_previsualizar_sysgra_privado.py`, salida PNG solo a ruta absoluta **externa al checkout**, rechaza symlink hacia el repo, colisiones y overwrite. Sus tests `tests/test_f2_previsualizar_sysgra_privado.py` agregan 17 pruebas sintéticas de swizzle/nibbles/CLUT y rutas privadas. Commit `a440785480a4fa8eee8bfb68c47ee0d065c3e71b`; Actions push `45045487042` y PR `45045491994` ambas SUCCESS, **291 pruebas Python**, integridad, Go y build Windows sin BPS. CI no equivale a PPSSPP.

## 4. Prioridad F2: PPSSPP 1.20.4 y pruebas funcionales controladas

Localizar binario PPSSPP 1.20.4 auténtico desde https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4 y autenticar SHA antes de ejecutar. En el último entorno: NO instalado; `curl` y `git fetch` fallan por DNS de github.com; descarga host también falló; NO hay ISO F1 canónica. Si persiste, documentar fallo, no simular gameplay, hacer mejora técnica distinta reproducible.

Con PPSSPP y fuente F1 privada auténticas, volver a probar Opciones F1 X11 960×544, ancho interior756/~764 y 005709/005710/005713 con navegación. Continuar con screenshots PPSSPP auténticos y originales, dos por escena en carpetas PRIVADAS, hashes individuales: CONTROLES, tutorial, HUD, ayudas, combate, diálogos. No llamar PNG estáticos de atlas capturas reales.

Depurador real `ws://127.0.0.1:24192/debugger`, subprotocolo `debugger.ppsspp.org`. Verificar `version`, `game.status`, `cpu.status`. Eventos válidos `cpu.stepping/resume`, `memory.read/disasm`, `memory.breakpoint.list/add/remove`, `cpu.getAllRegs`, `gpu.buffer.screenshot`, `gpu.record.dump`; no inventar `cpu.breakpoint.hit` ni `gpu.displaylist.disasm`.

Comandos de la instrumentación existente, CPU corriendo para captura GE:
`python tools/f2_ppsspp_ws_1204.py --scene CONTROLES --salida-privada /tmp/cladun-f2-controles-real-nuevo --port 24192 --ge-dump`
`python tools/f2_ge_dump_1204.py --entrada-privada /tmp/cladun-f2-controles-real-nuevo/CONTROLES_GE_PRIVATE.dump --reporte-privado /tmp/cladun-f2-ge-real-nuevo.json`
`python tools/f2_ram_provenance_1204.py --iso-usa /PRIVATE/USA.iso --salida-privada /tmp/cladun-f2-origen-nuevo --solo-origen`

Después `--scan-ram` solo detenido/ticks estables; `--watch-address 0xDIRECCION_PSP_RAM` solo si existe coincidencia real y sesión nueva, nunca usar offset ISO. Respetar breakpoints ajenos, razón de pausa exacta `memory.breakpoint`, `relatedAddress` y PC MIPS genuinos. Confrontar recurso comprimido, RAM descomprimida, TEXADDR/CLUT, PRIM/TRANSFERSTART, VRAM y píxel observado. Un candidato GE o un hash aislado NO demuestra causalidad. Comparar KITAJIMA, SYS1, MAHO_ST, TUIKA_MES, las dos FONT y PALETE_0..3; controles positivos y negativos. Esta es la condición de procedencia funcional.

**TUIKA_MES**: primero demostrar mediante PPSSPP que aparece un rótulo de esta imagen, con sonda privada de CLUT o modificación local aislada, y verificar 26 DSARC vecinos / 348 PSPFS vecinos. Si aparece, planificar traducción en el atlas: pixel art compatible, texto español, longitud/avance, CLUT, IMY recompresión segura, índices/offsets intactos; no subir recurso ni alterar fuentes sin integridad binaria. Separar F2 iconos de F3 intro y otras cadenas incrustadas.

## 5. Comprobaciones de glifos, integridad y no regresión

Validar VISUALMENTE los 19 glifos `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō` en PPSSPP real y varios contextos; anchos, avance, interlineado, tildes, clipping de «í» repetida y mayúsculas y15, color, □○×△, L/R y navegación. Sonda de CSV PRIVADA de 9237 registros mediante `tools/generar_probe_f2_glifos.py` y comparación de tinta `tools/generar_probe_f2_tinta.py`, sin tocar corpus canónico. Mantener `white_new_ink=False` hasta F1 regresada.

Seguridad de inserción: conservar 349 PSPFS, 345 recursos ajenos a cuatro contenedores, 348 vecinos PSPFS en modificaciones aisladas FONT/SYSGRA, 26 vecinos DSARC para KITAJIMA/TUIKA, ISO9660 restante, SCRIPT.DAT 51705 comandos, 46308 no textuales, 1625 inicios, cero desplazamientos, 4524 textos script pospuestos. Nunca eliminar `--event-safe-only`; usar `--experimental-parcial --event-safe-only` en ISO candidata y `--experimental --event-safe-only` para BPS privado experimental, SHA/roundtrip obligatorio.

Si el checkout está disponible, ejecutar:
`python -m unittest discover -s tests -v`
`python tools/verificar_integridad.py --raiz .`
`python tools/verificar_borrador_es.py`
`python tools/auditar_preinsercion_es.py --reporte /tmp/f2-preflight.json`
`python tools/reportar_integrabilidad_es.py --reporte /tmp/f2-integrabilidad.json`
`python tools/f2_auditar_origen_iconos.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-origen.json`
`python tools/f2_qa_raster_19.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-glifos.json`
`python tools/f2_inventario_sysgra_usa.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-sysgra.json`
`python tools/f2_catalogo_global_dsarc_usa.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-dsarc.json`
`python tools/f2_auditar_dos_fuentes_imy.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-fuentes.json`
`python tools/f2_auditar_27_imy_sysgra.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-27-imy.json`
`python tools/f2_previsualizar_sysgra_privado.py --iso-usa /PRIVATE/USA.iso --salida-privada /PRIVATE/atlas-unico.png`
`(cd patcher && go test ./...)`
`git diff --check`

Si falla red Git local, ejecutar lo posible con ISO privada y comprobar Python, integridad, Go y Windows desde ambas GitHub Actions del HEAD final. NO reclamar emulación desde CI.

## 6. GitHub final y obligación recursiva F3–F6

Al finalizar este relevo, publicar solo código, tests y documentación con hashes genuinos, actualizar `reports/ESTADO_CONTINUIDAD_PPSSPP.json` y `reports/RESULTADO_F2_...json`, verificar PR #7 DRAFT sin fusionar y ambas Actions `push`/`pull_request` SUCCESS para SHA final.

F2 se mantiene ABIERTA hasta demostrar en PPSSPP fuente/iconos con MIPS/RAM→GE→VRAM, los 19 glifos multicontesto, textos gráficos TUIKA_MES y F1 regresada X11. F3 intro aún inglesa; F4 ingeniería segura de referencias de 4524 cambios SCRIPT.DAT; F5 recorrido integral, combates/HUD/inventario/retratos/guardados; F6 BPS final, EXE Windows y QA. No declarar 100% por pruebas estáticas.

**AL FINAL ES IMPRESCINDIBLE REESCRIBIR TOTALMENTE `prompts/SIGUIENTE_TAREA.md` CON OTRO PROMPT AUTÓNOMO QUE IMPONGA ESTA MISMA RECURSIVIDAD, Y MOSTRARLO ÍNTEGRO AL USUARIO. REPETIR HASTA QUE F2–F6 SEAN AUTÉNTICAMENTE COMPLETADAS Y PROBADAS.**
