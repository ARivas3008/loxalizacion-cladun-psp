# CLADUN ES — NUEVO RELEVO AUTÓNOMO F2: PPSSPP 1.20.4 REAL, WebSocket ausente, TUIKA en gameplay, X11→PID→ISO, 19 glifos y continuidad F3–F6

Actúa como especialista en PSP/MIPS, depurador WebSocket de PPSSPP oficial 1.20.4, GE/VRAM, ISO9660, PSPFS/DSARC, fuentes IMY 4bpp/CLUT, CP932 y localización al español. **Realiza trabajo real**, modifica código y ejecuta pruebas con evidencia auténtica; no redactes únicamente recomendaciones. Distingue estrictamente lectura de ISO comercial autenticada, pruebas sintéticas y ejecución de juego REAL. No inventes IDs, hashes, imágenes, conexiones WS, PC MIPS, direcciones GPU, frames, saltos ni resultados.

**OBLIGACIÓN RECURSIVA:** al acabar TU tarea, sustituye COMPLETAMENTE `prompts/SIGUIENTE_TAREA.md` con OTRO NUEVO prompt autónomo que repita esta obligación, que indique absolutamente todo lo necesario para continuar (estado, commits, archivos, rutas, hashes, fallos, diagnósticos, comandos, evidencias, seguridad, siguientes fases) y **MUÉSTRALO ÍNTEGRO AL USUARIO**. Repite este procedimiento en cada futuro relevo F2–F6. Nunca prometas trabajar en segundo plano ni declarar éxito sin pruebas.

## 1. Repositorio y estado real obligatorio

Repositorio: https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama de trabajo: `integracion-eventos-segura-20261120`.
PR #7: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7 (base `revision-manual-dialogos`; mantener OPEN/DRAFT, nunca merge ni force push).

Antes de cambiar archivos, leer y comprobar el HEAD ACTUAL, tree, PR y Actions del HEAD final, no usar un SHA antiguo como HEAD supuesto. Si `git fetch` falla por DNS, usar conector GitHub (`fetch_file`, `create_blob`, `create_tree`, `create_commit`, `update_ref` con SHA esperado y `force:false`) sin fingir checkout local. Ejecutar tests reales contra un snapshot autenticado del mismo HEAD. No dejar workflows temporales de exportación.

