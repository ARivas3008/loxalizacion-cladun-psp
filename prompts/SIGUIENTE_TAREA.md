# CLADUN ES — RELEVO F2 AUTÓNOMO: PPSSPP REAL, vigilancia MIPS segura, GPU GE/VRAM y 19 caracteres

Actúa como ingeniero sénior PSP MIPS, depurador WebSocket PPSSPP oficial v1.20.4, GPU GE y VRAM, archivo ISO9660/PSPFS/DSARC, IMY/CLUT, CP932 español, inserción BPS segura y QA. No basta con escribir consejos: ejecuta pruebas, cambia archivos cuando los resultados lo avalen, actualiza GitHub y entrega evidencias auténticas. **NO inventar capturas, resultados de emulador, PCs MIPS, comandos GE, hashes ni pruebas de juego.**

**OBLIGACIÓN RECURSIVA INNEGOCIABLE:** al finalizar REESCRIBE ÍNTEGRAMENTE `prompts/SIGUIENTE_TAREA.md` con otro prompt autónomo que incluya la MISMA obligación, y muéstralo íntegro al usuario. Repetir en cada relevo hasta completar y verificar F2, F3, F4, F5 y F6 sin declarar trabajo asíncrono.

## 1. Inicio: preservar GitHub y leer fuentes

Repositorio: https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama de trabajo: `integracion-eventos-segura-20261120`. PR #7: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7, base `revision-manual-dialogos`. Mantener **DRAFT** y NO fusionar.

Verifica HEAD remoto, árbol, PR y ambas Actions antes de tocar archivos. Intenta exactamente `git fetch origin`, `git switch integracion-eventos-segura-20261120`, `git pull --ff-only`, `git status --short`, `git rev-parse HEAD`. Si no funciona el Git de terminal por DNS/restricción, usa GitHub conectado y NO afirmar que `git fetch` se ejecutó. Nunca force-push, checkout destructivo ni sobrescribir otros cambios.

Lee COMPLETOS: AGENTS.md, README.md, docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md, docs/RESULTADO_F1_PPSSPP_2026-11-21.md, docs/RESULTADO_F2_ATLAS_PPSSPP_2026-11-21.md, docs/F2_ICONOS_TINTA_PPSSPP_2026-11-21.md, docs/F2_AUDITORIA_ORIGEN_SOLO_LECTURA_2026-11-21.md, docs/F2_QA_ESTATICA_WS_2026-11-21.md, docs/F2_LECTOR_GE_V6_2026-11-21.md, docs/F2_RELEVO_CAPTURA_RAM_2026-11-21.md, docs/F2_FE_ERRATAS_SHA256_SNAPSHOT_RAM_2026-11-21.md, docs/F2_RELEVO_WS_BREAKPOINT_2026-11-21.md, reports/RESULTADO_F2_WS_BREAKPOINT_2026-11-21.json, todos los informes F2 en reports/, reports/ESTADO_CONTINUIDAD_PPSSPP.json y este prompt. Revisar tools/, tests/, patcher/ y .github/workflows.

No subir ISO, BPS, EBOOT, DATA.DAT, FONT.ARC, RAM, texturas, dumps GPU ni PNG comerciales a GitHub. Solo métricas, scripts, tests y documentación. Guardar evidencia con SHA256 PRIVADAMENTE fuera de Git.

## 2. Hechos y SHA-256 innegociables

