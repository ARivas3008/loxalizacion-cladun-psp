# CLADUN ES — NUEVO RELEVO AUTÓNOMO F3-R5: SEMÁNTICA REAL DE EVENTOS, PRÓLOGO Y F2 TUIKA; F4–F6 ABIERTAS

**Fecha de corte: 23/11/2026.** Actúa como ingeniero sénior PSP/MIPS, PPSSPP oficial 1.20.4, WebSocket, GPU GE/VRAM, ISO9660/PSPFS/DSARC, IMY/CLUT y fuentes CP932 españolas. **EJECUTA** diagnósticos, código, pruebas y correcciones justificadas; no te limites a un plan. Divide pruebas en (A) ISO original auténtica y análisis binario, (B) tests sintéticos/CI de código, (C) ejecución GENUINA de PPSSPP. Nunca inventes capturas, PCs, hashes, direcciones o resultados.

## 0. REGENERACIÓN RECURSIVA INNEGOCIABLE

**AL FINAL SUSTITUYE ÍNTEGRAMENTE prompts/SIGUIENTE_TAREA.md POR OTRO PROMPT NUEVO, COMPLETO Y AUTÓNOMO**, con estado/HEAD/PR/CI verificados, recursos, hashes, comandos, avances y bloqueos. **MUÉSTRALO ÍNTEGRO AL USUARIO. EL NUEVO PROMPT EXIGIRÁ LA MISMA REGENERACIÓN RECURSIVA EN EL SIGUIENTE RELEVO** hasta cerrar auténticamente F2–F6, aunque continúen bloqueadas. No prometas trabajo asíncrono.

## 1. GitHub y documentos canónicos

Repo: https://github.com/ARivas3008/loxalizacion-cladun-psp
Rama: integracion-eventos-segura-20261120
PR #7: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7
Base: revision-manual-dialogos

**Conservar PR OPEN/DRAFT, sin merge, sin force push, sin alterar corpus original ni rama base.** El HEAD al comienzo de F3-R4 fue dc76e1f020393c12060a5403866ca24245dd2ae9; los anteriores 70558c570ee6fd4534e5f30e9bf7dbc9a9b1e505 y cffd12b0550ac47f92980ebeb195fe1afabce9ab son HISTÓRICOS. No asumir que ninguno sigue siendo HEAD.

Con checkout real:

~~~bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
git status --short
git rev-parse HEAD
~~~

Si la terminal no resuelve github.com, NO fingir clonación: GitHub conector fetch_file y Git Data create_blob/create_tree/create_commit/update_ref con expected_sha real y force:false. Revalidar branch HEAD y árbol antes de cualquier actualización; conservar progresos simultáneos de F2.

Leer completos: AGENTS.md, README.md, prompts/SIGUIENTE_TAREA.md, reports/ESTADO_CONTINUIDAD_PPSSPP.json. Para F3: docs/F3_CAMPOS_ALINEACION_Y_EBOOT_2026-11-23.md, reports/RESULTADO_F3_CAMPOS_ALINEACION_2026-11-23.json, tools/f3_campos_alineacion.py, tests/test_f3_campos_alineacion.py, tools/f3_referencias_riesgo.py, tests/test_f3_referencias_riesgo.py, tools/f3_auditar_intro.py, tools/f3_anime_topologia.py, tools/f3_anime_imy_estructuras.py, tools/script_event_guard.py, tools/integrar_parche_seguro.py, tools/charset_es.py, docs/F3_PROLOGO_ANIME000_DEPENDENCIA_PPSSPP_REAL_2026-11-23.md y docs/F3_INTRO_INTENTO_PPSSPP_Y_ORIGEN_SCRIPTS_2026-11-23.md. Para F2: docs/F2_COTEJO_X11_AB_CON_GUARDAS_2026-11-23.md, docs/F2_IMPACTO_GLOBAL_CLUT2_REAL_2026-11-23.md, docs/F2_GE_ONLY_WEB_SOCKET_SIN_FRAMEBUFFER_2026-11-23.md, docs/F2_MAPA_JUGABLE_GE_X11_F1_2026-11-23.md, tools/f2_cotejar_x11_tuika.py, tools/f2_ppsspp_ws_1204.py, tools/f2_ruta_ws_liberacion_segura.py, tools/f2_ge_dump_1204.py, tools/f2_ws_procedencia_ppsspp.py y tests.

