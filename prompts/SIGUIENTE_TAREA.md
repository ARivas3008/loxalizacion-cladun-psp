# CLADUN ES — NUEVO RELEVO AUTÓNOMO F3-R4: REFERENCIAS DE EVENTOS, PRÓLOGO VISUAL Y F2 TUIKA; F4–F6 ABIERTAS

**Corte: 23/11/2026.** Eres ingeniero sénior de PSP MIPS, PPSSPP oficial v1.20.4, ISO9660/PSPFS/DSARC, IMY, fuentes CP932 A1–B3, GE/VRAM y WebSocket. Ejecuta análisis, pruebas y correcciones reales, no solo recomendaciones. Distingue evidencia **A** (ISO auténtica), **B** (sintéticos/CI) y **C** (juego ejecutado en PPSSPP). No inventes capturas, PCs, direcciones, tramas, hashes, éxito CI ni publicaciones.

## 0. Obligación recursiva INNEGOCIABLE

**AL TERMINAR sustituye COMPLETAMENTE `prompts/SIGUIENTE_TAREA.md` por OTRO prompt NUEVO, autónomo e íntegro, con el estado y SHA reales, herramientas, evidencias A/B/C, resultados CI, comandos, pendientes y esta MISMA obligación de REGENERAR otro prompt tras cada relevo hasta F2–F6 auténticamente completadas. Muestra ÍNTEGRO el nuevo prompt al usuario.** Nunca prometas trabajo asíncrono.

## 1. Estado GitHub, contrato y lecturas

Repositorio: https://github.com/ARivas3008/loxalizacion-cladun-psp . Rama: `integracion-eventos-segura-20261120`. PR #7 https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7 . Base: `revision-manual-dialogos`. Mantener **OPEN/DRAFT, sin merge, sin force push**. No modificar corpus original, rama base, ni recursos comerciales.

Los SHA `cffd12b0550ac47f92980ebeb195fe1afabce9ab`, `79e803510d2f2d5f08efe3d2b6cc7ff0810692db` son HISTÓRICOS, no asumir HEAD actual. Primero:
```bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
git status --short
git rev-parse HEAD
```
Si el terminal no resuelve github.com, NO fingir clone/checkout. El conector GitHub puede fetch y usar create_blob/create_tree/create_commit/update_ref con `expected_sha` y `force:false`; revalidar HEAD antes de cada escritura.

Leer completos: `AGENTS.md`, `README.md`, este prompt, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `docs/F3_REFERENCIAS_RIESGO_2026-11-23.md`, `reports/RESULTADO_F3_REFERENCIAS_RIESGO_2026-11-23.json`, `tools/f3_referencias_riesgo.py`, su test; `docs/F3_ANIME_TOPOLOGIA_2026-11-23.md`, `docs/F3_ANIME_IMY_ESTRUCTURAS_2026-11-23.md`, `docs/F3_PROLOGO_ANIME000_DEPENDENCIA_PPSSPP_REAL_2026-11-23.md`, `docs/F3_INTRO_INTENTO_PPSSPP_Y_ORIGEN_SCRIPTS_2026-11-23.md`, `tools/f3_auditar_intro.py`, `tools/f3_anime_topologia.py`, `tools/f3_anime_imy_estructuras.py`, `tools/script_event_guard.py`, `tools/integrar_parche_seguro.py`, `tools/charset_es.py`. Conservar F2: `docs/F2_GE_ONLY_WEB_SOCKET_SIN_FRAMEBUFFER_2026-11-23.md`, `docs/F2_REVALIDACION_ISO_TUIKA_Y_RELEASE_WS_2026-11-23.md`, `docs/F2_MAPA_JUGABLE_GE_X11_F1_2026-11-23.md`, herramientas `f2_ppsspp_ws_1204.py`, `f2_ruta_ws_liberacion_segura.py`, `f2_ge_dump_1204.py`, `f2_ws_procedencia_ppsspp.py`, `f2_tuika_proteger_subregiones.py` y tests.

