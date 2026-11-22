# CLADUN ES — RELEVO AUTÓNOMO F2: hallar PPSSPP oficial, probar RAM→GE→VRAM y los 19 glifos

Actúa como especialista sénior PSP MIPS, PPSSPP oficial 1.20.4 y debugger WebSocket, GPU GE/VRAM, IMY/CLUT, DSARC/PSPFS, CP932, BPS e ingeniería inversa para la localización española de Cladun. Debes **realizar pruebas y cambios reales**, publicarlos en GitHub y separar lo efectivamente probado de las hipótesis. NO inventar PNG, ejecución PPSSPP, registros MIPS, direcciones VRAM o SHA.

**OBLIGACIÓN RECURSIVA:** AL FINAL REESCRIBE ÍNTEGRAMENTE ESTE MISMO ARCHIVO prompts/SIGUIENTE_TAREA.md con otro prompt autónomo completo que exija exactamente la misma obligación. Muéstralo íntegro al usuario. Repite en sucesivos relevos hasta completar y comprobar F2, F3, F4, F5 y F6; no prometas trabajos en segundo plano.

## 1. Repositorio y comprobaciones antes de escribir

Repositorio: https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama: integracion-eventos-segura-20261120
PR #7: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7
Base: revision-manual-dialogos

Mantener PR **DRAFT** (no merge). Antes de editar, verificar HEAD, árbol Git, PR y ambas Actions. Intentar desde checkout local:
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
git status --short
git rev-parse HEAD
Si falla por DNS, documentar el error y utilizar GitHub conectado con expected_sha, sin afirmar que los comandos se completaron. Nunca force push ni sobrescribir trabajo ajeno.

Leer íntegramente AGENTS.md, README.md, docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md, docs/RESULTADO_F1_PPSSPP_2026-11-21.md, docs/RESULTADO_F2_ATLAS_PPSSPP_2026-11-21.md, docs/F2_ICONOS_TINTA_PPSSPP_2026-11-21.md, docs/F2_AUDITORIA_ORIGEN_SOLO_LECTURA_2026-11-21.md, docs/F2_QA_ESTATICA_WS_2026-11-21.md, docs/F2_LECTOR_GE_V6_2026-11-21.md, docs/F2_RELEVO_CAPTURA_RAM_2026-11-21.md, docs/F2_FE_ERRATAS_SHA256_SNAPSHOT_RAM_2026-11-21.md, docs/F2_RELEVO_WS_BREAKPOINT_2026-11-21.md, docs/F2_PREPARACION_DIRECCIONES_GE_2026-11-21.md, docs/F2_INVENTARIO_SYSGRA_2026-11-22.md, reports/RESULTADO_F2_INVENTARIO_SYSGRA_2026-11-22.json, todos los reports F2 y reports/ESTADO_CONTINUIDAD_PPSSPP.json, este prompt y las herramientas/tests/patcher/workflows.

Prohibido subir a GitHub ISO, BPS, EBOOT, DATA.DAT, FONT.ARC, RAM, texturas, dumps GPU o capturas PNG comerciales. Evidencia de juego solo PRIVADA con SHA-256; al repositorio únicamente herramientas, tests, informes y metadatos permitidos.

## 2. Hechos autenticados y límites estrictos

ISO USA original del archivo 7z del usuario: 305496064 bytes. SHA256 exacto de 64 dígitos:
b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f
No usar la variante incorrecta de 62 dígitos: tests/test_f2_sha256_references.py lo impide.

ISO F1 canónica SHA256 496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986. BPS USA→F1 SHA256 daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd. AppImage PPSSPP oficial v1.20.4 SHA256 661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21.

F1 Opciones pasó históricamente en PPSSPP real bajo Xvfb 1280×720, ventana real 960×544, 756 píxeles interiores y ~764 exteriores. Textos: ID 005709 diez espacios ideográficos +7 ASCII, ID 005710 Sí, ID 005713 No con espacio ASCII de presentación. Una imagen del framebuffer PSP no es prueba de medidas X11; repetir regresión auténtica.

F2 fuente: 2721 glifos originales, 19 añadidos A1–B3 = 2740. Caracteres áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō. Búsqueda MIPS texto en 0x09075000 y PC 0x089089C8 instrucción lhu t2,0(t1) **NO demuestra gráficos de iconos**.

