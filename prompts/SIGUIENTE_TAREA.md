# CLADUN ES — RELEVO AUTÓNOMO F4/F3-R15: PPSSPP 1.20.4 AUTENTICADO, UBICAR SCRIPT.DAT EN RAM Y PROBAR NUEVE SONDAS SIN ROMPER JUEGO

**Corte local: 23/11/2026.** Repositorio https://github.com/ARivas3008/loxalizacion-cladun-psp. Rama de trabajo `integracion-eventos-segura-20261120`, base `revision-manual-dialogos`, PR #7 OPEN/DRAFT SIN MERGE. HEAD al inicio del R14: `92dbe2e1b3e235ce0e62906adb159425347e3976`. Commits de herramientas R14 `1cea38dad3bced04971514f8bc6cec7507d1af67` y de tests WS `0d5f0aa33ae32c3fe2f5024e172b5896a5302fcf`. El commit documental R14 que contiene este prompt es POSTERIOR: siempre obtener SHA FINAL real, estado PR y workflows CI push/PR por ese SHA, sin dar por aprobados runs anteriores. No force push, rebase destructivo, cambios de rama base ni merge.

Eres ingeniero sénior PSP MIPS, PPSSPP oficial **v1.20.4**, ISO9660/PSPFS/DSARC, IMY/CLUT, CP932 A1–B3, localización española y QA. **Ejecuta las pruebas y cambios reales posibles AHORA; no basta con recomendaciones.** Evidencia A = ISO original autentificada (estática), B = código/tests sintéticos/CI, C = juego real ejecutado en PPSSPP con procedencia. Nunca inventes capturas, PCs MIPS, tramas GE/VRAM, ejecución, hashes, éxito CI o cierre de las cuatro áreas.

## 0. OBLIGACIÓN RECURSIVA INNEGOCIABLE (REPRODUCIR COMPLETA SI QUEDA UN PENDIENTE)

**Si cualquiera de los cuatro apartados sigue por debajo del 100 % VERIFICADO, al terminar CADA relevo debes sustituir por completo prompts/SIGUIENTE_TAREA.md en la rama de trabajo mediante un NUEVO prompt autosuficiente y exigirle que haga lo mismo al acabar.** No copies sin actualizar el prompt anterior. Incluye HEAD real, PR y CI reales, estado de cuatro áreas, pruebas A/B/C, hashes reales, archivos concretos, comandos correctos, fallos, hipótesis, tareas no terminadas, próximos criterios de cierre y prohibiciones. Muéstralo íntegro al usuario. Continúa por relevos en nuevas sesiones **solo mientras** existan tareas pendientes; cuando estén **las cuatro al 100 % confirmado**, cambia el entregable a informe final, checklist de lanzamiento y prompt de mantenimiento pospublicación. No generes artificialmente otro relevo de desarrollo tras cierre completo. Si no tienes acceso a GitHub, entrega el archivo nuevo en el chat y marca la escritura remota como NO EJECUTADA.

Si el emulador sigue bloqueado, realizar trabajo estático A y pruebas B sustantivas, describir el bloqueo y el desbloqueo concreto y crear relevo R16. B no sustituye C y no se promete trabajo fuera del turno.

## 1. ESTADO R14 Y PRUEBAS DISPONIBLES

**T — traducción:** 9.235/9.237 registros con borrador ES (99,98% escrito, NO traducción aprobada); dos orígenes truncados 008723/008724, 586 escenas/2.216 cajas pendientes de revisión contextual y en juego, glosario, tildes, textos gráficos y frase del prólogo.

**G — gráficos:** NO MEDIBLE global. Investigaciones parciales 6 PNG SYS.DAT2, 27 IMY SYSGRA; 2.721 glifos anteriores y 19 nuevos A1–B3. TUIKA_MES.IMY 256×256/4bpp CLUT2: 9.144 texeles afectados, 3.506 protegidos. No usar recolor CLUT2 global; `white_new_ink=False`. Probar 19 glifos en menús/HUD/batalla y prólogo con PPSSPP real.

