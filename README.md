# Cladun: This Is an RPG (USA, PSP) — Proyecto de localización

Proyecto de auditoría y extracción textual conservando el **orden original, índices, offsets y bytes de origen**.

## Auditoría de la ISO suministrada

- ISO9660: 12 archivos; volumen `CLASSIC_DUNGEON_TRIAL_AND_APPEND`.
- `PSP_GAME/USRDIR/DATA.DAT`: contenedor `PSPFS_V1`, **349/349** entradas descomprimidas.
- Archivos anidados `DSARC FL`/`DSARCIDX`: **1.186** entradas indexadas.
- `SCRIPT.SDT`: **1.625** bloques SCRIPT y **552** bloques AISCRIPT; **73.240** instrucciones.
- Textos extraídos del guion: 4.701 diálogos, 583 referencias de interlocutor (incluye vacías) y 113 opciones.
- Interfaz de `DATABASE.DAT/STRTBL.DAT`: 651 cadenas.
- Corpus total del análisis: **9.647 registros**, incluidos candidatos no confirmados y líneas de crédito vacías.

## Estructura del proyecto

El proyecto local completo contiene:
`corpus/todo_el_texto.csv`, `corpus/dialogos.csv`, `corpus/interfaz_hud.csv`, `corpus/objetos_lugares_personajes.csv`, `corpus/creditos.csv`, `indices/iso9660.csv`, `indices/pspfs.csv`, `indices/dsarc.csv`, `indices/script_blocks.csv`, `indices/script_commands.csv`, `indices/database_records.csv`, el extractor reproducible `tools/extract_cladun.py`, pruebas unitarias y documentación técnica.

## Estado y metodología

Los textos de `SCRIPT.DAT` se extraen por instrucciones (opcode, identificador, longitud, argumentos y cadenas CP932); `SCRIPT.TBL` conserva ID y nombre de archivo `.dsf`. Los datos de `STRTBL.DAT` se extraen por tabla de punteros, sin tocar variables como `%s` o `%02d`.

**No se ha probado aún la cobertura absoluta de todo el texto en el juego.** Cadenas encontradas heurísticamente en tablas binarias requieren validar sus campos, y falta revisar texto gráfico, ejecutable y reinserción en PPSSPP.

**Nota de derechos:** No subas imágenes ISO ni archivos binarios comerciales a este repositorio público. La futura distribución debe ser un parche que requiera una copia propia del juego.

Esta descripción resume el inventario verificado del proyecto.