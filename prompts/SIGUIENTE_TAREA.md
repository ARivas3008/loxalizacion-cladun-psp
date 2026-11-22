# CLADUN ES — RELEVO AUTÓNOMO F2: PPSSPP auténtico, 14 franjas TUIKA, capturas A/B, 19 glifos, MIPS→GE y F3–F6

Actúa como especialista PSP MIPS, PPSSPP oficial 1.20.4, depurador WebSocket, GPU GE/VRAM, DSARC/PSPFS/ISO9660, IMY 4bpp, CLUT y localización CP932 española. **Debes experimentar de verdad, ejecutar pruebas, corregir código, conservar seguridad de binarios y actualizar GitHub**. Separa evidencia de bytes ISO originales, tests sintéticos/CI y gameplay REAL en PPSSPP. No inventar emulación, capturas, direcciones MIPS/RAM/VRAM, hashes ni resultados.

**RECURSIVIDAD OBLIGATORIA HASTA COMPLETAR F2–F6:** Al terminar REESCRIBE COMPLETAMENTE el propio archivo `prompts/SIGUIENTE_TAREA.md` con otro NUEVO prompt autónomo completo e integral, que vuelva a exigir esta misma reescritura recursiva y muéstralo ÍNTEGRO al usuario. Nunca prometer trabajo en segundo plano.

## 1. GitHub y lectura íntegra requerida

Repositorio https://github.com/ARivas3008/loxalizacion-cladun-psp. Rama `integracion-eventos-segura-20261120`. PR #7 borrador https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7, base `revision-manual-dialogos`. Mantener **DRAFT**, prohibido force push y merge.

Primero verificar HEAD, tree SHA, PR y workflows `push`/`pull_request` sobre exactamente el mismo HEAD. Intentar `git fetch origin`, `git switch integracion-eventos-segura-20261120`, `git pull --ff-only`, `git status --short`, `git rev-parse HEAD` en checkout local. Entornos previos: DNS de github.com roto; si falla NO declarar git sincronizado, usar conector GitHub `expected_sha`.

Leer COMPLETOS `AGENTS.md`, `README.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, `docs/RESULTADO_F1_PPSSPP_2026-11-21.md`, `docs/RESULTADO_F2_ATLAS_PPSSPP_2026-11-21.md`, `docs/F2_ICONOS_TINTA_PPSSPP_2026-11-21.md`, `docs/F2_AUDITORIA_ORIGEN_SOLO_LECTURA_2026-11-21.md`, `docs/F2_QA_ESTATICA_WS_2026-11-21.md`, `docs/F2_LECTOR_GE_V6_2026-11-21.md`, `docs/F2_RELEVO_CAPTURA_RAM_2026-11-21.md`, `docs/F2_FE_ERRATAS_SHA256_SNAPSHOT_RAM_2026-11-21.md`, `docs/F2_RELEVO_WS_BREAKPOINT_2026-11-21.md`, `docs/F2_PREPARACION_DIRECCIONES_GE_2026-11-21.md`, `docs/F2_INVENTARIO_SYSGRA_2026-11-22.md`, `docs/F2_CATALOGO_GLOBAL_DSARC_2026-11-22.md`, `docs/F2_DOS_FUENTES_IMY_DECODIFICADAS_2026-11-22.md`, `docs/F2_SYSGRA_27_IMY_PALETAS_2026-11-22.md`, `docs/F2_PREVISUALIZACION_PRIVADA_SYSGRA_TEXTO_EN_GRAFICOS_2026-11-22.md`, `docs/F2_SONDA_MAGENTA_TUIKA_CLUT_PPSSPP_PENDIENTE_2026-11-22.md` y NUEVO `docs/F2_TUIKA_CLUT2_CONTADOR_PIXEL_MASK_2026-11-22.md` y NUEVO `docs/F2_RELEVO_COTEJO_AB_2026-11-22.md` y NUEVO `docs/F2_MAPA_FRANJAS_TUIKA_2026-11-22.md`. Leer `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `reports/RESULTADO_F2_TUIKA_CLUT2_PIXELES_2026-11-22.json`, NUEVO `reports/RESULTADO_F2_COTEJO_CAPTURAS_AB_2026-11-22.json` y NUEVO `reports/RESULTADO_F2_MAPA_FRANJAS_TUIKA_2026-11-22.json`, informes F2 anteriores, este prompt, código `tools/`, tests, integrador, parcheador Go y workflows.

