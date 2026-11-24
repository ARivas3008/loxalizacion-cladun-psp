# CLADUN ES — R27 AUTÓNOMO ×4: DE PILOTO ESTÁTICO DE 8.248 TEXTOS A ROMHACKING 100 % REAL, SIN ROMPER EVENTOS

## 0. Encargo y recursividad obligatoria

Actúa como equipo sénior de ingeniería inversa PSP MIPS, fuentes CP932/IMY/CLUT/GE, ISO9660/PSPFS/DSARC, traductores editores, PPSSPP 1.20.4 oficial y QA de videojuegos. **Ejecuta los diagnósticos y cambios concretos**, no te limites a una lista de consejos. Completa tandas extensas ×4 y múltiples regresiones, no tareas breves de seis minutos. Si un recurso no está disponible, implementa y valida lo demás con evidencia real y registra el bloqueo, sin inventar tiempos, PCs MIPS, direcciones RAM, comandos GPU, capturas ni pruebas de PPSSPP.

**Objetivo del usuario: ROMhacking 100 % real y seguro.** El planificador canónico ahora demuestra que existen **8.248 cambios de bytes elegibles**, pero **la cifra oficialmente probada sigue siendo 3.724/8.248 = 45,1503 %; 4.524 siguen sin integración C**. Los objetivos R24 5.374/8.248, R25 7.024/8.248 y el R26 8.248/8.248 son **pilotos B/hipótesis**: ninguno autoriza elevar las cifras oficiales sin un mismo binario autenticado y ejecución real. El nuevo R26 ofrece un generador experimental de ISO con 8.248 cambios de longitud variable, pero desplaza offsets de instrucciones y no se ha ejecutado sobre la fuente con PPSSPP. **Nunca confundir 100 % de planificación con 100 % funcional.**

**Al terminar este relevo sustituye COMPLETAMENTE `prompts/SIGUIENTE_TAREA.md` por R28 autónomo** con resultados, métricas, fallos, rutas y comando de reproducción, y exige la misma reescritura recursiva R29, R30... hasta cerrar T/G/R/Q con A/B/C reales. No afirmar que el siguiente relevo se ejecutará automáticamente en segundo plano.

Repositorio: `https://github.com/ARivas3008/loxalizacion-cladun-psp`; rama `integracion-eventos-segura-20261120`, PR #7 OPEN/DRAFT, base `revision-manual-dialogos`. Al iniciar verificar HEAD exacto, push CI y PR CI de ese HEAD, estatus del PR y estado de 4 áreas. No merge, no force push ni binarios comerciales en Git. Se dispone de archivo original aportado por usuario `Cladun_This_Is_An_RPG_USA_PSN_PSP-PLAYASiA.7z`. ISO legal USA SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`, 305.496.064 bytes. En R26 se extrajo y auditó solo en entorno privado. No presuponer que rutas `/mnt/data/cladun_private/source_usa.iso` sobrevivan; volver a autenticar. No publicar ISO, DATA.DAT, FONT.ARC, EBOOT ni parchadores que incluyan activos propietarios.

**Evidencia A:** ISO original autenticada, hashes + reconstrucción privada auditada. **B:** corpus, algoritmos, CI y escenarios sintéticos. **C:** juego real en PPSSPP oficial v1.20.4, con PID/starttime, FD de ISO, backend, capturas y A/B/A. No convertir un PASS B en C. El cierre requiere 0 bugs P0/P1, pruebas con saves/campaña y aprobación textual contextual.

## 1. Lectura obligatoria y material técnico

Leer ANTES de cambiar:

