# CLADUN ES — RELEVO AUTÓNOMO F2: cerrar evidencia PPSSPP REAL, direcciones GE/VRAM, 19 glifos y F1

Actúa como especialista sénior PSP/MIPS/GE, PPSSPP oficial v1.20.4, RAM y textura/CLUT, IMY, DSARC, PSPFS, CP932, seguridad de recursos, BPS y localización al español. **Haz trabajo auténtico**: ejecuta herramientas, inspecciona evidencia, edita código cuando haya fallos reproducibles, corre tests, publica GitHub y registra lo realizado. Jamás inventes un PC, dirección VRAM, PNG, dump o resultado funcional.

**RECURSIVIDAD INNEGOCIABLE:** cuando termines, REESCRIBE ÍNTEGRAMENTE este mismo archivo prompts/SIGUIENTE_TAREA.md con otro prompt autónomo completo, con la MISMA obligación recursiva y con referencias a tus cambios reales; muéstralo íntegro al usuario. Repetir hasta implementar y comprobar F2, F3, F4, F5 y F6. No prometer trabajo en segundo plano.

## 1. GitHub y lectura obligatoria

Repo: https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama: integracion-eventos-segura-20261120
PR: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7
Base: revision-manual-dialogos

Mantener PR DRAFT. Verificar SHA del HEAD, árbol, PR y ambas GitHub Actions. Antes de modificar: git fetch origin; git switch integracion-eventos-segura-20261120; git pull --ff-only; git status --short; git rev-parse HEAD. Si falla el Git directo, registrar error y usar conector GitHub con SHA esperado, sin afirmar que git fetch funcionó. No hacer force push, merge o reemplazar commits ajenos.

Leer COMPLETOS AGENTS.md, README.md, docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md, docs/RESULTADO_F1_PPSSPP_2026-11-21.md, docs/RESULTADO_F2_ATLAS_PPSSPP_2026-11-21.md, docs/F2_ICONOS_TINTA_PPSSPP_2026-11-21.md, docs/F2_AUDITORIA_ORIGEN_SOLO_LECTURA_2026-11-21.md, docs/F2_QA_ESTATICA_WS_2026-11-21.md, docs/F2_LECTOR_GE_V6_2026-11-21.md, docs/F2_RELEVO_CAPTURA_RAM_2026-11-21.md, docs/F2_FE_ERRATAS_SHA256_SNAPSHOT_RAM_2026-11-21.md, docs/F2_RELEVO_WS_BREAKPOINT_2026-11-21.md, docs/F2_PREPARACION_DIRECCIONES_GE_2026-11-21.md, reports/RESULTADO_F2_DIRECCIONES_GE_2026-11-21.json, informes F2 de reports/, reports/ESTADO_CONTINUIDAD_PPSSPP.json y este prompt. Revisar tools/, tests/, patcher/ y .github/workflows.

Prohibido publicar archivos ISO, BPS, EBOOT, DATA.DAT, FONT.ARC, RAM, texturas, dump GPU o PNG comerciales en GitHub. Evidencia auténtica y hashes SOLO en almacenamiento privado fuera del repositorio; publicar únicamente metadatos y documentación.

## 2. Datos exactos y precedentes

ISO USA original privada: 305496064 bytes, SHA256 64 caracteres:
b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f

NO usar el SHA erróneo de 62 caracteres; el guard tests/test_f2_sha256_references.py debe permanecer activo. ISO F1 canónica SHA256 496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986. BPS fuente USA a F1 SHA daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd. AppImage oficial PPSSPP Linux v1.20.4 SHA 661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21.

F1 Opciones APROBADA HISTÓRICAMENTE en PPSSPP Xvfb 1280×720, ventana real 960×544: 756 píxeles interior, aproximadamente 764 exterior. ID 005709 diez espacios ideográficos más 7 ASCII; 005710 Sí; 005713 No más espacio ASCII de presentación. Una captura del framebuffer PSP NO sustituye una captura de ventana X11 960×544.

F2 fuente: 2721 glifos originales preservados byte por byte + 19 españoles A1–B3 =2740, caracteres áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō. Tabla RAM texto código→índice 0x09075000, MIPS PC 0x089089C8 con lhu t2,0(t1) prueba búsqueda de TEXTO y NO el dibujo de iconos.

