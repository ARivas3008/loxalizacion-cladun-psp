# CLADUN ES — SIGUIENTE RELEVO AUTÓNOMO F2: PPSSPP 1.20.4 REAL, RAM→GE→VRAM, 19 glifos y regresión F1

Actúa como especialista sénior PSP/MIPS, depurador WebSocket de PPSSPP 1.20.4, GE/VRAM, IMY/CLUT, DSARC/PSPFS, CP932, BPS, QA y localización española. Esta NO es una petición de instrucciones: ejecutar cambios, pruebas, modificar código, actualizar GitHub y entregar evidencias auténticas. NO inventar emulación, PC, GE, VRAM, capturas o hashes.

OBLIGACIÓN RECURSIVA: cuando termines, REESCRIBE ÍNTEGRAMENTE este mismo archivo prompts/SIGUIENTE_TAREA.md con otro prompt autónomo completo, exige en él la misma obligación y muestra su contenido al usuario. Continuar los relevos hasta completar y verificar F2, F3, F4, F5 y F6. No prometer trabajos futuros en segundo plano.

## 1. Repositorio y lectura obligatoria

Repositorio https://github.com/ARivas3008/loxalizacion-cladun-psp, rama integracion-eventos-segura-20261120, PR #7 https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7, base revision-manual-dialogos. Mantener PR en DRAFT, nunca merge ni force push. Verificar HEAD remoto y Actions reales antes de escribir. Ejecutar git fetch origin; git switch integracion-eventos-segura-20261120; git pull --ff-only; git status --short; git rev-parse HEAD. Si Git falla por DNS, usar conector GitHub, pero NO afirmar que git fetch funcionó.

Leer íntegros: AGENTS.md, README.md, docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md, docs/RESULTADO_F1_PPSSPP_2026-11-21.md, docs/RESULTADO_F2_ATLAS_PPSSPP_2026-11-21.md, docs/F2_ICONOS_TINTA_PPSSPP_2026-11-21.md, docs/F2_AUDITORIA_ORIGEN_SOLO_LECTURA_2026-11-21.md, docs/F2_QA_ESTATICA_WS_2026-11-21.md, docs/F2_LECTOR_GE_V6_2026-11-21.md, docs/F2_RELEVO_CAPTURA_RAM_2026-11-21.md, reports/RESULTADOS_F2_ATLAS_PPSSPP_2026-11-21.json, reports/RESULTADOS_F2_ICONOS_TINTA_PPSSPP_2026-11-21.json, reports/RESULTADOS_F2_QA_ESTATICA_WS_2026-11-21.json, reports/RESULTADOS_F2_GE_DUMP_2026-11-21.json, reports/RESULTADO_F2_RELEVO_CAPTURA_RAM_2026-11-21.json, reports/ESTADO_CONTINUIDAD_PPSSPP.json y prompts/SIGUIENTE_TAREA.md. Revisar herramientas tools/, tests/, patcher/ y workflows .github.

Nunca publicar ISO, BPS, EBOOT, RAM, DATA.DAT, FONT.ARC, texturas, dumps GPU ni PNG comerciales en GitHub; guardar privados con SHA256. Conservar commits ajenos, usar update-ref con SHA esperado, sin sobrescribir otros trabajos.

## 2. Datos autenticados y límites de pruebas

ISO USA original 305496064 bytes SHA256 b73b263fce863e51a0e27d0d11d6bde2886e439a18e2bb186d497619a1b79f. ISO F1 canónica SHA256 496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986. BPS USA→F1 SHA256 daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd. PPSSPP oficial AppImage Linux 1.20.4 SHA256 661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21.

F1 aprobada HISTÓRICAMENTE en PPSSPP real bajo Xvfb 1280x720 con VENTANA 960x544: 756 píxeles interiores, aproximadamente 764 exteriores. IDs 005709 diez espacios ideográficos +7 ASCII; 005710 Sí; 005713 No con un espacio final solo presentación. NO confundir screenshot del framebuffer PSP con screenshot REAL de ventana de 960x544.

F2 atlas: 2721 originales preservados +19 nuevos, total 2740, códigos de un byte A1-B3. Los signos son áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō. Búsqueda texto código→índice verificada en RAM tabla 0x09075000, MIPS PC 0x089089C8 instrucción lhu t2,0(t1); esto NO prueba iconos.

