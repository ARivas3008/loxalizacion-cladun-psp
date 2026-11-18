# Formato del corpus, orden e identificadores

## Fuente maestra

La fuente editable es `corpus/CLADUN_TODO_TEXTO_ORIGINAL.csv`, codificada en UTF-8 con BOM. Cada fila describe **una posición textual**, por lo que una cadena repetida en otro recurso figura como otra fila. La columna `espanol` está deliberadamente **vacía**.

| Campo | Propósito |
| --- | --- |
| `grupo_id` | Orden de 6 cifras para lectura, **único**, generado en secuencia, no index nativo de PSP. |
| `text_id` | ID estable de la extracción: puede ser `CLD-...`, `CLD-F-...` o `CLD-GFX-...`. |
| `tipo` / `campo` | Clasificación de contenido y subcampo de registro. |
| `original` | Bytes recuperados decodificados a texto; **no corregir ni traducir aquí**. |
| `espanol` | Columna prevista para la futura localización; vacía en esta entrega. |
| `estado` | `pendiente_traduccion`, `requiere_comprobar_en_juego` o `requiere_reconstruccion`. |
| `revision_fuente` | Nivel de evidencia de la cadena, distinto de la traducción. |
| `origen` / `indice_registro` | Archivo y posición de origen en el inventario. |
| `script` / `script_id` / `orden_script` | Pertenencia y posición del diálogo, cuando corresponda. |
| `offset_hex` | Desplazamiento en su archivo de origen, **no necesariamente en la ISO**. |
| `capacidad_campo` | Capacidad nominal del campo cuando se conoce, no límite final de traducción. |
| `longitud_original_bytes` / `bytes_hex` | Longitud y bytes recuperados que permiten comprobar fidelidad CP932. |
| `idioma_origen` / `comentario` | Orientación de revisión; idioma solo estimado, sin traducir. |

## TXT de lectura

`CLADUN_TODO_TEXTO_ORIGINAL.txt` es el único TXT maestro: contiene exactamente 9.237 grupos numerados, cada uno con ID, tipo, estado, recurso y texto `ORIGINAL` íntegro, sin traducción ni espacio de edición. Es una **vista de lectura**, no el formato de reinserción. El CSV conserva los bytes, offsets y columnas editables.

Ejemplo creado con una cadena comprobada del corpus:

```text
========== GRUPO 000001 | ID CLD-000002 ==========
TIPO: dialogo
ESTADO: pendiente_traduccion
RECURSO: SCRIPT.SDT/SCRIPT.DAT
ORIGINAL:
Is this the tavern?
========== FIN GRUPO 000001 ==========
```

## Orden conservado

La numeración principal respeta el orden de extracción agrupado por recurso y posición. En scripts se conserva además el script y su orden interno. **No afirma que el jugador vea los mensajes en ese orden narrativo.** No ordenar alfabéticamente ni deduplicar aunque se repitan palabras o nombres.

## Reglas de traducción futuras

Preservar exactamente variables de formato (`%s`, `%d`, `%02d`, etc.), caracteres de control, saltos de línea, etiquetas, unidades y referencias técnicas. El espacio en bytes disponible para español **no está demostrado**: no inferirlo simplemente de `longitud_original_bytes`. Cualquier reinserción requerirá reconstrucción de tablas de punteros, longitudes y pruebas en PSP/PPSSPP.
