# Cladun PSP — fuente española experimental de 19 glifos

**Fase: prototipo privado que supera aislamiento binario. No está aprobado para redistribución ni inserción de todo el corpus.**

## Problema que se corrigió

La primera propuesta de codificación usaba `F040–F052`, mientras que el atlas real requiere **añadir** glifos al final de una tabla FONT.BIN ordenada, cuyo código original máximo es `F592`. Insertar códigos menores en medio habría alterado la asociación entre índices y posiciones de glifo. Se corrigió el códec y el prototipo: usan **`F5A0–F5B2`** para exactamente 19 caracteres: `áéíóúÁÉÍÓÚñÑüÜ¿¡«»ō`.

Los archivos `tools/charset_es.py`, `tools/font_es_patch.py` y `tools/font_es_guard.py` ahora deben usar la misma tabla. Las 2.721 entradas antiguas se conservan en el mismo orden y con idénticos cuatro bytes, sin desplazar glifos.

## Prueba realizada con la ISO USA aportada

SHA-256 original: `b73b263fce863e51a0e27d0d0d11d6bde2886e439a18e2bb186d497619a1b79f`.

| Prueba | Resultado |
|---|---|
| Tamaño total de ISO | Sin cambios, 305.496.064 bytes |
| Entradas PSPFS analizadas | 349 |
| Recursos ajenos a FONT.ARC idénticos byte por byte | 348 |
| Registros de glifos originales intactos | 2.721 |
| Registros tras la ampliación | 2.740 |
| IMY fuente: descomprimir→comprimir→descomprimir | Correcto |
| Desplazamientos ISO9660/PSPFS/DSARC | Sin cambios |
| Crecimiento FONT.ARC | 464 bytes |
| Espacio entre FONT.ARC y el siguiente recurso que queda libre | 32 bytes |
| Pruebas negativas con corrupción de índice/recurso/glifo/relleno | 4 rechazadas |
| Reconocimiento del nuevo mapeo y render en PPSSPP | **No verificado** |
| Inserción de los 9.235 textos traducidos | **No realizada** |

La comparación no se limita a mirar offsets: el verificador bloquea un solo byte no autorizado fuera de los segmentos nuevos de `FONT.ARC`. Dentro del atlas, rechaza cambios en los píxeles de todos los glifos existentes.

## Uso reproducible (en la computadora del propietario)

```bash
python tools/font_es_patch.py --iso /ruta/Cladun-USA.iso --candidate /ruta/cladun_fuente_prueba_privada.iso --report fuente_construccion.json
python tools/font_es_guard.py --original /ruta/Cladun-USA.iso --candidate /ruta/cladun_fuente_prueba_privada.iso --report fuente_aislamiento.json
python -m unittest discover -s tests -v
```

**No subir la ISO candidata**, `FONT.ARC`, imágenes IMY, sprites ni archivos originales a GitHub. Solo se distribuye el código de análisis y los informes JSON.

## Por qué esto no basta aún para el parche

1. El ejecutable debe aceptar los bytes PUA `F5A0–F5B2` al dibujar texto. Falta verlo en PPSSPP.
2. Hay que probar si el motor usa la tabla ordenada por código y si representa las métricas y todos los glifos nuevos.
3. El español es normalmente más largo: **ni el nuevo atlas ni los resultados de aislamiento autorizan agrandar scripts o reubicar punteros**.
4. Los campos de longitud fija deben caber incluyendo NUL; las cadenas de scripts de longitud variable necesitan un reinserter que compruebe referencias, o deben rechazarse.
5. Las imágenes de menús/títulos con texto rasterizado requieren modificación gráfica independiente y pruebas equivalentes.
6. Hay cadenas no codificables, nombres y símbolos de control cuyo uso debe verificarse individualmente.

La prueba de integridad **no equivale** a una prueba de arranque, presentación de retratos, mapas o tiles en el emulador. El objetivo de la siguiente fase es capturar imágenes y logs de PPSSPP para verificar el comportamiento, manteniendo un fail-closed si aparece cualquier anomalía.

Archivos de resultados: [informe](../reports/fuente_es_19_glifos.json) · [pruebas negativas](../reports/fuente_es_pruebas_negativas.json).

Este prototipo no incorpora ningún recurso gráfico original ni material comercial.
