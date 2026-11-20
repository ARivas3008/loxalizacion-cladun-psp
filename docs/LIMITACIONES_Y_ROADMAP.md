# Cobertura e integración de Cladun PSP (edición USA)

**Estado a 18/11/2026: cobertura estructural preliminar 100 %, ejecución y compatibilidad en PPSSPP NO validadas.**

## Qué está listo en código

Se conservan los **9.237 IDs** y sus originales. El integrador `tools/integrar_parche_seguro.py` analiza el borrador junto a `tools/ajustes_campos_es.py` y `tools/graficos_texto_es.py`. La comprobación GitHub Actions `44452350726` encontró **8.491 cambios preparados**, **746 entradas que no modifican bytes** y **cero entradas sin ruta técnica**.

Los antiguos desbordes de 280 nombres/efectos/terrenos ya tienen **etiquetas de inserción compactas**. Los textos completos del borrador permanecen intactos. No son diálogos: añadir una ventana de texto no corregiría las estructuras fijas de 14 a 44 bytes. Las dos fuentes truncadas reciben equivalentes provisionales en español con comprobación de sus bytes y límites originales.

Los seis textos de las imágenes `SYS.DAT2` cuentan con edición de regiones acotadas, reconocimiento SHA-256 de cada PNG y comparación de todos los píxeles fuera de esas regiones. Se realizó un ensayo contra la ISO aportada: 348 recursos PSPFS ajenos y los otros 11 archivos ISO9660 permanecieron idénticos (consultar `reports/ensayo_graficos_iso_2026-11-18.json`).

El integrador reconstruye longitudes de instrucciones de `SCRIPT.DAT` y `SCRIPT.TBL`, campos de `DATABASE.DAT`, punteros de `STRTBL.DAT`, créditos y los seis gráficos textuales. Actualiza solamente las entradas PSPFS de los contenedores modificados; las nuevas versiones se escriben al final, sin mover los offsets de los demás recursos. Usa la extensión de 19 glifos españoles en la fuente experimental.

## Lo que **NO** se ha certificado

- No se ejecutó **una ISO con las 9.237 entradas integradas simultáneamente** en PPSSPP.
- No se verificó que el ejecutable MIPS permita leer el archivo PSPFS extendido y redirigido a nuevas posiciones.
- No se demostró que referencias internas a instrucciones, saltos o índices fuera de `SCRIPT.TBL` no dependan de posiciones absolutas antiguas.
- No se han aprobado visualmente todos los signos españoles, diálogos, menús, rótulos de imágenes, retratos, tiles, iluminación, animaciones, combate o guardado.
- No se ha construido ni publicado un parche diferencial jugable validado. Las versiones privadas de ensayo no se redistribuyen.
- El significado de dos textos fuente truncados es una reconstrucción provisional de etiquetas técnicas; no debe confundirse con fidelidad narrativa confirmada.
- El corpus contiene traducciones automáticas aún pendientes de revisión narrativa y visibilidad; la cobertura técnica no equivale a calidad lingüística 100 %.

## Criterios de cierre final

1. Ejecutar el integrador en modo estricto contra la ISO privada y verificar **exactamente los 9.237 IDs**, hashes, punteros y recursos ajenos antes de publicar la candidata.
2. Confirmar arranque real en PPSSPP, lectura de los contenedores reubicados y rutas de juego representativas, sin omitir diálogos y menús de longitud variable.
3. Comparar capturas y funcionamiento de retratos, tiles, sprites, menús, fuente, seis rótulos y opciones de guardado. Ante cualquier anomalía, rechazar el parche.
4. Distribuir únicamente un parche diferencial para una ISO adquirida legítimamente, con hash de origen y verificador; jamás la ISO ni activos comerciales.

**No equiparar 100 % de preparación del corpus con 100 % de funcionalidad del juego.**
