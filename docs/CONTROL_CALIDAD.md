# Control de calidad (QA)

## Validaciones ya automatizadas

`python tools/verificar_integridad.py --raiz .` comprueba:

- Número de grupos y secuencia `000001...`; IDs irrepetibles.
- Ningún texto fuente ni columna `espanol` ya traducida en la entrega original.
- Bytes hexadecimales válidos, decodificación CP932 congruente, longitudes y desplazamientos con formato consistente.
- Cantidad y orden de los subconjuntos `confirmados_formato.csv` y `revisar_visibilidad.csv`.
- Cantidad de grupos presentes en el TXT; el CSV maestro conserva la procedencia.
- Concordancia con `reports/resumen.json` y `qa/decisiones_auditoria.csv`.

Las pruebas de GitHub Actions ejecutan esas comprobaciones en cada push/PR sin necesitar una ISO comercial. También ejecutan el cotejo del borrador y un inventario de riesgos de preinserción, adjuntado como artefacto de la ejecución.

## Validaciones que faltan

1. **Visualidad**: recorre menús, escenas, tutoriales, combate, finales y opciones en PPSSPP con una lista de casos representativa por recurso.
2. **Gráficos**: revisa recursos del HUD y texturas empaquetadas; no basta con PNG de `SYS.DAT2`.
3. **Ejecutable**: separa mensajes reales de literales técnicos/errores del PSP; no extraigas caracteres aleatorios de instrucciones binarias como texto.
4. **Reinserción**: al implementar un inyector, recalcula offsets/punteros, valida capacidad, y confirma que variables, glifos, saltos de línea y acentos se muestren sin corrupción.
5. **Lógica narrativa**: nombres, voces, diálogos repetidos, singular/plural, contextos, tono y consistencia de terminología.

## Reglas editoriales futuras

No deduplicar textos de diferente fuente. Conservar `%s`, `%d`, `%02d`, símbolos y signos especiales. No usar la columna `original` para sugerencias ni corregir por interpretación un byte ilegible. Cualquier extracción corregida debe dejar evidencia `text_id`, offset antiguo/nuevo y razón.

## Preflight estático obligatorio antes de experimentar con la ISO

```bash
python tools/verificar_borrador_es.py
python tools/auditar_preinsercion_es.py --reporte reports/preflight_local.json --filas reports/preflight_local.csv
python -m unittest discover -s tests -v
```

Sobre el corpus del 18/11/2026: **3.557 candidatas a ensayo** frente a **5.680 bloqueadas** (4.576 scripts con longitud diferente, 280 campos excedidos, 816 sin modelo de longitud, 6 gráficos y 2 fuentes incompletas). El verificador no edita ningún archivo y jamás declara aprobada una reinserción. La codificación experimental CP932-privada F5A0–F5B2 pasa comprobaciones reversibles sin demostrar representación visual. No admitir cambios de texto masivos hasta contar con ensayo de almacenamiento/compresión, punteros, líneas y PPSSPP.

Los textos, sprites, tiles y retratos están mezclados en distintos contenedores anidados: conservar **offsets** por sí solo no basta. Cada ejecución que genere un binario debe comparar hashes de todos los recursos PSPFS y miembros DSARC no autorizados, bytes fuera de los tramos permitidos y archivos ISO9660 fuera de DATA.DAT. Las diferencias no autorizadas abortan todo. Referencia: [protocolo fail-closed](PROTOCOLO_REINSERCION_FAIL_CLOSED.md) y [reporte de preinserción](INFORME_PREINSERCION_ESTATICA.md).