**R — ROMhacking:** 3.724/8.248 sustituciones históricas seguras en candidata experimental (45,15% de ese conjunto), **4.524 diferidas** por riesgo de tamaño/control de eventos. 97 textos demo1001: 11 de igual longitud solo simulados RAM, 85 variables bloqueados, 1 idéntico. Modelo lineal movería 588/878 inicios; no hay interpretación MIPS certificada, BPS/EXE final ni modelo de relocalización seguro.

**Q — betatesting:** **53 casos** Q001–Q053 definidos; Q052 procedencia y Q053 nueve sondas siguen NOT_RUN, igual que Q050/Q051 y el resto de la candidata final. Universo total no cerrado, cero C nuevos R14. Exigir segundo nivel, batalla, guardado-cerrar-cargar, enciclopedia, finales, audios y regresiones Opciones F1; 0 defectos P0/P1 al cierre.

**A ISO USA original:** archivo privado 305.496.064 B, SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`; DATA.DAT PSPFS 349; SCRIPT.DAT SHA `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`, SCRIPT.TBL SHA `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`. 1.625 scripts, 51.705 comandos, 46.308 no textuales. No asumir que rutas temporales anteriores sobreviven en otro entorno.

**NOVEDAD A R14 — MANIFIESTO DE NUEVE SONDAS CON OFFSET PRECISO DEL SCRIPT.DAT DESCOMPRIMIDO:**

| Bloque/orden | Offset SCRIPT.DAT decimal | Opcode | ID instrucción | u32 | Bloque si ID=valor−100 | Bloque literal |
|---|---:|---|---:|---:|---:|---:|
| 20/20 | 7420 | 0x0A | 818 | 100100 | 757 | 758 |
| 757/2 | 218095 | 0x0A | 8 | 100200 | 758 | 764 |
| 758/1 | 218133 | 0x0C | 18 | 100290 | 759 | 765 |
| 758/415 | 223351 | 0x0C | 523 | 100 | sin ID0 | 89 |
| 758/416 | 223360 | 0x0A | 525 | 100201 | 760 | 766 |
| 759/23 | 223602 | 0x0C | 573 | 100 | sin ID0 | 89 |
| 760/1 | 223637 | 0x0C | 7 | 100291 | 761 | no coincide |
| 760/336 | 227968 | 0x0C | 413 | 100 | sin ID0 | 89 |
| 761/23 | 228194 | 0x0C | 457 | 100 | sin ID0 | 89 |

**IMPORTANTE:** offsets SCRIPT.DAT no son direcciones RAM ni PCs MIPS. Los cinco enlaces y cuatro argumentos 100 son HIPÓTESIS, nunca llamadas/saltos comprobados. Informes `reports/F4_R14_SONDAS_Y_PPSSPP_2026-11-23.json` y `docs/F4_R14_SONDAS_Y_PPSSPP_2026-11-23.md`.

**NOVEDAD B R14:** `tools/f4_r14_manifest_sondas.py` y `tools/f4_r14_ppsspp_preflight.py`, pruebas `tests/test_f4_r14_manifest_sondas.py` (16), `tests/test_f4_r14_ppsspp_preflight.py` (13) y `tests/test_f4_r14_websocket_protocol.py` (7). **36 tests sintéticos PASS local**. Manifiesto A de la ISO real sin activos comerciales SHA256 privado `4b979163721dea3ba539c601f85ba7d449eb31e3f4807cb99ef72b0e5b63ab62`. Comprobar CI real del HEAD final en GitHub antes de afirmar PASS.

**Hallazgo crítico del PPSSPP tag v1.20.4:** respuesta WebSocket `version` solo devuelve `name` y `version`, NO devuelve PID ni ruta del disco (a diferencia de documentación master más reciente). Suplir con `/proc/PID/stat`, `/proc/PID/exe`, `/proc/PID/environ`, `/proc/PID/fd` y el inode LISTEN de `/proc/net/tcp*`. El protocolo de v1.20.4 dispone de ruta `/debugger`, subprotocolo `debugger.ppsspp.org`, `version`, `game.status`, `cpu.status`, `cpu.getAllRegs`, `memory.read` y breakpoints. No confiar en funciones de master inexistentes en v1.20.4.

**C R14 NO EJECUTADA:** AppImage oficial ausente y `github.com` sin DNS en terminal. El preflight real falló correctamente con exit=1 `Official PPSSPP AppImage absent or hash differs` y no generó informe de traza. No se han medido PCs, registros reales, retornos o lectura de SCRIPT.DAT en PPSSPP.

## 2. REPOSITORIO, INTEGRIDAD Y COMANDOS

Leer completos antes de editar `AGENTS.md`, `README.md`, `CHANGELOG.md`, `docs/REPRODUCIBILIDAD.md`, `docs/PROTOCOLO_REINSERCION_FAIL_CLOSED.md`, `docs/PLAN_HASTA_IMPLEMENTACION_PPSSPP_2026-11-20.md`, `docs/INTEGRACION_EVENTOS_PROTEGIDOS_2026-11-20.md`, el informe y JSON F4_R14, ambas herramientas R14 y sus 3 archivos de test, `tools/f4_r13_grafo_intro.py`, `tools/f4_r12_candidatos_especiales.py`, `tools/f4_r11_desfase_ids.py`, `tools/f3_referencias_riesgo.py`, `tools/script_event_guard.py`, `docs/F3_ANIME_IMY_ESTRUCTURAS_2026-11-23.md`, `docs/F2_TUIKA_SUBREGIONES_PROTEGIDAS_2026-11-23.md`, `qa/MATRIZ_BETATESTING_COBERTURA.csv`, `reports/COBERTURA_4_AREAS.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `docs/ESTADO_CIERRE_4_AREAS.md`, `prompts/SIGUIENTE_TAREA.md`.

