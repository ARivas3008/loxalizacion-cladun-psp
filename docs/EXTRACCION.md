# Procedimiento de extracción

## 1. Contenedor externo

La copia proporcionada está en 7z y contiene la imagen ISO de PSP. La ISO expone 12 archivos, entre ellos `PSP_GAME/USRDIR/DATA.DAT`. La imagen ISO9660 se analiza con su descriptor primario en sector 16 y con los registros de directorio (LBA, tamaño y nombre). El programa lee el archivo principal por offset, sin montar la ISO.

## 2. Contenedor `PSPFS_V1`

Tabla de 349 entradas con registros de 32 bytes en esta versión: nombre ASCII en 20 bytes, tamaño descomprimido `u32le`, tamaño almacenado `u32le` y desplazamiento absoluto `u32le`. Un tamaño descomprimido cero indica datos sin compresión. Otros se comprimen como bloques GZIP o paquetes IMY.

## 3. Contenedores anidados

`DSARC FL` almacena entradas con nombre de 40 bytes y campos `u32le` de tamaño y desplazamiento. `DSARCIDX` añade un array de índices `u16le` antes de la tabla, alineada a cuatro bytes. Se incluyen archivos anidados de RMAP, sonido, gráficos, diálogos y bases de datos. El índice representa **el orden en la tabla del archivo**, no el orden en la memoria del juego.

## 4. Comandos de scripts

`SCRIPT.SDT` contiene `SCRIPT.DAT`, `SCRIPT.TBL`, `AISCRIPT.DAT`, `AISCRIPT.TBL`. Cada tabla consta de 16 bytes de cabecera y entradas de 32 bytes (`u32 id`, `u32 offset`, nombre de 24 bytes). Cada instrucción binaria tiene `u8 opcode`, `u16 id`, `u16 longitud_argumentos` y los bytes de argumento. Los opcodes `0x66`, `0x69`, `0x6E` del guion principal contienen texto Shift-JIS/CP932 con `u16 longitud_texto`, bytes de texto y un byte NUL. Todos los comandos se enumeran en `indices/script_commands.csv`, incluso si no contienen texto.

## 5. Base de datos y GUI

`DATABASE.DAT/STRTBL.DAT` es una tabla de offsets de 32 bits. Su primer valor es la dirección del primer texto y equivale a cuatro veces la cantidad de slots de la tabla; en esta copia hay 654 slots, de los cuales 651 apuntan a cadenas. Sus textos se extraen sin modificar variables. Otras bases de datos se separan en registros de ancho fijo cuando el tamaño de cabecera y el recuento se pueden verificar; los campos con apariencia textual son **candidatos** hasta definir el esquema.

## 6. Calidad de cobertura

Los índices describen 349/349 entradas `PSPFS_V1` recuperadas, 1.186 elementos DSARC, 73.240 instrucciones y 9.647 registros del corpus. **Esto no significa que todos los elementos sean texto correcto, ni que toda cadena visible esté localizada**. Quedan revisiones de datos de formato variable, posibles mensajes gráficos, fallos de renderizado, cajas de diálogo y comprobación en PPSSPP.
