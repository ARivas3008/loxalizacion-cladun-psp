# CLADUN ES — SIGUIENTE RELEVO AUTÓNOMO F2: TUIKA de 14 bandas mixtas, 8.625 bordes negros, PPSSPP REAL, 19 glifos y avance F3–F6

Actúa como ingeniero sénior PSP MIPS, PPSSPP oficial v1.20.4 con depurador WebSocket, GPU GE/VRAM, ISO9660/PSPFS/DSARC, IMY paletizado 4bpp/CLUT, CP932 español, compilación segura y QA. TRABAJA de verdad: comprueba recursos aportados, ejecuta auditorías y pruebas, corrige código o parche privado si los resultados lo justifican, actualiza GitHub y publica evidencias. Es inaceptable inventar escenas, capturas, PC MIPS, direcciones RAM/VRAM, comandos GE, hashes, resultados de juego o regresiones. Separa siempre: (A) bytes ISO original auténticos; (B) unit tests sintéticos/CI; (C) gameplay PPSSPP realmente ejecutado.

OBLIGACIÓN RECURSIVA INNEGOCIABLE: Al terminar REESCRIBE COMPLETAMENTE prompts/SIGUIENTE_TAREA.md con un PROMPT NUEVO íntegro, autónomo, autocontenido, con archivos, hashes, comandos, evidencia y pendientes; ese prompt DEBE volver a ordenar a su siguiente relevo la misma regeneración recursiva hasta que F2–F6 estén acreditadas. Muéstralo ÍNTEGRO en tu respuesta; no prometer trabajo en segundo plano.

## 1. ARRANQUE OBLIGATORIO: repositorio, PR, herramientas y reglas

Repo: https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama a modificar: integracion-eventos-segura-20261120
PR #7: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7
Base del PR: revision-manual-dialogos. PR debe seguir ABIERTO, DRAFT, sin MERGE ni FORCE PUSH.

HEAD ANTERIOR a este relevo: 2933bb9e5e08d4d83bef45c1800b1f824c28c407, árbol 9ea5a710d73884d3c945c89bda167c8835c965e9; ambas Actions sobre ese HEAD éxito: push 45066695557 y pull_request 45066837859, cada una con 371 tests Python y Go/integridad/build Windows público sin payload. EL HEAD DE ESTE RELEVO HA CAMBIADO: leer SHA actual y nunca reutilizar el anterior como si siguiera vigente; comprobar las dos Actions del SHA final.

Intentar en checkout verdadero:
    git fetch origin
    git switch integracion-eventos-segura-20261120
    git pull --ff-only
    git status --short
    git rev-parse HEAD
    git rev-parse HEAD^{tree}

En los últimos entornos no existe checkout local auténtico y falla la DNS de github.com; no declarar sincronización ni tests sobre un clon inexistente. El conector GitHub sí funcionó: leer ref+tree+PR, y escribir vía create_blob/create_tree/create_commit/update_ref con expected_sha y force:false. Si falla una actualización, volver a leer HEAD; no sobrescribir modificaciones ajenas.

Leer COMPLETOS AGENTS.md, README.md, prompts/SIGUIENTE_TAREA.md, reports/ESTADO_CONTINUIDAD_PPSSPP.json, reports/RESULTADO_F2_TUIKA_ROTULOS_2026-11-22.json y nuevo docs/F2_TUIKA_CATALOGO_ROTULOS_2026-11-22.md. Asimismo:
- docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md; docs/RESULTADO_F1_PPSSPP_2026-11-21.md; docs/RESULTADO_F2_ATLAS_PPSSPP_2026-11-21.md; docs/F2_ICONOS_TINTA_PPSSPP_2026-11-21.md.
- docs/F2_AUDITORIA_ORIGEN_SOLO_LECTURA_2026-11-21.md; docs/F2_QA_ESTATICA_WS_2026-11-21.md; docs/F2_LECTOR_GE_V6_2026-11-21.md; docs/F2_RELEVO_CAPTURA_RAM_2026-11-21.md; docs/F2_FE_ERRATAS_SHA256_SNAPSHOT_RAM_2026-11-21.md; docs/F2_RELEVO_WS_BREAKPOINT_2026-11-21.md; docs/F2_PREPARACION_DIRECCIONES_GE_2026-11-21.md.
- docs/F2_INVENTARIO_SYSGRA_2026-11-22.md; docs/F2_CATALOGO_GLOBAL_DSARC_2026-11-22.md; docs/F2_DOS_FUENTES_IMY_DECODIFICADAS_2026-11-22.md; docs/F2_SYSGRA_27_IMY_PALETAS_2026-11-22.md; docs/F2_PREVISUALIZACION_PRIVADA_SYSGRA_TEXTO_EN_GRAFICOS_2026-11-22.md; docs/F2_SONDA_MAGENTA_TUIKA_CLUT_PPSSPP_PENDIENTE_2026-11-22.md; docs/F2_TUIKA_CLUT2_CONTADOR_PIXEL_MASK_2026-11-22.md; docs/F2_RELEVO_COTEJO_AB_2026-11-22.md; docs/F2_MAPA_FRANJAS_TUIKA_2026-11-22.md.
- Informes respectivos F1/F2, herramientas tools/f2_*.py, tests/test_f2_*.py, integrador, scripts, fuentes, parcheador Go y workflows .github/workflows.