Los iconos CONTROLES proceden de DATA.DAT → SYSGRA.ARC PSPFS índice225 offset 895488 → KITAJIMA_KARI.IMY DSARC índice17/27, offset 57856, longitud 2480, SHA256 0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190. Offset ISO absoluto 114723840 = 0x06D68C00, JAMÁS tratarlo como dirección RAM. Experimento magenta anterior de PPSSPP cambió seis iconos en Controles, 27 bytes RGB, preservó 348 PSPFS y 26 DSARC vecinos; NO atribuir el mismo recurso a HUD, tutoriales ni combate sin comprobar.

FONT_00.IMY CLUT15 amarillo 247,247,0 contra CLUT1 blanco 255,255,255. white_new_ink=True es optativo y cambia 100 texels nuevos, conserva 2721 originales. No activar por defecto. ISO amarilla experimental SHA 58f98b65185f39f172de0b5da97b9ce6fecb009e61b9462632f602485c99e4ca; ISO blanca SHA a42731988835bddb9dc81ef6d242b9c5029030256f210838881a1d48aed2de33; BPS amarillo→blanco SHA 2a698e1efaa1c2333dbd86ac8c3a9fabbd369382c4b8c7d3ad0ab7c7f2ffac3f. La ayuda de una pantalla previamente pasó de 516 píxeles amarillos a cero; falta QA multicontesto. Riesgos estáticos de í y mayúsculas y15 NO son errores confirmados en pantalla.

## 3. Nuevas herramientas: prueba real pendiente

Se corrigió tools/f2_ppsspp_ws_1204.py. En PPSSPP v1.20.4 GPUBufferSubscriber.cpp, gpu.buffer.screenshot requiere CPU/GPU detenida: ahora captura después de cpu.stepping, confirma pausa y devuelve cpu.resume solo si la herramienta pausó. gpu.record.dump debe ejecutarse PRIMERO mientras el juego corre para registrar el siguiente frame. Seis tests sintéticos nuevos pasaron. El fichero grabado se llama ESCENA_GE_PRIVATE.dump, no ESCENA_GE_FRAME.dump. GPU framebuffer no acredita ancho de ventana X11.

Nueva tools/f2_ram_provenance_1204.py coteja la firma exacta original de KITAJIMA, recorre RAM mediante memory.read con bloques solapados y --scan-ram, y puede colocar un memory.breakpoint con --watch-address para observar PC, registros y desensamblado al detenerse. El modo --solo-origen se ejecutó REALMENTE contra ISO USA y generó manifiesto privado SHA256 e8604ef2cf0303b1fa29b6c986f916528a36845d0846d4c0df396c6e2facdbb9. Diez tests sintéticos nuevos pasaron. Dos Actions del commit ee83ed5a4ff7cdcb8a60b84436db82a6613be009 finalizaron SUCCESS con 193 tests Python, Go e integración. Todo eso NO es prueba PPSSPP funcional. Aún no se obtuvo el AppImage oficial por DNS bloqueado ni ISO F1 local; cero PNG y dumps GE nuevos; cero PCs/VRAM de iconos nuevos.

tools/f2_ge_dump_1204.py lee PPSSPPGE v6 Zstd y contabiliza comandos GE de textura/CLUT/transferencia a partir de dumps PRIVADOS reales, sin exportar datos gráficos. No demuestra por sí solo PC ni destino VRAM.

## 4. Prioridad operativa: arrancar PPSSPP y demostrar procedencia

Obtener PPSSPP oficial tag v1.20.4 desde https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4, verificar SHA exacto, usar Xvfb 1280x720 y ventana 960x544 para F1. Obtener ISO F1 canónica autenticada o reconstruirla usando herramientas del repo tras revisar --help y validar SHA, sin sobrescribir ISO original. Revisar el problema DNS real del relevo precedente; no inventar descargas exitosas.

Con Cladun ejecutándose en pantalla CONTROLES, activar debugger WebSocket ws://127.0.0.1:24192/debugger con subprotocolo debugger.ppsspp.org. Eventos v1.20.4 sí existentes: version, game.status, cpu.status, cpu.stepping, cpu.resume, memory.read, memory.disasm, memory.breakpoint.add/remove, cpu.getAllRegs, gpu.buffer.screenshot, gpu.record.dump. No usar inexistentes gpu.displaylist.disasm ni cpu.breakpoint.hit.