## 2. Binarios originales, hashes, privacidad

ISO USA aportada: **305496064 bytes** SHA256 **b73b263fce863e51a0e27d0d11d6bde2886e439a18e2bb186d497619a1b79f**. ISO F1 española canónica histórica: **306456576 bytes** SHA256 **496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986**. BPS F1 histórico SHA256 **daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd**. PPSSPP oficial 1.20.4 AppImage Linux x86_64 **50689748 bytes**, SHA256 **661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21**, URL https://github.com/hrydgard/ppsspp/releases/download/v1.20.4/PPSSPP-v1.20.4-anylinux-x86_64.AppImage. No ejecutar sin hash autenticado.

**NUNCA versionar ni distribuir ISO, BPS, DATA.DAT, PSP EBOOT, fuentes, IMY, fondos, sprites, capturas/PNG de PPSSPP, vídeos o dumps RAM/GE/VRAM.** Solo código propio, tests sintéticos, informes agregados de métricas y documentos. La ISO y sondas deben permanecer fuera del checkout; original inmutable.

## 3. Avance F3-R4 A/B: falso indicador numérico identificado

Se leyó la ISO USA REAL autenticada. DATA.DAT→PSPFS índice 231 SCRIPT.SDT→SCRIPT.DAT SHA256 **c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358**, SCRIPT.TBL SHA256 **f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37**. Se verificaron **1.625 scripts / 51.705 comandos / 46.308 no textuales**, demo1001 siete bloques/878 comandos.

El escaneo anterior F3-R3 inspeccionó ventanas u32 deslizantes y encontró 2.883 coincidencias con offsets absolutos. **1.439** de ellas para opcode 0x02 byte +5 se debían a la REPETICIÓN DE UN SOLO VALOR, **8192**, y NO representan 1.439 saltos. Los 2.039 comandos opcode 0x02 tienen payload de 18 B compatible, únicamente a modo de hipótesis, con u16 seguido de cuatro u32 en +2/+6/+10/+14. En todos los 2.039: **u32(+5) = 256 × u32(+6)**. Campos +2 y +6: cero matches absolutos. Campo +14: 459 matches, de los cuales 442 repiten un solo valor. No atribuir semántica de salto al opcode por estos datos.

El nuevo auditor tools/f3_campos_alineacion.py solo examina campos HIPOTÉTICOS de seis opcodes (0x01, 0x02, 0x07, 0x0A, 0xFB, 0xFC). Resultados: 803 matches absolutos, 729 en otros bloques, 1.254 relativos, 3.253 de ID de script y 15 de inicio de script; para demo1001, 16 / 16 / 21 / 7 / 1. **NO COMPARAR DIRECTAMENTE 803 vs 2883 COMO REDUCCIÓN**, porque el nuevo alcance cubre solo seis opcodes. Los demás no fueron liberados. MIPS no verificado; las 85 entradas permanecen BLOQUEADAS.

Hallazgo adicional de ISO9660: BOOT.BIN **2158521 B**, SHA256 **d2240653adc6119df174c4a3cb8451381934f6898ef2bff8d6ffe00763aebdf2** son todos ceros; EBOOT.BIN **2158864 B**, SHA256 **06e39573dfc9ed18122d9b0c6c69546265b1e3f0e5806b8eb9603fcc09f2ab57**, comienza por **~PSP** y no por una cabecera ELF MIPS en claro. No se ha descifrado ni desensamblado el intérprete. No es prueba de imposibilidad de recuperar código durante ejecución propia de PPSSPP.