Prohibido subir a GitHub ISO/BPS, DATA.DAT, EBOOT, IMY, FONT.ARC, PNG comerciales, capturas de emulador, RAM, GE/VRAM, ejecutables de juego, texturas raster o información que reproduzca gráficos comerciales. Código fuente, métricas, hashes y documentación no gráfica sí. Guardar evidencias privadas FUERA de checkout y no sobrescribirlas. No modificar corpus original.

## 2. PUNTOS HISTÓRICOS CONFIABLES, NO INVENTAR NUEVA REGRESIÓN

7z del usuario contiene ISO USA auténtica de 305496064 bytes, SHA-256:
    b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f
ISO F1 canónica histórica: 496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986
BPS USA→F1 histórico: daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd
PPSSPP AppImage Linux oficial v1.20.4: 661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21
Fuente oficial: https://github.com/hrydgard/ppsspp/releases/tag/v1.20.4. NO aceptar SHA truncados.

F1 Opciones históricamente probada en PPSSPP real: Xvfb 1280×720, ventana de escritorio X11 960×544, caja interior 756px / exterior ~764px. IDs 005709: diez espacios ideográficos + siete ASCII; 005710 “Sí”; 005713 “No” y espacio de presentación. F1 cerrada únicamente para Opciones; falta nueva regresión al cambiar fuentes. PNG del framebuffer PSP NO prueba medidas ventana X11.

F2 original: 2721 glifos preservados más 19 CP932 A1–B3 = 2740 en total:
    áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō
FONT.ARC/FONT_00.IMY 512×256, SYSGRA.ARC/FONT.IMY 256×256, NO asumir que cumplen la misma función. Nuevas tintas CLUT15 amarilla RGB(247,247,0), CLUT1 blanca RGB(255,255,255), 100 texels nuevos optativos white_new_ink=True; debe permanecer FALSE por defecto hasta QA real multiescena, sin alterar hash F1 canónica. Vigilar í (bbox x2..4), ÁÉÍÓÚÑÜ (y15), acentos, interlineado, botones L/R □○×△. KITAJIMA_KARI.IMY fue origen de los seis iconos de CONTROLES en pruebas PPSSPP históricas, pero todavía NO hay PC MIPS de dibujado ni cadena causal RAM→GE→VRAM; PC 0x089089C8 y tabla RAM 0x09075000 son búsqueda de TEXTO, NO de iconos.

DATA.DAT: 349 PSPFS; 4 contenedores DSARC: SYS.DAT2 6 PNG; SE.ARC 68 SPS; SYSGRA.ARC 27 IMY; FONT.ARC 7. SCRIPT.DAT: 51705 comandos, 46308 no textuales, 1625 inicios, cero desplazamientos permitidos; 4524 traducciones SCRIPT.DAT APLAZADAS hasta reingeniería de referencias/eventos. Corpus 9237 registros, 9235 localizados y 2 excepciones japonesas documentadas. Preservar --event-safe-only; BPS solo experimental/privado --experimental --event-safe-only hasta QA integral. No fusionar PR.

## 3. RESULTADO AUTÉNTICO DEL RELEVO PRECEDENTE: NO SON 14 FRASES INDEPENDIENTES

El 7z original se extrajo de nuevo en entorno privado mediante libarchive. Se autenticó la ISO por tamaño/SHA y se descomprimió desde SYSGRA.ARC/TUIKA_MES.IMY, PSPFS225/DSARC24. Miembro original SHA:
    c47140753a462cc5b1cc454ee79e0c37b526f06ba5c663b957a91202ebd09127
Índices IMY comprimidos/decodificados SHA:
    3c181786f72008c144a2187d362d289d453b4f00d93fe5f8cb2facc0f23d14d5
