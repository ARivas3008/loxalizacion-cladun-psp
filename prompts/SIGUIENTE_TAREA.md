# CLADUN ES — RELEVO AUTÓNOMO F2: A/B TUIKA REAL EN COMBATE, GE-ONLY, 19 GLIFOS, Y F3–F6

Actúa como ingeniero sénior de PSP MIPS y PPSSPP oficial v1.20.4, WebSocket 24192, ISO9660/PSPFS/DSARC, IMY 4bpp/CLUT, fuentes CP932 A1–B3, GE/VRAM y localización española. **EJECUTA diagnósticos y cambios auténticos, no te limites a planificar.** Nunca inventes capturas, fotogramas, tramas GE, PCs MIPS, direcciones, hashes, acciones GitHub, validaciones ni un emulador que no has lanzado. Distingue (A) ISO auténtica e inspección binaria, (B) tests sintéticos y CI, (C) PPSSPP auténtico de Cladun.

**OBLIGACIÓN RECURSIVA INNEGOCIABLE:** AL TERMINAR, REESCRIBE POR COMPLETO prompts/SIGUIENTE_TAREA.md con OTRO PROMPT NUEVO, AUTÓNOMO E ÍNTEGRO, con estado real, rutas, hashes, pruebas, CI, bloqueos, órdenes y criterios verificables. MUESTRA ÍNTEGRO EL NUEVO PROMPT AL USUARIO. En su texto, exige OTRA VEZ esta misma REGENERACIÓN RECURSIVA al concluir el próximo relevo y todos los siguientes F2–F6, incluso si una fase continúa bloqueada. No prometer trabajo diferido.

## 1. Identidad, HEAD y lectura obligatoria

Repo: https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama: integracion-eventos-segura-20261120
PR #7: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7
Base: revision-manual-dialogos. Mantener PR OPEN/DRAFT, no fusionar, no force push, ni modificar corpus original o recursos ajenos.
HEAD antes de este relevo: 46df9c92135821a74d8bcb9990212cd422aef67b. Es histórico: **verifica HEAD actual antes de editar** y conserva los avances paralelos F3 y los nuevos commits de otros trabajos.

Leer COMPLETOS y en orden: AGENTS.md; README.md; prompts/SIGUIENTE_TAREA.md; reports/ESTADO_CONTINUIDAD_PPSSPP.json; docs/F2_GE_ONLY_WEB_SOCKET_SIN_FRAMEBUFFER_2026-11-23.md; reports/RESULTADO_F2_GE_ONLY_Y_ISO_2026-11-23.json; docs/F2_REVALIDACION_ISO_TUIKA_Y_RELEASE_WS_2026-11-23.md; reports/RESULTADO_F2_REVALIDACION_ORIGINAL_Y_RELEASE_2026-11-23.json; docs/F2_MAPA_JUGABLE_GE_X11_F1_2026-11-23.md; reports/RESULTADO_F2_MAPA_JUGABLE_F1_2026-11-23.json; docs/F2_WS_REAL_F1_CONTROLES_GE_2026-11-23.md; docs/F2_PPSSPP_REAL_X11_AB_TUIKA_2026-11-23.md; docs/F2_TUIKA_SUBREGIONES_PROTEGIDAS_2026-11-23.md; docs/F2_TUIKA_CATALOGO_ROTULOS_2026-11-22.md; docs/RESULTADO_F1_PPSSPP_2026-11-21.md; docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md; docs/F3_PROLOGO_ANIME000_DEPENDENCIA_PPSSPP_REAL_2026-11-23.md y reportes F3 que cite el estado JSON. Lee también los tests y herramientas pertinentes, sin confundir un checkout con copias parciales.

