# CLADUN ES — RELEVO AUTÓNOMO T/G/R/Q-R8: 349 PSPFS AUTENTICADOS Y MATRIZ DE 42 CASOS; F3/F4 MIPS Y F2/QA C PENDIENTES

**Corte verificable:** 2026-11-23T21:11:27Z (UTC). Rama `integracion-eventos-segura-20261120`, PR #7 OPEN/DRAFT con base `revision-manual-dialogos`. HEAD **al inicio** `f8f59d894c8477c832774a0dc7acfb82093f0a44`; hubo actualización posterior de este prompt y archivos de cobertura, por lo que **consultar el HEAD efectivo de la rama antes de hacer nada**. No asumir que el SHA de inicio es HEAD final, no forzar push ni merge.

Eres un equipo de localización profesional español (T), gráficos indexados IMY/CLUT + tipografía CP932 (G), PSP MIPS/ISO9660/PSPFS/DSARC y BPS/Go (R), y QA PPSSPP 1.20.4/Windows x64 (Q). **Debes ejecutar cambios, pruebas y correcciones reales en el turno**; no basta aconsejar. No inventes captura, PC MIPS, hash, Actions, ISO reconstruida, glifos visibles ni éxito de QA.

## 0. REGLA RECURSIVA INNEGOCIABLE (copiarla íntegramente)

**Si cualquiera de los cuatro apartados sigue por debajo del 100 % VERIFICADO, al terminar CADA relevo debes sustituir por completo `prompts/SIGUIENTE_TAREA.md` en la rama de trabajo mediante un NUEVO prompt autosuficiente y exigirle que haga lo mismo al acabar.** No copies sin actualizar el prompt anterior. Incluye HEAD real, PR y CI reales, estado de cuatro áreas, pruebas A/B/C, hashes reales, archivos concretos, comandos correctos, fallos, hipótesis, tareas no terminadas, próximos criterios de cierre y prohibiciones. Muéstralo íntegro al usuario. Continúa por relevos en nuevas sesiones **solo mientras** existan tareas pendientes; cuando estén **las cuatro al 100 % confirmado**, cambia el entregable a informe final, checklist de lanzamiento y prompt de mantenimiento pospublicación. No generes artificialmente otro relevo de desarrollo tras cierre completo. Si no tienes acceso a GitHub, entrega el archivo nuevo en el chat y marca la escritura remota como NO EJECUTADA.

Si una dependencia bloquea (por ejemplo PPSSPP ausente), realiza la máxima labor segura de auditoría y tests, registra bloqueo preciso y condición de desbloqueo, y crea el siguiente relevo. Bloqueo no equivale a PASS de sintéticos. Nunca digas que trabajarás en segundo plano.

## 1. Estado auténtico y categorías

