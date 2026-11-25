# R20 — Contraejemplo: longitud total idéntica no implica offsets internos estables

Fixture B: dos comandos textuales en un mismo bloque; primero crece 1 byte y segundo se reduce 1 byte. La reconstrucción conserva longitud total del archivo y tabla de inicios de bloques, pero el segundo comando se desplaza 1 byte. El modo `require_fixed_offsets=True` debe rechazarlo aunque la suma neta de crecimiento sea cero. Esto refuta la estrategia insegura de compensar crecimientos y recortes dentro del mismo bloque para insertar automáticamente las 4524 traducciones diferidas.

Cuatro tests: detección de desplazamiento con suma cero; rechazo de event-safe-only; rechazo de traducción no declarada; rechazo de preimagen incorrecta. Ninguna prueba B certifica comportamiento MIPS o PPSSPP. No se modifican recursos originales.
