# Checklist de control de calidad

- [x] Extraer y listar los archivos de la ISO.
- [x] Reconocer `PSPFS_V1` y conservar 349 posiciones de tabla.
- [x] Descomprimir las 349 entradas y validar tamaños.
- [x] Indexar los miembros DSARC, conservando su orden.
- [x] Parsear `SCRIPT.DAT` y `AISCRIPT.DAT` comando por comando.
- [x] Conservar nombres, diálogos, opciones y cadenas del HUD con offsets y bytes originales.
- [x] Desglosar tablas de bases de datos de ancho deducible y marcar dudas.
- [ ] Confirmar manualmente las cadenas halladas por heurísticas en binarios.
- [ ] Auditar todo texto dibujado en imágenes (fuentes/texture atlas e interfaz).
- [ ] Auditar posibles cadenas de `EBOOT.BIN`, tablas variables y recursos no reconocidos.
- [ ] Asociar personajes e intervenciones por escena y contexto.
- [ ] Preparar un glosario canónico y traducción al español.
- [ ] Desarrollar y verificar repaquetado/reinserción sin pérdida.
- [ ] Validar todas las pantallas y escenas en PPSSPP.

## Reglas automáticas antes de traducir

1. El número de filas y el orden deben coincidir con la versión fuente.
2. Los campos identificadores y `raw_hex` no deben cambiar.
3. Los marcadores printf (por ejemplo `%s`, `%d`, `%02d`) se preservan en cantidad y tipo.
4. Los finales de línea y las etiquetas embebidas se revisan por contexto.
5. La codificación final debe ser compatible con el juego, pero **no se ha validado** todavía una fuente con todos los caracteres españoles.
