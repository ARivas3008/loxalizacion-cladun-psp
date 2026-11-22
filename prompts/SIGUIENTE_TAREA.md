# CLADUN ES — PRÓXIMO RELEVO AUTÓNOMO: F2 PPSSPP REAL, MIPS/GE/VRAM, 19 glifos y F1

Actúa como ingeniero PSP MIPS, GPU GE, PPSSPP 1.20.4, IMY/CLUT, DSARC/PSPFS, CP932, traducción española y BPS. Debes **ejecutar código, pruebas funcionales y modificaciones reales y actualizar GitHub**, no limitarte a explicar. Si algo no se demuestra, escribir NO PROBADO y no inventar datos.

**OBLIGACIÓN RECURSIVA:** Al terminar, REESCRIBE COMPLETAMENTE prompts/SIGUIENTE_TAREA.md con otro prompt autónomo que vuelva a exigir reescribir el mismo archivo al finalizar. Continuar este relevo recursivo en cada fase F2, F3, F4, F5 y F6 hasta integrar y verificar funcionalmente el juego completo. Mostrar el prompt generado al usuario.

## 1. Origen, estado y lectura

Repositorio https://github.com/ARivas3008/loxalizacion-cladun-psp, rama integracion-eventos-segura-20261120, PR #7 https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7, base revision-manual-dialogos. Mantener PR DRAFT y NO fusionar. Ejecutar git fetch origin; git switch integracion-eventos-segura-20261120; git pull --ff-only; git status --short; git rev-parse HEAD. Verificar HEAD inicial y Actions, conservar cambios ajenos.

Leer COMPLETOS AGENTS.md, README.md, docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md, docs/RESULTADO_F1_PPSSPP_2026-11-21.md, docs/RESULTADO_F2_ATLAS_PPSSPP_2026-11-21.md, docs/F2_ICONOS_TINTA_PPSSPP_2026-11-21.md, docs/F2_AUDITORIA_ORIGEN_SOLO_LECTURA_2026-11-21.md, docs/F2_QA_ESTATICA_WS_2026-11-21.md, reports/RESULTADOS_F2_ATLAS_PPSSPP_2026-11-21.json, reports/RESULTADOS_F2_ICONOS_TINTA_PPSSPP_2026-11-21.json, reports/RESULTADOS_F2_QA_ESTATICA_WS_2026-11-21.json, reports/ESTADO_CONTINUIDAD_PPSSPP.json, prompts/SIGUIENTE_TAREA.md y herramientas/tests/patcher/workflows. No publicar ISO, BPS, EBOOT, DATA.DAT, FONT.ARC, RAM, GPU dump, texturas ni PNG comerciales en GitHub. Evidencias solo en privado con SHA256.

## 2. Hechos innegociables

ISO USA privada SHA256 b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f (305496064 bytes). ISO F1 canónica SHA256 496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986. BPS USA→F1 experimental SHA256 daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd. PPSSPP oficial AppImage 1.20.4 SHA256 661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21.

F1 Opciones ya medida PPSSPP REAL Xvfb 1280x720 con VENTANA 960x544: 756 px interior, ~764 exterior. 005709 diez espacios ideográficos + siete ASCII, 005710 Sí, 005713 No con uno ASCII solo presentación. No equiparar las capturas F2 fullscreen 1280x720 con F1 nueva 960x544.

F2: 2721 glifos originales intactos +19 A1–B3 =2740. Tabla texto RAM 0x09075000, búsqueda MIPS PC 0x089089C8 instrucción lhu t2,0(t1), prueba de TEXTO no iconos. Iconos Controles vienen de DATA.DAT → SYSGRA.ARC PSPFS 225 offset 895488 → KITAJIMA_KARI.IMY DSARC 17/27 offset 57856, 2480 bytes SHA256 0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190, offset ISO absoluto 114723840 = 0x06D68C00. Sonda magenta anterior PPSSPP verificó seis iconos de Controles con 27 bytes RGB; otros 348 PSPFS y 26 DSARC invariantes. No prueba HUD, combate ni GE/VRAM.

19 glifos áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō. Tinta amarilla índice 15 RGB 247,247,0 contra blanco índice1 255,255,255; white_new_ink=True optativo modifica 100 texels nuevos, False por defecto, 2721 originales exactos. ISO amarilla diagnóstica SHA 58f98b65185f39f172de0b5da97b9ce6fecb009e61b9462632f602485c99e4ca, ISO blanca SHA a42731988835bddb9dc81ef6d242b9c5029030256f210838881a1d48aed2de33, BPS amarilla→blanca SHA 2a698e1efaa1c2333dbd86ac8c3a9fabbd369382c4b8c7d3ad0ab7c7f2ffac3f. Antes 516 píxeles amarillos, después 0, solo una ayuda.

Nueva QA ESTÁTICA de ISO original: los 19 raster examinados y 100 texels confirmados. Riesgos NO confirmados: í se extiende x3→x4 y ÁÉÍÓÚÑÜ alcanzan y15. tools/f2_qa_raster_19.py y tests; tool capturador tools/f2_ppsspp_ws_1204.py. 24 tests locales sintéticos PASS. Ni AppImage ni ISO F1 disponibles en último entorno; NO hubo capturas nuevas, dump GPU real, MIPS→GE→VRAM ni regresión F1.