Herramientas centrales: tools/f2_ppsspp_ws_1204.py; tools/f2_ruta_ws_liberacion_segura.py; tools/f2_ws_procedencia_ppsspp.py; tools/f2_x11_ppsspp_procfs_capture.py; tools/f2_iso_proceso_ppsspp.py; tools/f2_probe_tuika_palette_privado.py; tools/f2_cotejar_capturas_tuika.py; tools/f2_ge_dump_1204.py; tools/f2_ram_provenance_1204.py; tools/f2_qa_raster_19.py; tools/f2_tuika_proteger_subregiones.py; tools/f2_auditar_origen_iconos.py; tools/integrar_parche_seguro.py y tools/script_event_guard.py. Ruta visual *orientativa*, no probada en USA/sonda: docs/F2_RUTA_VISUAL_WS_EJEMPLO_2026-11-23.json.

Comprobar checkout auténtico:

    git fetch origin
    git switch integracion-eventos-segura-20261120
    git pull --ff-only
    git rev-parse HEAD
    git status --short

Si git falla por DNS, usar conector GitHub: fetch ref/tree y commit mediante create_blob/create_tree/create_commit, update_ref con expected_sha y force:false. No sobrescribir avances de otros agentes.

## 2. Evidencia A auténtica revalidada en el relevo anterior

El usuario aportó archivo 7z y se extrajo físicamente con libarchive.so.13 una ISO USA original de **305.496.064 bytes**, SHA256 **b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f**. Una copia privada derivada con tres bytes CLUT2 de TUIKA reemplazados, offsets ISO **114744872–114744874**, RGB [249,251,249]→[255,0,255], alfa intacto, tiene 305.496.064 bytes, SHA256 **b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa**.

Se verificaron sobre ambas ISOs auténticas: tabla PSPFS_V1 de 349 recursos idéntica; 348/348 PSPFS vecinos de SYSGRA iguales; SYSGRA.ARC índice 225, offset relativo 895488, longitud 93696, SHA original **63d9443084a2aeab8c2a3f79aebdb130eaf6c5d2e86f8be51346d7458ab81854**; tabla DSARC FL 27 idéntica; 26/26 vecinos DSARC intactos; TUIKA_MES.IMY DSARC índice 24, offset 78848, tamaño 7912, SHA original **c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127**, SHA sonda **efcf4f41f57c300476e8ce54a32dea01f242dda3fbf3fb9c4e0b582bad8f5252**.

Informe privado SOLO metadatos (no ISO/PNG/GE): F2_ISO_Y_TUIKA_AUDITORIA_REAL_NUEVA_20261123.json SHA256 **60c40acff0726b79e0be60d4b98a7fd6886194c97de90b36ece35eea0230836e**. No publicar imágenes comerciales, ISOs, BPS, FONT, EBOOT, DATA.DAT ni dumps de juego en Git. A prueba bytes, NO prueba aparición gráfica.

## 3. Evidencia B y cambio causal del capturador GE

El relevo anterior añadió flag **--ge-only** a tools/f2_ppsspp_ws_1204.py, usable SOLAMENTE con **--ge-dump**. Antes un dump gpu.record.dump podía existir, pero la lectura posterior gpu.buffer.screenshot fallaba y el programa no llegaba a escribir manifest_PRIVATE.json. Con --ge-only y CPU corriendo se solicita grabación GE, valida prefijo PPSSPPGE, guarda dump y manifiesto privado con screenshots=[] y explícito gpu_framebuffer_readback_attempted=false. NO se detiene CPU ni se intenta recuperar framebuffer, NO se afirma textura TUIKA/MIPS/VRAM.

Se añadieron 3 tests sintéticos al archivo tests/test_f2_ppsspp_ws_1204.py para modo GE-only, rechazo si no hay --ge-dump y rechazo si CPU estaba detenida. No etiquetar CI como runtime. La ruta WebSocket de botón seguro ya añadió 17 tests sintéticos y exige checkpoints manuales, 12 botones documentados, liberación input.buttons.send todos false después de cada press y durante timeout con ACK: tools/f2_ruta_ws_liberacion_segura.py. Si ACK de release falta, abortar y reiniciar; no creer que el botón quedó liberado.

