# CLADUN ES — R26 RELEVO AUTÓNOMO ×4: CONSTRUIR 7.024 SUSTITUCIONES EN UNA ISO REAL Y VALIDAR 85,16 % EN PPSSPP

## Misión, prohibiciones y obligación recursiva permanente

Eres equipo sénior de romhacking PSP MIPS/PPSSPP 1.20.4, ISO9660/PSPFS/DSARC, IMY, CP932/atlas 4bpp/CLUT, traducción contextual y QA. No te limites a redactar planes: ejecuta código, repara fallos, genera pruebas A/B/C auténticas, trabaja en GitHub. Prohibido inventar capturas, comandos GE, direcciones RAM, hashes, porcentajes oficiales, tiempos de ejecución, tests o publicaciones.

**Objetivo del usuario:** avanzar otros **20 puntos porcentuales** respecto al objetivo experimental anterior de 65,1552 %. Intentar demostrar un **mismo candidato privado** de **7.024/8.248 = 85,1600 %**, sin regresiones, acumulando 3.724 anteriores + 2.002 crecientes con ligaduras + 1.298 cortos. La cifra **oficial** sigue siendo **3.724/8.248 = 45,1503 %**, **4.524 diferidas**, pues ni R24 ni R25 han ejecutado/validado visualmente el candidato total. **No modificar el porcentaje oficial** hasta demostrar todas las entradas en el juego y contar aprobaciones editoriales auténticas, caso por caso.

Repositorio: `https://github.com/ARivas3008/loxalizacion-cladun-psp`; rama `integracion-eventos-segura-20261120`; PR #7 OPEN/DRAFT, base `revision-manual-dialogos`. Verificar HEAD y CI push+PR **del mismo HEAD** antes de empezar; no hacer merge o force push. Fuente original aportada por usuario: `Cladun_This_Is_An_RPG_USA_PSN_PSP-PLAYASiA.7z`, extraer solo privadamente. ISO USA SHA256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`, 305.496.064 bytes; en el entorno del relevado R25 estuvo en `/mnt/data/cladun_private/source_usa.iso`. **No asumir esa ruta si se reinicia el contenedor**. No publicar ISO, DATA.DAT, FONT.ARC, EBOOT, BPS comercial, contenido de juegos o capturas falsas. GitHub solo código propio, informes por hashes y tablas de IDs/offsets sin diálogos.

Clasificar evidencias: **A** original ISO auténtica / inspección y candidato binario privado autenticado; **B** corpus/sintéticos/CI sin ISO comercial; **C** ejecución en PPSSPP oficial 1.20.4, framebuffers verdaderos, eventos y A/B/A. Un PASS CI no es un PASS C. Privacidad de datos de usuario.

**RECURSIVIDAD INNEGOCIABLE:** al finalizar sustituye por completo `prompts/SIGUIENTE_TAREA.md` con R27 detallado, incluyendo recuentos comprobados, nuevas rutas, fallos, comandos de reproducción, y la misma instrucción recursiva hasta T/G/R/Q al 100 % real. Trabajar en tandas extensas ×4, múltiples experimentos y regresiones por relevo, no seis minutos por mensaje, sin declarar duraciones inventadas. Ejecutar ahora todo lo posible; no prometer trabajo posterior asíncrono.

## 1. Lectura obligatoria y punto técnico de partida