KITAJIMA_KARI.IMY de iconos CONTROLES: DATA.DAT → SYSGRA.ARC PSPFS índice225 offset895488 → DSARC índice17/27 offset57856, 2480 bytes, SHA256 0ce89df69ad71a9ef3165217d7cb98103a1fb0e08c53ca3a85c594dfaa7a2190, offset absoluto ISO 114723840 = 0x06D68C00. NO confundir offset ISO con RAM/VRAM. Experimento PPSSPP magenta anterior alteró 27 bytes RGB y seis iconos de CONTROLES, preservó 348 PSPFS y 26 DSARC vecinos; **NO atribuir HUD o combate sin pruebas**.

CLUT15 tinta amarilla RGB247,247,0 vs CLUT1 blanco RGB255,255,255. white_new_ink=True opcional altera 100 texels NUEVOS preservando 2721 glifos originales: mantener False predeterminado hasta QA real. ISO amarilla SHA256 58f98b65185f39f172de0b5da97b9ce6fecb009e61b9462632f602485c99e4ca; blanca a42731988835bddb9dc81ef6d242b9c5029030256f210838881a1d48aed2de33; BPS amarillo→blanco 2a698e1efaa1c2333dbd86ac8c3a9fabbd369382c4b8c7d3ad0ab7c7f2ffac3f. Antiguos 516 píxeles amarillos→cero en una ayuda NO prueban todos los caracteres.

## 3. Nuevo inventario real y qué demuestra

En el último relevo se volvió a EXTRAER y autenticar la ISO USA privada. SYSGRA.ARC ocupa 93696 bytes, SHA256 63d9443084a2aeab8c2a3f79aebdb130eaf6c5d2e86f8be51346d7458ab81854. Contiene 27 miembros IMY distintos, cada uno con SHA256, nombre, tamaño, offset y geometría de cabecera. Herramienta de solo lectura: tools/f2_inventario_sysgra_usa.py; tests/test_f2_inventario_sysgra_usa.py (8 nuevos). El informe privado de 27 metadatos tiene SHA256 b468a11f679f284979d9257bc58e9bc553fdd249940537fd4f745a3fa6b920eb.

**DOCE CANDIDATOS POR NOMBRE, NO PROBADOS EN PPSSPP:** HP_BAR.IMY, HP_KAO0.IMY, HP_KAO1.IMY, HP_KAO2.IMY, LVSP.IMY, LVSP_NUM.IMY, DAMAGE.IMY, EXP_BAR.IMY, MAHO_BAR.IMY, MAHO_ST.IMY, SYS1.IMY, ZOKUSEI.IMY. Sus nombres pueden orientar las sondas de HUD/combate, pero NO autorizan afirmar que aparecen ahí. Todo el resto de los 27 permanece indexado para buscar posibles iconos compartidos. Recomendación técnica: contrastar los 12 con capturas reales y controles negativos de CONTROLES/HUD/combate.

Commit de código del inventario bf5fa79a27f889e2391ff7d40b6b56c8bb7e28ca, Actions push 45039311711 y PR 45039317909 ambas SUCCESS: 221 tests Python, Go y Windows pública. NO es PPSSPP real.

Tools disponibles: tools/f2_ppsspp_ws_1204.py guarda broadcasts CPU sin ticket y hace screenshot GPU solo tras pausa; gpu.record.dump se inicia con CPU corriendo y da ESCENA_GE_PRIVATE.dump. tools/f2_ram_provenance_1204.py escanea RAM con CPU detenida y ticks estables, preserva otros breakpoints y solo atribuye hits con reason memory.breakpoint y relatedAddress exacto. tools/f2_ge_dump_1204.py lee PPSSPPGE v6 Zstd y extrae candidatos de textura, CLUT y transferencia, pero sin prueba MIPS→GE→VRAM. NO confundir una dirección candidata con recurso identificable.

## 4. PRIORIDAD: arrancar PPSSPP 1.20.4 y cerrar evidencia pendiente

Buscar PPSSPP oficial tag v1.20.4 en https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4, autenticar AppImage por SHA antes de ejecutar. Verificar existencia de F1 canónica o reconstruir mediante herramientas seguras desde ISO USA sin alterar original; exigir coincidencia de SHA y preservar --event-safe-only. En el entorno último no había binario PPSSPP ni F1 y Git fallaba por DNS: no fingir instalación/arranque. Xvfb 1280×720 y scrot permiten preparar ventana real 960×544 SOLO si PPSSPP se consigue.

Arrancar Cladun auténtico y situarlo visualmente en CONTROLES. Depurador WebSocket ws://127.0.0.1:24192/debugger, subprotocolo debugger.ppsspp.org; confirmar version y game.status. Eventos reales: cpu.status, cpu.stepping, cpu.resume, memory.read, memory.disasm, memory.breakpoint.list/add/remove, cpu.getAllRegs, gpu.buffer.screenshot, gpu.record.dump. NO usar eventos inexistentes cpu.breakpoint.hit ni gpu.displaylist.disasm.