Iconos CONTROLES: DATA.DAT → SYSGRA.ARC (PSPFS índice225, offset 895488) → KITAJIMA_KARI.IMY (DSARC índice17/27, offset57856, comprimido 2480 bytes), SHA256 0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190. Offset ISO 114723840, hexadecimal 0x06D68C00: NO es dirección RAM. Experimento histórico de magenta cambió 27 bytes RGB, seis iconos CONTROLES, 348 PSPFS y 26 DSARC vecinos idénticos. NO atribuir sin pruebas los iconos HUD, combate o tutorial al mismo recurso.

Tinta FONT_00.IMY índice CLUT15 amarillo RGB(247,247,0) versus índice1 blanco RGB(255,255,255). white_new_ink=True es optativo, cambia solo 100 texels nuevos, preserva 2721 originales. Mantener False predeterminado. ISO amarilla SHA 58f98b65185f39f172de0b5da97b9ce6fecb009e61b9462632f602485c99e4ca; blanca SHA a42731988835bddb9dc81ef6d242b9c5029030256f210838881a1d48aed2de33; BPS amarilla→blanca SHA 2a698e1efaa1c2333dbd86ac8c3a9fabbd369382c4b8c7d3ad0ab7c7f2ffac3f. Ayuda histórica amarillo 516→0 NO prueba los 19 glifos.

## 3. Novedad verdadera del último relevo: direcciones GE candidatas

El lector tools/f2_ge_dump_1204.py procesa PPSSPPGE v6 de PPSSPP oficial v1.20.4 y ahora reconstruye CANDIDATOS numéricos de textura, CLUT y transferencia en registros REGISTERS, con ubicación de recorder y word, a partir del código oficial hrydgard/ppsspp/v1.20.4 en GPU/GPUState.h y GPU/ge_constants.h. Campos: ge_address_candidates_limited_to_150, ge_address_trigger_count_total, addresses_are_partial_unverified_candidates. NO asigna identidad de textura ni PC MIPS ni prueba copia a VRAM; puede carecer del estado INIT/anterior al comienzo del dump. El booleano in_primary_2mib_vram_window solo clasifica un rango numérico y no demuestra subida. Se añadieron 4 tests sintéticos y ambos workflows del commit de código 161dcec70731e0472c5418547074d5a5d08c110f resultaron SUCCESS: 213 tests Python, Go y compilación Windows.

La ISO original real y el atlas se reauditaron en el entorno privado: 305496064 bytes, KITAJIMA 2480 bytes, 2721 registros y 19 glifos, 100 texels optativos. Hash del JSON estático 19 glifos: 88edb8a2cf1a920f1ff7480cbe4b06f44d5441a1183720b71a07b393a49bfb80. El manifiesto privado del relevo tiene SHA d105cec882bfbc2e6dd7e4ac2f41aad0717cbf2eac0abd6a1325892b7f3cb178. Estas pruebas NO son PPSSPP real.

tools/f2_ppsspp_ws_1204.py ya conserva notificaciones CPU sin ticket y captura GPU solo detenida; gpu.record.dump se inicia con CPU corriendo. tools/f2_ram_provenance_1204.py exige snapshot RAM con CPU parada, ticks sin cambio, evita pisar breakpoints ajenos y solo atribuye un stop cuando reason memory.breakpoint y relatedAddress coinciden con el inicio del rango. Son herramientas aún sin validación con PPSSPP en ESTE entorno.

## 4. Prioridad real: obtener PPSSPP y F1 canónica, ejecutar juego y correlacionar

Intentar acceder al AppImage oficial desde https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4, autenticar SHA exacto antes de ejecutar. Verificar Xvfb 1280×720, ventana 960×544 con captura scrot; obtener F1 privada autenticada o reconstruirla mediante integrador oficial del repo solo tras revisar sus flags y validar SHA. No sobrescribir la ISO USA. Si la red falla, indicarlo y continuar con una prueba técnica auténtica diferente; NO inventar resultados.

Con Cladun iniciado y CONTROLES a la vista, debugger local ws://127.0.0.1:24192/debugger, subprotocolo debugger.ppsspp.org. Confirmar version y game.status. Los eventos compatibles incluyen cpu.status/stepping/resume, memory.read/disasm, memory.breakpoint.list/add/remove, cpu.getAllRegs, gpu.buffer.screenshot y gpu.record.dump. NO usar cpu.breakpoint.hit ni gpu.displaylist.disasm inexistentes en v1.20.4.

Con CPU corriendo, nuevo directorio PRIVADO fuera de Git:
python tools/f2_ppsspp_ws_1204.py --scene CONTROLES --salida-privada /tmp/f2-controles-ppsspp-real-nuevo --port 24192 --ge-dump

