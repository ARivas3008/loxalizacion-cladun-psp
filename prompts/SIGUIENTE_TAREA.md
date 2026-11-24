# CLADUN ES — R24 AUTÓNOMO ×4: CIERRE T/G/R/Q, FUENTE 44 IMY COMPACTA Y PPSSPP C

## 0. Trabajo real obligatorio, seguridad y recursividad

Eres equipo sénior de localización española PSP, ingeniería MIPS/PSPFS/DSARC/IMY/CLUT, QA de juego completo, PPSSPP oficial v1.20.4, Windows x64 BPS. **No basta con redactar un plan:** implementar cambios, ejecutar validaciones auténticas, probar regresiones y publicar GitHub únicamente cuando el resultado es seguro. Planifica cuatro tandas sustanciales ×4 (p. ej. 12–24 bloques de hipótesis → reproducción A → implementación → pruebas positivas y negativas → reparación → CI → QA/documentación); no afirmar tiempo trabajado sin evidencia. **Al acabar, si un apartado sigue abierto, SUSTITUIR por completo este archivo con R25 autosuficiente; R25 debe imponer el mismo relevo recursivo a R26, etc., hasta cierre realmente demostrado.**

Repositorio: https://github.com/ARivas3008/loxalizacion-cladun-psp . Rama de trabajo `integracion-eventos-segura-20261120`; base `revision-manual-dialogos`, [PR #7](https://github.com/ARivas3008/loxalizacion-cladun-psp/pull/7) **OPEN/DRAFT**. NO merge, NO force push, no alterar la rama base, no distribuir ISO, DATA.DAT, FONT.ARC, imágenes comerciales, dumps MIPS/VRAM ni parche BPS con assets comerciales. Confirmar HEAD actual y los **DOS** Actions push/PR del propio HEAD antes de trabajar y después de cada commit; no inventar CI, SHA, capturas, tramas o porcentajes.

Evidencias obligatorias: **A** = bytes auténticos de ISO privada, con SHA/medición comprobada; **B** = código, corpus, fixtures, tests y CI sin juego; **C** = ejecución genuina de PPSSPP 1.20.4 con procedencia ISO y observación visual/eventos. A/B **no** sustituyen C. Si PPSSPP no está accesible, avanzar ingeniería A/B y dejar C explícitamente sin pasar.

## 1. Corte R23 verificado

ISO USA original privada, **305.496.064 B**, SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. DATA.DAT contiene PSPFS 349; `SCRIPT.SDT` es registro PSPFS #231; `SCRIPT.DAT` expandido 633.344 B SHA `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`; `SCRIPT.TBL` SHA `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`. 1.625 scripts, 51.705 comandos, 46.308 no textuales. Guardas estrictas `tools/script_event_guard.py`; `--event-safe-only` no se puede desactivar para ahorrar trabajo.

**R23 fuente compacta A/B:** FONT.ARC original 143.888 B SHA `420613ae4a16595b00c75d17bfb86290e57a30419d81ddbc6f245035e63c9805`; PSPFS #308 offset 11.776, siguiente recurso offset 156.160, slot máximo **144.384 B**. Primer prototipo de **19+44** alineado 512+16 daba 145.696 B y excedía 1.312 B; **nuevo piloto compacta 16+16** deja FONT.ARC en **144.000 B**, margen **384 B**, font SHA `1bbdd6cba7490753d6af80ca469262fb2080ab7160fc9a8237bffe3805267af4`; ISO piloto **privada** SHA `f2b27d575b1693a74589459d3ddbfe10349ce06c12474e4fe647ac3061e0b434`. Preservados 2.721 glifos originales + 19 españoles y añadidas 44 ligaduras, 6/6 páginas IMY roundtrip, 348 PSPFS ajenos byte idénticos, ISO9660 intacta. **INCOMPATIBILIDAD POTENCIAL NO DESCARTADA:** el juego puede exigir padding interno de 512 bytes; comprobar en PPSSPP antes de asumir fuente utilizable.

Archivos ya implementados:
- `tools/f4_r21_ligature_font_prototype.py` y `tools/f4_r23_font_compact_candidate.py`.
- `tools/f4_r21_ligature_collision_safe.py` (151 colisiones entre 672 parejas, 521 opciones sin solapamiento), `tools/f4_r21_ligature_overlay.py`, `tools/f4_r21_ligature_capacity.py`, `tools/charset_es.py`, `tools/font_es_narrow.py`, `tools/font_es_guard.py`, `tools/script_event_guard.py`, `tools/f3_referencias_riesgo.py`.
- `tests/test_f4_r23_compact_font_candidate.py`: **12 nuevas regresiones sintéticas**. Commit `b8b5d71c977d9231b073e30d7394e334d64fc246`, CI push `45321731079` SUCCESS, PR `45321738170` SUCCESS.
- `docs/R23_FONT_IMY_COMPACT_2026-11-23.md`; `reports/R23_FONT_COMPACT_STATIC.json`.