Prohibido subir a GitHub ISO, BPS, DATA.DAT, EBOOT, IMY, FONT.ARC, PNG originales/retocados, RAM, dumps GE/VRAM, imágenes comerciales, ejecutables de juego. Solo código, tests sintéticos, hashes, métricas y documentación. Archivos privados fuera del repositorio.

## 2. Fuente auténtica y estado probado

ISO original USA de usuario extraída del 7z: **305496064 bytes**, SHA-256 exacto de 64 caracteres `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. ISO F1 canónica histórica SHA `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`, BPS USA→F1 `daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd`. PPSSPP AppImage oficial Linux v1.20.4 SHA `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`. Rechazar SHA USA truncado (ver `tests/test_f2_sha256_references.py`).

F1 Opciones aprobada **históricamente** en PPSSPP real: Xvfb 1280×720, ventana X11 960×544, caja interior 756px/exterior ~764px, 005709 diez espacios ideográficos más siete ASCII, 005710 «Sí», 005713 «No» y un espacio ASCII de presentación. **Sin regresión nueva todavía**. El framebuffer PSP no prueba ancho de ventana X11.

F2: 2721 glifos originales preservados más 19 nuevos A1–B3 `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō` =2740. FONT_00.IMY CLUT15 amarillo RGB(247,247,0) frente CLUT1 blanco RGB(255,255,255), `white_new_ink=True` optativo cambiaría 100 texels nuevos; mantener **False** predeterminado hasta PPSSPP multicontesto. MIPS PC `0x089089C8`, tabla RAM `0x09075000` son búsqueda de TEXTO, NO PC de iconos. Iconos Controles KITAJIMA_KARI.IMY demostrados históricamente mediante perturbación magenta, otros contextos y rutina MIPS→GE no demostrados.

DATA.DAT tiene 349 PSPFS; cuatro contenedores DSARC SYS.DAT2 (6 PNG), SE.ARC (68 SPS), SYSGRA.ARC (27 IMY), FONT.ARC (7) =108 miembros. Dos fuentes distintas `SYSGRA.ARC/FONT.IMY` 256×256 vs `FONT.ARC/FONT_00.IMY` 512×256; su función real por escena sigue sin resolverse.

## 3. AVANCES AUTÉNTICOS: TUIKA, 9144 píxeles estáticos y réplica independiente de la sonda

`TUIKA_MES.IMY` (SYSGRA.ARC PSPFS225, DSARC24) contiene texto inglés **gráfico** —por ejemplo «Replenished HP for all!», «Recovered SP!», «Attack all enemies on screen!», «No special attack»— que no está garantizado por las 9237 entradas textuales del corpus. El recurso en sí fue auditado, no su contexto de aparición en el juego.

Sonda original/privada ya generada:
- ISO USA SHA `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.
- ISO experimental CLUT2 magenta SHA `b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa`.
- Solo **3 bytes RGB** cambiados (offset absoluto ISO decimal 114744872–114744874), RGBA antes (249,251,249,255), después (255,0,255,255). No cambió alfa; **348 de 348 PSPFS vecinos y 26 de 26 miembros DSARC vecinos** intactos, tablas y el resto de la ISO bit a bit sin alterar.
- Código de generación `tools/f2_probe_tuika_palette_privado.py`, pruebas sintéticas (22).