- `docs/R26_ROMHACKING_100_AUDITORIA_2026-11-24.md`, `reports/R26_ROMHACKING_FULL_8248_DIAGNOSTICO.json`, `reports/R26_29_BLOQUES_PRIORIDAD.csv` (**29 índices/IDs de script, faltan solo 215 B de espacio en la mejor hipótesis 44 ligaduras**).
- `tools/r26_script_full_capacity_audit.py` (coteja original ISO+5207 traducciones frente a 1625 scripts), `tools/r26_piloto_total_8248_privado.py` (genera SIEMPRE candidato privado de 8248, solicita explícitamente riesgo por eventos desplazados, no permite lanzamiento).
- `tools/r26_auditar_reubicacion_eventos_total.py` (recompone los 4.900 comandos de SCRIPT **solo en memoria**, compara 51.705 offsets y 46.308 no textuales, exige declarar desplazamientos; todavía sin MIPS/C).
- `tests/test_r26_script_full_capacity_audit.py`, `tests/test_r26_piloto_total_8248_privado.py` y `.github/workflows/validacion-integracion-eventos.yml`.
- `tools/integrar_parche_seguro.py`, `tools/script_event_guard.py`, `tools/imy_repack_safe.py`, `tools/extract_cladun.py`, `tools/iso_guard_global.py`, `tools/generar_parche_bps.py`.
- `tools/f4_r25_piloto_85pct.py`, `tools/f4_r24_piloto_1650_ligaduras.py`, `tools/f4_r21_ligature_collision_safe.py`, `tools/f4_r23_font_compact_candidate.py`.
- `traduccion/CLADUN_BORRADOR_ES.csv`, `traduccion/propuestas/R25_COLA_CONJUNTA_3300.csv`, glosario, correcciones manuales y guion contextual, `qa/MATRIZ_BETATESTING_COBERTURA.csv` (75 casos, Q071–Q075 recién añadidos NOT_RUN).
- `reports/COBERTURA_4_AREAS.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `docs/ESTADO_CIERRE_4_AREAS.md`.

**A autenticada R26:** `PSP_GAME/USRDIR/DATA.DAT` 349 PSPFS. `SCRIPT.SDT` 8 bloques IMY, decodifica 930.304 B; `SCRIPT.DAT` 633.344 B SHA `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`; `SCRIPT.TBL` 52.016 B SHA `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`. 1.625 scripts, 51.705 comandos, 46.308 no textuales, 5.397 textuales (5.207 con texto, 190 vacíos), 14.621 B de padding. Se cotejaron 586 script IDs de corpus con registros originales.

**B planificador corregido, CI verificado:** de 9.237 registros canónicos, `plan_rows` produce exactamente **8.248 cambios de bytes**, de los cuales **4.900 son SCRIPT** (**4.524** de longitud variable y **376** igual longitud) y **3.348 otros recursos**. En SCRIPT hay otros **307 textos cuyo inglés/español son ya idénticos**. Esta era la causa de la discrepancia del primer test del R26; está corregida, y los tests B preservan estos valores. No presuponer 5.207 cambios binarios de SCRIPT.

**A/B riesgo de capacidad:** español directo crece **17.108 B**, se acorta **7.414 B**, neto **+9.694 B**; aunque hay 14.621 B globales de padding, **253 de 1.625 bloques** superan su padding local por **8.077 B agregados** (máximo 1.459). Con 44 ligaduras collision-free y textos cortos **sin espacios finales**, se ahorra 14.076 B teóricos, neto **−4.382 B**; solo **29** bloques no caben (**215 B** total, máximo 34). Es un límite inferior de capacidad, NO una solución MIPS: cambiar longitudes puede mover offsets incluso si cabe el bloque.

**A juego binario PSP:** `EBOOT.BIN` tiene magic `7E505350` (~PSP cifrado). R26 no descifró ni desensambló el motor ni demostró saltos. El clásico `SCRIPT.SDT` de 699.624 B tiene slot 699.904 B y recomprimirlo sin cambiar texto dio 700.483 B (+579 B de desbordamiento). No sobrescribir: usar append-only con aislamiento de imágenes y metadatos ISO9660/PSPFS.

## 2. Tanda A — ejecutar YA el prototipo total 8.248 y cerrar diferencias binarias

1. Conseguir checkout íntegro y el 7z propio del usuario (ISO fuera del repo). Calcular SHA antes de nada. Reproducir A del auditor; guardar informe por hashes sin texto ni archivos del juego.
2. Reproducir la planificación B:
```bash
python tools/r26_script_full_capacity_audit.py
python tools/r26_piloto_total_8248_privado.py
python tools/r26_auditar_reubicacion_eventos_total.py
python -m unittest discover -s tests -p 'test_r26*' -v
```
3. Antes del binario exportar **manifiesto de revisión de los 8.248 IDs** sin contenido comercial:
```bash
python tools/r26_piloto_total_8248_privado.py \
  --manifest /PRIVADO/R27_MANIFIESTO_8248_REVISION.json
```
Exigir **4.524 SCRIPT_VARIABLE + 376 SCRIPT_FIXED + 3.348 OTHER_RESOURCE**; cada ID con QA `NOT_RUN`, editorial `PENDIENTE_CONTEXTUAL`, integración canónica `NO` y MIPS `UNVERIFIED` para los que mueven longitud. No aprobarlos por generar el JSON.

4. Construir **un único candidato privado no publicable**, aceptando explícitamente solo el riesgo experimental:
```bash
python tools/r26_script_full_capacity_audit.py \
  --iso-original /PRIVADO/Cladun_USA.iso
python tools/r26_auditar_reubicacion_eventos_total.py \
  --iso-original /PRIVADO/Cladun_USA.iso
python tools/r26_piloto_total_8248_privado.py \
  --iso-original /PRIVADO/Cladun_USA.iso \
  --candidate /PRIVADO/Cladun_R27_8248_RIESGO_EVENTOS.iso \
  --i-accept-experimental-moving-event-offsets
