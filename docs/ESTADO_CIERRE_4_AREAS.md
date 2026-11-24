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

## R15 — nueve huellas únicas y escaneo RAM autenticado, sin PPSSPP ejecutado (23/11/2026)

A: ISO original SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`, SCRIPT.DAT 633344 B SHA256 `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`. Las nueve instrucciones R14 admiten cada una una ventana de 32 B única en SCRIPT.DAT; se publican solo SHA256/offsets, jamás bytes comerciales. B: `tools/f4_r15_localizador_ram.py` y 33 pruebas sintéticas nuevas PASS locales, 87 tests del checkout parcial PASS. El lector WS implementa `memory.read` base64 del PPSSPP v1.20.4 y exige ISO/AppImage/PID/FD/socket autenticados, mínimo tres coincidencias y digest completo de SCRIPT.DAT si está continuo. Una coincidencia **no prueba dispatch MIPS**. C: AppImage no descargado (DNS bloqueado); NO RAM/PC ni screenshots. Q054/Q055 NOT_RUN, total 55 casos definidos, universo aún abierto. T/G/R/Q `cierre_100=false`, 4.524 cambios diferidos y PR#7 DRAFT. Ver `docs/F4_R15_HUELLAS_RAM_2026-11-23.md`.

## R16 — carga segmentada

8 cuerpos auténticos, 16 huellas únicas disjuntas, 14 tests nuevos PASS, 101 tests locales parciales PASS. 8/8 cuerpos localizados en memoria artificial, NO PPSSPP. Q056 NOT_RUN; 56 casos definidos. 4.524 diferidos. Ver docs/F4_R16_BLOQUES_RAM_2026-11-23.md.

## R17 — avance de cuatro áreas

A: ANIME000: 192 registros, 231 flujos IMY, 136 tipo 0x00 y 95 tipo 0x02 compatibles con unidad de 4 B y límites verificados; 82/95 resultados distintos entre dos distancias verticales plausibles. TIPATTR 008723/008724 truncados en original; todos los 1625 bloques SCRIPT terminan en opcode 0x08. B: 16 tests nuevos PASS local, CI R16 2/2 SUCCESS. C: ausente. 58 casos definidos, Q057/Q058 NOT_RUN. Sin liberar 4524 ni cerrar áreas. Ver docs/R17_AVANCE_ESTATICO_2026-11-23.md. PR #7 DRAFT.


## R17 — 42 alternativas de longitud fija para demo1001

Se revisaron los 97 registros del prólogo; 42 de los 85 aplazados tienen propuestas españolas de igual tamaño, sin relleno artificial ni códigos de control. Solo se publican las propuestas y metadatos. La prueba independiente en memoria sobre SCRIPT.DAT auténtico conservó 51705 comandos, 46308 no textuales byte exactos y todos los offsets; 1028 bytes de texto distintos. SHA virtual (no archivo): 5e367618ebdbe617e5bf4efd01be21f17d2f14ecd5c6e47275fe2f3727f82037. El borrador canónico y su ancla F3-R5/R6 no cambian; 53 compatibles y 43 diferidos son una proyección si se aceptan las 42. Aplazados oficiales globales: 4524. Sin ISO nueva, PPSSPP ni autorización de inserción. 12 tests sintéticos locales del helper inicial; 28 acumulados R17. Primer commit R17 CI push 45303203679 y PR 45303209991 SUCCESS. La integración final del helper requiere CI propio.

Reproducir desde raíz con `python tools/f3_simular_intro_mismo_tamano.py --propuestas traduccion/propuestas/DEMO1001_LONGITUD_FIJA_R17.csv --iso-original /ruta/privada/Cladun.iso`. Sin --iso-original solo valida ancla de borrador y plan. Revisar contexto, tono, género y términos antes de aceptar; sincronizar CSV/TXT/anclas si cambia el canónico, generar variante privada y ejecutar PPSSPP antes de promover.

## R18 — LDT y 64 alternativas de tamaño fijo


ANIME001.LDT SHA cb7f1354e38ced1a5b19f36c2b45d939e59094e33de901d4b43dc8d65faaa174, 287472 B. ANIME002.LDT SHA e1617dd4aea349f60953db9471e53c1524e9c3184b2566a4a732c3ecc756eec6, 2067856 B. Ambos: cabecera global 16 B, registros de 16 B con longitud excluyendo cabecera, ID único, pares (2,2) en 001 y (0,2) en 002. 24/24 y 39/39 registros consumen exactamente el miembro. 001: 24 IMY tipo 00 modo8, stride64, 1188160 bytes decodificados; colas no clasificadas 14×60 B y 10×62 B, 7 con no ceros. NO confundir con padding, NO descartarlas. 002: cuerpo con 13 u32 (ID duplicado, seis magnitudes, seis offsets); primera tabla offset52 y cinco diferencias 8a/40b/48c/16d/4p. Descriptores 12 B, punteros alineados16, bloque interno longitud almacenada/expandida u32 y GZIP; 57/57 verifican CRC, fin exacto y tamaño igual w*h*bpp/8 (56 de 4 y 1 de 8), total 1714688 B; colas cero entre cargas. No se demuestra función visual, paleta, swizzle o letras; no repack. 18 tests sintéticos locales PASS tras corregir fixture de alineación. Comando: python tools/f3_anime_ldt_r18.py --iso-original /PRIVADO/USA.iso.

### Traducción y ROMhacking
Dictamen de las 42 propuestas R17: 36 aptas para ensayo estático (incluida revisión de 000797), 6 requieren contexto (000780,000785,000827,000839,000855,000873). 28 nuevas propuestas previamente diferidas: 15 demo1001 y 13 scr01. 64 total, 51 de intro y 13 de scr01. Revisión 000859 de género es aparte, misma longitud ya existente; no cuenta como recuperada. No cambia corpus canónico. Si se aceptaran todas las 64, proyección global 4460 diferidas; oficial sigue 4524. Simulación independiente de solo memoria con SCRIPT.DAT/TBL auténticos reparseó 51705 comandos, 46308 no textuales byte exactos, cero desplazamientos y 633344 B, 2007 B cubiertos, 1773 distintos. SHA virtual 8b41c60d6e0def06672398dc4e195bcac5da98de7ba57a8ffe2995cde3f584cd; no es un archivo ni ISO. No se certifica jugabilidad. El wrapper público reutiliza guardas del repo; pendiente CI y ejecución de wrapper en checkout completo con ISO. Reproducir: python tools/f4_r18_propuestas_globales.py --iso-original /PRIVADO/USA.iso (sin ISO: B solamente). CSV traduccion/propuestas/SCRIPT_LONGITUD_FIJA_R18.csv; dictamen traduccion/propuestas/REVISION_DEMO1001_R17_R18.csv. Corrección de género propuesta: 000859 «Tú eres la que siempre es imprudente.»; mantener como revisión no canónica hasta sincronización. Los 2 truncados TIPATTR y la ambigüedad 82 IMY 0x02 no se resuelven. No liberar cambios de longitud variable ni modificar --event-safe-only. Q059/Q060 NOT_RUN; 60 casos definidos. Sin recursos comerciales publicados. 


## Actualización R19 — revisión individual, regresiones y QA

- 64 propuestas comparadas con inglés y borrador: 32 aptas solo para revisión estática, 30 pendientes de contexto y 2 rechazadas estilísticamente (`000023`, `000031`). Ninguna se promocionó a corpus canónico ni se aprobó en PPSSPP. Ver `traduccion/propuestas/DICTAMEN_64_R19.csv`.
- Diez nuevos casos sintéticos de seguridad de eventos en `tests/test_script_event_guard_negative_r19.py`, incluidas cinco mutaciones que se habían ensayado de forma privada. CI de ese commit por verificar; no declarar PASS sin comprobar workflow.
- Nueva hipótesis gráfica: 15 cuádruplas RGBA candidatas en colas ANIME001, 7 registros no nulos, no verificada por GE/VRAM. Casos Q061 y Q062 añadidos como `NOT_RUN` (62 definidos), sin inventar resultados C.
- La simulación privada independiente de 64 cambios mantiene SHA virtual `8b41c60d6e0def06672398dc4e195bcac5da98de7ba57a8ffe2995cde3f584cd`, 51.705 comandos y 46.308 no textuales, offsets sin desplazamiento. No ISO candidata ni parche liberado.

### R19 — verificación CI y relación entre paletas

- Commit b0aa8b4528168906921eb9787ed27e7e98974c30: CI push 45310281300 y PR 45310288041 SUCCESS. 952 tests, 1 omitido, incluidas diez regresiones nuevas de guardas de eventos.
- ANIME001 IDs 6400/6410: 14/14 cuádruplas iguales desplazadas un índice, 0/15 iguales en posición; IDs 6960/6980: 15/15 iguales. Hipótesis de paleta NO validada en GPU; ver docs/R19_RELACIONES_PALETAS.md.
- Matriz Q061/Q062 NOT_RUN, 62 casos definidos; sin nuevo PASS C. Corpus canónico sin cambios; 4524 variables bloqueadas.

## R20 — ROMhacking: auditoría de 4524 diferencias de longitud

- A privada, SCRIPT.DAT original SHA `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`: 5397 comandos textuales, 46308 no textuales, 587 bloques con texto; todos los textos tienen al menos 2 comandos posteriores, mediana 67, máximo 1025. Suma de exposiciones a comandos posteriores 758170 (NO son referencias MIPS verificadas). El padding de 14621 bytes no demuestra seguridad para cambios internos.
- B, clasificación canónica por codec real CP932: 5207 traducciones SCRIPT; 683 igual longitud, 4524 distinta longitud, de las cuales 2883 crecen, 1641 disminuyen y 1971 difieren solo 1–3 bytes. Confirmado en CI `11ed7bd50` (push `45311298393`, PR `45311305834`, SUCCESS, 973 tests, 1 omitido). Después se endureció el fallo por preimagen y CI de `89a63050` (push `45311336942`, PR `45311343751`) SUCCESS.
- B, nueva prueba de compensación de longitudes: aumentar un texto y reducir otro dentro del mismo bloque puede mantener el tamaño y tabla originales, pero mueve comandos internos. `--event-safe-only` debe rechazarla. Seis alternativas nuevas de scr02 son SOLO propuestas no canónicas, sin modificación del borrador.
- R continúa 3724/8248 (45,15 %) integradas; 4524 bloqueadas, sin ingeniería MIPS/PPSSPP C ni BPS/EXE final. No inventar 100 %.

## R21 — análisis exhaustivo de ligaduras, fuente y guardas (continuación)

**A ISO original autenticada, exclusivamente en RAM:** FONT.ARC 143.888 B, 496 B de padding de origen comprobados como cero. De 672 pares de letras minúsculas con métricas ≤15 px, **151 presentan colisiones de píxeles**; se ha corregido el error de la hipótesis inicial. Los 521 restantes son utilizables geométricamente en una celda 16×16, sin prueba de render C. La selección final segura de 44, recomprimida en seis páginas IMY con roundtrip, ocupa 145.696 B: **sobran 1.312 B sobre el slot original, prohibido parchearla in-place**. Selección conservadora de cuatro parejas ('es', 'en', 'de', 'er') recompuesta a **144.384 B exactos** —en el límite, sin margen libre—, 6/6 páginas IMY validadas; aún sin cambio en disco ni prueba PPSSPP.

**B:** 20 propuestas postprólogo con longitud exacta, auditadas en copia RAM A sin desplazamientos, no canónicas; 2.002 candidatas de 44 ligaduras sin solapamientos, 542 candidatas de cuatro ligaduras con bytes de origen ASCII y sin marcadores peligrosos. Ninguna de las 2.544 cifras representa una integración efectiva; los conjuntos se solapan. La estrategia de 44 requiere relocalización append-only nueva; la de cuatro requiere todavía insertar fuente **bajo guardas independientes**, revisar narración y ejecutar A/B/A real.

**C:** 0 nuevas comprobaciones de juego en PPSSPP. Sin dispatcher MIPS confirmado, ISO española nueva, BPS definitivo ni EXE E2E. **R sigue exactamente 3.724/8.248 = 45,15 %, con 4.524 diferidas.** Q063/Q064 agregadas NOT_RUN (64 casos).

Código: `tools/f4_r21_ligature_collision_safe.py`, `tools/f4_r21_ligature_font_prototype.py --ligatures 4 --require-in-place`, `tools/f4_r21_ligature_overlay.py --ligatures 4 --iso-original /PRIVADO/Cladun.iso`. La fuente original no se modifica por los ensayos.

## R23 — fuente IMY compacta de 44 ligaduras, sin cierre ficticio

**ISO original A y candidata privada A (sin PPSSPP):** Se identificó que el primer prototipo de 44 ligaduras requería 145.696 bytes por alinear cada IMY a 512+16. Con alineación experimental **16+16**, y preservando el códec IMY y sus seis roundtrips, el FONT.ARC queda en **144.000 bytes**, dentro de los **144.384 bytes** disponibles, con **384 bytes de margen**. SHA-256 de fuente compacta `1bbdd6cba7490753d6af80ca469262fb2080ab7160fc9a8237bffe3805267af4`. SHA-256 de ISO piloto privada `f2b27d575b1693a74589459d3ddbfe10349ce06c12474e4fe647ac3061e0b434`, mismo tamaño que original. Comprobados **2.721 glifos antiguos + 19 españoles**, **44 ligaduras**, 6/6 IMY, **348 recursos PSPFS ajenos byte idénticos** y tabla ISO9660 conservada. Los archivos comerciales permanecen privados.

**Riesgo no resuelto:** una tabla DSARC correcta y seis descompresiones no certifican que el ejecutable PSP acepte alineación IMY distinta de la histórica de 512 bytes. **No distribuir ni habilitar en patcher canónico** sin ensayo PPSSPP real A/B/A, y no atribuir 2.002 textos candidatos de ligaduras como cambios integrados. La fuente con 4 ligaduras y alineación histórica sigue siendo alternativa sin prueba C.

**Código/CI:** `tools/f4_r21_ligature_font_prototype.py` incorpora `--member-alignment 16` experimental, `tools/f4_r23_font_compact_candidate.py` crea una ISO de ensayo en ruta privada NUEVA con guardas 349 PSPFS, y `tests/test_f4_r23_compact_font_candidate.py` añade 12 pruebas sintéticas positivas y negativas. CI en commit `b8b5d71c977d9231b073e30d7394e334d64fc246`: push `45321731079` **SUCCESS**; PR `45321738170` **SUCCESS**. Informe `docs/R23_FONT_IMY_COMPACT_2026-11-23.md` y `reports/R23_FONT_COMPACT_STATIC.json`.

**Métricas honestas, tras R23:**
- T: **9.235/9.237** entradas españolas en CSV (**99,98 % de borrador**); 2 originales truncados; juego traducido y calidad contextual final **sin medición de cierre**.
- G: inventario/render/aprobación total no realizado; **sin denominador para un porcentaje de gráficos completo**.
- R: **3.724/8.248 = 45,15 %** sustituciones históricas aceptadas en candidato parcial; **4.524 diferidas**; 2.002 potenciales con ligaduras 44, pero **0 nuevos aceptados canónicamente**. Interpretación MIPS y validación dinámica siguen bloqueadas.
- Q: **66 casos definidos**, Q065/Q066 `NOT_RUN`; la matriz completa de juego aún no está definida ni ejecutada; **0 nuevos PASS C**. Porcentaje de campaña integral **sin medir**.

**Cierre real: 0/4 áreas.** PR #7 sigue DRAFT, sin merge ni force push, sin BPS/EXE final. El sucesor R24 debe validar compatibilidad DSARC de 16 bytes en PPSSPP oficial y ampliar el trabajo T/G/R/Q sin falsear los indicadores.

### R23 adicional — primer inventario gráfico autenticado de PSPFS

Se releyeron los **349** registros PSPFS de la ISO USA original y se clasificaron por extensión: **187 DMD, 65 DAT, 50 SPS, 37 MPB, 3 ARC, 3 LDT, 1 IDT, 1 SDT, 1 DAT2 y 1 TXT**. Las familias gráficas de **primera pasada** suman **43 contenedores candidatos**: 37 MPB + 3 LDT + 1 IDT + 2 ARC (FONT.ARC y SYSGRA.ARC). `SE.ARC` es independiente y se excluye de ese subconjunto. Estos **43 NO constituyen el número total de imágenes**, pues hay IMY e imágenes anidadas y todavía no se ha demostrado cuáles muestran texto inglés; no se les atribuye un porcentaje de traducción gráfica. Informe `reports/R23_PSPFS_GRAPHICS_TRIAGE.json`; generador seguro `tools/r23_pspfs_graphics_inventory.py --iso-original /PRIVADO/USA.iso`; diez tests sintéticos `tests/test_r23_pspfs_graphics_inventory.py`. Mantener G ABIERTA sin inventar PASS visual C.

## R24 — objetivo +20 puntos de ROMhacking; pipeline piloto implementado, NO 65,15 % oficial

A: se extrajo la ISO original USA del 7z privado del usuario con SHA-256 autenticado `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. `SCRIPT.SDT` tiene **699.624 bytes comprimidos** y solo **699.904 B de slot**; recomprimir incluso el flujo auténtico sin cambios produjo **700.483 bytes**, con roundtrip completo de 8 bloques IMY pero **579 B de exceso**. Por tanto, prohibido parchar ese slot in-place con dicho recompresor; la ruta viable de experimento es `append-only` con verificación ISO9660/PSPFS/DSARC. Reparseo independiente de los **51.705 comandos**, **46.308 no textuales**, **1.625 scripts**, hash originales de SCRIPT.DAT/TBL iguales a baseline.