**T:** 9.235/9.237 filas escritas (99,98 % solo CSV); 2 originales truncados (TIPATTR 008723/008724), aprobación contextual y traducción visible sin denominador de cierre. **G:** sin inventario completo ni render aprobado al 100 %, sin porcentaje defendible. **R:** 3.724/8.248 = **45,15 %** (4.524 diferidas); 2.002 scripts largos teóricamente ajustables con 44 parejas (61.723 bytes de preimágenes) + 542 con cuatro; no integrados canónicamente, conjunto de cuatro incluido dentro del potencial de 44. Hay otros 841 largos sin ajuste, 1.641 más cortos y 40 excluidos por códigos de control. **Q:** 66 casos definidos en `qa/MATRIZ_BETATESTING_COBERTURA.csv`, Q065/Q066 NOT_RUN, universo final desconocido; C nuevos **0**; **0/4 cierres**. No aumentar R por caber en memoria o una ISO privada no jugada.

## 2. Tanda A — ingeniería PSP, fuentes, ROM y eventos (trabajo extenso)

1. Verificar SHA y parámetros de la ISO USA. **No fiarse de hashes documentados sin revalidación propia**, si hay archivos auténticos disponibles. Inventariar PSPFS 349 y DSARC FONT/SCRIPT y demostrar que todas las posiciones externas al font siguen intactas.
2. Reproducir 19+44 compacta en RAM, **registrando offset/longitud de 7 miembros**, 6/6 IMY, raster 2.721+19, guardar hashes solamente; después generar el piloto fuera del repo. **Si 512+16 requerido runtime**, bloquear totalmente despliegue compacto y analizar compresión IMY o relocalización segura, sin modificar SE.ARC.
3. Diseñar y ejecutar A/B/A con PPSSPP oficial 1.20.4 (AppImage SHA oficial previamente reportado `661c098e6b7f7610171a57b7c533ce8bba6f2312b71e76d61e850461973eba21`): ISO original → piloto → original, PID/starttime+FD+hash ISO y socket WS corroborados, `game.status` NPUH10072, capturas auténticas privadas; probar Options, prólogo, combate, TUIKA, mapa 2, enciclopedia, guardar/cargar, sonido, sprites y retratos. Registrar si la alineación de IMY de **16** funciona realmente antes de activar ligaduras para SCRIPT.
4. Revalidar overlay de **2.002** propuestas de 44 códigos en `tools/f4_r21_ligature_overlay.py --ligatures 44 --iso-original /PRIVADO/USA.iso`, byte-ancho exacto y **51.705 comandos/46.308 no textuales/0 offsets movidos**. Rechazar preimagen, controles, ID, opcode, orden, longitud, solapamiento, caracteres inexistentes. Solo tras C verde aceptar casos con revisión lingüística individual.
5. Para **841 crecientes fuera de capacidad**, **1641 decrecientes** y 40 control cases, investigar opciones reales de texto dinámico: semántica de opcodes 0x0A/0x0B/0x0C y referencias; R11–R16 son coincidencias numéricas, no desensamblaje; proteger 46.308 eventos, 1.625 inicios y todo recurso no textual. No relleno invisible inventado, no offsets desplazados sin mapa MIPS.
6. Validar ruta auténtica BPS parche diferencial y EXE Windows x64 E2E en Windows real, con ISO propia, roundtrip/hash, rollback y negativos. Los CI sin ISO son solo B.

Comandos desde checkout con archivos privados:
```bash
python tools/f4_r21_ligature_collision_safe.py --iso-original /PRIVADO/Cladun_USA.iso
python tools/f4_r21_ligature_font_prototype.py --iso-original /PRIVADO/Cladun_USA.iso --ligatures 44 --member-alignment 16 --require-in-place
python tools/f4_r23_font_compact_candidate.py --iso-original /PRIVADO/Cladun_USA.iso --candidate /PRIVADO/Cladun_PILOTO.iso
python tools/f4_r21_ligature_overlay.py --ligatures 44 --iso-original /PRIVADO/Cladun_USA.iso
python tools/f4_r21_ligature_font_prototype.py --iso-original /PRIVADO/Cladun_USA.iso --ligatures 44 --member-alignment 512 --require-in-place  # DEBE FALLAR
```

## 3. Tanda B — traducción editorial y contexto de juego

Revisar `traduccion/CLADUN_BORRADOR_ES.csv` (inmutabilidad de 9.237 IDs, referencias y glosario), `corpus/confirmados_formato.csv`, `qa/correcciones_manuales.csv`, `qa/decisiones_auditoria.csv`, `lectura/CLADUN_GUION_RECONSTRUIDO_LECTURA_ES.txt`, `traduccion/propuestas/DICTAMEN_64_R19.csv`, `traduccion/propuestas/SCRIPT_POSTPROLOGO_LONGITUD_FIJA_R21.csv`. Dictaminar 2 TIPATTR truncados **sin inventar fuente**, documentar imposibilidad cuando falte el original; contrastar variante inglesa, protagonista/hablantes, singular/plural, tildes, símbolos de ancho/códigos especiales, género, menús y controles. Revisar 2.002 candidatos de ligadura por escena antes de integrar. Las mejoras del menú F1 deben preservarse. Marcar estado editorial objetivo y visible con citas de archivo/captura C privada. Recalcular porcentajes **solo con denominador real y sin confundir borrador terminado con juego integrado**.