**NUEVO**: `tools/f2_cotejar_impacto_clut_tuika.py` reconstruye la textura original en memoria, compara ISO originales y de prueba con SHA completos y usa descompresión IMY + unswizzle PSP 16×8. Índices 4bpp antes/después son idénticos (SHA `3c181786f72008c144a2187d362d289d453b4f00d93fe5f8cb2facc0f23d14d5`), superficie 256×256 =65536 píxeles. **9144** usan índice2 (13,952637 %) y cambiarían de blanco a magenta en render directo de ese atlas; otros **56392** sin cambio. Píxeles activos en 200 filas, **14 franjas horizontales**, máscara de efecto SHA `382ae8d2ffa8908979050b5e83f38ec9967b461bbf9b614dd92775da90e409ba`. Test suite `tests/test_f2_cotejar_impacto_clut_tuika.py` añade **19 tests**. Commit de código `3241f5ca9463e202e3b9b1371bf0deefa52f4673`, CI push `45052513223`, PR `45052519322`, **332 tests Python**, Go/integridad/build Windows sin BPS. Estos son tests binarios/sintéticos, NO PPSSPP. **NUEVO RELEVO 22/11:** en un entorno distinto se extrajo de nuevo la ISO 305496064 bytes del 7z del usuario mediante libarchive, y se reprodujo independientemente la ISO TUIKA magenta exacta. El cotejo íntegro de 305496064 bytes mostró SOLO las 3 diferencias 114744872–114744874, SHA sonda b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa, 349 PSPFS (348 vecinos idénticos) y 27 DSARC (26 vecinos idénticos), tablas intactas. No se ejecutó PPSSPP y la ISO F1 canónica no está presente en este entorno. **Nueva herramienta tools/f2_cotejar_capturas_tuika.py con 21 pruebas locales SINTÉTICAS PASS**, no representa capturas del juego. GitHub Actions del último relevo de cotejo A/B aprobaron **353 tests Python** con push run `45054922146` y PR run `45054926574`, HEAD `853d66f33439c689641a4570506fc95f9518e3fa`; no son pruebas de PPSSPP. Se efectuó otro relevo, detallado a continuación, con 18 pruebas sintéticas adicionales.

Comparación privada de tres paneles: `CLADUN_F2_TUIKA_CLUT2_ANÁLISIS_ESTATICO_NO_PPSSPP_2026-11-22.png`, SHA `ec595486a96922d2066883cee9e2d4d895c3eda4525168d4dc15d865c659f50b`; informe privado `CLADUN_F2_TUIKA_CLUT2_CUANTIFICACION_PRIVADA_2026-11-22.json`, SHA `4c0836c0661bebc876b6271bffb516f88de435df3af1efcf39c49dc36d169c8d`. PRIVADOS: no versionar ni reutilizar como «capturas PPSSPP». Esta sonda recolorea todo píxel CLUT2; NO se ha demostrado su uso real ni traducido gráficos.

Comandos **privados**, usar rutas nuevas sin overwrite:
```bash
python tools/f2_probe_tuika_palette_privado.py --iso-usa /PRIVATE/USA.iso --salida-iso-privada /PRIVATE/TUIKA_magenta.iso --reporte-privado /PRIVATE/TUIKA_probe.json
python tools/f2_cotejar_impacto_clut_tuika.py --iso-usa /PRIVATE/USA.iso --iso-sonda /PRIVATE/TUIKA_magenta.iso --reporte-privado /PRIVATE/TUIKA_pixeles.json --png-privado /PRIVATE/TUIKA_comparacion.png
```

## 4. NUEVO: cotejador A/B de capturas privadas, sin confundir ISO en disco con ISO cargada

Herramienta `tools/f2_cotejar_capturas_tuika.py`, tests `tests/test_f2_cotejar_capturas_tuika.py`. **21 de 21 tests locales sintéticos PASS**. Verifica que cada versión tenga exactamente dos PNG y un `manifest_PRIVATE.json` del cliente PPSSPP v1.20.4, título y escena coincidentes, tamaños/hash SHA256 auténticos de archivos, rutas privadas sin symlink ni overwrite, y SHA completos de ambas ISOs en disco. Computa diferencias por píxel y candidatos magenta, nunca inserta PNG o datos comerciales en su informe. Se ha probado con PNG **creados artificialmente SOLO para unit tests**, no con capturas PPSSPP.

