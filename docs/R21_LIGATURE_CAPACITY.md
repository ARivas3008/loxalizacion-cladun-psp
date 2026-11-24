# R21 — Factibilidad de 44 ligaduras de un byte (sin escribir fuente)

**Propósito:** explorar reducción de bytes del español sin desplazar comandos. Esto NO autoriza inserción ni acredita que el motor dibuje ligaduras.

## Evidencia A privada, ISO original auténtica
FONT.ARC SHA256 `420613ae4a16595b00c75d17bfb86290e57a30419d81ddbc6f245035e63c9805`; FONT.BIN SHA256 `1f1f5692fecb3b4a66c50f4b20191c1f2658a32ca1220902a5888ae9a11afb46`. La tabla tiene 2721 códigos, ninguno entre A1–DF; hay 376 bytes de padding antes de FONT_00.IMY. Las 19 letras A1–B3 y 44 ligaduras B4–DF requerirían 252 bytes de índices, quedando 124 bytes. De 3072 celdas raster, quedarían 288 tras añadir 63. Los 9237 bytes_hex del corpus no contienen códigos A1–DF independientes (solo bytes trail Shift-JIS); 008723/008724 son dos fuentes truncadas ya conocidas. Estas son condiciones **estructurales necesarias**, no suficientes.

## Simulación B reproducible con corpus canónico
Hay 5207 textos españoles SCRIPT, 683 igual longitud, 2883 que crecen, 1641 que se acortan. Seleccionando las 44 parejas minúsculas más frecuentes cuya suma de métricas de ancho es como máximo 15 píxeles, un algoritmo de emparejamiento máximo no solapado encuentra capacidad teórica para mantener ancho en bytes en **2120/2883** textos que crecen (73,5%). Quedan 763 desbordamientos y los 1641 textos más cortos siguen sin estrategia de relleno invisible validada. La simulación realiza roundtrip por código, sin escribir ISO, fuente ni corpus.

**Limitación crítica:** ancho de glifo de FONT.BIN no demuestra avance real ni estética de dos letras dentro de celda 16×16; también falta garantizar que B4–DF no tengan comportamiento especial del intérprete. Se requiere fuente de ligaduras aislada, guardas de los 2721 glifos, ejecución de PPSSPP real y contraste GE. No asignar incremento del 45,15 % oficial solo por estos cálculos.

Reproducir: `python tools/f4_r21_ligature_capacity.py`; con ISO autenticada: `python tools/f4_r21_ligature_capacity.py --iso-original /PRIVADO/Cladun_USA.iso`; suite `python -m unittest discover -s tests -p 'test_f4_r21_ligature_capacity.py' -v`.
