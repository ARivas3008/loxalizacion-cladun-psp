# Auditoría independiente de cobertura textual — Cladun PSP (USA)

**Fecha:** 17 de noviembre de 2026.  
**Resultado:** **NO está demostrado el 100 % del texto del juego.** Se han confirmado al menos una omisión textual real (en gráficos) y falsos positivos (en datos numéricos). Es incorrecto equiparar «todos los contenedores descomprimidos» con «todas las cadenas localizables extraídas».

## Objeto de la comprobación

Se compararon los CSV y el extractor versionados para esta ISO con los archivos descomprimidos de la imagen facilitada, identificada por:

- Volumen ISO9660: `CLASSIC_DUNGEON_TRIAL_AND_APPEND`.
- ID de disco en `PARAM.SFO`: `NPUH10072`; título `CLADUN: This is an RPG!`.
- SHA-256 de la ISO: `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.

**Prueba de reproducibilidad:** nueva ejecución de `tools/extract_cladun.py` contra esa ISO; los **28 archivos** del corpus, índices y reportes generados coincidieron byte por byte con la versión de trabajo. La suite de **4 pruebas** pasó. Esto verifica *reproducibilidad*, no cobertura total.

## Qué sí está recuperado

| Fuente | Comprobación | Límite |
| --- | --- | --- |
| `PSP_GAME/USRDIR/DATA.DAT` | 349 de 349 entradas `PSPFS_V1` descomprimidas | Un contenedor descomprimido puede contener gráficos, texto no identificado y datos empaquetados |
| Paquetes `DSARC FL` / `DSARCIDX` | 1.186 miembros con índices y offsets | La mayoría de miembros no tiene decodificador textual específico |
| `SCRIPT.SDT` | 1.625 bloques `SCRIPT`, 552 `AISCRIPT` y 73.240 instrucciones parseadas | Los CSV guardan metadatos y tamaño de argumentos, **no el payload binario completo** de cada instrucción |
| `SCRIPT.DAT` | 4.701 diálogos, 583 entradas de interlocutor y 113 opciones | Solo se consideran textuales los opcodes `0x66`, `0x6E` y `0x69`. No está demostrado que sean todos los mecanismos de presentación de texto |
| `DATABASE.DAT/STRTBL.DAT` | 651 cadenas extraídas de 654 posiciones | La tabla de punteros está recuperada; los textos rasterizados no están cubiertos |
| Otras tablas `DATABASE.DAT` | Cadenas y campos candidatos | No se ha reconstruido formalmente la estructura de todos los registros |
| `STAFFROLL.TXT` | 366 líneas, incluidas vacías | Texto de créditos recuperado |

## Hallazgos demostrables que impiden declarar cobertura completa

### A. Texto gráfico omitido — **confirmado**

`SYS.DAT2` contiene los miembros `DOT_NODATA.PNG` y `NODATA.PNG`, ambos con el rótulo visual **`NO DATA`**. El texto es visible en la imagen, pero la búsqueda insensible a mayúsculas en `corpus/todo_el_texto.csv` encuentra **0** coincidencias de esa frase. Estos archivos sí están indexados en `indices/dsarc.csv`, pero **indexar la imagen no equivale a extraer su texto**.

Hay más recursos con posibles rótulos, incluidos 37 `.MPB` del contenedor principal. No se afirma que todos contengan textos; se necesita revisión visual específica.

### B. Registros no textuales incluidos como texto — **confirmado**

De los 9.647 registros del CSV global, **2.859 son `candidato` y solo 6.788 están etiquetados `confirmado`** (incluidos registros vacíos). En `DATABASE.DAT/LV.DAT`, **56 registros** consisten en artefactos como `ﾍﾌﾌ=c`, obtenidos al interpretar secuencias de datos numéricos como CP932. Por ejemplo, los bytes `CD CC CC 3D` son el valor IEEE-754 de precisión simple aproximado a **0,1**; una letra suelta próxima no lo transforma en texto de juego. Estos candidatos **no deben traducirse**.

En otros registros, cadenas como `eHiyo's Cave` requieren investigar si hay un byte de control/prefijo o una forma efectivamente presente en el juego. No se deben limpiar automáticamente sin esquema.

### C. Alcance incompleto del detector — **confirmado en el código**

La búsqueda de textos en registros binarios exige **terminación NUL** y mínimo de letras, por lo que puede omitir etiquetas muy cortas, campos de longitud fija sin NUL y cadenas con controles. Además, el extractor **excluye del escaneo textual** 91 entradas principales por extensión: 50 `.SPS` (audio), 37 `.MPB` (recursos gráficos), 3 `.LDT` y 1 `.IDT`. La exclusión por sí misma no prueba que haya textos visibles en todos esos archivos.

El módulo del ejecutable `PSP_GAME/SYSDIR/EBOOT.BIN` tampoco se ha analizado con herramientas específicas de ejecutable/cadenas cifradas. El identificador `CLDN_TRIAL` es visible en la cabecera, pero **no basta para concluir si la instalación incluye únicamente contenido de prueba o el juego completo desbloqueado**. El análisis solo puede certificar esta versión de ISO, no cualquier otra edición del juego.

### D. Scripts ordenados, pero no serializados íntegramente

`indices/comandos/parte_01.csv` a `parte_15.csv` conservan las 73.240 instrucciones, con ID, opcode, índices, offsets y **longitud** de argumentos. Sin embargo, **no guardan el valor completo de los argumentos** de todas las instrucciones, ni una forma reconstruible de cada archivo `.dsf`. En consecuencia, el repositorio no contiene literalmente «todos los scripts» para edición/reensamblado completo, aunque sí indexe sus instrucciones.

### E. Los registros no son cadenas únicas ni todos son diálogos

Hay **9.647 filas**, de las cuales **391 están vacías** (201 líneas de créditos, 183 de interlocutor y 7 de diálogo). Existen múltiples repeticiones; el número no se puede interpretar como total de frases únicas ni como medida de completitud. El orden es principalmente **orden de archivo, tabla, bloque o offset**, no orden cronológico garantizado de la historia.

## Prioridades para llegar a una auditoría sólida

1. **Gráficos:** revisar todos los recursos de interfaz, PNG de `SYS.DAT2`, `.MPB` e imágenes IMY con texto; registrar cada cadena visible y su ruta/posición gráfica.
2. **Base de datos:** reconstruir esquema por archivo y campo, separar columnas translatables de numéricos; poner en cuarentena los falsos positivos de `LV.DAT`.
3. **Scripts:** conservar `raw_arguments_hex` o derivación lossless por instrucción, además del CSV de texto; auditar los otros opcodes y verificar grafías/controles.
4. **Ejecutable y ediciones:** analizar tablas/cadenas embebidas en `EBOOT.BIN` y comprobar si la imagen refleja la versión completa pretendida.
5. **QA en PPSSPP:** recorrer todos los menús y rutas narrativas, comparar capturas con CSV y registrar hallazgos pendientes para reinserción.

**Dictamen final:** La extracción existente es una **base reproducible útil**, pero **no exhaustiva**. No es correcto afirmar «100 % del texto» ni usar las 9.647 filas como corpus final listo para traducción sin limpieza y comprobaciones adicionales.