B: `tools/f4_r24_piloto_1650_ligaduras.py` implementa una combinación en la misma ISO privada de las **3.724 históricas** y **1.650** candidatas estrictas de 44 ligaduras; utiliza las guardas de fuente, corpus, preimágenes, offsets, eventos, aislamiento PSPFS, extensión append-only y archivos privados sin sobrescritura. **1.650/8.248 = 20,00485 puntos** de mejora potencial, llegando a **5.374/8.248 = 65,1552 % SOLO COMO OBJETIVO DE PILOTO**. Se añadieron regresiones y un auditor del slot auténtico `tools/f4_r24_script_slot_audit.py`. Informe `reports/R24_ROMHACKING_MAS_20_PUNTOS.json`, explicación `docs/R24_ROMHACKING_OBJETIVO_MAS_20_PUNTOS.md`.

C: no hubo PPSSPP oficial 1.20.4 en este contenedor, ni ISO combinada 3.724+1.650 ejecutada, ni revisión editorial y dinámica de los 1.650 textos. No aumentar numerador oficial; **romhacking sigue 3.724/8.248 = 45,15 %, 4.524 pendientes**, T/G/Q también siguen abiertos. QA Q067/Q068 añadidos `NOT_RUN`, total **68 casos**, sin nuevos PASS C. PR #7 continúa en borrador. R25 debe producir y comprobar el piloto experimental completo, probar la fuente compacta de 44 ligaduras en PPSSPP real y liberar los 1.650 solo tras aceptación auténtica, sin falsos avances.

