# Formatos y criterios de integridad

| Formato | Estado | Tratamiento |
|---|---|---|
| ISO9660 | Estructura reconocida | Inventario, ruta, offset, tamaño |
| PSPFS_V1 | 349/349 | Inventario, extracción, SHA-256 |
| GZIP (en PSPFS) | Reconocido | Descompresión verificada por tamaño |
| IMY por bloques | Reconocido | Descompresión verificada por tamaño |
| DSARC FL | Reconocido | Archivos internos e índice |
| DSARCIDX | Reconocido | Índices y archivos internos |
| SCRIPT.DAT/.TBL | Reconocido | 51.705 comandos, 1.625 bloques |
| AISCRIPT.DAT/.TBL | Reconocido | 21.535 comandos, 552 bloques |
| STRTBL.DAT | Reconocido | 651 textos, 3 slots vacíos |
| Tablas fijas de DATABASE.DAT | Parcial | Registros conocidos, texto candidato |
| Tablas variables de DATABASE.DAT | Pendiente | Escaneo por bytes, sin equivalencia confirmada con registros |
| Fuentes, imágenes y texto rasterizado | Pendiente | Revisión gráfica y OCR manual según necesidad |
| Binario ejecutable EBOOT/BOOT | Pendiente | No se ha completado análisis de cadenas del ejecutable |

## Columnas principales

`text_id`: identificador ordinal reproducible. `source`: cadena de contenedores y archivo. `file_index`: índice del bloque o registro. `script_id` y `script_file`: clave lógica `.dsf`. `command_index` e `instruction_id`: ubicación en el bloque. `opcode_hex`: instrucción de origen. `offset_hex`: offset dentro del **archivo descomprimido correspondiente**, no dentro de la ISO. `raw_hex`: bytes de texto que se decodificaron con CP932. `confidence`: confirmado/candidato. `translation_es`: campo editable, inicialmente vacío.

La relación con el offset absoluto en la ISO se reconstruye mediante `indices/pspfs.csv` y `indices/dsarc.csv`; para archivos comprimidos no existe una correspondencia lineal entre offset descomprimido y offset físico del contenedor.