CONTRAINDICACIÓN: ese comparador NO verifica que PPSSPP haya cargado realmente la ISO declarada ni que ambos cuadros estén perfectamente alineados. El reporte mantiene `runtime_loaded_iso_identity_proven=false`, `frame_alignment_verified=false` y `tuika_texture_runtime_origin_proven=false`. Cero candidatos magenta en una escena no demuestra ausencia de uso del atlas; un candidato magenta exige inspección manual de ROI/control negativo y la cadena MIPS/RAM/GE/VRAM.

En dos sesiones auténticas con juego original y sonda, respectivamente, crear DOS capturas PNG reales privadas cada una, con la **MISMA escena, mismo estado y misma versión**. Solo entonces ejecutar:

    python tools/f2_ppsspp_ws_1204.py --scene TUIKA_HABILIDADES --salida-privada /PRIVATE/ab_usa_NUEVO --port 24192 --ge-dump
    # Reiniciar PPSSPP con la ISO sonda, volver al mismo estado/escena:
    python tools/f2_ppsspp_ws_1204.py --scene TUIKA_HABILIDADES --salida-privada /PRIVATE/ab_probe_NUEVO --port 24192 --ge-dump
    python tools/f2_cotejar_capturas_tuika.py --manifest-usa /PRIVATE/ab_usa_NUEVO/manifest_PRIVATE.json --manifest-sonda /PRIVATE/ab_probe_NUEVO/manifest_PRIVATE.json --iso-usa /PRIVATE/USA.iso --iso-sonda /PRIVATE/TUIKA_magenta.iso --reporte-privado /PRIVATE/reporte_AB_NUEVO.json

Acreditar por separado el binario arrancado en PPSSPP; la etiqueta de escena del manifiesto no prueba identidad de disco. No usar esta herramienta como evidencia de F1 X11 960x544: PNG de framebuffer PSP y ventana desktop son observaciones distintas.

## 5. NUEVO: mapa auténtico de 14 franjas TUIKA, útil para localizar texto gráfico SIN autorizar ediciones

**22/11, nuevo relevo autenticado:** se extrajo el 7z del usuario con libarchive, se verificó la ISO original USA de 305496064 bytes con SHA exacto y se reconstruyó una sonda privada TUIKA de SHA `b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa`. Una comparación byte a byte completa halló solo 3 diferencias en offsets 114744872–874. Se verificó de nuevo el recurso IMY original `c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127`, raster indexado decodificado SHA `3c181786f72008c144a2187d362d289d453b4f00d93fe5f8cb2facc0f23d14d5` y máscara CLUT2 SHA `382ae8d2ffa8908979050b5e83f38ec9967b461bbf9b614dd92775da90e409ba`.

Nueva `tools/f2_mapa_franjas_tuika.py` calcula, exclusivamente desde la máscara en memoria, los límites de las 14 franjas CLUT2, x/y, separaciones, conteos y SHA256 por franja; prohíbe sobrescribir/salir a Git. `tests/test_f2_mapa_franjas_tuika.py` añade **18 pruebas SINTÉTICAS locales PASS**. Evidencia de análisis binario real: 14 franjas con suma **9144 píxeles / 200 filas**; dos franjas de altura 16, doce de 14. Sus intervalos y conteos (y inicio–fin, píxeles): (2–15,1110), (20–33,730), (38–51,534), (56–69,578), (74–87,564), (92–105,532), (110–123,432), (128–141,784), (146–159,504), (164–177,980), (181–196,422), (199–214,270), (218–231,600), (236–249,1104). Informe PRIVADO fuera de Git `TUIKA_14_FRANJAS_EVIDENCIA_ESTATICA_PRIVADA_20261122.json`, SHA `23f02aa43e4d153c3d62ff065676788c34d6116890f158466ab5c0d9cf8f866e`. NO publicar textura, ISO, PNG o bitmaps.