## R25 — objetivo experimental acumulado 85,16 % de ROMhacking (NO cierre C)

A: nueva comprobación independiente de la ISO USA original SHA `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`: PSPFS 349; `SCRIPT.SDT` 8 IMY/930.304 B, `SCRIPT.DAT` 633.344 B, `SCRIPT.TBL` 52.016 B. Reparseados **1.625 scripts, 51.705 comandos, 46.308 no textuales y 5.397 textuales**; sin modificar fuente ni ejecutar PPSSPP en esta fase.

B: se corrigió el auditor final del piloto R24 para contrastar los recursos ya traducidos contra la **base 3.724**, no erróneamente contra la ISO inglesa. Nuevo `tools/f4_r25_piloto_85pct.py` para preparar una **única candidata privada** con **3.724 históricos + 2.002 textos crecientes mediante ligaduras + 1.298 textos cortos mediante relleno experimental**, total objetivo **7.024/8.248 = 85,1600 %**. Los 2.002 proceden de 44 ligaduras sin colisiones; los 1.298 se seleccionaron entre 1.345 textos de menor riesgo por longitud (máximo 7 espacios finales; 3.899 espacios en total), pendientes de demostrar que no generan wrap, espacios visibles o clipping. Las **3.300** nuevas filas están identificadas individualmente en `traduccion/propuestas/R25_COLA_CONJUNTA_3300.csv`; comparadas contra el corpus canónico por tests B. CI ejecuta comprobación explícita del **85,16 % como meta, no avance oficialmente validado**. Informe `reports/R25_ROMHACKING_OBJETIVO_85_PCT.json`; instrucciones `docs/R25_ROMHACKING_META_85_2026-11-24.md`.