ISO USA original PRIVADA: **305496064 bytes**; SHA256 de 64 hex EXACTOS:
`b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.
NO usar la cadena errónea de 62 caracteres; tests/test_f2_sha256_references.py impide regresión. ISO F1 canónica SHA256 `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`. BPS experimental USA→F1 SHA `daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd`. AppImage PPSSPP Linux oficial 1.20.4 SHA `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`.

F1 Opciones: PPSSPP real HISTÓRICO Xvfb 1280×720, VENTANA 960×544, 756px interior/aprox.764px exterior, ID 005709 diez espacios ideográficos más 7 ASCII, 005710 Sí, 005713 No con ASCII de presentación. No equiparar PNG framebuffer PSP con captura X11 real de ventana; para regresión repetir esa geometría y navegación.

F2 fuente: 2721 registros de glifos originales preservados más 19 A1–B3 = 2740. Los caracteres nuevos son `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō`. Tabla de TEXTO código→índice PSP RAM `0x09075000`, PC `0x089089C8`, `lhu t2,0(t1)`: NO demuestra PC de iconos.

Iconos de CONTROLES: DATA.DAT → SYSGRA.ARC PSPFS índice225 offset local 895488 → KITAJIMA_KARI.IMY DSARC índice17/27 offset 57856, longitud comprimida 2480 bytes, SHA256 `0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190`. Su offset ISO absoluto `114723840=0x06D68C00` **NO es dirección RAM**. Prueba PPSSPP histórica de magenta alteró 27 bytes RGB y seis iconos en CONTROLES, conservó 348 PSPFS vecinos y 26 DSARC vecinos. No extrapolar a combate/HUD/tutorial.

Tinta: CLUT15 amarillo RGB247,247,0 frente a CLUT1 blanco RGB255,255,255; `white_new_ink=True` optativo reemplaza 100 texels nuevos sin cambiar 2721 originales. **Mantener False por defecto**. ISO amarilla SHA `58f98b65185f39f172de0b5da97b9ce6fecb009e61b9462632f602485c99e4ca`; blanca `a42731988835bddb9dc81ef6d242b9c5029030256f210838881a1d48aed2de33`; BPS amarillo→blanco `2a698e1efaa1c2333dbd86ac8c3a9fabbd369382c4b8c7d3ad0ab7c7f2ffac3f`. El experimento visual antiguo solo probó amarillo 516→0 en una ayuda, NO 19 signos multicontesto.

## 3. Último avance VERIFICADO, y lo que NO demuestra

Se repitió QA ESTÁTICA real de la ISO original: 2721 registros, 19 glifos, 100 texels de tinta, informe detallado privado SHA256 `88edb8a2cf1a920f1ff7480cbe4b06f44d5441a1183720b71a07b393a49bfb80`; no son capturas PPSSPP.

`tools/f2_ppsspp_ws_1204.py` ahora mantiene una cola acotada de broadcasts asíncronos cuando llegan mientras espera respuestas por ticket; no puede perder `cpu.stepping` ni `cpu.resume` silenciosamente. Esos eventos NO llevan ticket. Cuatro nuevos tests sintéticos, PASS. Para `gpu.buffer.screenshot`, PPSSPP 1.20.4 exige detener CPU/GPU, capturar y reanudar solo si la pausa la provocó el cliente. Para `gpu.record.dump`, grabar PRIMERO con CPU corriendo: captura siguiente frame. Dump privado nombre ESCENA_GE_PRIVATE.dump, no GE_FRAME.dump.

`tools/f2_ram_provenance_1204.py` autentica la firma KITAJIMA, busca firma exacta en RAM mientras CPU está detenida, verifica ticks estables, y puede registrar el PC observado en watchpoint. **NUEVO PROTOCOLO DE SEGURIDAD**: consulta `memory.breakpoint.list` y falla si el rango ya tiene breakpoint de otro usuario; solo atribuye parada propia si broadcast `reason == "memory.breakpoint"` y `relatedAddress == inicio_watchpoint`. La razón exacta está verificada en el código fuente oficial PPSSPP `Core/Core.cpp` y `Core/Debugger/Breakpoints.cpp`. No reanudar pausas ajenas. No existe bloqueo transaccional entre clientes depuradores: usar solo un cliente. Se añadieron 6 pruebas sintéticas PASS.

`tools/f2_ge_dump_1204.py` inspecciona registros PPSSPPGE v6 Zstd, enumera comandos GE y su posición sin copiar texturas. Solo sirve cuando el dump es realmente de PPSSPP. CI último código: **209 tests Python PASS, Go y Windows CI PASS**; estas pruebas NO prueban ejecución real de Cladun.

Bloqueo auténtico: en último contenedor no existía AppImage oficial PPSSPP ni ISO F1, el acceso GitHub por DNS e IP directa estaba bloqueado. Hay ISO USA auténtica; NO nuevos PNG, dumps GE, PCs de iconos, direcciones VRAM ni regresión F1. F2 sigue ABIERTA.

## 4. Prioridad: PPSSPP 1.20.4 REAL, de inicio a framebuffer

Buscar PPSSPP oficial https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4, autenticar SHA SHA256 exacto antes de ejecutar. Verificar Xvfb, scrot, apertura en 960×544; recuperar o reconstruir ISO F1 PRIVADA solo con integrador revisado y SHA canónico, sin sobrescribir USA. Si no es posible, registrar NO PROBADO y avanzar con otro fallo reproducible real; no falsificar experiencia jugable.

Arrancar Cladun con depurador WS LOCAL `ws://127.0.0.1:24192/debugger`, subprotocolo `debugger.ppsspp.org`; confirmar eventos `version`, `game.status`, `cpu.status`, `memory.read`, `memory.disasm`, `memory.breakpoint.list/add/remove`, `cpu.getAllRegs`, `cpu.stepping`, `cpu.resume`, `gpu.buffer.screenshot`, `gpu.record.dump`. NO inventar `cpu.breakpoint.hit` ni `gpu.displaylist.disasm`, ausentes v1.20.4.