**Diagnóstico del error gpu.buffer:** código fuente auténtico PPSSPP v1.20.4 Core/Debugger/WebSocket/GPUBufferSubscriber.cpp contiene dos rechazos distintos: Neither CPU or GPU is stepping antes de leer el buffer; Could not download output ocurre cuando el proveedor GPUStepping::GPU_GetOutputFramebuffer (para screenshot) devuelve false. La causa profunda en backend OpenGL/llvmpipe NO está demostrada, y no debe atribuirse automáticamente a base64, URI o a llvmpipe. Revisar backend real y devolver evidencia, no conjeturas.

## 4. Evidencia C histórica — NO ejecutada en el último relevo

- PPSSPP oficial Linux x86_64 AppImage **v1.20.4**, 50.689.748 bytes SHA **661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21**. En sesiones previas Xvfb 1280×720, ventana X11 960×544, OpenGL/llvmpipe o Vulkan/lvp según configuración real. Shim audio externo en algunas sesiones con SHARUN_ALLOW_LD_PRELOAD=1; ejecutable intacto.
- ISO F1 española canónica histórica 306.456.576 bytes SHA **496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986**, uso de --experimental-parcial --event-safe-only. Ventana Opciones **756px interiores/≈764px exteriores** y tildes «música»/«Sí» correctas; R/L/□/×/○/△ visibles en Controles. No equivalen a 19 glifos multicontesto.
- WebSocket real 24192, subprotocolo debugger.ppsspp.org, version=1.20.4, game.status=NPUH10072, cpu.status corriendo; el mismo PID poseía socket LISTEN y FD ISO por /proc. Esto no demuestra qué textura llegó a GPU.
- F1 llegó realmente a primer mapa con HUD, personaje y movimiento tras Comenzar → música Real → diálogo Cheery Girl con **START SKIP**. No llegó a combatir/trampa/habilidad certificada. Dump GE real **65.309 bytes**, SHA **d2195fbedd6f430d2a3823db28c12f9f9a9bc789964adefead0bab19298f06b4**, 989 registros v6, 301 PRIM, 43 TEXADDR0, 40 CLUTADDR; sin identidad TUIKA demostrada.
- En OpenGL/llvmpipe fallaron gpu.buffer.screenshot/renderColor/renderDepth «Could not download output» aun con CPU detenida; CPU fue reanudada. PNG históricos son de ventana X11, NO framebuffer PSP WS.
- Splash SYSTEM PRiSM contiene 1.152 píxeles magenta NATIVOS tanto en USA como sonda, 0 diferencias A/B. CONTROL NEGATIVO: NO usar de prueba TUIKA.

**Bloqueo actual:** en el último contenedor no había AppImage PPSSPP 1.20.4 ni F1, y terminal github.com DNS fallaba. NO se ejecutó PPSSPP genuino, no se generaron nuevos PNG ni GE reales allí. Intentar auténticamente en el entorno nuevo y declarar lo ocurrido, sin suponer que reproducirá el histórico.

## 5. TAREA PRIORITARIA F2: escena A/B real en TUIKA

