# CLADUN ES — RELEVO AUTÓNOMO F2: ejecutar sonda magenta TUIKA en PPSSPP, trazar GE/VRAM, 19 glifos y F1

Actúa como especialista PSP MIPS y PPSSPP oficial 1.20.4 (WebSocket debugger), GE/VRAM, IMY 4bpp/CLUT, PSPFS/DSARC/ISO9660, fuentes CP932, BPS y QA de traducción española. **Trabaja realmente:** diagnostica recursos disponibles, modifica herramientas, ejecuta pruebas auténticas y actualiza GitHub. Separa siempre tres niveles: evidencia del binario original, pruebas sintéticas en CI y ejecución del juego en PPSSPP. No inventes capturas, señales MIPS, direcciones RAM/VRAM, hashes ni supuestos resultados visuales.

**OBLIGACIÓN RECURSIVA:** AL TERMINAR, REESCRIBE COMPLETAMENTE ESTE MISMO ARCHIVO `prompts/SIGUIENTE_TAREA.md` con un NUEVO prompt autónomo completo y actualizado que exija nuevamente esta obligación. Muéstralo íntegramente al usuario. Repetir sucesivamente hasta que F2, F3, F4, F5 y F6 estén realizadas y demostradas. No anunciar trabajos futuros asíncronos.

## 1. Identidad de GitHub y lectura obligatoria

Repositorio: https://github.com/ARivas3008/loxalizacion-cladun-psp ; rama `integracion-eventos-segura-20261120` ; PR borrador #7 https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7 ; base `revision-manual-dialogos`. **Conservar DRAFT, nunca fusionar ni forzar HEAD.**

Antes de tocar nada, verificar SHA de HEAD/tree, PR y ambas Actions de ese SHA. En checkout local intentar `git fetch origin`, `git switch integracion-eventos-segura-20261120`, `git pull --ff-only`, `git status --short`, `git rev-parse HEAD`. En el último entorno `git fetch/pull` fallaron por DNS `Could not resolve host github.com`, no hubo checkout sincronizado. Si vuelve a fallar, registrar fallo y utilizar conector GitHub con `expected_sha` (sin force push); distinguir pruebas locales de CI.

Leer COMPLETOS `AGENTS.md`, `README.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, `docs/RESULTADO_F1_PPSSPP_2026-11-21.md`, `docs/RESULTADO_F2_ATLAS_PPSSPP_2026-11-21.md`, `docs/F2_ICONOS_TINTA_PPSSPP_2026-11-21.md`, `docs/F2_AUDITORIA_ORIGEN_SOLO_LECTURA_2026-11-21.md`, `docs/F2_QA_ESTATICA_WS_2026-11-21.md`, `docs/F2_LECTOR_GE_V6_2026-11-21.md`, `docs/F2_RELEVO_CAPTURA_RAM_2026-11-21.md`, `docs/F2_FE_ERRATAS_SHA256_SNAPSHOT_RAM_2026-11-21.md`, `docs/F2_RELEVO_WS_BREAKPOINT_2026-11-21.md`, `docs/F2_PREPARACION_DIRECCIONES_GE_2026-11-21.md`, `docs/F2_INVENTARIO_SYSGRA_2026-11-22.md`, `docs/F2_CATALOGO_GLOBAL_DSARC_2026-11-22.md`, `docs/F2_DOS_FUENTES_IMY_DECODIFICADAS_2026-11-22.md`, `docs/F2_SYSGRA_27_IMY_PALETAS_2026-11-22.md`, `docs/F2_PREVISUALIZACION_PRIVADA_SYSGRA_TEXTO_EN_GRAFICOS_2026-11-22.md` y **NUEVO** `docs/F2_SONDA_MAGENTA_TUIKA_CLUT_PPSSPP_PENDIENTE_2026-11-22.md`. Leer `reports/RESULTADO_F2_SONDA_TUIKA_CLUT_2026-11-22.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, informes F2 previos, este prompt, herramientas, tests, patcher y workflows.

**Privacidad innegociable:** NO subir ISO originales/experimentales, BPS, EBOOT, DATA.DAT, IMY, FONT.ARC, PNG de juego/atlas, RAM, dumps GE/VRAM ni ejecutables comerciales al repositorio. Solo publicar código, pruebas sintéticas, hashes, metadatos y documentación; mantener binarios, imágenes y emulación en ruta PRIVADA fuera del repositorio.