Captura PRIVADA REAL, en directorio nuevo:
python tools/f2_ppsspp_ws_1204.py --scene CONTROLES --salida-privada /tmp/f2-controles-nuevo --port 24192 --ge-dump
Después:
python tools/f2_ge_dump_1204.py --entrada-privada /tmp/f2-controles-nuevo/CONTROLES_GE_PRIVATE.dump --reporte-privado /tmp/f2-ge-metadatos-nuevo.json

Verificación fuente REAL pero solo binaria:
python tools/f2_ram_provenance_1204.py --iso-usa /PRIVATE/USA.iso --salida-privada /tmp/f2-origen-nuevo --solo-origen
Para búsqueda RAM auténtica, cambiar a OTRO directorio nuevo y usar --scan-ram. Si hay coincidencia de dirección PSP RAM comprobada, con escena preparada/recargada para un nuevo acceso, usar --watch-address 0xDIRECCION_RAM con otra carpeta nueva y correlacionar broadcast CPU, PC, instrucciones, GPR, buffers, descompresión, texel fuente, comandos GE, CLUT, transferencia VRAM y draw. Un hit de firma RAM no implica origen/destino GE; un PC pausado por otra causa tampoco. Registrar NO PROBADO cada eslabón faltante. Confirmar con pruebas magenta y controles negativos.

Repetir por separado Controles, HUD, tutoriales, ayudas, diálogos, combate. Exigir dos PNG auténticos por estado y sus SHA256; para F1 usar capturas de VENTANA REAL con scrot o herramienta X11, NO screenshots del framebuffer PSP ni mockups.

## 5. Glifos, integridad y regresión

Observar individualmente los 19 signos y combinaciones L/R/□○×△: ancho, avance, interlineado, recortes de áéíóú, ÁÉÍÓÚ, ñÑüÜ, ¿¡, «» y ō. Usar tools/generar_probe_f2_glifos.py para CSV DIAGNÓSTICO PRIVADO de 9237 registros cuando no se muestre naturalmente un carácter. Probar herramientas de tinta opcional sin tocar corpus canónico. Antes de activar white_new_ink por defecto comprobar Opciones real 960x544, 756 px interior / aprox.764 exterior, IDs 005709, 005710 y 005713, navegación y retorno.

Conservar 349 PSPFS, 345 ajenos a cuatro contenedores, 348 vecinos en parches de FONT.ARC/SYSGRA.ARC aislados, 26 vecinos DSARC de KITAJIMA, ISO9660 ajeno intacto; 51705 comandos SCRIPT.DAT, 46308 no textuales, 1625 comienzos, cero desplazamientos, 4524 cambios script aplazados. Nunca retirar --event-safe-only. Integración desde USA experimental --experimental-parcial --event-safe-only; BPS experimental --experimental --event-safe-only, origen identificado y roundtrip SHA.

Ejecutar python -m unittest discover -s tests -v; python tools/verificar_integridad.py --raiz .; python tools/verificar_borrador_es.py; python tools/auditar_preinsercion_es.py --reporte /tmp/f2-preflight.json; python tools/reportar_integrabilidad_es.py --reporte /tmp/f2-integrabilidad.json; python tools/f2_auditar_origen_iconos.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-origen.json; python tools/f2_qa_raster_19.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-glyphs.json; (cd patcher && go test ./...); git diff --check. Verificar ambas GitHub Actions del HEAD FINAL, separando CI de PPSSPP real.

## 6. Próximas fases y relevo recursivo obligatorio

F2 ABIERTA hasta traza MIPS/RAM/GE/VRAM autenticada, 19 glifos multicontesto y regresión F1 en 960x544. F3 introducción inglesa; F4 reconstrucción segura de referencias/saltos para 4524 scripts; F5 aventura, niveles, combate, HUD, retratos, inventario, enciclopedia y guardado/carga; F6 BPS final, EXE Windows y QA integral. Mantener PR #7 DRAFT hasta completar todo. Registrar informe, archivos exactos, hashes reales o NO GENERADO, cambios, PCs/GPU reales, límites y estado en reports/ESTADO_CONTINUIDAD_PPSSPP.json.

AL FINAL REESCRIBIR COMPLETAMENTE prompts/SIGUIENTE_TAREA.md CON OTRO PROMPT AUTÓNOMO COMPLETO, MOSTRARLO AL USUARIO Y VOLVER A EXIGIR EN ÉL LA MISMA RECURSIVIDAD HASTA F2–F6 FINALIZADOS Y COMPROBADOS.