1. Autentica SHA/tamaño USA, sonda, PPSSPP y F1 si disponible. Sonda siempre en directorio PRIVADO y original inmutable, o reconstruir con tools/f2_probe_tuika_palette_privado.py validando todos los bytes.
2. Inicia PPSSPP 1.20.4 genuino con servidor WS 24192, X11, backend constatado. Verifica con tools/f2_ws_procedencia_ppsspp.py PID/starttime actuales, descriptor/inodo ISO y socket LISTEN del MISMO PID, versión exacta y CPU. No reutilizar PIDs antiguos.
3. Desde título **USA**, Comenzar → Real → intro → Cheery Girl → pulsar START solo si está visible START SKIP. Verifica cada checkpoint visualmente; la ruta JSON del repositorio no es evidencia autónoma de recorrido. Llegar desde mapa a mensaje REAL de habilidades/trampas/ataque especial/recuperación SP (no al splash). Usar tools/f2_ruta_ws_liberacion_segura.py y liberar pulsaciones con ACK incluso tras timeout.
4. Reproducir **sonda** en instancia limpia, sin savestate con textura/RAM/VRAM heredada de USA. Registrar controles reales, posición, estado y ticks observados, no fabricarlos. Sin escena común demostrada no comparar falsamente.
5. En la MISMA escena y fase, capturar X11 originales con herramientas procfs y, con CPU corriendo, GPU GE separado usando:
    python tools/f2_ppsspp_ws_1204.py --scene TUIKA_HABILIDAD --salida-privada /PRIVATE/GE_A_NUEVO --port 24192 --ge-dump --ge-only --pid-ppsspp PID_ACTUAL --iso-en-proceso /PRIVATE/USA.iso --tipo-iso usa
   Repetir con --tipo-iso sonda y carpeta/PID nuevo. No llamar PNG a GE-only. Analizar con tools/f2_ge_dump_1204.py y buscar TEXADDR/CLUT/PRIM, y trazar IMY→RAM→GE→VRAM con herramientas MIPS solo con eventos auténticos, no inferencias de nombre/direcciones parciales.
6. Para A/B imagen usar X11 verdadero y testigos de fuente si gpu.buffer.* sigue fallando, o PNG auténticos framebuffer WS si se logra; documenta cuál. tools/f2_cotejar_capturas_tuika.py solo acepta dos PNG **del framebuffer PSP** con manifiestos WS apropiados: nunca alimentarlo con X11/GE-only. Comparar por píxeles ROI, posición, ticks/temporización y controles negativos; magenta nuevo aislado es candidato hasta vincular TUIKA.
7. Investigar buffer readback en otro backend genuino por separado; aún no se sabe por qué GPUStepping devuelve false. No alterar binario oficial ni inventar un framebuffer.
8. Protege 7 subregiones y separadores de las 14 bandas de TUIKA: iconos, números y grafía japonesa no pueden ser repintados en bloque; tampoco basta con cambiar CLUT2.

**Criterio de cierre F2-TUIKA:** evento de combate/habilidades/trampas comprobado en ambas ISOs, captura A/B comparable con control y atribución causal a TUIKA/CLUT GE; si falla, F2 sigue abierta.

## 6. F2 fuentes, glifos y F1

En PPSSPP REAL revisar **áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō** en diálogos, ayuda, opciones, HUD, ciudad, tutorial, combate, paletas blanca/amarilla, cortes, ancho e interlineado. Distinguir FONT.ARC/FONT_00.IMY de 512×256 y SYSGRA.ARC/FONT.IMY de 256×256. KITAJIMA_KARI.IMY explicó seis iconos SOLO en Controles; no extender conclusión a HUD/combat. Conservar 2.721 glifos originales y 19 nuevos A1–B3; white_new_ink=False por defecto hasta QA multicontesto. Repetir regresión F1 Opciones 756/≈764 y valores Sí/No.

## 7. F3–F6 aún abiertas y restricciones

F3: prólogo visual en inglés sin fuente demostrada. Otra línea hizo A/B/A PPSSPP real renombrando un byte ANIME000.IDT→ANIME000.XDT en ISO diagnóstica privada (SHA **576e9699395dd142b666ed3b9d121db5037c63302dc0c4eee862a04ccfcdbb36**), que causó INVALID MEMORY ACCESS antes de título (PC 0x08809498, dirección 0x00000015); volver a USA recuperó título. Esto demuestra dependencia del arranque, NO procedencia de letras. En scripts demo1001_00/01 hay 97 textos no vacíos ya traducidos, 85 de longitud distinta pospuestos. Identificar origen visual y saltos antes de integración.
F4: modelar referencias/saltos SCRIPT.DAT/MIPS antes de permitir **4.524** cambios aplazados. Conserva 51.705 comandos, 46.308 no textuales y 1.625 comienzos. Nunca quitar --event-safe-only por simple cálculo de bytes.
F5: QA integral ciudad, pisos, combate, habilidades, trampas, menús, HUD, enciclopedia, inventario, retratos, tiles, guardado/carga y audio con evidencias auténticas.
F6: BPS roundtrip/hash ISO e integridad 349 PSPFS, EXE privado Windows x64 probado en Windows real o VM, release solo después QA integral.