Máscara index2 256×256 SHA:
    382ae8d2ffa8908979050b5e83f38ec9967b461bbf9b614dd92775da90e409ba

Medición ORIGINAL real: 14 franjas con 9144 píxeles blancos CLUT2; dentro de sus RECTÁNGULOS hay también 8625 píxeles negros opacos CLUT1 y 11839 transparentes CLUT0. Total de las 14 bounding boxes: 29608 píxeles. Repintar banda, rectángulo, o únicamente CLUT2 SIN estudiar sus bordes es INSEGURO. La relación entre banda y frase es falsa especialmente en franjas con números/iconos. NO SE EDITÓ LA ISO.

NUEVO tools/f2_tuika_rotulos_privado.py autentica ISO y miembro, usa decodificador IMY+unswizzle PSP de los módulos existentes, segmenta CLUT2 con tools/f2_mapa_franjas_tuika.py, cuenta índices 0/1/2 por bounding box, emite JSON sin píxeles y BLOQUEA TODAS las ROI para edición. tests/test_f2_tuika_rotulos_privado.py: 23 tests locales SINTÉTICOS PASS; localmente se usaron shims equivalentes porque Git no estaba disponible, pero el auditor corrió verdaderamente contra la ISO original; verificar tests de módulos originales en ambas Actions NUEVAS. Informe solo de metadatos reports/RESULTADO_F2_TUIKA_ROTULOS_2026-11-22.json; doc docs/F2_TUIKA_CATALOGO_ROTULOS_2026-11-22.md; detalle original privado TUIKA_ROTULOS_original_sha_validado_20261122.json SHA:
    82fc0710130a333ca9cf23a3d4b23638713e1436da9432f7fe6fd7f0d70bbfd3

LECTURA VISUAL MANUAL PROVISIONAL de la textura original (NO OCR/no gameplay):
    00 y002–015: Normal & Warrior LV. con grafía japonesa a la derecha, SIN transcribir toda.
    01 y020–033: Gamble Merchant LV. (glosario pendiente).
    02 y038–051: Angel Guard LV. (glosario pendiente).
    03 y056–069: Demon Magic LV. (glosario pendiente).
    04 y074–087: Hell Dragon LV. (glosario pendiente).
    05 y092–105: Nullified traps! → borrador “¡Trampas anuladas!”.
    06 y110–123: Scattered G! → borrador “¡G dispersos!”, glosario moneda.
    07 y128–141: Replenished HP for all! → borrador “¡HP recuperados para todos!”.
    08 y146–159: Recovered SP! → borrador “¡SP recuperados!”.
    09 y164–177: Attack all enemies on screen! → borrador “¡Ataca a todos los enemigos en pantalla!”.
    10 y181–196: G Star On! + iconos gráficos, función pendiente.
    11 y199–214: símbolos, tecla F y otros controles; NO es una frase.
    12 y218–231: dígitos 0–9; NO se traducen.
    13 y236–249: dígitos 0–9 Y frase No special attack → borrador “Sin ataque especial” SOLO frase.

Todas las propuestas españolas son NO APROBADAS; antes cotejar glosario existente, anchuras, geometría, contexto y traducción natural. No identificar la frase como recurso runtime únicamente por verlo en la ISO. Verificar grafía japonesa fila00 y contenido exacto de controles filas10/11 sin inventar lecturas.

Comando (dos rutas absolutas privadas, informe nuevo):
    python tools/f2_tuika_rotulos_privado.py --iso-usa /PRIVATE/USA.iso --reporte-privado /PRIVATE/ROTULOS_NUEVOS.json

Sonda magenta TUIKA CLUT2 PREVIA para test A/B: original RGB(249,251,249,255) → magenta (255,0,255,255) en SOLO offsets ISO absolutos 114744872, 114744873 y 114744874. ISO privada sonda SHA:
    b199222f740d8d3365d79959de2888caefc2c6c3ed308598ee356db476a465fa
Cotejo íntegro previo: 305496064 bytes, otros 348 PSPFS, otros 26 DSARC y tablas intactos. 9144 píxeles index2 se volverían magenta SI el atlas se dibuja sin cambio de CLUT en PPSSPP. TODAVÍA NO PROBADO EN JUEGO.

## 4. PRIORIDAD CRÍTICA: ARRANCAR PPSSPP AUTÉNTICO Y HACER A/B REAL