## 2. SHA originales e invariantes verificadas

ISO USA original del 7z del usuario: **305496064 bytes**, SHA-256 exacto (64 caracteres) `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. ISO F1 canónica anterior SHA `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`; BPS USA→F1 SHA `daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd`. AppImage oficial PPSSPP Linux v1.20.4 esperado SHA `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`. Nunca usar variante antigua incorrecta de SHA USA.

F1 Opciones fue aprobada **históricamente en PPSSPP real**: Xvfb 1280×720, ventana X11 **960×544**, caja texto interior **756px**, exterior ~764; ID 005709 diez espacios ideográficos + 7 ASCII, 005710 «Sí», 005713 «No» + espacio de presentación. Regresión actual **NO** repetida: una captura framebuffer PSP NO acredita ventana X11.

F2: 2721 glifos originales + 19 nuevos A1–B3 `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō` =2740. `white_new_ink=True` opcional cambia 100 texels nuevos; mantener `False` por defecto. FONT_00.IMY CLUT15 amarilla RGB247,247,0 y CLUT1 blanca RGB255,255,255. Tabla RAM `0x09075000`/PC `0x089089C8` demostraron lookup de TEXTO, **no PC de iconos**.

DATA.DAT contiene 349 PSPFS y cuatro DSARC: SYS.DAT2 seis PNG, SE.ARC 68 SPS, SYSGRA.ARC 27 IMY, FONT.ARC siete BIN/IMY =108 miembros con 108 SHA diferentes. SYSGRA.ARC original 93696 bytes SHA `63d9443084a2aeab8c2a3f79aebdb130eaf6c5d2e86f8be51346d7458ab81854`, PSPFS225 offset 895488. Se decodificaron 27/27 IMY en memoria; 24 superficies indexadas únicas, cuatro variantes PALETE_0..3 con misma imagen indexada y diferente RGBA, **sin función de juego todavía demostrada**. Las dos imágenes de fuente son diferentes: SYSGRA/FONT.IMY **256×256** frente FONT.ARC/FONT_00.IMY **512×256**. Controles KITAJIMA_KARI.IMY se atribuyó históricamente mediante sonda magenta de seis botones; HUD/combate no probado.

## 3. NUEVA sonda TUIKA_MES REAL: ISO privada de tres bytes, integridad demostrada

Relevo anterior (22/11/2026): ISO USA original AUTÉNTICA extraída del 7z privado y validada SHA. TUIKA_MES.IMY (SYSGRA.ARC DSARC **índice24**, offset 78848, 7912 bytes, SHA original `c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127`) almacena texto inglés *como píxeles*: «Replenished HP for all!», «Recovered SP!», «Attack all enemies on screen!», «No special attack», «Nullified traps!» y otros. Es un activo potencial para localización gráfica; su uso visual en PPSSPP **NO DEMOSTRADO**. Previsualización real SOLO ESTÁTICA anterior: `Cladun_F2_Atlas_SYSGRA_27_Previsualizacion_Privada_NO_PPSSPP_2026-11-22.png`; detalle privado `Cladun_F2_TUIKA_MES_Texto_Embebido_Previsualizacion_Privada.png`.

Se creó REALMENTE una ISO experimental privada desde la USA: cambiar **índice de CLUT 2** de **RGBA(249,251,249,255)** a **RGBA(255,0,255,255)** (magenta), modificando solo bytes absolutos ISO **114744872, 114744873, 114744874**, cambios `F9→FF, FB→00, F9→FF`. Alfa original intacta; los otros **348 PSPFS** y **26 DSARC** idénticos, tablas PSPFS/DSARC e ISO9660 resto byte por byte idénticos. No se cambiaron offsets ni tamaño ISO. **Esto afecta TODOS los píxeles CLUT2**, no exclusivamente letras: usar como control cromático, no como traducción. 

ISO PROBE PRIVADA NO PUBLICABLE SHA-256 `b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa`, tamaño 305496064. Nuevo SHA de miembro TUIKA `efcf4f41f57c300476e8ce54a32dea01f242dda3fbf3fb9c4e0b582bad8f5252`; nuevo SHA contenedor SYSGRA `403f391c4b1ab2c8618ac5d098f0a4316b7fd8262ecb80f7f39a2553ec06c758`. Informe PRIVADO de metadatos `CLADUN_F2_probe_TUIKA_rgba2_INTEGRIDAD_PRIVADA_2026-11-22.json` SHA `05287b3af776794936e5a548f351585f2413e12877fea9ac62d58292a53b438d`. No guardar estas ISO en GitHub.

Nueva herramienta reproducible `tools/f2_probe_tuika_palette_privado.py` con 22 pruebas sintéticas `tests/test_f2_probe_tuika_palette_privado.py`. Commit de código `ff91106a6997019bbd532c449160101df04f460a`; Actions `push 45051308641` y `PR 45051315010` SUCCESS, **313 pruebas Python**, Go, integridad/preflight y build Windows pública. El trabajo de ISO original se realizó privadamente con un script independiente; CI no contiene ni ejecuta la ISO comercial. No declarar que el script de GitHub fue probado en la ISO por las Actions.

Para reproducir PRIVADO desde la fuente exacta:

`python tools/f2_probe_tuika_palette_privado.py --iso-usa /PRIVATE/USA.iso --salida-iso-privada /PRIVATE/TUIKA_probe_nueva.iso --reporte-privado /PRIVATE/TUIKA_probe_resultado.json`

Exige ruta ISO nueva, SHA correcto, no overwrite, no archivo dentro del checkout y compara 349 PSPFS, 27 DSARC y delta de disco exacto. El resultado NO es prueba de visualización. Probar ahora en PPSSPP junto con ISO original.

## 4. PRIORIDAD PPSSPP: procedencia visual y MIPS→RAM→GE→VRAM

Primero localizar PPSSPP oficial **1.20.4** y validar versión/huella SHA antes de ejecutarlo. En último entorno NO instalado; `curl/git` a github.com fallaron por DNS. Si no puede descargarse el AppImage oficial https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4 , registrar el fallo REAL y continuar mejoras estáticas distintas sin fingir emulación. ISO F1 canónica tampoco estaba disponible; recuperar en privado o reconstruir bajo `--experimental-parcial --event-safe-only` y verificar SHA exacto, nunca sobrescribir USA.

Cuando PPSSPP y juego estén funcionando, abrir primero contexto que muestre mensajes de habilidad/TUIKA; capturar **dos PNG originales y dos PNG de la sonda**, auténticos, en carpetas PRIVADAS con SHA individuales. Misma escena, mismo orden de botones/frames; si aparece magenta en lugar del blanco de mensajes mientras otros gráficos permanecen igual, establecer evidencia funcional específica. Si NO aparece, dejar atribución como NO PROBADA y buscar otro contexto; no concluir que el asset no se utiliza en ninguna parte. Contrastar KITAJIMA controles, SYS1 iconos, MAHO_ST rótulos, dos FONT y PALETE 0..3 con controles positivos/negativos. Capturar CONTROLES, HUD, tutorial, ayuda, diálogo y combate auténticos.

Depurador WebSocket `ws://127.0.0.1:24192/debugger` con subprotocolo `debugger.ppsspp.org`: comprobar `version`, `game.status`, `cpu.status`. Acepta `memory.read/disasm`, `memory.breakpoint.list/add/remove`, `cpu.getAllRegs`, `cpu.stepping/resume`, `gpu.buffer.screenshot`, `gpu.record.dump`. No inventar `cpu.breakpoint.hit` o `gpu.displaylist.disasm`. Con CPU corriendo:

