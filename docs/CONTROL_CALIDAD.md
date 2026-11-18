# Control de calidad (QA)

## Validaciones ya automatizadas

`python tools/verificar_integridad.py --raiz .` comprueba:

- Número de grupos y secuencia `000001...`; IDs irrepetibles.
- Ningún texto fuente ni columna `espanol` ya traducida en la entrega original.
- Bytes hexadecimales válidos, decodificación CP932 congruente, longitudes y desplazamientos con formato consistente.
- Cantidad y orden de los subconjuntos `confirmados_formato.csv` y `revisar_visibilidad.csv`.
- Cantidad de grupos presentes en el TXT; el CSV maestro conserva la procedencia.
- Concordancia con `reports/resumen.json` y `qa/decisiones_auditoria.csv`.

Las pruebas de GitHub Actions ejecutan esas comprobaciones en cada push/PR sin necesitar una ISO comercial.

## Validaciones que faltan

1. **Visualidad**: recorre menús, escenas, tutoriales, combate, finales y opciones en PPSSPP con una lista de casos representativa por recurso.
2. **Gráficos**: revisa recursos del HUD y texturas empaquetadas; no basta con PNG de `SYS.DAT2`.
3. **Ejecutable**: separa mensajes reales de literales técnicos/errores del PSP; no extraigas caracteres aleatorios de instrucciones binarias como texto.
4. **Reinserción**: al implementar un inyector, recalcula offsets/punteros, valida capacidad, y confirma que variables, glifos, saltos de línea y acentos se muestren sin corrupción.
5. **Lógica narrativa**: nombres, voces, diálogos repetidos, singular/plural, contextos, tono y consistencia de terminología.

## Reglas editoriales futuras

No deduplicar textos de diferente fuente. Conservar `%s`, `%d`, `%02d`, símbolos y signos especiales. No usar la columna `original` para sugerencias ni corregir por interpretación un byte ilegible. Cualquier extracción corregida debe dejar evidencia `text_id`, offset antiguo/nuevo y razón.