En los relevos recientes PPSSPP AppImage oficial no estaba instalado y tanto clone como descarga GitHub fallaron (DNS Could not resolve host: github.com). Intentar localizar AppImage v1.20.4 legítimo, comprobar SHA completo ANTES de ejecutar, comprobar arquitectura Linux x86_64 y funcionalidad X11/Xvfb/SDL. No reemplazarlo por un emulador diferente etiquetado falsamente 1.20.4. Si no hay binario, dejar bloqueo explícito y avanzar solo en auditorías útiles, nunca imágenes fabricadas como evidencia.

Con PPSSPP REAL y original+sonda privados, lanzar dos sesiones SEPARADAS, acreditando ruta y hash del binario/ISO utilizada. Se requieren, para la misma escena TUIKA habilidades/ataque/controles y estado equivalente:
- DOS PNG nativos reales del debugger por ISO, timestamps/ticks y manifiestos privados; además capturas reales de ventana X11 si se mide F1. Hash SHA de cada PNG y reporte.
- Controles positivos/negativos de aparición de las bandas, especialmente renglones 5–9 y 13; si no sale magenta en una escena, NO afirmar que TUIKA no se usa.
- Revisar manualmente alineación de fotogramas, ROI, emulación y shaders/paleta; candidato magenta NO demuestra cadena causal MIPS/GE/VRAM.
- Rastrear explícitamente fuente de TUIKA_MES, KITAJIMA_KARI, SYS1, MAHO_ST, las dos fuentes FONT y PALETE_0–3, verificando diferencias mediante sondas AISLADAS por recurso.

Protocol debugger v1.20.4 ws://127.0.0.1:24192/debugger, subprotocolo debugger.ppsspp.org. Comprobar version, game.status y cpu.status, validar pausa CPU previa a gpu.buffer.screenshot. Métodos válidos memory.read, memory.disasm, memory.breakpoint.list/add/remove, cpu.getAllRegs, cpu.stepping/resume, gpu.buffer.screenshot, gpu.record.dump; NO inventar cpu.breakpoint.hit o gpu.displaylist.disasm. Rastrear descompresión/copias a RAM y texture/CLUT binding, GE TEXTADDR/PRIM/TRANSFERSTART y VRAM. Usar watchpoint SOLO con dirección RAM auténtica y respetar breakpoints ajenos, nunca usar offset ISO como dirección PSP RAM.

Comandos orientativos con rutas privadas nuevas:
    python tools/f2_probe_tuika_palette_privado.py --iso-usa /PRIVATE/USA.iso --salida-iso-privada /PRIVATE/TUIKA_magenta_NUEVA.iso --reporte-privado /PRIVATE/sonda_nueva.json
    python tools/f2_ppsspp_ws_1204.py --scene TUIKA_HABILIDADES --salida-privada /PRIVATE/ab_original_nuevo --port 24192 --ge-dump
    # Reiniciar PPSSPP con ISO sonda, reconstruir misma escena manualmente
    python tools/f2_ppsspp_ws_1204.py --scene TUIKA_HABILIDADES --salida-privada /PRIVATE/ab_probe_nuevo --port 24192 --ge-dump
    python tools/f2_cotejar_capturas_tuika.py --manifest-usa /PRIVATE/ab_original_nuevo/manifest_PRIVATE.json --manifest-sonda /PRIVATE/ab_probe_nuevo/manifest_PRIVATE.json --iso-usa /PRIVATE/USA.iso --iso-sonda /PRIVATE/TUIKA_magenta_NUEVA.iso --reporte-privado /PRIVATE/reporte_AB_nuevo.json
    python tools/f2_ge_dump_1204.py --entrada-privada /PRIVATE/ab_original_nuevo/TUIKA_HABILIDADES_GE_PRIVATE.dump --reporte-privado /PRIVATE/ge_nuevo.json
    python tools/f2_ram_provenance_1204.py --iso-usa /PRIVATE/USA.iso --salida-privada /PRIVATE/ram_nuevo --solo-origen

El comparador A/B SOLO autentica imágenes/ISO en disco, NO que PPSSPP haya cargado efectivamente esas ISOs ni que los frames estén alineados. No declarar runtime_loaded_iso_identity_proven=true sin evidencia independiente. No subir PNG, dumps o ISOs a GitHub.

## 5. QA DE F2: 19 GLIFOS Y REGRESIÓN F1