Pantalla CONTROLES auténtica y carpeta nueva PRIVADA:
`python tools/f2_ppsspp_ws_1204.py --scene CONTROLES --salida-privada /tmp/f2-controles-real-nuevo --port 24192 --ge-dump`
Luego:
`python tools/f2_ge_dump_1204.py --entrada-privada /tmp/f2-controles-real-nuevo/CONTROLES_GE_PRIVATE.dump --reporte-privado /tmp/f2-ge-real-metadatos.json`
Origen binario:
`python tools/f2_ram_provenance_1204.py --iso-usa /PRIVATE/USA.iso --salida-privada /tmp/f2-origen-nuevo --solo-origen`
RAM real: usar `--scan-ram` con NUEVA carpeta privada. Si se demuestra dirección RAM PSP de firma comprimida, preparar otro contexto para watchpoint `--watch-address 0xDIRECCION_RAM` en carpeta NUEVA; correlacionar evento memory.breakpoint genuino, PC, registros, descompresor, salida, GE TEXADDR/CLUT/PRIM/transferencia, VRAM, dibujo final. Un hit comprimido o un dump GE aislado no prueban procedencia. No tratar offset ISO como RAM ni tabla TEXTO como icono.

Repetir para CONTROLES, HUD, tutorial, ayuda, diálogos y combate por separado con controles positivos/negativos y al menos DOS PNG AUTÉNTICOS por escena (SHA256). Regresión F1 exige captura real de VENTANA X11 960×544, no la textura framebuffer PSP.

## 5. QA caracteres e invariantes de parche seguro

Analizar en PPSSPP cada uno de `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō`: ancho, advance, acento, línea base, desplazamiento con □○×△ y L/R, recorte y15 de mayúsculas y x4 de í, interlineado, colores. Si faltan signos naturales generar CSV diagnóstico PRIVADO con `tools/generar_probe_f2_glifos.py` (9237 registros) y variación tinta con `tools/generar_probe_f2_tinta.py`. No modificar corpus canónico. No activar tinta blanca por defecto hasta regresión real de F1 960×544, 756 interiores/aprox764 exteriores, ID 005709 sangría, 005710 Sí, 005713 No, navegación y retorno.

Preservar 349 PSPFS, 345 recursos ajenos a 4 contenedores, 348 PSPFS vecinos en sondas de FONT.ARC/SYSGRA.ARC, 26 DSARC vecinos, ISO9660 fuera de localización, SCRIPT.DAT 51705 comandos, 46308 no textuales, 1625 inicios, cero cambios de desplazamiento y 4524 traducciones de script aplazadas. **NO retirar nunca `--event-safe-only`**. Integración experimental desde USA `--experimental-parcial --event-safe-only`; BPS experimental `--experimental --event-safe-only` solo privado, origen SHA y roundtrip exactos.

Ejecutar `python -m unittest discover -s tests -v`; `python tools/verificar_integridad.py --raiz .`; `python tools/verificar_borrador_es.py`; `python tools/auditar_preinsercion_es.py --reporte /tmp/f2-preflight.json`; `python tools/reportar_integrabilidad_es.py --reporte /tmp/f2-integrabilidad.json`; `python tools/f2_auditar_origen_iconos.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-origen.json`; `python tools/f2_qa_raster_19.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-19.json`; `(cd patcher && go test ./...)`; `git diff --check`. Diferenciar CI de Python/Go/Windows de PPSSPP visual real; comprobar ambas Actions del HEAD FINAL. Si algo no se puede ejecutar, documentar el bloqueo exacto.

## 6. Entregables y regeneración recursiva

Actualizar archivos de código, tests, docs, reports/ESTADO_CONTINUIDAD_PPSSPP.json, manifiestos de SHA de evidencia privada y nueva documentación, sin exponer materiales comerciales. Registrar SHA y PC/direcciones que se hayan probado verdaderamente y campos `NO PROBADO` para los ausentes. Mantener PR #7 en DRAFT hasta completar el proyecto.

F2 abierta hasta demostrar cadena MIPS/RAM/GE/VRAM, 19 glifos multicontesto y regresión F1 auténtica. F3 intro inglesa; F4 control de saltos/referencias de 4524 scripts; F5 juego completo, HUD, inventario, retratos, enciclopedia, combate y guardar/cargar; F6 BPS final, EXE Windows y QA integral.

**AL FINAL REESCRIBE COMPLETAMENTE `prompts/SIGUIENTE_TAREA.md` CON OTRO PROMPT AUTÓNOMO ÍNTEGRO, MUÉSTRALO AL USUARIO Y EXIGE DE NUEVO LA MISMA RECURSIVIDAD HASTA COMPLETAR Y VERIFICAR F2–F6.**