## 4. Tanda C — edición gráfica completa

Reproducir primero `tools/r23_pspfs_graphics_inventory.py --iso-original /PRIVADO/USA.iso` y `reports/R23_PSPFS_GRAPHICS_TRIAGE.json`: **349 recursos PSPFS**, 37 MPB + 3 LDT + 1 IDT + 2 ARC gráficas = **43 contenedores de primera pasada**, que **NO** son total de IMY, imágenes con inglés ni porcentaje G. Ejecutar diez tests sintéticos en `tests/test_r23_pspfs_graphics_inventory.py`. Inventariar archivos con texto inglés original dentro de los **349 PSPFS**, GRAPHICS/SYSGRA/ANIME/TUIKA, LDT/IMY/GZIP/CLUT2 y todo atlas restante; priorizar prólogo aún en inglés, Opciones, NOW LOADING, pantallas de combate, segundo nivel, enciclopedia, iconos y tutoriales. Usar `tools/f2_auditar_27_imy_sysgra.py`, `tools/f2_inventario_sysgra_usa.py`, `tools/f3_anime_ldt_r18.py`, `reports/R18_LDT_OVERLAY_2026-11-23.json`, `docs/R19_RELACIONES_PALETAS.md`; las 15 cuádruplas candidatas no son CLUT confirmado. Crear pares original/editado bajo máscaras exactas y reconstrucción reversible, conservar colores, alpha, dimensiones, swizzle, paletas y vecindad; ejecutar GE/VRAM PPSSPP para demostrar función real. Nunca dibujar píxeles y adjudicarlos a capturas del juego. Publicar solo metadatos/código que no incluya obras del juego. Numerador/denominador G debe surgir del inventario exhaustivo aprobado, no estimaciones.

## 5. Tanda D — QA integral, CI, control y cierre

Extender la matriz `qa/MATRIZ_BETATESTING_COBERTURA.csv`: 66 son **casos definidos, no el universo completo**. Introducir rutas de reproducción y save states privados para todo el juego, medir cada capítulo y escenas de eventos. Ejecutar casos en PPSSPP C con ISO SHA, backend y evidencia visual genuinos. Confirmar 19 signos, 44 ligaduras si runtime las aprueba, tildes, saltos, menús, tutorial, mapas, retratos, tiles, combate, prólogo, iconos, textos de cada personaje, segundo nivel, enciclopedia, guardado/carga y Win64 installer. Mantener cero P0/P1, volver a ejecutar pruebas tras cada corrección; no marcar PASS sin hash real + prueba runtime. Validar:

```bash
python -m unittest discover -s tests -v
python tools/qa_cobertura_4_areas.py
python tools/qa_cobertura_4_areas.py --require-closed  # tiene que fallar mientras no haya cuatro cierres
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte /tmp/cladun-preflight.json
python tools/reportar_integrabilidad_es.py --reporte /tmp/cladun-integrabilidad.json
(cd patcher && go test ./...)
git diff --check
```

Actualizar después de hechos (NO por mera redacción): `reports/COBERTURA_4_AREAS.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `qa/MATRIZ_BETATESTING_COBERTURA.csv`, `docs/ESTADO_CIERRE_4_AREAS.md`, informes nuevos, fuentes/tests/CI. Presentar HEAD, commits y IDs precisos de Actions push/PR. Mantener PR DRAFT hasta cierre.

## 6. Condición de 100 % no negociable + recursividad

**T** corpus íntegro y natural, visibilidad total y lectura C de todo texto, cero inconsistencias/censura inventada; **G** inventario completo, todo texto inglés gráficamente convertido y paleta/raster C verificado sin alterar fondos; **R** 8.248/8.248 inserciones **reales** con 0 diferidas, eventos MIPS seguros, 348 assets ajenos byte idénticos, glifos/símbolos correctamente renderizados en C, ISO/BPS/EXE original→parche→rollback E2E; **Q** matriz exhaustiva con todos los casos PASS C, 0 P0/P1, múltiples estados de juego y regresiones. Si falta C, o un denominador es desconocido, área NO CIERRA. Si persisten pendientes, terminar sustituyendo completamente `prompts/SIGUIENTE_TAREA.md` por **R25**, preservando las cuatro tandas, ×4 de trabajo real y generación obligatoria de R26. No prometer ejecución en segundo plano; entregar lo que se compruebe durante el relevo.
