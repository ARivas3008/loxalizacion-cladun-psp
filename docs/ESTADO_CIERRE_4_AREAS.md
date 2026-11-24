# CLADUN ES — estado auditable de cierre T/G/R/Q (23-11-2026)

**Corte de este relevo: 2026-11-23T21:11:27Z.** Estado: **T PARTIAL, G BLOCKED, R PARTIAL/BLOCKED, Q NOT_RUN**. Este documento no convierte pruebas A/B en evidencia C. PR #7 permanece OPEN/DRAFT. Las pruebas históricas no se adjudican a esta sesión.

## A: verificación binaria auténtica de esta sesión

ISO USA extraída por libarchive desde el .7z del usuario en una carpeta privada fuera del repositorio, sin modificación: **305.496.064 bytes**, SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. Su volumen ISO9660 es `CLASSIC_DUNGEON_TRIAL_AND_APPEND`; contiene **16 registros ISO9660**, `PSP_GAME/USRDIR/DATA.DAT` en offset **113.770.496**, longitud **191.697.408**. Se comprobaron por límites y SHA los **349 registros PSPFS**; manifiesto privado de metadatos SHA256 `39ab95f5cb0f6f4b749e96db447faddf9881fd2b7a3f99c02ea4b7bb9cf97248`.

PSPFS #231 `SCRIPT.SDT`: **699.624 bytes** comprimidos, SHA256 `1811742d7d3e88da530c1fd2b98885e8426f7af761f7c89aecc80f34ffdbe2d4`, descomprime a **930.304 bytes** y **4 DSARC**. `SCRIPT.DAT`: **633.344 bytes**, SHA256 `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`; `SCRIPT.TBL`: **52.016 bytes**, SHA256 `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`. Coinciden con el baseline histórico; **no se editaron los recursos ni se creó ISO candidata**.

**No se reparsearon los 51.705 comandos en esta sesión**: sus recuentos y la simulación de 11 textos proceden de los informes anteriores, no de la auditoría nueva. Tampoco se ha observado PC MIPS, prólogo dibujado o TUIKA en juego.

## B: cobertura real versus métricas históricas

| Apartado | Métrica con población | Estado |
|---|---|---|
| T | 9.235/9.237 textos escritos (99,98 % del CSV); 2 origen truncado; aprobación contextual y visibilidad de todo el juego **NO MEDIBLES** | PARTIAL |
| G | 6 PNG y 27 IMY de estudios históricos; inventario completo de imágenes con inglés y aprobación en PPSSPP desconocidos | BLOCKED / NO MEDIBLE |
| R | 3.724/8.248 sustituciones planificadas (45,15 %) en candidata parcial histórica; 4.524 aplazadas; sin modelo MIPS para longitudes variables | PARTIAL / BLOCKED |
| Q | **42 casos iniciales** definidos, **0 ejecutados en este relevo**; no representan necesariamente todos los casos finales | NOT_RUN / cobertura total NO MEDIBLE |

Nuevo validador `tools/qa_cobertura_4_areas.py` con **11 pruebas sintéticas PASS locales** y rechazo explícito de PASS C sin hashes, cierre con denominadores nulos, 4524 diferidas o matriz incompleta. El PASS del validador significa *consistencia de metadatos*, no juego probado. Nuevo `qa/MATRIZ_BETATESTING_COBERTURA.csv` define 42 casos sin falsificar `PASS`; `reports/COBERTURA_4_AREAS.json` conserva null para mediciones ausentes. En el HEAD inicial `f8f59d894c8477c832774a0dc7acfb82093f0a44` se verificaron Actions **45256952901 (PR)** y **45256935071 (push)**: SUCCESS, sin ISO. El CI del nuevo commit se verificará separadamente.

## C: pruebas de juego no ejecutadas ahora

No hay binario oficial PPSSPP v1.20.4 disponible en este contenedor, y `git ls-remote` falló con `Could not resolve host: github.com`. El conector GitHub sí está habilitado. Históricamente existen capturas de Opciones F1 y primer mapa, **pero ninguna captura, trama GE, PC MIPS o test C se produjo ahora**. Falta la procedencia de las letras del prólogo, TUIKA en combate, glifos multicontesto, segundo nivel, enciclopedia, guardado/carga y Windows x64 E2E.

