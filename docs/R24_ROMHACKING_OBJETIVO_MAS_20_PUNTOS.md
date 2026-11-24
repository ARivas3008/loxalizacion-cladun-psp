# CLADUN ES — R24: ruta de +20,00 puntos de ROMhacking sin romper eventos

**24/11/2026.** Referencia oficial previa **3.724/8.248 (45,1503 %)**, con **4.524 sustituciones diferidas**. El incremento solicitado de 20 puntos porcentuales exige al menos **1.650 nuevas sustituciones** (1.650/8.248 = 20,00485 puntos); resultado objetivo **5.374/8.248 (65,1552 %)**. Es importante separar **objetivo de PILOTO binario** de integración oficialmente aprobada: **en R24 NO se han liberado/validado 1.650 textos en PPSSPP**, por lo que el avance oficial NO cambia.

## A: nueva comprobación de ISO original auténtica, sin mutación

Se extrajo localmente la ISO USA del archivo `.7z` privado del usuario con libarchive y se validó SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f` y **305.496.064 bytes**. `SCRIPT.SDT` PSPFS #231 está en offset relativo **9.652.224**, tamaño comprimido **699.624 B**, descomprimido **930.304 B**, SHA comprimido `1811742d7d3e88da530c1fd2b98885e8426f7af761f7c89aecc80f34ffdbe2d4`. El siguiente miembro PSPFS empieza en 10.352.128: capacidad disponible **699.904 B**, incluyendo **280 B de margen**.

Nueva prueba independiente: se descomprimieron los 8 bloques IMY sin cambios, se verificó SHA del DSARC expandido `2c5ad0532e1f3106585dd9ba3a4dfcb7a8f61d8a09235b3b0d8e621f21f66051`; se recompusieron todos los bloques con el algoritmo existente y se descomprimieron de nuevo **byte exactos**. El recomprimido **sin siquiera cambiar un texto** produjo **700.483 B**, un exceso de **579 B sobre el slot de 699.904**. En consecuencia, **prohibido escribir en el espacio original** con este códec; se utilizará reubicación `append-only` de `SCRIPT.SDT` manteniendo los bytes de otros miembros. `SCRIPT.DAT` SHA `c9b360942a6845e7eba893c6e833e5dbebd6d6fc46004ea3f35ffa0d3618f358`; `SCRIPT.TBL` SHA `f8b32b9da5aef1deaa2a345cea799b5795d7682ca02830cea554a43ac2f7ed37`. Auditoría autónoma cuenta **1.625 bloques, 51.705 comandos, 46.308 no textuales y 5.397 textuales**. No se tocó ISO fuente.

## B: implementación real de pipeline privado 3.724 + 1.650

Se agregó `tools/f4_r24_piloto_1650_ligaduras.py`. No se limita a estimar cifras: **implementa** el flujo para generar un piloto privado, sujeto a validaciones que fallan cerradas:

1. Leer `traduccion/CLADUN_BORRADOR_ES.csv` con hash y 9.237 IDs inmutables. Generar el diccionario de 44 parejas sin colisiones y la cola de 2.002 textos largos compatibles con la codificación de un byte. Seleccionar **1.650** offsets únicos de forma determinista y asegurar el tamaño fijo y reversibilidad. Sin `--iso-original`, ejecutar preflight B con hashes de selección, sin exportar textos.
2. Con ISO original auténtica, cotejar cada una de las 1.650 preimágenes contra `SCRIPT.DAT` original, y auditar copia RAM con los **51.705 comandos**, **46.308 instrucciones no textuales** y **cero** offsets internos cambiados.
3. Crear una **candidata base privada** con `tools/integrar_parche_seguro.py` en modo `experimental_partial=True, event_safe_only=True`. Exigir que esa candidata contiene efectivamente las **3.724** sustituciones históricas y aplaza **4.524**. No confundir la suma con dos ISOs distintas.
4. Sustituir solo FONT.ARC en la base por variante **44 ligaduras + 19 signos**, prototipo de 144.000 B dentro del slot 144.384, preservando otros 348 PSPFS. **Alineación IMY 16+16 EXPERIMENTAL, no aprobada en PPSSPP**.
5. Aplicar 1.650 sustituciones adicionales sobre `SCRIPT.DAT` **de esa misma candidata base**. Guardar `SCRIPT.TBL` exacto; revalidar inalteradas las 46.308 instrucciones no textuales, 1.625 inicios y 51.705 órdenes; no modificar longitud ni desplazamientos. Reempacar la DSARC y recomprimir con roundtrip verificado.
6. Reubicar `SCRIPT.SDT` al final por la implementación existente `append_text_containers`, actualizando solo su entrada PSPFS y extensión ISO9660 `DATA.DAT`. Comparar con la ISO original los **347 restantes** miembros PSPFS: mismos nombres, índice, offset, tamaños y contenido byte exacto. Crear el piloto en una ruta privada nueva, de forma atómica y sin sobrescribir ISO.
7. Mantener `report["new_official_integrations"]=0` y `not_release_authorized=True` hasta revisión editorial y A/B/A C.

Archivos nuevos: `tools/f4_r24_piloto_1650_ligaduras.py`, `tools/f4_r24_script_slot_audit.py`, pruebas `tests/test_f4_r24_piloto_1650_ligaduras.py` y `tests/test_f4_r24_script_slot_audit.py`, `reports/R24_ROMHACKING_MAS_20_PUNTOS.json`. La suite incluye casos negativos para tamaño, índices, corpus real y archivo original. Los tests de corpus permiten verificar el conjunto real de **2.002** y el objetivo **1.650** en CI sin ISO.

## Comandos de ejecución privada

Desde un checkout completo y **solo si se dispone de la ISO adquirida legítimamente**:

```bash
python tools/f4_r24_piloto_1650_ligaduras.py
python tools/f4_r24_script_slot_audit.py --iso-original /PRIVADO/Cladun_USA.iso
python -m unittest discover -s tests -p 'test_f4_r24*' -v
python tools/f4_r24_piloto_1650_ligaduras.py \
  --iso-original /PRIVADO/Cladun_USA.iso \
  --candidate /PRIVADO/Cladun_R24_5374_EXPERIMENTAL.iso
