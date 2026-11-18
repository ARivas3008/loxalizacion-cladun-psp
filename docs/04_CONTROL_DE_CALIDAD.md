# 04 — Control de calidad

## Comprobaciones automáticas

`python tools/validar_corpus.py` revisa conteos, IDs, grupos consecutivos, original no vacío, traducción todavía vacía, hexadecimal de origen, estados, coincidencia básica TXT↔CSV, marcadores de errores de decodificación, ausencia de rutas técnicas y resumen. La suite unitaria cubre formatos y reglas de campos.

## Comprobaciones editoriales posteriores (todavía pendientes)

- Comparar el original y el español con juego en pantalla, preservando intención, voz y límites de UI.
- Validar placeholders, porcentajes y secuencias `%s`, `%d`, `%02d` y similares.
- Revisar longitud, saltos de línea, fuentes y glifos españoles en PPSSPP.
- Aprobar o descartar por evidencia las cadenas marcadas `requiere_comprobar_en_juego`.
- Revisar las dos entradas `requiere_reconstruccion` solo con evidencia de origen adicional; jamás completar caracteres mediante suposición.
- Hacer pruebas de ida/vuelta de reinserción con los archivos originales y elaborar **parche diferencial**, sin redistribuir archivos comerciales.

## Política de identificadores

Ni el código de QA ni colaboradores deben reindexar los bloques al traducir. Si se descubre un texto nuevo, documentar la nueva versión del catálogo y el manifiesto de migración de IDs. No alterar valores `text_id` previamente identificados solo por simplificar la lectura. Los números `grupo_id` de este lote quedan congelados a efectos editoriales.