En checkout real:

```bash
git fetch origin
git switch integracion-eventos-segura-20261120
git pull --ff-only
git status --short
git rev-parse HEAD
python -m unittest discover -s tests -v
python -m unittest discover -s tests -p 'test_f4_r14*.py' -v
python tools/qa_cobertura_4_areas.py
python tools/qa_cobertura_4_areas.py --require-closed   # DEBE FALLAR
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/cladun-preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/cladun-integrabilidad.json
(cd patcher && go test ./...)
git diff --check
```

Con ISO original privada de SHA exacto, no reutilizar reportes:

```bash
python tools/f4_r14_manifest_sondas.py --iso-original /PRIVADO/Cladun_USA_original.iso --reporte-privado /PRIVADO/R15_MANIFIESTO_NUEVO.json
```

Si GitHub DNS no resuelve, leer y escribir con el conector GitHub de forma no forzada verificando HEAD. No afirmar que se ejecutó suite completa local si se ejecutó solo CI.

## 3. P0 — EMULADOR REAL Y TRAZA MIPS SIN SUPOSICIONES

Conseguir PPSSPP **OFICIAL v1.20.4 Linux x86_64** de fuente verificada (AppImage `PPSSPP-v1.20.4-anylinux-x86_64.AppImage`), hash histórico esperado `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`. No ejecutar binarios alternativos sin autenticación. Una sesión real debe tener ISO original SHA exacto, backend, starttime, fd ISO y socket 24192 asociados al mismo PID. Instalar `websocket-client` si hace falta. Con PPSSPP arrancado y `PID_REAL` recuperado:

```bash
python -m pip install websocket-client
python tools/f4_r14_ppsspp_preflight.py --iso-original /PRIVADO/Cladun_USA_original.iso --appimage /PRIVADO/PPSSPP-v1.20.4-anylinux-x86_64.AppImage --pid PID_REAL --port 24192 --reporte-privado /PRIVADO/R15_PPSSPP_SESION_NUEVA.json
```

Esta herramienta comprueba **procedencia**, no se autopromueve a prueba C de eventos. Si falla el hash o falta fd de ISO, detener la captura y documentar. No confundir `version` con PID, pues v1.20.4 no lo devuelve. Nunca usar direcciones RAM inventadas a partir de offsets en SCRIPT.DAT.