`python tools/f2_ppsspp_ws_1204.py --scene CONTROLES --salida-privada /tmp/f2-controles-autentico --port 24192 --ge-dump`

`python tools/f2_ge_dump_1204.py --entrada-privada /tmp/f2-controles-autentico/CONTROLES_GE_PRIVATE.dump --reporte-privado /tmp/f2-ge-autentico.json`

`python tools/f2_ram_provenance_1204.py --iso-usa /PRIVATE/USA.iso --salida-privada /tmp/f2-ram-autentico --solo-origen`

Para escanear RAM, CPU detenida con ticks estables; vigilancia `--watch-address 0xDIRECCION_REAL_PSP_RAM` solo si hubo coincidencia exacta y sesión nueva, nunca un offset de ISO como `0x06D68C00`. Exigir `reason == memory.breakpoint`, `relatedAddress` correcto, PC MIPS genuino, lectura/descompresión RAM, registers TEXTADDR/CLUT/PRIM/TRANSFERSTART, VRAM y píxeles finales correlacionados. Un hash/rango aislado no demuestra causalidad.

## 5. QA de los 19 glifos, F1, blindaje y BPS

Validar individual y VISUALMENTE en PPSSPP real `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō` en varios contextos: métricas, advance, interlineado, tildes, recortes «í» x4/mayúsculas y15, CLUT blanca/amarilla, □○×△, L/R y navegación. Crear probador PRIVADO de CSV con `tools/generar_probe_f2_glifos.py` sin editar **9237** registros canónicos; `tools/generar_probe_f2_tinta.py` solo diagnóstico. `white_new_ink=False` predeterminado hasta QA.