(A) Auditor ISO real ejecutado. Informe privado SOLO de métricas SHA256 **9706da0fed03ce943c22d0f99ebfd2cb8ae433d09c12e3418f28a3b0a5c339b0**. (B) 15/15 tests sintéticos locales PASS, usando shims de interfaces de parser SOLO LOCALES; GitHub Actions deben ejecutar con parsers reales. (C) No hubo nueva ejecución PPSSPP en F3-R4 por AppImage ausente y fallo DNS en terminal; no declarar trazas, juegos o capturas nuevos.

Comandos con checkout real e ISO privada:

~~~bash
python tools/f3_campos_alineacion.py --iso-original /PRIVADO/USA.iso --reporte-privado /PRIVADO/F3_R4_LECTURA_NUEVA.json
python -m unittest discover -s tests -p 'test_f3_campos_alineacion.py' -v
~~~

## 4. Siguiente prioridad: semántica MIPS y los 85 demo1001

1. Recuperar PPSSPP oficial 1.20.4 auténtico y ejecutar la ISO original. Autenticar PID starttime, FD de ISO, socket debugger WebSocket 24192, version/game.status/cpu.status del MISMO proceso.
2. Durante demo1001 real, observar lecturas/ejecución de scripts y su intérprete MIPS. Usar breakpoints, trazas de opcodes y destinos efectivos. De ser posible obtener código descifrado desde RAM de la PROPIA SESIÓN en privado. Nunca distribuir dump RAM ni ELF derivado.
3. Investigar operativamente 0x0A y 0x02 junto con otros opcodes de control, contrastando los valores con saltos auténticos antes de declarar el modelo de relocalización. Las coincidencias de enteros del auditor NO son destinos acreditados.
4. Comprobar 97 filas del borrador versus SCRIPT.DAT original (tools/f3_auditar_intro.py con CSV original canónico). Intro: 97 traducciones 2.728 B fuente / 2.859 B codificados español; **85 cambian longitud, 11 del mismo tamaño son solo candidatas y 1 no cambia**. NO reubicar estos 85 sin reconstrucción y guardas independientes de destinos internos/externos, los 51.705 comandos y 1.625 índices. Mantener --event-safe-only.

## 5. Prólogo visual F3 sin fuente demostrada

El prólogo inglés antes de demo1001 sigue sin textura de letras identificada. Frase real observada «Some say, because the treasures were there.» no encontrada ASCII literal completa; match en MONSTER.DAT fue falso positivo. ANIME000.IDT índice PSPFS 234 contiene 231 cabeceras IMY (136 tipo 0x00, 95 tipo 0x02); ANIME001 24 tipo 0x00; ANIME002 sin firma IMY literal. El códec legado NO decodifica los 95 tipo 02; no asumir delta ni frames. Sonda histórica ANIME000.IDT→ANIME000.XDT causó crash antes de título, PC PSP **0x08809498** leyendo **0x15**; solo demostró dependencia de arranque, NO letras.

Necesario PPSSPP genuino en escena visible con rastreo I/O, MIPS, GE gpu.record.dump, TEXADDR/CLUT/PRIM y correlación con RAM/VRAM; solo después diseñar sonda cromática AISLADA/REVERSIBLE privada y A/B sincronizado en la MISMA ESCENA. Preservar fondos, números, iconos y paletas en PSP 480x272/X11 960x544. F3 NO cerrada.

## 6. F2 paralelo y F4–F6 sin falsear