python tools/qa_cobertura_4_areas.py
python tools/qa_cobertura_4_areas.py --require-closed  # se espera falla
```

**No se ha ejecutado en este relevo la última orden de producción de la ISO combinada**. Haber programado su generador no prueba que los 1.650 textos rendericen, ni autoriza marcar 65,1552 % oficial. El informe A de compresión demuestra una limitación real que evita una sobrescritura de PSPFS; el CI B prueba algoritmos y regresiones, no el motor PSP.

## Pendientes antes del +20 oficial

- Generar el **piloto combinado** en entorno local con corpus y scripts completos, verificar hashes finales, guardas y aislamientos, y resolver fallos de pruebas si los hubiera.
- PPSSPP oficial 1.20.4 autenticado por binario/PID/starttime/FD/WS; probar carga de la fuente IMY compacta a 16 bytes, retorno a ISO original y reversibilidad.
- Revisar **individualmente** los 1.650 diálogos por personajes, sentido, género, cortes de línea y signos; comprobar en contexto dentro del juego que las 44 ligaduras visualizan con anchura y tinta correctas.
- Ejecutar menú, prólogo, combate, segundo nivel, enciclopedia y guardado/carga; registrar capturas auténticas fuera de Git, corregir regresiones y pasar un E2E de BPS/EXE Windows x64.
- Tras aceptación, actualizar realmente el contador 3.724→5.374, diferidas 4.524→2.874; **hoy NO procede** actualizarlo. Matriz QA Q067/Q068 sigue NOT_RUN, no se declara 100 %.

El PR #7 sigue abierto en borrador; no hay merge, force push ni activos comerciales publicados.