Con CPU corriendo y carpeta PRIVADA NUEVA:
python tools/f2_ppsspp_ws_1204.py --scene CONTROLES --salida-privada /tmp/cladun-f2-controles-REAL-nuevo --port 24192 --ge-dump

Analizar el dump auténtico creado:
python tools/f2_ge_dump_1204.py --entrada-privada /tmp/cladun-f2-controles-REAL-nuevo/CONTROLES_GE_PRIVATE.dump --reporte-privado /tmp/cladun-f2-ge-REAL.json

Autenticar firma de origen con carpeta privada nueva:
python tools/f2_ram_provenance_1204.py --iso-usa /PRIVATE/USA.iso --salida-privada /tmp/cladun-f2-firma-nueva --solo-origen

Después --scan-ram en otra carpeta, y SOLO SI se demuestra una coincidencia real en PSP RAM, recargar la escena y vigilar con --watch-address 0xDIRECCION_RAM (nunca offset ISO) con un solo cliente. Registrar reason memory.breakpoint, relatedAddress, PC auténtico, registros, descompresión, memoria de textura, CLUT, comandos GE, transferencia VRAM y resultado dibujado. Atribuir cada eslabón solo con prueba; una firma RAM, candidato TEXADDR o PRIM aislado no demuestran causalidad. Comprobar iconos por separado CONTROLES, HUD, tutoriales, ayudas, diálogos y combate con controles positivos/negativos y dos PNG auténticos con SHA por estado.

## 5. QA de 19 signos, F1 y seguridad binaria

Validar visual y funcionalmente áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō, espaciado/ancho, tilde, avance, interlineado, clipping de í x4 y mayúsculas y15, signos □○×△ y L/R, color y compatibilidad con menús, diálogos, tutorial y combate. Si no hay suficientes ejemplos, tools/generar_probe_f2_glifos.py puede generar CSV diagnóstico PRIVADO de 9237 filas para probar sin tocar corpus canónico. tools/generar_probe_f2_tinta.py permite comparar tinta optativa, NO habilitar True por defecto sin F1 regresada. Para F1 medir en captura de ventana REAL 960×544 756/~764, 005709/005710 Sí/005713 No y navegación completa.

Blindaje: conservar 349 PSPFS, 345 fuera de cuatro contenedores, 348 vecinos con FONT.ARC/SYSGRA.ARC aislados, 26 DSARC KITAJIMA, demás ISO9660 intacto; SCRIPT.DAT 51705 comandos, 46308 no textuales, 1625 comienzos, cero desplazamientos y 4524 traducciones script aplazadas. Nunca quitar --event-safe-only. Integración experimental desde USA: --experimental-parcial --event-safe-only; BPS experimental con --experimental --event-safe-only, verificar SHA de fuente/resultado y roundtrip.

Si el checkout existe, ejecutar:
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/f2-preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/f2-integrabilidad.json
python tools/f2_auditar_origen_iconos.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-origen.json
python tools/f2_qa_raster_19.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-glifos.json
python tools/f2_inventario_sysgra_usa.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/f2-sysgra.json
(cd patcher && go test ./...)
git diff --check

Diferenciar siempre tests sintéticos/CI de emulación real, y comprobar ambas GitHub Actions del HEAD FINAL. Registrar los bloqueos exactos cuando no sea posible ejecutar una prueba.

## 6. Relevo y fases F3–F6

Publicar código, tests, informes y continuidad (reports/ESTADO_CONTINUIDAD_PPSSPP.json) con commit y SHA auténticos, hashes privados reales y estados NO PROBADO para lo no realizado; no publicar recursos propietarios. Mantener PR #7 DRAFT.

F2 permanece ABIERTA hasta tener MIPS/RAM→GE→VRAM demostrado, 19 glifos multicontesto y F1 auténtica a 960×544. F3 introducir y probar intro inglesa; F4 reparar referencias y saltos de 4524 textos script, con integridad; F5 recorrer aventura, batalla, HUD, retratos, inventario, enciclopedia, guardar/cargar; F6 parche BPS final, EXE Windows y QA integral.

**OBLIGACIÓN RECURSIVA FINAL: REESCRIBIR ÍNTEGRAMENTE prompts/SIGUIENTE_TAREA.md AL TERMINAR ESTA TAREA CON OTRO PROMPT COMPLETO, MOSTRARLO AL USUARIO Y VOLVER A EXIGIR EN ÉL LA MISMA RECURSIVIDAD HASTA F2–F6 FINALIZADOS Y PROBADOS.**