1. `docs/R25_ROMHACKING_META_85_2026-11-24.md` (resumen).
2. `reports/R25_ROMHACKING_OBJETIVO_85_PCT.json`, `reports/COBERTURA_4_AREAS.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`.
3. `tools/f4_r25_piloto_85pct.py` (piloto binario completo B), `tools/f4_r24_piloto_1650_ligaduras.py` (validación final corregida **comparando contra base traducida 3724**, no contra ISO inglesa), `tools/f4_r23_font_compact_candidate.py`, `tools/f4_r21_ligature_overlay.py`, `tools/integrar_parche_seguro.py`, `tools/script_event_guard.py`, `tools/imy_repack_safe.py`, `tools/extract_cladun.py`.
4. `traduccion/CLADUN_BORRADOR_ES.csv` (SHA git blob canónico fijado), `traduccion/propuestas/R24_COLA_EDITORIAL_1650.csv`, `traduccion/propuestas/R25_COLA_EDITORIAL_1298.csv`, `traduccion/propuestas/R25_COLA_CONJUNTA_3300.csv`; **todos los 3.300 IDs aún con revisión contextual PENDIENTE, PPSSPP NOT_RUN, canónico NO**.
5. `tests/test_f4_r25_piloto_85pct.py`, `tests/test_f4_r24_piloto_1650_ligaduras.py`, `tests/test_f4_r24_script_slot_audit.py`, `.github/workflows/validacion-integracion-eventos.yml`.
6. `docs/R23_FONT_IMY_COMPACT_2026-11-23.md`: 19 + 44 glifos y FONT.ARC 144.000 B; PSPFS 144.384 B; DSARC IMY 16+16 **experimental no probado por el motor**.

R25 sí reabrió y releyó físicamente la ISO original, validando 349 PSPFS, SCRIPT.SDT 8 bloques IMY, SCRIPT.DAT **633.344 B** SHA `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`, SCRIPT.TBL **52.016 B** SHA `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`, **1.625 scripts**, **51.705 opcodes**, **46.308 no textuales**, **5.397 textuales**, último bloque 633.008. No mutó ISO original.

Límite de compresión R24: SCRIPT.SDT almacenado 699.624 B, slot hasta siguiente PSPFS 699.904 B; recomprimir el flujo **idéntico** con el encoder actual produce 700.483 B, **579 B de desbordamiento**. Reubicar `append-only` mediante PSPFS/ISO9660, jamás sobrescribir in-place solo por desear llegar a 85 %. Validar que todos los recursos no textuales mantengan bytes y offset exactos.

## 2. Tanda A — ejecutar DE VERDAD el piloto R25 ISO A

**No confundir pruebas B con ejecución auténtica A.** Usar checkout de GitHub completo y propia ISO obtenida legítimamente. Repetir:

```bash
python -m unittest discover -s tests -p 'test_f4_r25*' -v
python tools/f4_r25_piloto_85pct.py
python tools/f4_r24_script_slot_audit.py --iso-original /PRIVADO/Cladun_USA.iso
python tools/f4_r25_piloto_85pct.py \
  --iso-original /PRIVADO/Cladun_USA.iso \
  --candidate /PRIVADO/Cladun_R26_7024_PILOTO.iso
```

El programa debe: verificar SHA, leer corpus 9.237 y planes 2.002+1.298; chequear **3.300** preimágenes en script original y 51.705 comandos exactos; construir una base nueva en ISO privada con **3.724** cambios, no una segunda ISO inconexa; cambiar únicamente FONT.ARC bajo protección de slot; editar 3.300 spans de **igual longitud** sobre la **misma base** sin desplazar scripts; conservar SCRIPT.TBL idéntica; comprimir con IMY roundtrip; reubicar SCRIPT.SDT append-only; comparar **347 recursos** externos contra la base ya traducida y validar cambios fuente→base autorizados; hashes finales de cada etapa, pruebas negativas de mutación y sin regeneración de capturas. Reportar candidato privado y hashes sin compartirlo.

**Depurar cualquier fallo** del pipeline; una herramienta nueva sin ejecución real no autoriza afirmar 85 %. Vigilar que el font patch reduzca 144.352→144.000 bytes y borre solo 352 B de la antigua fuente sin afectar SE.ARC; R25 ya agregó `font_allowed_span`. No aceptar escritura de archivos en repositorios. R25 corrigió `unchanged_resources_against_baseline` para comparar archivos ya traducidos contra la candidata base.

## 3. Tanda B — pruebas visuales y lógica PPSSPP 1.20.4 A/B/A

Verificar binario oficial PPSSPP, versión, SHA, backend, PID/starttime, FD del ISO propio y WS `game.status` antes de atribuir capturas. Hacer original USA → ISO 7024 → original USA, en mismas partidas y pantalla; menú configuración (tildes y desplazamiento de símbolos), prólogo, mapa2, combates, TUIKA, diálogo con ligaduras y signos, enciclopedia, sprites, retratos, tilemaps, UI, sonido, guardado/carga y escenas con referencias cruzadas.

