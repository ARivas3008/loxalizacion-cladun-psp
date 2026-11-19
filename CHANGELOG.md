# Historial del proyecto

## 0.3.0 — Auditoría y orientación exclusivamente textual (2026-11-17)

- Revisadas estructuralmente las detecciones de texto; se recuperan 127 registros, se corrigen 133 asociaciones y se descartan coincidencias binarios y rutas técnicas.
- 9.237 unidades textuales originales en CSV + TXT por grupos, con campos de traducción **sin rellenar**.
- 8.202 textos de formato confirmado; 1.035 para comprobar visualidad o decodificación.
- Añadidos 6 rótulos de imágenes verificadas y traza CSV de 809 decisiones.
- Eliminada la exposición de índices de instrucciones del motor, archivos redundantes y documentación obsoleta de la rama principal.
- Documentación de método, estados, límites, QA, pipeline reproducible y verificación continua.

## 0.2.x — Extracción inicial (conservada en rama de archivo)

- Inventarios ISO/PSPFS/DSARC, descompresión y corpus preliminar con heurísticas de texto.
- Sus cifras de texto confirmado **han quedado sustituidas** por la nueva auditoría; no usar los listados brutos como fuente para traducir.

## 2026-11-18 — Blindaje de binarios y normalización terminológica

- Revisión contextual + 130 correcciones de traducciones automáticas (total acumulado 196 entradas con intervención de IA).
- Glosario canónico: Pudding, Widen, personajes de apoyo, bastón, Círculo mágico y cambio de clase.
- Auditoría de FONT.BIN y 6 texturas de glifos; diseño de mapeo español PUA/CP932 de 19 caracteres (sin insertar ni renderizar fuentes).
- Ensayo de 2 reemplazos en ISO temporal, offsets intactos, 347 recursos PSPFS protegidos idénticos y copia de prueba eliminada.
- Sigue pendiente la traducción narrativa integral, la compatibilidad en PPSSPP y el inyector general.

## 2026-11-18 — Revisión contextual y aislamiento binario de dos fases

- Post-edición de 196 posiciones adicionales, incluyendo 66 repeticiones contextuales; 369 posiciones revisadas/normalizadas acumuladas.
- Códec y atlas de prueba unificados con 19 glifos PUA F5A0–F5B2, sin reordenar los 2.721 registros anteriores.
- Guardia independiente de FONT.ARC y guardia global de cambios textuales con rangos explícitos; ensayo privado en dos etapas aprobado y pruebas negativas rechazadas.
- Sin prueba visual PPSSPP ni reinserción completa; no publicar ninguna ISO ni assets del juego.

## 2026-11-18 — Fase 3-5: naturalidad, términos, preflight y CI

- 73 ediciones lingüísticas trazadas sobre 72 entradas nuevas para la revisión IA, total acumulado **441 revisadas/normalizadas** y **8.794 pendientes**.
- CSV, TXT español y TXT bilingüe actualizados juntos, con logs de fases 3, 4 y 5; conservados fuente, IDs, posiciones y marcadores.
- Glosario canónico de 63 términos; se han corregido usos de New-geon/Ran-geon, Ward, Job en interfaz, exclamaciones y caracteres Unicode invisibles.
- Auditoría estática y pruebas de capacidad/CP932/variables en CI. Corte: **3.557 candidatas a ensayo**, **5.680 bloqueadas**, **0 aprobadas para parche definitivo**.
- Sin reinserción masiva ni prueba visual PPSSPP. Los guardas de aislamiento ya existentes se conservan como requisito antes de cualquier cambio binario.