**IMPORTANTE:** el CLUT2 no es toda la imagen y sus bounding boxes pueden contener píxeles de otros índices; una banda NO se equipara a una frase ni es ROI editada segura. NO se tradujeron las franjas ni se aseguró aparición en gameplay. Solo con PPSSPP real identificar la escena de cada frase inglesa embebida, comparar control/sonda, textura cargada, MIPS→RAM→GE→VRAM y decidir un ROI o repack safe. Cero capturas PPSSPP nuevas, PPSSPP oficial ausente (GitHub DNS/descarga fallidas), ISO F1 canónica ausente y QA de 19 glifos sin repetir.

Comando real del analizador, **solo tras disponer de ambas ISOs privadas y rutas nuevas**:

    python tools/f2_mapa_franjas_tuika.py --iso-usa /PRIVATE/USA.iso --iso-sonda /PRIVATE/TUIKA_magenta.iso --reporte-privado /PRIVATE/TUIKA_franjas_nuevo.json

## 6. Prioridad real del siguiente relevo: PPSSPP y cadena funcional

Localizar auténtico PPSSPP Linux 1.20.4 https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4; verificar SHA exacto **antes de ejecutar**. Último entorno no lo tenía y `curl`/Git fallaban por DNS `Could not resolve host: github.com`; en el último relevo `container.download` también falló. La publicación oficial confirma AppImage SHA sin que ello implique que se haya descargado/ejecutado. Si persiste, registrar NO DISPONIBLE; nunca inventar captura/juego. Recuperar o reconstruir ISO F1 canónica de manera PRIVADA con `--experimental-parcial --event-safe-only` y SHA exacto, preservando original.

Con PPSSPP real, comparar las ISOs USA ORIGINAL y sonda TUIKA MAGENTA, en **idénticas escenas y controles**, dos PNG por versión, hashes y captures X11 privadas, idealmente mensajes de habilidades/tienda/ataque. Verificar ROI de letras, cambio a magenta y no cambios en iconos ajenos; si no aparecen cambios en una escena, no declarar nunca que no se usa TUIKA. Identificar uso de `SYS1.IMY`, `MAHO_ST.IMY`, `KITAJIMA_KARI.IMY`, las dos fuentes FONT y PALETE_0–3 por pruebas funcionales independientes, no por nombre de archivo.

Debugger oficial `ws://127.0.0.1:24192/debugger` subprotocolo `debugger.ppsspp.org`, comprobar `version`, `game.status`, `cpu.status`. Métodos reales `memory.read`, `memory.disasm`, `memory.breakpoint.list/add/remove`, `cpu.getAllRegs`, `cpu.stepping/resume`, `gpu.buffer.screenshot`, `gpu.record.dump`; NO inventar `cpu.breakpoint.hit`, `gpu.displaylist.disasm`. Ejecutar, con CPU corriendo:
```bash
python tools/f2_ppsspp_ws_1204.py --scene CONTROLES --salida-privada /tmp/f2-controles-real --port 24192 --ge-dump
python tools/f2_ge_dump_1204.py --entrada-privada /tmp/f2-controles-real/CONTROLES_GE_PRIVATE.dump --reporte-privado /tmp/f2-ge-real.json
python tools/f2_ram_provenance_1204.py --iso-usa /PRIVATE/USA.iso --salida-privada /tmp/f2-ram-real --solo-origen
```
Para `--scan-ram`, CPU detenida/ticks estables, watchpoint solo a dirección PSP RAM auténtica con coincidencia real, en sesión nueva, nunca offset ISO (ej. `0x06D68C00`). Respetar breakpoints ajenos. Confirmar evento `reason==memory.breakpoint`, `relatedAddress` correcto, PC MIPS real, descompresión/copia a RAM, TEXTADDR/CLUT, PRIM/TRANSFERSTART, VRAM y píxel final. Un hash o candidato GE NO prueban cadena causal.