C: sin generación/ejecución completa de la ISO conjunta de 7.024, sin PPSSPP oficial 1.20.4, sin aprobación contextual de las 3.300, sin validación visual del relleno ni del FONT compacto (DSARC 16+16). QA añadidos Q069/Q070 `NOT_RUN`, total **70 casos definidos**; 0 nuevas pruebas C aprobadas.

**Contador oficial sigue en 3.724/8.248 = 45,15 %; 4.524 diferidas.** 65,15 % (R24) y 85,16 % (R25) siguen siendo objetivos experimentales no cerrados. No reducir pruebas ni vender una estadística teórica como juego terminado. PR #7 OPEN/DRAFT, no merge ni force push, fuente comercial no publicada. Continuar con `prompts/SIGUIENTE_TAREA.md` R26.

## R26 — intento de cierre integral de ROMhacking 8.248/8.248: plan B 100 %, NO ejecución C

**A**: ISO original USA privada SHA `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f` reabierta sin editar; SCRIPT.DAT 633.344 B, SCRIPT.TBL 52.016 B, 1.625 scripts, 51.705 comandos (46.308 no textuales, 5.397 textuales), 190 opcodes textuales vacíos, 14.621 bytes de padding. Cotejados 586 script IDs del corpus con la tabla de la ISO real.

