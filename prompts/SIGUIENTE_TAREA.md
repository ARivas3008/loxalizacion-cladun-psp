# CLADUN ES — R25: EJECUTAR PILOTO 3.724 + 1.650, VALIDAR PPSSPP Y ALCANZAR +20 PUNTOS REALES EN ROMHACKING

## 0. Misión ejecutiva y relevo recursivo obligatorio

El objetivo prioritario es transformar la **preparación R24** en **al menos 1.650 integraciones reales verificadas**, elevando romhacking de **3.724/8.248 = 45,1503 %** a **5.374/8.248 = 65,1552 %**, o **+20,00485 puntos**. Nunca publicar ese incremento si el juego no lo demuestra. Ejecución integral y verificable, no solo diseño. Plan de trabajo ×4 sobre los relevos originales: varias tandas largas de construcción, verificaciones positivas/negativas, inspección auténtica, reparación, regresión, CI y publicación. No declarar minutos trabajados ni resultados ficticios.

**Recursividad permanente:** si persiste cualquier pendiente de romhacking o de traducción/gráficos/betatesting, al FINAL sustituir COMPLETAMENTE `prompts/SIGUIENTE_TAREA.md` con R26 autosuficiente, que impondrá la misma recursividad a R27 y sucesivos. No hay promesa de trabajo en segundo plano: completar todo lo posible en el relevo. No ofrecer 100 % sin A/B/C, no reducir la seguridad para cumplir el porcentaje.

Repositorio: `https://github.com/ARivas3008/loxalizacion-cladun-psp`, rama `integracion-eventos-segura-20261120`, PR #7 OPEN/DRAFT, base `revision-manual-dialogos`. Verificar HEAD, PR y CI push/PR **exactos** al comenzar; no merge, no force push. No subir ni publicar ISO, DATA.DAT, FONT.ARC, EBOOT, capturas comerciales, registros RAM, BPS con payload ni fuentes comerciales. Los reportes GitHub contendrán solo SHA, métricas y código propio.

**Clases de evidencia:** A = ISO USA original auténtica privada / análisis y hashes; B = algoritmos, corpus canónico, regresiones, CI sin juego; C = ejecución genuina de PPSSPP oficial v1.20.4, juego realmente representado, evidencia visual A/B/A y comportamiento de eventos. El PASS de B no cierra C. No marcar integrado oficial sin aceptación editorial contextual y PPSSPP C.

## 1. Punto de partida R24 (debe revalidarse)

Fuente 7z aportada en conversación: `Cladun_This_Is_An_RPG_USA_PSN_PSP-PLAYASiA.7z`. ISO original privada USA **305.496.064 bytes**, SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. `PSP_GAME/USRDIR/DATA.DAT`: 349 PSPFS, dentro `SCRIPT.SDT` PSPFS #231 en offset **9652224**, original comprimido **699624 B**, descomprimido **930304 B**, siguiente PSPFS offset **10352128** (slot 699904 B). 8 bloques IMY, 1.625 scripts, **51.705 comandos** (46.308 no textuales + 5.397 textuales), SCRIPT.DAT 633344 B SHA256 `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`, SCRIPT.TBL SHA256 `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`.

**Descubrimiento nuevo A:** la recomposición IMY del SCRIPT original *sin modificar* genera **700.483 B** con roundtrip byte exacto, **579 bytes demasiado grande** para el slot de 699.904 B. No escribir SCRIPT.SDT in-place, incluso para una sola sustitución, a menos que se valide otro compresor que quepa. En R24 se implementó ruta `append-only` que actualiza solo la entrada SCRIPT.SDT y extensión ISO9660, mantiene instrucciones internas con offsets fijos y preserva los otros 347 PSPFS (salvo FONT.ARC experimental). Reproducir `python tools/f4_r24_script_slot_audit.py --iso-original /PRIVADO/Cladun_USA.iso`.

**Traducción R:** oficial intacta **3.724/8.248 (45,15 %)**, diferidas **4.524**. El corpus contiene 2.883 textos SCRIPT que crecen, 1.641 que se acortan y 683 de igual ancho. Las 44 ligaduras sin colisiones generan **2.002 candidatas estrictas**. R24 selecciona determinísticamente 1.650 para formar un mismo piloto con las 3.724 de base; modelo objetivo **5.374/8.248 = 65,1552 %**, pero **NO** se generó ni ejecutó esa ISO combinada en R24, no subió la cifra oficial, no hubo nuevos C.

**Fuente G/F2:** modelo de 19 glifos A1–B3 + 44 ligaduras B4–DF; 2.721 originales preservados; FONT.ARC compacta **144.000 B** dentro del slot de 144.384 B, utilizando **alineación DSARC IMY 16+16 experimental** frente al 512+16 histórico. R23 tiene una ISO privada solo con fuente, ver `docs/R23_FONT_IMY_COMPACT_2026-11-23.md`. **No se sabe si PPSSPP/juego acepta la alineación a 16**. Sin resolverla no se pueden aprobar las ligaduras.