**Q050/Q053:** hallar la carga real de SCRIPT.DAT dentro del proceso PSP y la función de dispatch mediante debugging legítimo y lectura de RAM; ubicar nueve comandos según firmas/IDs y offsets reales, registrar PCs MIPS, registros y modificación de estado. Contrastar rutas 20→757→758→760 y el literal 20→758 / 757→764. Exigir causalidad y retorno observado, no solo igualdad de IDs. Guardar trazas y screenshots privadas con hashes y proceso autenticado.

**Q051/Q053:** distinguir `0x0C` con u32 `100290` / `100291` (posibles bloques 759/761) del `0x0C` con u32 `100` en cuatro sitios. Verificar semántica y efectos con A/B/A original-sonda-original; no confundir aparente fin de bloque con retorno, ni asumir que el u32 es llamada. Revisar `0x0B` (valor 3 / quinto byte 100/101), `0x0A` 0/1, referencias 16bit, tablas indirectas, stack y retornos.

**PROHIBIDO RELOCALIZAR** los 85 textos variables de demo1001 o los 4.524 globales sin demostrar semántica completa y primeros cambios privados A/B/A, reparseo idéntico de 51.705 comandos y 46.308 payloads no textuales, además de recursos PSPFS ajenos intactos. Mantener `--event-safe-only`.

## 4. F3/F2, T/G/Q Y F6

F3: localizar origen de la frase inglesa del prólogo `Some say, because the treasures were there.` en bitmap/script realmente ejecutado, no inferir de 231 firmas IMY de ANIME000.IDT. Antes se produjo crash por renombrar ANIME000; NO repetir. Trace auténtica archivo→RAM→GE/VRAM/TEXADDR/CLUT/PRIM; traducir ROI local con A/B/A y sin corrupción de sprites/tiles/retratos.

T: revisar glosario, 9.237 registros, 586 escenas/2.216 cajas, tildes, variables, naturalidad y 008723/008724 cuyo original está truncado; no inventar fuente. Sincronizar corpus derivado CSV/TXT/bilingüe/guiones sin tocar corpus fuente; inventariar todo texto gráfico visible.

G: proteger 2.721 glifos originales +19 A1–B3 `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō`; usar `white_new_ink=False`, TUIKA_MES CLUT2 sin recolor global, probar variantes de tinta, diálogos/HUD/Opciones/combate, 6 PNG y 27 IMY e inventario real completo.

Q: completar al menos 53 casos definidos y ampliar por escenas. Ningún PASS C de candidata final sin PPSSPP autenticado, capturas privadas, reproducibilidad, ciclo guardar/cerrar/cargar, segundo nivel, jefes, enciclopedia, final/créditos y cero defectos P0/P1.

F6: únicamente tras T/G/R/Q 100% realmente verificados, crear BPS diferencial y EXE Windows x64 con pruebas E2E negativas y roundtrip/hashes, revisión legal. No subir ISO, EBOOT, DATA.DAT, IMY, FONT, sprites, RAM/GE/VRAM, capturas ni BPS con recursos comerciales. PR #7 sigue DRAFT, sin merge.

## 5. ENTREGA, GITHUB Y SUCESIÓN

Actualizar sin borrar historia `reports/COBERTURA_4_AREAS.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `qa/MATRIZ_BETATESTING_COBERTURA.csv`, `docs/ESTADO_CIERRE_4_AREAS.md`, informes/validaciones nuevos; aportar tabla antes/después con numeradores reales o NO MEDIBLE, evidencias A/B/C, SHA ISO/CI, errores, rollback, HEAD final y PR/CI de ese SHA. No elevar porcentaje por B o por un preflight sin gameplay.

**AL FINAL, SI CUALQUIER ÁREA PERMANECE BAJO 100% VERIFICADO, REEMPLAZA COMPLETAMENTE `prompts/SIGUIENTE_TAREA.md` CON UN NUEVO PROMPT AUTÓNOMO R16 QUE COPIE ENTERA LA REGLA RECURSIVA 0, Y MUÉSTRALO ÍNTEGRO AL USUARIO.** Si T/G/R/Q están realmente cerrados, informe final de lanzamiento y prompt de mantenimiento, nunca inventar un relevo de desarrollo.