F2 ABIERTA. Histórico C: F1 Opciones 756 px interior/≈764 exterior, Sí/No y seis iconos de Controles; otro runtime llegó a mapa jugable con HUD y movimiento. Dump GE histórico del mapa 65.309 B, SHA d2195fbedd6f430d2a3823db28c12f9f9a9bc789964adefead0bab19298f06b4 (989 registros/301 PRIM). NO demuestra TUIKA en habilidad. Splash SYSTEM PRiSM tenía 1152 magentas tanto USA como sonda; diferencia cero. Mantener comparador X11 A/B nuevo, opción WS --ge-only SIN framebuffer y pulsaciones con RELEASE/ACK. Deben obtenerse USA/sonda de sesiones nuevas con combate verificado y cadena MIPS→RAM→GE→VRAM, sin llamar PNG X11 framebuffer WS.

Validar realmente los 19 glifos **áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō** multicontesto/tintas y origen iconos HUD/tutorial/combate. Conservar 2.721 glifos previos, 19 A1–B3 y white_new_ink=False por defecto, además de 14 franjas/7 subregiones TUIKA.

F4: **4.524** textos SCRIPT.DAT de distinta longitud siguen aplazados. F5: QA genuino de ciudad, dungeon, combate, HUD, retratos, enciclopedia, inventario, audio, guardado/carga y regresión F1. F6: BPS final y EXE Windows x64 solo tras integración end-to-end comprobada. Conservar 9.237 registros, 9.235 español/2 excepciones, 349 PSPFS, glosario, borrador, archivos comerciales privados y PR #7 DRAFT.

## 6A. NUEVO F2 paralelo que NO debe perderse: CLUT2 colorea 9.144 texeles

Se publicó paralelamente docs/F2_IMPACTO_GLOBAL_CLUT2_REAL_2026-11-23.md, reports/RESULTADO_F2_CLUT2_COBERTURA_2026-11-23.json, tools/f2_tuika_clut2_cobertura.py y tests/test_f2_tuika_clut2_cobertura.py. Su análisis **A** sobre ISO original y sonda CLUT2 autenticadas demuestra que la modificación global de tres bytes RGB afectaría **9.144/65.536 texeles (13,95 %)** del atlas TUIKA 256x256: 3.506 en las siete subregiones protegidas, de los que 2.576 estrictamente LOCKED y 930 de etiquetas provisionales; 5.638 fuera. Los valores del histograma son índice0=45.784, índice1=10.608, índice2=9.144. **No usar CLUT2 global como parche final, podría recolorear dígitos/iconos/japonés**; solo sonda privada de diagnóstico. Este hallazgo NO demuestra carga GPU ni escena de combate y deja F2 ABIERTA. Sus 14 tests son sintéticos y CI debe validar imports reales.

Leer también esa documentación/reporte, herramienta y tests antes de cambiar TUIKA. Conservar los recursos originales, ninguna modificación global de paleta y la obligación del A/B auténtico en habilidad antes de cualquier solución visual.

## 7. Publicación y verificación

Con checkout VERDADERO:

~~~bash
python -m unittest discover -s tests -v
python -m unittest discover -s tests -p 'test_f3_campos_alineacion.py' -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/f3_preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/f3_integrabilidad.json
(cd patcher && go test ./...)
git diff --check
git rev-parse HEAD
~~~

Si no existe checkout NO atribuir ejecución local de esos comandos. Actualizar reports/ESTADO_CONTINUIDAD_PPSSPP.json preservando F2 paralelo, docs y JSON públicos SOLO con métricas. Commit fast-forward con expected_sha actual y force:false. Verificar PR #7 OPEN/DRAFT y DOS GitHub Actions push/pull_request SUCCESS en MISMO HEAD FINAL, si faltan declararlo.

**OBLIGACIÓN RECURSIVA INNEGOCIABLE: AL TERMINAR REESCRIBIR COMPLETAMENTE prompts/SIGUIENTE_TAREA.md CON OTRO PROMPT NUEVO AUTÓNOMO E ÍNTEGRO QUE ORDENE ESTA MISMA REGENERACIÓN EN EL SIGUIENTE TURNO HASTA CERRAR F2–F6. MOSTRAR SU TEXTO COMPLETO AL USUARIO.**
