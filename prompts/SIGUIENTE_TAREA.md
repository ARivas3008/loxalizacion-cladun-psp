# CLADUN ES — RELEVO F2 AUTÓNOMO: PPSSPP 1.20.4 REAL, identidad ISO/PID/WS, TUIKA A/B, 19 glifos y F3–F6

Actúa como ingeniero sénior PSP MIPS, PPSSPP WebSocket v1.20.4, GPU GE/VRAM, ISO9660/PSPFS/DSARC, IMY 4bpp/CLUT, fuentes CP932 y localización española. **EJECUTA** diagnósticos y pruebas auténticas, modifica código cuando proceda, protege los archivos comerciales y actualiza GitHub. No inventar capturas, PCs MIPS, direcciones RAM/VRAM, comandos GE, archivos, hashes, resultados ni emulación. Separa (A) lectura de ISO original real; (B) pruebas sintéticas locales/CI; (C) ejecución real de videojuego. No afirmar que C existe porque A/B funcionó.

**OBLIGACIÓN RECURSIVA OBLIGATORIA F2–F6:** Al terminar REESCRIBE COMPLETAMENTE `prompts/SIGUIENTE_TAREA.md` con **OTRO NUEVO** prompt autónomo íntegro y autocontenido, que vuelva a exigir la misma reescritura recursiva y dé archivos, hashes, procesos, pruebas, riesgos y fases siguientes. **MUÉSTRALO ÍNTEGRO AL USUARIO**. No trabajo en segundo plano ni promesas de ejecución diferida.

## 1. GitHub — autenticación inicial y reglas

Repo https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama `integracion-eventos-segura-20261120`.
PR #7 https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7, base `revision-manual-dialogos`. Mantener abierto, **DRAFT**, sin merge ni force push.

HEAD anterior a este nuevo relevo: `948e9307ca0adfee613f73da40d0d70604a73b89`; GitHub CI push `45172386614` y PR `45172398914` **SUCCESS** exactamente sobre ese commit, 426 tests Python sin fallos, integridad/Go/compilación Windows sin payload. **Este SHA dejará de ser HEAD después del presente commit**; leer nuevamente ref, tree, PR y ambos CI del HEAD final, no suponer que los anteriores son actuales.

Intentar checkout REAL, nunca simular sincronización si DNS GitHub falla:

    git fetch origin
    git switch integracion-eventos-segura-20261120
    git pull --ff-only
    git status --short
    git rev-parse HEAD
    git rev-parse HEAD^{tree}

Último entorno sin checkout local: `git ls-remote` falló por `Could not resolve host: github.com`. Conector GitHub sí permite operar con `fetch_file`, `create_blob`, `create_tree`, `create_commit`, `update_ref` con `expected_sha`/`force:false`. Revalidar ref antes de escribir.

