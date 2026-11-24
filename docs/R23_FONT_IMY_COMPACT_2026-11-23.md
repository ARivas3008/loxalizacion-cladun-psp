# CLADUN ES — R23: FONT.ARC compacta de 44 ligaduras, prueba privada A/B

## Alcance y estado

**No es una liberación ni un cierre al 100 %.** Se realizó una reconstrucción de FONT.ARC sobre la **ISO USA original autenticada** aportada por el usuario, sin subir recursos comerciales al repositorio. La variante ensaya una geometría DSARC distinta, que debe verificarse en PPSSPP 1.20.4 antes de promoverse.

**A — auténtico, sin ejecución de juego:** ISO original de 305.496.064 bytes con SHA-256 `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`. FONT.ARC fuente SHA-256 `420613ae4a16595b00c75d17bfb86290e57a30419d81ddbc6f245035e63c9805`, 143.888 bytes; PSPFS #308, offset relativo 11.776, siguiente recurso en 156.160, límite 144.384 bytes, margen original 496 ceros.

## Cambio estructural novedoso

La versión antigua de 44 ligaduras aplicaba offsets `ceil(fin/512)*512 + 16` a cada uno de los seis miembros IMY, resultando en **145.696 bytes**: 1.312 más que el espacio disponible. El prototipo R23 conserva las mismas **44 parejas sin colisión** y el mismo codificador IMY, pero experimenta con `ceil(fin/16)*16 + 16`. Los 7 miembros quedan en offsets de DSARC **528, 11696, 28352, 54016, 79776, 105632, 131440**. Nuevo FONT.ARC **144.000 bytes**, sobrando **384 bytes**, sin escribir sobre `SE.ARC`.

Se descomprimieron y compararon exactamente **6/6 páginas IMY**, preservando **2.721 glifos originales** y **19 españoles**, con 44 ligaduras adicionales `B4–DF`. Los registros de FONT.BIN son 2.784. El font experimental tiene SHA-256 `1bbdd6cba7490753d6af80ca469262fb2080ab7160fc9a8237bffe3805267af4`. La ISO privada experimental tiene SHA-256 `f2b27d575b1693a74589459d3ddbfe10349ce06c12474e4fe647ac3061e0b434` y longitud **305.496.064 bytes**; comprobados los **348 recursos PSPFS ajenos** byte a byte y la tabla ISO9660. La original quedó intacta. Ninguno de esos hashes implica ejecutabilidad.

**Riesgo central:** el intérprete PSP puede esperar offsets de páginas IMY con la alineación histórica de 512 bytes. Parsear el contenedor en Python, verificar límites y descomprimir IMY **no prueba la compatibilidad del motor**. Queda bloqueada la distribución incluso cuando el slot cabe. No cambiar el pipeline canónico a 16 bytes sin ensayo GE/VRAM A/B/A.

## Implementación versionada sin recursos comerciales

- `tools/f4_r21_ligature_font_prototype.py`: por defecto sigue usando alineación histórica 512; opción **experimental** `--member-alignment 16`, validación de slots en RAM y opción interna `include_binary`.
- `tools/f4_r23_font_compact_candidate.py`: exige hash de ISO original, genera variante experimental en ruta privada NUEVA, audita 349 PSPFS, 348 contenidos ajenos y rangos fuera de `DATA.DAT`, comprueba orden `A1–DF` y revoca el archivo candidato si falla.
- `tests/test_f4_r23_compact_font_candidate.py`: 12 regresiones sintéticas (incluidas alteraciones de recursos vecinos, índices y margen), sin simular que existe prueba de juego.
- `reports/R23_FONT_COMPACT_STATIC.json`: metadatos y evidencia A/B/C, sin bytes comerciales.

CI reproducido sobre commit `b8b5d71c977d9231b073e30d7394e334d64fc246`: [push 45321731079](https://github.com/ARivas3008/loxalizacion-cladun-psp/actions/runs/45321731079) **SUCCESS** y [PR 45321738170](https://github.com/ARivas3008/loxalizacion-cladun-psp/actions/runs/45321738170) **SUCCESS**. Solo certifican código/test sintético, **no** PPSSPP.

Para ejecutarlo en un equipo con ISO propia (nunca publicarla):

```bash
python tools/f4_r21_ligature_font_prototype.py --iso-original /PRIVADO/Cladun_USA.iso --ligatures 44 --member-alignment 16 --require-in-place
python tools/f4_r23_font_compact_candidate.py --iso-original /PRIVADO/Cladun_USA.iso --candidate /PRIVADO/Cladun_R23_PILOTO.iso
python -m unittest discover -s tests -p 'test_f4_r23_compact_font_candidate.py' -v
python tools/qa_cobertura_4_areas.py
python tools/qa_cobertura_4_areas.py --require-closed  # fallo esperado: aún no hay cierre
```

## Fronteras reales de cierre

La traducción CSV sigue 9.235/9.237 y su revisión contextual completa no está medida. Gráficos: no se ha inventariado ni validado visualmente todo el contenido. ROMhacking: **3.724/8.248 = 45,15 % integradas**, 4.524 diferidas. Los **2.002** textos largos que podrían caber en campos con 44 ligaduras son **propuestas teóricas/no canónicas**, no sustituciones aplicadas; quedan 841 que crecen sin capacidad de 44 parejas y 1.641 más cortos. Betatesting: no hay nueva evidencia C ni cierre de campaña; PR #7 continúa DRAFT.

## Próxima verificación crítica

Obtener PPSSPP 1.20.4 oficial con SHA autenticado, abrir **ISO original** y **piloto** con PID/starttime/FD verificados, ejecutar A/B/A y registrar si el PSP acepta los miembros IMY a 16+16. Probar caracteres en Opciones, prólogo, combate, TUIKA, segundo nivel, enciclopedia y guardado/carga; detectar métricas, GE/VRAM, texturas, sonido y regresiones. Si falla, revertir prototipo compacto, conservar ruta 19+4 de alineación histórica y estudiar compresión o relocalización real sin tocar recursos vecinos. Solo tras prueba C permitir valorar las propuestas 2002 individualmente y resolver los demás 2.522 SCRIPT diferidos. No modificar `--event-safe-only`, no merge, no force push.
