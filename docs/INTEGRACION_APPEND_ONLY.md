# Integración append-only para evitar cambios en assets ajenos

**Estado: 9.237/9.237 rutas de inserción estructuralmente preparadas; NO parche final validado en PPSSPP.** Se congela la traducción y se trabaja en la reinserción.

## Hallazgos verificados en la ISO USA

- SHA-256 fuente: b73b263fce863e51a0e27d0d11d6bde2886e439a18e2bb186d497619a1b79f.
- DATA.DAT: 349 entradas PSPFS. SCRIPT.SDT contiene cuatro miembros DSARC, con SCRIPT.DAT de 633.344 bytes y SCRIPT.TBL, separados por solo 512 bytes.
- El archivo SCRIPT.SDT original ocupa 699.624 bytes IMY y dispone de apenas 280 bytes libres antes del siguiente recurso PSPFS. DATABASE.DAT dispone de 36 bytes.
- El corpus tiene 5.207 textos de SCRIPT.DAT. Sus borradores españoles requieren unos 17.712 bytes adicionales netos, antes de contar nuevas alineaciones.
- No se debe escribir un diálogo más largo en su posición original ni desplazar a los siguientes recursos.

## Integrador experimental

La herramienta [integrar_parche_seguro.py](../tools/integrar_parche_seguro.py) y el [compresor IMY](../tools/imy_repack_safe.py):

1. Verifican ISO, 9.237 IDs originales, bytes y metadatos inmutables.
2. Preparan el prototipo de fuente F5A0–F5B2 con verificación independiente de sus 19 glifos.
3. Reconstruyen solo opcodes textuales conocidos de SCRIPT.DAT, actualizando sus longitudes y los inicios de SCRIPT.TBL. Copian todos los opcodes no textuales sin alterar sus bytes.
4. Mantienen idénticos los miembros AISCRIPT.DAT y AISCRIPT.TBL; solo ajustan metadatos de los miembros afectados.
5. Modifican campos de DATABASE.DAT únicamente si se conoce y respeta su capacidad exacta, incluyendo NUL. Nunca recortan traducciones ni sobrescriben datos vecinos.
6. Permiten créditos en STAFFROLL.TXT conservando sus separadores.
7. Recomprimen como IMY, sin sustituirlo por GZIP, y vuelven a descomprimir para cotejar los bytes completos.
8. Agregan al final de DATA.DAT nuevas versiones de los contenedores textuales y actualizan exclusivamente sus registros PSPFS, además de los tamaños de DATA.DAT/ISO9660. Los otros recursos retienen offsets, tamaños y bytes originales.
9. Comprueban de nuevo todos los recursos PSPFS y los otros archivos ISO9660.

## Uso privado

Modo estricto: genera informe y **rechaza** crear una ISO si persiste cualquier campo no integrable:

~~~bash
python tools/integrar_parche_seguro.py --iso Cladun-USA.iso --candidate Cladun-Espanol-PRIVADA.iso --report auditoria_integracion.json
~~~

Modo experimental parcial: permite generar un candidato privado con los registros de estructura reconocida, pero **no equivale a una traducción completa**:

~~~bash
python tools/integrar_parche_seguro.py --iso Cladun-USA.iso --candidate Cladun-Espanol-PRIVADA.iso --report auditoria_integracion.json --experimental-parcial
~~~

Nunca subir la ISO resultante, los atlas comerciales o datos del juego a GitHub.

## Ensayo con la ISO proporcionada

Se realizó una prueba privada sobre una cadena sintética de sustitución, no sobre todo el corpus español:

- Reconstrucción sin cambios: SCRIPT.DAT y SCRIPT.TBL recuperados byte por byte de forma idéntica.
- Reconstrucción de un diálogo: recompresión IMY y decodificación de retorno correctas.
- 348 recursos PSPFS no intervenidos: bytes y offsets exactamente iguales.
- La ISO candidata de prueba pasó de 305.496.064 a 306.196.992 bytes al añadir un contenedor textual al final; la ISO original permaneció intacta.

Esto **no demuestra todavía** que el cargador PSPFS acepte los recursos añadidos ni que PPSSPP renderice correctamente.

## Pendientes que impiden llamarlo parche completo

El último informe de integrabilidad entrega **8.491 cambios técnicamente planificados, 746 cadenas sin cambios de bytes y 0 bloqueos**. Los 280 desbordamientos históricos se tratan con etiquetas compactas solo para la inserción; 2 originales defectuosos se cotejan por bytes exactos; los seis rótulos gráficos tienen regiones de edición verificadas por SHA y píxeles. Las 816 entradas antiguamente sin capacidad se resuelven a través de reconstrucción de tablas y créditos, no inventando espacio.

También faltan pruebas reales en PPSSPP de arranque, diálogos, signos españoles, retratos, mapas, tiles y combate. La garantía de bytes es separada de la validación del motor y sus gráficos.


## Cobertura actualizada y verificación de rótulos

- [Adaptador de campos fijos](../tools/ajustes_campos_es.py): traducciones literarias intactas; 280 etiquetas de inserción compactas y 2 orígenes truncados explícitos, sin escribir fuera del campo.
- [Localizador de seis PNG](../tools/graficos_texto_es.py): edición limitada al texto y comparación de píxeles **exactos** fuera del rectángulo; no tocar retratos, tiles ni otras imágenes.
- [Prueba REAL en la ISO aportada](../reports/ensayo_graficos_iso_2026-11-18.json): 348 recursos PSPFS diferentes de SYS.DAT2 y 11 archivos ISO9660 ajenos conservaron tanto bytes como offsets. Esto solo prueba el ensayo aislado de los seis gráficos.
- La ISO candidata del integrador ahora se prepara en una ruta temporal y se publica atómicamente solo tras pruebas y reevaluación del SHA de origen. No se sobrescriben archivos.
- **El modo estricto ya puede planificar el 100 % del corpus**, pero la ejecución conjunta con PPSSPP y las posibles referencias de salto no identificadas del intérprete siguen sin verificar. Nunca anunciar el parche como final solo por pasar estas pruebas.

## Validación adicional del códec IMY (19/11/2026)

Una auditoría posterior detectó que la segunda palabra de la cabecera global IMY representa el **tamaño de bloque descomprimido** (`131072` bytes en esta ISO), **no** la longitud total del contenedor. Se corrigió `tools/imy_repack_safe.py` y se añadió una prueba de dos bloques que debe fallar si se introduce nuevamente el tamaño total. Una prueba privada sobre la ISO proporcionada descomprimió y volvió a recomprimir de forma íntegra `SCRIPT.SDT` (8 bloques, 930.304 bytes expandidos) y `DATABASE.DAT` (5 bloques, 620.032 bytes expandidos): ambos recuperaron **exactamente** los bytes originales tras la segunda descompresión. Se publica solo el [informe no comercial](../reports/roundtrip_imy_multibloque_iso_real_2026-11-19.json). Esta evidencia demuestra el formato de recompresión, no el funcionamiento del juego ni la inserción española íntegra. Sigue pendiente una prueba en PPSSPP con una ISO candidata conjunta.