## Reglas y siguiente paso

No se tocó corpus, fuentes, gráficos, EBOOT, `SCRIPT.DAT/TBL`, BPS, ISO ni rama base. `--event-safe-only`, `white_new_ink=False` y PR DRAFT siguen obligatorios. Hay que obtener PPSSPP 1.20.4 oficial y autenticar PID/FD ISO/WS antes de la prueba C, o continuar con auditoría de solo lectura mientras dure el bloqueo. No subir assets comerciales, capturas ni dumps.

Comandos para un checkout real (no ejecutados aquí por DNS): `python -m unittest discover -s tests -v`, `python tools/qa_cobertura_4_areas.py`, `python tools/qa_cobertura_4_areas.py --require-closed` (debe FALLAR todavía), `python tools/f3_simular_intro_mismo_tamano.py --iso-original /PRIVADO/USA.iso --reporte-privado /PRIVADO/sim.json`, `python tools/f3_presupuesto_padding_intro.py --iso-original /PRIVADO/USA.iso --reporte-privado /PRIVADO/padding.json`, `(cd patcher && go test ./...)`.

**Cierre automático: 0/4 áreas.** No certificar 100% por que exista matriz, script de validación o Actions en verde.

## R8 — auditoría estática F4 sobre la ISO auténtica (23/11/2026)

El barrido de **101.659 ventanas u32** en argumentos de **46.308 comandos no textuales**, extraídos de la ISO USA original y reparseados como parte de 51.705 comandos, encontró **1 igualdad externa con ID demo1001** y **21 igualdades relativas dentro de demo1001**. Op 0x0A/+0: una coincidencia; 0x01/+0: cinco; 0x02/+2: cuatro; 0x02/+6: doce. **No son saltos demostrados; no autorizan reubicar las 4.524 traducciones aplazadas.** Diez tests sintéticos nuevos PASS local; PPSSPP C NO EJECUTADO. Informe en `docs/F4_R8_REFERENCIAS_DEMO1001_2026-11-23.md` y JSON asociado. T/G/R/Q siguen abiertos; los 42 casos QA siguen NOT_RUN en este relevo.

## R9 — nuevo perfil estático 0x0A y reducción de falsos candidatos (23/11/2026)

En la ISO original A: 862 opcodes 0x0A con 320/862 valores u32 iguales a IDs de script (183 distintos). Un candidato externo concreto, scr01.dsf bloque 20, orden 20, offset 7420, ID de instrucción 818, u32 100100, coincide con script demo1001_00 bloque 758; NO demuestra llamada MIPS. Los 21 matches relativos previos de 0x01/0x02 forman seis patrones de valores frecuentes 23/32/55/85, no 21 saltos. 13 tests sintéticos B locales nuevos PASS; ISO sin modificaciones; PPSSPP C NO EJECUTADO. Nueva matriz Q043 NOT_RUN; 43 casos definidos, universo final aún NO MEDIBLE. Ver docs/F4_R9_PERFIL_OPCODES_2026-11-23.md. Ningún cierre T/G/R/Q, PR #7 sigue DRAFT.

## R10 — cruce real SCRIPT/AISCRIPT y clasificación 0x0B/0x0C (23/11/2026)

Nueva evidencia A: 1.625 IDs SCRIPT, 552 AISCRIPT, seis IDs en común. En 0x0A/0x0B/0x0C se encontraron respectivamente 320/75/86 coincidencias u32 con SCRIPT.TBL, **0** con AISCRIPT.TBL. Los 166 0x0B tienen quinto byte 100 en 112 casos, 101 en 54. No demuestra llamadas/saltos. 15 tests B sintéticos nuevos PASS local, nuevos Q044/Q045 NOT_RUN, total 45 casos definidos. PPSSPP C no ejecutado; sin cambios de ISO ni liberación de los 4524 diferidos. Ver docs/F4_R10_CRUCE_SCRIPT_AISCRIPT_2026-11-23.md.

## R11 — corrección estadística del destino 0x0A (23/11/2026)