## 7. QA F2 19 glifos, regresión F1, integridad y protección de scripts

Probar visualmente en PPSSPP real cada `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō` en CONTROLES/HUD/tutorial/ayuda/diálogo/combate y menús, capturas auténticas privadas. Revisar CLUT blanca/amarilla, altura, interlineado, recorte de «í» ×4 y mayúsculas y15, ancho y botones L/R □○×△. Diagnósticos CSV/ISO PRIVADOS con `tools/generar_probe_f2_glifos.py` y `tools/generar_probe_f2_tinta.py` sin alterar 9237 registros canónicos. Mantener `white_new_ink=False` hasta pruebas satisfactorias.

Regresión F1 Opciones con ventana **X11 real 960×544**, Xvfb 1280×720, medida scrot, 756/≈764 píxeles y IDs 005709/005710 Sí/005713 No y navegación; framebuffer PSP solo NO basta.

Invariantes: 349 PSPFS, 345 externos a cuatro DSARC autorizados, 348 vecinos en sondas aisladas, 26 DSARC vecinos TUIKA, ISO9660 restante sin cambio, SCRIPT.DAT **51705 comandos, 46308 no textuales y 1625 inicios**, desplazamientos cero, 4524 traducciones SCRIPT.DAT aplazadas. Prohibido retirar `--event-safe-only`; BPS exclusivamente experimental/privado `--experimental --event-safe-only`, comprobar source/output SHA y roundtrip. PR #7 DRAFT, no release final.

Con checkout auténtico:
```bash
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/integrabilidad.json
python tools/f2_auditar_origen_iconos.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/iconos.json
python tools/f2_qa_raster_19.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/19.json
python tools/f2_inventario_sysgra_usa.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/sysgol.json
python tools/f2_catalogo_global_dsarc_usa.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/dsarc.json
python tools/f2_auditar_dos_fuentes_imy.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/fuentes.json
python tools/f2_auditar_27_imy_sysgra.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/27.json
(cd patcher && go test ./...)
git diff --check
```
Si no hay checkout local real, comprobar pruebas Python/Go/Windows e integridad vía AMBAS GitHub Actions de SHA final; **NO atribuir esos resultados a PPSSPP**.

## 8. F3–F6 pendientes y RELEVO OBLIGATORIO

F2 ABIERTA hasta demostrar en PPSSPP 1.20.4 cadena MIPS→RAM→GE→VRAM de iconos y fuentes, uso real de mensajes gráficos TUIKA, 19 glifos en contextos pertinentes y regresión F1. F3 intro inglesa; F4 4524 scripts con referencias/saltos/eventos seguros; F5 recorrer historia, combate, HUD, inventario, retratos, enciclopedia, guardado/carga; F6 BPS final y EXE Windows con pruebas end-to-end. Nunca fusionar PR #7 ni declarar 100% antes.

AL FINAL: commit GitHub con código/tests/docs sin binarios comerciales, incluyendo 14 franjas TUIKA, hashes/métricas nuevos y el cotejo A/B, actualizar `reports/ESTADO_CONTINUIDAD_PPSSPP.json` y un informe de metadatos, verificar HEAD PR DRAFT y DOS Actions SUCCESS. **REESCRIBIR POR COMPLETO `prompts/SIGUIENTE_TAREA.md` CON OTRO PROMPT AUTÓNOMO ACTUALIZADO Y COMPLETO; VOLVER A EXIGIR A ESE RELEVO LA MISMA REESCRITURA RECURSIVA; MOSTRARLO ÍNTEGRO AL USUARIO. Repetir hasta F2–F6 autentificadas. El relevo debe preservar las 9237 traducciones, 4524 scripts aplazados, F1 aprobada históricamente y prohibición de publicar arte de juego.**