```
5. Si alguna guarda rechaza construcción (IMY final, DSARC, capacidad, redimensionamiento, condición CLI), diagnosticar y corregir en el código con test positivo/negativo, sin deshabilitar protección. Exigir 8.248 cambios reales, 4.900 SCRIPT, 46.308 nontext byte exact, 51.705 opcodes/IDs/orden, 349 PSPFS y recursos no textuales byte-identicos, original inalterado. Registrar **exactamente** los comandos/inicios que se desplazaron. Mantener el candidato fuera de Git y no dar instrucciones de distribuir.

## 3. Tanda B — resolver específicamente los 29 bloques y TODOS los punteros MIPS

A partir de `reports/R26_29_BLOQUES_PRIORIDAD.csv`, trabajar cada uno de los 29 (script id, filename, padding, déficit exacto). Prioridades: `battle_info.dsf` id 500101 **34 B** e id 540 **9 B**, `end04_syabet.dsf` 145501 **25 B**, `demo1005_00.dsf` 300512 **20 B**, `demo1504_01.dsf` 150401 **16 B** y otros de esa escena. No asignar parches por conjeturas: repetir encoders, simular restricciones y si una compresión cabe, validar tablas y offsets.

**Problema esencial:** incluso un buen codebook no asegura que 51.705 offsets permanezcan inmutables. Identificar cómo el motor PSP lee SCRIPT.TBL, usa instruction IDs y calcula saltos, callbacks, referencia a entradas desde BOOT/EBOOT u otros recursos. Desencriptar/disensamblar el ejecutable solo con binario privado y herramientas legítimas; instrumentar PPSSPP 1.20.4 para observar llamadas y referencias con trazabilidad PC MIPS comprobada. No inventar direcciones, no declarar seguridad porque los opcodes no textuales son iguales. Construir old→new relocation map exacto y reparaciones cuando se demuestre la semántica. Añadir auditor de referencias y pruebas negativas; cerrar el último byte de déficit con método reproducible sin afectar recursos.

En paralelo comprobar 44 ligaduras de atlas FONT: 19 signos A1–B3, ligaduras B4–DF, 2.721 originales, FONT compacto 144.000 B en slot 144.384 B, alineación 16+16 no probada por PSP. Resolver/runtime antes de tratar la compresión de 29 como segura. Alternativa de texto de longitud variable debe preservar control de eventos y renderización.

## 4. Tanda C — campaña PPSSPP A/B/A y 8.248 textos realmente aprobados

Probar **original USA → ISO privada 8248 → original USA** con PPSSPP oficial 1.20.4 autenticado (binario SHA, PID/starttime, FD ISO, backend, WebSocket game.status, timestamp). Verificar menú de opciones, tildes y símbolos sin desplazamiento, tutorial/prólogo, mapas 1–2+, combate TUIKA, encargos, escenas con rutas cruzadas, retratos, sprites, iluminación, inventario, enciclopedia, créditos, saves/load y regreso a partidas. Registrar capturas reales por pantalla y IDs, datos GE/VRAM solo si se observan. Ejecutar QA Q001–Q075 + expansión por todas las escenas reales, incluir 0 P0/P1, 8.248 correspondencias de texto según contexto, género, glosario y fluidez. No inventar capturas o afirmar 100 % por una pantalla.

Solo si 8.248 pasan técnica+edición+C y validación BPS/EXE Windows x64 privada, **elevar el contador oficial a 8.248/8.248 (100 %)**. Si hay fallos C o falta PPSSPP, dejar 3.724/8.248 (45,15 %) o sumar únicamente las aprobadas individualmente. Las dos filas originales truncadas del corpus necesitan informe de reconstrucción contextual aparte y no se confunden con este denominador. T/G/Q siguen separados.

## 5. Tanda D — pruebas, CI, informes y obligación R28

```bash
python -m unittest discover -s tests -v
python tools/r26_script_full_capacity_audit.py
python tools/r26_piloto_total_8248_privado.py
python tools/qa_cobertura_4_areas.py
python tools/qa_cobertura_4_areas.py --require-closed  # falla hasta cierre real
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/reportar_integrabilidad_es.py --reporte /tmp/r27-integrabilidad.json
(cd patcher && go test ./...)
git diff --check
```

Revisar push+PR CI para **HEAD exacto**, no esconder fallas intermedias, mencionar las reparadas. Actualizar `reports/R26_ROMHACKING_FULL_8248_DIAGNOSTICO.json` o R27, `reports/R26_29_BLOQUES_PRIORIDAD.csv` con decisiones/soluciones **solo si se prueban**, `reports/COBERTURA_4_AREAS.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `docs/ESTADO_CIERRE_4_AREAS.md`, `qa/MATRIZ_BETATESTING_COBERTURA.csv` y documentos por A/B/C. Mantener PR #7 DRAFT, sin merge ni force push, no subir ISO ni archivos comerciales. BPS seguro con hashes/rollback solo tras pruebas runtime.

**Al finalizar, REEMPLAZAR TODO este archivo por R28 con estos mismos principios y recursividad R29**, sin prometer trabajo futuro automático ni permitir porcentajes inventados.