F1 Opciones: nueva ventana auténtica X11 **960×544**, Xvfb 1280×720, medir con scrot y verificar anchura 756/~764, IDs 005709 005710 Sí 005713 No y navegación. NO sustituir X11 por framebuffer PSP.

Blindaje de inserción: PSPFS 349, fuera de cuatro DSARC 345 recursos protegidos, en sonda aislada 348 vecinos sin cambiar, TUIKA 26 DSARC vecinos intactos; ISO9660 resto idéntico, SCRIPT.DAT 51705 comandos, 46308 no textuales, 1625 inicios, cero desplazamientos y 4524 traducciones script diferidas. **NUNCA retirar `--event-safe-only`. BPS solo privado y experimental `--experimental --event-safe-only`, SHA fuente/salida y roundtrip exacto. PR #7 DRAFT.

En checkout real si está disponible:
`python -m unittest discover -s tests -v`
`python tools/verificar_integridad.py --raiz .`
`python tools/verificar_borrador_es.py`
`python tools/auditar_preinsercion_es.py --reporte /tmp/preflight.json`
`python tools/reportar_integrabilidad_es.py --reporte /tmp/integrabilidad.json`
`python tools/f2_auditar_origen_iconos.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/origen.json`
`python tools/f2_qa_raster_19.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/glifos.json`
`python tools/f2_inventario_sysgra_usa.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/sysgra.json`
`python tools/f2_catalogo_global_dsarc_usa.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/dsarc.json`
`python tools/f2_auditar_dos_fuentes_imy.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/fuentes.json`
`python tools/f2_auditar_27_imy_sysgra.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/27-imy.json`
`python tools/f2_probe_tuika_palette_privado.py --iso-usa /PRIVATE/USA.iso --salida-iso-privada /PRIVATE/TUIKA_nuevo.iso --reporte-privado /PRIVATE/TUIKA_nuevo.json`
`(cd patcher && go test ./...)`
`git diff --check`

Si la terminal no puede acceder Git, recoger evidencia de test Python, Go, integridad y build Windows desde las DOS Actions del HEAD FINAL, **no confundir con ejecución PPSSPP**.

## 6. F3–F6, cierre y RECURSIVIDAD

F2 continúa ABIERTA hasta atribuir fuentes/iconos mediante PPSSPP real RAM→MIPS→GE→VRAM, demostrar la sonda TUIKA en uso real, verificar los 19 glifos en varios contextos y repetir regresión F1 X11. F3 intro visible en inglés; F4 reparar saltos/referencias de 4524 cambios SCRIPT.DAT sin alterar eventos; F5 recorrer historia/combat/HUD/inventario/retratos/enciclopedia/guardar-cargar; F6 BPS final y EXE Windows QA end-to-end. No fusionar PR #7 antes de demostrar todo.

Al concluir publicar código, pruebas y metadatos, actualizar `reports/ESTADO_CONTINUIDAD_PPSSPP.json` e informes, comprobar SHA final y que Actions push/PR para ese SHA son SUCCESS, PR DRAFT; no subir materiales comerciales.

**REESCRITURA RECURSIVA OBLIGATORIA: reemplazar POR COMPLETO `prompts/SIGUIENTE_TAREA.md` con un nuevo prompt autónomo e integral que exija exactamente esta misma obligación, y MOSTRAR SU CONTENIDO ÍNTEGRO AL USUARIO. Continuar hasta F2, F3, F4, F5 y F6 auténticamente terminadas.**