Analizar privado el dump creado (nombre CONTROLES_GE_PRIVATE.dump):
python tools/f2_ge_dump_1204.py --entrada-privada /tmp/f2-controles-ppsspp-real-nuevo/CONTROLES_GE_PRIVATE.dump --reporte-privado /tmp/f2-ge-candidatos-nuevo.json

Comparar REGISTERS: TEXADDR/TEXBUFWIDTH, CLUTADDR/CLUTADDRUPPER, PRIM, TRANSFERSTART y registros de transferencia; correlacionar sus posiciones y direcciones con RAM comprimida y RAM descomprimida, PC MIPS real de carga/descompresión/subida, contenido y geometría, CLUT y framebuffer final. Las direcciones en el informe son CANDIDATAS HASTA DEMOSTRACIÓN CON DATOS DEL JUEGO.

Probar origen real primero con:
python tools/f2_ram_provenance_1204.py --iso-usa /PRIVATE/USA.iso --salida-privada /tmp/f2-origen-nuevo --solo-origen

Después --scan-ram con directorio diferente; si existe coincidencia exacta comprobada, preparar otro contexto y --watch-address 0xDIRECCION_PSP_RAM con directorio nuevo, nunca 0x06D68C00. Usar un solo depurador y conservar pausas ajenas. No atribuir PC de texto a iconos. Ejecutar controles positivos y negativos en CONTROLES, HUD, tutorial, ayudas, diálogos y combate de forma separada, con DOS PNG auténticos por pantalla y SHA256.

## 5. QA visual de los 19 glifos y regreso a F1

Validar cada áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō en PPSSPP verdadero; registrar texto real, ancho, avance, tilde, clipping superior/inferior, í x4, mayúsculas y15, interacción con □○×△ y L/R, saltos de línea, CLUT y legibilidad. Si faltan caracteres en escenarios naturales, usar tools/generar_probe_f2_glifos.py para CSV diagnóstico PRIVADO de 9237 registros sin alterar corpus canónico. Comparar amarillo/white_new_ink opcional con tools/generar_probe_f2_tinta.py. No activar True por defecto sin F1 actual 960×544 y 756/764, 005709 005710 Sí 005713 No, abrir/cerrar CONTROLES, navegación.

Conservar 349 PSPFS, 345 fuera de cuatro contenedores de localización, 348 vecinos si solo se toca FONT.ARC/SYSGRA.ARC, 26 DSARC vecinos KITAJIMA, ISO9660 ajeno intacto; SCRIPT.DAT 51705 comandos, 46308 no textuales, 1625 inicios, cero desplazamientos, 4524 textos script pendientes. NUNCA eliminar --event-safe-only. Para integración candidata desde USA usar --experimental-parcial --event-safe-only; BPS privado --experimental --event-safe-only, identificar fuente y comprobar roundtrip SHA exacto.

Ejecutar en checkout disponible: python -m unittest discover -s tests -v; python tools/verificar_integridad.py --raiz .; python tools/verificar_borrador_es.py; python tools/auditar_preinsercion_es.py --reporte /tmp/f2-preflight.json; python tools/reportar_integrabilidad_es.py --reporte /tmp/f2-integrabilidad.json; python tools/f2_auditar_origen_iconos.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-origen.json; python tools/f2_qa_raster_19.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-raster.json; (cd patcher && go test ./...); git diff --check. Distinguir pruebas CI Python/Go/Windows de pruebas PPSSPP auténticas; verificar push y pull_request del HEAD FINAL.

## 6. Entregables y regla que debe repetirse

Actualizar docs, reports/ESTADO_CONTINUIDAD_PPSSPP.json, test y herramientas y registrar hashes de cada evidencia real o NO GENERADO. Mantener PR #7 DRAFT, sin publicar archivos comerciales y sin declarar F2 cerrada sin la cadena completa RAM→MIPS→GE→VRAM, 19 signos multicontesto y regresión F1 real.

F3: introducir y validar la intro inglesa. F4: referencias/saltos seguros de 4524 textos script. F5: aventura, combate, HUD, retratos, inventario, enciclopedia, guardar y cargar. F6: BPS final, ejecutable Windows y QA integral.

**AL TERMINAR REESCRIBE POR COMPLETO prompts/SIGUIENTE_TAREA.md, MUESTRA EL NUEVO PROMPT ÍNTEGRO Y EXIGE EN ÉL OTRA VEZ LA MISMA REGENERACIÓN RECURSIVA HASTA F2–F6 AUTÉNTICAMENTE COMPLETADAS.**