**A ISO auténtica:** de 862 argumentos 0x0A, solo 320 coinciden literalmente con IDs SCRIPT.TBL, frente a **860/862 cuando se resta 100**; únicas excepciones 0 y 1. En 0x0B son 75/166 literales frente a **158/166 al restar 100**, únicas excepciones ocho valores 3. En 0x0C **delta 0 gana con 86/102**, por lo que no aplicar regla a ciegas. Esto convierte el candidato `scr01.dsf`/0x0A/offset7420/u32=100100 en posible destino **ID 100000/bloque757**, no ID100100/bloque758. Ambas opciones MIPS NO PROBADAS. Auditor `tools/f4_r11_desfase_ids.py`, 15 tests B sintéticos PASS local y reparseo A real de 51.705 comandos; nuevos Q046/Q047 NOT_RUN, total 47 casos. PPSSPP C ausente, 4.524 variables siguen protegidos. Ver `docs/F4_R11_DESFASE_IDS_2026-11-23.md`.

## R12 — revisión de 0x0C y operandos no coincidentes (23/11/2026)

Evidencia A: ISO original SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`; SCRIPT.DAT/TBL sin modificación. El 0x0A presenta 860/862 operandos que cumplen ID=argumento−100, y solo otros valores 0/1; 0x0B 158/166, otros ocho 3; 0x0C 66/102 y los otros 36 son exactamente 100, en 34 bloques. ID0 no existe. Este resultado corrige la presunción R11 de que 0x0C no compartiría el esquema +100: delta0 obtenía más coincidencias por la repetición de 100. No se ha probado su semántica MIPS. Nuevo auditor y 17 tests sintéticos PASS locales; 49 casos QA definidos, Q048/Q049 NOT_RUN, C PPSSPP no ejecutado, R 4524 cambios variables aún bloqueados. Informe `docs/F4_R12_CANDIDATOS_ESPECIALES_2026-11-23.md`. Cuatro áreas T/G/R/Q siguen abiertas, PR#7 DRAFT.

## R13 — grafo numérico del prólogo y perfil de enlaces (23/11/2026)

ISO original USA intacta, SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. Cinco candidatos bajo regla u32−100: bloque20→757, 757→758, 758→759 (`0x0C`), 758→760 (`0x0A`), 760→761 (`0x0C`). La interpretación literal del enlace desde bloque757 apuntaría a demo1002 bloque764, por lo que el modelo desplazado tiene mayor coherencia estructural, no comprobación MIPS. `0x0A` 86/860 matches de mismo nombre; `0x0B` 142/158; `0x0C` 64/66. Los bloques758/760 tienen `0x0C` con ID candidato y con valor100. Sin PPSSPP C: AppImage ausente, github.com DNS no resuelve; EBOOT protegido ~PSP, BOOT sin código al inicio. Se añadieron `tools/f4_r13_grafo_intro.py`, 18 tests sintéticos locales, reporte `docs/F4_R13_GRAFO_INTRO_2026-11-23.md`; nuevos Q050/Q051 NOT_RUN, total 51 casos, todavía no universo completo. T/G/R/Q abiertos, 4.524 sustituciones variables BLOQUEADAS, PR #7 DRAFT.

## R14 — nueve offsets reales de SCRIPT.DAT y preflight PPSSPP 1.20.4 (23/11/2026)

Manifiesto autentico A de nueve instrucciones originales en offsets `7420,218095,218133,223351,223360,223602,223637,227968,228194`, todos del SCRIPT.DAT DESCOMPRIMIDO, no direcciones RAM. Preflight de PPSSPP 1.20.4: hash ISO/AppImage, PID+starttime+FD+socket y WS version/game.status; versión oficial 1.20.4 devuelve nombre/versión, no PID/ruta. **36 tests B sintéticos locales PASS**. Intento de PPSSPP real rechazado porque falta AppImage, sin informe C falso. Q052/Q053 NOT_RUN; matriz 53 casos, 4.524 eventos diferidos, T/G/R/Q abiertos y PR #7 DRAFT. Informe `docs/F4_R14_SONDAS_Y_PPSSPP_2026-11-23.md`.