Documentación y estado PRIORITARIOS que debes leer COMPLETOS:
- `AGENTS.md`, `README.md` y `prompts/SIGUIENTE_TAREA.md`.
- `docs/F2_PPSSPP_REAL_X11_AB_TUIKA_2026-11-23.md` y `reports/RESULTADO_F2_PPSSPP_REAL_X11_AB_TUIKA_2026-11-23.json`.
- `reports/ESTADO_CONTINUIDAD_PPSSPP.json`.
- `docs/F2_PROCEDENCIA_ISO_PROCESO_PPSSPP_2026-11-23.md`, `reports/RESULTADO_F2_PROCEDENCIA_ISO_PROCFS_2026-11-23.json`.
- `docs/F2_TUIKA_SUBREGIONES_PROTEGIDAS_2026-11-23.md`, `docs/F2_MAPA_FRANJAS_TUIKA_2026-11-22.md`, `docs/F2_TUIKA_CATALOGO_ROTULOS_2026-11-22.md`.
- `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, `docs/RESULTADO_F1_PPSSPP_2026-11-21.md`, `docs/RESULTADO_F2_ATLAS_PPSSPP_2026-11-21.md` y demás auditorías F2 y reportes JSON.
- `tools/f2_x11_ppsspp_procfs_capture.py`, `tests/test_f2_x11_ppsspp_procfs_capture.py`, `tools/f2_ppsspp_ws_1204.py`, `tools/f2_iso_proceso_ppsspp.py`, `tools/f2_cotejar_capturas_tuika.py`, `tools/f2_ge_dump_1204.py`, `tools/f2_ram_provenance_1204.py`.
- `tools/f2_probe_tuika_palette_privado.py`, `tools/f2_tuika_proteger_subregiones.py`, `tools/f2_qa_raster_19.py`, `tools/f2_auditar_origen_iconos.py`, `tools/integrar_parche_seguro.py` y `tools/script_event_guard.py`.

## 2. Estado autentificado al cierre del relevo 23/11

**ISO USA original privada del 7z del usuario:**
- 305.496.064 bytes; SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. Debe verificarse nuevamente antes de usar.
- La ISO F1 históricamente aprobada en PPSSPP tiene SHA `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`; no fue regenerada ni sometida a regresión nueva en este relevo.
- Sonda privada TUIKA magenta regenerada desde original: SHA `b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa`. SOLO 3 bytes RGB cambiados en offsets absolutos 114744872–114744874. Se validaron 348/348 PSPFS vecinos y 26/26 DSARC vecinos. No se editó ningún texto ni gráfico fuera de paleta.

**PPSSPP auténtico:**
- Oficial `PPSSPP-v1.20.4-anylinux-x86_64.AppImage`: 50.689.748 bytes, SHA256 `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`.
- Se recuperó y ejecutó en Linux x86_64 bajo Xvfb 1280×720, SDL/ventana X11 960×544, software renderer. Logs REAL muestran `Booted` de ISO USA y de sonda.
- Problema de audio específico del contenedor: launcher transformaba `SDL_AUDIODRIVER=dummy` en `pulseaudio`; para permitir ejecución se usó un shim EXTERNO/PRIVADO `LD_PRELOAD` que devuelve `dummy` para `getenv("SDL_AUDIODRIVER")`. El binario de PPSSPP no se modificó. Si el sistema nuevo ejecuta directamente, no imponer shim; si lo usa, registrarlo. Jamás incluir binario comercial o shim compilado en Git.
- Nueva herramienta X11 vincula ventana `NPUH10072 : CLADUN: This is an RPG!`, `_NET_WM_PID` y descriptor `/proc/<pid>/fd` al inodo de ISO autenticado, con PID/starttime estables antes/después. **No acredita juego cargado funcionalmente ni relación con servidor WS o textura GE**. PIDs 1574/1948/2141 fueron efímeros, NO reutilizarlos.
- 7 tests sintéticos X11 nuevos, suite local **482 tests Python OK (uno omitido)**, verificadores de corpus, borrador y auditorías estáticas OK. Go normal OK; Go `cladun_embedded` no ejecutable en snapshot sin BPS privado (`go:embed`). Windows sin payload compila.

**A/B de splash — falsación importante:**
- En la captura de `SYSTEM PRiSM` la ISO sonda contiene 1.152 píxeles RGB(255,0,255), pero **el juego USA ORIGINAL también tiene exactamente 1.152**.
- PNG original y sonda SHA256 idénticos `c20b515ddee01cdfd1bd55de184c079fc1a50ad45df9512dc5d9bf2a15fa078f` y **0/522.240 píxeles RGB distintos**. **No es evidencia de efecto de TUIKA**. Las capturas diferentes de logos/ticks dan falsos positivos, y el color magenta natural no sirve para identificar esa textura.
- Evidencias privadas de la conversación (no Git) contienen las capturas y manifiestos. No extraer imágenes de textos del repositorio ni publicarlas en Git.

**WS BLOQUEADO:**
- Se probaron configuración `RemoteDebuggerOnStartup=True`, puerto `24192` y CLI `--debugger=24192`, pero no se vio servicio TCP escuchando. NO hubo conexión WS real, `gpu.record.dump`, `gpu.buffer.screenshot`, ni trazas RAM/GE.
- No concluir que PPSSPP 1.20.4 no tiene WS: investigar configuración, servicios, parámetros reales y posibles diferencias SDL/Qt; verificar con un socket auténtico y protocolo `debugger.ppsspp.org`. No inventar éxitos.

**F2 ABIERTA:** 19 glifos `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō`, símbolos L/R/□○×△, CLUT en amarillo/blanco, textos de TUIKA y su uso en juego NO validados multicontesto. Código mantiene `white_new_ink=False`. FONT.ARC/FONT_00.IMY 512×256 es DISTINTO de SYSGRA.ARC/FONT.IMY 256×256. Las 14 franjas TUIKA incluyen números/japonés/controles protegidos: no son 14 cadenas editables ni hay ROIs aprobadas. F1 opciones solo PASÓ históricamente; sin regresión nueva. F3–F6 pendientes, 4.524 traducciones de longitud distinta aplazadas para proteger offsets de 51.705 comandos/1.625 scripts.

## 3. TAREA PRIORITARIA AHORA: efecto funcional real de TUIKA y WS

1. Obtener y SHA-verificar PPSSPP oficial 1.20.4, original y sonda, antes de ejecutar. Si no se puede descargar, revisar si el AppImage oficial ya existe en adjuntos de la conversación, como se consiguió en el relevo 23/11. No confundir metadatos remotos con archivos presentes.
2. Abrir PPSSPP y comprobar que TÍTULO, PID, _NET_WM_PID, /proc starttime, ISO fd y pantalla X11 pertenecen a la misma sesión. Usar `f2_x11_ppsspp_procfs_capture.py` para corroboración, no como sustituto de GPU. Si no hay fd, dejar desconocido.
3. **Habilitar WS REAL** de PPSSPP 1.20.4: verificar opción Developer Tools/Remote Debugger, archivo de configuración efectivamente leído, puerto TCP en LISTEN, handshake WebSocket, `version`, `game.status` y `cpu.status`. Si la build SDL lo impide, probar otra build oficial 1.20.4 compatible o documentar el bloqueo técnicamente; no simular server ni usar HTTP 8080 ajeno a PPSSPP.
4. Llegar por **gameplay REAL** a una pantalla con mensajes de habilidad/combate/trampas donde `SYSGRA.ARC/TUIKA_MES.IMY` sea candidata razonable. No asumir uso por nombre de archivo o por la pantalla de splash. Conservar un estado reproducible de juego y entrar al MISMO lugar en ambas ISO.
5. Grabar A (USA) y B (sonda) con igual escena, posición, animación/ticks o sincronización documentada; controles negativos y positivos. Cotejar PNGs, áreas, color y contexto, excluyendo falsos positivos naturales de `SYSTEM PRiSM`. Si NO aparece magenta, registrar resultado negativo en esa escena, que NO descarta TUIKA en todas las escenas.
6. Si WS conecta: grabar `gpu.record.dump` con CPU en ejecución; pausar correctamente para `gpu.buffer.screenshot`; asociar datos a PID/ISO y sin confundir ventana X11 con framebuffer PSP. Analizar `f2_ge_dump_1204.py`, RAM read/watchpoint real, GE TEXADDR, CLUT, PRIM, TRANSFERSTART y VRAM. No confundir offset ISO `0x06D68C00` con dirección MIPS. No atribuir a iconos el PC `0x089089C8` (búsqueda de fuente TEXTOS, no iconos).
7. **Revalidar F1** realmente en PPSSPP: X11 960×544, Opciones interior aprox. 756 px/exterior 764 px, música/configuración, IDs `005709`, `005710 Sí`, `005713 No`; navegación y no solapamiento.
8. **19 glifos y símbolos**: verificar en Controles, ayuda, diálogo, HUD y combate; métricas, signos, colores, índices físicos, fuentes independientes y recortes. Mantener `white_new_ink=False` salvo prueba real multicontesto.
9. Si el problema queda bloqueado, dejar código nuevo y pruebas de la próxima hipótesis concreta; NO declarar F2 cerrada. Añadir tests de regresión para el fallo realmente encontrado.

## 4. Rutas, comandos reproducibles y seguridad

~~~bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
git status --short
git rev-parse HEAD
git rev-parse 'HEAD^{tree}'
# Si falla DNS, operar mediante conector GitHub; nunca fingir git local.
sha256sum /PRIVATE/USA.iso /PRIVATE/PPSSPP-v1.20.4-anylinux-x86_64.AppImage
python tools/f2_probe_tuika_palette_privado.py --iso-usa /PRIVATE/USA.iso \
  --salida-iso-privada /PRIVATE/TUIKA_sonda_nueva.iso \
  --reporte-privado /PRIVATE/sonda_nueva.json
python tools/f2_tuika_proteger_subregiones.py --iso-usa /PRIVATE/USA.iso \
  --reporte-privado /PRIVATE/subregiones_nuevas.json
python tools/f2_auditar_origen_iconos.py --iso-usa /PRIVATE/USA.iso --reporte /PRIVATE/iconos_nuevos.json
python tools/f2_qa_raster_19.py --iso-usa /PRIVATE/USA.iso --reporte /PRIVATE/glifos_nuevos.json
# Con PPSSPP X11 realmente iniciado y PID confirmado:
python tools/f2_x11_ppsspp_procfs_capture.py --display :95 --pid PID_REAL --iso /PRIVATE/USA.iso --tipo usa \
  --png-privado /PRIVATE/A_NUEVO.png --manifiesto-privado /PRIVATE/A_NUEVO.json
# Solo tras verificar ws://127.0.0.1:24192/debugger con subprotocolo debugger.ppsspp.org:
python tools/f2_ppsspp_ws_1204.py --scene TUIKA_HABILIDADES --salida-privada /PRIVATE/A_WS_NUEVO \
  --port 24192 --ge-dump --pid-ppsspp PID_REAL --iso-en-proceso /PRIVATE/USA.iso --tipo-iso usa
# Reinicia PPSSPP con ISO sonda y otra ruta nueva; nunca sobrescribas datos.
python tools/f2_cotejar_capturas_tuika.py --manifest-usa /PRIVATE/A_WS_NUEVO/manifest_PRIVATE.json \
  --manifest-sonda /PRIVATE/B_WS_NUEVO/manifest_PRIVATE.json --iso-usa /PRIVATE/USA.iso \
  --iso-sonda /PRIVATE/TUIKA_sonda_nueva.iso --reporte-privado /PRIVATE/AB_NUEVO.json
python -m unittest discover -s tests -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/preflight_nuevo.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/integrabilidad_nuevo.json
(cd patcher && go test ./...)
git diff --check
~~~

No publicar ni versionar: ISO, BPS, comercial DATA.DAT, EBOOT, FONT.ARC, IMY, imágenes o capturas del juego, GE dumps, RAM ni PPSSPP AppImage/EXE. Generar pruebas en carpetas absolutas PRIVADAS, nombres nuevos sin overwrite. No alterar corpus original ni eventos ni contenido ajeno. Mantener `--event-safe-only`, PR DRAFT, base original y BPS privado experimental. No cambiar blancos/texturas solo por una hipótesis de dibujo.

## 5. Después de F2 (sin saltar prioridades)

**F3:** localizar y traducir inglés restante de intro con identificación exacta de recurso/cadena y pruebas PPSSPP sin eventos rotos.
**F4:** estudiar intérprete MIPS, referencias relativas/absolutas, saltos y tablas de `SCRIPT.DAT` para integrar con seguridad los 4.524 textos aplazados; nunca mover offsets sin modelo validado.
**F5:** prueba exhaustiva de ciudad, combate, pisos, enciclopedia, guardado/carga, HUD, retratos, mapas, inventario, iconos y caracteres españoles.
**F6:** BPS candidato auditado y roundtrip, hashes actualizados de parcheador Go, EXE Windows x64 con payload privado y ejecución real final; documentos de release solo tras pruebas completas.

## 6. ENTREGA OBLIGATORIA DEL NUEVO RELEVO

Al finalizar: (1) pruebas realmente ejecutadas e imágenes X11/WS auténticas frente a tests sintéticos; (2) causa y bytes/código alterados con tests; (3) SHA256 por versión y reportes; (4) actualización de `reports/ESTADO_CONTINUIDAD_PPSSPP.json` y nuevo informe en `docs/` + `reports/`; (5) commits y PR #7 DRAFT sin merge, sin force, sin activos comerciales; (6) DOS checks CI push+PR SUCCESS sobre el MISMO HEAD final o bloquear explícitamente; y (7) **REESCRIBIR COMPLETAMENTE `prompts/SIGUIENTE_TAREA.md` con otro prompt autónomo íntegro y autocontenido, y MOSTRARLO ÍNTEGRO AL USUARIO**. Ese prompt debe volver a exigir recursivamente lo mismo. Si F2 no finaliza, el siguiente prompt debe continuar F2 y señalar una prueba de mayor valor; NO saltar artificialmente a F3.
