# 02 — Formato de texto plano y trazabilidad

## Archivo principal

`corpus/CLADUN_TODO_TEXTO_ORIGINAL.txt` usa bloques fáciles de leer, similares a un corpus de localización profesional:

```text
========== GRUPO 000001 | UNIDADES 1 | ID CLD-000002 ==========
TIPO: dialogo
RECURSO: SCRIPT.SDT/SCRIPT.DAT
SCRIPT: scr01.dsf | ID SCRIPT: 41
REGISTRO: 6 | ORDEN SCRIPT: 8
OFFSET: 0x000002AF
CAMPO: cadena
VALIDACIÓN: verificado_formato
ORIGINAL:
Is this the tavern?
FIN ORIGINAL
ESPAÑOL EDICIÓN:
ESTADO: pendiente_traduccion
PREVIO: (inicio)
SIGUIENTE: CLD-000003
```

Una traducción **no** se proporciona en esta etapa. El bloque `ORIGINAL` es multilínea: se conservan los saltos de línea del recurso. `FIN ORIGINAL` es un delimitador de formato, no parte del juego. El archivo se codifica en UTF-8 con BOM, legible en editores habituales.

## CSV maestro

`grupo_id`: orden de lectura del TXT. `text_id`: ID estable por fuente (puede venir de extracción anterior). `tipo`: categoría. `campo`: función presumida del campo dentro del recurso. `original`: contenido de fuente tal como se decodificó del campo. `espanol`: espacio vacío reservado para futura traducción. `estado`: clasificación QA. `revision_fuente`: evidencia estructural/visual. `origen`: cadena de contenedores y archivo interior. `indice_registro`: posición dentro de tabla o bloque. `script`, `script_id`, `orden_script`: identificación narrativa cuando existe. `offset_hex`: posición en el **archivo interior descomprimido**, no offset físico de la ISO. `capacidad_campo`: bytes reservados en campo de tabla (cuando se conocen). `longitud_original_bytes`: bytes efectivos del contenido extraído. `bytes_hex`: representación sin pérdida de los bytes fuente (salvo rótulos PNG, cuya fuente es la imagen). `idioma_origen` y `comentario`: marcadores auxiliares de revisión.

**No se han establecido límites de reinserción para diálogos y STRTBL**; no confundir la longitud original con capacidad máxima. Algunos campos de tabla sí tienen capacidad fija y el español deberá respetarla o requerirá adaptar el formato. El sistema de codificación/fuente del juego también necesita trabajo de ingeniería de reinserción.

## Reglas del TXT

- Nunca editar directamente el TXT como fuente de verdad: editar `espanol` del CSV y regenerar cuando se empiece a traducir.
- Las repeticiones son deliberadas. No eliminar bloques repetidos.
- No convertir saltos internos en espacios ni modificar formatos `%d`, `%s`, `%02d`, entre otros.
- Los campos ilegibles conservan el **hexadecimal exacto** para cotejo posterior, y la sustitución `�` del TXT **no es un carácter supuesto del juego**.
