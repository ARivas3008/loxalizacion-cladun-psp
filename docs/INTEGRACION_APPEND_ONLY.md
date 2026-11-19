# Integración append-only para evitar cambios en assets ajenos

**Estado: implementación experimental, NO parche final validado.** Se congela la traducción y se trabaja en la reinserción.

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

Los últimos informes estáticos identifican 280 desbordes de campo, 816 entradas sin capacidad modelada, seis textos gráficos y dos originales incompletos. Se deben resolver por estructura, no forzar inserciones destructivas.

También faltan pruebas reales en PPSSPP de arranque, diálogos, signos españoles, retratos, mapas, tiles y combate. La garantía de bytes es separada de la validación del motor y sus gráficos.