## 2. Hashes y límites de publicación

ISO USA original del 7z del usuario: **305496064 B**, SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. F1 española CANÓNICA histórica: **306456576 B**, SHA256 `496689f858322fa5dbef63c797365e32b2005ef812f230c34e367550eb53e986`; BPS USA→F1 histórico SHA `daaa64ab1994271debc6464f3c70ab0f30a2ab3f9a1743dbd6a65f3c88d20acd`. PPSSPP AppImage 1.20.4 oficial Linux x86_64: **50689748 B**, SHA256 `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`; https://github.com/hrydgard/ppsspp/releases/download/v1.20.4/PPSSPP-v1.20.4-anylinux-x86_64.AppImage . Autenticar hash ANTES de correr.

**NUNCA versionar, publicar ni distribuir ISO, DATA.DAT, EBOOT, BPS, fuentes, IMY, imágenes/PNG comerciales del juego, capturas PPSSPP, RAM/GE/VRAM, vídeos o dumps.** Solo código propio, pruebas con datos sintéticos, documentos, métricas y hashes. Experimentos ISO y evidencias de juego SOLO privados. No alterar originales.

## 3. NUEVO F3-R3: candidatos numéricos, NO destinos

Se ejecutó auditoría A sobre ISO USA original auténtica → DATA.DAT, PSPFS 231 SCRIPT.SDT → DSARC SCRIPT.DAT SHA `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`, SCRIPT.TBL SHA `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`. Se leyeron **1625 bloques, 51705 comandos, 46308 no textuales**, siete bloques demo1001 con 878 comandos. Script solo lectura y 11 tests sintéticos PASS (no equivalen a PPSSPP).

Las ventanas u32 de argumentos NO textuales, excluyendo cero, coincidieron con:
- IDS de script: **4680** global / **25** demo1001.
- Inicios de script: **39** global / **1** demo1001.
- Offsets absolutos de comandos: **2883** / **40** demo1001.
- De esos absolutos, en otros bloques: **2706** / **40** demo1001.
- Offsets relativos al bloque: **1451** / **21** demo1001.

**ESTOS NÚMEROS NO SON SALTOS DEMOSTRADOS.** Valores u32 pueden ser coincidentes por casualidad, y las categorías se solapan. `0x02` payload byte 5 acumula 1439 coincidencias absolutas; **no llamarlo instrucción branch** por esto. En próxima fase, identificar intérprete MIPS, semántica de opcodes y destinos reales; verificar referencias externas y relocación de SOLO los 85 mensajes demo1001 antes de cambiar su longitud. El script público `tools/f3_referencias_riesgo.py` debe ser sometido al mismo ISO privado con su auditoría; nunca tratar la CI sintética como prueba C.

Comando:
```bash
python tools/f3_referencias_riesgo.py --iso-original /PRIVADO/USA.iso --reporte-privado /PRIVADO/F3_RIESGO_NUEVO.json
```

## 4. F3-prólogo visual: todavía sin origen demostrado

Prólogo previo a demo1001 muestra inglés sobre fondo animado tanto USA como F1. No está localizado el origen de sus letras: una coincidencia `some say` en MONSTER.DAT era biografía, falso positivo. Prueba A/B/A histórica PPSSPP 1.20.4: renombrar ANIME000.IDT→ANIME000.XDT cambiando un byte en ISO privada causó crash ANTES del título en PC `0x08809498` con lectura `0x00000015`; restaurar USA recuperó. NO prueba que ANIME000 dibuje letras ni se debe repetir como sonda visual.

Inventario autenticado ANIME000.IDT (PSPFS 234) 231 cabeceras IMY: 136 tipo `0x00`, 95 tipo `0x02`; 17 intervalos 0x02 idénticos repetidos. ANIME001.LDT 24 tipo 0x00; ANIME002.LDT cero firmas IMY. En algoritmo legado 160 tipo 00 compatibles con flujo, 95 tipo 02 incompatibles. Esto no prueba imágenes/frames ni deltas.