R24 publicó:
- `tools/f4_r24_piloto_1650_ligaduras.py` — **pipeline de un solo candidato**, reconstruye base 3.724 `--event-safe-only`, inserta FONT 44 compacta, añade 1.650 textos de igual longitud, recompone IMY, reubica SCRIPT.SDT `append-only` y verifica ISO9660/PSPFS/eventos. Exige ISO original y ruta candidata nueva fuera del Git, no distribuye.
- `tools/f4_r24_script_slot_audit.py` — auditor real A de compresión no-op y capacidad; rechaza datos distintos.
- `tests/test_f4_r24_piloto_1650_ligaduras.py` y `tests/test_f4_r24_script_slot_audit.py` — regresiones sintéticas y corpus canónico real, incluida cola de 2.002 y 1.650 seleccionables.
- `reports/R24_ROMHACKING_MAS_20_PUNTOS.json`, `docs/R24_ROMHACKING_OBJETIVO_MAS_20_PUNTOS.md`, Q067/Q068 `NOT_RUN`. CI `.github/workflows/validacion-integracion-eventos.yml` contiene prueba estática adicional de 1.650. Validar runs propios antes de afirmar SUCCESS.

## 2. Tanda A — reproducir archivo fuente y producir PILOTO PRIVADO

1. Confirmar actual HEAD, CI, SHA de ISO original. Reproducir auditores R21–R24, 7 FONT DSARC members y 8 bloques SCRIPT. No modificar original.
2. Ejecutar `python tools/f4_r24_piloto_1650_ligaduras.py` sin ISO: exigir 2.002 posibles, 1.650 seleccionables, 5.374 de objetivo, `new_official_integrations = 0`.
3. Ejecutar **realmente**:
```bash
python tools/f4_r24_script_slot_audit.py --iso-original /PRIVADO/Cladun_USA.iso
python tools/f4_r24_piloto_1650_ligaduras.py \
  --iso-original /PRIVADO/Cladun_USA.iso \
  --candidate /PRIVADO/Cladun_R25_5374_PILOTO.iso
```
4. Si falla, depurar la causa específica; añadir test de regresión, corregir sin saltarse las preimágenes, el control de longitud, los 51.705 comandos, los 46.308 no textuales, el hash de SOURCE, `SCRIPT.TBL` byte exacta, los 1.625 offsets, la fuente y los 347 otros PSPFS. Repetir hasta lograr un candidato privado validado o dejar bloqueo preciso.
5. Confirmar contra la ISO original diferencias permitidas: FONT.ARC + SCRIPT.SDT + sus entradas PSPFS + registro de tamaño DATA.DAT y volumen ISO9660. Ningún EBOOT, retrato, tile, sprite o recurso no textual alterado.

## 3. Tanda B — PPSSPP real y validez de 44 ligaduras

Con PPSSPP oficial 1.20.4 autenticado (AppImage histórico SHA256 `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`) probar A/B/A: original USA → piloto 5374 → original USA. Documentar procedencia del proceso: PID/starttime, FD de ISO y WebSocket game.status; captura real de opciones, prólogo, diálogos seleccionados, textos con "es/en/de/er", combate, TUIKA, mapa 2, enciclopedia, iconos, guardar/cargar. Inspeccionar GE/VRAM de FONT/IMY: anchura, tinte, orden de glifos, linebreaks, clipping y que 16+16 realmente funcione.

Si PPSSPP no está disponible, no inventar C y seguir trabajando otras tareas A/B. Si IMY 16 falla, abandonar esa rama de inserción y probar compresión alternativa (histórica 512+16 sin exceso) o reubicación FONT append-only auditable; no romper elementos que siguen a FONT.ARC.

## 4. Tanda C — revisión editorial de 1.650 y evolución futura

Obtener lista exacta de los 1.650 elegidos por el plan, emparejar ID de `traduccion/CLADUN_BORRADOR_ES.csv` con `lectura/CLADUN_GUION_RECONSTRUIDO_COTEJO_ES_EN.txt` y `qa/correcciones_manuales.csv`. Evaluar individualmente por escena, hablante, género, consistencia terminológica, códigos de control, longitud en píxeles, tildes/¿¡, contexto y opción. Registrar una decisión por ID; cambios literarios no se aceptan automáticamente por caber en bytes. Re-ejecutar las guardas si el texto cambia y resolver texto truncado en fuente solo con evidencia. Otras **2.874 diferidas** quedarían si 1.650 se integran de verdad, pero no cambiar contador hasta entonces.

## 5. Tanda D — regresiones totales, actualización honesta de métricas y CI

Ejecutar:
```bash
python -m unittest discover -s tests -v
python tools/f4_r24_piloto_1650_ligaduras.py
python tools/qa_cobertura_4_areas.py
python tools/qa_cobertura_4_areas.py --require-closed  # FALLA mientras hay áreas abiertas
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/cladun-preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/cladun-integrabilidad.json
(cd patcher && go test ./...)
git diff --check
```
Verificar GH Actions **push y PR** del nuevo HEAD con URLs y conclusiones exactas. Mantener el PR #7 DRAFT, sin merge o force push. Actualizar `reports/COBERTURA_4_AREAS.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `docs/ESTADO_CIERRE_4_AREAS.md`, `qa/MATRIZ_BETATESTING_COBERTURA.csv`, reportes A/B/C y código. Repetir ruta Win64 BPS/EXE privada con rollback; probar 0 P0/P1.

**Solo si TODO lo anterior demuestra el resultado en un mismo juego** elevar oficialmente R a `5.374/8.248` y diferidas a `2.874`. Si falla una condición, dejar `3.724/8.248` y explicar exactamente cuántos ensayos sí funcionaron, sin maquillar número. T, G y Q siguen independientes con cierre 100 % por evidencia real. **Al finalizar reemplazar completamente este archivo por R26**, conservando ×4, cuatro tandas, pruebas auténticas y continuación recursiva hasta completar T/G/R/Q sin fingir 100 %.