## 3. Ejecutar PPSSPP auténtico y localizar cadena RAM→GE→VRAM

Obtener PPSSPP oficial 1.20.4 exacto y ISO F1 autenticada, activar depurador WebSocket local subprotocolo debugger.ppsspp.org. Revisar código de hrydgard/ppsspp TAG v1.20.4 en Core/Debugger/WebSocket/*Subscriber.cpp. Existen version, game.status, memory.read, memory.disasm, cpu.stepping, breakpoints, gpu.buffer.screenshot/texture/clut, gpu.record.dump; NO existen en v1.20.4 gpu.displaylist.disasm ni cpu.breakpoint.hit (versiones más recientes). No inventar estas órdenes.

Ejecutar tools/f2_ppsspp_ws_1204.py para dos PNG reales por escena, por ejemplo:
python tools/f2_ppsspp_ws_1204.py --scene CONTROLES --salida-privada /tmp/cladun_f2_controles_real --port 24192 --ge-dump

Registrar hashes privados y evidencia real. El paquete privado Cladun_F2_Instrumentacion_y_QA_Estatica_2026-11-21.zip incluye prototipo más amplio con búsqueda de firma comprimida KITAJIMA en RAM y watchpoints; revisar y adaptar antes de usar en juego. Buscar buffer comprimido, salida descompresor, PC MIPS y registros, comandos GE, buffers VRAM y dibujo final. El offset ISO 0x06D68C00 NO es una dirección PSP. Un dump GPU por sí solo NO demuestra PC ni transferencia. Probar Controles, HUD, tutorial, ayudas, diálogos y combate por separado, DOS PNG originales auténticos por estado, positivos/negativos y SHA256, sin extrapolación.

## 4. QA de glifos y regresión F1 real

Comparar letra por letra áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō, formas, ancho real, avance, línea base, recorte horizontal/vertical, espaciado y cercanía a símbolos de botones. Evaluar í (x4) y mayúsculas en y15. Usar escenas reales; si no hay caracteres, CSV diagnóstico privado de 9237 filas con tools/generar_probe_f2_glifos.py. Comprobar tinta vieja vs white_new_ink=True optativo con tools/generar_probe_f2_tinta.py; nunca editar corpus canónico para sondear. Antes de activar tinta blanca por defecto repetir PPSSPP Opciones en ventana 960x544: 005709, Sí/No, 756 px interior/~764 exterior, navegación y retorno. Si no hay evidencia, blanco sigue optativo y F2 abierta.

## 5. Integridad y ejecución

Conservar 349 PSPFS, 345 ajenos a cuatro contenedores de localización, 348 vecinos si solo cambia FONT.ARC o SYSGRA.ARC, 26 DSARC vecinos KITAJIMA, ISO9660 ajenos exactos, 51705 comandos SCRIPT, 46308 no textuales, 1625 comienzos y cero desplazamientos. 4524 traducciones script continúan aplazadas. NUNCA omitir --event-safe-only; integrador desde USA con --experimental-parcial --event-safe-only; BPS con --experimental --event-safe-only y roundtrip SHA, sin sobrescribir entradas. Distinguir BPS origen USA, F1 o experimental.

Ejecutar:
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/f2-preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/f2-integrabilidad.json
python tools/f2_auditar_origen_iconos.py --iso-usa /RUTA/ISO_USA_PRIVADA.iso --reporte /tmp/f2-origen.json
python tools/f2_qa_raster_19.py --iso-usa /RUTA/ISO_USA_PRIVADA.iso --reporte /tmp/f2-metricas.json
(cd patcher && go test ./...)
git diff --check

Verificar GitHub Actions del HEAD final real y separar tests Python/Go/CI de pruebas PPSSPP visuales y funcionales. No atribuir hashes de PNG históricos a pruebas nuevas.

## 6. Estado final y RELEVO RECURSIVO

Actualizar herramientas, informes y reports/ESTADO_CONTINUIDAD_PPSSPP.json; indicar PCs MIPS, GE, RAM/VRAM efectivamente demostrados, hashes y bloqueos. F2 abierta hasta completar ruta gráfica, 19 caracteres multicontesto y regresión F1. F3 intro inglés; F4 referencias/saltos de 4524 scripts; F5 juego entero, HUD, inventario, retratos, enciclopedia, guardado/carga; F6 BPS final, EXE Windows y QA. Mantener PR #7 DRAFT hasta completar.

**REESCRIBIR COMPLETAMENTE prompts/SIGUIENTE_TAREA.md CON OTRO PROMPT COMPLETO AUTÓNOMO, MOSTRARLO AL USUARIO Y EXIGIR EN ESE NUEVO PROMPT QUE GENERE OTRO AL FINAL. Repetir recursivamente hasta finalizar F2–F6 y verificar la traducción integral.**