**B**: el planificador canónico de `integrar_parche_seguro.py` confirma **8.248 sustituciones efectivas**: **4.900** en SCRIPT.DAT (**4.524** de longitud variable + **376** de ancho igual) y **3.348** en otros recursos; **307** textos SCRIPT de ancho igual ya tienen bytes idénticos y no necesitan sustitución. El full script sin ligaduras aumenta 9.694 B, pero **253 bloques** desbordan su padding local por **8.077 B acumulados** (máximo 1.459). Con 44 ligaduras seguras + acortamientos sin relleno, mejora el límite de capacidad a **29 bloques** desbordados por **215 B** (máximo 34), no a 0. Herramienta `tools/r26_script_full_capacity_audit.py` y pruebas B; informe `reports/R26_ROMHACKING_FULL_8248_DIAGNOSTICO.json`.

**Piloto de reinserción completa programado, NO construido aquí**: `tools/r26_piloto_total_8248_privado.py`, llama al integrador real en modo experimental de longitud variable, exige ISO propia válida, destino privado nuevo, autorización explícita de riesgo, comparación de 46.308 comandos no textuales y 8.248 sustituciones. Advierte y audita **desplazamiento de comandos y 1.625 inicios de script**; no puede declarar funcionamiento MIPS ni 100 % oficial sin localizar referencias a offsets y hacer A/B/A C. El original `EBOOT.BIN` empieza con cabecera cifrada `7E505350 (~PSP)`; no hay desensamblado autentificado ni PPSSPP oficial 1.20.4 disponible en el entorno. Documentación completa `docs/R26_ROMHACKING_100_AUDITORIA_2026-11-24.md`.

**C/QA**: no hubo candidato ISO completo ni PPSSPP A/B/A; tampoco revisión contextual de los 8.248, ni E2E Windows. Nuevos casos Q071–Q075 **NOT_RUN**, matriz total **75 casos**, ningún PASS C nuevo. Por eso **romhacking oficial NO se incrementa: 3.724/8.248 = 45,15 %, 4.524 pendientes**. El código ofrece plan B para las 8.248, NO un parche español final 100 %. PR #7 sigue OPEN/DRAFT; no merge, force push ni binarios comerciales publicados. La siguiente tarea recursiva R27 debe priorizar ISO privada completa, ingeniería MIPS de referencias, solvencia de 29 bloques y PPSSPP real, antes de elevar cifras.