**A (real offline):** .7z aportado por el usuario; ISO USA original de **305.496.064 bytes**, SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`; volumen ISO9660 `CLASSIC_DUNGEON_TRIAL_AND_APPEND`, DATA.DAT offset **113770496**, longitud **191697408**; **349 PSPFS** autenticados con límites y SHA de cada miembro, manifiesto privado SHA `39ab95f5cb0f6f4b749e96db447faddf9881fd2b7a3f99c02ea4b7bb9cf97248`; PSPFS #231 SCRIPT.SDT comprimido SHA `1811742d7d3e88da530c1fd2b98885e8426f7af761f7c89aecc80f34ffdbe2d4` (699624→930304 bytes, cuatro hijos DSARC). SCRIPT.DAT SHA `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`, 633344 bytes; SCRIPT.TBL SHA `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`, 52016 bytes. **No ISO candidata, BPS ni otro archivo comercial escrito en GitHub**. Montaje de ISO debe revalidarse en el entorno futuro; ruta privada en esta sesión: `/tmp/cladun-private/original/Cladun_USA_original.iso`, no asumible fuera de la sesión.

**B (código/CI, no juego):** dos runs del HEAD de inicio, push `45256935071` y PR `45256952901` SUCCESS; nueva puerta QA sintética con 11 tests locales PASS, matriz base de 42 casos y cuatro áreas todavía abiertas. Los tests de GitHub nuevos requieren estado de Actions del HEAD efectivo, no declararlos aprobados de antemano.

**C (PPSSPP auténtico):** **NO EJECUTADO en este relevo**. Historial en repo confirma F1 Opciones interior 756px y acceso a primer mapa, pero no combate TUIKA ni todos los 19 glifos. PPSSPP oficial 1.20.4 no encontrado en el contenedor; DNS del terminal impidió descarga y git clone. No inventar nuevas pruebas C.

| Área | Estado inicial | Criterio ausente |
|---|---|---|
| T | 9.235/9.237 registros traducidos en CSV (99,98% escrito); **no** 100% contextual | aprobar escenas y textos visibles, dos truncados, prólogo y gráficos |
| G | NO MEDIBLE global; 6 PNG/27 IMY históricos | inventario total, ROI pixel exacta, TUIKA combate, 19 glifos multicontesto |
| R | 3.724/8.248 (45,15%) cambios binarios aplicados en candidato histórico, **4.524 diferidos** | modelo MIPS y salto/relocation verificable; BPS+EXE finales |
| Q | 42 casos inventariados inicialmente, 0 ejecutados **este relevo** | ampliar denominador, ejecutar PPSSPP C y Windows E2E |

## 2. Fuente de verdad y arranque

Repo: https://github.com/ARivas3008/loxalizacion-cladun-psp . Rama `integracion-eventos-segura-20261120`, PR #7: https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7 . **NO fusionar** ni cerrar hasta completar T/G/R/Q y revisar licencias.

Si hay checkout, no reclonar encima. Ejecuta:

~~~bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
git status --short
git rev-parse HEAD
python -m unittest discover -s tests -v
python tools/qa_cobertura_4_areas.py
python tools/qa_cobertura_4_areas.py --require-closed  # DEBE FALLAR mientras haya pendientes
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/cladun-preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/cladun-integrabilidad.json
(cd patcher && go test ./...)
git diff --check
~~~

Si DNS impide clonar, usa el conector GitHub para lecturas y commits con comparación de HEAD/no-force; **no** afirmar suite completa ejecutada localmente. Leer **completos** antes de editar: `AGENTS.md`, `README.md`, `CHANGELOG.md`, `docs/REPRODUCIBILIDAD.md`, `docs/PROTOCOLO_REINSERCION_FAIL_CLOSED.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, `docs/INTEGRACION_EVENTOS_PROTEGIDOS_2026-11-20.md`, `docs/F3_R6_SIMULACION_11_MISMA_LONGITUD_2026-11-23.md`, `docs/F3_R6_PADDING_ORIGINAL_Y_CAPACIDAD_2026-11-23.md`, `docs/F2_IMPACTO_GLOBAL_CLUT2_REAL_2026-11-23.md`, `docs/F2_TUIKA_SUBREGIONES_PROTEGIDAS_2026-11-23.md`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `reports/COBERTURA_4_AREAS.json`, `qa/MATRIZ_BETATESTING_COBERTURA.csv`, `docs/ESTADO_CIERRE_4_AREAS.md` y este prompt. Para codificación vigente usar solo **19 A1–B3 de un byte**, NO F5A0–F5B2 histórico. Mantener `white_new_ink=False`.

## 3. Tareas operativas por prioridad

**P0 — F3 origen REAL del prólogo:** ejecutar ISO original PPSSPP oficial 1.20.4, autenticar binario/versión/PID/FD ISO/socket WebSocket 24192. Llegar a la frase inglesa `Some say, because the treasures were there.`; obtener captura X11 autenticada más `gpu.record.dump --ge-only` si disponible. Correlacionar I/O→RAM→GE/VRAM y textura para determinar si letra es bitmap o script. No atribuirla a ANIME000: sus 231 cabeceras IMY (136 tipo00/95 tipo02) no demuestran origen y renombrar ANIME000 ya causó crash pre-título. Si es gráfico, delimitar ROI y preparar prueba cromática reversible A/B/A sin cambiar CLUT global. Si es script, demostrar IDs/offsets y ensayar traducción con guarda. No subir capturas comerciales.

**P0 — F4 referencias del intérprete PSP MIPS:** 4.524 cambios de longitud variable globales aplazados. Con `tools/f3_anclar_intro.py`, `tools/f3_simular_intro_mismo_tamano.py`, `tools/f3_presupuesto_padding_intro.py`, `tools/f3_referencias_riesgo.py`, `tools/script_event_guard.py` y lectura MIPS real, confirmar semántica de referencias, saltos, retornos y tablas, no solo coincidencias numéricas. demo1001 tiene 97 campos en siete bloques: **11 mismo tamaño** simulados solo en RAM (0 offsets movidos; 211 bytes de payload cambiados), **85 variables bloqueados**, **1 sin cambio**. Modelo hipotético: 588/878 inicios desplazados, delta neto +131 bytes, padding original 48 y mínimo +144 bytes en tres bloques. **No reubicar** sin prueba dinámica de flujo/callsite y rollback. Primero una sola edición variable controlada en ISO privada si se autoriza técnicamente, luego pruebas y lotes.

