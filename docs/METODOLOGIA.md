# Metodología de extracción y revisión

## Alcance

Copia de *Cladun: This Is an RPG!* de USA/PSP aportada al proyecto. Se recuperan las cadenas **no vacías** de estructuras de texto reconocidas, tablas de base de datos, títulos/avisos gráficos verificados y créditos. Se mantienen los nombres y descripciones en japonés que existen en esta edición, sin confundir idioma de origen con falta de localización.

## Pipeline

1. **ISO9660**: identificar `PSP_GAME/USRDIR/DATA.DAT` y el volumen; conservar suma SHA-256.
2. **PSPFS_V1**: leer la tabla y decodificar las 349 entradas (IMY/GZip/sin compresión según corresponda).
3. **Archivos anidados**: abrir `SCRIPT.SDT` y `DATABASE.DAT` mediante el índice de contenedores, sin alterar los originales.
4. **Scripts narrativos**: usar `SCRIPT.TBL` para agrupar IDs/nombres `.dsf`, recuperar solo argumentos textuales de los comandos relevantes; preservar orden y offset. Las operaciones del motor no se publican.
5. **Interfaz**: recuperar la tabla de punteros `STRTBL.DAT`, conservando los marcadores de formato.
6. **Bases de datos**: distinguir campos textuales de atributos numéricos mediante los offsets y longitudes por estructura, en vez de detección libre de bytes imprimibles. Conservar cada registro, aunque una cadena se repita.
7. **Créditos**: preservar solo líneas no vacías; los 201 espacios o líneas vacías se registran como exclusiones para localizar, sin perder el origen bruto para una futura reinserción.
8. **Rótulos gráficos**: incluir únicamente cadenas comprobadas visualmente. Estas requerirán edición de imagen para materializar la traducción.
9. **QA**: cotejar `bytes_hex` → CP932 → `original`, ID único, grupos consecutivos, subconjuntos completos, TXT y resultados de auditoría.

## Niveles de evidencia

- `verificado_formato`: argumento de script o crédito procedente de un formato identificado; **no** significa que una captura en juego lo confirme.
- `verificado_tabla_punteros`: texto de interfaz desde tabla de punteros.
- `campo_binario_confirmado`: texto alojado en un campo identificado de un registro de base de datos.
- `verificado_visual`: texto rasterizado observado en la imagen original.
- `texto_real_uso_pendiente`: cadena que ocupa un campo textual real, pero puede ser etiqueta de depuración, referencia o dato no expuesto al jugador.
- `bytes_no_decodificables`: campo textual de longitud limitada cuyos bytes no forman una secuencia CP932 completa; **no reconstruir por suposición**.

## Limitación

La indexación no demuestra que el juego pueda mostrar todos esos textos, ni que estén **todos** los textos visibles. Se requiere revisión de imágenes no indexadas, ejecutable, paquetes comprimidos no cubiertos y PPSSPP en escenas y menús. El proyecto no contiene un inyector funcional de traducciones.