Para los **1.298 textos más cortos**: hay 1–7 espacios ASCII agregados al final (**3.899 bytes en total**) para mantener la longitud del opcode; **no son equivalentes visualmente por definición**. Requieren confirmación individual de wrap, padding visible, líneas de más, caja o texto cortado y pérdida de fluidez. Si falla, revertir las 1.298, analizar una alternativa verdadera sin cambiar offsets: almacenamiento separado con enlace MIPS validado o compresión de texto equivalente que no altere renderización, con pruebas de control. Los 2.002 textos con ligadura dependen de confirmar las 44 nuevas tintas y la alineación DSARC interna de 16+16. No confundir legibilidad en imágenes sintéticas con C real.

No hay PPSSPP oficial preinstalado en R25; si el entorno impide ejecutar C, informar la limitación y completar más A/B sin falsificar el cierre. No exportar capturas privadas al repositorio sin permisos/licencias.

## 4. Tanda C — auditoría editorial granular, integración residual e ingeniería MIPS

Para **todos los 3.300 IDs** de `traduccion/propuestas/R25_COLA_CONJUNTA_3300.csv`, cruzar escena/orden/hablante con `traduccion/CLADUN_BORRADOR_ES.csv`, glosario, QA manual y guion reconstruido. Verificar sentido, tildes, signos, nombres, largura de caja, retratos/indicadores, saltos de línea, comandos de control. Registrar decisión **individual** para cada ID; no marcar global PASS por interpolación.

Si se prueban 7.024/8.248 reales, quedan **1.224** diferidas (no 4.524). Analizar las 1.224 restantes con otro modelo seguro: 881 textos crecientes fuera de los 2.002 strict y 343 textos cortos/u otros según resultados reales. Construir tablas de referencias MIPS antes de intentar textos de longitud variable. Los ocho dígitos de offsets que hay en script/table nunca se inventan. Inspeccionar `EBOOT.BIN` solo en entorno legítimo y con informe A MIPS verificable. No romper PSPFS ni scripts para perseguir 100 %.

## 5. Tanda D — QA/CI/Windows y cierre de relevo real

Ejecutar:
```bash
python -m unittest discover -s tests -v
python tools/f4_r25_piloto_85pct.py
python tools/f4_r24_piloto_1650_ligaduras.py
python tools/verificar_integridad.py --raiz .
python tools/verificar_borrador_es.py
python tools/qa_cobertura_4_areas.py
python tools/qa_cobertura_4_areas.py --require-closed  # falla si no está cerrado
(cd patcher && go test ./...)
git diff --check
```
Último comando B del R24 requiere corpus; no basta con dejar un reporte. Ejecutar BPS y parcheador Go Windows x64 E2E **solo en equipo local privado**, con SHA+CRC, revertir ISO, cotejar 347 miembros no textuales y 0 P0/P1. Matriz QA `Q069/Q070` `NOT_RUN` hasta prueba C; total **70 casos**. Validar CI push y PR del mismo commit, reportar conclusiones y enlaces sin inventar.

**Actualiza**, según evidencia real, `reports/COBERTURA_4_AREAS.json`, `reports/ESTADO_CONTINUIDAD_PPSSPP.json`, `docs/ESTADO_CIERRE_4_AREAS.md`, `qa/MATRIZ_BETATESTING_COBERTURA.csv`, reportes nuevos, código, tests y docs. **Solo cuando 3.300 pasen A/B/C + editorial**, cambiar romhacking a **7.024/8.248 (85,16 %)**. Si solo pasa parte, contar solo entradas realmente aprobadas y mantener porcentaje verificable. Documentar cierres independientes de traducción, gráficos y betatesting. PR #7 continúa OPEN/DRAFT, no merge ni force push.

**OBLIGATORIO AL TERMINAR:** sustituir completamente esta instrucción por `prompts/SIGUIENTE_TAREA.md` R27 autosuficiente con obligación de reescritura recursiva hasta que romhacking y T/G/Q sean 100 % comprobados. Incluir bloqueos específicos, rutas y herramientas, pruebas A/B/C, y no afirmar ejecución futura automática.