**Prioridad C auténtica:** recuperar AppImage oficial, autenticar ISO y PID/socket/FD/versión WS, arrancar prólogo real, registrar I/O, MIPS y GE `gpu.record.dump` con TEXADDR/CLUT/PRIM en escena visible. Correlacionar textura/VRAM con miembro PSPFS antes de cualquier sonda. Solo si existe cadena causal, producir sonda cromática aislada NO destructiva en copia privada, A/B sincronizado + control negativo, preservar 349 PSPFS y DSARC, y traducir ROI de letras en PSP 480×272 / ventana 960×544. Sin traza, seguir parsers fail-closed de IMY 0x02; no repintar a ciegas.

## 5. F3 eventos 85, F2 y F4–F6

En `demo1001_00.dsf` y `demo1001_01.dsf`: 7 bloques, 878 comandos, 98 opcodes textuales, 97 no vacíos (2728 bytes origen), 97 traducciones español (2859 bytes con codec A1–B3), **85 diferente longitud BLOQUEADOS**, 11 candidatos mismo tamaño, 1 idéntico. Seguir `--event-safe-only` y auditar 97 offsets contra CSV e ISO; no desplazar 51705 comandos ni 1625 comienzos sin modelar referencias con MIPS y pruebas independientes. F4: **4524** textos globales de longitud cambiante pendientes.

F2 permanece **ABIERTA**: PPSSPP F1 anterior llegó a mapa jugable, pero no A/B TUIKA en combate; falta traza MIPS→RAM→GE→VRAM y 19 caracteres `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō` multicontesto. F1 Opciones alcance anterior 756px interior/≈764 exterior, seis iconos. GE mapa real histórico 65309 B/989 registros/301 PRIM SHA `d2195fbedd6f430d2a3823db28c12f9f9a9bc789964adefead0bab19298f06b4` NO demuestra TUIKA. En splash SYSTEM PRiSM original y sonda había 1152 magentas y 0 diferencia; falso positivo. Conservar modo WS `--ge-only` (dump GE, SIN PNG framebuffer), y mecanismo botones RELEASE con ACK. No confundir captura X11 con framebuffer WS.

F5: QA auténtico aventura, combate, segundo piso, retratos, HUD, glifos, guardado/carga, enciclopedia, sonido. F6: BPS final/EXE Windows x64 con pruebas end-to-end sin publicar assets. Preservar 9237 registros, 9235 en español/2 excepciones, 349 PSPFS, 2721 glifos originales+19 nuevos, `white_new_ink=False`, `--event-safe-only`. Mantener PR #7 DRAFT.

## 6. Validación y publicación

En checkout GIT VERDADERO:
```bash
python -m unittest discover -s tests -v
python -m unittest discover -s tests -p 'test_f3_referencias_riesgo.py' -v
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/f3_preflight_nuevo.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/f3_integrabilidad_nuevo.json
(cd patcher && go test ./...)
git diff --check
```
Separar resultados CI B de pruebas C. Documentar reportes con hashes y bloquear cualquier cambio binario no justificado. Commit rápido sin fuerza/expected_sha, CI push y PR verificadas SUCCESS **sobre mismo HEAD final**, PR #7 sigue OPEN/DRAFT. Si emulador o red no disponibles, no declarar tests C, dejar el bloqueo explícito.

**OBLIGACIÓN RECURSIVA INNEGOCIABLE: AL TERMINAR REEMPLAZAR COMPLETAMENTE ESTE PROMPT POR OTRO NUEVO AUTÓNOMO, ACTUALIZADO, CON ESTADO, SHA, HALLAZGOS, HASHES, CÓDIGO, CI, INSTRUCCIONES Y PENDIENTES REALES, Y EXIGIR LA MISMA REGENERACIÓN RECURSIVA HASTA COMPLETAR F2–F6. MOSTRARLO ÍNTEGRO AL USUARIO.**