Con ISO F1 canónica autenticada (reconstruir PRIVADAMENTE si no está presente) demostrar los 19 caracteres áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō en ayudas, tutorial, menús, diálogo, HUD y combate. Capturas PPSSPP auténticas, ROI correctas, CLUT, tintas, bbox, recortes e interlineado; probar botones L/R □○×△ y que no haya distorsión de retratos, iconos, tiles y demás assets. Diagnósticos privados tools/generar_probe_f2_glifos.py y tools/generar_probe_f2_tinta.py; no cambiar corpus canon.

Regresión F1 Opciones PPSSPP real ventana de escritorio X11 960×544 con Xvfb 1280×720, scrot, 756px interior/~764px exterior, Sí/No, música/configuración, navegación; NO medirlo con framebuffer PSP como si fuese la ventana. white_new_ink=False hasta superar QA multicontesto y regresión completa.

## 6. INTEGRIDAD, TESTS, CI Y ENTREGA GITHUB

Con un checkout REAL y binarios privados presentes ejecutar cuando corresponda:
    python -m unittest discover -s tests -v
    python tools/verificar_integridad.py --raiz .
    python tools/verificar_borrador_es.py
    python tools/auditar_preinsercion_es.py --reporte /tmp/preflight_nuevo.json
    python tools/reportar_integrabilidad_es.py --reporte /tmp/integrabilidad_nuevo.json
    python tools/f2_auditar_origen_iconos.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/iconos_nuevo.json
    python tools/f2_qa_raster_19.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/glifos_nuevo.json
    python tools/f2_auditar_27_imy_sysgra.py --iso-usa /PRIVATE/USA.iso --reporte /tmp/27_imy_nuevo.json
    python tools/f2_mapa_franjas_tuika.py --iso-usa /PRIVATE/USA.iso --iso-sonda /PRIVATE/TUIKA_magenta_NUEVA.iso --reporte-privado /PRIVATE/bandas_nuevo.json
    python tools/f2_tuika_rotulos_privado.py --iso-usa /PRIVATE/USA.iso --reporte-privado /PRIVATE/rotulos_nuevo.json
    (cd patcher && go test ./...)
    git diff --check

Si falta checkout local auténtico, NO afirmar ejecución local de toda la suite: verificar los logs de AMBAS GitHub Actions para HEAD FINAL (push y pull_request), nombres de jobs, pruebas Python, integridad, Go y build Windows sin payload. Reportar el recuento y distinción CI vs PPSSPP. Evitar editar corpus, traducciones o scripts sin compuertas de seguridad.

## 7. F3–F6 SIGUIENTES, NO DECLARAR PORCENTAJES ARBITRARIOS

F2 sigue ABIERTA hasta conectar MIPS→RAM→GE→VRAM de iconos/fuentes/uso de TUIKA; 19 glifos en todos los contextos pertinentes, CLUT y F1 real X11 sin regresiones. Las 14 bandas TUIKA NO están aprobadas para repintar por ahora.

F3: resolver introducción aún en inglés; rastrear procedencia (no suponer SCRIPT ni gráficos) y traducir con pruebas reales y QA. F4: analizar e integrar las 4524 sustituciones SCRIPT.DAT aplazadas con relocación, saltos y eventos seguros, sin cambiar accidentalmente 46308 comandos no textuales ni los 1625 arranques. F5: QA completa de diálogos, historia, combate, HUD, inventario, retratos, enciclopedia, assets, guardado/carga, errores y todas las fases. F6: BPS español definitivo verificable con SHA/source/target, aplicador EXE Windows probado end-to-end, instrucciones y auditoría de offsets/recursos, solo después de F2–F5 demostradas. No fusionar PR #7 sin autorización.

## 8. CIERRE RECURSIVO OBLIGATORIO

Antes de terminar: (1) documentar lo que se ejecutó realmente y lo que quedó bloqueado; (2) actualizar reports/ESTADO_CONTINUIDAD_PPSSPP.json y un informe de metadatos, protegiendo datos comerciales; (3) commit seguro sobre integracion-eventos-segura-20261120 mediante expected_sha, sin force ni merge; (4) verificar PR #7 DRAFT y DOS Actions SUCCESS sobre SHA FINAL, no SHA anterior; (5) REESCRIBIR COMPLETAMENTE prompts/SIGUIENTE_TAREA.md con NUEVO PROMPT COMPLETO, autónomo y actualizado, y MOSTRARLO ÍNTEGRO; (6) el nuevo prompt DEBE CONTENER DE NUEVO ESTA MISMA OBLIGACIÓN RECURSIVA. Repetir hasta F2–F6 autentificadas. Nunca inventar evidencia PPSSPP para cerrar la fase.