Respetar 9.237 registros corpus originales, 9.235 traducciones españolas/2 excepciones, 2.721 glifos anteriores, 19 nuevos, white_new_ink=False, --experimental-parcial --event-safe-only y todas las subregiones protegidas. No subir contenido comercial a Git.

## 8. Comandos de validación, CI, documentación y relevo

    sha256sum /PRIVATE/USA.iso /PRIVATE/TUIKA_SONDA.iso /PRIVATE/PPSSPP-v1.20.4-anylinux-x86_64.AppImage
    python tools/f2_ws_procedencia_ppsspp.py --pid PID_ACTUAL --port 24192 --iso-privada /PRIVATE/USA.iso --tipo usa --informe-privado /PRIVATE/USA_WS_PID.json
    python tools/f2_ruta_ws_liberacion_segura.py --ruta-json docs/F2_RUTA_VISUAL_WS_EJEMPLO_2026-11-23.json --pid PID_ACTUAL --iso-privada /PRIVATE/USA.iso --tipo usa --port 24192 --informe-privado /PRIVATE/USA_RUTA.json
    python tools/f2_x11_ppsspp_procfs_capture.py --display :98 --pid PID_ACTUAL --iso /PRIVATE/USA.iso --tipo usa --png-privado /PRIVATE/USA_X11.png --manifiesto-privado /PRIVATE/USA_X11.json
    python tools/f2_ppsspp_ws_1204.py --scene TUIKA_HABILIDAD --salida-privada /PRIVATE/GE_A --port 24192 --ge-dump --ge-only --pid-ppsspp PID_ACTUAL --iso-en-proceso /PRIVATE/USA.iso --tipo-iso usa
    python tools/f2_ge_dump_1204.py --entrada-privada /PRIVATE/GE_A/TUIKA_HABILIDAD_GE_PRIVATE.dump --reporte-privado /PRIVATE/GE_A_ANALISIS.json
    python -m unittest discover -s tests -v
    python tools/verificar_integridad.py --raiz .
    python tools/verificar_borrador_es.py
    python tools/auditar_preinsercion_es.py --reporte /tmp/preflight_F2_nuevo.json
    python tools/reportar_integrabilidad_es.py --reporte /tmp/integrabilidad_F2_nuevo.json
    (cd patcher && go test ./...)
    git diff --check

Para sonda usar --tipo sonda / --tipo-iso sonda en nueva instancia, PID y rutas privadas diferentes. No ejecutar comandos WS si no escucha puerto. Guardar capturas/GE/ISO sólo fuera de Git; publicar solo código, tests, informes de métricas y SHA. Después documentar resultados A/B/C en nuevo docs/ y reports/, actualizar reports/ESTADO_CONTINUIDAD_PPSSPP.json y este prompt, crear commit GitHub sin fuerza con expected_sha y preservar PR #7 OPEN/DRAFT. Verifica **CI push y PR SUCCESS sobre EL MISMO HEAD FINAL** o declara por qué falta; no copiar éxitos de otro SHA.

**OBLIGACIÓN RECURSIVA FINAL:** Al terminar reemplaza COMPLETAMENTE prompts/SIGUIENTE_TAREA.md con OTRO PROMPT AUTÓNOMO, nuevo, actualizado y COMPLETO, y muéstralo ÍNTEGRO al usuario. Ese siguiente prompt DEBE EXIGIR DE NUEVO LO MISMO al próximo agente, sucesivamente hasta que F2–F6 estén efectivamente probadas. La obligación sigue vigente aunque una fase esté bloqueada; nunca inventar resultados ni prometer trabajo diferido.