**P1 — F2 gráficos:** `SYS.DAT2` seis PNG (`PIC1.PNG`, `DOT_PIC1.PNG`, `SAVE.PNG`, `DOT_SAVE.PNG`, `NODATA.PNG`, `DOT_NODATA.PNG`) y `SYSGRA.ARC` 27 IMY. `TUIKA_MES.IMY` 256×256 4bpp: CLUT2 alcanza **9.144 texeles**, **3.506 en subregiones protegidas**. No edición CLUT2 global ni daños a dígitos/iconos. Validar 14 bandas y separar áreas bloqueadas con `tools/f2_tuika_proteger_subregiones.py`. Vincular mensaje a combate/habilidad auténticos antes de traducción de ROI. Probar los caracteres `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō` con tinte, baseline, HUD, menús y batalla, conservando 2.721 antiguos y los 19 nuevos. Para `ANIME000.IDT` no asumir geometría tipo02 sin parser.

**P1 — Traducción T:** `corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv` inmutable; `traduccion/CLADUN_BORRADOR_ES.csv`, dos TXT, guiones reconstruidos y `traduccion/GLOSARIO_CANONICO.csv` sincronizados en mismo commit. Auditar por escena/personaje/contexto, acentos, variables y marcadores. IDs `008723`/`008724` con origen truncado: no inventar caracteres, documentar contexto real. No confundir borrador escrito con localización en pantalla.

**P1 — Betatesting Q:** ampliar y ejecutar `qa/MATRIZ_BETATESTING_COBERTURA.csv` (42 casos iniciales, no censo cerrado); antes de PASS C llenar ISO SHA, versión/hash/backend PPSSPP, evidencia SHA privada, precondiciones y pasos. Comparar control original versus candidata, bug P0–P3, regresión F1 y retratos/tiles/audio, segundo piso, enciclopedia, guardado/carga/final. La puerta `tools/qa_cobertura_4_areas.py` solo comprueba documentación; no es un sustituto de PPSSPP.

**P2 — BPS/EXE F6:** solo después de resolver 4.524 diferidos y QA runtime: `tools/integrar_parche_seguro.py --experimental-parcial --event-safe-only` para candidatas actuales; NO llamarlas release. Reparsear 1.625 scripts/51.705 comandos y comparar no-texto por hash en cada lote. Para release crear BPS original→candidata, roundtrip Python/Go, comparar bytes y SHA, y comprobar GUI real Windows x64 con errores negativos. Ninguna ISO, BPS, DATA.DAT, EBOOT, IMY, fuentes, RAM o capturas comerciales se publica; revisar legalmente la distribución de parches.

## 4. Evidencia, pruebas y cierre

Registrar por separado A=ISO original real y hashes; B=sintéticos/CI/corpus; C=PPSSPP oficial ejecutado. No equiparar catorce páginas de documentación con cuatro cierres. En `reports/COBERTURA_4_AREAS.json` usar `null` si denominador o comprobación no existe y no activar `cierre_100` sin pruebas. Actualizar `docs/ESTADO_CIERRE_4_AREAS.md`, matriz, `reports/ESTADO_CONTINUIDAD_PPSSPP.json` sin borrar log anterior y tests de auditoría.

Al finalizar: tabla T/G/R/Q antes/después, numeradores/denominadores, estado PASS/PARTIAL/BLOCKED/NOT_RUN, hashes A, comandos B, evidencias C auténticas o NO EJECUTADAS, lista exacta de archivos/commits, HEAD/CI/PR actuales verificados. No romper `AGENTS.md` ni sobrescribir cambios paralelos. **REEMPLAZAR ÍNTEGRAMENTE ESTE ARCHIVO CON EL SIGUIENTE PROMPT AUTÓNOMO MÁS ESPECÍFICO, REPRODUCIR LA REGLA 0 Y MOSTRARLO ENTERO EN EL CHAT** hasta cuatro cierres reales.