Leer COMPLETOS primero: `AGENTS.md`, `README.md`, `prompts/SIGUIENTE_TAREA.md`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json` y NEW:
- `docs/F2_PROCEDENCIA_ISO_PROCESO_PPSSPP_2026-11-23.md`
- `reports/RESULTADO_F2_PROCEDENCIA_ISO_PROCFS_2026-11-23.json`
- `tools/f2_iso_proceso_ppsspp.py`
- `tools/f2_ppsspp_ws_1204.py` (opciones nuevas)
- `tools/f2_cotejar_capturas_tuika.py` (testigo opcional)
- `tests/test_f2_iso_proceso_ppsspp.py`
- `tests/test_f2_procfs_capture_integration.py`
- `tests/test_f2_procfs_ab_witness_validation.py`

También todos los documentos históricos del proyecto necesarios:
- `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`; `docs/RESULTADO_F1_PPSSPP_2026-11-21.md`; `docs/RESULTADO_F2_ATLAS_PPSSPP_2026-11-21.md`; `docs/F2_ICONOS_TINTA_PPSSPP_2026-11-21.md`.
- `docs/F2_AUDITORIA_ORIGEN_SOLO_LECTURA_2026-11-21.md`, `docs/F2_QA_ESTATICA_WS_2026-11-21.md`, `docs/F2_LECTOR_GE_V6_2026-11-21.md`, `docs/F2_RELEVO_CAPTURA_RAM_2026-11-21.md`, `docs/F2_FE_ERRATAS_SHA256_SNAPSHOT_RAM_2026-11-21.md`, `docs/F2_RELEVO_WS_BREAKPOINT_2026-11-21.md`, `docs/F2_PREPARACION_DIRECCIONES_GE_2026-11-21.md`.
- `docs/F2_INVENTARIO_SYSGRA_2026-11-22.md`, `docs/F2_CATALOGO_GLOBAL_DSARC_2026-11-22.md`, `docs/F2_DOS_FUENTES_IMY_DECODIFICADAS_2026-11-22.md`, `docs/F2_SYSGRA_27_IMY_PALETAS_2026-11-22.md`, `docs/F2_PREVISUALIZACION_PRIVADA_SYSGRA_TEXTO_EN_GRAFICOS_2026-11-22.md`, `docs/F2_SONDA_MAGENTA_TUIKA_CLUT_PPSSPP_PENDIENTE_2026-11-22.md`, `docs/F2_TUIKA_CLUT2_CONTADOR_PIXEL_MASK_2026-11-22.md`, `docs/F2_RELEVO_COTEJO_AB_2026-11-22.md`, `docs/F2_MAPA_FRANJAS_TUIKA_2026-11-22.md`, `docs/F2_TUIKA_CATALOGO_ROTULOS_2026-11-22.md` y `docs/F2_TUIKA_SUBREGIONES_PROTEGIDAS_2026-11-23.md`.
- Sus informes JSON bajo `reports/` y herramientas/tests relacionados. Revisar integrador, parcheador Go, .github/workflows.

PROHIBIDO publicar o commitear ISO, BPS, DATA.DAT, EBOOT, IMY, FONT.ARC, PNG reales de juego, PMF, RAM, capturas PPSSPP, dumps GE/VRAM, ejecutables o cualquier arte comercial. Solo código, tests sintéticos, métricas, hashes, documentos. Evidencia privada siempre fuera del checkout, rutas absolutas nuevas, sin overwrite. No cambiar corpus original ni ramas base.

## 2. Entradas genuinas comprobadas y F1/F2 históricas

7z privado aportado por usuario, ISO USA original **305.496.064 bytes**, SHA256 EXACTO (64 dígitos):
    b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f

F1 ISO canónica histórica SHA:
    496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986
BPS USA→F1 histórico:
    daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd

PPSSPP AppImage Linux oficial **v1.20.4** SHA histórico:
    661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21
Activo remoto OFICIAL confirmado por GitHub Release API: `PPSSPP-v1.20.4-anylinux-x86_64.AppImage` tamaño **50.689.748 bytes**, https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4. **No se descargó en el entorno precedente**: DNS de GitHub falló y `container.download` falló. Verificar SHA real antes de ejecutar; no confundir metadatos oficiales del asset con disponer del binario.

F1 Opciones **aprobada históricamente PPSSPP real**, NO regresión nueva: Xvfb 1280×720, ventana X11 960×544, caja interior 756px/exterior ≈764px. IDs 005709 diez espacios ideográficos + siete ASCII; 005710 «Sí»; 005713 «No» más espacio. El framebuffer PSP NO mide el ancho de ventana X11. Nuevo QA pendiente.

F2 conserva **2.721 glifos originales +19 nuevos =2740** CP932:
    áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō
FONT.ARC/FONT_00.IMY 512×256 ≠ SYSGRA.ARC/FONT.IMY 256×256; no asumir que son la misma fuente. Nueva tinta index15 amarilla RGB(247,247,0), index1 blanca RGB(255,255,255). La opción `white_new_ink=True` alteraría 100 texels de nueva tinta; **mantener FALSE por defecto**, no cambiar F1 sin PPSSPP multicontesto. Vigilar í x2..4 y mayúsculas que llegan hasta y15, ancho/interlineado y símbolos L/R □○×△. KITAJIMA_KARI.IMY causó seis iconos de CONTROLES en PPSSPP real histórico; otros contextos y cadena MIPS→RAM→GE→VRAM NO probados. PC MIPS 0x089089C8 y RAM 0x09075000 son búsqueda de glifos de TEXTO, no PC de iconos.

DATA.DAT: 349 PSPFS; cuatro DSARC: SYS.DAT2 6 PNG; SE.ARC 68 SPS; SYSGRA.ARC 27 IMY; FONT.ARC 7. SCRIPT.DAT 51.705 comandos, 46.308 no textuales, 1.625 inicios y 4.524 traducciones pendientes, no mover offsets ni saltos. Corpus original 9.237 registros, 9.235 localizados + 2 excepciones japonesas documentadas. Mantener `--event-safe-only`; integración BPS solo experimental/privada `--experimental --event-safe-only` hasta QA integral.

## 3. TUIKA real: 14 franjas NO equivalen a 14 cadenas

Recurso original privado SYSGRA.ARC/TUIKA_MES.IMY, PSPFS índice 225/DSARC índice 24, SHA:
    c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127
Índices IMY decodificados SHA:
    3c181786f72008c144a2187d362d289d453b4f00d93fe5f8cb2facc0f23d14d5
Índices lineales 256x256 (un byte por index4bpp) SHA:
    a3da2c0d728288c2842b0d9164f4dd220c4713eaa19b3559ef7105f837f8106d
Máscara index2 CLUT de 9.144 píxeles SHA:
    382ae8d2ffa8908979050b5e83f38ec9967b461bbf9b614dd92775da90e409ba

Del atlas original se identificaron 14 franjas, algunas con rótulos ingleses como «Nullified traps!», «Scattered G!», «Recovered SP!», «Attack all enemies on screen!» y «No special attack». Las bandas 0/10/11/12/13 incluyen japoneses, controles y números. Propuestas de traducción solo borradores y NO insertadas. En las bounding boxes index2 había también 8.625 píxeles index1 negro y 11.839 transparentes; no repintar franjas completas ni solo CLUT2.

Desde 23/11: herramientas `tools/f2_tuika_rotulos_privado.py` y `tools/f2_tuika_proteger_subregiones.py`. Se autenticaron **7 subregiones** y **3 huecos CLUT0 transparentes**, 9.738 posiciones protegidas:
- Banda10 rótulo: x4–79 y181–196; iconos x92–115, separados por **x80–91** totalmente transparentes (192px).
- Banda12 dígitos: x1–138 y218–231, bloqueados.
- Banda13 dígitos: x1–108 y236–249; mensaje «No special attack»: x112–248, separados por **x109–111** totalmente transparentes (42px). Entre palabras x190–199 índice0 (140px).
- Banda0 mixta japonés/inglés y banda11 controles BLOQUEADAS.
- `guard_candidate` deniega TODAS las modificaciones de píxeles por defecto, incluso si existe una propuesta española. Los SHA de los recortes se documentan en informes estáticos; no existe ROI aprobada hasta validar en PPSSPP.
Sonda TUIKA CLUT2 magenta previa tiene ISO SHA:
    b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa
Solo 3 bytes RGB absolutos de ISO cambiaron en offsets 114744872–114744874; 348/348 PSPFS vecinos, 26/26 DSARC vecinos y tablas intactos. Los 9.144 píxeles se colorearían en lectura directa, NO está probado que aparezcan en juego.

## 4. NUEVO RELEVO 23/11: procedencia ISO→PID→capturas sin inventar identidad cargada

Se verificó nuevamente la ISO USA auténtica (stream SHA completo 305496064 bytes). No había PPSSPP AppImage oficial; sin capturas reales, dumps GE o nueva regresión F1. La debilidad del antiguo A/B era comprobar solo ISOs en DISCO, sin vincularlas a un proceso. Se añadieron:

- `tools/f2_iso_proceso_ppsspp.py`: valida ISO por SHA/tamaño, consulta **solo lectura** Linux `/proc/<pid>/stat` (starttime con paréntesis en comm), `cmdline` (argumento EXACTO, no subcadena), `exe` (indicio nominal) y descriptores `fd` (st_dev, st_ino, st_size iguales a ISO). Compara muestras antes/después sin admitir PID reciclado ni sustitución del inodo. No publica argv/rutas privadas, ni contenido de ISO.
- Integración OPTATIVA en `tools/f2_ppsspp_ws_1204.py` con `--pid-ppsspp PID --iso-en-proceso /PRIVATE/ISO.iso --tipo-iso usa|sonda`. El capturador PPSSPP recibe dos PNG por WS solo con emulador auténtico; muestrea procfs antes y después, revalida SHA ISO después, exige PID nominal PPSSPP/AppRun y mantiene marcadores explícitos `runtime_loaded_iso_identity_proven=false` y `websocket_server_pid_correlated=false`.
- `tools/f2_cotejar_capturas_tuika.py` acepta el testigo opcional en ambos manifiestos, comprueba rol/SHA declarados y no eleva una declaración de FD a evidencia de juego cargado.
- Nuevas suites: 30 tests procfs SINTÉTICOS locales PASS; 10 tests sintéticos de integración captura y 9 del cotejador de manifestos para validar en CI. No confundir test de Python con PPSSPP real.
- Reportes: `docs/F2_PROCEDENCIA_ISO_PROCESO_PPSSPP_2026-11-23.md` y `reports/RESULTADO_F2_PROCEDENCIA_ISO_PROCFS_2026-11-23.json`. Informe privado sin ruta comercial SHA `faaadcabef4676eee68af90728f09f3de28cb25e4edaff7a2250833a992ba145`.

**Interpretación rigurosa**: FD abierto al mismo inodo prueba **acceso del proceso** a un archivo, NO que ese sea el juego que se renderiza, ni que ese PID sea el WS server, ni el origen GE/VRAM; FD ausente deja resultado desconocido. Incluso un testigo positivo aún exige control de sesión e identificación funcional.

## 5. PRIORIDAD 1 del siguiente relevo: PPSSPP REAL y A/B verificable

Obtener por medio legítimo PPSSPP AppImage oficial v1.20.4 x86_64 de la URL del release, comprobar SHA (661c...eba21) y tamaño 50689748 bytes **antes de ejecutar**. El último contenedor no pudo descargar; si vuelve a fallar, declarar bloqueo y NO fabricar fotogramas/GE.

Con PPSSPP auténtico y CPU capaz de avanzar, iniciar una sesión USA original, entrar a escenas donde realmente aparezcan mensajes de habilidades, combate y ayudas; confirmar PID proceso, puerto local ws://127.0.0.1:24192/debugger y protocolo debugger.ppsspp.org. Verificar version, game.status, cpu.status. Para grabar próximo frame GE, CPU corriendo; para screenshot gpu.buffer.screenshot, CPU o GPU detenida. Mantener pausas ajenas. Separar ventana X11 del framebuffer PSP.

Comandos para dos capturas reales por ISO (carpetas privadas distintas, nuevas, con PID real; nunca publicar arte):
    sha256sum /PRIVATE/PPSSPP-v1.20.4-anylinux-x86_64.AppImage
    python tools/f2_ppsspp_ws_1204.py --scene TUIKA_HABILIDADES --salida-privada /PRIVATE/A_NUEVA --port 24192 --ge-dump --pid-ppsspp PID_ORIGINAL --iso-en-proceso /PRIVATE/USA.iso --tipo-iso usa

    # Reiniciar PPSSPP en ISO TUIKA magenta, restaurar mismo estado:
    python tools/f2_ppsspp_ws_1204.py --scene TUIKA_HABILIDADES --salida-privada /PRIVATE/B_NUEVA --port 24192 --ge-dump --pid-ppsspp PID_SONDA --iso-en-proceso /PRIVATE/TUIKA_magenta.iso --tipo-iso sonda

    python tools/f2_cotejar_capturas_tuika.py --manifest-usa /PRIVATE/A_NUEVA/manifest_PRIVATE.json --manifest-sonda /PRIVATE/B_NUEVA/manifest_PRIVATE.json --iso-usa /PRIVATE/USA.iso --iso-sonda /PRIVATE/TUIKA_magenta.iso --reporte-privado /PRIVATE/AB_NUEVO.json
    python tools/f2_ge_dump_1204.py --entrada-privada /PRIVATE/A_NUEVA/TUIKA_HABILIDADES_GE_PRIVATE.dump --reporte-privado /PRIVATE/GE_NUEVO.json
    python tools/f2_ram_provenance_1204.py --iso-usa /PRIVATE/USA.iso --salida-privada /PRIVATE/RAM_NUEVO --solo-origen

El método extra:
    python tools/f2_iso_proceso_ppsspp.py --pid PID_REAL --iso-privada /PRIVATE/USA.iso --tipo usa
no guarda PNG, solo instantánea de un FD; NO es procedencia funcional suficiente. La etiqueta TUIKA_HABILIDADES no prueba que esa escena se visualizó.

Asegurar controles positivo/negativo de magenta, misma escena, ticks y alineación manual. Cero magenta no descarta atlas; magenta no prueba cadena MIPS. Rastrear lectura IMY→decodificación RAM→TEXADDR/CLUT/PRIM/TRANSFERSTART GE→VRAM y píxel visible; watchpoint solo sobre RAM real, no sobre offset ISO (por ejemplo 0x06D68C00). No inventar cpu.breakpoint.hit ni gpu.displaylist.disasm; usar métodos PPSSPP oficiales memory.read, memory.disasm, memory.breakpoint.list/add/remove, cpu.getAllRegs, cpu.stepping/resume, gpu.buffer.screenshot y gpu.record.dump.

## 6. QA F2, regresión F1, seguridad scripts

19 glifos españoles áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō en Controles, ayuda, diálogo, tutorial, HUD, combate, menús. Verificar CLUT amarillo/blanco, ancho, altura, signos, iconos y posibles recortes; dos fuentes distintas, no asumir contexto por su nombre. Mantener `white_new_ink=False` hasta validación PPSSPP multicontesto. Generar sondas privadas con `tools/generar_probe_f2_glifos.py` y `tools/generar_probe_f2_tinta.py`, no alterando 9237 registros.

Regresión real de F1 Opciones: Xvfb 1280x720, ventana **X11 960×544**, scrot real, interior 756px/exterior≈764px, IDs 005709/005710 Sí/005713 No; navigation, música/configuración. Nunca presentar framebuffer PSP como captura de ventana X11.

Integridad: fuente original inalterada, 349 PSPFS, DSARC sin cambios no autorizados, SCRIPT.DAT 51705 comandos, 46308 no textuales, 1625 comienzos, 4524 traducciones diferidas. Nunca retirar `--event-safe-only`; BPS solo privado experimental `--experimental --event-safe-only` con hashes y roundtrip; PR DRAFT.

## 7. Pruebas, CI y planes F3–F6

En checkout real ejecutar:
    python -m unittest discover -s tests -v
    python tools/verificar_integridad.py --raiz .
    python tools/verificar_borrador_es.py
    python tools/auditar_preinsercion_es.py --reporte /tmp/preflight_nuevo.json
    python tools/reportar_integrabilidad_es.py --reporte /tmp/integrabilidad_nuevo.json
    python tools/f2_auditar_origen_iconos.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/iconos_nuevo.json
    python tools/f2_qa_raster_19.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/19_nuevo.json
    python tools/f2_tuika_proteger_subregiones.py --iso-usa /PRIVATE/USA.iso --reporte-privado /PRIVATE/subregiones_nuevo.json
    (cd patcher && go test ./...)
    git diff --check

Sin checkout local, leer logs CI de DOS GitHub Actions sobre el HEAD final — push y pull_request — incluyendo recuentos Python, QA integridad, Go y build Windows sin payload. NO atribuir CI a gameplay. Comprobar que no se subieron imágenes/ISOs/BPS ni se alteró corpus, parche canónico o scripts.

F2 ABIERTA hasta cadena funcional MIPS/RAM/GE/VRAM y 19 glifos, TUIKA y F1 en PPSSPP. F3 INTRO en inglés: localizar fuente y traducir con QA real sin suponer el formato. F4: 4524 cambios SCRIPT.DAT con relocación/saltos/referencias seguros sin alterar comandos; F5: recorrer historia, combate, HUD, inventario, retratos, enciclopedia, guardado/carga; F6: BPS final y EXE Windows aplicado y probado end-to-end, hashes/integridad y distribución segura. No declarar 100% ni fusionar PR #7.

## 8. CIERRE RECURSIVO INNEGOCIABLE

Al final de ESTA tarea (1) ejecutar trabajo auténtico, reportar bloqueos, distinguir bytes ISO vs sintéticos vs PPSSPP; (2) escribir código/tests/docs nuevos si corresponde, publicar SOLO métricas seguras; (3) actualizar reports/ESTADO_CONTINUIDAD_PPSSPP.json con hechos y límites, y generar informe; (4) commit branch con update_ref expected_sha, sin force, PR #7 DRAFT sin fusionar; (5) verificar DOS CI SUCCESS del mismo HEAD final; (6) **REESCRIBIR COMPLETAMENTE prompts/SIGUIENTE_TAREA.md con otro NUEVO prompt autónomo e íntegro, con la MISMA OBLIGACIÓN RECURSIVA para el siguiente relevo, y MOSTRARLO ÍNTEGRO al usuario**. Repetir hasta F2–F6 auténticamente completadas.
